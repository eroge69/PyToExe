import random
import time
import sys
from colorama import init, Fore, Back, Style

# Инициализация colorama
init(autoreset=True)

# ===== Общие функции =====
def exit_check(input_str):
    """Проверка на выход (999)"""
    if input_str == "999":
        print(Fore.YELLOW + "\nВозврат в меню...")
        time.sleep(1)
        return True
    return False

def print_header(title):
    """Красивое отображение заголовка"""
    print(Fore.MAGENTA + "\n" + "="*40)
    print(Fore.GREEN + f"=== {title.upper()} ===".center(36))
    print(Fore.MAGENTA + "="*40)

def clear_screen():
    """Очистка экрана"""
    print("\n" * 50 if sys.platform == "win32" else "\033c", end="")

def input_with_exit(prompt):
    """Безопасный ввод с проверкой на выход"""
    while True:
        try:
            user_input = input(prompt)
            if exit_check(user_input):
                return None
            return user_input
        except (EOFError, KeyboardInterrupt):
            print("\n" + Fore.RED + "Ошибка ввода!")
            continue

# ===== Игры =====

def guess_the_number():
    print_header("Угадай число")
    secret = random.randint(1, 100)
    attempts = 0
    
    while True:
        guess = input_with_exit(f"\n{Fore.YELLOW}Твой вариант (1-100) или 999 для выхода: ")
        if guess is None: return
        
        try:
            guess = int(guess)
            if guess < 1 or guess > 100:
                raise ValueError
        except ValueError:
            print(Fore.RED + "Введи число от 1 до 100!")
            continue
            
        attempts += 1
        
        if guess < secret:
            print(Fore.BLUE + "Слишком мало!")
        elif guess > secret:
            print(Fore.BLUE + "Слишком много!")
        else:
            print(Fore.GREEN + f"Победа! Число {secret} угадано за {attempts} попыток!")
            time.sleep(2)
            break

def memory_game():
    print_header("Игра на память")
    sequence = [random.choice("ABCDEFGH") for _ in range(4)]
    
    print("Запомни последовательность букв:")
    print(Fore.YELLOW + " ".join(sequence))
    time.sleep(3)
    clear_screen()
    
    user_input = input_with_exit("Введи буквы через пробел (например: A B C D): ")
    if user_input is None: return
    
    user_sequence = user_input.upper().split()
    
    if user_sequence == sequence:
        print(Fore.GREEN + "★ Поздравляю! Идеальная память!")
    else:
        print(Fore.RED + f"Ошибка! Правильно: {' '.join(sequence)}")
    time.sleep(2)

def tic_tac_toe():
    print_header("Крестики-нолики")
    board = [" "] * 9
    current_player = "X"
    
    def draw_board():
        print("\n  0 1 2")
        for i in range(3):
            row = board[i*3:i*3+3]
            colored_row = []
            for cell in row:
                if cell == "X":
                    colored_row.append(Fore.RED + cell)
                elif cell == "O":
                    colored_row.append(Fore.BLUE + cell)
                else:
                    colored_row.append(Style.RESET_ALL + cell)
            print(f"{i} {' '.join(colored_row)}")
    
    def check_winner():
        lines = [
            [0,1,2],[3,4,5],[6,7,8],
            [0,3,6],[1,4,7],[2,5,8],
            [0,4,8],[2,4,6]
        ]
        for line in lines:
            if board[line[0]] == board[line[1]] == board[line[2]] != " ":
                return board[line[0]]
        return None
    
    while True:
        draw_board()
        winner = check_winner()
        if winner or " " not in board:
            if winner:
                print(Fore.GREEN + f"\nИгрок {winner} победил!")
            else:
                print(Fore.YELLOW + "\nНичья!")
            time.sleep(2)
            break
            
        while True:
            move = input_with_exit(f"\n{Fore.YELLOW}Ход {current_player} (ряд столбец, например '1 2'): ")
            if move is None: return
            
            try:
                row, col = map(int, move.split())
                pos = row * 3 + col
                if 0 <= pos < 9 and board[pos] == " ":
                    board[pos] = current_player
                    break
                print(Fore.RED + "Некорректный ход!")
            except:
                print(Fore.RED + "Введи два числа через пробел!")
        
        current_player = "O" if current_player == "X" else "X"

