import subprocess
from tkinter import messagebox
import tkinter


def run_module(filename):
    try:
        subprocess.Popen(["python", filename])
    except Exception as e:
        messagebox.showwarning("Помилка", f"Не вдалося запустити {filename}\n\n{e}")


buttons = [
    ("Обстріли", "Obstrily.py"),
    ("Робота по ворогу", "Vognevi.py"),
    ("Звіт по БПЛА 218", "BPLA.py"),
    ("Звіт по БПЛА 2сб", "BPLApryd.py"),    
    ("Доповіді", "Dopovidi.py"),
    ("Менеджер БД", "manager.py")
]

window_main = tkinter.Tk()
window_main.title('Frontline')

# Створення фрейму для меню
frame_main = tkinter.Frame(window_main)
frame_main.pack(side=tkinter.TOP, fill=tkinter.X, pady=20)

# Додавання кнопок до меню горизонтально
for text, file in buttons:
    button_menu = tkinter.Button(frame_main, text=text, width=15, command=lambda f=file: run_module(f))
    button_menu.pack(side=tkinter.LEFT, padx=15)

# Кнопка "Вихід" - чомусь не працює
#exit_button = tkinter.Button(window_main, text="Вихід", width=77, command=window_main.quit)
#exit_button.pack(pady=20)

window_main.mainloop()
