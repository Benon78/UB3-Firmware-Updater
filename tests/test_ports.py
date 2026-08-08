import sys
import bootstrap
import serial.tools.list_ports

print("=" * 80)
print("USB PORT DIAGNOSTICS")
print("=" * 80)

ports = serial.tools.list_ports.comports()

if not ports:
    print("No COM ports found.")

for port in ports:
    print(f"Device       : {port.device}")
    print(f"Description  : {port.description}")
    print(f"Manufacturer : {port.manufacturer}")
    print(f"VID          : {port.vid}")
    print(f"PID          : {port.pid}")
    print(f"HWID         : {port.hwid}")
    print(f"Serial       : {port.serial_number}")
    print(f"Location     : {port.location}")
    print("-" * 80)