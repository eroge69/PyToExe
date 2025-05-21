import serial.tools.list_ports

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
    else:
        print("Available Serial Ports:")
        for port in ports:
            print(f" - Port: {port.device}")
            print(f"   Description: {port.description}")
            print(f"   HWID: {port.hwid}")
            print()

if __name__ == "__main__":
    list_serial_ports()
