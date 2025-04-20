import random
import time

def razdacha():
    print("добрый день, вас приветствует игра в 21!")

    player = 0
    diler = 0

    kartaP = random.randint(1, 11)
    kartaD = random.randint(1, 11)
    kartaP2 = random.randint(3, 11)
    kartaD2 = random.randint(4, 11)

    player += kartaP + kartaP2
    diler += kartaD + kartaD2

    print('Ваши очки', player, '\n Взять ещё или Оставить эти?')
    resheny = input('Ваше решение? ')
    if resheny == '1' or resheny == 'ещё' or resheny == 'взять':
        player += kartaP
    if resheny == '2' or resheny == 'оставить' or resheny == 'оставить эти':
        pass
    print('Ваши очки', player, '\n Взять ещё или Оставить эти?')
    resheny = input('Ваше решение? ')
    if resheny == '1' or resheny == 'ещё' or resheny == 'взять':
        player += kartaP
        print('Ваши очки', player)
    if resheny == '2' or resheny == 'оставить' or resheny == 'оставить эти':
        print('Ваши очки', player)
        pass


    if diler <= 13:
        diler += kartaD

    print("открываем карты...")
    time.sleep(5)

    print("oчки дилера: ", diler, '\n' "очки игрока: ", player)

    if player > 21:
        print('выйграл дилер')
        quit()

    if diler > 21:
        print("выйграл игрок")
        quit()
    if player > diler:
        print('выйграл игрок')
    else:
        print('дилер выйграл')
    time.sleep(10)
def calculator():
    def add(a, b):
        return a + b

    def minus(a, b):
        return a - b

    def ymnoshenie(a, b):
        return a * b

    def delenie(a, b):
        if b == 0:
            return 'на ноль нельзя'
        return a / b
    print("добро пожаловать в волшебный калькулятор")
    while True:
        sheslo1 = float(input("введите 1 число: "))
        sheslo2 = float(input("введите 2 число: "))
        operatchiya = input("введите операцию: \n(+, -, *, /) \n или \n'q'(выход) \n что выберешь: ")
        if operatchiya == "q":
            print('спасибо за использование, досвидание!')
            break
        if operatchiya == "+":
            resultat = add(sheslo1, sheslo2)
        elif operatchiya == '-':
            resultat = minus(sheslo1, sheslo2)
        elif operatchiya == '*':
            resultat = ymnoshenie(sheslo1, sheslo2)
        elif operatchiya == '/':
            resultat = delenie(sheslo1, sheslo2)
        else:
            print("неверная операция, попробуйте снова")
            continue
        print(f"результат: {resultat} \n ")
def alximik():
    elements = ['огонь', 'земля', 'вода', "воздух"]
    recept = {'огоньземля': 'пар', 'водаогонь': 'пар', 'землявода': 'мокрая земля', 'водаземля': 'мокрая земля',
              'огоньвода': 'пар', "водаземля": "растение", "землявода": 'растение', "растениерастение": "дерево",
              "водавоздух": 'облако', "воздухвода": 'облако',
              "облакооблако": 'небо', "небоогонь": 'солнце', 'огоньнебо': 'солнце', 'водаоблако': 'дождь',
              "облаковода": 'дождь', "солнцедождь": 'радуга', 'дождьсолнце': 'радуга'}
    print("!!!!!!!!!!!!!!!!!!!!!!!!")
    print('попробуй сделать радугу')
    print("!!!!!!!!!!!!!!!!!!!!!!!!")
    while True:
        print('открытых элементов', len(elements))
        print('твои доступные элементы: ', *elements)
        el1 = input('напиши название первого элемента: ')
        el2 = input('напиши название второго элемента: ')
        if el1 in elements and el2 in elements:
            formyla = el1 + el2
            if formyla in recept:
                print('получился: ', recept[formyla])
                if recept[formyla] not in elements:
                    elements.append(recept[formyla])

            else:
                print('нечего невышло ')
            if "радуга" in elements:
                print("ты выйграл! \n молодец!")
                time.sleep(10)
                break

igra = input("что ты хочешь открыть?""\n""*калькулятор""\n""*21 очко""\n"'*алхимик'"\n""выбор: ")
if igra == 'калькулятор':
    calculator()
elif igra == "21 очко":
    razdacha()
elif igra == 'алхимик':
    alximik()
else:
    print("такого нету")
    exit()
