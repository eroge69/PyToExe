from tkinter import *
from tkinter import messagebox
import math

def clicked():
    POL_R = float(POL.get()) 
    GB_R = float(GB.get())
    IL_R = float(IL.get())
    SII_R = float(SII.get())
    LMR_R = float(LMR.get())
    FIZ_R = float(FIZ.get())
    FIO_R = str(FIO.get())
    VOZRAST_R = float(VOZRAST.get())
    CHISLO_R = str(CHISLO.get())
          
    D = (1.355 * POL_R + 2.519 * GB_R + 0.254 * IL_R
         + 0.003 * SII_R + 0.489 * LMR_R - 0.101 * FIZ_R
         + 0.131 * VOZRAST_R - 10.966)
    D1 = math.exp(-1 * D)  
    REZ = 1 / (1 + D1)
    REZ = round(REZ, 3)
    
    if REZ > 0.5:
        REZS = 'ПРОГНОЗ ДЕБЮТ ИБС'
    else:
        REZS = 'БЛАГОПРИЯТНЫЙ'
    
    VOZRAST_R = str(VOZRAST_R) 
    REZ_R = str(REZ)
    with open('result debut IBS.txt','a') as file:
        file.write(FIO_R + ', возраст: ' + VOZRAST_R
                   + ', дата обследования: ' + CHISLO_R
                   + ', вероятность = ' + REZ_R
                   + '; ИСХОД: ' + REZS +'\n')

    messagebox.showinfo('ИСХОД              ', REZS)
    
window = Tk()
window.title("ПРОГРАММА ДЕБЮТ ИБС ПОСЛЕ КОВИД")
window.geometry('400x300') 

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

GB = Label(frame, text="СТАДИЯ ГИЕРТОНИЧЕСКОЙ БОЛЕЗНИ  ")
GB.grid(row=5, column=1)

GB = Entry(frame)
GB.grid(row=5, column=2)

ZAG2 = Label(frame, text="БИОХИМИЧЕСКИЙ АНАЛИЗ КРОВИ:  ")
ZAG2.grid(row=6, column=1)

IL = Label(frame, text="ИЛ-6  ")
IL.grid(row=7, column=1)

IL = Entry(frame)
IL.grid(row=7, column=2)

SII = Label(frame, text="SII  ")
SII.grid(row=8, column=1)

SII = Entry(frame)
SII.grid(row=8, column=2)

LMR = Label(frame, text="LMR, ед  ")
LMR.grid(row=9, column=1)

LMR = Entry(frame)
LMR.grid(row=9, column=2)

ZAG2 = Label(frame, text="ОПРОСНИК SF-36:  ")
ZAG2.grid(row=10, column=1)

FIZ = Label(frame, text="cубшкала физкомпонент  ")
FIZ.grid(row=11, column=1)

FIZ = Entry(frame)
FIZ.grid(row=11, column=2)

btn = Button(frame, text="РАССЧИТАТЬ", command=clicked)
btn.grid(column=2, row=12)

btn = Button(frame, text='ВЫХОД', command=window.destroy)
btn.grid(column=2, row=13)

window.mainloop()
