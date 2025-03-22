from pygame import *
from random import *
init()
window = display.set_mode((640,480))
x = 270
y = 190
play = 1
while play > 0:
    r = randint(0,255)
    g = randint(0,255)
    b = randint(0,255)
    x = randint(0,640)
    y = randint(0,480)
    for e in event.get():
        if e.type==QUIT:
            play=0
    draw.rect(window, (r,g,b), Rect(x,y,10,10))
    display.flip()
    
          
        
quit()
