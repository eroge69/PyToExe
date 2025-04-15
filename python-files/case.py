import random
import time
import os

def n():
    while True:
        try:
            threshold = int(input("ШАНС АПГРЕЙДА(1-100%): "))
            if 1 <= threshold <= 100:
                break
            else:
                print("ЧИСЛО ДОЛЖНО БЫТЬ ОТ 1 ДО 100")
        except ValueError:
            print("ВВЕДИ ЧИСЛО")

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
    time.sleep(1)
    print("======================")
    print(f"ПРОЦЕНТ {number}%")
    print("======================")
    
    if number > threshold:
        print("L")
        return input("ДОДЕП? (да/нет): ").lower() == 'да'
    else:
        print("W")
        return input("ВЫВОД? (да/нет): ").lower() == 'нет'

def main():
    print("============================ CASE BATTLE BETA 0.1 =============================")
    
    while True:
        if not n():
            print("bb")
            os.system('shutdown /r')
            break

if __name__ == "__main__":
    main()
