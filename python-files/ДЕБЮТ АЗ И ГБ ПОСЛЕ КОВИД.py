from tkinter import *
from tkinter import messagebox
import math

def clicked():
    POL_R = float(POL.get()) 
    NT_R = float(NT.get())
    LP_R = float(LP.get())    
    FIO_R = str(FIO.get())
    VOZRAST_R = float(VOZRAST.get())
    CHISLO_R = str(CHISLO.get())
          
    D = (0.294 * VOZRAST_R + 1.436 * LP_R + 0.064 * NT_R - 14.699)
    D1 = math.exp(-1 * D)  
    REZ = 1 / (1 + D1)
    REZ = round(REZ, 3)
    
    if REZ > 0.5:
        REZS = 'ДЕБЮТ АТЕРОСКЛЕРОЗА И ГБ'
    else:
        REZS = 'БЛАГОПРИЯТНЫЙ'
    
    VOZRAST_R = str(VOZRAST_R)
    REZ_R = str(REZ)
    with open('result ishod AZ i GB.txt','a') as file:
        file.write(FIO_R + ', возраст: ' + VOZRAST_R
                   + ', дата обследования: ' + CHISLO_R
                   + ', вероятность = ' + REZ_R
                   + '; ИСХОД: ' + REZS +'\n')

    messagebox.showinfo('ИСХОД              ', REZS)
    
window = Tk()
window.title("ПРОГРАММА ДЕБЮТА АЗ И ГБ ПОСЛЕ КОВИД")
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

NT = Label(frame, text="NTproBNP, пг/мл  ")
NT.grid(row=6, column=1)

NT = Entry(frame)
NT.grid(row=6, column=2)

LP = Label(frame, text="ЛПОНП, ед  ")
LP.grid(row=7, column=1)

LP = Entry(frame)
LP.grid(row=7, column=2)

btn = Button(frame, text="РАССЧИТАТЬ", command=clicked)
btn.grid(column=2, row=8)

btn = Button(frame, text='ВЫХОД', command=window.destroy)
btn.grid(column=2, row=9)

window.mainloop()
