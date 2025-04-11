
# Free Pasta Loader by Ksynax
# https://t.me/ksynax
# https://www.youtube.com/@Ksynax_ru
# Version: 1.1

import ctypes
import functools
import hashlib
import inspect
import json
import os
import os.path
import subprocess
import sys
import time
import zipfile

import requests
from colorama import init, Fore
from tqdm import tqdm

ctypes.windll.kernel32.SetConsoleTitleA(b"Loader")
init(autoreset=True)

logo = [
    "██████╗░███████╗░██████╗██╗░░░██╗███╗░░██╗░█████╗░  ██╗░░░░░░█████╗░░█████╗░██████╗░███████╗██████╗░",
    "██╔══██╗██╔════╝██╔════╝╚██╗░██╔╝████╗░██║██╔══██╗  ██║░░░░░██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗",
    "██║░░██║█████╗░░╚█████╗░░╚████╔╝░██╔██╗██║██║░░╚═╝  ██║░░░░░██║░░██║███████║██║░░██║█████╗░░██████╔╝",
    "██║░░██║██╔══╝░░░╚═══██╗░░╚██╔╝░░██║╚████║██║░░██╗  ██║░░░░░██║░░██║██╔══██║██║░░██║██╔══╝░░██╔══██╗",
    "██████╔╝███████╗██████╔╝░░░██║░░░██║░╚███║╚█████╔╝  ███████╗╚█████╔╝██║░░██║██████╔╝███████╗██║░░██║",
    "╚═════╝░╚══════╝╚═════╝░░░░╚═╝░░░╚═╝░░╚══╝░╚════╝░  ╚══════╝░╚════╝░╚═╝░░╚═╝╚═════╝░╚══════╝╚═╝░░╚═╝"
]

username = "Test"
till = "12.12.2222"
build = "Stable 1.16.5"
last_update_date = "14.14.2088"
loader_ver = "1.1"

IGNORED_MODULES = []
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

config_path = "C:\\Nemesis\\config\\memory_config.json"
def load_memory_config():
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)
            return config.get("memory", "2048")
    return "2048"

def save_memory_config(memory):
    config = {"memory": memory}
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as file:
        json.dump(config, file)

def ram_select():
    default_memory = load_memory_config()
    print(f"Текущее количество памяти: {default_memory} MB")
    user_input = input("Введите количество памяти в MB (по умолчанию 2048): ").strip()
    if user_input.isdigit():
        memory = user_input
    else:
        memory = default_memory
    save_memory_config(memory)
    print(f"Выбранное количество памяти: {memory} MB")
    return memory



def build_select():
    print("\nБудет доступно позже...\n")

# ФУНКЦИЯ СТАРТА КЛИЕНТА
def start():
    if not os.path.isdir("C:\\Nemesis") or os.path.isdir("C:\\Nemesis\\client"):
        os.mkdir("C:\\Nemesis")
        print("[!] Создаём main директорию...")
        print("[!] Скачиваем и распаковываем файлы клиента...")
        download_and_extract(
            "https://mega.nz/file/OMkEXZpZ#DU-89N51Q3gmD3UOPzn8ycBhXWAFC4J3249VxptdWvo",
            "C:\\Nemesis\\")
    if os.path.isdir("C:\\Nemesis\\client\\client.jar"):
        os.remove("C:\\Nemesis\\client\\client.jar")
    if os.path.isdir("C:\\Nemesis\\client\\jar.zip"):
        os.remove("C:\\Nemesis\\client\\jar.zip")
    print("[!] Загружаю последнее обновление...")
    download_and_extract("https://mega.nz/file/iclAHA7J#7C3PqBl0Ji-Jyoean1_G-SAGAVORgoczlD0oqZDHmes", "C:\\Nemesis\\client")
    memory = load_memory_config()
    while True:
        try:
            print("[!] Запускаю клиент...\n[!] Приятной игры!")
            launch_command = [
                "C:\\Nemesis\\client\\jre-21.0.2\\bin\\java.exe",
                f"-Xmx{memory}G",
                "-Djava.library.path=C:\\Nemesis\\client\\natives",
                "-cp",
                "C:\\Nemesis\\client\\libraries\\*;C:\\Nemesis\\client\\client.jar",
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
                "C:\\Nemesis\\game",
                "--assetsDir",
                "C:\\Nemesis\\client\\assets",
                "--assetIndex",
                "1.16",
                "--accessToken",
                "0"
            ]
            execute_command(launch_command, ram=memory)
            break
        except ValueError:
            print("[!] Введенное значение не является целым числом. Пожалуйста, попробуйте снова.")

def info():
    print(f"\nВерсия клиента: {build}")
    print(f"Имя пользователя: {username}")
    print(f"Подписка до: {till}")
    print(f"Дата последнего обновления: {last_update_date}")
    print(f"Версия лоадера: {loader_ver}\n")


def selector():
    while True:
        enter = input(Fore.CYAN + "Выберите пункт: ")
        if enter == "1":
            start()

        elif enter == "2":
            ram_select()
            print("Изменения сохранены...\nПерезапустите лоадер...\nЛоадер будет закрыт через 5 секунд...")
            time.sleep(5)
            sys.exit()

        elif enter == "3":
            build_select()

        elif enter == "4":
            info()

        else:
            print("Неккоректный выбор!")
            print(f"Выберите пункт: {enter}")

# ФУНКЦИЯ АВТОРИЗАЦИИ AKA ИНИЦИЛИЗАЦИИ
def auth():
    for line in logo:
        print(Fore.CYAN + line)
    print("Запускаю...")
    time.sleep(3)
    main_func()

# MAIN ФУНКЦИЯ
def main_func():
    print("\nДобро пожаловать!")
    print("=============================")
    print("[1] Запуск клиента")
    print("[2] Выбор RAM")
    print("[3] Выбор версии клиента")
    print("[4] Информация")
    print("=============================\n")
    selector()

if __name__ == '__main__':
    auth()
    while True:
        pass