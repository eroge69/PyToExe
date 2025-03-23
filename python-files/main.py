# =======================================
# DesyncLoader by Ksynax
# https://t.me/ksynax
# =======================================
from datetime import datetime, date
import time
from time import sleep
import subprocess
import os
import os.path
import sys
import ctypes
import functools
import inspect
import zipfile
import requests
import discord
from discord import Webhook, SyncWebhook
from tqdm import tqdm
import hashlib
from keyauth import api

webhook_url = "https://discord.com/api/webhooks/1277371410125426845/tkI3VFXdZlX1Q5_k_qzLw8Qti70BM36QQof92Z6hcfhmQk9OqmWWH7urDSHsL9HF0xeh"

def getchecksum():
    md5_hash = hashlib.md5()
    file = open(''.join(sys.argv), "rb")
    md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest

keyauthapp = api(
    name = "Loader", # Application Name
    ownerid = "0H9ssQrcWg", # Owner ID
    secret = "96d57d25c7759c6ef8ae063bf992fb77093e7b6ee4df625e4fc0edebd8596dfe", # Application Secret
    version = "1.0", # Application Version
    hash_to_check = getchecksum()
)



IGNORED_MODULES = []

username = "Ksynax"
build = "Alpha 1.16.5"

class MODULEENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.c_ulong),
        ("th32ModuleID", ctypes.c_ulong),
        ("th32ProcessID", ctypes.c_ulong),
        ("GlblcntUsage", ctypes.c_ulong),
        ("ProccntUsage", ctypes.c_ulong),
        ("modBaseAddr", ctypes.POINTER(ctypes.c_byte)),
        ("modBaseSize", ctypes.c_ulong),
        ("hModule", ctypes.c_void_p),
        ("szModule", ctypes.c_char * 256),
        ("szExePath", ctypes.c_char * 260)
    ]

def check_for_injection():
    previous_modules = get_loaded_modules()

    while True:
        current_modules = get_loaded_modules()
        new_modules = [module for module in current_modules if
                       module not in previous_modules and module not in IGNORED_MODULES]
        if new_modules:
            print("[!] Обнаружена попытка инжекта кода")
            os.kill(os.getpid(), 9)
        previous_modules = current_modules
        time.sleep(0.001)

def get_loaded_modules():
    module_list = []
    snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(0x00000008, 0)  # TH32CS_SNAPMODULE
    if snapshot == -1:
        return []

    me32 = MODULEENTRY32()
    me32.dwSize = ctypes.sizeof(MODULEENTRY32)

    ret = ctypes.windll.kernel32.Module32First(snapshot, ctypes.byref(me32))
    while ret != 0:
        if me32.szExePath.endswith(b".dll"):
            module_list.append(me32.szModule)
        ret = ctypes.windll.kernel32.Module32Next(snapshot, ctypes.byref(me32))

    ctypes.windll.kernel32.CloseHandle(snapshot)
    return module_list

def generate_hash(func):
    source_code = inspect.getsource(func)
    lines = source_code.splitlines()
    non_decorator_lines = [line for line in lines if not line.strip().startswith('@')]
    return hashlib.sha256('\n'.join(non_decorator_lines).encode("utf-8")).hexdigest()

def verify_hash(original_hash):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_hash = generate_hash(func)
            if current_hash != original_hash:
                raise ValueError("Integrity check failed.")
            return func(*args, **kwargs)

        return wrapper

    return decorator

def execute_command(command, ram):
    try:
        subprocess.run(command)
    except subprocess.CalledProcessError as e:
        print(f"[!] Процесс не запустился, ошибка: {e}")


def download_and_extract(url: str, extract_dir: str):
    target_folder = os.path.join(extract_dir)
    response = requests.get(url, stream=True)
    filename = url.split('/')[-1].split(".zip")[0] + ".zip"
    target_path = os.path.join(target_folder, filename)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    t = tqdm(total=total_size, unit='B', unit_scale=True, desc=filename, leave=True)
    with open(target_path, 'wb') as file:
        for data in response.iter_content(block_size):
            t.update(len(data))
            file.write(data)
    t.close()

    with zipfile.ZipFile(target_path, 'r') as zip_ref:
        zip_ref.extractall(target_folder)
        try:
            os.remove(target_path)
        except OSError:
            pass

def main_func():
    if not os.path.isdir("C:\\DesyncClient"):
        os.mkdir("C:\\DesyncClient")
        print("[!] Stage 1: Created main directory")
        print("[!] Stage 2: Downloading & extracting required files...")
        download_and_extract(
            "https://www.dropbox.com/scl/fi/td4srz7e2870zlru1skpn/client.zip?rlkey=q6smxa3ma78fqb42nfbmqubfm&st=k6imqtu4&dl=1",
            "C:\\DesyncClient\\")

    while True:
        print(f"Добро пожаловать! \nАвторизованы как: {username}\nВерсия: {build}")
        memory_input = input("[>] Введите кол-во оперативной памяти (в гигабайтах): ")
        try:
            memory = int(memory_input)
            print("[!] Stage 3: Launching client...")
            launch_command = [
                "C:\\DesyncClient\\client\\jre-21.0.2\\bin\\java.exe",
                f"-Xmx{memory}G",
                "-Djava.library.path=C:\\DesyncClient\\client\\natives",
                "-cp",
                "C:\\DesyncClient\\client\\libraries\\*;C:\\DesyncClient\\client\\Excellent.jar",
                "net.minecraft.client.main.Main",
                "--username",
                "test1488",
                "--width",
                "854",
                "--height",
                "480",
                "--version",
                "xyipenis141",
                "--gameDir",
                "C:\\DesyncClient\\game",
                "--assetsDir",
                "C:\\DesyncClient\\client\\assets",
                "--assetIndex",
                "1.16",
                "--accessToken",
                "0"
            ]
            execute_command(launch_command, ram=memory)
            break
        except ValueError:
            print("[!] Введенное значение не является целым числом. Пожалуйста, попробуйте снова.")

def auth():
    print("██████╗░███████╗░██████╗██╗░░░██╗███╗░░██╗░█████╗░  ██╗░░░░░░█████╗░░█████╗░██████╗░███████╗██████╗░")
    print("██╔══██╗██╔════╝██╔════╝╚██╗░██╔╝████╗░██║██╔══██╗  ██║░░░░░██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗")
    print("██║░░██║█████╗░░╚█████╗░░╚████╔╝░██╔██╗██║██║░░╚═╝  ██║░░░░░██║░░██║███████║██║░░██║█████╗░░██████╔╝")
    print("██║░░██║██╔══╝░░░╚═══██╗░░╚██╔╝░░██║╚████║██║░░██╗  ██║░░░░░██║░░██║██╔══██║██║░░██║██╔══╝░░██╔══██╗")
    print("██████╔╝███████╗██████╔╝░░░██║░░░██║░╚███║╚█████╔╝  ███████╗╚█████╔╝██║░░██║██████╔╝███████╗██║░░██║")
    print("╚═════╝░╚══════╝╚═════╝░░░░╚═╝░░░╚═╝░░╚══╝░╚════╝░  ╚══════╝░╚════╝░╚═╝░░╚═╝╚═════╝░╚══════╝╚═╝░░╚═╝")
    print("Запускаю...")
    key = input("Введите ваш ключ: ")
    keyauthapp.license(key)
    sleep(5)
    main_func()


if __name__ == '__main__':
    auth()
    while True:
        pass



