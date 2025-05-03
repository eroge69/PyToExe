import zlib

import hid

import os

import sys

import time

import ctypes

from pynput import mouse

import pyautogui

import torch

import threading

from hid_mouse import MouseInstruct, DeviceNotFoundError

import serial
from serial.tools import list_ports


Loaded = False


def restart_program():

    print("Digital] -> restarting, please wait...")

    python = sys.executable

    os.execv(python, ['python'] + sys.argv)



user32 = ctypes.WinDLL("user32")



def show_console(visible=True):

    hwnd = ctypes.windll.kernel32.GetConsoleWindow()

    if hwnd:

        ctypes.windll.user32.ShowWindow(hwnd, 5 if visible else 0)

        import threading



class others:

    @staticmethod

    def get_hwid():

        if platform.system() == "Linux":

            with open("/etc/machine-id") as f:

                hwid = f.read()

                return hwid

        elif platform.system() == 'Windows':

            try:

                c = wmi.WMI()

                for disk in c.Win32_DiskDrive():

                    if 'PHYSICALDRIVE' in disk.DeviceID:

                        pnp_device_id = disk.PNPDeviceID

                        return pnp_device_id

            except:

                winuser = os.getlogin()

                sid = win32security.LookupAccountName(None, winuser)[0]

                hwid = win32security.ConvertSidToStringSid(sid)

                return hwid

        elif sys.platform.system() == 'Darwin':

            output = subprocess.Popen("ioreg -l | grep IOPlatformSerialNumber", stdout=subprocess.PIPE, shell=True).communicate()[0]

            serial = output.decode().split('=', 1)[1].replace(' ', '')

            hwid = serial[1:-2]

            return hwid



class Protect():

    def start(self):

        try:

            import psutil

            import requests

        except:

            os.system(f'py -m pip --no-cache-dir --disable-pip-version-check install psutil requests >nul 2>&1')

            restart_program()



        BLACKLISTED_PROGRAMS = [

            "httpdebuggerui.exe",

            "systeminformer.exe",

            "wireshark.exe",

            "HTTPDebuggerSvc.exe",

            "fiddler.exe",

            "dumper.exe",

            "regedit.exe",

            "vboxservice.exe",

            "df5serv.exe",

            "processhacker.exe",

            "vboxtray.exe",

            "vmtoolsd.exe",

            "vmwaretray.exe",

            "ida.exe",

            "ida64.exe",

            "ollydbg.exe",

            "pestudio.exe",

            "vmwareuser",

            "vgauthservice.exe",

            "vmacthlp.exe",

            "x96dbg.exe",

            "vmsrvc.exe",

            "x32dbg.exe",

            "vmusrvc.exe",

            "prl_cc.exe",

            "prl_tools.exe",

            "xenservice.exe",

            "qemu-ga.exe",

            "joeboxcontrol.exe",

            "ksdumperclient.exe",

            "ksdumper.exe",

            "cheatengine.exe",

            "dnspy.exe",

            "resourcehacker.exe",

            "reshacker.exe",

            "ollyice.exe",

            "frida-server",

            "frida.exe",

            "radare2.exe",

            "radare.exe",

            "dbgview.exe",

            "apimonitor.exe",

            "scylla.exe",

            "syser.exe",

            "hookshark.exe",

            "pe-sieve.exe",

            "unpacker.exe",

            "procdump.exe",

            "windump.exe",

            "tcpview.exe",

            "winsockws.exe",

            "lordpe.exe",

            "lordpe64.exe",

            "procmon.exe",

            "windowdetect.exe",

            "wireshark-cli.exe",

            "api_spy.exe",

            "reclass.exe",

            "debugview.exe",

            "apateDNS.exe",

            "peid.exe",

            "darkspy.exe",

            "networkminer.exe",

        ]



        BLACKLISTED_WINDOW_NAMES = [

            "IDA: Quick start", "VBoxTrayToolWndClass", "proxifier", "graywolf", "extremedumper", 

            "zed", "exeinfope", "titanHide", "ilspy", "x32dbg", "codecracker", "simpleassembly", 

            "process hacker 2", "System Informer", "http debugger", "Centos", "pyarmor", "ILSpy", "reverse", "simpleassemblyexplorer", 

            "de4dotmodded", "dojandqwklndoqwd-x86", "memdump", "fiddler", "die", "pizza", "crack", "strongod", 

            "ida -", "debugger", "gdb", "x64_dbg", "windbg", "wireshark", "wpe pro", "dbg", "httpanalyzer", 

            "wireshark", "dbgclr", "HxD", "ollydbg", "ksdumper", "wpe pro", "scyllahide", "MegaDumper", 

            "ghidra", "0harmony", "hacker", "process hacker", "PE Tools", "scyllaHide", "frida", "radare2", 

            "dnSpy", "scylla", "Cheat Engine", "ProcDump", "ReClass", "Window Detector", "Reverse Engineering"

        ]



        def get_blacklisted_process_name():

            for process in psutil.process_iter(['pid', 'name']):

                for name in BLACKLISTED_WINDOW_NAMES:

                    if name.lower() in process.info['name'].lower():

                        return process.info['name'], process.info['pid']

            return None, None



        def warn(message):

            print(f"[Digital] -> Blacklisted process detected. You have been warned")

            url = b""

            data = {"content": message}

            requests.post(url, json=data)



        def block_bad_processes():

            while True:

                blacklisted_process_name, blacklisted_pid = get_blacklisted_process_name()

                if blacklisted_process_name:

                    try:

                        warn(f"> Blacklisted **PROCESS** detected: **{blacklisted_process_name}**\n> User license key: **{api.user_data.username}**\n> User hwid: **{others.get_hwid()}**")

                    except:

                        pass



                    try:

                        process = psutil.Process(blacklisted_pid)

                        process.terminate()

                    except:

                        time.sleep(1)

                        exit(1)

                        os.system('taskkill /f /fi "imagename eq cmd.exe" >nul 2>&1')

                        os.system('taskkill /f /fi "imagename eq python.exe" >nul 2>&1')

                time.sleep(5)



        def block_debuggers():

            while True:

                for proc in psutil.process_iter():

                    if any(procstr in proc.name().lower() for procstr in BLACKLISTED_PROGRAMS):

                        try:

                            warn(f"> Blacklisted **DEBUGGER** detected: **{proc.name()}**\n> User license key: **{api.user_data.username}**\n> User hwid: **{others.get_hwid()}**")

                        except:

                            pass

                        

                        try:

                            proc.kill()

                        except:

                            time.sleep(1)

                            exit(1)

                            os.system('taskkill /f /fi "imagename eq cmd.exe" >nul 2>&1')

                            os.system('taskkill /f /fi "imagename eq python.exe" >nul 2>&1')

                            pass

                time.sleep(10)



        threading.Thread(target=block_debuggers, daemon=True).start()

        threading.Thread(target=block_bad_processes, daemon=True).start()



def download_requirements():

    os.system("cls")

    print("[Digital] -> please wait...")



    modules = [

        "numpy==1.25.2",

        "pygame",

        "opencv-python",

        "PyQt5",

        "wmi",

        "pycryptodomex",

        "pywin32",

        "psutil",

        "requests",

        "matplotlib --prefer-binary",

        "ultralytics",

        "pandas",

        "Pillow",

        "PyYAML",

        "scipy",

        "seaborn",

        "tqdm",

        "onnxruntime==1.15",

        "onnxruntime_gpu",

        "comtypes",

        "torch==2.3.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html",

        "torchvision==0.18.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html",

        "observable",

        "bettercam",

        "pyserial",

        "cryptography",

    ]



    total_modules = len(modules)

    i = 1

    for module in modules:

        print(f"[Digital] -> installing requirements.. ({int((i/total_modules)*100)}%)")

        i+=1

        os.system(f'py -m pip --no-cache-dir --disable-pip-version-check install {module} >nul 2>&1')

        os.system("cls")



    print("[Digital] -> successfuly installed packages")

    print("[Digital] -> restarting program...")

    time.sleep(1)

    restart_program()



try:

    import zipfile

    import requests

    import math

    import hashlib

    import threading

    import time

    Protect().start()

    import json as jsond

    import webbrowser

    import bettercam

    import numpy as np

    from ultralytics import YOLO

    import win32api

    from win32file import *

    from win32ui import *

    from win32con import *

    from win32gui import *

    from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QSlider, QHBoxLayout, QCheckBox, QComboBox, QFrame, QStackedWidget, QRadioButton, QButtonGroup, QGraphicsEllipseItem, QGraphicsView, QGraphicsScene

    from PyQt5.QtGui import QPainter, QColor, QPen, QIcon, QFont, QFontDatabase, QPixmap, QCursor, QImage, QBrush, QPolygon

    from PyQt5.QtCore import Qt, QSize, QTimer, QPoint, QRectF, pyqtSignal

    import serial

    from serial.tools import list_ports

    import binascii

    import platform

    import subprocess

    import datetime

    import wmi

    if os.name == 'nt':

        import win32security

    from Cryptodome.Cipher import AES

    from Cryptodome.Hash import SHA256

    from Cryptodome.Util.Padding import pad, unpad

    from datetime import datetime, timedelta

except Exception as e:

    if os.path.exists(r'C:\\ProgramData\\NezAI\\icons\\logo.png'):

        print(e)

    download_requirements()


Protect().start()



os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

sys.dont_write_bytecode = True



os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

os.environ["QT_SCALE_FACTOR"] = "1"



if hasattr(Qt, 'AA_EnableHighDpiScaling'):

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):

    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    

try:

    file = open('./config.json')

    config = jsond.load(file)

    Fov_Size = config.get('Fov_Size', 200)

    Confidence = config.get('Confidence', 56)

    Roundness = config.get('Roundness', 13)

    Outline_Thickness = config.get('Outline_Thickness', 2)

    Strength = config.get('Strength', 140)

    ADS_Strength = config.get('ADS_Strength', 170)

    Aim_Bone = config.get('Aim_Bone', 'Head')

    Mouse_Movement = config.get('Mouse_Movement', 'Default')

    Humanization = config.get('Humanization', 'Default')

    Aimbot = config.get('Aimbot', True)

    Norecoil = config.get ('Norecoil', False)

    Norecoil_senstivity = config.get('Norecoil_senstivity',1)

    Keybind = config.get('Keybind', 2)

    Backup_Keybind = config.get('Backup_Keybind', None)

    Overlay = config.get('Overlay', False)

    Fov = config.get('Fov', False)

    Box = config.get('Box', False)

    Box_Type = config.get('Box_Type', 'Default')

    Point = config.get('Point', False)

    Line = config.get('Line', False)

    Menu_Keybind = config.get('Menu_Keybind', 45)

    Fov_Thickness = config.get('Fov_Thickness', 1)

    Box_Thickness = config.get('Box_Thickness', 1)

    Line_Thickness = config.get('Line_Thickness', 1)

    Point_Thickness = config.get('Point_Thickness', 1)

    Fov_Outline = config.get('Fov_Outline', False)

    Box_Outline = config.get('Box_Outline', False)

    Line_Outline = config.get('Line_Outline', False)

    Point_Outline = config.get('Point_Outline', False)

    Fov_color = QColor(*config.get('Fov_color', (138, 66, 245, 255)))

    Box_color = QColor(*config.get('Box_color', (138, 66, 245, 255)))

    Line_color = QColor(*config.get('Line_color', (138, 66, 245, 255)))

    Point_color = QColor(*config.get('Point_color', (138, 66, 245, 255)))

    Gui_color = QColor(*config.get('Gui_color', (250, 0, 250, 255)))

    AI_Model = config.get("AI_Model")

except:

    os.makedirs('./', exist_ok=True)

    with open('./config.json', 'w') as file:

        jsond.dump({

    "Fov_Size": 200,

    "Confidence": 80,

    "Roundness": 13,

    "Outline_Thickness": 2,

    "Strength": 60,

    "ADS_Strength": 100,

    "Aim_Bone": "Head",

    "Mouse_Movement": "Default",

    "Humanization": "Default",

    "Aimbot": True,

    "NoRecoil": 0,

    "Norecoil_senstivity": 1,

    "Keybind": 2,

    "Backup_Keybind": None,

    "Overlay": False,

    "Fov": False,

    "Box": False,

    "Box_Type": "Default",

    "Point": False,

    "Line": False,

    "Menu_Keybind": 45,

    "Fov_Thickness": 1,

    "Box_Thickness": 1,

    "Line_Thickness": 1,

    "Point_Thickness": 1,

    "Fov_Outline": False,

    "Box_Outline": False,

    "Line_Outline": False,

    "Point_Outline": False,

    "Fov_color": (255, 255, 255, 255),

    "Box_color": (255, 255, 255, 255),

    "Line_color": (255, 255, 255, 255),

    "Point_color": (255, 255, 255, 255),

    "Gui_color": (157, 29, 144, 255),

    "Arduino_COM_Port": None,

    "AI_Model": "model.pt",

}, file, indent=4)



def download_assets():

    paths = ['C:\\ProgramData\\NezAI\\icons', 'C:\\ProgramData\\NezAI\\font', 'C:\\ProgramData\\NezAI\\models']



    for path in paths:

        os.makedirs(path, exist_ok=True)



    if not os.path.exists(r'C:\\ProgramData\\NezAI\\icons\\logo.png'):

        print("[Digital] -> downloading icons...")

        zip_path = r'C:\\ProgramData\\NezAI\\icons\\icons.zip'

        with open(zip_path, 'wb') as f:

            f.write(requests.get('https://www.dropbox.com/scl/fi/a23cijt55pn6vbjud8ovn/icons.zip?rlkey=28gpty55dzwabydttsyr1p9ap&st=s2mo89lo&dl=1').content)



        with zipfile.ZipFile(zip_path, 'r') as zip_ref:

            zip_ref.extractall(r'C:\\ProgramData\\NezAI')



        try:

            os.remove(zip_path)

        except Exception as e:

            print(f"[Digital] -> error removing zip file: {e}")



    if not os.path.exists(r'C:\\ProgramData\\NezAI\\font\\Font.ttf'):

        print("[Digital] -> downloading font...")

        zip_path = r'C:\\ProgramData\\NezAI\\font\\font.zip'

        with open(zip_path, 'wb') as f:

            f.write(requests.get('https://www.dropbox.com/scl/fi/ogvg5kkgge31euz16auqh/font.zip?rlkey=jo0gz1qoxvarub6tdj7vk01gt&st=pbdcxys5&dl=1').content)



        with zipfile.ZipFile(zip_path, 'r') as zip_ref:

            zip_ref.extractall(r'C:\\ProgramData\\NezAI')



        try:

            os.remove(zip_path)

        except Exception as e:

            print(f"[Digital] -> error removing zip file: {e}")



    if not os.path.exists(r'C:\\ProgramData\\NezAI\\models\model.pt'):

        print("[Digital] -> downloading models...")

        zip_path = r'C:\\ProgramData\\NezAI\\models\\models.zip'

        with open(zip_path, 'wb') as f:

            f.write(requests.get('https://www.dropbox.com/scl/fi/g8vhqqx3moy6wos0xr6t4/models.zip?rlkey=b3df38mgr7z16hkob92v6t8iq&st=snf6mhab&dl=1').content)



        with zipfile.ZipFile(zip_path, 'r') as zip_ref:

            zip_ref.extractall(r'C:\\ProgramData\\NezAI')



        try:

            os.remove(zip_path)

        except Exception as e:

            print(f"[Digital] -> error removing zip file: {e}")



download_assets()






screensize = {

    'X': ctypes.windll.user32.GetSystemMetrics(0),

    'Y': ctypes.windll.user32.GetSystemMetrics(1)

}



screen_res_X = screensize['X']

screen_res_Y = screensize['Y']



