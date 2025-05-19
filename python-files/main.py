import subprocess
import re
import sys


choise = [1,2,3]

match = []
validIP = []
bussyAdd = 0
print('Скрипт для нахождения свободных IP-адресов')
print('Выберите диапозон:')
print('1 - 10.25.13.0/24')
print('2 - 10.25.17.0/24')
print('_________________')
print('3 - выйти')


def choices():

    scope = ''
    while scope not in choise:
        try:
           
            scope = int(input('->'))
        except:
            print('Надо выбрать цифру от 1 до 3 и нажать ENTER')

        switch = {1:scope13,2:scope17,3:sys.exit}
        try:
            switch.get(scope)()
        except:
            ...


def cmdCommand(command):

    content = subprocess.run([command],shell=True, capture_output=True, text=True, encoding="cp866")
    content = content.stdout
    print(content)
    #with open('ipaddres.txt', 'r', encoding='UTF-8') as file:
     #   content = file.read()
    return content


def scope13():
    global match
    match = []
    content = cmdCommand('netsh dhcp server scope 10.25.13.0 show client')

    match = re.findall(r'(?<=10\.25\.13\.)\d+', content)
    match = [i for i in match if i != '0']

    findAddress('10.25.13.')


def scope17():
    global match
    match = []
    content = cmdCommand('netsh dhcp server scope 10.25.17.0 show client')
    match = re.findall(r'(?<=10\.25\.17\.)\d+', content)
    match = [i for i in match if i != '0']

    findAddress('10.25.17.')


def findAddress(NetAddres):
    global bussyAdd
    global validIP
    validIP = []
    bussyAdd = len(match)
    i=1

    while i <254:

        lenM=len(match)
        if len(match)!=0:
            ip = int(match[0])
            if i < ip:
                validIP.append(NetAddres+str(i))
                i+=1
            elif i == int(match[0]):
                match.pop(0)
                i+=1
            else:
                print("Произошла ошибка при анализе свободных ip адресов. Это сообщение будет появляться не больше 254 раз")
        else:
            i+=1
            validIP.append(NetAddres + str(i))

    for i in range(0, len(validIP), 6):
        print("Свободные ip: ", ', '.join(validIP[i:i + 6]))
    print('Всего свободных: ', len(validIP))
    print('Всего занятых: ', bussyAdd)
    print('Общее количество адресов:',bussyAdd+len(validIP))
    choices()

choices()