import os
import sys
import ctypes
import winreg
import subprocess
import requests
import hashlib
import platform
import psutil
import socket
import shutil
import datetime
import wmi
from time import sleep
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ==================== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ====================
VERSION = "3.0"
ADMIN_MODE = False
SYSTEM_INFO = {}

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def get_system_info():
    global SYSTEM_INFO
    SYSTEM_INFO = {
        "os": platform.system(),
        "version": platform.version(),
        "architecture": platform.architecture(),
        "processor": platform.processor(),
        "ram": round(psutil.virtual_memory().total / (1024**3), 2),
        "disks": psutil.disk_partitions()
    }

# ==================== ОСНОВНЫЕ ФУНКЦИИ (45+) ====================
class SystemFunctions:
    @staticmethod
    def unlock_task_manager():
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                               0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, "DisableTaskMgr")
            return True, "Диспетчер задач разблокирован!"
        except WindowsError:
            return False, "Ограничение не найдено или уже снято"

    @staticmethod
    def repair_mbr():
        try:
            commands = [
                "bootrec /fixmbr",
                "bootrec /fixboot",
                "bootrec /scanos",
                "bootrec /rebuildbcd"
            ]
            for cmd in commands:
                subprocess.run(cmd, shell=True, check=True)
            return True, "MBR/GPT успешно восстановлен!"
        except subprocess.CalledProcessError as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def clean_temp_files():
        try:
            temp_folders = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('SystemRoot', ''), 'Temp'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp')
            ]
            
            deleted = 0
            for folder in temp_folders:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                                deleted += 1
                        except Exception as e:
                            continue
            
            return True, f"Удалено {deleted} временных файлов!"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def enable_god_mode():
        try:
            god_mode_dir = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'GodMode')
            os.makedirs(god_mode_dir, exist_ok=True)
            
            with open(os.path.join(god_mode_dir, 'GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}'), 'w') as f:
                pass
                
            return True, "GodMode активирован на рабочем столе!"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def manage_startup():
        try:
            startup_path = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            os.startfile(startup_path)
            return True, "Папка автозагрузки открыта"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def create_restore_point():
        try:
            subprocess.run('wmic.exe /Namespace:\\\\root\\default Path SystemRestore Call CreateRestorePoint "HelperProgram Restore", 100, 7', shell=True)
            return True, "Точка восстановления создана!"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def optimize_drives():
        try:
            subprocess.run('defrag /C /H /V', shell=True)
            return True, "Оптимизация дисков выполнена!"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def check_ram():
        try:
            mem = psutil.virtual_memory()
            return True, f"ОЗУ: {mem.percent}% используется ({mem.used/1024/1024:.0f} MB из {mem.total/1024/1024:.0f} MB)"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def manage_services():
        try:
            os.system('services.msc')
            return True, "Диспетчер служб открыт"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def show_system_info():
        try:
            info = []
            info.append(f"ОС: {platform.system()} {platform.version()}")
            info.append(f"Архитектура: {platform.architecture()[0]}")
            info.append(f"Процессор: {platform.processor()}")
            info.append(f"ОЗУ: {round(psutil.virtual_memory().total / (1024**3), 2)} GB")
            
            disks = []
            for part in psutil.disk_partitions():
                usage = psutil.disk_usage(part.mountpoint)
                disks.append(f"{part.device} ({part.mountpoint}) - {usage.percent}% заполнено")
            
            return True, "Системная информация:\n" + "\n".join(info) + "\n\nДиски:\n" + "\n".join(disks)
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def show_ip_addresses():
        try:
            result = []
            hostname = socket.gethostname()
            result.append(f"Имя компьютера: {hostname}")
            
            for interface, addrs in psutil.net_if_addrs().items():
                result.append(f"\nИнтерфейс: {interface}")
                for addr in addrs:
                    result.append(f"  {addr.family.name}: {addr.address}")
            
            return True, "\n".join(result)
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def flush_dns():
        try:
            subprocess.run('ipconfig /flushdns', shell=True, check=True)
            return True, "DNS кэш очищен!"
        except subprocess.CalledProcessError as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def check_ports():
        try:
            connections = psutil.net_connections()
            result = []
            for conn in connections:
                if conn.status == 'LISTEN':
                    result.append(f"Порт {conn.laddr.port} ({conn.status}) - PID {conn.pid}")
            return True, "Открытые порты:\n" + "\n".join(result[:20])  # Ограничиваем вывод
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def analyze_network():
        try:
            io = psutil.net_io_counters()
            return True, f"Сетевой трафик:\nОтправлено: {io.bytes_sent/1024/1024:.2f} MB\nПолучено: {io.bytes_recv/1024/1024:.2f} MB"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def manage_network_adapters():
        try:
            os.system('ncpa.cpl')
            return True, "Сетевые подключения открыты"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def ping_host():
        host, ok = QInputDialog.getText(None, 'Ping', 'Введите хост:')
        if ok and host:
            try:
                result = subprocess.run(f'ping {host}', shell=True, capture_output=True, text=True)
                return True, result.stdout
            except Exception as e:
                return False, f"Ошибка: {e}"
        return False, "Отменено"

    @staticmethod
    def show_arp_table():
        try:
            result = subprocess.run('arp -a', shell=True, capture_output=True, text=True)
            return True, result.stdout
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def analyze_routes():
        try:
            result = subprocess.run('route print', shell=True, capture_output=True, text=True)
            return True, result.stdout
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def check_internet_speed():
        try:
            import speedtest
            st = speedtest.Speedtest()
            download = st.download()/1024/1024
            upload = st.upload()/1024/1024
            return True, f"Скорость интернета:\nСкачивание: {download:.2f} Mbps\nОтправка: {upload:.2f} Mbps"
        except Exception as e:
            return False, f"Ошибка: {e}. Установите модуль speedtest-cli"

    @staticmethod
    def check_system_files():
        try:
            result = subprocess.run('sfc /scannow', shell=True, capture_output=True, text=True)
            return True, result.stdout
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def scan_viruses():
        try:
            result = subprocess.run('"%ProgramFiles%\\Windows Defender\\MpCmdRun.exe" -Scan -ScanType 1', shell=True, capture_output=True, text=True)
            return True, "Сканирование Windows Defender запущено!\n" + result.stdout
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def manage_firewall():
        try:
            os.system('wf.msc')
            return True, "Брандмауэр открыт"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def check_security_updates():
        try:
            result = subprocess.run('wmic qfe list', shell=True, capture_output=True, text=True)
            return True, "Установленные обновления:\n" + result.stdout
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def analyze_processes():
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                processes.append(f"{proc.info['pid']} {proc.info['name']} {proc.info['username']}")
            return True, "Процессы:\n" + "\n".join(processes[:50])  # Ограничиваем вывод
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def check_rootkits():
        try:
            suspicious = []
            for proc in psutil.process_iter():
                try:
                    exe = proc.exe()
                    if "temp" in exe.lower() or "appdata" in exe.lower():
                        suspicious.append(f"{proc.pid} {proc.name()} {exe}")
                except:
                    continue
            if suspicious:
                return False, "Подозрительные процессы:\n" + "\n".join(suspicious)
            return True, "Подозрительные процессы не найдены"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def check_digital_signatures():
        try:
            result = subprocess.run('sigverif', shell=True)
            return True, "Проверка цифровых подписей запущена"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def manage_users():
        try:
            os.system('lusrmgr.msc')
            return True, "Управление пользователями открыто"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def repair_bootloader():
        try:
            subprocess.run('bcdedit /export C:\\BCD_Backup', shell=True)
            subprocess.run('bootrec /rebuildbcd', shell=True)
            return True, "Загрузчик восстановлен (резервная копия в C:\\BCD_Backup)"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def repair_registry():
        try:
            subprocess.run('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion" /v SystemRoot /t REG_SZ /d %SystemRoot% /f', shell=True)
            return True, "Ключи реестра восстановлены"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def repair_system_files():
        try:
            subprocess.run('DISM /Online /Cleanup-Image /RestoreHealth', shell=True)
            subprocess.run('sfc /scannow', shell=True)
            return True, "Системные файлы восстановлены"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def safe_boot():
        try:
            subprocess.run('bcdedit /set {current} safeboot minimal', shell=True)
            return True, "Безопасный режим активирован (перезагрузите компьютер)"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def access_winre():
        try:
            subprocess.run('reagentc /boottore', shell=True)
            return True, "WinRE будет запущен при следующей перезагрузке"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def reset_admin_password():
        try:
            subprocess.run('net user Administrator *', shell=True)
            return True, "Введите новый пароль для Administrator"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def repair_network():
        try:
            commands = [
                'netsh winsock reset',
                'netsh int ip reset',
                'ipconfig /release',
                'ipconfig /renew',
                'ipconfig /flushdns'
            ]
            for cmd in commands:
                subprocess.run(cmd, shell=True)
            return True, "Сетевые настройки сброшены!"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def open_registry_editor():
        try:
            os.system('regedit')
            return True, "Редактор реестра открыт"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def advanced_task_manager():
        try:
            os.system('taskmgr')
            return True, "Диспетчер задач открыт"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def resource_monitor():
        try:
            os.system('resmon')
            return True, "Монитор ресурсов открыт"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def disk_space_analyzer():
        try:
            os.system('cleanmgr')
            return True, "Очистка диска запущена"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def device_manager():
        try:
            os.system('devmgmt.msc')
            return True, "Диспетчер устройств открыт"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def event_viewer():
        try:
            os.system('eventvwr.msc')
            return True, "Просмотр событий открыт"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def manage_updates():
        try:
            os.system('control update')
            return True, "Центр обновлений открыт"
        except Exception as e:
            return False, f"Ошибка: {e}"

    @staticmethod
    def optimize_system():
        try:
            commands = [
                'powercfg /h off',
                'bcdedit /set {current} bootmenupolicy legacy',
                'reg add "HKCU\\Control Panel\\Desktop" /v MenuShowDelay /t REG_SZ /d 0 /f'
            ]
            for cmd in commands:
                subprocess.run(cmd, shell=True)
            return True, "Оптимизация выполнена!"
        except Exception as e:
            return False, f"Ошибка: {e}"

