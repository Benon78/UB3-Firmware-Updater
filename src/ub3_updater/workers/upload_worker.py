"""
=========================================================
UB3 Firmware Updater

Upload Worker

Purpose
-------
Runs UploadService.upload() in a background thread so
the application UI does not block during firmware upload.

Architecture
------------

    GUI
     |
     v
 UploadWorker
     |
     v
 UploadService
     |
     +-- DeviceService
     +-- FirmwareService
     +-- ProcessRunner
     +-- Maple Loader
     |
     v
 UploadResult


Important
---------
UploadWorker does NOT detect or cache the COM port.

UploadService remains responsible for performing a fresh
device scan immediately before the upload.

Therefore:

    UB3 #1 -> COM3
        |
        | remove
        v
    UB3 #2 -> COM7
        |
        | Update
        v
    UploadService fresh scan -> COM7


Version:
    0.7.0
=========================================================
"""

from __future__ import annotations

import threading
import traceback
from datetime import datetime
from enum import Enum
from typing import Callable, Optional

from ub3_updater.models.firmware import Firmware
from ub3_updater.models.upload_result import (
    UploadResult,
    UploadStatus,
)
from ub3_updater.services.upload_service import UploadService


# =========================================================
# Worker State
# =========================================================

class UploadWorkerState(Enum):
    """
    Lifecycle state of UploadWorker.
    """

    IDLE = "Idle"

    STARTING = "Starting"

    UPLOADING = "Uploading"

    COMPLETED = "Completed"

    FAILED = "Failed"

    CANCELLED = "Cancelled"


# =========================================================
# Callback Types
# =========================================================

StateCallback = Callable[
    [UploadWorkerState],
    None,
]

OutputCallback = Callable[
    [str],
    None,
]

ProgressCallback = Callable[
    [str],
    None,
]

CompletedCallback = Callable[
    [UploadResult],
    None,
]

ErrorCallback = Callable[
    [Exception],
    None,
]


# =========================================================
# Upload Worker
# =========================================================

