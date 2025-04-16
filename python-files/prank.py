import time
import webbrowser
import tkinter as tk
import random
import sys

def prank_windows():
    def spawn_window():
        window = tk.Tk()
        window.title("Привет!")
        window.geometry(f"200x100+{random.randint(0, 1000)}+{random.randint(0, 800)}")
        label = tk.Label(window, text="Улыбнись!")
        label.pack()
        window.after(1000, spawn_window)
        window.mainloop()

    spawn_window()

def rickroll():
    urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Рикролл
        "https://i.imgur.com/w3duR07.png",              # Мем
    ]
    for url in urls:
        webbrowser.open(url)
        time.sleep(1)

def fake_console_spam():
    print("У тебя 5 секунд, чтобы успеть закрыть это окно!")
    time.sleep(5)
    for _ in range(30):
        print("СИСТЕМА: Обнаружен вирус... ШУТКА!")

def show_menu():
    print("""
    ==== Шуточный вирус ====
    1. Спавн окон "Улыбнись!"
    2. Рикролл в браузере
    3. Спам в консоли
    4. Выход
    """)
    choice = input("Выбери шалость (1-4): ")

    if choice == '1':
        prank_windows()
    elif choice == '2':
        rickroll()
    elif choice == '3':
        fake_console_spam()
    elif choice == '4':
        sys.exit()
    else:
        print("Неверный выбор.")
        show_menu()

if __name__ == "main":
    show_menu()