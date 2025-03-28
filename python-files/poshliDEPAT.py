import tkinter as tk
from tkinter import messagebox
import random
import copy

# Стандартна колода: ранги і масті
ranks = "23456789TJQKA"
suits = {"H": "♥", "D": "♦", "C": "♣", "S": "♠"}
deck_full = [r + s for r in ranks for s in suits.keys()]

# Глобальні списки для вибраних карт
selected_player = []  # карти гравця (мають бути 2)
selected_board = []   # карти на столі (0-5)

def toggle_card(card, selection_list, label):
    if card in selection_list:
        selection_list.remove(card)
    else:
        # Перевірка: для карт гравця – не більше 2, для столу – не більше 5
        if selection_list is selected_player and len(selection_list) >= 2:
            messagebox.showinfo("Інформація", "Можна вибрати рівно 2 карти для себе.")
            return
        if selection_list is selected_board and len(selection_list) >= 5:
            messagebox.showinfo("Інформація", "Можна вибрати максимум 5 карт для столу.")
            return
        selection_list.append(card)
    update_label(label, selection_list)

def update_label(label, selection_list):
    # Відображаємо карти з символами (наприклад, "A♠")
    text = ", ".join([c[0] + suits[c[1]] for c in selection_list])
    label.config(text=text)

def evaluate_hand(cards):
    # Простенька функція оцінки руки для симуляції.
    # У реальному застосунку слід використати бібліотеку для оцінки покерних рук.
    # Тут повертаємо суму індексів рангу (для демонстрації) плюс невелике випадкове відхилення.
    rank_value = {r: i for i, r in enumerate("23456789TJQKA", start=2)}
    score = sum([rank_value[c[0]] for c in cards]) + random.uniform(0, 1)
    return score

def simulate_equity(player_cards, board_cards, num_simulations=1000, num_opponents=1):
    deck = copy.deepcopy(deck_full)
    # Видаляємо вибрані карти з колоди
    for card in player_cards + board_cards:
        if card in deck:
            deck.remove(card)
    
    wins = 0
    total = 0
    for _ in range(num_simulations):
        sim_deck = copy.deepcopy(deck)
        random.shuffle(sim_deck)
        
        # Доповнюємо дошку до 5 карт
        board_needed = 5 - len(board_cards)
        sim_board = board_cards + sim_deck[:board_needed]
        sim_deck = sim_deck[board_needed:]
        
        # Для спрощення симулюємо лише одного супротивника з двома картами
        opp_cards = sim_deck[:2]
        
        # Оцінюємо силу рук (чим більше - тим сильніша рука)
        my_strength = evaluate_hand(player_cards + sim_board)
        opp_strength = evaluate_hand(opp_cards + sim_board)
        
        if my_strength >= opp_strength:
            wins += 1
        total += 1

    equity = wins / total * 100
    return equity

def recommend_action(equity):
    # Простий алгоритм для рекомендації:
    # Якщо equity >= 60% -> "Bet"
    # Якщо equity від 40% до 60% -> "Check/Call"
    # Якщо equity < 40% -> "Fold"
    if equity >= 60:
        return "Bet"
    elif equity >= 40:
        return "Check/Call"
    else:
        return "Fold"

def calculate():
    if len(selected_player) != 2:
        messagebox.showerror("Помилка", "Виберіть рівно 2 карти для себе.")
        return
    # board може бути 0-5 карт
    equity = simulate_equity(selected_player, selected_board, num_simulations=1000, num_opponents=1)
    action = recommend_action(equity)
    result_text = f"Ваш equity: {equity:.1f}%\nРекомендована дія: {action}"
    label_result.config(text=result_text)

# Створення основного вікна
root = tk.Tk()
root.title("Покерний аналітичний двигун")

# Фрейм для вибору карт гравця
frame_player = tk.LabelFrame(root, text="Ваші карти (оберіть 2)", padx=5, pady=5)
frame_player.pack(padx=10, pady=5, fill="x")
label_player_sel = tk.Label(frame_player, text="Немає вибраних", font=("Arial", 12))
label_player_sel.pack(pady=5)

# Фрейм для вибору карт на столі
frame_board = tk.LabelFrame(root, text="Карти на столі (0-5)", padx=5, pady=5)
frame_board.pack(padx=10, pady=5, fill="x")
label_board_sel = tk.Label(frame_board, text="Немає вибраних", font=("Arial", 12))
label_board_sel.pack(pady=5)

# Фрейм для карт (будемо відображати всі 52 карти як кнопки)
frame_cards = tk.Frame(root)
frame_cards.pack(padx=10, pady=5)

def create_card_buttons(selection_list, label):
    row = 0
    col = 0
    buttons = {}
    for card in deck_full:
        btn_text = card[0] + suits[card[1]]
        btn = tk.Button(frame_cards, text=btn_text, width=4,
                        command=lambda c=card: toggle_card(c, selection_list, label))
        btn.grid(row=row, column=col, padx=2, pady=2)
        buttons[card] = btn
        col += 1
        if col == 13:
            row += 1
            col = 0
    return buttons

# Створюємо кнопки. Ми використовуємо одну сітку для всіх карт;
# При кліку карта може бути додана як до вибору гравця або столу залежно від режиму.
# Тому для цього прикладу ми додамо окремі кнопки для кожного режиму.
# Для простоти зробимо: натискай по карті, і вона додається в обидва списки – але користувач повинен спочатку вибрати свій режим.
#
# Тому додамо перемикач режиму:
mode_var = tk.StringVar(value="player")  # "player" або "board"

frame_mode = tk.Frame(root)
frame_mode.pack(padx=10, pady=5)
tk.Label(frame_mode, text="Режим вибору:").pack(side="left")
tk.Radiobutton(frame_mode, text="Ваші карти", variable=mode_var, value="player").pack(side="left")
tk.Radiobutton(frame_mode, text="Карти на столі", variable=mode_var, value="board").pack(side="left")

def mode_toggle(card):
    mode = mode_var.get()
    if mode == "player":
        toggle_card(card, selected_player, label_player_sel)
    else:
        toggle_card(card, selected_board, label_board_sel)

# Оновимо функцію створення кнопок, щоб вона враховувала режим вибору:
def create_mode_buttons():
    row = 0
    col = 0
    for card in deck_full:
        btn_text = card[0] + suits[card[1]]
        btn = tk.Button(frame_cards, text=btn_text, width=4,
                        command=lambda c=card: mode_toggle(c))
        btn.grid(row=row, column=col, padx=2, pady=2)
        col += 1
        if col == 13:
            row += 1
            col = 0

create_mode_buttons()

# Кнопка для розрахунку equity та рекомендації
btn_calc = tk.Button(root, text="Розрахувати equity та рекомендацію", command=calculate, font=("Arial", 12))
btn_calc.pack(pady=10)

label_result = tk.Label(root, text="", font=("Arial", 14))
label_result.pack(pady=5)

root.mainloop()