class UploadWorker:
    """
    Background worker for firmware uploads.

    The worker owns the execution thread but does not own
    firmware-update business logic.

    UploadService remains responsible for:

        - Device detection
        - Firmware validation
        - Firmware preparation
        - COM-port selection
        - Maple command construction
        - Maple Loader execution
        - Upload result interpretation
    """

    def __init__(
        self,
        upload_service: UploadService,
    ) -> None:

        self.upload_service = upload_service

        # -------------------------------------------------
        # Thread
        # -------------------------------------------------

        self._thread: Optional[
            threading.Thread
        ] = None

        # -------------------------------------------------
        # Cancellation
        # -------------------------------------------------

        self._cancel_event = (
            threading.Event()
        )

        # -------------------------------------------------
        # State
        # -------------------------------------------------

        self._state = (
            UploadWorkerState.IDLE
        )

        self._state_lock = (
            threading.Lock()
        )

        # -------------------------------------------------
        # Current firmware
        # -------------------------------------------------

        self._firmware: Optional[
            Firmware
        ] = None

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        self._result: Optional[
            UploadResult
        ] = None

        # -------------------------------------------------
        # Error
        # -------------------------------------------------

        self._exception: Optional[
            Exception
        ] = None

        # -------------------------------------------------
        # Timing
        # -------------------------------------------------

        self._started_at: Optional[
            datetime
        ] = None

        self._completed_at: Optional[
            datetime
        ] = None

        # -------------------------------------------------
        # Callbacks
        # -------------------------------------------------

        self._on_state_changed: Optional[
            StateCallback
        ] = None

        self._on_output: Optional[
            OutputCallback
        ] = None

        self._on_progress: Optional[
            ProgressCallback
        ] = None

        self._on_completed: Optional[
            CompletedCallback
        ] = None

        self._on_error: Optional[
            ErrorCallback
        ] = None

    # =====================================================
    # Properties
    # =====================================================

    @property
    def state(self) -> UploadWorkerState:
        """
        Current worker state.
        """

        with self._state_lock:

            return self._state

    # -----------------------------------------------------

    @property
    def firmware(self) -> Optional[Firmware]:
        """
        Firmware currently assigned to the worker.
        """

        return self._firmware

    # -----------------------------------------------------

    @property
    def result(self) -> Optional[UploadResult]:
        """
        Final upload result.

        Returns None while no result is available.
        """

        return self._result

    # -----------------------------------------------------

    @property
    def exception(self) -> Optional[Exception]:
        """
        Unexpected worker exception, if any.
        """

        return self._exception

    # -----------------------------------------------------

    @property
    def is_running(self) -> bool:
        """
        True while the background upload thread is active.
        """

        thread = self._thread

        return (
            thread is not None
            and thread.is_alive()
        )

    # -----------------------------------------------------

    @property
    def is_finished(self) -> bool:
        """
        True when the worker reached a terminal state.
        """

        return self.state in (
            UploadWorkerState.COMPLETED,
            UploadWorkerState.FAILED,
            UploadWorkerState.CANCELLED,
        )

    # -----------------------------------------------------

    @property
    def is_cancel_requested(self) -> bool:
        """
        True when cancellation has been requested.
        """

        return (
            self._cancel_event.is_set()
        )

    # =====================================================
    # Callback Registration
    # =====================================================

    def set_on_state_changed(
        self,
        callback: Optional[StateCallback],
    ) -> None:
        """
        Register a state-change callback.
        """

        self._on_state_changed = callback

    # -----------------------------------------------------

    def set_on_output(
        self,
        callback: Optional[OutputCallback],
    ) -> None:
        """
        Register an output callback.

        This will later allow the GUI to display Maple
        Loader output in real time.

        Note:
        UploadService/ProcessRunner must expose streaming
        output for real-time messages. The worker does not
        fabricate output.
        """

        self._on_output = callback

    # -----------------------------------------------------

    def set_on_progress(
        self,
        callback: Optional[ProgressCallback],
    ) -> None:
        """
        Register a progress callback.

        The current Maple Loader integration does not
        provide reliable numeric percentage information.

        Therefore progress is represented as a textual
        phase until a proper progress parser is introduced.
        """

        self._on_progress = callback

    # -----------------------------------------------------

    def set_on_completed(
        self,
        callback: Optional[CompletedCallback],
    ) -> None:
        """
        Register the completion callback.
        """

        self._on_completed = callback

    # -----------------------------------------------------

    def set_on_error(
        self,
        callback: Optional[ErrorCallback],
    ) -> None:
        """
        Register the unexpected-error callback.
        """

        self._on_error = callback

    # =====================================================
    # Combined Callback Configuration
    # =====================================================

    def configure_callbacks(
        self,
        *,
        on_state_changed: Optional[
            StateCallback
        ] = None,

        on_output: Optional[
            OutputCallback
        ] = None,

        on_progress: Optional[
            ProgressCallback
        ] = None,

        on_completed: Optional[
            CompletedCallback
        ] = None,

        on_error: Optional[
            ErrorCallback
        ] = None,
    ) -> None:
        """
        Configure all worker callbacks.
        """

        self._on_state_changed = (
            on_state_changed
        )

        self._on_output = (
            on_output
        )

        self._on_progress = (
            on_progress
        )

        self._on_completed = (
            on_completed
        )

        self._on_error = (
            on_error
        )

    # =====================================================
    # Start
    # =====================================================

    def start(
        self,
        firmware: Firmware,
    ) -> bool:
        """
        Start firmware upload in a background thread.

        Returns
        -------
        bool
            True if the worker was started.

            False if the worker is already running or
            otherwise cannot be started.
        """

        # -------------------------------------------------
        # Validate firmware object
        # -------------------------------------------------

        if not isinstance(
            firmware,
            Firmware,
        ):

            raise TypeError(
                "UploadWorker.start() expects "
                "a Firmware object."
            )

        # -------------------------------------------------
        # Prevent duplicate upload
        # -------------------------------------------------

        if self.is_running:

            return False

        # -------------------------------------------------
        # Prevent starting while in a terminal state
        # without reset
        # -------------------------------------------------

        if self.state != UploadWorkerState.IDLE:

            return False

        # -------------------------------------------------
        # Store firmware
        # -------------------------------------------------

        self._firmware = firmware

        # -------------------------------------------------
        # Clear previous state
        # -------------------------------------------------

        self._result = None

        self._exception = None

        self._cancel_event.clear()

        self._started_at = None

        self._completed_at = None

        # -------------------------------------------------
        # Start worker
        # -------------------------------------------------

        self._set_state(
            UploadWorkerState.STARTING
        )

        self._thread = threading.Thread(
            target=self._run,
            name="UB3-UploadWorker",
            daemon=True,
        )

        self._thread.start()

        return True

    # =====================================================
    # Run
    # =====================================================

    def _run(self) -> None:
        """
        Background worker execution method.
        """

        self._started_at = (
            datetime.now()
        )

        try:

            # ---------------------------------------------
            # Starting
            # ---------------------------------------------

            self._emit_progress(
                "Preparing firmware upload..."
            )

            # ---------------------------------------------
            # Cancellation before upload
            # ---------------------------------------------

            if self.is_cancel_requested:

                self._handle_cancelled()

                return

            # ---------------------------------------------
            # Uploading
            # ---------------------------------------------

            self._set_state(
                UploadWorkerState.UPLOADING
            )

            self._emit_progress(
                "Starting firmware upload..."
            )

            # ---------------------------------------------
            # IMPORTANT:
            #
            # Do not scan the device here.
            #
            # UploadService performs the authoritative
            # fresh scan immediately before upload.
            # ---------------------------------------------

            result = (
                self.upload_service.upload(
                    self._firmware
                )
            )

            self._result = result

            self._completed_at = (
                datetime.now()
            )

            # ---------------------------------------------
            # Determine final state
            # ---------------------------------------------

            if (
                result.status
                == UploadStatus.CANCELLED
            ):

                self._set_state(
                    UploadWorkerState.CANCELLED
                )

                self._emit_progress(
                    "Firmware upload cancelled."
                )

            elif result.success:

                self._set_state(
                    UploadWorkerState.COMPLETED
                )

                if result.has_warning:

                    self._emit_progress(
                        "Firmware upload completed "
                        "with warning."
                    )

                else:

                    self._emit_progress(
                        "Firmware upload completed "
                        "successfully."
                    )

            else:

                self._set_state(
                    UploadWorkerState.FAILED
                )

                self._emit_progress(
                    "Firmware upload failed."
                )

            # ---------------------------------------------
            # Completion callback
            # ---------------------------------------------

            self._emit_completed(
                result
            )

        except Exception as exc:

            self._exception = exc

            self._completed_at = (
                datetime.now()
            )

            # ---------------------------------------------
            # Unexpected exception
            # ---------------------------------------------

            if self.is_cancel_requested:

                self._set_state(
                    UploadWorkerState.CANCELLED
                )

            else:

                self._set_state(
                    UploadWorkerState.FAILED
                )

            # ---------------------------------------------
            # Diagnostic output
            # ---------------------------------------------

            self._emit_output(
                traceback.format_exc()
            )

            # ---------------------------------------------
            # Error callback
            # ---------------------------------------------

            self._emit_error(
                exc
            )

    # =====================================================
    # Cancel
    # =====================================================

    def cancel(self) -> bool:
        """
        Request cancellation.

        Important:
        ----------
        This does not forcibly terminate the Maple Loader
        process.

        Process-level cancellation must be implemented
        cooperatively by ProcessRunner.

        Returns
        -------
        bool
            True when cancellation was requested.
        """

        if not self.is_running:

            return False

        self._cancel_event.set()

        self._emit_progress(
            "Cancellation requested..."
        )

        return True

    # =====================================================
    # Wait
    # =====================================================

    def wait(
        self,
        timeout: Optional[float] = None,
    ) -> bool:
        """
        Wait for the worker thread to finish.

        Parameters
        ----------
        timeout:
            Maximum number of seconds to wait.

        Returns
        -------
        bool
            True if the worker finished.
            False if timeout expired.
        """

        thread = self._thread

        if thread is None:

            return True

        thread.join(
            timeout=timeout
        )

        return not thread.is_alive()

    # =====================================================
    # Reset
    # =====================================================

    def reset(self) -> bool:
        """
        Reset worker to IDLE.

        The worker must not be running.
        """

        if self.is_running:

            return False

        self._firmware = None

        self._result = None

        self._exception = None

        self._started_at = None

        self._completed_at = None

        self._cancel_event.clear()

        self._set_state(
            UploadWorkerState.IDLE
        )

        return True

    # =====================================================
    # Internal State
    # =====================================================

    def _set_state(
        self,
        state: UploadWorkerState,
    ) -> None:
        """
        Change worker state and notify callback.
        """

        with self._state_lock:

            self._state = state

        callback = (
            self._on_state_changed
        )

        if callback is not None:

            try:

                callback(state)

            except Exception:

                # Callback failures must never kill the
                # upload worker.
                pass

    # =====================================================
    # Internal Progress
    # =====================================================

    def _emit_progress(
        self,
        message: str,
    ) -> None:
        """
        Emit a textual progress message.
        """

        callback = (
            self._on_progress
        )

        if callback is not None:

            try:

                callback(message)

            except Exception:

                pass

    # =====================================================
    # Internal Output
    # =====================================================

    def _emit_output(
        self,
        message: str,
    ) -> None:
        """
        Emit raw diagnostic/output text.
        """

        callback = (
            self._on_output
        )

        if callback is not None:

            try:

                callback(message)

            except Exception:

                pass

    # =====================================================
    # Internal Completion
    # =====================================================

    def _emit_completed(
        self,
        result: UploadResult,
    ) -> None:
        """
        Emit completed callback.
        """

        callback = (
            self._on_completed
        )

        if callback is not None:

            try:

                callback(result)

            except Exception:

                pass

    # =====================================================
    # Internal Error
    # =====================================================

    def _emit_error(
        self,
        error: Exception,
    ) -> None:
        """
        Emit unexpected worker error.
        """

        callback = (
            self._on_error
        )

        if callback is not None:

            try:

                callback(error)

            except Exception:

                pass

    # =====================================================
    # Internal Cancel Handling
    # =====================================================

    def _handle_cancelled(self) -> None:
        """
        Handle cancellation requested before upload starts.
        """

        result = (
            UploadResult.cancelled_result(
                "Firmware upload was cancelled "
                "before it started.",
            )
        )

        self._result = result

        self._completed_at = (
            datetime.now()
        )

        self._set_state(
            UploadWorkerState.CANCELLED
        )

        self._emit_completed(
            result
        )