#beginning
import math
from random import random
agr = input ("Сыграем? Да(1)/Нет(0)... ")
pcwin = 0 #сброс счетчиков счета
uswin = 0
while agr == '1':
    txt = input('Камень(1), ножницы(2) или бумага(3)? ')
    a = math.ceil(random() * 3)  # задали выбор компа
    if txt != '1' and txt != '2' and txt != '3':
        print ('Неверно. Надо 1 или 2 или 3. Пусть будет 1')
        txt = '1'
    if a == 1 and txt == '2':
        pcwin = pcwin + 1
        print('Камень! Я победил! Счёт: Комп ',pcwin, '/ Юзер',uswin)
    elif a == 1 and txt == '1':
        print ('НИЧЬЯ')
    elif a == 1 and txt == '3':
        uswin = uswin + 1
        print ('Ты победил... Счёт: Комп ', pcwin, "/ Юзер", uswin)
    if a == 2 and txt == '3':
        pcwin = pcwin + 1
        print ('Ножницы! Я победил! Счёт: Комп ', pcwin, '/ Юзер', uswin)
    elif a == 2 and txt == '2':
        print ("НИЧЬЯ")
    elif a == 2 and txt == '1':
        uswin = uswin + 1
        print ('Ты победил... Счёт: Комп ', pcwin, "/ Юзер", uswin)
    if a == 3 and txt == '1':
        pcwin = pcwin + 1
        print ('Бумага! Я победил! Счёт: Комп ', pcwin, '/ Юзер', uswin)
    elif a == 3 and txt == '3':
        print ("НИЧЬЯ")
    elif a == 3 and txt == '2':
        uswin = uswin + 1
        print ('Ты победил... Счёт: Комп ', pcwin, "/ Юзер", uswin)
    agr = input ('Еще? Да(1)/Нет(0)...')
    if agr == '0': break
    else: agr = '1'