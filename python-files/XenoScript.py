
import tkinter as tk
import threading

def create_window(i):
    window = tk.Tk()
    window.title(f"Error {i}")
    window.geometry(f"200x100+{100 + i * 30}+{100 + i * 30}")

    # Убираем рамку окна (нет крестика, минуса, квадрата)
    window.overrideredirect(True)

    label = tk.Label(window, text=f"Error404 😈")
    label.pack(expand=True)

    # Блокируем клавиши вроде Alt+F4, Esc и т.п.
    window.bind("<Alt-F4>", lambda e: "break")
    window.bind("<Escape>", lambda e: "break")
    window.bind("<Control-w>", lambda e: "break")

    # Просто запускаем окно
    window.mainloop()

if __name__ == "__main__":
    num_windows = 1000  # Сколько окон появится
    threads = []
    for i in range(num_windows):
        t = threading.Thread(target=create_window, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
