from tkinter import*
from math import*
from time import sleep
from random import*
fabric = Canvas(width=800, height=800,bg='#000000')
fabric.pack()






ship=[
    400,400,
    10,
    0.001,
    0,
    0,
    0
    ]



forces=[
    0,
    0
    ]


C=[
        [ship[0]+cos(ship[3])*25,ship[1]+sin(ship[3])*25],
        [ship[0]-cos(pi/4.5+ship[3])*25,ship[1]-sin(pi/4.5+ship[3])*25],
        [ship[0]-cos(pi/4.5-ship[3])*25,ship[1]+sin(pi/4.5-ship[3])*25]
        ]



bullets=[]
asteroids=[]
score=0
cd=0
teleport=0
game = False
playing = False
name = ''

# ship 0-1 : XY
# ship 2 : weight
# ship 3 : angle
# ship 4-5 : VX/Y
# ship 6 : rotation speed

# forces 0 : acceleration
# forces 1 : rotation force

# bullets 0-1 : XY
# bullets 2 : angle



def press(event):
    global forces,playing

    if playing:
        if event.keysym=='a':
            forces[1]=-0.01
        if event.keysym=='d':
            forces[1]=0.01
        if event.keysym=='w':
            forces[0]=1
        if event.keysym=='s':
            forces[0]=-0.2
        if event.keysym=='e':
            hyperspace()


    if not(playing):
        global name
        if len(event.keysym)<2:
            name+=event.keysym
            print(name)
        if event.keysym=="BackSpace":
            name=name[0:-1]
        


def stop(event):
    global forces
    
    if event.keysym=='d':
        if forces[1]>0:
            forces[1]=0
            
    if event.keysym=='a':
      if forces[1]<0:
            forces[1]=0
            
    if event.keysym=='w':
        if forces[0]>0:
            forces[0]=0
    if event.keysym=='s':
        if forces[0]<0:
            forces[0]=0



def shoot(event):
    global bullets,ship,cd,teleport



    if teleport>0:
        return
    
    if cd<0:
        bullets.append([ship[0]+cos(ship[3])*25,ship[1]+sin(ship[3])*25,ship[3],1])
        cd=3


    
def angle_between(a, b):
    return pi-abs(abs(a-b)-pi)



def ship_update():
    global ship,forces,teleport



    if teleport>0:
        return
    
    ship[6]+=forces[1]/ship[2]*5
    ship[6]=ship[6]*0.99
    ship[3]+=ship[6]
    ship[3]%=2*pi
    #angle updates
    
    ship[4]+=cos(ship[3])*forces[0]/ship[2]
    ship[5]+=sin(ship[3])*forces[0]/ship[2]
    #velocity update
    
    ship[0]+=ship[4]
    ship[1]+=ship[5]
    ship[0]%=800
    ship[1]%=800
    #coord updates



def bullet():
    global bullets
    
    for i in bullets:
        i[0]+=cos(i[2])*10
        i[1]+=sin(i[2])*10
        i[0]%=800
        i[1]%=800
        i[3]-=1/60
        if i[3]<=0:
            bullets.remove(i)
        fabric.create_line(i[0],i[1],i[0]-cos(i[2])*10,i[1]-sin(i[2])*10,fill='#4AF626')


    
def draw_ship():
    global ship,forces,C,teleport
    
    C=[
        [ship[0]+cos(ship[3])*25,ship[1]+sin(ship[3])*25],
        [ship[0]-cos(pi/4.5+ship[3])*25,ship[1]-sin(pi/4.5+ship[3])*25],
        [ship[0]-cos(pi/4.5-ship[3])*25,ship[1]+sin(pi/4.5-ship[3])*25]
        ]
    
    L=[
        [ship[0]-cos(ship[3])*25,ship[1]-sin(ship[3])*25],
        [ship[0]-cos(ship[3])*40,ship[1]-sin(ship[3])*40]]
    
    if forces[0]>0:
        fabric.create_line(L[0][0],L[0][1],L[1][0],L[1][1],fill='#4AF626')

    if teleport>0:
        return
    
    fabric.create_polygon(C[0][0],C[0][1],C[1][0],C[1][1],C[2][0],C[2][1],outline='#4AF626')
    


def create_asteroid():
    global asteroids,ship
    
    xy=[ship[0],ship[1]]
    
    while abs(xy[0]-ship[0])<100 or abs(xy[1]-ship[1])<100:
        xy=[random()*800,random()*800]
        
        if xy[0]>xy[1]:
            xy[0]=800
            
        else :
            xy[1]=800
            
    asteroids.append([xy[0],xy[1],random()*2*pi,randint(30,40)])


    
def asteroid():
    global asteroids,ship,bullets,score
    
    for i in asteroids:
        i[0]+=cos(i[2])*2
        i[1]+=sin(i[2])*2
        i[0]%=800
        i[1]%=800

        fabric.create_oval(i[0]-i[3],i[1]-i[3],i[0]+i[3],i[1]+i[3],outline='#4AF626')
        
                    
        for j in bullets:
            d=sqrt((i[0]-j[0])**2+(i[1]-j[1])**2)
            
            if d<i[3]:
                bullets.remove(j)
                asteroid_child(i)
                score+=100
                break



