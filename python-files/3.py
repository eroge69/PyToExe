import tkinter as tk
import requests
import threading
import time

# Общая функция для отправки HTTP-запроса
def send_command(url):
    try:
        response = requests.get(url)
        print(f"Отправлено: {url}, Статус: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при отправке запроса: {url} | {e}")

# Команда для кнопки "Влево"
def send_left_commands():
    send_command("http://admin:admin@192.168.50.50/protect/rb0n.cgi")
    time.sleep(0.2)
    send_command("http://admin:admin@192.168.50.50/protect/rb0f.cgi")

# Команда для кнопок "Вверх" и "Вниз"
def send_up():
    send_command("http://admin:admin@192.168.50.50/protect/rb2n.cgi",)
    time.sleep(0.2)
    send_command("http://admin:admin@192.168.50.50/protect/rb2f.cgi",)

def send_down():
    send_command("http://admin:admin@192.168.50.50/protect/rb3n.cgi",)
    time.sleep(0.2)
    send_command("http://admin:admin@192.168.50.50/protect/rb3f.cgi",)


# Команда для кнопки "Вправо" (заглушка)
def send_right():
    send_command("http://admin:admin@192.168.50.50/protect/rb1n.cgi")
    time.sleep(0.2)
    send_command("http://admin:admin@192.168.50.50/protect/rb1f.cgi")

# Создание окна
root = tk.Tk()
root.title("ПАМИР КРАСАВА")
root.geometry("300x120")

# Кнопки, расположенные в виде креста
btn_left = tk.Button(root, text="⬅ Влево", width=10, command=lambda: threading.Thread(target=send_left_commands).start())
btn_up = tk.Button(root, text="⬆ Вверх", width=10, command=send_up)
btn_right = tk.Button(root, text="Вправо ➡", width=10, command=send_right)
btn_down = tk.Button(root, text="⬇ Вниз", width=10, command=send_down)

# Размещение кнопок с помощью grid
btn_up.grid(row=0, column=1, pady=10)
btn_left.grid(row=1, column=0, padx=10)
btn_right.grid(row=1, column=2, padx=10)
btn_down.grid(row=2, column=1, pady=10)

# Запуск главного цикла
root.mainloop()