def hangman():
    print_header("Виселица")
    words = ["ПРОГРАММИРОВАНИЕ", "КОМПЬЮТЕР", "АЛГОРИТМ", "ПИТОН", "ИНТЕРНЕТ"]
    word = random.choice(words)
    guessed = set()
    attempts = 6
    
    while attempts > 0:
        display = "".join([letter if letter in guessed else "_" for letter in word])
        print("\n" + " ".join(display))
        print(Fore.CYAN + f"Осталось попыток: {attempts}")
        
        if "_" not in display:
            print(Fore.GREEN + "\n★ Ты победил! Слово: " + word)
            time.sleep(2)
            return
            
        guess = input_with_exit(f"{Fore.YELLOW}Введи букву: ")
        if guess is None: return
        guess = guess.upper()
        
        if len(guess) != 1 or not guess.isalpha():
            print(Fore.RED + "Введи одну букву!")
            continue
            
        if guess in guessed:
            print(Fore.YELLOW + "Уже было!")
            continue
            
        guessed.add(guess)
        if guess not in word:
            attempts -= 1
            print(Fore.RED + "Нет такой буквы!")
    
    print(Fore.RED + f"\nИгра окончена! Слово было: {word}")
    time.sleep(2)

def blackjack():
    print_header("21 очко")
    cards = [2,3,4,5,6,7,8,9,10,10,10,10,11] * 4
    random.shuffle(cards)
    
    def deal_card():
        return cards.pop()
    
    def calculate_score(hand):
        if sum(hand) == 21 and len(hand) == 2:
            return 0
        if 11 in hand and sum(hand) > 21:
            hand.remove(11)
            hand.append(1)
        return sum(hand)
    
    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]
    
    while True:
        player_score = calculate_score(player_hand)
        dealer_score = calculate_score(dealer_hand)
        
        print(f"\nТвои карты: {player_hand}, очков: {player_score}")
        print(f"Карта дилера: [{dealer_hand[0]}, ?]")
        
        if player_score == 0 or dealer_score == 0 or player_score > 21:
            break
            
        action = input_with_exit(f"{Fore.YELLOW}Ещё карту (1) или хватит (2)? ")
        if action is None: return
        
        if action == "1":
            player_hand.append(deal_card())
        else:
            break
    
    while dealer_score != 0 and dealer_score < 17:
        dealer_hand.append(deal_card())
        dealer_score = calculate_score(dealer_hand)
    
    print(f"\nТвои карты: {player_hand}, очков: {player_score}")
    print(f"Карты дилера: {dealer_hand}, очков: {dealer_score}")
    
    if player_score > 21:
        print(Fore.RED + "Перебор! Ты проиграл.")
    elif dealer_score > 21:
        print(Fore.GREEN + "Дилер перебрал! Ты победил!")
    elif player_score == dealer_score:
        print(Fore.YELLOW + "Ничья!")
    elif player_score == 0:
        print(Fore.GREEN + "★ Blackjack! Ты победил!")
    elif dealer_score == 0:
        print(Fore.RED + "У дилера Blackjack! Ты проиграл.")
    elif player_score > dealer_score:
        print(Fore.GREEN + "Ты победил!")
    else:
        print(Fore.RED + "Дилер победил.")
    
    time.sleep(3)

def battleship():
    print_header("Морской бой")
    board_size = 5
    board = [["~" for _ in range(board_size)] for _ in range(board_size)]
    ship_row = random.randint(0, board_size-1)
    ship_col = random.randint(0, board_size-1)
    attempts = 5
    
    print(f"\nУ тебя {attempts} попыток потопить корабль!")
    
    for attempt in range(attempts):
        print("\n  " + " ".join(str(i) for i in range(board_size)))
        for i, row in enumerate(board):
            print(f"{i} " + " ".join(row))
        
        while True:
            guess = input_with_exit(f"\n{Fore.YELLOW}Выстрел (ряд столбец, например '1 2'): ")
            if guess is None: return
            
            try:
                row, col = map(int, guess.split())
                if 0 <= row < board_size and 0 <= col < board_size:
                    break
                print(Fore.RED + "Координаты вне поля!")
            except:
                print(Fore.RED + "Введи два числа через пробел!")
        
        if row == ship_row and col == ship_col:
            board[row][col] = Fore.RED + "X"
            print(Fore.GREEN + "\n★ Потопил! Ты победил!")
            time.sleep(2)
            return
        else:
            board[row][col] = Fore.BLUE + "O"
            print(Fore.RED + "Мимо!")
    
    print(Fore.RED + f"\nКорабль был на: {ship_row} {ship_col}")
    time.sleep(2)

