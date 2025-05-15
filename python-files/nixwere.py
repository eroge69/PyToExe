import tkinter as tk
import random
import os
import subprocess
import threading
import time

def check_password():
    if entry.get() == "123":
        root.destroy()
        os._exit(0)  # Полное завершение процесса
    else:
        show_error()
        entry.delete(0, tk.END)

def show_error():
    error_frame = tk.Frame(root, bg="#ff5555", bd=0)
    error_frame.place(relx=0.5, rely=0.3, anchor="center", width=300, height=80)
    
    error_label = tk.Label(error_frame, text="Неверный пароль!", font=("Helvetica", 16, "bold"), 
                          fg="white", bg="#ff5555")
    error_label.pack(pady=15)
    
    def fade_out(alpha=1.0):
        if alpha > 0:
            alpha -= 0.05
            error_frame.configure(bg=f"#ff5555{int(alpha*255):02x}")
            error_label.configure(bg=f"#ff5555{int(alpha*255):02x}")
            root.after(50, fade_out, alpha)
        else:
            error_frame.destroy()
    
    root.after(1000, fade_out)

def prevent_close():
    pass

def on_entry_click(event):
    if entry.get() == "Введите пароль...":
        entry.delete(0, tk.END)
        entry.config(fg="white")

def on_focusout(event):
    if entry.get() == "":
        entry.insert(0, "Введите пароль...")
        entry.config(fg="grey")

def button_hover(event):
    button.config(bg="#ff5555")

def button_leave(event):
    button.config(bg="#ff3333")

def update_stars():
    canvas.delete("star")
    for star in stars:
        star[0] += star[2]
        star[1] += star[3]
        if star[0] < 0 or star[0] > root.winfo_screenwidth() or star[1] < 0 or star[1] > root.winfo_screenheight():
            star[0] = random.randint(0, root.winfo_screenwidth())
            star[1] = random.randint(0, root.winfo_screenheight())
            star[2] = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
            star[3] = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
        canvas.create_oval(star[0], star[1], star[0] + 2, star[1] + 2, fill="white", outline="white", tags="star")
    root.after(50, update_stars)

def monitor_process():
    while True:
        time.sleep(1)
        if not root.winfo_exists():  # Если окно закрыто
            subprocess.Popen(["python", __file__])  # Перезапуск скрипта
            os._exit(0)

root = tk.Tk()
root.attributes('-fullscreen', True)
root.protocol("WM_DELETE_WINDOW", prevent_close)
root.configure(bg="#1e1e2e")

# Запуск мониторинга процесса в отдельном потоке
threading.Thread(target=monitor_process, daemon=True).start()

# Фон с звездами
canvas = tk.Canvas(root, bg="#1e1e2e", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Создание звезд
stars = []
for _ in range(50):
    x = random.randint(0, root.winfo_screenwidth())
    y = random.randint(0, root.winfo_screenheight())
    dx = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
    dy = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
    stars.append([x, y, dx, dy])

update_stars()

# Контейнер для интерфейса
frame = tk.Frame(canvas, bg="#1e1e2e")
frame.place(relx=0.5, rely=0.5, anchor="center")

# Заголовок
label = tk.Label(frame, text="Введите пароль", font=("Helvetica", 28, "bold"), fg="#ffffff", bg="#1e1e2e")
label.pack(pady=20)

# Поле ввода
entry = tk.Entry(frame, show="*", font=("Helvetica", 20), fg="grey", bg="#2e2e3e", 
                 insertbackground="white", relief="flat", width=20, justify="center")
entry.insert(0, "Введите пароль...")
entry.bind("<FocusIn>", on_entry_click)
entry.bind("<FocusOut>", on_focusout)
entry.pack(pady=20, padx=20)

# Кнопка
button = tk.Button(frame, text="Разблокировать", font=("Helvetica", 18, "bold"), fg="white", 
                   bg="#ff3333", relief="flat", command=check_password)
button.pack(pady=20)
button.bind("<Enter>", button_hover)
button.bind("<Leave>", button_leave)

# Тень для поля ввода
entry.config(highlightthickness=2, highlightbackground="#3e3e4e", highlightcolor="#3e3e4e")

root.mainloop()