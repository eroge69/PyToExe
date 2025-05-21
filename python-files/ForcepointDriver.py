import asyncio
from bleak import BleakClient, BleakScanner
import pyautogui
import time

pyautogui.FAILSAFE = False

DEVICE_NAME = "GyroMouse"
GYRO_CHAR_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
CLICK_CHAR_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"

def scale(val):
    return int(val) * 0.005  # Mouse sensitivity scaling

async def handle_gyro(sender, data):   
    x = int.from_bytes(data[:2], byteorder='little', signed=True)
    y = int.from_bytes(data[2:], byteorder='little', signed=True)
    print(f"Gyro Notification - X: {x}, Y: {y}")
    
    # Move mouse
    await asyncio.to_thread(pyautogui.moveRel, scale(x), -scale(y))

async def handle_click(sender, data):
    if len(data) > 0 and data[0] == 1:
        print("Click detected!")
        await asyncio.to_thread(pyautogui.click)

async def main():
    print("Scanning for devices...")
    device = await BleakScanner.find_device_by_filter(lambda d, adv: d.name and DEVICE_NAME in d.name)
    if not device:
        print(f"Device '{DEVICE_NAME}' not found.")
        return

    print(f"Found device: {device.name} ({device.address})")
    async with BleakClient(device) as client:
        if not client.is_connected:
            print("Failed to connect.")
            return

        print("Connected. Subscribing to characteristics...")
        await asyncio.sleep(1)

        try:
            await client.start_notify(GYRO_CHAR_UUID, handle_gyro)
            await client.start_notify(CLICK_CHAR_UUID, handle_click)
            print("Notifications subscribed. Listening...")
            await asyncio.sleep(100000000)  # Keep script alive
        except Exception as e:
            print(f"Notification error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
