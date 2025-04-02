
#importing stuff
import time
import turtle
print("launching")
turtle.forward(0)
#defining
t = turtle


def w():
    t.forward(10)
def a():
    t.left(90)
def s():
    t.backward(10)
def d():
    t.right(90)


t.bgpic("i.png")

t.onkey(w, "w")
t.onkey(a, "a")
t.onkey(s, "s")
t.onkey(d, "d")


#actions
t.listen()








