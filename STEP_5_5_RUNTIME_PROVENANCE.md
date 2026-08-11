# Step 5.5 Final Runtime Provenance

Source archive:
Arduino(2).zip supplied for the UB3 project.

Approved Maple runtime:
- Arduino/hardware/Arduino_STM32/Arduino_STM32-master/tools/win/maple_loader.jar
- Arduino/hardware/Arduino_STM32/Arduino_STM32-master/tools/win/lib/jssc.jar
- Arduino/hardware/Arduino_STM32/Arduino_STM32-master/tools/win/dfu-util.exe
- Arduino/hardware/Arduino_STM32/Arduino_STM32-master/tools/win/libusb0.dll

Java runtime:
- Arduino/java/
- JAVA_VERSION="1.8.0_191"
- OS_ARCH="i586"
- JVM: java/bin/client/jvm.dll

Windows drivers:
- Arduino/hardware/Arduino_STM32/Arduino_STM32-master/drivers/win/
- Includes install_drivers.bat
- Includes install_STM_COM_drivers.bat
- Includes Maple DFU, Maple Serial, and STM COM resources

Upload contract:
    maple_upload <detected COM> 2 1EAF:003 <firmware.bin>

The firmware binaries are not modified by Step 5.5.
README.md unchanged: True
