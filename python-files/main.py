
import os
import platform
import datetime
import time
import getpass
import json
import mysql.connector

# Путь к системной папке конфигурации
config_dir = os.path.expanduser("~/.riseos")
config_file = os.path.join(config_dir, "settings.json")

# Настройки по умолчанию
default_settings = {
    "animations": True,
    "show_welcome_tip": True,
    "show_motivation": True,
    "riseos_version": "1.0.1"
}

# Загрузка и сохранение настроек
def load_settings():
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    if not os.path.exists(config_file):
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=4, ensure_ascii=False)
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings():
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

settings = load_settings()

def animate_text(text, delay=0.03):
    if settings.get("animations", True):
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
    else:
        print(text)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def riseos_boot_animation():
    clear_screen()
    logo = [
        "▄▄▄▄▄▄▄  ▄▄                    ▄▄▄▄▄▄   ▄▄▄▄▄▄",
        "██▀▀▀▀██ ▀▀                   ██▀▀▀▀██ ██▀▀▀▀██",
        "██    ██ ██  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄  ██    ██ ██",
        "███████  ██ ██▀▀▀▀▀▀ ██▀▀▀▀██ ██    ██  ██████",
        "██    ██ ██  ██████  ████████ ██    ██       ██",
        "██    ██ ██ ▄▄▄▄▄▄██ ██▄▄▄▄▄▄ ██▄▄▄▄██ ██▄▄▄▄██",
        "▀▀    ▀▀ ▀▀ ▀▀▀▀▀▀▀   ▀▀▀▀▀▀▀  ▀▀▀▀▀▀   ▀▀▀▀▀▀"

    ]
    for line in logo:
        animate_text(line.lower(), delay=0.01)
    print()
    animate_text("RiseOS успешно загружена!")
    if settings.get("show_welcome_tip", True):
        animate_text("Введите 'help', чтобы отобразить все команды.\n")

def check_for_updates():
    animate_text('Подключение к серверу...')
    try:
        connection = mysql.connector.connect(
            host="sql7.freesqldatabase.com",  # <-- УКАЖИ СЮДА ХОСТ
            user="sql7777664",  # <-- УКАЖИ СЮДА ПОЛЬЗОВАТЕЛЯ
            password="wh6znQ16Z7",  # <-- УКАЖИ СЮДА ПАРОЛЬ
            database="sql7777664"  # <-- УКАЖИ СЮДА НАЗВАНИЕ БД
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM riseos_updates ORDER BY id DESC LIMIT 1")
        latest = cursor.fetchone()
        if latest and latest["version"] != settings.get("riseos_version"):
            animate_text(f"Доступно обновление RiseOS: {latest['version']}")
            animate_text(f"Что нового: {latest['changelog']}")
        else:
            animate_text("У вас последняя версия RiseOS.")
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        animate_text(f"[Ошибка подключения к базе]: {err}")

def show_help():
    animate_text("Список доступных команд:")
    animate_text(" - help: Показать все команды")
    animate_text(" - settings: Настройки RiseOS")
    animate_text(" - reset: Очистка экрана")
    animate_text(" - pyver: Версия Python")
    animate_text(" - rsver: Версия RiseOS")
    animate_text(" - check: Проверить наличие более новой версии")
    animate_text(" - date: Сегодняшняя дата")
    animate_text(" - clock: Текущее время")
    animate_text(" - authors: Авторы RiseOS")
    animate_text(" - exit: Выход")

def open_settings():
    while True:
        animate_text("\nНастройки RiseOS:")
        animate_text(" 1. Переключить анимации (вкл/выкл)")
        animate_text(" 2. Показывать подсказку при запуске")
        animate_text(" 3. Показывать мотивацию при запуске")
        animate_text(" 4. Назад\n")
        choice = input("Выберите опцию (1-4): ").strip()
        if choice == "1":
            settings["animations"] = not settings["animations"]
            animate_text(f"Анимации теперь {'включены' if settings['animations'] else 'отключены'}")
        elif choice == "2":
            settings["show_welcome_tip"] = not settings["show_welcome_tip"]
            animate_text(f"Подсказки теперь {'включены' if settings['show_welcome_tip'] else 'отключены'}")
        elif choice == "3":
            settings["show_motivation"] = not settings["show_motivation"]
            animate_text(f"Мотивация теперь {'включена' if settings['show_motivation'] else 'отключена'}")
        elif choice == "4":
            save_settings()
            break
        else:
            animate_text("Неверный выбор!")

def show_pyver():
    animate_text(f"Версия Python: {platform.python_version()}")

def show_rsver():
    animate_text(f"Версия RiseOS: {settings.get('riseos_version', 'неизвестно')}")

def show_date():
    now = datetime.datetime.now()
    animate_text(f"Дата: {now.strftime('%Y-%m-%d')}")

def show_clock():
    now = datetime.datetime.now()
    animate_text(f"Время: {now.strftime('%H:%M:%S')}")

def show_authors():
    animate_text("Авторы RiseOS:")
    animate_text(" - shfhtz (Дизайн, код, функции, сервер)")
    animate_text(" - MA5K5 (Идеи, )")

def show_motivation():
    if settings.get("show_motivation", True):
        user = getpass.getuser()
        animate_text(f"Добро пожаловать, {user}! Помни: брат брату не тот брат который за брата брат, а тот кто за братскую братву на не братскую не променяет")

def main():
    riseos_boot_animation()
    show_motivation()
    animate_text('Не забудьте проверить наличие обновлений!и т')
    while True:
        command = input("RiseOS> ").strip().lower()
        if command == "help":
            show_help()
        elif command == "settings":
            open_settings()
        elif command == "reset":
            clear_screen()
        elif command == "pyver":
            show_pyver()
        elif command == "rsver":
            show_rsver()
        elif command == "check":
            check_for_updates()
        elif command == "date":
            show_date()
        elif command == "clock":
            show_clock()
        elif command == "authors":
            show_authors()
        elif command == "exit":
            animate_text("Выход из RiseOS...")
            break
        else:
            animate_text("Неизвестная команда. Введите 'help' для списка.")

if __name__ == "__main__":
    main()
