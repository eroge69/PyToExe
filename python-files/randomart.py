import random
import turtle as t1
from turtle import TurtleScreen
t1.setpos(0,0)
t1.speed(99999999999999999999999999999999999999)
t1.pencolor('Black')
c = (random.randint(0,3))
t1.hideturtle()
def randomcolor():
    while True:
        if c == 1 :
            t1.pencolor('Red')
        if c == 2 :
            t1.pencolor('Green')
        if c == 3 :
            t1.pencolor('Blue')

def crandom():
    c = (random.randint(-1,4))
while True:
    a = (random.randint(-500,500))
    b = (random.randint(-5,5))
    t1.fd(1)
    t1.rt(a)
    x = t1.xcor
    y = t1.ycor
while True:
    t1.ontimer(randomcolor(), 500)
    t1.ontimer(crandom(), 500)
