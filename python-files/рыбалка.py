import random
from tkinter import *
from tkinter import PhotoImage
window = Tk()
window.title('поймай это рыбку уже')
c = Canvas(window, width=600, height=600, bg='blue')
p = Canvas(window, width=600, height=100, bg='orange')
c.pack()
p.pack()
count = 0
im = PhotoImage(file="viva.png")
def ball():
    x = random.randint(10, 500)
    y = random.randint(10, 500)
    r = 30
    new_ball = c.create_image(x, y, image=im, anchor=NW)
    c.tag_bind(new_ball,'<Button-1>',click_on_circle)

def click_on_circle(event):
    c.delete(ALL)
    window.after(1,ball)
    global count
    count = count + 1
    print(str(count))
    p.delete(ALL)
    p.create_text(80,30, font='Arial 18',text='Вылов:')
    p.create_text(180,30, font='Arial 20',text=str(count))
    

ball ()

window.mainloop()
