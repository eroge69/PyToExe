from tkinter import *
from tkinter import messagebox
import math

def clicked():
    POL_R = float(POL.get()) 
    TG_R = float(TG.get())
    FNO_R = float(FNO.get())
    NT_R = float(NT.get())
    LMR_R = float(LMR.get())    
    FIO_R = str(FIO.get())
    VOZRAST_R = str(VOZRAST.get())
    CHISLO_R = str(CHISLO.get())
          
    D = (1.324 * POL_R + 0.468 * TG_R + 0.625 * FNO_R
         + 0.004 * NT_R + 0.101 * LMR_R - 5.312)
    D1 = math.exp(-1 * D)  
    REZ = 1 / (1 + D1)
    REZ = round(REZ, 3)
    
    if REZ > 0.5:
        REZS = 'НЕБЛАГОПРИЯТНЫЙ'
    else:
        REZS = 'БЛАГОПРИЯТНЫЙ'
    

    REZ_R = str(REZ)
    with open('result ishod IBS.txt','a') as file:
        file.write(FIO_R + ', возраст: ' + VOZRAST_R
                   + ', дата обследования: ' + CHISLO_R
                   + ', вероятность = ' + REZ_R
                   + '; ИСХОД: ' + REZS +'\n')

    messagebox.showinfo('ИСХОД              ', REZS)
    
window = Tk()
window.title("ПРОГРАММА УХУДШЕНИЯ ИБС ПОСЛЕ КОВИД")
window.geometry('400x250') 

frame = Frame(window, padx=10, pady=10)
frame.pack(expand=True)

FIO = Label(frame, text="ФИО / НИК  ")
FIO.grid(row=1, column=1)

FIO = Entry(frame)
FIO.grid(row=1, column=2)

VOZRAST = Label(frame, text="Возраст, лет  ")
VOZRAST.grid(row=2, column=1)

VOZRAST = Entry(frame)
VOZRAST.grid(row=2, column=2)

CHISLO = Label(frame, text="Дата обследования  ")
CHISLO.grid(row=3, column=1)

CHISLO = Entry(frame)
CHISLO.grid(row=3, column=2)

POL = Label(frame, text="Пол  ")
POL.grid(row=4, column=1)

POL = Entry(frame)
POL.grid(row=4, column=2)

ZAG2 = Label(frame, text="БИОХИМИЧЕСКИЙ АНАЛИЗ КРОВИ:  ")
ZAG2.grid(row=5, column=1)

TG = Label(frame, text="Триглицериды, ммоль/л  ")
TG.grid(row=6, column=1)

TG = Entry(frame)
TG.grid(row=6, column=2)

FNO = Label(frame, text="ФНО-α, пг/мл  ")
FNO.grid(row=7, column=1)

FNO = Entry(frame)
FNO.grid(row=7, column=2)

NT = Label(frame, text="NTproBNP, пг/мл  ")
NT.grid(row=8, column=1)

NT = Entry(frame)
NT.grid(row=8, column=2)

LMR = Label(frame, text="LMR, ед  ")
LMR.grid(row=9, column=1)

LMR = Entry(frame)
LMR.grid(row=9, column=2)

btn = Button(frame, text="РАССЧИТАТЬ", command=clicked)
btn.grid(column=2, row=10)

btn = Button(frame, text='ВЫХОД', command=window.destroy)
btn.grid(column=2, row=11)

window.mainloop()
