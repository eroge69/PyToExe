import serial
import time
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
import numpy as np  # For moving average filter

# Serial port settings
port = "COM5"  # Change to your COM port
baudrate = 9600
filter_size = 5  # Moving average filter size

try:
    ser = serial.Serial(port, baudrate)
    print(f"Connected to port {port}")

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    filtered_values = np.zeros(filter_size, dtype=np.uint16)  # Use uint16 for 16-bit values

    while True:
        try:
            line = ser.readline().decode('utf-8').strip()  # Read and decode the line
            if line:
                try:
                    value = int(line)  # Convert the line to an integer

                    # Input validation
                    if 0 <= value <= 1023:
                        filtered_values = np.roll(filtered_values, -1)
                        filtered_values[-1] = value
                        average_value = np.mean(filtered_values)
                        volume_percent = average_value / 1023 * 100
                        volume.SetMasterVolumeLevelScalar(volume_percent / 100, None)
                        print(f"Volume: {volume_percent:.2f}%")
                    else:
                        print("Received invalid value from Arduino")

                except ValueError:
                    print("Error reading data from Arduino")

        except (serial.SerialException, OSError) as e:
            print(f"Error communicating with serial port: {e}")
            break  # Exit the loop if there's a serial error

except serial.SerialException as e:
    print(f"Error connecting to serial port: {e}")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")
    input()