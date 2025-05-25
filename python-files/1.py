import subprocess
import time
import schedule

# Читаем настройки из файла
def read_settings():
    try:
        with open("settings.txt", "r") as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
            time1, path1 = lines[0].split("=")
            time2, path2 = lines[1].split("=")
            return time1.strip(), path1.strip(), time2.strip(), path2.strip()
    except FileNotFoundError:
        print("Файл settings.txt не найден. Использую стандартные значения.")
        return "12:30", "C:\\путь\\к\\файлу1.bat", "12:50", "C:\\путь\\к\\файлу2.bat"

# Функции запуска бат-файлов
def run_file1():
    subprocess.run([path1])

def run_file2():
    subprocess.run([path2])

# Читаем настройки
time1, path1, time2, path2 = read_settings()

# Запуск по расписанию
schedule.every().day.at(time1).do(run_file1)
schedule.every().day.at(time2).do(run_file2)

while True:
    schedule.run_pending()
    time.sleep(1)