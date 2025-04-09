import math
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import matplotlib.pyplot as plt

def filewrite(f, x):
     f.write(str(x))
     f.write("\n")
     
class body:
     x = 0
     m = 0
     v = 0
     a = 0
     def __init__(self, x, m, v, a):
          self.x = x
          self.m = m
          self.v = v
          self.a = a

def distance(first, second):
     D = abs(first.x - second.x)
     return D

def time(first, second):
     if first.a == 0 and second.a ==0:
          return -(first.x - second.x)/(first.v-second.v)
     else:
          D = (first.v - second.v)**2 - 4*(first.x-second.x)*((first.a/2)-(second.a/2))
          Time= []
          t = ((-1*(first.v-second.v)) + math.sqrt(D)) / (2*(first.a/2 - second.a/2))
          Time.append(t)
          t = ((-1*(first.v-second.v)) - math.sqrt(D)) / (2*(first.a/2 - second.a/2))          
          Time.append(t)
          return max(Time)

def Impulse(first, second, t):
     Imp_1  = first.m*(first.v + first.a*t)
     Imp_2 = second.m*(second.v + second.a*t)
     return abs(Imp_1)+abs(Imp_2)

def Imp (first, second, t):
     Imp_01  = first.m*first.v
     print("начальный импульс первого тела равен:", Imp_01)
     Imp_02 = second.m*second.v
     print("начальный импульс второго тела равен:", Imp_02)
     Imp_1  = first.m*(first.v + first.a*t)
     print("конечный импульс первого тела перед ударом равен:", Imp_1)
     Imp_2 = second.m*(second.v + second.a*t)
     print("конечный импульс второго тела перед ударом равен:", Imp_2)
     
    #график1

     step = 0
     X = []
     Y = []
     while step < t:
          Y.append(first.m*(first.v + first.a*step))
          step+=0.1
          X.append(step)
     for i in range(5):
          step+=0.1
          X.append(step)
     Y += [Impulse(first, second, t)]*5
     plt.plot(X, Y)

     #график2
     step2 = 0
     X2 = []
     Y2 = []
     while step2 < t:
          Y2.append(second.m*(second.v + second.a*step2))
          step2+=0.1
          X2.append(step2)
     for i in range(5):
          step2+=0.1
          X2.append(step2)
     Y2 += [Impulse(first, second, t)]*5
     plt.plot(X2, Y2)
     plt.show()
def speed(first, second, t):
    return Impulse(first, second, t) / (first.m + second.m)

def startOperations():
     #file = open("Data/data.txt", "w")
     
     first = body(float(point1_mb.get()), float(mass1_mb.get()), float(speed1_mb.get()), float(boost1_mb.get()))
     second = body(float(point2_mb.get()), float(mass2_mb.get()), float(speed2_mb.get()), float(boost2_mb.get()))
     '''
     filewrite(file, first.a) ##file0:  a1, a2, v01, vo2, t, m1, m2, v1, v2, ImpK. Speed, x1, x2
     filewrite(file, second.a)
     filewrite(file, first.v)
     filewrite(file, second.v)
     filewrite(file, first.m)
     filewrite(file, second.m)
     '''
     ttime = time(first, second)
     #filewrite(file, ttime)
     print("Время столкновения:", ttime)
     #filewrite(file, (first.v + first.a*ttime) )
     #filewrite(file, (second.v + second.a*ttime))
     
     sspeed = speed(first, second, ttime)
     #filewrite(file, sspeed)
     print("Конечная скорость системы:", sspeed)
     #filewrite(file, first.x)
     #filewrite(file, second.x)
     #file.close()
     print("Конечный испульс системы:", Impulse(first, second, ttime))
     Imp(first, second, ttime)
  
#main
window = Tk() 
window.title("Демонстрация ЗСИ. Абсолютно неупругие столкновения") 
window.geometry('1000x400')
frame = Frame(window, padx = 10, pady = 10)
frame.pack(expand=True)
#подписи
title1_lb = Label(frame, text = "Первое тело")
title1_lb.grid(row = 1, column = 1)
title2_lb = Label(frame, text = "Второе тело")
title2_lb.grid(row = 1, column = 3)

mass1_lb = Label(frame, text="Масса:  ")
mass1_lb.grid(row=3, column=1)
mass2_lb = Label(frame, text="Масса:  ")
mass2_lb.grid(row=3, column=3)

speed1_lb = Label(frame, text="Начальная скорость:  ")
speed1_lb.grid(row=4, column=1)
speed2_lb = Label(frame, text="Начальная скорость:  ")
speed2_lb.grid(row=4, column=3)

boost1_lb = Label(frame, text="Ускорение:  ")
boost1_lb.grid(row=5, column=1)
boost2_lb = Label(frame, text="Ускорение:  ")
boost2_lb.grid(row=5, column=3)

point1_lb = Label(frame, text="Начальная координата X:  ")
point1_lb.grid(row=6, column=1)
point2_lb = Label(frame, text="Начальная координата X:  ")
point2_lb.grid(row=6, column=3)
########

#Поля ввода
mass1_mb = Entry(frame, )
mass1_mb.grid(row=3, column=2)
mass2_mb = Entry(frame, )
mass2_mb.grid(row=3, column=4)

speed1_mb = Entry(frame, )
speed1_mb.grid(row=4, column=2)
speed2_mb = Entry(frame, )
speed2_mb.grid(row=4, column=4)

boost1_mb = Entry(frame, )
boost1_mb.grid(row=5, column=2)
boost2_mb = Entry(frame, )
boost2_mb.grid(row=5, column=4)

point1_mb = Entry(frame, )
point1_mb.grid(row=6, column=2)
point2_mb = Entry(frame, )
point2_mb.grid(row=6, column=4)
##########
          

#кнопка одобрения
mainbutton = Button(frame, text="Начать", command=startOperations)
mainbutton.grid(row=7, column=5)

#mainbutton = Button(frame, text="Запустить анимацию", command=StartAnim)
#mainbutton.grid(row=8, column=5)
int(input())