screen_x = int(screen_res_X // 2)

screen_y = int(screen_res_Y // 2)



os.system("cls")



import onnxruntime as ort

model = None  # Global model variable
model_type = None  # To track whether it's YOLO or ONNX

def load_model(model_path):
    global model, model_type
    if model_path.endswith('.pt') or model_path.endswith('.engine'):
        # Load YOLO model
        try:
            import torch_tensorrt
            model = YOLO(model_path, task="detect").to("cuda").half()
            model = torch_tensorrt.compile(
                model,
                inputs=[torch_tensorrt.Input((1, 3, 640, 640))],
                enabled_precisions={torch.float32},
            )
            model_type = "yolo"
        except:
            model = YOLO(model_path, task="detect")
            model_type = "yolo"
    elif model_path.endswith('.onnx'):
        # Load ONNX model
        providers = ['CUDAExecutionProvider'] if torch.cuda.is_available() else ['CPUExecutionProvider']
        model = ort.InferenceSession(model_path, providers=providers)
        model_type = "onnx"
    else:
        raise ValueError(f"Unsupported model format: {model_path}")
    os.system("cls")

# Initial model load
load_model("C:/ProgramData/NezAI/models/" + AI_Model)



KEY_NAMES = {

    0x01: "LMB",

    0x02: "RMB",

    0x03: "Control-Break",

    0x04: "MMB",

    0x05: "MB1",

    0x06: "MB2",

    0x08: "BACK",

    0x09: "TAB",

    0x0C: "CLR",

    0x0D: "ENTER",

    0x10: "SHFT",

    0x11: "CTRL",

    0x12: "ALT",

    0x13: "PAUSE",

    0x14: "CAPS",

    0x15: "IME Kana",

    0x19: "IME Kanji",

    0x1B: "ESC",

    0x20: "SPCE",

    0x21: "PG UP",

    0x22: "PG DN",

    0x23: "END",

    0x24: "HOME",

    0x25: "LEFT",

    0x26: "UP",

    0x27: "RIGHT",

    0x28: "DOWN",

    0x29: "SEL",

    0x2C: "NONE",

    0x2D: "INS",

    0x2E: "DEL",

    0x2F: "HELP",

    0x30: "0",

    0x31: "1",

    0x32: "2",

    0x33: "3",

    0x34: "4",

    0x35: "5",

    0x36: "6",

    0x37: "7",

    0x38: "8",

    0x39: "9",

    0x41: "A",

    0x42: "B",

    0x43: "C",

    0x44: "D",

    0x45: "E",

    0x46: "F",

    0x47: "G",

    0x48: "H",

    0x49: "I",

    0x4A: "J",

    0x4B: "K",

    0x4C: "L",

    0x4D: "M",

    0x4E: "N",

    0x4F: "O",

    0x50: "P",

    0x51: "Q",

    0x52: "R",

    0x53: "S",

    0x54: "T",

    0x55: "U",

    0x56: "V",

    0x57: "W",

    0x58: "X",

    0x59: "Y",

    0x5A: "Z",

    0x5B: "Left Win",

    0x5C: "Right Win",

    0x5D: "Apps",

    0x60: "Numpad 0",

    0x61: "Numpad 1",

    0x62: "Numpad 2",

    0x63: "Numpad 3",

    0x64: "Numpad 4",

    0x65: "Numpad 5",

    0x66: "Numpad 6",

    0x67: "Numpad 7",

    0x68: "Numpad 8",

    0x69: "Numpad 9",

    0x6A: "Numpad *",

    0x6B: "Numpad +",

    0x6C: "Numpad Enter",

    0x6D: "Numpad -",

    0x6E: "Numpad .",

    0x6F: "Numpad /",

    0x70: "F1",

    0x71: "F2",

    0x72: "F3",

    0x73: "F4",

    0x74: "F5",

    0x75: "F6",

    0x76: "F7",

    0x77: "F8",

    0x78: "F9",

    0x79: "F10",

    0x7A: "F11",

    0x7B: "F12",

    0x90: "NUMLOCK",

    0x91: "SCROLL",

    0xA0: "LSHIFT",

    0xA1: "RSHIFT",

    0xA2: "LCTRL",

    0xA3: "RCTRL",

    0xA4: "LALT",

    0xA5: "RALT",

    0xBA: ";",

    0xBB: "=",

    0xBC: ",",

    0xBD: "-",

    0xBE: ".",

    0xBF: "/",

    0xC0: "`",

    0xDB: "[",

    0xDC: "\\",

    0xDD: "]",

    0xDE: "'",

    0xE5: "IME PROCESS",

}


class ClickableLabel(QLabel):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setCursor(QCursor(Qt.PointingHandCursor))



    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            webbrowser.open("https://discord.gg/H7KZTVCTtV")

        super().mousePressEvent(event)



class CustomSlider(QSlider):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)



    def enterEvent(self, event):

        self.setCursor(QCursor(Qt.PointingHandCursor))

        super().enterEvent(event)



    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            slider_position = event.pos().x() if self.orientation() == Qt.Horizontal else event.pos().y()

            slider_length = self.width() if self.orientation() == Qt.Horizontal else self.height()

            ratio = slider_position / slider_length



            new_value = self.minimum() + ratio * (self.maximum() - self.minimum())

            self.setValue(int(new_value))



        super().mousePressEvent(event)



    def leaveEvent(self, event):

        self.setCursor(QCursor(Qt.ArrowCursor))

        super().leaveEvent(event)



class CustomSliderVertical(QSlider):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setStyleSheet("""

            QSlider::groove:vertical {

                border: none;

                border-radius: 3px;

                width: 10px;

                background: qlineargradient(

                    spread: pad, x1: 0, y1: 1, x2: 0, y2: 0,

                    stop: 0 #FF0000, stop: 0.17 #FFFF00,

                    stop: 0.33 #00FF00, stop: 0.50 #00FFFF,

                    stop: 0.67 #0000FF, stop: 0.83 #FF00FF,

                    stop: 1 #FF0000

                );

            }



            QSlider::handle:vertical {

                background: white;

                border: 1px solid #000000;

                width: 12px;

                height: 4px;

                margin: -2px -2px;

                border-radius: 2px;

            }

        """)



    def enterEvent(self, event):

        self.setCursor(QCursor(Qt.PointingHandCursor))

        super().enterEvent(event)



    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            if self.orientation() == Qt.Vertical:

                slider_position = self.height() - event.pos().y()

                slider_length = self.height()

            else:

                slider_position = event.pos().x()

                slider_length = self.width()



            ratio = slider_position / slider_length

            new_value = self.minimum() + ratio * (self.maximum() - self.minimum())

            self.setValue(int(new_value))



        super().mousePressEvent(event)



    def leaveEvent(self, event):

        self.setCursor(QCursor(Qt.ArrowCursor))

        super().leaveEvent(event)



class CustomRadioButton(QRadioButton):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)



    def enterEvent(self, event):

        self.setCursor(QCursor(Qt.PointingHandCursor))

        super().enterEvent(event)



    def leaveEvent(self, event):

        self.setCursor(QCursor(Qt.ArrowCursor))

        super().leaveEvent(event)



