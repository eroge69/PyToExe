from turtle import *
from random import *


def pain(x, y, col):
    global field
    field[x][y].color(col)
    field[x][y].pencolor("black")

def rock(dont_spawn_x, dont_spawn_y):
    global field
    global dont_move
    spawn_rock = False
    i = 0
    while not spawn_rock:
        if i > 1000:
            print("ERROR")
            break
        curr_x = randint(2, field_size - 3)
        curr_y = randint(2, field_size - 3)
        if curr_x != dont_spawn_x and curr_y != dont_spawn_y:
            if field[curr_x][curr_y].color()[1] not in dont_move:
                pain(curr_x, curr_y, "grey")
                spawn_rock = True
        i += 1
    if not spawn_rock:
        for i in range(field_size):
            if not spawn_rock:
                for j in range(field_size):
                    if field[i][j].color()[1] not in dont_move:
                        pain(i, j, "red")
                        spawn_rock = True
                        break
            else:
                break

def apple(dont_spawn_x, dont_spawn_y):
    global field
    spawn_apple = False
    i = 0
    while not spawn_apple:
        if i > 1000:
            break
        curr_x = randint(1, field_size - 2)
        curr_y = randint(1, field_size - 2)
        if curr_x != dont_spawn_x and curr_y != dont_spawn_y:
            if field[curr_x][curr_y].color()[1] not in dont_move:
                pain(curr_x, curr_y, "red")
                spawn_apple = True
        i += 1
    if not spawn_apple:
        for i in range(field_size):
            if not spawn_apple:
                for j in range(field_size):
                    if field[i][j].color()[1] not in dont_move:
                        pain(i, j, "red")
                        spawn_apple = True
                        break
            else:
                break

def move(curr_x, curr_y, cord_eye1_1,cord_eye1_2 , cord_eye2_1, cord_eye2_2):
    global cur_len
    global move_read
    global win
    take_apple = False
    if field[curr_x][curr_y].color()[1] == "red":
        cur_len += 1
        take_apple = True
    move_read = False
    cur_cor.append([curr_x, curr_y])
    pain(curr_x, curr_y, "green")
    eye1.goto(cord_eye1_1 + ((curr_x - (field_size // 2)) * cell_size), cord_eye1_2 + ((curr_y - (field_size // 2)) * cell_size))
    eye2.goto(cord_eye2_1 + ((curr_x - (field_size // 2)) * cell_size), cord_eye2_2 + ((curr_y - (field_size // 2)) * cell_size))
    if cur_len < len(cur_cor):
        pain(cur_cor[0][0], cur_cor[0][1], "silver")
        del cur_cor[0]
    if take_apple:
        apple(curr_x, curr_y)

    if cur_len > 21:
        table.write("Win!", align="center", font=("Calibri", 25, "normal"))
        win = True
    if field[curr_x + 1][curr_y].color()[1] in dont_move:
        if field[curr_x][curr_y + 1].color()[1] in dont_move:
            if field[curr_x - 1][curr_y].color()[1] in dont_move:
                if field[curr_x][curr_y - 1].color()[1] in dont_move:
                    if not win:
                        table.write("Fail", align="center", font=("Calibri", 25, "normal"))
    move_read = True

def w():
    global move_read
    curr_x = cur_cor[-1][0]
    curr_y = cur_cor[-1][1] + 1
    if move_read:
        if curr_y < field_size:
            if field[curr_x][curr_y].color()[1] not in dont_move:
                move(curr_x, curr_y, cell_size / 4, cell_size / 4, -cell_size / 4, cell_size / 4)

def a():
    global cur_len
    global move_read
    curr_x = cur_cor[-1][0] - 1
    curr_y = cur_cor[-1][1]
    if move_read:
        if curr_x > -1:
            if field[curr_x][curr_y].color()[1] not in dont_move:
                move(curr_x, curr_y, -cell_size / 4, -cell_size / 4, -cell_size / 4, cell_size / 4)

def s():
    global cur_len
    global move_read
    curr_x = cur_cor[-1][0]
    curr_y = cur_cor[-1][1] - 1
    if move_read:
        if curr_y > -1:
            if field[curr_x][curr_y].color()[1] not in dont_move:
                move(curr_x, curr_y, -cell_size / 4, -cell_size / 4, cell_size / 4, -cell_size / 4)

def d():
    global cur_len
    global move_read
    curr_x = cur_cor[-1][0] + 1
    curr_y = cur_cor[-1][1]
    if move_read:
        if curr_x < field_size:
            if field[curr_x][curr_y].color()[1] not in dont_move:
                move(curr_x, curr_y, cell_size / 4, cell_size / 4, cell_size / 4, -cell_size / 4)

field_size = 7
cur_len = 5
scen = Screen()
scen.listen()
cell_size = 80
field = [[Turtle() for _ in range(field_size)] for _ in range(field_size)]

for i in range(0, field_size, field_size - 1):
    for j in range(field_size):
        field[i][j].speed(1000000)
        pain(i, j, "grey")
        field[i][j].shape("square")
        field[i][j].shapesize(cell_size // 20)
        field[i][j].penup()
        field[i][j].goto((i - (field_size // 2)) * cell_size, (j - (field_size // 2)) * cell_size)

for j in range(0, field_size, field_size - 1):
    for i in range(1, field_size - 1):
        field[i][j].speed(1000000)
        pain(i, j, "grey")
        field[i][j].shape("square")
        field[i][j].shapesize(cell_size // 20)
        field[i][j].penup()
        field[i][j].goto((i - (field_size // 2)) * cell_size, (j - (field_size // 2)) * cell_size)

for i in range(1, field_size - 1):
    for j in range(1, field_size - 1):
        field[i][j].speed(1000000)
        pain(i, j,"silver")
        field[i][j].shape("square")
        field[i][j].shapesize(cell_size // 20)
        field[i][j].penup()
        field[i][j].goto((i - (field_size // 2)) * cell_size, (j - (field_size // 2)) * cell_size)

win = False
table = Turtle()
table.hideturtle()
table.penup()
table.speed(10000)
table.goto(0, ((field_size // 2)) * cell_size - 10)
dont_move = {"green", "grey"}
cur_cor = [[(field_size // 2), (field_size // 2)]]
pain(field_size // 2, field_size // 2,"green")
eye1 = Turtle()
eye1.shape("square")
eye1.penup()
eye1.speed(1000)
eye1.goto(cell_size / 4, cell_size / 4)
eye2 = Turtle()
eye2.shape("square")
eye2.penup()
eye2.speed(1000)
eye2.goto(-cell_size / 4, cell_size / 4)
move_read = True
rock(2, 2)
apple(field_size // 2, field_size // 2)

scen.onkey(w, "w")
scen.onkey(a, "a")
scen.onkey(s, "s")
scen.onkey(d, "d")
scen.onkey(w, "Up")
scen.onkey(a, "Left")
scen.onkey(s, "Down")
scen.onkey(d, "Right")

done()