# Maple Loader Java Runtime

`maple_loader.jar` is a Java application. The bundled Maple Loader classes require a Java runtime capable of loading Java class-file major version 51 (Java 7 or newer).

Resolution order used by `maple_upload.bat`:
1. `resources/tools/maple/java/bin/java.exe`
2. `%JAVA_HOME%\bin\java.exe`
3. `java.exe` on `PATH`
4. Legacy Arduino STM32 `%5\java\bin\java.exe`

The supplied `Arduino_STM32.zip` contains the Maple Loader and DFU tooling but does not contain the Arduino IDE Java runtime. Therefore this baseline does not embed Java.

For a fully portable release, add a compatible Windows x64 JRE under:
`resources/tools/maple/java/`

No Python-side architecture change is required when that runtime is added.
