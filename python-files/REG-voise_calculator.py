import speech_recognition as sr

from tkinter import *
from tkinter import ttk
import pyautogui
import pyperclip

import re

from inspect import getsourcefile
from os.path import abspath
path=abspath(getsourcefile(lambda:0))
i=-1
for i in range(len(path)):
    if path[0-i]=="\\":
        last=-i
        break
path=path[:last]

window=Tk()
window.geometry('450x300')
window.title('REG голосовой калькулятор')
window.resizable(False, False)

window.iconbitmap(default=str(path)+"\REG.ico")








lbl=Label(window, text="Последний вывод:",font=("Arial Bold", 12))
lbl.place(x=7, y=80)

def copy():
    pyperclip.copy(txt)

button_copy = ttk.Button(window,text='Копировать',width=18, command=copy)
button_copy.place(x=7, y=140)
txt=""
lbl_text = Label(window, text=txt)
lbl_text.place(x=7, y=110)











r=sr.Recognizer()

def past(txt):
    for w in range(len(txt)):
        #конвертируем запятые в точки для программы (1,2 -> 1.2)
        if txt[w]==",":
            txt=txt[:w]+'.'+txt[(w+1):]
        if txt[w]=="/" or txt[w]=="х" or txt[w]=="+" or txt[w]=="-":
            #назначаем индекс математического знака знака
            s=w
            #a - цифра до запятой
            #b - цифра после запятой
            a=float(txt[:(w-1)])
            b=str(txt[(w+2):])
            #повторяем процесс 1,2 -> 1.2 для второго числа
            for v in range(len(b)):
                if b[v]==",":
                    b=b[:v]+'.'+b[(v+1):]
            b=float(b)
    print(a)
    print(b)
    if txt[s]=="+":
        res=a+b
    if txt[s]=="-":
        res=a-b
    if txt[s]=="х":
        res=a*b
    if txt[s]=="/":
        res=a/b

    if str(res)[-1]=="0" and str(res)[-2]==".":
        res=str(res)[:-2]
    print(res)
    pyautogui.typewrite(str(res))

def speech():
    global txt, window
    err=False
    # Создаем объект Recognizer
    recognizer = sr.Recognizer()

    # Получаем звуковой сигнал с микрофона
    with sr.Microphone() as source:
        print("Скажите что-нибудь:")
        audio_data = recognizer.listen(source)

        try:
            # Распознаем текст из аудио
            sp = recognizer.recognize_google(audio_data, language='ru-RU')
            print("Вы сказали: " + sp)
            if re.search(r'[абвгдеёжзиклмнопрстуфцчшщэюя]', sp)!=None or re.search(r'[\+\-\х\/]', sp)==None:
                speech()
            txt=str(sp)
            lbl_text.configure(text=txt)
            err=True
            if err:
                past(txt)
            speech()
        except sr.UnknownValueError:
            err=False
            speech()
        except sr.RequestError as e:
            print("Ошибка сервиса распознавания речи; {0}".format(e))
            err=False
            speech()
    speech()





def com(event):
    if event.keysym=="r" or event.keysym=="к":
        speech()

window.bind("<Key>", com)

button_reg=ttk.Button(window,text='Слушай, Рэг!',width=18, command=speech)
button_reg.place(x=7, y=23)














window.mainloop()