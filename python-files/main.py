import time

zigzag = int(input('Введите градус, на который хотите поднять руку(числом, без знаков; 0 - рука вдоль тела, 90 - рука вверх):'))
while True:
    if zigzag >= 84 or 0 <= zigzag < 10 or zigzag < 0 :
        print('Nothing happened...')
        time.sleep(2)
        zigzag = int(input('Введите градус:'))
    elif 84 > zigzag > 44:
        print('354 УК РФ')
        time.sleep(1.8)
        break
    elif 10 < zigzag < 23:
        print('You pet the dog!')
        time.sleep(1.7)
        break
    elif 23 <= zigzag < 44:
        print('You pet the children!')
        time.sleep(1.7)
        break