# ==================== ГРАФИЧЕСКИЙ ИНТЕРФЕЙС ====================
class HelperProgram(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"HelperProgram {VERSION}")
        self.setGeometry(100, 100, 900, 700)
        
        if not is_admin():
            self.show_message("Требуются права администратора!")
            run_as_admin()
        
        self.init_ui()
        get_system_info()
        
    def init_ui(self):
        # Главный виджет и layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Панель вкладок
        tabs = QTabWidget()
        
        # 1. Вкладка "Система"
        system_tab = QWidget()
        system_layout = QVBoxLayout()
        
        system_functions = [
            ("Разблокировать Диспетчер задач", self.unlock_task_manager),
            ("Восстановить MBR/GPT", self.repair_mbr),
            ("Очистить временные файлы", self.clean_temp_files),
            ("Включить GodMode", self.enable_god_mode),
            ("Управление автозагрузкой", self.manage_startup),
            ("Создать точку восстановления", self.create_restore_point),
            ("Оптимизировать диски", self.optimize_drives),
            ("Проверить ОЗУ", self.check_ram),
            ("Управление службами", self.manage_services),
            ("Системная информация", self.show_system_info)
        ]
        
        for text, slot in system_functions:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            system_layout.addWidget(btn)
        
        system_tab.setLayout(system_layout)
        
        # 2. Вкладка "Сеть"
        network_tab = QWidget()
        network_layout = QVBoxLayout()
        
        network_functions = [
            ("Показать IP-адреса", self.show_ip_addresses),
            ("Сбросить кэш DNS", self.flush_dns),
            ("Проверить открытые порты", self.check_ports),
            ("Анализ сетевого трафика", self.analyze_network),
            ("Управление сетевыми адаптерами", self.manage_network_adapters),
            ("Ping хоста", self.ping_host),
            ("Показать ARP-таблицу", self.show_arp_table),
            ("Анализ маршрутов", self.analyze_routes),
            ("Проверить скорость интернета", self.check_internet_speed)
        ]
        
        for text, slot in network_functions:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            network_layout.addWidget(btn)
        
        network_tab.setLayout(network_layout)
        
        # 3. Вкладка "Безопасность"
        security_tab = QWidget()
        security_layout = QVBoxLayout()
        
        security_functions = [
            ("Проверить целостность системных файлов", self.check_system_files),
            ("Сканировать на вирусы", self.scan_viruses),
            ("Управление брандмауэром", self.manage_firewall),
            ("Проверить обновления безопасности", self.check_security_updates),
            ("Анализ запущенных процессов", self.analyze_processes),
            ("Поиск руткитов", self.check_rootkits),
            ("Проверить цифровые подписи", self.check_digital_signatures),
            ("Управление пользователями", self.manage_users)
        ]
        
        for text, slot in security_functions:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            security_layout.addWidget(btn)
        
        security_tab.setLayout(security_layout)
        
        # 4. Вкладка "Восстановление"
        recovery_tab = QWidget()
        recovery_layout = QVBoxLayout()
        
        recovery_functions = [
            ("Восстановить загрузчик", self.repair_bootloader),
            ("Восстановить реестр", self.repair_registry),
            ("Восстановить системные файлы", self.repair_system_files),
            ("Безопасный режим", self.safe_boot),
            ("Доступ к WinRE", self.access_winre),
            ("Сбросить пароль администратора", self.reset_admin_password),
            ("Восстановить сеть", self.repair_network)
        ]
        
        for text, slot in recovery_functions:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            recovery_layout.addWidget(btn)
        
        recovery_tab.setLayout(recovery_layout)
        
        # 5. Вкладка "Инструменты"
        tools_tab = QWidget()
        tools_layout = QVBoxLayout()
        
        tools_functions = [
            ("Редактор реестра", self.open_registry_editor),
            ("Продвинутый Диспетчер задач", self.advanced_task_manager),
            ("Монитор ресурсов", self.resource_monitor),
            ("Анализатор дискового пространства", self.disk_space_analyzer),
            ("Диспетчер устройств", self.device_manager),
            ("Просмотр событий", self.event_viewer),
            ("Управление обновлениями", self.manage_updates),
            ("Оптимизация системы", self.optimize_system)
        ]
        
        for text, slot in tools_functions:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            tools_layout.addWidget(btn)
        
        tools_tab.setLayout(tools_layout)
        
        # Добавляем вкладки
        tabs.addTab(system_tab, "Система")
        tabs.addTab(network_tab, "Сеть")
        tabs.addTab(security_tab, "Безопасность")
        tabs.addTab(recovery_tab, "Восстановление")
        tabs.addTab(tools_tab, "Инструменты")
        
        # Лог действий
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        
        # Добавляем элементы в главный layout
        main_layout.addWidget(tabs)
        main_layout.addWidget(QLabel("Лог действий:"))
        main_layout.addWidget(self.log_area)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Статус бар
        self.statusBar().showMessage("Готово")
    
    # ==================== ОБРАБОТЧИКИ СОБЫТИЙ ====================
    def unlock_task_manager(self):
        success, message = SystemFunctions.unlock_task_manager()
        self.log(message)
        self.show_message(message)
    
    def repair_mbr(self):
        success, message = SystemFunctions.repair_mbr()
        self.log(message)
        self.show_message(message)
    
    def clean_temp_files(self):
        success, message = SystemFunctions.clean_temp_files()
        self.log(message)
        self.show_message(message)
    
    def enable_god_mode(self):
        success, message = SystemFunctions.enable_god_mode()
        self.log(message)
        self.show_message(message)
    
    def manage_startup(self):
        success, message = SystemFunctions.manage_startup()
        self.log(message)
        self.show_message(message)
    
    def create_restore_point(self):
        success, message = SystemFunctions.create_restore_point()
        self.log(message)
        self.show_message(message)
    
    def optimize_drives(self):
        success, message = SystemFunctions.optimize_drives()
        self.log(message)
        self.show_message(message)
    
    def check_ram(self):
        success, message = SystemFunctions.check_ram()
        self.log(message)
        self.show_message(message)
    
    def manage_services(self):
        success, message = SystemFunctions.manage_services()
        self.log(message)
        self.show_message(message)
    
    def show_system_info(self):
        success, message = SystemFunctions.show_system_info()
        self.log(message)
        self.show_message(message)
    
    def show_ip_addresses(self):
        success, message = SystemFunctions.show_ip_addresses()
        self.log(message)
        self.show_message(message)
    
    def flush_dns(self):
        success, message = SystemFunctions.flush_dns()
        self.log(message)
        self.show_message(message)
    
    def check_ports(self):
        success, message = SystemFunctions.check_ports()
        self.log(message)
        self.show_message(message)
    
    def analyze_network(self):
        success, message = SystemFunctions.analyze_network()
        self.log(message)
        self.show_message(message)
    
    def manage_network_adapters(self):
        success, message = SystemFunctions.manage_network_adapters()
        self.log(message)
        self.show_message(message)
    
    def ping_host(self):
        success, message = SystemFunctions.ping_host()
        self.log(message)
        self.show_message(message)
    
    def show_arp_table(self):
        success, message = SystemFunctions.show_arp_table()
        self.log(message)
        self.show_message(message)
    
    def analyze_routes(self):
        success, message = SystemFunctions.analyze_routes()
        self.log(message)
        self.show_message(message)
    
    def check_internet_speed(self):
        success, message = SystemFunctions.check_internet_speed()
        self.log(message)
        self.show_message(message)
    
    def check_system_files(self):
        success, message = SystemFunctions.check_system_files()
        self.log(message)
        self.show_message(message)
    
    def scan_viruses(self):
        success, message = SystemFunctions.scan_viruses()
        self.log(message)
        self.show_message(message)
    
    def manage_firewall(self):
        success, message = SystemFunctions.manage_firewall()
        self.log(message)
        self.show_message(message)
    
    def check_security_updates(self):
        success, message = SystemFunctions.check_security_updates()
        self.log(message)
        self.show_message(message)
    
    def analyze_processes(self):
        success, message = SystemFunctions.analyze_processes()
        self.log(message)
        self.show_message(message)
    
    def check_rootkits(self):
        success, message = SystemFunctions.check_rootkits()
        self.log(message)
        self.show_message(message)
    
    def check_digital_signatures(self):
        success, message = SystemFunctions.check_digital_signatures()
        self.log(message)
        self.show_message(message)
    
    def manage_users(self):
        success, message = SystemFunctions.manage_users()
        self.log(message)
        self.show_message(message)
    
    def repair_bootloader(self):
        success, message = SystemFunctions.repair_bootloader()
        self.log(message)
        self.show_message(message)
    
    def repair_registry(self):
        success, message = SystemFunctions.repair_registry()
        self.log(message)
        self.show_message(message)
    
    def repair_system_files(self):
        success, message = SystemFunctions.repair_system_files()
        self.log(message)
        self.show_message(message)
    
    def safe_boot(self):
        success, message = SystemFunctions.safe_boot()
        self.log(message)
        self.show_message(message)
    
    def access_winre(self):
        success, message = SystemFunctions.access_winre()
        self.log(message)
        self.show_message(message)
    
    def reset_admin_password(self):
        success, message = SystemFunctions.reset_admin_password()
        self.log(message)
        self.show_message(message)
    
    def repair_network(self):
        success, message = SystemFunctions.repair_network()
        self.log(message)
        self.show_message(message)
    
    def open_registry_editor(self):
        success, message = SystemFunctions.open_registry_editor()
        self.log(message)
        self.show_message(message)
    
    def advanced_task_manager(self):
        success, message = SystemFunctions.advanced_task_manager()
        self.log(message)
        self.show_message(message)
    
    def resource_monitor(self):
        success, message = SystemFunctions.resource_monitor()
        self.log(message)
        self.show_message(message)
    
    def disk_space_analyzer(self):
        success, message = SystemFunctions.disk_space_analyzer()
        self.log(message)
        self.show_message(message)
    
    def device_manager(self):
        success, message = SystemFunctions.device_manager()
        self.log(message)
        self.show_message(message)
    
    def event_viewer(self):
        success, message = SystemFunctions.event_viewer()
        self.log(message)
        self.show_message(message)
    
    def manage_updates(self):
        success, message = SystemFunctions.manage_updates()
        self.log(message)
        self.show_message(message)
    
    def optimize_system(self):
        success, message = SystemFunctions.optimize_system()
        self.log(message)
        self.show_message(message)
    
    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")
        self.statusBar().showMessage(message)
    
    def show_message(self, text):
        QMessageBox.information(self, "Результат", text)

# ==================== ЗАПУСК ПРОГРАММЫ ====================
if __name__ == "__main__":
    run_as_admin()
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Проверка зависимостей
    try:
        import psutil
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"])
    
    try:
        import speedtest
    except ImportError:
        pass  # Не критично
    
    window = HelperProgram()
    window.show()
    sys.exit(app.exec_())