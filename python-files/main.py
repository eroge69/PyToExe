import time

zigzag = int(input('Введите градус, на который хотите поднять руку(числом, без знаков; 0 - рука вдоль тела, 90 - рука вверх):'))

if zigzag >= 90 or 0 <= zigzag < 10 or zigzag < 0 :
    print('Nothing happened...')
    time.sleep(2)
elif 90 > zigzag > 44:
    print('354 УК РФ')
elif 10 < zigzag < 23:
    print('You pet the dog!')
elif 23 < zigzag < 44:
    print('You pet the children')