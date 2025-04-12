"""
phonebook_1
===========
Телефонная книга
"""

import sys, io

buffer = io.StringIO()
sys.stdout = sys.stderr = buffer
from tkinter import *

# настройка главного окна
win = Tk()
win.title("Телефонная книга")
win.iconbitmap(
    "C:\\Users\\boris\OneDrive\\Документы\\my_projects\\phonebook\\phonebook.ico"
)
win.geometry("830x450+200+100")

# фото
image_tel = PhotoImage(
    file="C:\\Users\\boris\\OneDrive\\Документы\\my_projects\\phonebook\\phonebook.png"
)
oleg_image = PhotoImage(
    file="C:\\Users\\boris\\OneDrive\\Документы\\my_projects\\phonebook\\oleg.png"
)
tatyana_image = PhotoImage(
    file="C:\\Users\\boris\\OneDrive\\Документы\\my_projects\\phonebook\\tatyana.png"
)
roma_image = PhotoImage(
    file="C:\\Users\\boris\\OneDrive\\Документы\\my_projects\\phonebook\\roma.png"
)
anastasiya_image = PhotoImage(
    file="C:\\Users\\boris\\OneDrive\\Документы\\my_projects\\phonebook\\anastasiya.png"
)
artur_image = PhotoImage(
    file="C:\\Users\\boris\\OneDrive\\Документы\\my_projects\\phonebook\\artur.png"
)
masha_image = PhotoImage(
    file="C:\\Users\\boris\\OneDrive\\Документы\\my_projects\\phonebook\\masha.png"
)
anton_image = PhotoImage(
    file="C:\\Users\\boris\\OneDrive\\Документы\\my_projects\\phonebook\\anton.png"
)
dima_image = PhotoImage(
    file="C:\\Users\\boris\\OneDrive\\Документы\\my_projects\\phonebook\\dima.png"
)
list_images = [
    tatyana_image,
    oleg_image,
    roma_image,
    anastasiya_image,
    artur_image,
    masha_image,
    anton_image,
    dima_image,
]
list_names = [
    "Борисова Татьяна Евгеньевна",
    "Борисов Олег Валентинович",
    "Борисов Роман Олегович",
    "Борисова Анастасия Олеговна",
    "Максумов Артур Тимурович",
    "Евсеева Мария Сергеевна",
    "Евсеев Антон                  ",
    "Евсеев Дмитрий Антонович",
]
list_tel = [
    "тел.:  +7 (964) 771-01-87",
    "тел.:  +7 (916) 126-56-32",
    "тел.:  +7 (966) 342-95-66",
    "тел.:  +7 (905) 571-16-88",
    "тел.:  +7 (901) 381-33-32",
    "тел.:  +7 (901) 384-33-32",
    "тел.:  +7 (985) 953-59-54",
    "тел.:  отсутствует",
]
list_post = [
    "должность: мать, жена",
    "должность: отец, муж",
    "должность: сын, староста",
    "должность: дочь, абитуриент",
    "должность: сын, внук",
    "должность: дочь, мать, жена",
    "должность: сын, отец, муж",
    "должность: сын, внук",
]


def get_info():
    lab_name["text"] = list_names[var.get()]
    lab_post["text"] = list_post[var.get()]
    lab_image["image"] = list_images[var.get()]
    lab_tel["text"] = list_tel[var.get()]


# фрайм для кнопок Checkbutton
frame_but = Frame()
frame_but.pack(side=LEFT)

# переменная радиокнопки
var = IntVar()
var.set(0)

# кнопки Checkbutton
lab_tel_image = Label(frame_but, image=image_tel)
check1 = Radiobutton(
    frame_but,
    activebackground="red",
    activeforeground="white",
    text="Татьяна",
    font=("Arial", 14),
    variable=var,
    value=0,
    indicatoron=0,
    command=get_info,
)
check2 = Radiobutton(
    frame_but,
    activebackground="red",
    activeforeground="white",
    text="Олег",
    font=("Arial", 14),
    variable=var,
    value=1,
    indicatoron=0,
    command=get_info,
)
check3 = Radiobutton(
    frame_but,
    activebackground="red",
    activeforeground="white",
    text="Роман",
    font=("Arial", 14),
    variable=var,
    value=2,
    indicatoron=0,
    command=get_info,
)
check4 = Radiobutton(
    frame_but,
    activebackground="red",
    activeforeground="white",
    text="Анастасия",
    font=("Arial", 14),
    variable=var,
    value=3,
    indicatoron=0,
    command=get_info,
)
check5 = Radiobutton(
    frame_but,
    activebackground="red",
    activeforeground="white",
    text="Артур",
    font=("Arial", 14),
    variable=var,
    value=4,
    indicatoron=0,
    command=get_info,
)
check6 = Radiobutton(
    frame_but,
    activebackground="red",
    activeforeground="white",
    text="Маша",
    font=("Arial", 14),
    variable=var,
    value=5,
    indicatoron=0,
    command=get_info,
)
check7 = Radiobutton(
    frame_but,
    activebackground="red",
    activeforeground="white",
    text="Антон",
    font=("Arial", 14),
    variable=var,
    value=6,
    indicatoron=0,
    command=get_info,
)
check8 = Radiobutton(
    frame_but,
    activebackground="red",
    activeforeground="white",
    text="Дима",
    font=("Arial", 14),
    variable=var,
    value=7,
    indicatoron=0,
    command=get_info,
)
lab_tel_image.pack()
check1.pack(fill="x")
check2.pack(fill="x")
check3.pack(fill="x")
check4.pack(fill="x")
check5.pack(fill="x")
check6.pack(fill="x")
check7.pack(fill="x")
check8.pack(fill="x")

# фрэйм для вывода информации
frame_info = Frame()
frame_info.pack(side=LEFT)
lab_tel = Label(
    frame_info,
    anchor=W,
    text=list_tel[var.get()],
    font=("Comic Sans", 16, "bold"),
    fg="blue",
)
lab_name = Label(
    frame_info, text=list_names[var.get()], font=("Comic Sans", 18, "bold")
)
lab_image = Label(frame_info, image=list_images[var.get()])
lab_post = Label(
    frame_info, anchor=W, text=list_post[var.get()], font=("Comic Sans", 16, "bold")
)
lab_image.pack(side=LEFT)
lab_name.pack()
lab_post.pack(fill="both")
lab_tel.pack(fill="both")
win.mainloop()