def asteroid_child(parent):
    global asteroids
    
    size=parent[3]/sqrt(2)


    
    if size<15:
        asteroids.remove(parent)
        
    else :
        direction=parent[2]
        dir1=direction+pi/4
        dir2=direction-pi/4
        asteroids.append([parent[0]+cos(dir2)*size,parent[1]+sin(dir2)*size,dir2,size])
        asteroids.append([parent[0]+cos(dir1)*size,parent[1]+sin(dir1)*size,dir1,size])
        asteroids.remove(parent)



def hyperspace():
    global teleport,ship

    
    
    if teleport>0:
        return
    
    teleport=1
    ship[0]=random()*800
    ship[1]=random()*800



def collision():
    global asteroids,C,teleport
    if teleport>0:
        return
    
    for j in asteroids:
        d=sqrt((ship[0]-j[0])**2+(ship[1]-j[1])**2)
        if d<j[3]+5:
            return True
        for i in C:
            d=sqrt((i[0]-j[0])**2+(i[1]-j[1])**2)
            if d<j[3]+5:
                return True
    return False



def score_entry(score):
    global name,playing

    name=""
    playing=False

    while len(name)<3:
        fabric.delete(ALL)
        fabric.create_text(400,400,font=("Atari Vector",20),text="Enter your name",fill='#4AF626')
        fabric.create_text(400,450,font=("Atari Vector",15),text=name,fill='#4AF626',anchor="sw")
        fabric.create_text(400,450,font=("Atari Vector",15),text="___",fill='#4AF626',anchor="sw")
        fabric.update()
        sleep(0.1)

        
    fabric.delete(ALL)
    fabric.create_text(400,450,font=("Atari Vector",15),text=name[0:3],fill='#4AF626',anchor="sw")
    fabric.create_text(400,450,font=("Atari Vector",15),text="___",fill='#4AF626',anchor="sw")
    fabric.update()

    

    HS=''
    scores=[]
    print(score)
    with open("scores.txt", "a") as f:
        f.write("\n"+name[0:3]+" "+str(score))
    f.close()
        
    with open("scores.txt") as f:
        for i in range(10):
            data=f.readline()
            if len(data)>4:
                scores.append(data)
    f.close()
    scores.sort(reverse=True,key=scorenum)
    scores=[i[0:].replace('\n','') for i in scores]
    print(scores)
    for i in scores:
        HS+="\n"
        HS+=i
        
    sleep(0.1)
    fabric.delete(ALL)
    fabric.create_text(400,100,font=("Atari Vector",25,"bold"),text="HIGH SCORES :",fill='#4AF626')
    fabric.create_text(300,200,font=("Atari Vector",25,"bold"),text=HS,fill='#4AF626',anchor="nw")
    fabric.create_text(400,700,font=("Atari Vector",25),text="Press ENTER to start",fill='#4AF626')



    

def scorenum(l):
    return int(l[4:].replace('\n',''))
    
    

        

def start(event):
    
    global cd,asteroids,score,ship,bullets,forces,game,teleport,playing

    if game==True :
        return
    game=True
    playing=True

    
    ship=[
    400,400,
    10,
    0.001,
    0,
    0,
    0
    ]
    forces=[
        0,
        0
        ]

    bullets=[]
    asteroids=[]
    score=0
    cd=0
    dif=1
    teleport=0

    for i in range(dif*4):
        create_asteroid()
    

    while not(collision()):
        
        fabric.delete(ALL)
        ship_update()
        draw_ship()
        bullet()
        asteroid()
        
        fabric.create_text(400,790,font=("Atari Vector",12),text="WASD : Movement     Space : Shoot      E : teleport",fill='#4AF626')
        fabric.create_text(15,10,font=("Atari Vector",20),text=str(score),fill='#4AF626',anchor="nw")
        fabric.update()
        cd-=0.5
        teleport-=1/30
        sleep(1/60)

        if len(asteroids)==0:
            dif+=1
            ship=[
            400,400,
            10,
            0,
            0,
            0,
            0
            ]
            forces=[
                0,
                0
                ]

            bullets=[]
            asteroids=[]
            cd=0

            for i in range(dif*4):
                create_asteroid()

    fabric.delete(ALL)
    
    bullet()
    asteroid()
    
    fabric.create_text(400,400,font=("Atari Vector",25,"bold"),text="GAME OVER",fill='#4AF626')

    
    fabric.update()

    sleep(3)

    fabric.delete(ALL)

    score_entry(score)
    
    game = False
    
    return 



fabric.create_text(400,400,font=("Atari Vector",25),text="Press ENTER to start",fill='#4AF626')
fabric.bind('<KeyPress>',press)
fabric.bind('<KeyRelease>',stop)
fabric.bind('<space>',shoot)
fabric.bind('<Return>',start)



fabric.focus_set()

