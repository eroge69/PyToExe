import os
import zipfile
import requests
import hashlib
import sys
import webbrowser
import subprocess
from urllib.parse import urlparse
import json as jsond
import time
import binascii
import platform
import qrcode
from datetime import datetime, timezone, timedelta
from discord_interactions import verify_key

try:
    if os.name == 'nt':
        import win32security
except ModuleNotFoundError:
    print("Exception when importing modules")
    print("Installing necessary modules....")
    if os.path.isfile("requirements.txt"):
        os.system("pip install -r requirements.txt")
    else:
        if os.name == 'nt':
            os.system("pip install pywin32")
        os.system("pip install requests discord-interactions qrcode[pil]")
    print("Modules installed!")
    time.sleep(1.5)
    os._exit(1)

# ASCII логотип
logo = [
    "░█████╗░██████╗░██████╗░███████╗███╗░░██╗░█████╗░██╗░░░░░██╗███╗░░██╗███████╗  ███╗░░██╗███████╗██╗░░██╗████████╗",
    "██╔══██╗██╔══██╗██╔══██╗██╔════╝████╗░██║██╔══██╗██║░░░░░██║████╗░██║██╔════╝  ████╗░██║██╔════╝╚██╗██╔╝╚══██╔══╝",
    "███████║██║░░██║██████╔╝█████╗░░██╔██╗██║███████║██║░░░░░██║██╔██╗██║█████╗░░  ██╔██╗██║█████╗░░░╚███╔╝░░░░██║░░░",
    "██╔══██║██║░░██║██╔══██╗██╔══╝░░██║╚████║██╔══██║██║░░░░░██║██║╚████║██╔══╝░░  ██║╚████║██╔══╝░░░██╔██╗░░░░██║░░░",
    "██║░░██║██████╔╝██║░░██║███████╗██║░╚███║██║░░██║███████╗██║██║░╚███║███████╗  ██║░╚███║███████╗██╔╝╚██╗░░░██║░░░",
    "╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚══╝╚═╝░░╚═╝╚══════╝╚═╝╚═╝░░╚══╝╚══════╝  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝░░░╚═╝░░░"
]


def print_logo():
    for line in logo:
        print(line)


def getchecksum():
    md5_hash = hashlib.md5()
    with open(os.path.basename(__file__), 'rb') as file:
        md5_hash.update(file.read())
    return md5_hash.hexdigest()


