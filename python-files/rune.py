import time
goyda = input('Штефанов - фашист?'); a = 'ДА'; b = 'Да'; c = 'НЕТ'; d = 'Нет'
while True:
    if a in goyda or b in goyda:
        print('Нет, мои милые, я не фашист, просто мне нравятся...')
        break
    elif c in goyda or d in goyda:
        print('Да, мои милые, я не фашист, просто мне нравятся...')
        break
    else:
        print('Ну хз, мои милые, я не фашист, просто мне нравятся...')
        break
def rune(row, col):
    for i in range(row):
        for j in range(col):
            if i < row // 2:
                if j < col // 2:
                    if j == 0:
                        print("*", end="")
                    else:
                        print(" ", end=" ")
                elif j == col // 2:
                    print(" *", end="")
                else:
                    if i == 0:
                        print(" *", end="")
            elif i == row // 2:
                print("* ", end="")
            else:
                if j == col // 2 or j == col - 1:
                    print("* ", end="")
                elif i == row - 1:
                    if j <= col // 2 or j == col - 1:
                        print("* ", end="")
                    else:
                        print(" ", end=" ")
                else:
                    print(" ", end=" ")
        print()
row = 14; col = 17
rune(row, col)
time.sleep(120)