class CustomComboBox(QComboBox):

    def __init__(self, update_function=None, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.update_function = update_function



    def enterEvent(self, event):

        self.setCursor(QCursor(Qt.PointingHandCursor))

        super().enterEvent(event)



    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            if self.update_function is not None:

                self.update_function()

        super().mousePressEvent(event)



    def leaveEvent(self, event):

        self.setCursor(QCursor(Qt.ArrowCursor))

        super().leaveEvent(event)



class api:

    name = ownerid = version = hash_to_check = ""



    def __init__(self, name, ownerid, version, hash_to_check):

        self.name = name

        self.ownerid = ownerid

        self.version = version

        self.hash_to_check = hash_to_check

        self.init()



    sessionid = enckey = ""

    initialized = False



    def init(self):

        if self.sessionid != "":

            pass

        

        post_data = {

            "type": "init",

            "ver": self.version,

            "hash": self.hash_to_check,

            "name": self.name,

            "ownerid": self.ownerid

        }



        response = self.__do_request(post_data)



        if response == "KeyAuth_Invalid":

            show_console(True)

            print("The application doesn't exist")

            time.sleep(5)

            os._exit(1)



        json = jsond.loads(response)



        if json["message"] == "invalidver":

            if json["download"] != "":

                show_console(True)

                print("New Version Available")

                download_link = json["Download on discord /download"]

                os.system(f"start {download_link}")

                time.sleep(5)

                os._exit(1)

            else:

                show_console(True)

                print("Invalid Version, Download on discord /download")

                time.sleep(5)

                os._exit(1)



        if not json["success"]:

            show_console(True)

            print(json["message"])

            time.sleep(5)

            os._exit(1)



        self.sessionid = json["sessionid"]

        self.initialized = True



    def license(self, key, hwid=None):

        self.checkinit()

        if hwid is None:

            hwid = others.get_hwid()



        post_data = {

            "type": "license",

            "key": key,

            "hwid": hwid,

            "sessionid": self.sessionid,

            "name": self.name,

            "ownerid": self.ownerid

        }



        response = self.__do_request(post_data)



        json = jsond.loads(response)



        if json["success"]:

            try:

                self.__load_user_data(json["info"])

            except:

                exit(99)



            print("[Digital] -> launching...")



            key_file = open(rf"{os.getcwd()}\license.Digital", 'w')

            key_file.write(f"{key}")

            key_file.close()



            global Loaded

            Loaded = True



            AI.gui.load_gui()

        else:

            Loaded = False

            input("[Digital] -> invalid, expired or used license key\n")

            time.sleep(5)

            os._exit(1)



    def checkinit(self):

        if not self.initialized:

            show_console(True) 

            print("Initialize first, in order to use the functions")

            time.sleep(5)

            os._exit(1)



    def __do_request(self, post_data):

        try:

            response = requests.post("https://prod.keyauth.com/api/1.3/", data=post_data, timeout=10)



            if post_data["type"] == "log" or post_data["type"] == "file":

                return response.text



            signature = response.headers.get("x-signature-ed25519")

            timestamp = response.headers.get("x-signature-timestamp")



            if not signature or not timestamp:

                show_console(True)

                print("Ask for HWID change")

                time.sleep(5)

                os._exit(1)



            server_time = datetime.utcfromtimestamp(int(timestamp))

            current_time = datetime.utcnow()



            buffer_seconds = 5

            time_difference = current_time - server_time



            if time_difference > timedelta(seconds=20 + buffer_seconds):

                show_console(True)

                print("Please synchronize your device time.")

                time.sleep(5)

                os._exit(1)



            return response.text



        except requests.exceptions.Timeout:

            caption = "Error!"

            message = ("Request timed out.")

            message_type = 0x10

            ctypes.windll.user32.MessageBoxW(0, message, caption, message_type)



            try:

                console_window = ctypes.windll.kernel32.GetConsoleWindow()

                ctypes.windll.user32.PostMessageW(console_window, 0x10, 0, 0)

            except:

                try:

                    sys.exit()

                except:

                    os.system('taskkill /f /fi "imagename eq cmd.exe" 1>NUL 2>NUL')



    class user_data_class:

        username = ip = hwid = expires = createdate = lastlogin = subscription = subscriptions = ""



    user_data = user_data_class()



    def __load_user_data(self, data):

        self.user_data.username = data["username"]

        self.user_data.ip = data["ip"]

        self.user_data.hwid = data["hwid"] or "N/A"

        self.user_data.expires = data["subscriptions"][0]["expiry"]

        self.user_data.createdate = data["createdate"]

        self.user_data.lastlogin = data["lastlogin"]

        self.user_data.subscription = data["subscriptions"][0]["subscription"]

        self.user_data.subscriptions = data["subscriptions"]

        

class encryption:

    @staticmethod

    def encrypt_string(plain_text, key, iv):

        plain_text = pad(plain_text, 16)

        aes_instance = AES.new(key, AES.MODE_CBC, iv)

        raw_out = aes_instance.encrypt(plain_text)

        return binascii.hexlify(raw_out)



    @staticmethod

    def decrypt_string(cipher_text, key, iv):

        cipher_text = binascii.unhexlify(cipher_text)

        aes_instance = AES.new(key, AES.MODE_CBC, iv)

        cipher_text = aes_instance.decrypt(cipher_text)

        return unpad(cipher_text, 16)



    @staticmethod

    def encrypt(message, enc_key, iv):

        try:

            _key = SHA256.new(enc_key.encode()).hexdigest()[:32]

            _iv = SHA256.new(iv.encode()).hexdigest()[:16]

            return encryption.encrypt_string(message.encode(), _key.encode(), _iv.encode()).decode()

        except:

            print("encrypt error")

            os._exit(1)



    @staticmethod

    def decrypt(message, enc_key, iv):

        try:

            _key = SHA256.new(enc_key.encode()).hexdigest()[:32]

            _iv = SHA256.new(iv.encode()).hexdigest()[:16]

            return encryption.decrypt_string(message.encode(), _key.encode(), _iv.encode()).decode()

        except:

            print("decrypt error")

            os._exit(1)



class ColorPicker(QWidget):

    color_changed = pyqtSignal(QColor)



    def __init__(self, label="... Color", color=QColor):

        super().__init__()

        layout = QHBoxLayout(self)

        layout.setContentsMargins(12, 2, 0, 0)



        self.view = QGraphicsView()

        self.view.setFixedSize(60, 60)

        self.view.setAlignment(Qt.AlignCenter)

        self.view.setStyleSheet("border: none;")

        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.view.setRenderHint(QPainter.Antialiasing)



        self.scene = QGraphicsScene(self)

        self.view.setScene(self.scene)



        self.color_slider = CustomSliderVertical(Qt.Vertical)

        self.color_slider.setRange(0, 359)

        self.color_slider.setValue(color.hue())

        self.color_slider.setMaximumHeight(60)



        self.color_label = QLabel(f"{label}")



        self.color_slider.valueChanged.connect(self.update_color_picker)



        self.layout_with_color_picker = QHBoxLayout()

        self.layout_with_color_picker.addWidget(self.view)



        self.layout_with_slider = QHBoxLayout()

        self.layout_with_slider.addWidget(self.color_slider)

        self.layout_with_slider.addStretch(False)



        self.layout_with_label = QHBoxLayout()

        self.layout_with_label.addWidget(self.color_label)

        self.layout_with_label.addSpacing(252)

        

        layout.addLayout(self.layout_with_color_picker)

        layout.addLayout(self.layout_with_slider)

        layout.addLayout(self.layout_with_label)



        self.hue = color.hue()

        self.last_selected_pos = self.color_to_position(color)

        self.create_color_picker()



        self.selector = QGraphicsEllipseItem(2, 2, 6, 6)

        self.selector.setBrush(Qt.black)

        self.selector.setPen(Qt.black)

        self.scene.addItem(self.selector)

        self.update_selector_position(self.last_selected_pos)



        self.view.setMouseTracking(True)

        self.view.viewport().installEventFilter(self)

        self.is_mouse_pressed = False



    def color_to_position(self, color):

        saturation = color.saturation() / 255

        value = color.value() / 255

        

        x = saturation * 60

        y = (1 - value) * 60

        

        return (x, y)



    def create_color_picker(self):

        width, height = 60, 60

        image = QImage(width, height, QImage.Format_RGB32)

        painter = QPainter(image)



        for x in range(width):

            for y in range(height):

                saturation = int(x / width * 255)

                value = int((height - y) / height * 255)

                color = QColor.fromHsv(self.hue, max(0, min(255, saturation)), max(0, min(255, value)))

                painter.setPen(color)

                painter.drawPoint(x, y)



        painter.end()

        

        pixmap = QPixmap.fromImage(image)

        self.color_item = self.scene.addPixmap(pixmap)

        self.color_item.setPos(0, 0)



    def update_color_picker(self):

        self.hue = self.color_slider.value()

        self.scene.clear()

        self.create_color_picker()

        

        self.selector = QGraphicsEllipseItem(2, 2, 6, 6)

        self.selector.setBrush(Qt.white)

        self.selector.setPen(Qt.black)

        self.scene.addItem(self.selector)

        

        self.update_selector_position(self.last_selected_pos)

        

        self.pixel_color = self.get_color_at(self.last_selected_pos)

        self.color_changed.emit(self.pixel_color)



    def eventFilter(self, source, event):

        if source == self.view.viewport():

            if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:

                self.is_mouse_pressed = True

                pos = event.pos()

                scene_pos = self.view.mapToScene(pos)

                if self.color_item.contains(scene_pos):

                    self.last_selected_pos = (scene_pos.x(), scene_pos.y())

                    self.update_selector_position(self.last_selected_pos)

                    self.pixel_color = self.get_color_at(self.last_selected_pos)

                    self.color_changed.emit(self.pixel_color)



            elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:

                self.is_mouse_pressed = False

            elif event.type() == event.MouseMove and self.is_mouse_pressed:

                pos = event.pos()

                scene_pos = self.view.mapToScene(pos)

                if self.color_item.contains(scene_pos):

                    self.last_selected_pos = (scene_pos.x(), scene_pos.y())

                    self.update_selector_position(self.last_selected_pos)

                    self.pixel_color = self.get_color_at(scene_pos)

                    self.color_changed.emit(self.pixel_color)



        return super().eventFilter(source, event)



    def update_selector_position(self, pos):

        x, y = pos

        self.selector.setPos(x - 5, y - 5)



    def get_color_at(self, pos):

        if isinstance(pos, tuple):

            x, y = int(pos[0]), int(pos[1])

        else:

            x, y = int(pos.x()), int(pos.y())

            

        pixmap = self.color_item.pixmap()

        image = pixmap.toImage()

        if 0 <= x < image.width() and 0 <= y < image.height():

            color = QColor(image.pixel(x, y))

            return color

        return QColor()



class License():

    def check_license():

        def getchecksum():

            md5_hash = hashlib.md5()

            file = open(''.join(sys.argv), "rb")

            md5_hash.update(file.read())

            digest = md5_hash.hexdigest()

            return digest



        auth = api(

            name = "Test",

            ownerid = "8lNWyaNuge",

            version = "1.0",

            hash_to_check = getchecksum()

        )



        auth.init()



        license_key = AI.gui.text_input_license.text()  



        print("[Digital] -> logging in...")

        auth.license(license_key)



    def auto_login():

        license_key = ""



        try:

            key_file = open(rf"{os.getcwd()}\license.Digital", "r")

            license_key = key_file.read()

            key_file.close()

        except:

            pass



        def getchecksum():

            md5_hash = hashlib.md5()

            file = open(''.join(sys.argv), "rb")

            md5_hash.update(file.read())

            digest = md5_hash.hexdigest()

            return digest

        

        auth = api(

            name = "Test",

            ownerid = "8lNWyaNuge",

            version = "1.0",

            hash_to_check = getchecksum()

        )



        auth.init()



        if license_key == "":

            return

        

        print("[Digital] -> logging in...")

        auth.license(license_key)


class GUI(QWidget):

    


    def toggle_overlay(self, state):
        if state == Qt.Checked:
            print("Overlay Enabled")
        else:
            print("Overlay Disabled")



    def __init__(self):

        super().__init__()

        self.init_ui()

        self.is_dragging = False

        self.drag_position = QPoint()

        self.is_selecting_menu_hotkey = False

        self.Norecoil_offset = 0  
        self.start_global_mouse_listener()
        self.is_left_held = False
        self.is_right_held = False




    def disable_events(self, combo_box):

        def block_event(event):

            event.ignore()



        combo_box.wheelEvent = block_event

        combo_box.keyPressEvent = block_event



    def start_global_mouse_listener(self):
        listener_thread = threading.Thread(target=self.run_mouse_listener, daemon=True)
        listener_thread.start()
        movement_thread = threading.Thread(target=self.move_mouse_continuously, daemon=True)
        movement_thread.start()

    def run_mouse_listener(self):
        def on_click(x, y, button, pressed):
            if self.Norecoil_checkbox.isChecked():  
                current_pos = pyautogui.position()  

                if button == mouse.Button.left:  
                    if pressed:
                        self.is_left_held = True
                        new_pos = (current_pos[0], current_pos[1] + Norecoil_senstivity)
                        pyautogui.moveTo(new_pos[0], new_pos[1], duration=0.01)  
                        print("Left Click - Moving Down")
                    else:
                        self.is_left_held = False  

                elif button == mouse.Button.right: 
                    if pressed:
                        self.is_right_held = True
                        new_pos = (current_pos[0], current_pos[1] - Norecoil_senstivity)
                        pyautogui.moveTo(new_pos[0], new_pos[1], duration=0.01) 
                        print("Right Click - Moving Up")
                    else:
                        self.is_right_held = False 
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
    def move_mouse_continuously(self):
        while True:
            if self.Norecoil_checkbox.isChecked():
                current_pos = pyautogui.position()
                if self.is_left_held:
                    new_pos = (current_pos[0], current_pos[1] + Norecoil_senstivity)
                    pyautogui.moveTo(new_pos[0], new_pos[1], duration=0.05)
                    print("Holding Left Click - Moving Down")
                if self.is_right_held:
                    new_pos = (current_pos[0], current_pos[1] - Norecoil_senstivity)
                    pyautogui.moveTo(new_pos[0], new_pos[1], duration=0.05)  
                    print("Holding Right Click - Moving Up")

            time.sleep(0.01)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.pos().y() < 20:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.pos()
        if self.Norecoil_checkbox.isChecked():
            if event.button() == Qt.RightButton:  
                self.Norecoil_offset -= Norecoil_senstivity
                print("Right Click - Moving Up")
            elif event.button() == Qt.LeftButton: 
                self.Norecoil_offset += Norecoil_senstivity  
                print("Left Click - Moving Down")
            self.adjust_mouse_position()

        event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
        event.accept()

    def adjust_mouse_position(self):
        current_pos = QCursor.pos()
        new_pos = QPoint(current_pos.x(), current_pos.y() + self.Norecoil_offset)
        QCursor.setPos(new_pos)

    def init_ui(self):

        global Fov_Size, Confidence, Strength, ADS_Strength, Aim_Bone, Mouse_Movement, Humanization, AI_Model, Aimbot, Keybind, Backup_Keybind, Menu_Keybind, Overlay, Fov_color, Box_color, Line_color, Point_color, Fov, Box, Box_Type, Roundness, Outline_Thickness, Point, Line, Fov_Thickness, Box_Thickness, Line_Thickness, Point_Thickness, Fov_Outline, Box_Outline, Line_Outline, Point_Outline, Arduino_COM_Port

        try:

            self.Keybind = Keybind

            self.Backup_Keybind = Backup_Keybind

            self.Menu_Keybind = Menu_Keybind

            self.Fov_Size = Fov_Size

            self.Confidence = Confidence

            self.Strength = Strength

            self.ADS_Strength = ADS_Strength

            self.Aim_Bone = Aim_Bone

            self.Mouse_Movement = Mouse_Movement

            self.Humanization = Humanization

            self.Aimbot = Aimbot

            self.Overlay = Overlay

            self.Fov = Fov

            self.Box = Box

            self.Box_Type = Box_Type

            self.Point = Point

            self.Line = Line

            self.Roundness = Roundness

            self.Outline_Thickness = Outline_Thickness

            self.Fov_Thickness = Fov_Thickness

            self.Box_Thickness = Box_Thickness

            self.Line_Thickness = Line_Thickness

            self.Point_Thickness = Point_Thickness

            self.Fov_Outline = Fov_Outline

            self.Box_Outline = Box_Outline

            self.Line_Outline = Line_Outline

            self.Point_Outline = Point_Outline

            self.Fov_color = Fov_color

            self.Box_color = Box_color

            self.Line_color = Line_color

            self.Point_color = Point_color

            self.AI_Model = AI_Model

        except:

            restart_program()



        self.timer = QTimer(self)

        self.timer.timeout.connect(self.update)

        self.timer.start(300)



        self.setWindowTitle(" ")

        self.setWindowOpacity(0.98)

        self.setFixedSize(550, 350)



        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.setWindowFlag(Qt.MSWindowsFixedSizeDialogHint, True)

        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)

        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.setWindowFlag(Qt.FramelessWindowHint, True)

        self.setWindowFlag(Qt.Tool, False)

        self.setWindowIcon(QIcon("C:/ProgramData/NezAI/icons/logo.png"))

        user32.SetWindowDisplayAffinity(int(self.winId()), 0x00000000)

        self.theme_hex_color = Gui_color.name()

        self.widget_bg_color = "#1E1E1E"



        font_id = QFontDatabase.addApplicationFont("C:/ProgramData/NezAI/font/Font.ttf")

        if font_id != -1:

            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

            custom_font = QFont(font_family, 13)

            QApplication.setFont(custom_font)



        # AIMING SETTINGS START

        self.Fov_label = QLabel(

            f"FOV: {str(Fov_Size)} px")

        self.Fov_slider = CustomSlider(Qt.Horizontal)

        self.disable_events(self.Fov_slider)

        self.Fov_slider.setStyleSheet(self.get_slider_style())

        self.Fov_slider.setMaximumWidth(160)

        self.Fov_slider.setMinimumWidth(160)

        self.Fov_slider.setMinimum(100)

        self.Fov_slider.setMaximum(450)

        self.Fov_slider.setValue(int(round(Fov_Size)))



        self.Strength_label = QLabel(

            f"Strength: {str(Strength)}%")

        self.Strength_slider = CustomSlider(Qt.Horizontal)

        self.disable_events(self.Strength_slider)

        self.Strength_slider.setStyleSheet(self.get_slider_style())

        self.Strength_slider.setMaximumWidth(160)

        self.Strength_slider.setMinimumWidth(160)

        self.Strength_slider.setMinimum(10)

        self.Strength_slider.setMaximum(700)

        self.Strength_slider.setValue(int(round(Strength)))



        self.ADS_Strength_label = QLabel(

            f"ADS Strength: {str(ADS_Strength)}%")

        self.ADS_Strength_slider = CustomSlider(Qt.Horizontal)

        self.disable_events(self.ADS_Strength_slider)

        self.ADS_Strength_slider.setStyleSheet(self.get_slider_style())

        self.ADS_Strength_slider.setMaximumWidth(160)

        self.ADS_Strength_slider.setMinimumWidth(160)

        self.ADS_Strength_slider.setMinimum(10)

        self.ADS_Strength_slider.setMaximum(700)

        self.ADS_Strength_slider.setValue(int(round(ADS_Strength)))



        self.aim_bone_label = QLabel("Aim Bone")



        self.aim_bone_head = CustomRadioButton("Head")

        self.aim_bone_head.setStyleSheet(self.get_radio_button_style())

        self.aim_bone_neck = CustomRadioButton("Neck")

        self.aim_bone_neck.setStyleSheet(self.get_radio_button_style())

        self.aim_bone_torso = CustomRadioButton("Torso")

        self.aim_bone_torso.setStyleSheet(self.get_radio_button_style())

        self.aim_bone_nearest = CustomRadioButton("Nearest")

        self.aim_bone_nearest.setStyleSheet(self.get_radio_button_style())



        self.aim_bone_group = QButtonGroup(self)

        self.aim_bone_group.addButton(self.aim_bone_head)

        self.aim_bone_group.addButton(self.aim_bone_neck)

        self.aim_bone_group.addButton(self.aim_bone_torso)

        self.aim_bone_group.addButton(self.aim_bone_nearest)



        def update_selected_bone(button):
            self.Aim_Bone = button.text()
            self.save_config()

        self.aim_bone_group.buttonClicked.connect(update_selected_bone)

        if self.Aim_Bone == "Head":
            self.aim_bone_head.setChecked(True)
        elif self.Aim_Bone == "Neck":
            self.aim_bone_neck.setChecked(True)
        elif self.Aim_Bone == "Torso":
            self.aim_bone_torso.setChecked(True)
        else:
            self.aim_bone_nearest.setChecked(True)

        self.Aim_Bone = self.aim_bone_group.checkedButton().text()

        # Existing Mouse Movement Options
        self.mouse_movement_type_label = QLabel("Mouse Movement")

        self.mouse_movement_group = QButtonGroup(self)

        self.mouse_movement_default = QRadioButton("Default")
        self.mouse_movement_default.setStyleSheet(self.get_radio_button_style())

        self.mouse_movement_arduino = QRadioButton("Arduino")
        self.mouse_movement_arduino.setStyleSheet(self.get_radio_button_style())

        self.mouse_movement_makcu = QRadioButton("Makcu")
        self.mouse_movement_makcu.setStyleSheet(self.get_radio_button_style())
        self.mouse_movement_group.addButton(self.mouse_movement_makcu)


        self.Norecoil_checkbox = QCheckBox("Norecoil")

        self.Norecoil_checkbox.setCursor(QCursor(Qt.PointingHandCursor))

        self.Norecoil_checkbox.setChecked(Norecoil)

        self.Norecoil_checkbox.setCheckable(True)

        self.Norecoil_checkbox.setStyleSheet(self.get_toggle_button_style())
      

        


        self.Norecoil_label = QLabel(

            f"Senstivity: {str(Norecoil_senstivity)}%")

        self.Norecoil_slider = CustomSlider(Qt.Horizontal)

        self.disable_events(self.Norecoil_slider)

        self.Norecoil_slider.setStyleSheet(self.get_slider_style())

        self.Norecoil_slider.setMaximumWidth(160)

        self.Norecoil_slider.setMinimumWidth(160)

        self.Norecoil_slider.setMinimum(1)

        self.Norecoil_slider.setMaximum(20)

        self.Norecoil_slider.setValue(int(round(Norecoil_senstivity)))
        self.mouse_movement_group = QButtonGroup(self)
        self.mouse_movement_group.addButton(self.mouse_movement_default)
        self.mouse_movement_group.addButton(self.mouse_movement_arduino)
        self.mouse_movement_group.addButton(self.mouse_movement_makcu)
        self.mouse_movement_group.addButton(self.Norecoil_checkbox)
        
      
       
     

        self.mouse_movement_default.setChecked(True)



        def update_mouse_movement(button):

            self.Mouse_Movement = button.text()
            if self.Norecoil_checkbox.isChecked():
                self.set_widgets_visible([self.Norecoil_label, self.Norecoil_slider], True)
            else:
                self.set_widgets_visible([self.Norecoil_label, self.Norecoil_slider], False)

            self.set_widgets_visible([self.Norecoil_label, self.Norecoil_checkbox,self.Norecoil_slider], self.Mouse_Movement == "Default")

            self.save_config()



        self.mouse_movement_group.buttonClicked.connect(update_mouse_movement)



        if self.Mouse_Movement == "Default":

            self.mouse_movement_default.setChecked(True)



        self.Norecoil_checkbox = QCheckBox("Norecoil")

        self.Norecoil_checkbox.setCursor(QCursor(Qt.PointingHandCursor))

        self.Norecoil_checkbox.setChecked(Norecoil)

        self.Norecoil_checkbox.setCheckable(True)

        self.Norecoil_checkbox.setStyleSheet(self.get_toggle_button_style())



        if self.Mouse_Movement == "Arduino":

            self.mouse_movement_arduino.setChecked(True)

        elif self.Mouse_Movement == "MAKCU":
            self.mouse_movement_makcu.setChecked(True)
        else:
            self.mouse_movement_default.setChecked(True)




       



        self.AI_Model_label = QLabel("AI Model")

        self.AI_Model_combobox = CustomComboBox(None)

        self.disable_events(self.AI_Model_combobox)

        self.update_models()

        self.AI_Model_combobox.setStyleSheet(self.get_combo_box_style())

        self.AI_Model = self.AI_Model_combobox.currentText()

        self.AI_Model_combobox.setCurrentText(AI_Model)



        self.humanization_type_label = QLabel("Humanization")



        self.humanization_default = QRadioButton("Default")

        self.humanization_default.setStyleSheet(self.get_radio_button_style())

        self.humanization_bezier = QRadioButton("Bezier")

        self.humanization_bezier.setStyleSheet(self.get_radio_button_style())

        self.humanization_catmull_rom = QRadioButton("Catmull-Rom")

        self.humanization_catmull_rom.setStyleSheet(self.get_radio_button_style())



        self.humanization_group = QButtonGroup(self)

        self.humanization_group.addButton(self.humanization_default)

        self.humanization_group.addButton(self.humanization_bezier)

        self.humanization_group.addButton(self.humanization_catmull_rom)



        self.humanization_default.setChecked(True)



        def update_humanization(button):

            self.Humanization = button.text()

            self.save_config()



        self.humanization_group.buttonClicked.connect(update_humanization)



        if self.Humanization == "Default":

            self.humanization_default.setChecked(True)

        elif self.Humanization == "Bezier":

            self.humanization_bezier.setChecked(True)

        elif self.Humanization == "Catmull-Rom":

            self.humanization_catmull_rom.setChecked(True)



        self.Aimbot_checkbox = QCheckBox("Aimbot")

        self.Aimbot_checkbox.setCursor(QCursor(Qt.PointingHandCursor))

        self.Aimbot_checkbox.setChecked(Aimbot)

        self.Aimbot_checkbox.setCheckable(True)

        self.Aimbot_checkbox.setStyleSheet(self.get_toggle_button_style())



        self.aimbot_key_name = "None" if Keybind is None else KEY_NAMES.get(Keybind, f"0x{Keybind:02X}")

        self.hotkey_label = QLabel("Keybind")

        self.btn_hotkey = QPushButton(f"{self.aimbot_key_name}")

        self.btn_hotkey.setStyleSheet(self.get_button_style())

        self.btn_hotkey.setMinimumWidth(55)

        self.btn_hotkey.setMaximumWidth(55)

        self.btn_hotkey.setMinimumHeight(22)

        self.btn_hotkey.setMaximumHeight(22)

        self.btn_hotkey.clicked.connect(self.start_select_hotkey)



        self.aimbot_backup_key_name = "None" if Backup_Keybind is None else KEY_NAMES.get(Backup_Keybind, f"0x{Backup_Keybind:02X}")

        self.backup_hotkey_label = QLabel("Backup Keybind")

        self.btn_backup_hotkey = QPushButton(f"{self.aimbot_backup_key_name}")

        self.btn_backup_hotkey.setStyleSheet(self.get_button_style())

        self.btn_backup_hotkey.setMinimumWidth(55)

        self.btn_backup_hotkey.setMaximumWidth(55)

        self.btn_backup_hotkey.setMinimumHeight(22)

        self.btn_backup_hotkey.setMaximumHeight(22)

        self.btn_backup_hotkey.clicked.connect(self.start_select_backup_hotkey)

        # AIMING SETTINGS END



        # VISUAL SETTINGS START

        self.Overlay_checkbox = QCheckBox("Overlay")
        self.Overlay_checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.Overlay_checkbox.setChecked(Overlay)
        self.Overlay_checkbox.setCheckable(True)
        self.Overlay_checkbox.setStyleSheet(self.get_toggle_button_style())
        self.Overlay_checkbox.stateChanged.connect(self.toggle_overlay)





        self.Fov_checkbox = QCheckBox("Show FOV")

        self.Fov_checkbox.setCursor(QCursor(Qt.PointingHandCursor))

        self.Fov_checkbox.setChecked(Fov)

        self.Fov_checkbox.setCheckable(True)

        self.Fov_checkbox.setStyleSheet(self.get_toggle_button_style())



        self.Box_checkbox = QCheckBox("Show Box")

        self.Box_checkbox.setCursor(QCursor(Qt.PointingHandCursor))

        self.Box_checkbox.setChecked(Box)

        self.Box_checkbox.setCheckable(True)

        self.Box_checkbox.setStyleSheet(self.get_toggle_button_style())



        self.Line_checkbox = QCheckBox("Show Tracer")

        self.Line_checkbox.setCursor(QCursor(Qt.PointingHandCursor))

        self.Line_checkbox.setChecked(Line)

        self.Line_checkbox.setCheckable(True)

        self.Line_checkbox.setStyleSheet(self.get_toggle_button_style())



        self.Point_checkbox = QCheckBox("Show Point")

        self.Point_checkbox.setCursor(QCursor(Qt.PointingHandCursor))

        self.Point_checkbox.setChecked(Point)

        self.Point_checkbox.setCheckable(True)

        self.Point_checkbox.setStyleSheet(self.get_toggle_button_style())



        self.Fov_outline_checkbox = QCheckBox("FOV Outline")

        self.Fov_outline_checkbox.setCursor(QCursor(Qt.PointingHandCursor))

        self.Fov_outline_checkbox.setChecked(Fov_Outline)

        self.Fov_outline_checkbox.setCheckable(True)

        self.Fov_outline_checkbox.setStyleSheet(self.get_toggle_button_style())



        self.Box_outline_checkbox = QCheckBox("Box Outline")

        self.Box_outline_checkbox.setCursor(QCursor(Qt.PointingHandCursor))

        self.Box_outline_checkbox.setChecked(Box_Outline)

        self.Box_outline_checkbox.setCheckable(True)

        self.Box_outline_checkbox.setStyleSheet(self.get_toggle_button_style())



        self.Line_outline_checkbox = QCheckBox("Tracer Outline")

        self.Line_outline_checkbox.setCursor(QCursor(Qt.PointingHandCursor))

        self.Line_outline_checkbox.setChecked(Line_Outline)

        self.Line_outline_checkbox.setCheckable(True)

        self.Line_outline_checkbox.setStyleSheet(self.get_toggle_button_style())



        self.Point_outline_checkbox = QCheckBox("Point Outline")

        self.Point_outline_checkbox.setCursor(QCursor(Qt.PointingHandCursor))

        self.Point_outline_checkbox.setChecked(Point_Outline)

        self.Point_outline_checkbox.setCheckable(True)

        self.Point_outline_checkbox.setStyleSheet(self.get_toggle_button_style())



        self.Fov_Thickness_label = QLabel(

            f"FOV Thickness: {str(Fov_Thickness)} px")

        self.Fov_Thickness_slider = CustomSlider(Qt.Horizontal)

        self.disable_events(self.Fov_Thickness_slider)

        self.Fov_Thickness_slider.setStyleSheet(self.get_slider_style())

        self.Fov_Thickness_slider.setMaximumWidth(160)

        self.Fov_Thickness_slider.setMinimumWidth(160)

        self.Fov_Thickness_slider.setMinimum(1)

        self.Fov_Thickness_slider.setMaximum(3)

        self.Fov_Thickness_slider.setValue(int(round(Fov_Thickness)))



        self.Box_Thickness_label = QLabel(

            f"Box Thickness: {str(Box_Thickness)} px")

        self.Box_Thickness_slider = CustomSlider(Qt.Horizontal)

        self.disable_events(self.Box_Thickness_slider)

        self.Box_Thickness_slider.setStyleSheet(self.get_slider_style())

        self.Box_Thickness_slider.setMaximumWidth(160)

        self.Box_Thickness_slider.setMinimumWidth(160)

        self.Box_Thickness_slider.setMinimum(1)

        self.Box_Thickness_slider.setMaximum(3)

        self.Box_Thickness_slider.setValue(int(round(Box_Thickness)))



        self.Line_Thickness_label = QLabel(

            f"Line Thickness: {str(Line_Thickness)} px")

        self.Line_Thickness_slider = CustomSlider(Qt.Horizontal)

        self.disable_events(self.Line_Thickness_slider)

        self.Line_Thickness_slider.setStyleSheet(self.get_slider_style())

        self.Line_Thickness_slider.setMaximumWidth(160)

        self.Line_Thickness_slider.setMinimumWidth(160)

        self.Line_Thickness_slider.setMinimum(1)

        self.Line_Thickness_slider.setMaximum(3)

        self.Line_Thickness_slider.setValue(int(round(Line_Thickness)))



        self.Point_Thickness_label = QLabel(

            f"Point Thickness: {str(Point_Thickness)} px")

        self.Point_Thickness_slider = CustomSlider(Qt.Horizontal)

        self.disable_events(self.Point_Thickness_slider)

        self.Point_Thickness_slider.setStyleSheet(self.get_slider_style())

        self.Point_Thickness_slider.setMaximumWidth(160)

        self.Point_Thickness_slider.setMinimumWidth(160)

        self.Point_Thickness_slider.setMinimum(1)

        self.Point_Thickness_slider.setMaximum(3)

        self.Point_Thickness_slider.setValue(int(round(Point_Thickness)))



        self.box_type_label = QLabel("Box Type")

        self.box_type_default = QRadioButton("Default")

        self.box_type_default.setStyleSheet(self.get_radio_button_style())

        self.box_type_corner = QRadioButton("Corner")

        self.box_type_corner.setStyleSheet(self.get_radio_button_style())

        self.box_type_filled = QRadioButton("Filled")

        self.box_type_filled.setStyleSheet(self.get_radio_button_style())



        self.box_type_group = QButtonGroup(self)

        self.box_type_group.addButton(self.box_type_default)

        self.box_type_group.addButton(self.box_type_corner)

        self.box_type_group.addButton(self.box_type_filled)



        self.box_type_default.setChecked(True)



        def update_box_type(button):

            global Box_Type

            Box_Type = button.text()

            self.save_config()




        self.box_type_group.buttonClicked.connect(update_box_type)



        if Box_Type == "Default":

            self.box_type_default.setChecked(True)

        elif Box_Type == "Corner":

            self.box_type_corner.setChecked(True)

        elif Box_Type == "Filled":

            self.box_type_filled.setChecked(True)



        self.menu_key_name = "None" if Menu_Keybind is None else KEY_NAMES.get(Menu_Keybind, f"0x{Menu_Keybind:02X}")

        

        self.menu_label = QLabel("Menu Keybind")

        self.menu_hotkey = QPushButton(f"{self.menu_key_name}")

        self.menu_hotkey.setStyleSheet(self.get_button_style())

        self.menu_hotkey.setMinimumWidth(55)

        self.menu_hotkey.setMaximumWidth(55)

        self.menu_hotkey.setMinimumHeight(22)

        self.menu_hotkey.setMaximumHeight(22)

        self.menu_hotkey.clicked.connect(self.start_select_menu_hotkey)



        self.Confidence_label = QLabel(f"Confidence: {str(Confidence)}%")

        self.Confidence_slider = CustomSlider(Qt.Horizontal)

        self.disable_events(self.Confidence_slider)

        self.Confidence_slider.setStyleSheet(self.get_slider_style())

        self.Confidence_slider.setMaximumWidth(160)

        self.Confidence_slider.setMinimumWidth(160)

        self.Confidence_slider.setMinimum(20)

        self.Confidence_slider.setMaximum(95)

        self.Confidence_slider.setValue(int(round(Confidence)))



        self.Roundness_label = QLabel(f"GUI Roundness: {str(Roundness)}")

        self.Roundness_slider = CustomSlider(Qt.Horizontal)

        self.disable_events(self.Roundness_slider)

        self.Roundness_slider.setStyleSheet(self.get_slider_style())

        self.Roundness_slider.setMaximumWidth(160)

        self.Roundness_slider.setMinimumWidth(160)

        self.Roundness_slider.setMinimum(0)

        self.Roundness_slider.setMaximum(20)

        self.Roundness_slider.setValue(int(round(Roundness)))



        self.Outline_Thickness_label = QLabel(f"GUI Outline Thickness: {str(Outline_Thickness)}")

        self.Outline_Thickness_slider = CustomSlider(Qt.Horizontal)

        self.disable_events(self.Outline_Thickness_slider)

        self.Outline_Thickness_slider.setStyleSheet(self.get_slider_style())

        self.Outline_Thickness_slider.setMaximumWidth(160)

        self.Outline_Thickness_slider.setMinimumWidth(160)

        self.Outline_Thickness_slider.setMinimum(0)

        self.Outline_Thickness_slider.setMaximum(3)

        self.Outline_Thickness_slider.setValue(int(round(Outline_Thickness)))

        

        self.User_Info_label = QLabel(f"User Info:")

        self.User_Info_key = QLabel(f"Your Key: *******")

        self.User_Info_expiry = QLabel(f"Expiry: *******")

        self.User_Info_purchased = QLabel(f"Purchased: *******")



        btn_aimbot = QPushButton()

        btn_aimbot.setCursor(QCursor(Qt.PointingHandCursor))

        btn_aimbot.setObjectName("menu_tab_aimbot")

        btn_aimbot.setIcon(QIcon(f"C:/ProgramData/NezAI/icons/aimbot.png"))

        btn_aimbot.setStyleSheet(self.menu_tab_selected_style())

        btn_aimbot.setIconSize(QSize(25, 25))



        btn_visual = QPushButton()

        btn_visual.setCursor(QCursor(Qt.PointingHandCursor))

        btn_visual.setObjectName("menu_tab_visual")

        btn_visual.setIcon(QIcon(f"C:/ProgramData/NezAI/icons/visuals.png"))

        btn_visual.setStyleSheet(self.menu_tab_selected_style())

        btn_visual.setIconSize(QSize(25, 25))



        btn_profile = QPushButton()

        btn_profile.setCursor(QCursor(Qt.PointingHandCursor))

        btn_profile.setIcon(QIcon(f"C:/ProgramData/NezAI/icons/profile.png"))

        btn_profile.setObjectName("menu_tab_profile")

        btn_profile.setStyleSheet(self.menu_tab_selected_style())

        btn_profile.setIconSize(QSize(25, 25))



        btn_aiming = QPushButton("General")

        btn_aiming.setCursor(QCursor(Qt.PointingHandCursor))

        btn_advanced = QPushButton("Advanced")

        btn_advanced.setCursor(QCursor(Qt.PointingHandCursor))

        btn_humanization = QPushButton("Humanization")

        btn_humanization.setCursor(QCursor(Qt.PointingHandCursor))



        def update_aimbot_button_style(index):

            selected_style = "color: white; font-weight: bold;"

            unselected_style = "color: gray; font-weight: normal;"



            btn_aiming.setStyleSheet(unselected_style)

            btn_advanced.setStyleSheet(unselected_style)

            btn_humanization.setStyleSheet(unselected_style)



            if index == 0:

                btn_aiming.setStyleSheet(selected_style)

            elif index == 1:

                btn_advanced.setStyleSheet(selected_style)

            elif index == 2:

                btn_humanization.setStyleSheet(selected_style)



        aimbot_sub_category_layout = QHBoxLayout()

        aimbot_sub_category_layout.addWidget(btn_aiming)

        aimbot_sub_category_layout.addWidget(btn_advanced)

        aimbot_sub_category_layout.addWidget(btn_humanization)



        aimbot_horizontal_separator = QFrame()

        aimbot_horizontal_separator.setStyleSheet("background-color: #800080; height: 1px;")

        aimbot_horizontal_separator.setFrameShape(QFrame.HLine)

        aimbot_horizontal_separator.setFrameShadow(QFrame.Sunken)



        aimbot_main_layout = QVBoxLayout()



        aiming_layout = QVBoxLayout()

        aiming_line_1 = QHBoxLayout()

        aiming_line_1.addWidget(self.Aimbot_checkbox)

        aiming_layout.addLayout(aiming_line_1)

        aiming_line_2 = QHBoxLayout()

        aiming_line_2.addWidget(self.Fov_slider)

        aiming_line_2.addWidget(self.Fov_label)

        aiming_layout.addLayout(aiming_line_2)

        aiming_line_3 = QHBoxLayout()

        aiming_line_3.addWidget(self.Strength_slider)

        aiming_line_3.addWidget(self.Strength_label)

        aiming_layout.addLayout(aiming_line_3)

        aiming_line_4 = QHBoxLayout()

        aiming_line_4.addWidget(self.ADS_Strength_slider)

        aiming_line_4.addWidget(self.ADS_Strength_label)

        aiming_layout.addLayout(aiming_line_4)

        aiming_line_5 = QHBoxLayout()

        aiming_line_5.addWidget(self.aim_bone_label)

        aiming_layout.addLayout(aiming_line_5)

        aiming_layout.addSpacing(-10)

        aiming_line_6 = QHBoxLayout()

        aiming_line_6.addWidget(self.aim_bone_head)

        aiming_line_6.addWidget(self.aim_bone_neck)

        aiming_line_6.addWidget(self.aim_bone_torso)

        aiming_line_6.addWidget(self.aim_bone_nearest)

        aiming_layout.addLayout(aiming_line_6)

        aiming_line_7 = QHBoxLayout()

        aiming_line_7.addWidget(self.btn_hotkey)

        aiming_line_7.addWidget(self.hotkey_label)

        aiming_layout.addLayout(aiming_line_7)

        aiming_line_8 = QHBoxLayout()

        aiming_line_8.addWidget(self.btn_backup_hotkey)

        aiming_line_8.addWidget(self.backup_hotkey_label)

        aiming_layout.addLayout(aiming_line_8)

        aiming_layout.setSpacing(10)

        aiming_layout.addStretch(False)

        


        advanced_layout = QVBoxLayout()

        advanced_line_1 = QHBoxLayout()

        advanced_line_1.addWidget(self.mouse_movement_type_label)
        

        advanced_layout.addLayout(advanced_line_1)

        advanced_layout.addSpacing(-10)

        advanced_line_2 = QHBoxLayout()

        advanced_line_2.addWidget(self.mouse_movement_default)

        advanced_line_2.addWidget(self.mouse_movement_arduino)
        advanced_line_2.addWidget(self.mouse_movement_makcu)
        
        

        advanced_layout.addLayout(advanced_line_2)


        advanced_line_3 = QHBoxLayout()
        advanced_line_3.addWidget(self.Norecoil_checkbox)

        advanced_layout.addLayout(advanced_line_3)

        advanced_line_4 = QHBoxLayout()
        advanced_line_4.addWidget(self.Norecoil_slider)
        advanced_line_4.addWidget(self.Norecoil_label)
        advanced_layout.addLayout(advanced_line_4)

        advanced_layout.setSpacing(10)




        advanced_layout.addStretch(False)






        humanization_layout = QVBoxLayout()

        humanization_line_1 = QHBoxLayout()

        humanization_line_1.addWidget(self.humanization_type_label)

        humanization_layout.addLayout(humanization_line_1)

        humanization_layout.addSpacing(-10)

        humanization_line_2 = QHBoxLayout()

        humanization_line_2.addWidget(self.humanization_default)

        humanization_line_2.addWidget(self.humanization_bezier)

        humanization_line_2.addWidget(self.humanization_catmull_rom)

        humanization_layout.addLayout(humanization_line_2)

        humanization_layout.setSpacing(10)

        humanization_layout.addStretch(False)



        aimbot_sub_stacked_widget = QStackedWidget()

        aiming_widget = QWidget()

        aiming_widget.setLayout(aiming_layout)



        advanced_widget = QWidget()

        advanced_widget.setLayout(advanced_layout)



        humanization_widget = QWidget()

        humanization_widget.setLayout(humanization_layout)



        aimbot_sub_stacked_widget.addWidget(aiming_widget)

        aimbot_sub_stacked_widget.addWidget(advanced_widget)

        aimbot_sub_stacked_widget.addWidget(humanization_widget)



        aimbot_sub_stacked_widget.widget(0).setLayout(aiming_layout)

        aimbot_sub_stacked_widget.widget(1).setLayout(advanced_layout)

        aimbot_sub_stacked_widget.widget(2).setLayout(humanization_layout)



        btn_aiming.clicked.connect(lambda: aimbot_sub_stacked_widget.setCurrentIndex(0))

        btn_advanced.clicked.connect(lambda: aimbot_sub_stacked_widget.setCurrentIndex(1))

        btn_humanization.clicked.connect(lambda: aimbot_sub_stacked_widget.setCurrentIndex(2))



        def on_aimbot_index_changed(index):

            update_aimbot_button_style(index)



        aimbot_sub_stacked_widget.currentChanged.connect(on_aimbot_index_changed)



        update_aimbot_button_style(aimbot_sub_stacked_widget.currentIndex())



        aimbot_main_layout.addLayout(aimbot_sub_category_layout)

        aimbot_main_layout.addWidget(aimbot_horizontal_separator)

        aimbot_main_layout.addWidget(aimbot_sub_stacked_widget)



        aimbot_main_layout.setAlignment(Qt.AlignTop)



        btn_visuals = QPushButton("General")

        btn_visuals.setCursor(QCursor(Qt.PointingHandCursor))

        btn_advanced_visuals = QPushButton("Advanced")

        btn_advanced_visuals.setCursor(QCursor(Qt.PointingHandCursor))

        btn_colors = QPushButton("Colors")

        btn_colors.setCursor(QCursor(Qt.PointingHandCursor))



        def update_visuals_button_style(index):

            selected_style = "color: white; font-weight: bold;"

            unselected_style = "color: gray; font-weight: normal;"



            btn_visuals.setStyleSheet(unselected_style)

            btn_advanced_visuals.setStyleSheet(unselected_style)

            btn_colors.setStyleSheet(unselected_style)



            if index == 0:

                btn_visuals.setStyleSheet(selected_style)

            elif index == 1:

                btn_advanced_visuals.setStyleSheet(selected_style)

            elif index == 2:

                btn_colors.setStyleSheet(selected_style)



        visuals_sub_category_layout = QHBoxLayout()

        visuals_sub_category_layout.addWidget(btn_visuals)

        visuals_sub_category_layout.addWidget(btn_advanced_visuals)

        visuals_sub_category_layout.addWidget(btn_colors)



        visuals_horizontal_separator = QFrame()

        visuals_horizontal_separator.setStyleSheet("background-color: #800080; height: 1px;")

        visuals_horizontal_separator.setFrameShape(QFrame.HLine)

        visuals_horizontal_separator.setFrameShadow(QFrame.Sunken)



        visuals_main_layout = QVBoxLayout()



        visuals_layout = QVBoxLayout()

        visuals_line_1 = QHBoxLayout()

        visuals_line_1.addWidget(self.Overlay_checkbox)

        visuals_layout.addLayout(visuals_line_1)

        visuals_line_2 = QHBoxLayout()

        visuals_line_2.addWidget(self.Fov_checkbox)

        visuals_layout.addLayout(visuals_line_2)

        visuals_line_3 = QHBoxLayout()

        visuals_line_3.addWidget(self.Box_checkbox)

        visuals_layout.addLayout(visuals_line_3)

        visuals_line_4 = QHBoxLayout()

        visuals_line_4.addWidget(self.Line_checkbox)

        visuals_layout.addLayout(visuals_line_4)

        visuals_line_5 = QHBoxLayout()

        visuals_line_5.addWidget(self.Point_checkbox)

        visuals_layout.addLayout(visuals_line_5)

        visuals_layout.addSpacing(5)

        visuals_line_6 = QHBoxLayout()

        visuals_line_6.addWidget(self.box_type_label)

        visuals_layout.addLayout(visuals_line_6)

        visuals_layout.addSpacing(-10)

        visuals_line_7 = QHBoxLayout()

        visuals_line_7.addWidget(self.box_type_default)

        visuals_line_7.addWidget(self.box_type_corner)

        visuals_line_7.addWidget(self.box_type_filled)

        visuals_layout.addLayout(visuals_line_7)

        visuals_layout.setSpacing(10)

        visuals_layout.addStretch(False)



        advanced_visuals_layout = QVBoxLayout()

        advanced_visuals_line_1 = QHBoxLayout()

        advanced_visuals_line_1.addWidget(self.Fov_outline_checkbox)

        advanced_visuals_layout.addLayout(advanced_visuals_line_1)

        advanced_visuals_line_2 = QHBoxLayout()

        advanced_visuals_line_2.addWidget(self.Box_outline_checkbox)

        advanced_visuals_layout.addLayout(advanced_visuals_line_2)

        advanced_visuals_line_3 = QHBoxLayout()

        advanced_visuals_line_3.addWidget(self.Line_outline_checkbox)

        advanced_visuals_layout.addLayout(advanced_visuals_line_3)

        advanced_visuals_line_4 = QHBoxLayout()

        advanced_visuals_line_4.addWidget(self.Point_outline_checkbox)

        advanced_visuals_layout.addLayout(advanced_visuals_line_4)

        advanced_visuals_line_5 = QHBoxLayout()

        advanced_visuals_line_5.addWidget(self.Fov_Thickness_slider)

        advanced_visuals_line_5.addWidget(self.Fov_Thickness_label)

        advanced_visuals_layout.addLayout(advanced_visuals_line_5)

        advanced_visuals_line_6 = QHBoxLayout()

        advanced_visuals_line_6.addWidget(self.Box_Thickness_slider)

        advanced_visuals_line_6.addWidget(self.Box_Thickness_label)

        advanced_visuals_layout.addLayout(advanced_visuals_line_6)

        advanced_visuals_line_7 = QHBoxLayout()

        advanced_visuals_line_7.addWidget(self.Line_Thickness_slider)

        advanced_visuals_line_7.addWidget(self.Line_Thickness_label)

        advanced_visuals_layout.addLayout(advanced_visuals_line_7)

        advanced_visuals_line_8 = QHBoxLayout()

        advanced_visuals_line_8.addWidget(self.Point_Thickness_slider)

        advanced_visuals_line_8.addWidget(self.Point_Thickness_label)

        advanced_visuals_layout.addLayout(advanced_visuals_line_8)

        advanced_visuals_layout.setSpacing(10)

        advanced_visuals_layout.addStretch(False)



        colors_layout = QVBoxLayout()

        colors_layout.setContentsMargins(0, 5, 0, 0)



        colors_line_1 = QHBoxLayout()

        self.fov_color_picker = ColorPicker("FOV Color", Fov_color)

        self.fov_color_picker.color_changed.connect(self.update_fov_color)

        colors_layout.addSpacing(5)

        colors_line_1.addWidget(self.fov_color_picker)

        colors_layout.addLayout(colors_line_1)



        colors_line_2 = QHBoxLayout()

        self.box_color_picker = ColorPicker("Box Color", Box_color)

        self.box_color_picker.color_changed.connect(self.update_box_color)

        colors_line_2.addWidget(self.box_color_picker)

        colors_layout.addLayout(colors_line_2)



        colors_line_3 = QHBoxLayout()

        self.line_color_picker = ColorPicker("Line Color", Line_color)

        self.line_color_picker.color_changed.connect(self.update_line_color)

        colors_line_3.addWidget(self.line_color_picker)

        colors_layout.addLayout(colors_line_3)



        colors_line_4 = QHBoxLayout()

        self.point_color_picker = ColorPicker("Point Color", Point_color)

        self.point_color_picker.color_changed.connect(self.update_point_color)

        colors_line_4.addWidget(self.point_color_picker)

        colors_layout.addLayout(colors_line_4)



        visuals_sub_stacked_widget = QStackedWidget()

        visuals_widget = QWidget()

        visuals_widget.setLayout(visuals_layout)



        advanced_visuals_widget = QWidget()

        advanced_visuals_widget.setLayout(advanced_visuals_layout)



        colors_widget = QWidget()

        colors_widget.setLayout(colors_layout)



        visuals_sub_stacked_widget.addWidget(visuals_widget)

        visuals_sub_stacked_widget.addWidget(advanced_visuals_widget)

        visuals_sub_stacked_widget.addWidget(colors_widget)



        visuals_sub_stacked_widget.widget(0).setLayout(visuals_layout)

        visuals_sub_stacked_widget.widget(1).setLayout(advanced_visuals_layout)

        visuals_sub_stacked_widget.widget(2).setLayout(colors_layout)



        btn_visuals.clicked.connect(lambda: visuals_sub_stacked_widget.setCurrentIndex(0))

        btn_advanced_visuals.clicked.connect(lambda: visuals_sub_stacked_widget.setCurrentIndex(1))

        btn_colors.clicked.connect(lambda: visuals_sub_stacked_widget.setCurrentIndex(2))



        def on_visuals_index_changed(index):

            update_visuals_button_style(index)



        visuals_sub_stacked_widget.currentChanged.connect(on_visuals_index_changed)



        update_visuals_button_style(visuals_sub_stacked_widget.currentIndex())



        visuals_main_layout.addLayout(visuals_sub_category_layout)

        visuals_main_layout.addWidget(visuals_horizontal_separator)

        visuals_main_layout.addWidget(visuals_sub_stacked_widget)



        visuals_main_layout.setAlignment(Qt.AlignTop)



        btn_ai = QPushButton("AI")

        btn_ai.setCursor(QCursor(Qt.PointingHandCursor))

        btn_ui = QPushButton("Menu")

        btn_ui.setCursor(QCursor(Qt.PointingHandCursor))

        btn_user_info = QPushButton("User Info")

        btn_user_info.setCursor(QCursor(Qt.PointingHandCursor))



        def update_profile_button_style(index):

            selected_style = "color: white; font-weight: bold;"

            unselected_style = "color: gray; font-weight: normal;"



            btn_ai.setStyleSheet(unselected_style)

            btn_ui.setStyleSheet(unselected_style)

            btn_user_info.setStyleSheet(unselected_style)



            if index == 0:

                btn_ai.setStyleSheet(selected_style)

            elif index == 1:

                btn_ui.setStyleSheet(selected_style)

            elif index == 2:

                btn_user_info.setStyleSheet(selected_style)



        profile_sub_category_layout = QHBoxLayout()

        profile_sub_category_layout.addWidget(btn_ai)

        profile_sub_category_layout.addWidget(btn_ui)

        profile_sub_category_layout.addWidget(btn_user_info)



        profile_horizontal_separator = QFrame()

        profile_horizontal_separator.setStyleSheet("background-color: #800080; height: 1px;")

        profile_horizontal_separator.setFrameShape(QFrame.HLine)

        profile_horizontal_separator.setFrameShadow(QFrame.Sunken)



        profile_main_layout = QVBoxLayout()



        ai_layout = QVBoxLayout()

        ai_line_1 = QHBoxLayout()

        ai_line_1.addWidget(self.Confidence_slider)

        ai_line_1.addWidget(self.Confidence_label)

        ai_layout.addLayout(ai_line_1)

        ai_line_2 = QHBoxLayout()

        ai_line_2.addWidget(self.AI_Model_label)

        ai_line_2.addWidget(self.AI_Model_combobox)

        ai_layout.addLayout(ai_line_2)

        ai_layout.setSpacing(10)

        ai_layout.addStretch(False)


        
        ui_layout = QVBoxLayout()



        ui_line_1 = QHBoxLayout()

        ui_line_1.addWidget(self.menu_hotkey)

        ui_line_1.addWidget(self.menu_label)

        ui_layout.addLayout(ui_line_1)



        ui_line_2 = QHBoxLayout()

        ui_line_2.addWidget(self.Roundness_slider)

        ui_line_2.addWidget(self.Roundness_label)

        ui_layout.addLayout(ui_line_2)



        ui_line_3 = QHBoxLayout()

        ui_line_3.addWidget(self.Outline_Thickness_slider)

        ui_line_3.addWidget(self.Outline_Thickness_label)

        ui_layout.addLayout(ui_line_3)



        ui_line_4 = QHBoxLayout()

        self.gui_color_picker = ColorPicker("GUI Color", Gui_color)

        self.gui_color_picker.color_changed.connect(self.update_gui_color)

        ui_line_4.addWidget(self.gui_color_picker)

        ui_layout.addLayout(ui_line_4)



        ui_layout.setSpacing(10)

        ui_layout.addStretch(False)



        user_info_layout = QVBoxLayout()

        user_info_line_1 = QHBoxLayout()

        user_info_line_1.addWidget(self.User_Info_label)

        user_info_layout.addLayout(user_info_line_1)

        user_info_line_2 = QHBoxLayout()

        user_info_line_2.addWidget(self.User_Info_key)

        user_info_layout.addLayout(user_info_line_2)

        user_info_line_3 = QHBoxLayout()

        user_info_line_3.addWidget(self.User_Info_expiry)

        user_info_layout.addLayout(user_info_line_3)

        user_info_line_4 = QHBoxLayout()

        user_info_line_4.addWidget(self.User_Info_purchased)

        user_info_layout.addLayout(user_info_line_4)

        user_info_layout.setSpacing(0)

        user_info_layout.addStretch(False)



        profile_sub_stacked_widget = QStackedWidget()

        ai_widget = QWidget()

        ai_widget.setLayout(ai_layout)



        ui_widget = QWidget()

        ui_widget.setLayout(ui_layout)



        user_info_widget = QWidget()

        user_info_widget.setLayout(user_info_layout)



        profile_sub_stacked_widget.addWidget(ai_widget)

        profile_sub_stacked_widget.addWidget(ui_widget)

        profile_sub_stacked_widget.addWidget(user_info_widget)



        profile_sub_stacked_widget.widget(0).setLayout(ai_layout)

        profile_sub_stacked_widget.widget(1).setLayout(ui_layout)

        profile_sub_stacked_widget.widget(2).setLayout(user_info_layout)



        btn_ai.clicked.connect(lambda: profile_sub_stacked_widget.setCurrentIndex(0))

        btn_ui.clicked.connect(lambda: profile_sub_stacked_widget.setCurrentIndex(1))

        btn_user_info.clicked.connect(lambda: profile_sub_stacked_widget.setCurrentIndex(2))



        def on_profile_index_changed(index):

            update_profile_button_style(index)



        profile_sub_stacked_widget.currentChanged.connect(on_profile_index_changed)



        update_profile_button_style(profile_sub_stacked_widget.currentIndex())



        profile_main_layout.addLayout(profile_sub_category_layout)

        profile_main_layout.addWidget(profile_horizontal_separator)

        profile_main_layout.addWidget(profile_sub_stacked_widget)



        profile_main_layout.setAlignment(Qt.AlignTop)



        stacked_widget = QStackedWidget()

        stacked_widget.addWidget(QWidget())

        stacked_widget.addWidget(QWidget())

        stacked_widget.addWidget(QWidget())



        stacked_widget.widget(0).setLayout(aimbot_main_layout)

        stacked_widget.widget(1).setLayout(visuals_main_layout)

        stacked_widget.widget(2).setLayout(profile_main_layout)



        global layout, loader_layout, close_menu_layout, left_menu_layout, separator_vertical, main_content_layout



        layout = QHBoxLayout()

        btn_aimbot.setFixedWidth(45)

        btn_visual.setFixedWidth(45)

        btn_profile.setFixedWidth(45)

        left_menu_layout = QVBoxLayout()

        close_menu_layout = QVBoxLayout()
        


        separator_horizontal_top = QFrame()

        separator_horizontal_top.setStyleSheet("background-color: #000000; height: 1px;")

        separator_horizontal_top.setFrameShape(QFrame.HLine)

        separator_horizontal_top.setFrameShadow(QFrame.Sunken)



        separator_horizontal_bottom = QFrame()

        separator_horizontal_bottom.setStyleSheet("background-color: #000000; height: 1px;")

        separator_horizontal_bottom.setFrameShape(QFrame.HLine)

        separator_horizontal_bottom.setFrameShadow(QFrame.Sunken)



        gmarket_logo_label = QLabel()

        gmarket_logo_pixmap = QPixmap("C:/ProgramData/NezAI/icons/logo.png").scaled(47, 47, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        gmarket_logo_label.setPixmap(gmarket_logo_pixmap)

        gmarket_logo_label.setContentsMargins(4, 0, 0, 0)



        discord_logo_label = ClickableLabel()

        discord_logo_pixmap = QPixmap("C:/ProgramData/NezAI/icons/discord.png").scaled(47, 47, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        discord_logo_label.setPixmap(discord_logo_pixmap)

        discord_logo_label.setContentsMargins(3, 0, 0, 0)



        left_menu_layout.addWidget(gmarket_logo_label)



        left_menu_layout.addSpacing(-18)



        left_menu_layout.addWidget(separator_horizontal_top)



        left_menu_layout.addSpacing(18)



        left_menu_layout.setSpacing(25)



        button_layout = QVBoxLayout()

        button_layout.addWidget(btn_aimbot, alignment=Qt.AlignCenter)

        button_layout.addWidget(btn_visual, alignment=Qt.AlignCenter)

        button_layout.addWidget(btn_profile, alignment=Qt.AlignCenter)

        

        left_menu_layout.addLayout(button_layout)



        left_menu_layout.addStretch()

        left_menu_layout.setSpacing(25)



        left_menu_layout.addWidget(separator_horizontal_bottom)



        left_menu_layout.addSpacing(-19)



        left_menu_layout.addWidget(discord_logo_label)



        btn_close_layout = QVBoxLayout()

        btn_close = QPushButton("x")

        btn_close.setCursor(QCursor(Qt.PointingHandCursor))

        btn_close.setFixedSize(15, 15)

        btn_close.setStyleSheet("""

            QPushButton {

                color: gray;

            }

            QPushButton:hover {

                color: white;

            }

        """)



        btn_close.clicked.connect(self.close)

        btn_close_layout.addWidget(btn_close, alignment=Qt.AlignTop | Qt.AlignRight)

        close_menu_layout.addLayout(btn_close_layout)

        close_menu_layout.setContentsMargins(0, 0, 0, 0)



        separator_vertical = QFrame()

        separator_vertical.setStyleSheet("background-color: #800080; width: 1px; ")

        separator_vertical.setFrameShape(QFrame.VLine)

        separator_vertical.setFrameShadow(QFrame.Sunken)



        main_content_layout = QVBoxLayout()

        main_content_layout.addWidget(stacked_widget)



        btn_check_license = QPushButton("Check License")

        btn_check_license.setCursor(QCursor(Qt.PointingHandCursor))

        btn_check_license.setMinimumWidth(110)

        btn_check_license.setMaximumWidth(110)

        btn_check_license.setStyleSheet(f"""

            QPushButton {{

                color: white;

                border-radius: 5px;

                background-color: {self.widget_bg_color};

                border: none; 

            }}

            QPushButton:hover {{

                color: white;

            }}

        """)



        license_text = QLabel("License Key:")



        self.text_input_license = QLineEdit("")

        self.text_input_license.setCursor(QCursor(Qt.PointingHandCursor))

        self.text_input_license.setMaximumWidth(400)

        self.text_input_license.setMaxLength(49)

        self.text_input_license.setStyleSheet(f"""

            QLineEdit {{

                color: gray;

                border-radius: 5px;

                background-color: {self.widget_bg_color};

                border: none;

            }}

        """)



        loader_layout = QVBoxLayout()

        loader_layout.addSpacing(50)

        loader_layout.addWidget(license_text, alignment=Qt.AlignBottom)

        loader_layout.addWidget(self.text_input_license, alignment=Qt.AlignBottom)

        loader_layout.addWidget(btn_check_license, alignment=Qt.AlignCenter | Qt.AlignTop)

        loader_layout.setContentsMargins(60, 0, 0, 0)

        loader_layout.addStretch(False)



        layout.addLayout(loader_layout)

        layout.addLayout(close_menu_layout)



        self.setLayout(layout)

        btn_check_license.clicked.connect(lambda: self.check_license())



        self.load_gui()



        def set_button_style(selected_button):

            btn_aimbot.setStyleSheet(self.menu_tab_selected_style() if selected_button == "Aimbot" else self.menu_tab_selected_style())

            btn_aimbot.setIcon(QIcon(f"C:/ProgramData/NezAI/icons/aimbot-highlighted.png") if selected_button == "Aimbot" else QIcon("C:/ProgramData/NezAI/icons/aimbot.png"))



            btn_visual.setStyleSheet(self.menu_tab_selected_style() if selected_button == "Visual" else self.menu_tab_selected_style())

            btn_visual.setIcon(QIcon("C:/ProgramData/NezAI/icons/visuals-highlighted.png") if selected_button == "Visual" else QIcon("C:/ProgramData/NezAI/icons/visuals.png"))



            btn_profile.setStyleSheet(self.menu_tab_selected_style() if selected_button == "Profile" else self.menu_tab_selected_style())

            btn_profile.setIcon(QIcon("C:/ProgramData/NezAI/icons/profile-highlighted.png") if selected_button == "Profile" else QIcon("C:/ProgramData/NezAI/icons/profile.png"))



        set_button_style("Aimbot")

        btn_aimbot.clicked.connect(lambda: set_button_style("Aimbot"))

        btn_aimbot.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))



        btn_visual.clicked.connect(lambda: set_button_style("Visual"))

        btn_visual.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))



        btn_profile.clicked.connect(lambda: set_button_style("Profile"))

        btn_profile.clicked.connect(lambda: stacked_widget.setCurrentIndex(2))



        self.Fov_slider.valueChanged.connect(self.FOV_slider_value_change)

        self.Confidence_slider.valueChanged.connect(self.Confidence_slider_value_change)

        self.Strength_slider.valueChanged.connect(self.Strength_slider_value_change)

        self.Norecoil_slider.valueChanged.connect(self.Norecoil_slider_value_change)

        self.ADS_Strength_slider.valueChanged.connect(self.ADS_Strength_slider_value_change)

        self.Aimbot_checkbox.stateChanged.connect(self.on_checkbox_state_change)

        self.Norecoil_checkbox.stateChanged.connect(self.on_checkbox_state_change)

        self.Fov_checkbox.stateChanged.connect(self.on_checkbox_state_change)

        self.Overlay_checkbox.stateChanged.connect(self.on_checkbox_state_change)

        self.Box_checkbox.stateChanged.connect(self.on_checkbox_state_change)

        self.Point_checkbox.stateChanged.connect(self.on_checkbox_state_change)

        self.Line_checkbox.stateChanged.connect(self.on_checkbox_state_change)

        self.Fov_outline_checkbox.stateChanged.connect(self.on_checkbox_state_change)

        self.Box_outline_checkbox.stateChanged.connect(self.on_checkbox_state_change)

        self.Point_outline_checkbox.stateChanged.connect(self.on_checkbox_state_change)

        self.Line_outline_checkbox.stateChanged.connect(self.on_checkbox_state_change)

        self.Fov_Thickness_slider.valueChanged.connect(self.Fov_Thickness_slider_value_change)

        self.Box_Thickness_slider.valueChanged.connect(self.Box_Thickness_slider_value_change)

        self.Line_Thickness_slider.valueChanged.connect(self.Line_Thickness_slider_value_change)

        self.Point_Thickness_slider.valueChanged.connect(self.Point_Thickness_slider_value_change)

        self.Roundness_slider.valueChanged.connect(self.Roundness_slider_value_change)

        self.Outline_Thickness_slider.valueChanged.connect(self.Outline_Thickness_slider_value_change)

        self.AI_Model_combobox.currentIndexChanged.connect(self.AI_Model_change)



        self.setStyleSheet(f"""

            QWidget {{

                background-color: #000000;

                color: #ffffff;

                font-size: 15px;

                outline: none;

            }}

            QPushButton {{

                outline: none;

            }}

            QSlider {{

                outline: none;

            }}

            QLabel {{

                outline: none;

            }}

            QRadioButton {{

                outline: none;

            }}

        """)



        self.set_widgets_visible([self.Norecoil_label, self.Norecoil_checkbox], self.Mouse_Movement == "Default")



        self.set_widgets_visible([self.Fov_checkbox, self.Box_checkbox, self.Line_checkbox, self.Point_checkbox], Overlay)



        self.set_widgets_visible([self.box_type_label, self.box_type_default, self.box_type_corner, self.box_type_filled], Box and Overlay)



        self.set_widgets_visible([

                self.Fov_slider, self.Fov_label,

                self.Strength_slider, self.Strength_label,

                self.ADS_Strength_slider, self.ADS_Strength_label,

                self.aim_bone_label,

                self.aim_bone_head, self.aim_bone_neck, self.aim_bone_torso, self.aim_bone_nearest,

                self.btn_hotkey, self.hotkey_label,

                self.btn_backup_hotkey, self.backup_hotkey_label],

            Aimbot

        )

        self.set_widgets_visible([

              
                self.Norecoil_slider, self.Norecoil_label],

            Norecoil

        )



    def check_license(self):

        threading.Thread(target=License.check_license, daemon=True).start()







    def update_fov_color(self, color):

        global Fov_color

        Fov_color = color

        self.save_config()

        

    def update_box_color(self, color):

        global Box_color

        Box_color = color

        self.save_config()



    def update_line_color(self, color):

        global Line_color

        Line_color = color

        self.save_config()



    def update_point_color(self, color):

        global Point_color

        Point_color = color

        self.save_config()



    def update_style_sheets(self):

        self.Fov_slider.setStyleSheet(self.get_slider_style())

        self.Strength_slider.setStyleSheet(self.get_slider_style())

        self.ADS_Strength_slider.setStyleSheet(self.get_slider_style())

        self.aim_bone_head.setStyleSheet(self.get_radio_button_style())

        self.aim_bone_neck.setStyleSheet(self.get_radio_button_style())

        self.aim_bone_torso.setStyleSheet(self.get_radio_button_style())

        self.aim_bone_nearest.setStyleSheet(self.get_radio_button_style())

        self.mouse_movement_default.setStyleSheet(self.get_radio_button_style())

        self.mouse_movement_arduino.setStyleSheet(self.get_radio_button_style())

        self.humanization_default.setStyleSheet(self.get_radio_button_style())

        self.humanization_bezier.setStyleSheet(self.get_radio_button_style())

        self.humanization_catmull_rom.setStyleSheet(self.get_radio_button_style())

        self.Aimbot_checkbox.setStyleSheet(self.get_toggle_button_style())

        self.btn_hotkey.setStyleSheet(self.get_button_style())

        self.btn_backup_hotkey.setStyleSheet(self.get_button_style())

        self.Overlay_checkbox.setStyleSheet(self.get_toggle_button_style())

        self.Line_checkbox.setStyleSheet(self.get_toggle_button_style())

        self.Point_checkbox.setStyleSheet(self.get_toggle_button_style())

        self.Fov_outline_checkbox.setStyleSheet(self.get_toggle_button_style())

        self.Line_outline_checkbox.setStyleSheet(self.get_toggle_button_style())

        self.Point_outline_checkbox.setStyleSheet(self.get_toggle_button_style())

        self.Fov_Thickness_slider.setStyleSheet(self.get_slider_style())

        self.Box_Thickness_slider.setStyleSheet(self.get_slider_style())

        self.Line_Thickness_slider.setStyleSheet(self.get_slider_style())

        self.Point_Thickness_slider.setStyleSheet(self.get_slider_style())

        self.box_type_default.setStyleSheet(self.get_radio_button_style())

        self.box_type_corner.setStyleSheet(self.get_radio_button_style())

        self.box_type_filled.setStyleSheet(self.get_radio_button_style())

        self.menu_hotkey.setStyleSheet(self.get_button_style())

        self.Confidence_slider.setStyleSheet(self.get_slider_style())

        self.Roundness_slider.setStyleSheet(self.get_slider_style())

        self.Outline_Thickness_slider.setStyleSheet(self.get_slider_style())

        self.Box_checkbox.setStyleSheet(self.get_toggle_button_style())

        self.Fov_checkbox.setStyleSheet(self.get_toggle_button_style())

        self.Box_outline_checkbox.setStyleSheet(self.get_toggle_button_style())

        self.AI_Model_combobox.setStyleSheet(self.get_combo_box_style())

    def update_gui_color(self, color):

        global Gui_color

        Gui_color = color

        self.theme_hex_color = Gui_color.name()

        self.update_style_sheets()

        self.save_config()






    def update_models(self):

        models_path = 'C:\\ProgramData\\NezAI\\models'



        models = [

            file for file in os.listdir(models_path)

            if file.endswith(('.pt', '.engine', '.onnx'))

        ]


        self.AI_Model_combobox.clear()

        self.AI_Model_combobox.addItems(models)



    def set_widgets_visible(self, widgets, visible):

        for widget in widgets:

            widget.setVisible(visible)



    def toggle_box_widgets(self, state):

        self.set_widgets_visible([self.box_type_default, self.box_type_corner, self.box_type_filled], state == Qt.Checked)



    def format_time_difference(self, timestamp):

        timestamp_datetime = datetime.fromtimestamp(int(timestamp))

        now = datetime.now()

        difference = now - timestamp_datetime



        total_seconds = int(difference.total_seconds())

        if total_seconds < -10000:

            total_seconds = abs(total_seconds)



        minutes = 60

        hours = 3600

        days = 86400

        months = 2592000

        years = 31536000

        if total_seconds >= years:

            years_count = total_seconds // years

            return f"{years_count} year{'s' if years_count > 1 else ''}"

        if total_seconds >= months:

            months_count = total_seconds // months

            return f"{months_count} month{'s' if months_count > 1 else ''}"

        elif total_seconds >= days:

            days_count = total_seconds // days

            return f"{days_count} day{'s' if days_count > 1 else ''}"

        elif total_seconds >= hours:

            hours_count = total_seconds // hours

            return f"{hours_count} hour{'s' if hours_count > 1 else ''}"

        elif total_seconds >= minutes:

            minutes_count = total_seconds // minutes

            return f"{minutes_count} minute{'s' if minutes_count > 1 else ''}"

        else:

            seconds_count = total_seconds

            return f"{seconds_count} second{'s' if seconds_count > 1 else ''}"



    def update_labels(self):

        self.User_Info_key.setText(f"Your Key: " + api.user_data.username[:15] + "*******")

        self.User_Info_expiry.setText(f"Expiry: " + self.format_time_difference(api.user_data.expires))

        self.User_Info_purchased.setText(f"Purchased: " + self.format_time_difference(api.user_data.createdate) + " ago")



    def get_slider_style(self):

        return f"""

            QLineEdit {{

                border: 1px solid {self.theme_hex_color};

                color: #800080;

                border-radius: 4px;

                font-weight: bold;

            }}

            QSlider::groove:horizontal {{

                height: 9px;

                background: {self.widget_bg_color};

                border-radius: 4px;

            }}

            QSlider::handle:horizontal {{

                background: white;

                border: 2px solid white;

                width: 8px;

                height: 9px;

                margin: -1px 0;

                border-radius: 5px;

            }}

            QSlider::sub-page:horizontal {{

                background: {self.theme_hex_color};

                border-radius: 4px;

            }}

        """

    

    def get_radio_button_style(self):

        return f"""

            QRadioButton {{

                padding-top: -2px;

            }}

            QRadioButton::indicator {{

                width: 16px;

                height: 16px;

                border-radius: 8px;

                background-color: {self.widget_bg_color};

                border: none;

            }}

            QRadioButton::indicator:checked {{

                background-color: {self.theme_hex_color};

            }}

        """



    def menu_tab_selected_style(self):

        return f"""

            QPushButton {{

                border: none;

                padding-bottom: 6px;

                margin-left: 60%;

                margin-right: 60%;

            }}

        """

    

    def get_toggle_button_style(self):

        return f"""

            QCheckBox {{

                spacing: 10px;

            }}

            QCheckBox::indicator {{

                width: 40px;

                height: 20px;

                border-radius: 10px;

                background-color: white;

                border: none;

                position: absolute;

            }}

            QCheckBox::indicator:checked {{

                background: {self.theme_hex_color};

                image: url(C:/ProgramData/NezAI/icons/o-right.png);

                border: none;

            }}

            QCheckBox::indicator:unchecked {{

                background: {self.widget_bg_color};

                image: url(C:/ProgramData/NezAI/icons/o-left.png);

                border: none;

            }}

        """

    

    def load_gui(self):

        global Loaded



        if Loaded:

            layout.removeItem(loader_layout)

            layout.removeItem(close_menu_layout)

            for i in range(loader_layout.count()):

                item = loader_layout.itemAt(i)

                widget = item.widget()

                if widget is not None:

                    widget.setVisible(False)

            loader_layout.deleteLater()



            layout.addLayout(left_menu_layout)

            layout.addWidget(separator_vertical)

            layout.addLayout(main_content_layout)

            os.system("cls")

            layout.addLayout(close_menu_layout)

            self.update_labels()



    def get_combo_box_style(self):

        return f"""

            QComboBox {{

                background-color: {self.widget_bg_color};

                color: #ffffff;

                font-size: 14px;

                border-radius: 3px;

                border: 1px #800080;

                padding: 3px 20px 3px 5px;

            }}

            QComboBox::drop-down {{

                subcontrol-origin: padding;

                subcontrol-position: top right;

                width: 15px;

                border-left-width: 1px;

                border-left-color: #800080;

                border-left-style: solid;

                border-top-right-radius: 3px;

                border-bottom-right-radius: 3px;

                background-color: {self.theme_hex_color};

            }}

            QComboBox::down-arrow {{

                width: 8px;

                height: 8px;

                image: url(C:/ProgramData/NezAI/icons/d.png);

            }}

            QComboBox QAbstractItemView {{

                background-color: {self.widget_bg_color};

                color: #ffffff;

                selection-background-color: {self.theme_hex_color};

                selection-color: #ffffff;

                border: 1px solid #800080;

                border-radius: 3px;

                padding: 5px;

                font-size: 14px;

            }}

        """



    def get_button_style(self):

        return f"""

            QPushButton {{

                background-color: {self.theme_hex_color};

                color: white; border-radius:

                6px; border:

                2px solid {self.theme_hex_color};

                height: 20px;

            }} 

            QPushButton:hover {{

                background-color: {self.theme_hex_color};

            }}

            QPushButton:pressed {{ 

                background-color: {self.theme_hex_color}; 

            }}

        """



    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setBrush(self.palette().window())

        if Outline_Thickness != 0:

            painter.setPen(QPen(QColor(self.theme_hex_color), Outline_Thickness))

        else:

            painter.setPen(Qt.NoPen)

        painter.setRenderHint(QPainter.Antialiasing, True)

        painter.drawRoundedRect(self.rect(), Roundness, Roundness)

        super().paintEvent(event)



    def save_config(self):

        config_settings = {

            "Fov_Size": Fov_Size,

            "Confidence": Confidence,

            "Strength": Strength,

            "ADS_Strength": ADS_Strength,

            "Aim_Bone": self.Aim_Bone,

            "Mouse_Movement": self.Mouse_Movement,

            "Humanization": self.Humanization,

            "Aimbot": bool(Aimbot),           
            
          
            "Norecoil_senstivity" : ('Norecoil', True),

            "Norecoil_senstivity" : config.get('Norecoil_senstivity',1),

            "Keybind": Keybind,

            "Backup_Keybind": Backup_Keybind,

            "Overlay": bool(Overlay),

            "Fov": bool(Fov),

            "Box": bool(Box),

            "Box_Type": Box_Type,

            "Point": bool(Point),

            "Line": bool(Line),

            "Menu_Keybind": Menu_Keybind,

            "Roundness": Roundness,

            "Outline_Thickness": Outline_Thickness,

            "Fov_Thickness": Fov_Thickness,

            "Box_Thickness": Box_Thickness,

            "Line_Thickness": Line_Thickness,

            "Point_Thickness": Point_Thickness,

            "Fov_Outline": Fov_Outline,

            "Box_Outline": Box_Outline,

            "Line_Outline": Line_Outline,

            "Point_Outline": Point_Outline,

            "Fov_color": Fov_color.getRgb(),

            "Box_color": Box_color.getRgb(),

            "Line_color": Line_color.getRgb(),

            "Point_color": Point_color.getRgb(),

            "Gui_color": (250, 0, 250, 255),

            "AI_Model": "model.pt",

        }



        with open('./config.json', 'w') as outfile:

            jsond.dump(config_settings, outfile, indent=4)



        self.update_labels()



    def closeEvent(self, event):

        self.save_config()

        try:

            console_window = ctypes.windll.kernel32.GetConsoleWindow()

            ctypes.windll.user32.PostMessageW(console_window, 0x10, 0, 0)

        except:

            try:

                sys.exit()

            except:

                os.system('taskkill /f /fi "imagename eq cmd.exe" 1>NUL 2>NUL')



    def start_select_hotkey(self):

        global Keybind



        self.is_selecting_hotkey = True

        Keybind = None

        self.btn_hotkey.setText("...")

        threading.Thread(target=self.Keybind_listen_for_hotkey).start()



    def Keybind_listen_for_hotkey(self):

        global Keybind



        while self.is_selecting_hotkey:

            for vk in range(256):

                if win32api.GetKeyState(vk) in (-127, -128):

                    Keybind = vk

                    self.is_selecting_hotkey = False

                    key_name_converted = "None" if Keybind is None else KEY_NAMES.get(Keybind, f"0x{Keybind:02X}")

                    self.btn_hotkey.setText(f"{key_name_converted}")

                    self.save_config()

                    break



    def start_select_backup_hotkey(self):

        global Backup_Keybind



        self.is_selecting_backup_hotkey = True

        Backup_Keybind = None

        self.btn_backup_hotkey.setText("...")

        threading.Thread(target=self.listen_for_backup_hotkey).start()



    def listen_for_backup_hotkey(self):

        global Backup_Keybind



        while self.is_selecting_backup_hotkey:

            for vk in range(256):

                if win32api.GetKeyState(vk) in (-127, -128):

                    Backup_Keybind = vk

                    self.is_selecting_backup_hotkey = False

                    key_name_converted = "None" if Backup_Keybind is None else KEY_NAMES.get(Backup_Keybind, f"0x{Backup_Keybind:02X}")

                    self.btn_backup_hotkey.setText(f"{key_name_converted}")

                    self.save_config()

                    break



    def start_select_menu_hotkey(self):

        global Menu_Keybind



        self.is_selecting_menu_hotkey = True

        Menu_Keybind = None

        self.menu_hotkey.setText("...")

        threading.Thread(target=self.Menu_Keybind_listen_for_hotkey).start()



    def Menu_Keybind_listen_for_hotkey(self):

        global Menu_Keybind



        while self.is_selecting_menu_hotkey:

            for vk in range(256):

                if win32api.GetKeyState(vk) in (-127, -128):

                    Menu_Keybind = vk

                    self.is_selecting_menu_hotkey = False

                    key_name_converted = "None" if Menu_Keybind is None else KEY_NAMES.get(Menu_Keybind, f"0x{Menu_Keybind:02X}")

                    self.menu_hotkey.setText(f"{key_name_converted}")

                    self.save_config()

                    break



    def toggle_menu_visibility(self):

        if self.isVisible():

            self.hide()

        else:

            self.show()

            self.raise_()

            self.activateWindow()



    def FOV_slider_value_change(self, value):

        val = round(value / 10) * 10

        self.Fov_slider.setValue(val)



        global Fov_Size

        Fov_Size = val

        self.Fov_label.setText(f'FOV: {str(Fov_Size)} px')

        overlay = Visuals_Overlay()

        overlay.update_fov_size()

        self.save_config()



    def Confidence_slider_value_change(self, value):

        val = round(value / 1) * 1

        self.Confidence_slider.setValue(val)



        global Confidence

        Confidence = val

        self.Confidence_label.setText(f'Confidence: {str(Confidence)}%')

        self.save_config()



    def Strength_slider_value_change(self, value):

        val = round(value / 5) * 5

        self.Strength_slider.setValue(val)



        global Strength

        Strength = val

        self.Strength_label.setText(f'Strength: {str(Strength)}%')

        self.save_config()
    
    def Norecoil_slider_value_change(self, value):
        global Norecoil_senstivity
        Norecoil_senstivity = value  
        self.Norecoil_label.setText(f'Sensitivity: {str(Norecoil_senstivity)}')
        self.save_config()

    def ADS_Strength_slider_value_change(self, value):

        val = round(value / 5) * 5

        self.ADS_Strength_slider.setValue(val)



        global ADS_Strength

        ADS_Strength = val

        self.ADS_Strength_label.setText(f'ADS Strength: {str(ADS_Strength)}%')

        self.save_config()



    def Fov_Thickness_slider_value_change(self, value):

        val = round(value)

        self.Fov_Thickness_slider.setValue(val)



        global Fov_Thickness

        Fov_Thickness = val

        self.Fov_Thickness_label.setText(f'FOV Thickness: {str(Fov_Thickness)} px')

        self.save_config()



    def Box_Thickness_slider_value_change(self, value):

        val = round(value)

        self.Box_Thickness_slider.setValue(val)



        global Box_Thickness

        Box_Thickness = val

        self.Box_Thickness_label.setText(f'Box Thickness: {str(Box_Thickness)} px')

        self.save_config()



    def Roundness_slider_value_change(self, value):

        val = round(value)

        self.Roundness_slider.setValue(val)



        global Roundness

        Roundness = val

        self.Roundness_label.setText(f'GUI Roundness: {str(Roundness)}')

        self.save_config()



    def Outline_Thickness_slider_value_change(self, value):

        val = round(value)

        self.Outline_Thickness_slider.setValue(val)



        global Outline_Thickness

        Outline_Thickness = val

        self.Outline_Thickness_label.setText(f'GUI Outline Thickness: {str(Outline_Thickness)}')

        self.save_config()



    def Line_Thickness_slider_value_change(self, value):

        val = round(value)

        self.Line_Thickness_slider.setValue(val)



        global Line_Thickness

        Line_Thickness = val

        self.Line_Thickness_label.setText(f'Line Thickness: {str(Line_Thickness)} px')

        self.save_config()



    def Point_Thickness_slider_value_change(self, value):

        val = round(value)

        self.Point_Thickness_slider.setValue(val)



        global Point_Thickness

        Point_Thickness = val

        self.Point_Thickness_label.setText(f'Point Thickness: {str(Point_Thickness)} px')

        self.save_config()






    def AI_Model_change(self):

        self.AI_Model = self.AI_Model_combobox.currentText()

        global AI_Model

        AI_Model = self.AI_Model



        os.system("cls")




        import multiprocessing as mp

        import torch



        def detect(frame, confi, result_queue):
            frame = torch.tensor(frame, device="cuda", dtype=torch.float16, pin_memory=True, non_blocking=True)

            

            with torch.no_grad():
                    batch_frames = torch.stack([frame] * 4)  
                    results = model(frame.to("cuda"), conf=confi, iou=0.45, imgsz=640, max_det=10, retina_masks=False, verbose=False, classes=0)

            return results 

           
            results = process_frame(frame)
            if results is not None:               
                tracked_objects = track_objects(results)



                result_queue.put(results)


        def start_detection(frame, confi):
            result_queue = mp.Queue()
            process = mp.Process(target=detect, args=(frame, confi, result_queue))
            process.start()
            process.join()
            return result_queue.get()





        self.save_config()



    def on_checkbox_state_change(self, state):
        

        self.save_config()

        if self.sender() == self.Aimbot_checkbox:

            global Aimbot

            Aimbot = (state == Qt.Checked)

            self.set_widgets_visible([

                    self.Fov_slider, self.Fov_label,

                    self.Strength_slider, self.Strength_label,

                    self.ADS_Strength_slider, self.ADS_Strength_label,

                    self.aim_bone_label,

                    self.aim_bone_head, self.aim_bone_neck, self.aim_bone_neck, self.aim_bone_torso, self.aim_bone_nearest,

                    self.btn_hotkey, self.hotkey_label,

                    self.btn_backup_hotkey, self.backup_hotkey_label],

                Aimbot

            )
        
        if self.sender() == self.Norecoil_checkbox:

            global Norecoil

            Norecoil = (state == Qt.Checked)

            self.set_widgets_visible([


                    self.Norecoil_slider, self.Norecoil_label,

                    ],

                Norecoil

            )
        



        global Box

        if self.sender() == self.Overlay_checkbox:

            global Overlay

            Overlay = (state == Qt.Checked)

            self.set_widgets_visible([self.Fov_checkbox, self.Box_checkbox, self.Line_checkbox, self.Point_checkbox], Overlay)

            self.set_widgets_visible([self.box_type_label, self.box_type_default, self.box_type_corner, self.box_type_filled], Box and Overlay)



        if self.sender() == self.Fov_checkbox:

            global Fov

            Fov = (state == Qt.Checked)



        if self.sender() == self.Box_checkbox:

            Box = (state == Qt.Checked)

            self.set_widgets_visible([self.box_type_label, self.box_type_default, self.box_type_corner, self.box_type_filled], Box)



        if self.sender() == self.Line_checkbox:

            global Line

            Line = (state == Qt.Checked)



        if self.sender() == self.Point_checkbox:

            global Point

            Point = (state == Qt.Checked)



        if self.sender() == self.Fov_outline_checkbox:

            global Fov_Outline

            Fov_Outline = (state == Qt.Checked)



        if self.sender() == self.Box_outline_checkbox:

            global Box_Outline

            Box_Outline = (state == Qt.Checked)



        if self.sender() == self.Line_outline_checkbox:

            global Line_Outline

            Line_Outline = (state == Qt.Checked)



        if self.sender() == self.Point_outline_checkbox:

            global Point_Outline

            Point_Outline = (state == Qt.Checked)



        self.sender().setStyleSheet(self.get_toggle_button_style())

        self.save_config()