class KeyAuthAPI:
    name = ownerid = version = hash_to_check = ""

    def __init__(self, name, ownerid, version, hash_to_check):
        if len(ownerid) != 10:
            print("Visit https://keyauth.cc/app/, copy Python code, and replace code in main.py with that")
            time.sleep(3)
            os._exit(1)

        self.name = name
        self.ownerid = ownerid
        self.version = version
        self.hash_to_check = hash_to_check
        self.sessionid = ""
        self.enckey = ""
        self.initialized = False
        self.init()

    def init(self):
        if self.sessionid != "":
            print("You've already initialized!")
            time.sleep(3)
            os._exit(1)

        post_data = {
            "type": "init",
            "ver": self.version,
            "hash": self.hash_to_check,
            "name": self.name,
            "ownerid": self.ownerid
        }

        response = self.__do_request(post_data)

        if response == "KeyAuth_Invalid":
            print("The application doesn't exist")
            time.sleep(3)
            os._exit(1)

        json = jsond.loads(response)

        if json["message"] == "invalidver":
            if json["download"] != "":
                print("New Version Available")
                download_link = json["download"]
                os.system(f"start {download_link}")
                time.sleep(3)
                os._exit(1)
            else:
                print("Invalid Version, Contact owner to add download link to latest app version")
                time.sleep(3)
                os._exit(1)

        if not json["success"]:
            print(json["message"])
            time.sleep(3)
            os._exit(1)

        self.sessionid = json["sessionid"]
        self.initialized = True

    def license(self, key, code=None, hwid=None):
        self.checkinit()
        if hwid is None:
            hwid = self.get_hwid()

        post_data = {
            "type": "license",
            "key": key,
            "hwid": hwid,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }

        if code is not None:
            post_data["code"] = code

        response = self.__do_request(post_data)

        json = jsond.loads(response)

        if json["success"]:
            self.__load_user_data(json["info"])
            print(json["message"])
        else:
            print(json["message"])
            time.sleep(3)
            os._exit(1)

    def get_hwid(self):
        if platform.system() == "Linux":
            with open("/etc/machine-id") as f:
                hwid = f.read()
                return hwid
        elif platform.system() == 'Windows':
            winuser = os.getlogin()
            sid = win32security.LookupAccountName(None, winuser)[0]
            hwid = win32security.ConvertSidToStringSid(sid)
            return hwid
        elif platform.system() == 'Darwin':
            output = subprocess.Popen("ioreg -l | grep IOPlatformSerialNumber", stdout=subprocess.PIPE,
                                      shell=True).communicate()[0]
            serial = output.decode().split('=', 1)[1].replace(' ', '')
            hwid = serial[1:-2]
            return hwid

    def checkinit(self):
        if not self.initialized:
            print("Initialize first, in order to use the functions")
            time.sleep(3)
            os._exit(1)

    def __do_request(self, post_data):
        try:
            response = requests.post(
                "https://keyauth.win/api/1.3/", data=post_data, timeout=10
            )

            if post_data["type"] == "log" or post_data["type"] == "file" or post_data["type"] == "2faenable" or \
                    post_data["type"] == "2fadisable":
                return response.text

            signature = response.headers.get("x-signature-ed25519")
            timestamp = response.headers.get("x-signature-timestamp")

            if not signature or not timestamp:
                print("Missing headers for signature verification.")
                time.sleep(3)
                os._exit(1)

            server_time = datetime.fromtimestamp(int(timestamp), timezone.utc)
            current_time = datetime.now(timezone.utc)

            buffer_seconds = 5
            time_difference = current_time - server_time

            if time_difference > timedelta(seconds=20 + buffer_seconds):
                print("Timestamp is too old (exceeded 20 seconds + buffer).")
                time.sleep(3)
                os._exit(1)

            if not verify_key(response.text.encode('utf-8'), signature, timestamp,
                              '5586b4bc69c7a4b487e4563a4cd96afd39140f919bd31cea7d1c6a1e8439422b'):
                print("Signature checksum failed. Request was tampered with or session ended most likely.")
                time.sleep(3)
                os._exit(1)

            return response.text

        except requests.exceptions.Timeout:
            print("Request timed out. Server is probably down/slow at the moment")
            time.sleep(3)
            os._exit(1)

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


class AuthManager:
    def __init__(self):
        self.keyauthapp = None
        self.initialize_auth()

    def initialize_auth(self):
        try:
            self.keyauthapp = KeyAuthAPI(
                name="Stasivcenko792's Application",
                ownerid="BHYK4V1EsI",
                version="1.0",
                hash_to_check=getchecksum()
            )
            return True
        except Exception as e:
            print(f"[AUTH ERROR] Ошибка инициализации KeyAuth: {str(e)}")
            return False

    def authenticate(self):
        if not self.keyauthapp:
            print("[ERROR] KeyAuth не инициализирован")
            return False

        try:
            print("\n")
            print_logo()
            print("\n=== АВТОРИЗАЦИЯ ПО ЛИЦЕНЗИИ ===")

            license_file = "license.txt"
            saved_key_exists = os.path.exists(license_file)

            if saved_key_exists:
                with open(license_file, "r") as f:
                    saved_key = f.read().strip()

                print("\n1. Использовать сохраненный ключ")
                print("2. Ввести новый ключ")
                print("3. Наш Telegram (помощь)")
                print("4. Выход")

                choice = input("\nВыберите вариант (1-4): ")

                if choice == "1":
                    print("\nИспользуется сохраненный ключ...")
                    self.keyauthapp.license(saved_key)
                elif choice == "2":
                    new_key = input("\nВведите новый лицензионный ключ: ").strip()
                    self.keyauthapp.license(new_key)

                    with open(license_file, "w") as f:
                        f.write(new_key)
                    print("Новый ключ сохранен!")
                elif choice == "3":
                    webbrowser.open("https://t.me/amphetaminereload")
                    return self.authenticate()
                elif choice == "4":
                    print("Выход...")
                    return False
                else:
                    print("Неверный выбор, попробуйте снова.")
                    return self.authenticate()
            else:
                print("Пожалуйста, введите ваш лицензионный ключ")
                print("Если у вас нет ключа, посетите наш Telegram: https://t.me/amphetaminereload")
                license_key = input("Ключ: ").strip()
                self.keyauthapp.license(license_key)

                with open(license_file, "w") as f:
                    f.write(license_key)
                print("Лицензия активирована! Данные сохранены.")

            print(f"\nДобро пожаловать! Лицензия активна до: {self.keyauthapp.user_data.expires}")
            print(f"Подписка: {self.keyauthapp.user_data.subscriptions}")
            return True

        except Exception as e:
            print(f"\n[ОШИБКА] Авторизация не удалась: {str(e)}")
            if os.path.exists(license_file):
                os.remove(license_file)
            return False


