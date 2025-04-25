def sum(x, y):
    return x + y

def ymn(x, y):
    return x * y

def delen(x, y):
    return x / y

def minus(x, y):
    return x - y

while True:
    print("\n\n1. Сложение")
    print("2. Вычитание")
    print("3. Умножение")
    print("4. Деление")
    print("5. Выход")
    choise = input("Выберите операцию (от 1 до 5) - ")

    if choise == '5':
        print("Программа завершена.")
        break 

    if choise not in ('1', '2', '3', '4'):
        print("Выберите правильное действие!!!!!\n")
        continue
    x = float(input("Введите первое число: "))
    y = float(input("Введите второе число: "))

    if choise == '1':
        print(x, ' + ', y, ' = ', sum(x, y))
    elif choise == '2':
        print(x, ' - ', y, ' = ', minus(x, y))
    elif choise == '3':
        print(x, ' * ', y, ' = ', ymn(x, y))
    elif choise == '4':
        if y == 0:
            print("Деление на ноль нельзя!")
        else:
            print(x, ' / ', y, ' = ', delen(x, y))