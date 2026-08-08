import bootstrap

from ub3_updater.utils.process_runner import ProcessRunner


runner = ProcessRunner()


print("=" * 70)
print("PROCESS RUNNER TEST")
print("=" * 70)


def output(line):

    print(f"[OUT] {line}")


def error(line):

    print(f"[ERR] {line}")


result = runner.run(
    [
        "cmd.exe",
        "/c",
        "echo UB3 ProcessRunner Test"
    ],
    on_output=output,
    on_error=error,
)


print()
print("=" * 70)
print("RESULT")
print("=" * 70)

print("Started :", result.started)

print("Success :", result.success)

print("Failed  :", result.failed)

print("Return  :", result.return_code)

print("Timeout :", result.timed_out)

print("Cancel  :", result.cancelled)

print("Error   :", result.error)

print("Output  :", result.stdout.strip())

print(
    "Duration:",
    round(result.duration_seconds, 3),
    "seconds",
)