def tetris():
    print_header("Тетрис")
    print(Fore.YELLOW + "Упрощенная консольная версия")
    print("\nУправление:")
    print("A - влево, D - вправо")
    print("S - ускорить падение")
    print("Q - повернуть, 999 - выход")
    
    shapes = [
        [['****'], ['*', '*', '*', '*']],
        [['***', ' * '], ['* ', '**', '* '], [' * ', '***'], [' *', '**', ' *']],
        [['***', '*  '], ['**', '* ', '* '], ['  *', '***'], [' *', ' *', '**']]
    ]
    
    current_shape = random.choice(shapes)
    pos_x, pos_y = 5, 0
    
    while True:
        clear_screen()
        print_header("Тетрис")
        
        # Отображение игрового поля с фигурой
        for y in range(10):
            row = []
            for x in range(10):
                if (x, y) in [(pos_x + dx, pos_y + dy) 
                             for dy in range(len(current_shape[0]))
                             for dx in range(len(current_shape[0][0])) 
                             if current_shape[0][dy][dx] == '*']:
                    row.append(Fore.RED + '#')
                else:
                    row.append('.')
            print(" ".join(row))
        
        cmd = input_with_exit("\nКоманда (A/D/S/Q): ")
        if cmd is None: return
        
        if cmd.upper() == 'A' and pos_x > 0:
            pos_x -= 1
        elif cmd.upper() == 'D' and pos_x < 10 - len(current_shape[0][0]):
            pos_x += 1
        elif cmd.upper() == 'S':
            pos_y += 1
        elif cmd.upper() == 'Q':
            current_shape = current_shape[1:] + [current_shape[0]]
        
        pos_y += 1
        if pos_y > 8:
            print(Fore.RED + "\nКонец игры!")
            time.sleep(2)
            return

def sudoku():
    print_header("Судоку")
    print(Fore.YELLOW + "Упрощенная версия - заполни пропущенные цифры")
    
    board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    
    def print_board():
        print("\n   " + " ".join(str(i) for i in range(9)))
        for i, row in enumerate(board):
            colored_row = []
            for num in row:
                colored_row.append(Fore.RED + str(num) if num != 0 else Fore.BLUE + ".")
            print(f"{i}  " + " ".join(colored_row))
    
    while True:
        print_board()
        try:
            move = input_with_exit("\nВведи ряд столбец число (например '2 3 5'): ")
            if move is None: return
            
            row, col, num = map(int, move.split())
            if 0 <= row < 9 and 0 <= col < 9 and 1 <= num <= 9:
                if board[row][col] == 0:
                    board[row][col] = num
                    print(Fore.GREEN + "Число добавлено!")
                else:
                    print(Fore.RED + "Здесь нельзя изменить число!")
            else:
                print(Fore.RED + "Некорректные координаты или число!")
        except:
            print(Fore.RED + "Введи три числа через пробел!")
        
        # Проверка на победу
        if all(0 not in row for row in board):
            print(Fore.GREEN + "\n★ Поздравляю! Судоку решено!")
            time.sleep(2)
            return

