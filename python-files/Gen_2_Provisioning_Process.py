# pip install bleak
# Gen 2
import asyncio
import requests
import json
from bleak import BleakScanner, BleakClient
import sys
import jwt
from tkinter import messagebox, simpledialog

###############################
DSN = "103899" #"103064"
Device_Address = ""
SSID = "Typical"
PASS = "Arghya@19"

USER_Gmail = "shuvabrata@wooshair.com"
USER_Password = "Shuva@123"
###############################

NOTIFY_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # ACK
WRITE_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # Network
READ_UUID = "6e400006-b5a3-f393-e0a9-e50e24dcca9e"  # Baseline Data

url = "https://api-dev.wooshair.com/v2/admin/mock/onboad/gen2"

BSLP = 0

async def notification_handler(
    sender: int, data: bytearray, client: BleakClient
):
    global DSN, Device_Address, SSID, PASS, USER_Gmail, USER_Password, BSLP
    # Convert bytearray to integer
    status = int.from_bytes(
        data, byteorder="little"
    )  # Assuming data is little-endian

    print(f"Notification received from {sender}: {status}")

    if status == 32:
        print("Device connected successfully.")

        # Read from the READ_UUID characteristic
        try:
            value = await client.read_gatt_char(READ_UUID)
            BSLP = value.decode('utf-8')
            print(f"Read value from READ_UUID: {BSLP}")
        except Exception as e:
            print("Error reading from READ_UUID:", e)
            messagebox.showerror("Error", f"{e}")
            quit()

    elif status != 0:
        # If it's not the "WAITING" state (0), print the status
        print(f"Device status: {status}")

    # Stop notifications after receiving CONNECTED status
    await client.stop_notify(NOTIFY_UUID)
    print("Stopped notifications after receiving CONNECTED status.")

    # Disconnect from the device after reading the characteristic
    await client.disconnect()
    print("Disconnected from the device.")

    if status == 32:
        print("Signing in to Wooshair onboarding account ...")
        payload = {"email": USER_Gmail, "password": USER_Password}
        headers = {"Content-Type": "application/json"}
        response = requests.request(
            "POST",
            "https://api-dev.wooshair.com/user/signin",
            json=payload,
            headers=headers,
        )

        try:
            response_json = json.loads(response.text)
            idToken = response_json["IdToken"]
            print(idToken)

        except Exception as sign_in_exception:
            print("Sign In Error")
            messagebox.showerror("Error", "Sign In Error!")
            quit()
        decoded = jwt.decode(idToken, options={"verify_signature": False})
        payload = {"user_id": decoded["sub"], "dsn": DSN}

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "insomnia/11.0.2",
            "Authorization": idToken,
        }
        response = requests.request("POST", url, json=payload, headers=headers)
        if response.status_code == 200 and BSLP:
            print(f"Onboard Success with BSLP: {BSLP}")
            messagebox.showinfo("Success", f"Onboard Success ☻ with BSLP: {BSLP}")
        else:
            print("Onboard Fail")
            messagebox.showerror("Error", "Onboard Fail!")
    quit()


def takeUserInputs():
    global DSN, Device_Address, SSID, PASS, USER_Gmail, USER_Password
    user_input = simpledialog.askstring("DSN", "Enter DSN")

    # Use the input
    if user_input is not None:
        print("DSN:", user_input)
        DSN = user_input
    else:
        print("No input provided.")
        messagebox.showerror("Error", "No input provided!")
        quit()
    #############################################################
    user_input = simpledialog.askstring("SSID", "Enter WiFi SSID")

    # Use the input
    if user_input is not None:
        print("SSID:", user_input)
        SSID = user_input
    else:
        print("No input provided.")
        messagebox.showerror("Error", "No input provided!")
        quit()
    #############################################################
    user_input = simpledialog.askstring("PASS", "Enter WiFi Password")

    # Use the input
    if user_input is not None:
        print("Password:", user_input)
        PASS = user_input
    else:
        print("No input provided.")
        messagebox.showerror("Error", "No input provided!")
        quit()
    #############################################################
    user_input = simpledialog.askstring("Gmail ID", "Enter Your Mail Id")

    # Use the input
    if user_input is not None:
        print("Mail Id:", user_input)
        USER_Gmail = user_input
    else:
        print("No input provided.")
        messagebox.showerror("Error", "No input provided!")
        quit()
    #############################################################
    user_input = simpledialog.askstring("Gmail PASS", "Enter Your Mail Pass")

    # Use the input
    if user_input is not None:
        print("Mail Pass:", user_input)
        USER_Password = user_input
    else:
        print("No input provided.")
        messagebox.showerror("Error", "No input provided!")
        quit()


async def main():
    global DSN, Device_Address, SSID, PASS, USER_Gmail, USER_Password
    if (DSN == "" or Device_Address == "") and SSID == "" and PASS == "" and USER_Gmail == "" and USER_Password == "":
        takeUserInputs()
    if (DSN == "") and (Device_Address == ""):
        sys.exit("Device Name or MAC Address is blank")
    elif (DSN != "") and (Device_Address != ""):
        sys.exit("Device Name or MAC Address is blank")
    devices = await BleakScanner.discover(timeout=3)
    for d in devices:
        print(f"{d.name} | {d.address} | {d._rssi}")
        if (DSN != "") and (Device_Address == ""):
            if d.name == ("WOOSH_SM_" + DSN):
                Device_Address = d.address
                break
        elif (DSN == "") and (Device_Address != ""):
            if d.address == Device_Address:
                DSN = d.name.replace("WOOSH_SM_", "")
                break
        elif (DSN == "") and (Device_Address == ""):
            sys.exit("Device Name or MAC Address is blank")
        else:
            sys.exit("Enter Only Device Name or MAC Address")
    if (DSN != "") and (Device_Address != ""):
        print(f"Device MAC Address ==> {Device_Address}")
        async with BleakClient(Device_Address, timeout=20) as client:
            # Subscribe to notifications for the Notify UUID
            await client.start_notify(
                NOTIFY_UUID,
                lambda sender, data: asyncio.create_task(
                    notification_handler(sender, data, client)
                ),
            )
            await asyncio.sleep(5)
            # Write a string to the Write UUID characteristic
            STRING_TO_WRITE = (
                '{"ssid":"' + SSID + '","password":"' + PASS + '"}'
            )
            await client.write_gatt_char(
                WRITE_UUID, STRING_TO_WRITE.encode("utf-8")
            )
            print(f"Sent '{STRING_TO_WRITE}' to Write UUID")

            # Wait until we receive the CONNECTED status (this will be handled in the notification handler)
            while True:
                await asyncio.sleep(1)  # Sleep and continue checking for CONNECTED status
    else:
        messagebox.showerror("Error", f"No WOOSH_SM_{DSN} Device Found !")        

asyncio.run(main())