POINTER = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):

    _fields_ = [("wVk", ctypes.c_ushort),

                ("wScan", ctypes.c_ushort),

                ("dwFlags", ctypes.c_ulong),

                ("time", ctypes.c_ulong),

                ("dwExtraInfo", POINTER)]



class HardwareInput(ctypes.Structure):

    _fields_ = [("uMsg", ctypes.c_ulong),

                ("wParamL", ctypes.c_short),

                ("wParamH", ctypes.c_ushort)]



class MouseInput(ctypes.Structure):

    _fields_ = [("dx", ctypes.c_long),

                ("dy", ctypes.c_long),

                ("mouseData", ctypes.c_ulong),

                ("dwFlags", ctypes.c_ulong),

                ("time", ctypes.c_ulong),

                ("dwExtraInfo", POINTER)]



class Input_I(ctypes.Union):

    _fields_ = [("ki", KeyBdInput),

                ("mi", MouseInput),

                ("hi", HardwareInput)]



class Input(ctypes.Structure):

    _fields_ = [("type", ctypes.c_ulong),

                ("ii", Input_I)]



class POINT(ctypes.Structure):

    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]



class Visuals_Overlay(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput | Qt.WindowDoesNotAcceptFocus)

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.setAttribute(Qt.WA_ShowWithoutActivating)



        user32.SetWindowDisplayAffinity(int(self.winId()), 0x00000000)

        self.detected_players = []



        self.update_fov_size()



        self.timer = QTimer(self)

        self.timer.timeout.connect(self.update)

        self.timer.start(100)



    def update_detected_players(self, detected_players):

        self.detected_players = detected_players

        self.update()



    def update_fov_size(self):

        self.setGeometry(0, 0, screen_res_X, screen_res_Y)

        self.update()



    def paintEvent(self, event):

        if not Overlay or not Loaded:

            return



        global Fov_color, Box_color, Line_color, Point_color



        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)



        font = QFont("Verdana")

        font.setPixelSize(15)

        painter.setFont(font)



        painter.setPen(QPen(Qt.white, 5))

        font.setBold(True)

        painter.drawText(3, 15, f"Digtal Ai Aimbot")



        center_x = screen_res_X // 2

        center_y = screen_res_Y // 2



        box_size = int(Fov_Size * 2)

        box_width = int(box_size // 2)

        box_height = int(box_size // 2)



        fix_x = int((screen_res_X / 2) - box_width)

        fix_y = int((screen_res_Y / 2) - box_height)



        if Fov:

            fov_radius = Fov_Size // 2 - Fov_Thickness // 2

            fov_rect = QRectF(center_x - fov_radius, center_y - fov_radius, 2 * fov_radius, 2 * fov_radius)

            if Fov_Outline:

                painter.setPen(QPen(Qt.black, Fov_Thickness * 2, Qt.SolidLine))

                painter.drawEllipse(fov_rect)

                painter.setPen(QPen(Fov_color, Fov_Thickness, Qt.SolidLine))

                painter.drawEllipse(fov_rect)

            else:

                painter.setPen(QPen(Fov_color, Fov_Thickness, Qt.SolidLine))

                painter.drawEllipse(fov_rect)



        for player in self.detected_players:

            x1, y1, x2, y2 = player['x1'], player['y1'], player['x2'], player['y2']

            head1, head2 = player['head1'], player['head2']



            width = x2 - x1

            height = y2 - y1



            margin_factor = 0.03

            margin_x = width * margin_factor

            margin_y = height * margin_factor



            x1 -= margin_x

            y1 -= margin_y

            x2 += margin_x

            y2 += margin_y



            x1, y1, x2, y2 = int(x1) + fix_x, int(y1) + fix_y, int(x2) + fix_x, int(y2) + fix_y

            head1, head2 = int(head1) + fix_x, int(head2) + fix_y



            if Line:

                painter.setRenderHint(QPainter.Antialiasing)

                painter.setPen(QPen(Line_color, Line_Thickness))

                painter.drawLine(head1, y2, center_x, screen_res_Y)



                if Line_Outline:

                    painter.setPen(QPen(Qt.black, Line_Thickness * 2))

                    painter.drawLine(head1, y2, center_x, screen_res_Y)

                    painter.setPen(QPen(Line_color, Line_Thickness))

                    painter.drawLine(head1, y2, center_x, screen_res_Y)



            if Point:

                painter.setRenderHint(QPainter.Antialiasing, False)

                painter.setPen(QPen(Qt.black if Point_Outline else Point_color, 1))



                painter.setBrush(QBrush(Point_color))



                target_size = Point_Thickness + Point_Thickness * 2 if Point_Outline else Point_Thickness + Point_Thickness

                painter.drawRect(head1 - target_size // 2, head2 - target_size // 2, target_size, target_size)



            if Box:

                if Box_Type == "Corner":

                    corner_length = int(min(width, height) * 0.25)



                    if Box_Outline:

                        painter.setPen(QPen(Qt.black, Box_Thickness * 2))

                        painter.setRenderHint(QPainter.Antialiasing, False)



                        painter.drawLine(x1, y1, x1 + corner_length, y1)

                        painter.drawLine(x1, y1, x1, y1 + corner_length)

                        painter.drawLine(x2, y1, x2 - corner_length, y1)

                        painter.drawLine(x2, y1, x2, y1 + corner_length)

                        painter.drawLine(x1, y2, x1 + corner_length, y2)

                        painter.drawLine(x1, y2, x1, y2 - corner_length)

                        painter.drawLine(x2, y2, x2 - corner_length, y2)

                        painter.drawLine(x2, y2, x2, y2 - corner_length)



                    painter.setPen(QPen(Box_color, Box_Thickness))



                    painter.drawLine(x1, y1, x1 + corner_length, y1)

                    painter.drawLine(x1, y1, x1, y1 + corner_length)

                    painter.drawLine(x2, y1, x2 - corner_length, y1)

                    painter.drawLine(x2, y1, x2, y1 + corner_length)

                    painter.drawLine(x1, y2, x1 + corner_length, y2)

                    painter.drawLine(x1, y2, x1, y2 - corner_length)

                    painter.drawLine(x2, y2, x2 - corner_length, y2)

                    painter.drawLine(x2, y2, x2, y2 - corner_length)



                elif Box_Type == "Default":

                    if Box_Outline:

                        painter.setPen(QPen(Qt.black, Box_Thickness * 2))

                        painter.setRenderHint(QPainter.Antialiasing, False)

                        painter.drawLine(x1, y1, x2, y1)

                        painter.drawLine(x2, y1, x2, y2)

                        painter.drawLine(x2, y2, x1, y2) 

                        painter.drawLine(x1, y2, x1, y1)



                    painter.setPen(QPen(Box_color, Box_Thickness))



                    painter.drawLine(x1, y1, x2, y1)

                    painter.drawLine(x2, y1, x2, y2)

                    painter.drawLine(x2, y2, x1, y2)

                    painter.drawLine(x1, y2, x1, y1)



                else:

                    painter.setPen(Qt.NoPen)

                    fill_color = QColor(0, 0, 0, 100)

                    painter.setBrush(QBrush(fill_color, Qt.SolidPattern))



                    points = [QPoint(x1, y1), QPoint(x2, y1), QPoint(x2, y2), QPoint(x1, y2)]



                    painter.drawPolygon(QPolygon(points))



    def focusInEvent(self, event):

        ctypes.windll.user32.SetFocus(None)


        from hid_mouse import MouseInstruct, DeviceNotFoundError


class MakcuController:
    def __init__(self):
        self.serial = None
        self.connected = False
        self.baud_rate = 115200  # Default baud rate
        
    def connect(self):
        try:
            for port in list_ports.comports():
                if "VID:PID=1A86:55D3" in port.hwid:
                    self.serial = serial.Serial("COM3", self.baud_rate, timeout=1)
                    self.serial.write(b"km.version()\r")
                    response = self.serial.readline().decode().strip()
                    if "km.MAKCU" in response:
                        self.connected = True
                        # Set 4Mbps baud rate
                        self.serial.write(bytes.fromhex("DE AD 05 00 A5 00 09 3D 00"))
                        self.serial.baudrate = 4000000
                        return True
            return False
        except Exception as e:
            print(f"MAKCU connection error: {e}")
            return False

    def move(self, x, y):
        if self.connected and self.serial:
            try:
                cmd = f"km.move({int(x)},{int(y)})\r".encode()
                self.serial.write(cmd)
            except Exception as e:
                print(f"MAKCU move error: {e}")
                self.connected = False

    def click(self, button="left", press=True):
        if self.connected and self.serial:
            try:
                state = 1 if press else 0
                cmd = f"km.{button}({state})\r".encode()
                self.serial.write(cmd)
                time.sleep(0.01)  # Delay between commands
            except Exception as e:
                print(f"MAKCU click error: {e}")
                self.connected = False

    def close(self):
        if self.serial and self.connected:
            self.serial.close()
            self.connected = False

class AI:

    extra = ctypes.c_ulong(0)

    ii_ = Input_I()

    lock = threading.Lock()



    app = QApplication(sys.argv)



    gui = GUI()



    prev_state = 0

    last_time_selecting_menu_hotkey = 0

    def __init__(self, gui):
        self.gui = gui
        self.hid_mouse = None
        self.makcu = None

    def key_down(self):

        return False if Keybind is None else win32api.GetAsyncKeyState(Keybind) < 0



    def backup_key_down(self):

        return False if Backup_Keybind is None else win32api.GetAsyncKeyState(Backup_Keybind) < 0

    

    def bezier_interpolation(self, start, end, t):

        return (1 - t) * start + t * end



    def catmull_rom_interpolation(self, p0, p1, p2, p3, t):

        return 0.5 * ((2 * p1) +

                    (-p0 + p2) * t +

                    (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +

                    (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t)



    def move_mouse(self, x, y, humanization=None):
        if not self.key_down() and not self.backup_key_down():
            return

        delta_x = (x - screen_x) * 1.0
        delta_y = (y - screen_y) * 1.0
        distance = np.linalg.norm((delta_x, delta_y))

        if distance == 0:
            return
    
        smooth = ADS_Strength if win32api.GetKeyState(0x02) < 0 else Strength
        smoothing = round(0.5 + (smooth - 10) / 10.0, 1)
        move_x = (delta_x / distance) * 1000 * smoothing
        move_y = (delta_y / distance) * 1000 * smoothing
        move_x *= 0.005
        move_y *= 0.005
        distance_clamped = min(1, (distance / 100))
        move_x *= distance_clamped
        move_y *= distance_clamped
        if humanization == "Bezier":
            t = distance / 100
            move_x = self.bezier_interpolation(0, move_x, t)
            move_y = self.bezier_interpolation(0, move_y, t)
        elif humanization == "Default":
            smooth_move_x = smoothing * move_x + (1 - smoothing) * move_x
            smooth_move_y = smoothing * move_y + (1 - smoothing) * move_y
            smooth_move_x = 0.005 * smooth_move_x + (1 - 0.005) * move_x
            smooth_move_y = 0.005 * smooth_move_y + (1 - 0.005) * move_y
            move_x = smooth_move_x
            move_y = smooth_move_y

        with self.lock:
            if self.gui.Mouse_Movement == "Arduino":
                if self.hid_mouse is None:
                    try:
                        self.hid_mouse = MouseInstruct.getMouse()
                        print(f"Using HID mouse with protocol: {self.hid_mouse._protocol.value}")
                    except DeviceNotFoundError:
                        print("HID mouse device not found! Aiming disabled without hardware.")
                        return  # Stop here if no hardware
                try:
                    self.hid_mouse.move(int(move_x), int(move_y))
                except Exception as e:
                    print(f"Error moving HID mouse: {e}")
                    self.hid_mouse = None
            elif self.gui.Mouse_Movement == "Makcu":
                if self.makcu is None:
                    self.makcu = MakcuController()
                    if not self.makcu.connect():
                        print("Makcu device not found! Aiming disabled without hardware.")
                        self.makcu = None
                        return
                try:
                    self.makcu.move(int(move_x), int(move_y))
                except Exception as e:
                    print(f"Error moving MAKCU: {e}")
                    self.makcu.close()
                    self.makcu = None
            else:
                rounded_x = round(move_x)
                rounded_y = round(move_y)
                self.ii_.mi = MouseInput(rounded_x, rounded_y, 0, 0x0001, 0, ctypes.pointer(self.extra))
                input_struct = Input(ctypes.c_ulong(0), self.ii_)
                ctypes.windll.user32.SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(input_struct))



    def start(self):

        detected_players = []



        AI.gui.show()



        prev_state = 0

        last_time_selecting_menu_hotkey = 0



        camera = bettercam.create(output_idx=0, output_color="BGR", max_buffer_len=1)



        os.system("cls")



        overlay = Visuals_Overlay()

        overlay.show()



        show_console(False)



        results = None



        closest_detection = None



        while True:

            self.Fov_Size = Fov_Size



            box_size = int(self.Fov_Size * 2)

            box_width = int(box_size // 2)

            box_height = int(box_size // 2)

            left, top = int(screen_res_X / 2 - box_width), int(screen_res_Y / 2 - box_height)

            right, bottom = int(screen_res_X / 2 - box_width) + int(box_size), int(screen_res_Y / 2 - box_height) + int(box_size)

            frame = camera.grab(region=(left, top, right, bottom))

            if frame is None:

                continue

            frame = np.asarray(frame)[..., :3]

            frame = np.ascontiguousarray(frame)

            confi = Confidence / 100

            if (Overlay and (Box or Line or Point)) or (Aimbot and (self.key_down() or self.backup_key_down())) or results is None:

                results = model(frame, conf=confi, iou=0.45, imgsz=640, max_det=10, retina_masks=False, verbose=False, classes=0)

                if len(results[0].boxes.xyxy) != 0:

                    least_crosshair_dist = False

                    confi = Confidence / 100

                    for detection, conf in zip(results[0].boxes.xyxy.tolist(), results[0].boxes.conf.tolist()):

                        x1, y1, x2, y2 = detection

                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                        height = y2 - y1

                        if AI.gui.Aim_Bone == "Head":

                            relative_head_X, relative_head_Y = int((x1 + x2) / 2), int((y1 + y2) / 2 - height / 2.5)

                        elif AI.gui.Aim_Bone == "Neck":

                            relative_head_X, relative_head_Y = int((x1 + x2) / 2), int((y1 + y2) / 2 - height / 3)

                        elif AI.gui.Aim_Bone == "Torso":

                            relative_head_X, relative_head_Y = int((x1 + x2) / 2), int((y1 + y2) / 2 - height / 6.5)

                        else:

                            center_x, center_y = self.Fov_Size, self.Fov_Size

                            

                            bones = {

                                "Head": (int((x1 + x2) / 2), int((y1 + y2) / 2 - height / 2.5)),

                                "Neck": (int((x1 + x2) / 2), int((y1 + y2) / 2 - height / 3)),

                                "Torso": (int((x1 + x2) / 2), int((y1 + y2) / 2 - height / 6.5)),

                            }

                            distances = {}

                            for bone, (bone_x, bone_y) in bones.items():

                                distance = ((bone_x - center_x) ** 2 + (bone_y - center_y) ** 2) ** 0.5

                                distances[bone] = distance

                            

                            nearest_bone = min(distances, key=distances.get)

                            relative_head_X, relative_head_Y = bones[nearest_bone]

                        

                        crosshair_dist = math.dist((relative_head_X, relative_head_Y), (self.Fov_Size, self.Fov_Size))

                        if crosshair_dist < self.Fov_Size // 2:

                            if not least_crosshair_dist or crosshair_dist < least_crosshair_dist:

                                least_crosshair_dist = crosshair_dist

                                closest_detection = {"relative_head_X": relative_head_X, "relative_head_Y": relative_head_Y, "conf": conf}

                            if Overlay and Box or Line or Point:

                                detected_players.append({

                                    'x1': x1, 

                                    'y1': y1, 

                                    'x2': x2, 

                                    'y2': y2, 

                                    'head1': closest_detection["relative_head_X"] if closest_detection else 0, 

                                    'head2': closest_detection["relative_head_Y"] if closest_detection else 0, 

                                    'conf': closest_detection["conf"] if closest_detection else 0

                                })

                        else:

                            closest_detection = None

                    if closest_detection:

                        absolute_head_X = closest_detection["relative_head_X"] + left

                        absolute_head_Y = closest_detection["relative_head_Y"] + top

                        if Aimbot:

                            if Loaded:

                                threading.Thread(target=self.move_mouse, args=(absolute_head_X, absolute_head_Y, AI.gui.Humanization)).start()

                if Overlay and Box or Line or Point:

                    overlay.update_detected_players(detected_players)

                    detected_players = []



            curr_state = 0 if Menu_Keybind is None else win32api.GetKeyState(Menu_Keybind)

            if AI.gui.is_selecting_menu_hotkey:

                last_time_selecting_menu_hotkey = time.time()



            if curr_state < 0 and prev_state >= 0 and time.time() - last_time_selecting_menu_hotkey > 0.01:

                AI.gui.toggle_menu_visibility()



            prev_state = curr_state



            AI.app.processEvents()

            if not ((Overlay and (Box or Line or Point)) or (AI.gui.isVisible() and AI.gui.is_dragging) or (Aimbot and (self.key_down() or self.backup_key_down()))):

                time.sleep(0.001)

        try:
            AI(self.gui).start()
        finally:
            if self.makcu:
                self.makcu.close()

if __name__ == "__main__":

    print("[Digital] -> launching...")



    threading.Thread(target=License.auto_login, daemon=True).start()

    AI(AI.gui).start()