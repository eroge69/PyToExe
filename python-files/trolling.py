
import pyautogui
import time

def main():
    try:
        with open("input.txt", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Файл input.txt не найден")
        return

    print("Запуск через 3 секунды... Перейди в Telegram и поставь курсор в поле ввода.")
    time.sleep(3)

    indent = 0
    for line in lines:
        message = " " * indent + line
        pyautogui.write(message, interval=0.005)
        pyautogui.press("enter")
        indent += 2
        time.sleep(0.01)

if __name__ == "__main__":
    main()
