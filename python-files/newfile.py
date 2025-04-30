import tkinter as tk
from plyer import notification
import threading
import time

running = False

def show_notification():
    notification.notify(
        title="Нагадування",
        message="Минає година!",
        timeout=10
    )

def start_notifications():
    global running
    running = True

    def notify_loop():
        while running:
            show_notification()
            for _ in range(3600):  # чекати 1 годину, перевіряючи щосекунди, чи не натиснули "Стоп"
                if not running:
                    break
                time.sleep(1)

    thread = threading.Thread(target=notify_loop)
    thread.daemon = True
    thread.start()

def stop_notifications():
    global running
    running = False

# GUI
root = tk.Tk()
root.title("Щогодинне сповіщення")

start_btn = tk.Button(root, text="Старт", command=start_notifications, width=20)
start_btn.pack(pady=10)

stop_btn = tk.Button(root, text="Стоп", command=stop_notifications, width=20)
stop_btn.pack(pady=10)

root.mainloop()