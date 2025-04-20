import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from PIL import Image, ImageTk
# Глобальная переменная для хранения ссылки на новое окно
new_window = None
new_window2 = None
new_window3 = None
def load_image(izobrazhenie):
    try:
        image = Image.open(izobrazhenie)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return None
    
def okno_grammatika():
    global new_window
    # Проверяем, открыто ли новое окно
    if new_window is None or not new_window.winfo_exists():
        new_window = Toplevel()  # Используем Toplevel вместо Tk для вторичного окна
        new_window.title("Grammar tasks окно")
        new_window.geometry("1100x800")
        
        img = load_image("времена.png")
        if img:
            img_label = tk.Label(new_window, image=img)
            img_label.image = img  # Сохраняем ссылку на изображение, чтобы оно не удалялось сборщиком мусора
            img_label.pack()
            
        close_button = tk.Button(new_window, text="Назад", command=lambda: new_window.destroy())
        close_button.pack(anchor="sw", expand=1)
        

def okno_leksika():
    global new_window
    # Проверяем, открыто ли новое окно
    if new_window is None or not new_window.winfo_exists():
        new_window = Toplevel()  # Используем Toplevel вместо Tk для вторичного окна
        new_window.title("New words окно")
        new_window.geometry("550x500")
        
        words_button = tk.Button(new_window, text="Полезная лексика по теме Аппаратное обеспечение", command=SLOVAR)
        words_button.pack(anchor=CENTER, expand=1)
        
        words_button2 = tk.Button(new_window, text="Полезная лексика по теме Программное обеспечение", command=SLOVAR2)
        words_button2.pack(anchor=CENTER, expand=1)
        
        words_button3 = tk.Button(new_window, text="Полезная лексика по теме Интернет", command=SLOVAR3)
        words_button3.pack(anchor=CENTER, expand=1)
        
        close_button = tk.Button(new_window, text="Назад", command=lambda: new_window.destroy())
        close_button.pack(anchor="sw", expand=1)      

def okno_zadachi():
    global new_window
    # Проверяем, открыто ли новое окно
    if new_window is None or not new_window.winfo_exists():
        new_window = Toplevel()  # Используем Toplevel вместо Tk для вторичного окна
        new_window.title("Exercises окно")
        new_window.geometry("550x500")
        
        tests_button = tk.Button(new_window, text="Тестовые упражнения", command=TESTY)
        tests_button.pack(anchor=CENTER, expand=1)
        
        tests_button2 = tk.Button(new_window, text="Упражнения на чтение", command= CHTENYE)
        tests_button2.pack(anchor=CENTER, expand=1)
        
        close_button = tk.Button(new_window, text="Назад", command=lambda: new_window.destroy())
        close_button.pack(anchor="sw", expand=1)  
        
def okno_progress():
    global new_window
    # Проверяем, открыто ли новое окно
    if new_window is None or not new_window.winfo_exists():
        new_window = Toplevel()  # Используем Toplevel вместо Tk для вторичного окна
        new_window.title("Progress окно")
        new_window.geometry("550x500")
        
        label = tk.Label(new_window, text="Progress окно")
        label.pack(anchor=CENTER, expand=1)
        
        close_button = tk.Button(new_window, text="Назад", command=lambda: new_window.destroy())
        close_button.pack(anchor="sw", expand=1)
def TESTY():
    global new_window2
    # Проверяем, открыто ли новое окно
    if new_window2 is None or not new_window2.winfo_exists():
        new_window2 = Toplevel()  # Используем Toplevel вместо Tk для вторичного окна
        new_window2.title("tests")
        new_window2.geometry("700x700")
        
        img = load_image("test1.png")
        if img:
            img_label = tk.Label(new_window2, image=img)
            img_label.image = img  # Сохраняем ссылку на изображение, чтобы оно не удалялось сборщиком мусора
            img_label.pack()
        img2 = load_image("test2.png")
        if img2:
            img2_label = tk.Label(new_window2, image=img2)
            img2_label.image = img2  # Сохраняем ссылку на изображение, чтобы оно не удалялось сборщиком мусора
            img2_label.pack()
            
        close_button = tk.Button(new_window2, text="Назад", command=lambda: new_window2.destroy())
        close_button.pack(anchor="sw", expand=1)
        