def download_file(url, destination):
    local_filename = os.path.join(destination, os.path.basename(urlparse(url).path))
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return local_filename
    except Exception as e:
        print(f"[DOWNLOAD ERROR] Ошибка загрузки файла: {str(e)}")
        return None


def extract_zip(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        os.remove(zip_path)
        return True
    except Exception as e:
        print(f"[EXTRACT ERROR] Ошибка распаковки: {str(e)}")
        return False


def download_and_extract(url, destination):
    print(f"\n[Загрузка] {url}")
    zip_path = download_file(url, destination)
    if not zip_path:
        return False

    print(f"[Распаковка] {zip_path}")
    if not extract_zip(zip_path, destination):
        return False

    print("[Успешно] Файлы установлены")
    return True


def show_info():
    print("\n=== ИНФОРМАЦИЯ ===")
    print("Adrenaline/amphetamine v1.0(test)")
    print("Разработчик: tg: @dellsrc_out")
    print("Лицензия: требуется активация")
    print("Telegram: https://t.me/amphetaminereload")
    print("Рекомендую поставить 4гб памяти для стабильной работы")
    input("\nНажмите Enter чтобы вернуться в меню...")


def update_client():
    print("\n=== ОБНОВЛЕНИЕ КЛИЕНТА ===")
    jar_zip_url = "https://www.dropbox.com/scl/fi/nzafd0ps0rkuldfapms64/adrenaline.jar.zip?rlkey=010w4cm7e8d277g18eiie5nxm&st=bzslxb6z&dl=1"
    client_dir = "C:\\adrenaline\\client"

    if not os.path.exists(client_dir):
        os.makedirs(client_dir, exist_ok=True)

    if os.path.exists(os.path.join(client_dir, "adrenaline.jar")):
        os.remove(os.path.join(client_dir, "adrenaline.jar"))
        print("Старая версия клиента удалена.")

    if download_and_extract(jar_zip_url, client_dir):
        print("Клиент успешно обновлен!")
    else:
        print("Не удалось обновить клиент.")

    input("\nНажмите Enter чтобы вернуться в меню...")


def select_ram():
    print("\n=== ВЫБОР ОПЕРАТИВНОЙ ПАМЯТИ ===")
    print("1. 2GB (минимум)")
    print("2. 4GB (рекомендуется)")
    print("3. 6GB")
    print("4. 8GB")
    print("5. Вручную")

    choice = input("\nВыберите вариант (1-5): ")

    ram_mapping = {
        '1': 2048,
        '2': 4096,
        '3': 6144,
        '4': 8192
    }

    if choice in ram_mapping:
        return ram_mapping[choice]
    elif choice == '5':
        try:
            custom_ram = int(input("Введите количество MB (например, 3072 для 3GB): "))
            return custom_ram
        except ValueError:
            print("Некорректный ввод, будет использовано значение по умолчанию (2048MB)")
            return 2048
    else:
        print("Неверный выбор, будет использовано значение по умолчанию (2048MB)")
        return 2048


def launch_minecraft(ram=2048):
    base_dir = "C:\\adrenaline"
    client_dir = os.path.join(base_dir, "client")
    game_dir = os.path.join(base_dir, "game")

    java_path = os.path.join(client_dir, "jdk-19.0.2", "bin", "java.exe")
    if not os.path.exists(java_path):
        print("\n[ОШИБКА] Java не найдена!")
        input("Нажмите Enter для выхода...")
        return False

    print(f"\n[Запуск] Подготовка к запуску Minecraft с {ram}MB RAM...")
    cmd = [
        java_path,
        f"-Xmx{ram}M",
        "-Djava.library.path=C:\\adrenaline\\client\\natives",
        "-cp",
        "C:\\adrenaline\\client\\libraries\\*;C:\\adrenaline\\client\\adrenaline.jar",
        "net.minecraft.client.main.Main",
        "--username", "Player",
        "--width", "854",
        "--height", "480",
        "--version", "adrenaline",
        "--gameDir", "C:\\adrenaline\\game",
        "--assetsDir", "C:\\adrenaline\\client\\assets",
        "--assetIndex", "1.16",
        "--accessToken", "0"
    ]

    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        subprocess.Popen(
            cmd,
            creationflags=subprocess.CREATE_NO_WINDOW,
            startupinfo=startupinfo
        )
        return True
    except Exception as e:
        print(f"[LAUNCH ERROR] Ошибка запуска Minecraft: {str(e)}")
        return False


def main_menu():
    auth_manager = AuthManager()

    if not auth_manager.authenticate():
        print("[ERROR] Не удалось авторизоваться")
        input("Нажмите Enter для выхода...")
        return

    base_dir = "C:\\adrenaline"
    client_dir = os.path.join(base_dir, "client")
    game_dir = os.path.join(base_dir, "game")

    os.makedirs(client_dir, exist_ok=True)
    os.makedirs(game_dir, exist_ok=True)

    client_zip_url = "https://www.dropbox.com/scl/fi/z6060t7hfmlfllpipyk61/client.zip?rlkey=0dla83j3vsoj7md937hsz0a55&st=rlfo46kn&dl=1"
    jar_zip_url = "https://www.dropbox.com/scl/fi/nzafd0ps0rkuldfapms64/adrenaline.jar.zip?rlkey=010w4cm7e8d277g18eiie5nxm&st=bzslxb6z&dl=1"

    if not os.path.exists(os.path.join(client_dir, "libraries")):
        print("\n[ИНФО] Обнаружена первая установка, загружаем необходимые файлы...")
        if not download_and_extract(client_zip_url, base_dir):
            input("Нажмите Enter для выхода...")
            return

    if not os.path.exists(os.path.join(client_dir, "adrenaline.jar")):
        if not download_and_extract(jar_zip_url, client_dir):
            input("Нажмите Enter для выхода...")
            return

    while True:
        print("\n")
        print_logo()
        print("\n=== ADRENALINE CLIENT ===")
        print("1. Запустить клиент (2048MB)")
        print("2. Выбрать объем оперативной памяти")
        print("3. Информация")
        print("4. Установить/обновить клиент")
        print("5. Наш Telegram")
        print("6. Выход")

        choice = input("\nВыберите вариант (1-6): ")

        if choice == "1":
            if launch_minecraft():
                print("\nMinecraft запускается... Лоудер будет закрыт.")
                sys.exit(0)
            else:
                print("\nНе удалось запустить Minecraft.")
                input("Нажмите Enter чтобы вернуться в меню...")
        elif choice == "2":
            ram = select_ram()
            if launch_minecraft(ram):
                print("\nMinecraft запускается... Лоудер будет закрыт.")
                sys.exit(0)
            else:
                print("\nНе удалось запустить Minecraft.")
                input("Нажмите Enter чтобы вернуться в меню...")
        elif choice == "3":
            show_info()
        elif choice == "4":
            update_client()
        elif choice == "5":
            webbrowser.open("https://t.me/amphetaminereload")
        elif choice == "6":
            print("\nВыход из программы...")
            sys.exit(0)
        else:
            print("\nНеверный выбор, попробуйте снова.")


if __name__ == "__main__":
    if sys.platform == "win32":
        import ctypes

        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    main_menu()