def chess():
    print_header("Шахматы")
    print(Fore.YELLOW + "Упрощенная версия - передвижение фигур")
    
    board = [
        ['r','n','b','q','k','b','n','r'],
        ['p']*8,
        ['.']*8,
        ['.']*8,
        ['.']*8,
        ['.']*8,
        ['P']*8,
        ['R','N','B','Q','K','B','N','R']
    ]
    
    def print_board():
        print("\n   " + " ".join(chr(97+i) for i in range(8)))
        for i, row in enumerate(board):
            colored_row = []
            for piece in row:
                if piece == '.':
                    colored_row.append('.')
                elif piece.isupper():
                    colored_row.append(Fore.BLUE + piece)
                else:
                    colored_row.append(Fore.RED + piece.upper())
            print(f"{8-i}  " + " ".join(colored_row))
    
    while True:
        print_board()
        move = input_with_exit("\nХод (например 'e2 e4'): ")
        if move is None: return
        
        try:
            src, dest = move.split()
            x1, y1 = ord(src[0])-97, 8-int(src[1])
            x2, y2 = ord(dest[0])-97, 8-int(dest[1])
            
            if 0 <= x1 < 8 and 0 <= y1 < 8 and 0 <= x2 < 8 and 0 <= y2 < 8:
                piece = board[y1][x1]
                if piece != '.':
                    board[y1][x1] = '.'
                    board[y2][x2] = piece
                    print(Fore.GREEN + "Ход сделан!")
                else:
                    print(Fore.RED + "Нет фигуры на стартовой позиции!")
            else:
                print(Fore.RED + "Некорректные координаты!")
        except:
            print(Fore.RED + "Введи ход в формате 'e2 e4'!")

def wheel_of_fortune():
    print_header("Поле чудес")
    words = ["ПРОГРАММИСТ", "КОМПЬЮТЕР", "АЛГОРИТМ", "ПИТОН", "ИНТЕРНЕТ"]
    word = random.choice(words)
    guessed = []
    attempts = 5
    
    while attempts > 0:
        masked = "".join([letter if letter in guessed else "_" for letter in word])
        print("\n" + " ".join(masked))
        print(Fore.CYAN + f"Осталось попыток: {attempts}")
        
        if "_" not in masked:
            print(Fore.GREEN + "\n★ Ты угадал слово: " + word)
            time.sleep(2)
            return
            
        guess = input_with_exit(f"{Fore.YELLOW}Введи букву или слово целиком: ")
        if guess is None: return
        guess = guess.upper()
        
        if len(guess) == 1:
            if guess in guessed:
                print(Fore.YELLOW + "Уже было!")
            elif guess in word:
                guessed.append(guess)
                print(Fore.GREEN + "Есть такая буква!")
            else:
                attempts -= 1
                print(Fore.RED + "Нет такой буквы!")
        else:
            if guess == word:
                print(Fore.GREEN + "\n★ Ты угадал слово!")
                time.sleep(2)
                return
            else:
                attempts -= 1
                print(Fore.RED + "Неверное слово!")
    
    print(Fore.RED + f"\nИгра окончена! Слово было: {word}")
    time.sleep(2)

def main_menu():
    games = {
        "1": ("Угадай число", guess_the_number),
        "2": ("Игра на память", memory_game),
        "3": ("Крестики-нолики", tic_tac_toe),
        "4": ("Виселица", hangman),
        "5": ("21 очко", blackjack),
        "6": ("Морской бой", battleship),
        "7": ("Тетрис", tetris),
        "8": ("Судоку", sudoku),
        "9": ("Шахматы", chess),
        "10": ("Поле чудес", wheel_of_fortune),
        "0": ("Выход", None)
    }

    while True:
        clear_screen()
        print_header("Главное меню")
        
        for key in sorted(games.keys(), key=lambda x: int(x) if x != "0" else 999):
            name = games[key][0]
            color = Fore.CYAN if key != "0" else Fore.RED
            print(f"{color}{key.rjust(2)}. {name}")
        
        while True:
            choice = input(f"\n{Fore.YELLOW}Выбери игру (0-{len(games)-1}): ")
            if choice in games:
                clear_screen()
                games[choice][1]()
                break
            elif choice == "":
                continue
            else:
                print(Fore.RED + "Некорректный ввод!")
                time.sleep(1)
                break

if __name__ == "__main__":
    clear_screen()
    print(Fore.MAGENTA + "="*50)
    print(Fore.GREEN + "🌟 10 ЛУЧШИХ ИГР 🌟".center(50))
    print(Fore.MAGENTA + "="*50)
    print(f"{Fore.YELLOW}В любой момент введи 999 для выхода в меню\n")
    input(Fore.CYAN + "Нажми Enter чтобы начать...")
    main_menu()