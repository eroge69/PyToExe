import math
from tkinter import *
#import pygame.mixer
#pygame.mixer.init()


# Перемнные--------------------------------------
window = Tk()
frame = Frame(window, bg="blue")
label = Label(frame, text="Поле с циферками", font=100)
buttons = []
xb = 5
yb = 325
calc = ""
mode = ""
num1, num2 = 0, 0
#sound = pygame.mixer.Sound("mixkit-modern-technology-select-3124.wav")
#sound.set_volume(0.2)


# Функции----------------------------------------
def button(num):
    global calc
    calc += str(num)
    label.config(text=calc)
    #sound.play()

def doMath(mode_to):
    global mode, num1, mode, calc
    #sound.play()
    mode = mode_to
    num1 = float(calc)
    calc = ""
    label.config(text=calc)

def clear():
    global calc, num1, num2
    #sound.play()
    num1 = 0
    num2 = 0
    calc = ""
    label.config(text=calc)

def clear1():
    global calc
    #sound.play()
    calc = calc[:-1]
    label.config(text=calc)

def plmn():
    global calc
    #sound.play()
    calc = float(calc)
    calc *= -1
    calc = str(calc)
    label.config(text=calc)

def power(num):
    global calc, num1
    #sound.play()
    num1 = math.pow(float(calc), num)
    calc = str(num1)
    label.config(text=calc)

def doravn():
    global calc, num1, num2
    #sound.play()
    num2 = float(calc)
    if mode == "+":
        num1 += num2
    if mode == "-":
        num1 -= num2
    if mode == "*":
        num1 *= num2
    if mode == "/":
        if num2 == 0:
            label.config(text="На ноль делить нельзя!")
            calc = ""
            return
        num1 /= num2
    if mode == "**":
        num1 **= num2
    calc = str(num1)
    label.config(text=calc)
    calc = ""

# Создание интерфейса---------------------------------------------------------------------
window.title("Калькулятор alpha 1.3")
window.geometry("400x500")
window.resizable(False, False)
frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.98)
label.place(x=5, y=5, width=382, height=100)
for i in range(10):
    buttons.append(Button(frame, text=i, font=50,command=lambda num=i: button(num), bg="#73ffdc", activebackground="#35b897"))
    if i == 0: buttons[i].place(x=87, y=407, width=80, height=80)
    else:
        buttons[i].place(x=xb, y=yb, width=80, height=80)
        xb += 82
        if xb > 240:
            xb = 5
            yb -= 82

# Кнопки действий
bPlus = Button(frame, text="+", font=50, command=lambda:doMath("+"))
bPlus.place(x=310, y=407, width=80, height=80)
bMinus = Button(frame, text="-", font=50, command=lambda:doMath("-"))
bMinus.place(x=310, y=325, width=80, height=80)
bUmn = Button(frame, text="x", font=50, command=lambda:doMath("*"))
bUmn.place(x=310, y=243, width=80, height=80)
bDel = Button(frame, text="/", font=50, command=lambda:doMath("/"))
bDel.place(x=310, y=161, width=80, height=80)
bStep = Button(frame, text="**", font=50, command=lambda:doMath("**"))
bStep.place(x=251, y=161, width=57, height=80)
bVvs = Button(frame, text="**2", font=50, command=lambda:power(2))
bVvs.place(x=5, y=107, width=80, height=52)
bOdx = Button(frame, text="1/x", font=50, command=lambda:power(-1))
bOdx.place(x=87, y=107, width=80, height=52)
bCkc = Button(frame, text="√", font=50, command=lambda:power(1/2))
bCkc.place(x=169, y=107, width=80, height=52)
bRavn = Button(frame, text="=", font=50, command=doravn)
bRavn.place(x=251, y=325, width=57, height=162)
bClear = Button(frame, text="C", font=50, command=clear)
bClear.place(x=310, y=107, width=80, height=52)
bClear1 = Button(frame, text="<<", font=50, command=clear1)
bClear1.place(x=250, y=107, width=58, height=52)
bPM = Button(frame, text="+/-", font=50, command=plmn)
bPM.place(x=5, y=407, width=80, height=80)

window.mainloop()