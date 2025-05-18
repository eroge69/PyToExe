import serial
import threading
import msvcrt
import time

ser = serial.Serial('COM3', 115200)

stop_event = threading.Event()

def read_from_serial():
    while not stop_event.is_set():
        if ser.in_waiting:
            try:
                data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                print(data, end='', flush=True)
            except serial.SerialException:
                break  # Port closed, exit thread

thread = threading.Thread(target=read_from_serial, daemon=True)
thread.start()

print("Serial terminal started. Type to send. Ctrl+C to exit.\n")

try:
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getwch()

            if char == '\r': # Enter 
                ser.write(b'\r\n')
                print()
            elif char == '\x08': # Backspace character
                ser.write(b'\x7f') # Send Del character for that
                print('\b \b', end='', flush=True)
            elif char == '\x03':
                raise KeyboardInterrupt
            else:
                ser.write(char.encode('utf-8'))
                print(char, end='', flush=False)

except KeyboardInterrupt:
    print("\nExiting...")
    stop_event.set()  # Tell the thread to stop
    thread.join()     # Wait for thread to finish

finally:
    if ser.is_open:
        ser.close()
