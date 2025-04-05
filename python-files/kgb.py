a = 'Да'
b = 'ДА'
c = 'Нет'
d = 'НЕТ'

arrest = input('Сожалеете ли вы о распаде Союза Советских Социалистических Республик? Ответьте Да или Нет.')

while True:

 if a in arrest or b in arrest:
    pass
    print('Пройдёмте, гражданин')
    break
 elif c in arrest or d in arrest:
    pass
    print('Пройдёмте, товарищ')
    break
 else:
     pass
     print('Не-не-не, так не пойдёт.')
     arrest = input('Да или Нет?')
