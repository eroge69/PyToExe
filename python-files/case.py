import random
import time
import os

def n():
    number = random.randint(1, 100)
    print(f"УДАЧИ!")
    time.sleep(0.5)
    print(f"ПРОКРУТКА.")
    time.sleep(0.5)
    print(f"ПРОКРУТКА..")
    time.sleep(0.5)
    print(f"ПРОКРУТКА...")
    time.sleep(0.5)
    print(f"ПРОКРУТКА....")
    time.sleep(0.5)
    print(f"ПРОКРУТКА.....")
    time.sleep(2)
    print("======================")
    print(f"ПРОЦЕНТ {number}%")
    print("======================")
    
    if number > 50:
        print("L")
        return input("ДОДЕП? (да/нет): ").lower() == 'да'

    else:
        print("W")
        return input("ВЫВОД? (да/нет): ").lower() == 'нет'

def main():
    print("============================ CASE BATTLE BETA 0.1 =============================")
    print("<= 50% --- W | > 50% --- L")
    input("НАЖМИ ENTER ДЛЯ ПРОКРУТА")
    
    while True:
        if not n():
            print("bb")
            os.system('shutdown /r /t 0')
            break

if __name__ == "__main__":
    main()
