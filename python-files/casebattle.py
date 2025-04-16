import random
import time
import json
import os

# Файл для сохранения данных
SAVE_FILE = "game_save.json"

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    return {"balance": 1000, "last_game": None}

def save_game(data):
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)

def get_int_input(prompt, min_val, max_val):
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            print(f"ЧИСЛО ДОЛЖНО БЫТЬ ОТ {min_val} ДО {max_val}")
        except ValueError:
            print("ВВЕДИ ЧИСЛО")

def print_balance(balance):
    print(f"БАЛАНС: {balance}₽".rjust(50))

def play_round(balance):

    
    bet = get_int_input(f"\nВАША СТАВКА (1-{balance}₽): ", 1, balance)
    threshold = get_int_input("ШАНС АПГРЕЙДА (1-100%): ", 1, 100)
    multiplier = 100 / threshold
    
    number = random.randint(1, 100)
    
    print(f"\nУДАЧИ!")
    for i in range(5):
        print(f"ПРОКРУТКА{'.' * (i+1)}")
        time.sleep(0.3)
    
    print(f"\nПРОЦЕНТ: {number}%")
    
    if number <= threshold:
        win_amount = int(bet * multiplier)
        print(f"\nW! ВЫ ВЫИГРАЛИ {win_amount}₽")
        return win_amount
    print(f"\nL! ВЫ ПРОИГРАЛИ {bet}₽")
    return -bet

def ask_deposit():
    while True:
        choice = input("\nДОДЕП? (да/нет): ").lower()
        if choice == 'да':
            return 1000
        if choice == 'нет':
            print("\nДо свидания!")
            exit()
        print("Введите 'да' или 'нет'")

def main():
    game_data = load_game()
    balance = game_data["balance"]
    
    print("\n" + " CASE BATTLE ".center(50, "~"))
    if game_data["last_game"]:
        print(f"\nПоследняя игра: {game_data['last_game']}")
    print_balance(balance)
    
    while True:
        result = play_round(balance)
        balance += result
        
        if balance <= 0:
            print("\nУ ВАС ЗАКОНЧИЛИСЬ ДЕНЬГИ!")
            balance = ask_deposit()
            print(f"\nВАШ НОВЫЙ БАЛАНС: {balance}₽")
            continue
            
        choice = input("\nХОТИТЕ ПРОДОЛЖИТЬ? (да/нет): ").lower()
        if choice != 'да':
            # Сохраняем игру перед выходом
            save_game({
                "balance": balance,
                "last_game": time.strftime("%d.%m.%Y %H:%M")
            })
            print(f"\nИгра сохранена. Ваш баланс: {balance}₽")
            print("Возвращайтесь в любое время!")
            break
    
    print("\nСПАСИБО ЗА ИГРУ!")

if __name__ == "__main__":
    main()
