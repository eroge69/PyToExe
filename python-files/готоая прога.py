from tkinter import *
from  tkinter import ttk
import tkinter as tk
root = Tk()
root.title('Шифрование')
root.geometry('1200x400')
root.configure(bg='#76FF7B')

def perevod():
 a=entry.get().upper()
 key=3
 alfavit ='АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
 itog = ''
 for i in a:
     mesto = alfavit.find(i)
     if combobox.current()   == 1:
         new_mesto = mesto - key
         if i in alfavit:
             itog += alfavit[new_mesto]
         else:
             itog += i
     else:
         new_mesto = mesto + key
         
         if i in alfavit:
             itog += alfavit[new_mesto]
         else:
             itog += i

 lbl['text'] = ('Ответ:') 
 lbl ['text'] = lbl ['text'] + itog

def zifr(event):
        zifr=combobox.current()
def delete1():
        entry.delete(0, 'end')
lbl = ttk.Label(root, text='Перевод в шифр',background="#76FF7B", font='Arial 25')
lbl.pack()
lbl = ttk.Label(root, text='Введите текст',background="#76FF7B", font='Arial 20')
lbl.pack()
entry=ttk.Entry(root,text = '',font = 'Arial 25', width=60)
entry.pack()
languages = ["Шифровать", "Дешифровать"]
combobox = ttk.Combobox(values=languages,width=15, state="readonly")
combobox.pack(anchor=NW, padx=5, pady=5)
combobox.bind("<<ComboboxSelected>>", zifr)
combobox.current(0)
btn = ttk.Button(root, text='Выполнить',command=perevod)
btn.pack()
lbl = ttk.Label(root, text='Ответ: ',background="#76FF7B", font='Arial 25')
lbl.pack()
btn = ttk.Button(root, text='Очистить', command=delete1)
btn.pack()






