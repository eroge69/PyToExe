import time

a = 'Yes'; b = 'No'; c = 'YES'; d = 'NO'; i = 1000

dead = input('Are you dead inside?')

while True:
    if a in dead or c in dead:
        print('Me too')
        time.sleep(0.2)
        break
    elif b in dead or d in dead:
        print('"As if you had a choice"')
        time.sleep(0.5)
        break
    else:
        print("Well, you definitely are if you don't even wanna answer appropriately.")
        time.sleep(2.1)
        break

while True:
    print(i, '- 7')
    time.sleep(0.03)
    i -= 7
    if i < 0:
        print('-1')
        print('всё, кончил')
        time.sleep(1.7)
        print('Ну программу выполнять')
        time.sleep(1.5)
        print('А вы о чём подумали, товарищ Никулин')
        time.sleep(1.3)
        break