def CHTENYE():
    global new_window2
    # Проверяем, открыто ли новое окно
    if new_window2 is None or not new_window2.winfo_exists():
        new_window2 = Toplevel()  # Используем Toplevel вместо Tk для вторичного окна
        new_window2.title("texts")
        new_window2.geometry("1100x900")
        
        img = load_image("Text1.png")
        if img:
            img_label = tk.Label(new_window2, image=img)
            img_label.image = img  # Сохраняем ссылку на изображение, чтобы оно не удалялось сборщиком мусора
            img_label.pack()
            
        close_button = tk.Button(new_window2, text="Назад", command=lambda: new_window2.destroy())
        close_button.pack(anchor="sw", expand=1)
        
def SLOVAR():
    global new_window3
    # Проверяем, открыто ли новое окно
    if new_window3 is None or not new_window3.winfo_exists():
        new_window3 = Toplevel()  # Используем Toplevel вместо Tk для вторичного окна
        new_window3.title("slova")
        new_window3.geometry("1100x800")
        
        img = load_image("Аппаратное обеспечение1.png")
        if img:
            img_label = tk.Label(new_window3, image=img)
            img_label.image = img  # Сохраняем ссылку на изображение, чтобы оно не удалялось сборщиком мусора
            img_label.pack(anchor="center")
            
        close_button = tk.Button(new_window3, text="Назад", command=lambda: new_window3.destroy())
        close_button.pack(anchor="sw", expand=1)
        
def SLOVAR2():
    global new_window3
    # Проверяем, открыто ли новое окно
    if new_window3 is None or not new_window3.winfo_exists():
        new_window3 = Toplevel()  # Используем Toplevel вместо Tk для вторичного окна
        new_window3.title("slova")
        new_window3.geometry("1100x900")
        
        img = load_image("Программное обеспечение1.png")
        if img:
            img_label = tk.Label(new_window3, image=img)
            img_label.image = img  # Сохраняем ссылку на изображение, чтобы оно не удалялось сборщиком мусора
            img_label.pack(anchor="center")
            
        close_button = tk.Button(new_window3, text="Назад", command=lambda: new_window3.destroy())
        close_button.pack(anchor="sw", expand=1)

def SLOVAR3():
    global new_window3
    # Проверяем, открыто ли новое окно
    if new_window3 is None or not new_window3.winfo_exists():
        new_window3 = Toplevel()  # Используем Toplevel вместо Tk для вторичного окна
        new_window3.title("slova")
        new_window3.geometry("1100x900")
        
        img = load_image("Интернет.png")
        if img:
            img_label = tk.Label(new_window3, image=img)
            img_label.image = img  # Сохраняем ссылку на изображение, чтобы оно не удалялось сборщиком мусора
            img_label.pack(anchor="center")
            
        close_button = tk.Button(new_window3, text="Назад", command=lambda: new_window3.destroy())
        close_button.pack(anchor="sw", expand=1)
               
# Закрываем новое окно при закрытии главного окна
def on_closing():
    if new_window:
        new_window.destroy()  # Закрываем новое окно, если оно открыто
    root.destroy()

root = Tk()
root.title("первое окно/меню")
root.geometry("2000x1100")
root.configure(bg="#d1ddde")  # Фон окна

# Создаем кнопки
o_b1 = tk.Button(text="Грамматика", background="orange", foreground="#fff", padx="500", pady="70", font="16", command=okno_grammatika)
o_b1.pack(anchor="center", expand=1)
o_b2 = tk.Button(text="Лексика", background="green", foreground="#fff", padx="500", pady="70", font="16", command=okno_leksika)
o_b2.pack(anchor="center", expand=1)
o_b3 = tk.Button(text="Задачи", background="purple", foreground="#fff", padx="500", pady="70", font="16", command=okno_zadachi)
o_b3.pack(anchor="center", expand=1)
o_b4 = tk.Button(text="Прогресс", background="blue", foreground="#fff", padx="500", pady="70", font="16", command=okno_progress)
o_b4.pack(anchor="center", expand=1)

# Привязка функции к событию закрытия окна
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

