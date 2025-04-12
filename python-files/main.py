import tkinter as tk
import random

class RPGGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Epic 2D RPG")

        # Статы игрока
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.defense = 5
        self.gold = 50
        self.location = "Деревня"
        self.weapon = "Кулаки"
        self.armor = "Тряпичная рубаха"
        self.state = "normal"  # normal, dungeon, battle
        self.floor = 1  # этаж в данже
        self.monster = None
        
        # Интерфейс
        self.text = tk.Label(master, text="Добро пожаловать в игру!", font=("Arial", 14))
        self.text.pack(pady=10)

        self.buttons_frame = tk.Frame(master)
        self.buttons_frame.pack()

        self.buttons = {}
        self.create_main_buttons()

    def create_main_buttons(self):
        self.clear_buttons()
        self.buttons["explore"] = tk.Button(self.buttons_frame, text="🗺️ Исследовать", command=self.explore)
        self.buttons["shop"] = tk.Button(self.buttons_frame, text="🏪 Магазин", command=self.shop)
        self.buttons["dungeon"] = tk.Button(self.buttons_frame, text="🏰 Данж", command=self.enter_dungeon)
        self.buttons["inventory"] = tk.Button(self.buttons_frame, text="🎒 Инвентарь", command=self.show_inventory)
        self.buttons["heal"] = tk.Button(self.buttons_frame, text="💖 Лечиться", command=self.heal)
        self.buttons["status"] = tk.Button(self.buttons_frame, text="📜 Статус", command=self.show_status)

        for btn in self.buttons.values():
            btn.pack(pady=2)

    def clear_buttons(self):
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        self.buttons.clear()

    def explore(self):
        self.text.config(text="Вы исследуете окрестности...")
        event = random.choice(["ничего", "монстр", "сундук"])
        if event == "монстр":
            self.start_battle()
        elif event == "сундук":
            gold_found = random.randint(10, 50)
            self.gold += gold_found
            self.text.config(text=f"Вы нашли сундук с {gold_found} золотыми монетами!")
        else:
            self.text.config(text="Вы ничего не нашли.")

    def shop(self):
        self.text.config(text="Добро пожаловать в магазин!")
        self.clear_buttons()
        self.buttons["sword"] = tk.Button(self.buttons_frame, text="🗡️ Меч (30 золота)", command=lambda: self.buy_item("sword"))
        self.buttons["armor"] = tk.Button(self.buttons_frame, text="🛡️ Броня (40 золота)", command=lambda: self.buy_item("armor"))
        self.buttons["back"] = tk.Button(self.buttons_frame, text="⬅️ Назад", command=self.create_main_buttons)
        for btn in self.buttons.values():
            btn.pack(pady=2)

    def buy_item(self, item):
        if item == "sword" and self.gold >= 30:
            self.weapon = "Стальной меч"
            self.attack += 10
            self.gold -= 30
            self.text.config(text="Вы купили Стальной меч!")
        elif item == "armor" and self.gold >= 40:
            self.armor = "Стальная броня"
            self.defense += 10
            self.gold -= 40
            self.text.config(text="Вы купили Стальную броню!")
        else:
            self.text.config(text="Недостаточно золота!")
        self.create_main_buttons()

    def enter_dungeon(self):
        self.state = "dungeon"
        self.floor = 1
        self.text.config(text="Вы вошли в данж! Этаж 1")
        self.dungeon_menu()

    def dungeon_menu(self):
        self.clear_buttons()
        self.buttons["continue"] = tk.Button(self.buttons_frame, text="⚔️ Продолжить бой", command=self.start_battle)
        self.buttons["inventory"] = tk.Button(self.buttons_frame, text="🎒 Инвентарь", command=self.show_inventory)
        self.buttons["heal"] = tk.Button(self.buttons_frame, text="💖 Лечиться", command=self.heal)
        self.buttons["status"] = tk.Button(self.buttons_frame, text="📜 Статус", command=self.show_status)
        for btn in self.buttons.values():
            btn.pack(pady=2)

    def start_battle(self):
        self.state = "battle"
        monsters = ["Гоблин", "Орк", "Слизень", "Скелет"]
        boss = "Демон-босс" if self.floor == 3 else None
        self.monster = boss if boss else random.choice(monsters)
        monster_hp = 30 + (self.floor * 10)
        self.monster_hp = monster_hp
        self.text.config(text=f"На вас напал {self.monster} (HP: {self.monster_hp})!")
        self.battle_menu()

    def battle_menu(self):
        self.clear_buttons()
        self.buttons["attack"] = tk.Button(self.buttons_frame, text="⚔️ Атаковать", command=self.attack_monster)
        self.buttons["inventory"] = tk.Button(self.buttons_frame, text="🎒 Инвентарь", command=self.show_inventory)
        self.buttons["heal"] = tk.Button(self.buttons_frame, text="💖 Лечиться", command=self.heal)
        self.buttons["status"] = tk.Button(self.buttons_frame, text="📜 Статус", command=self.show_status)
        for btn in self.buttons.values():
            btn.pack(pady=2)

    def attack_monster(self):
        damage = max(self.attack - random.randint(0, 5), 0)
        self.monster_hp -= damage
        if self.monster_hp <= 0:
            self.text.config(text=f"Вы победили {self.monster}!")
            loot = random.randint(20, 60)
            self.gold += loot
            self.floor += 1
            if self.floor > 3:
                self.state = "normal"
                self.text.config(text="Вы зачистили данж! 🏆")
                self.create_main_buttons()
            else:
                self.state = "dungeon"
                self.text.config(text=f"Вы поднялись на этаж {self.floor}!")
                self.dungeon_menu()
        else:
            self.monster_attack()

    def monster_attack(self):
        damage = max(5 - self.defense // 4, 1)
        self.hp -= damage
        if self.hp <= 0:
            self.text.config(text="Вы погибли... Игра окончена.")
            self.clear_buttons()
        else:
            self.text.config(text=f"{self.monster} ударил вас на {damage} урона!\nВаше HP: {self.hp}")
            self.battle_menu()

    def heal(self):
        if self.hp < self.max_hp:
            heal_amount = random.randint(10, 20)
            self.hp = min(self.max_hp, self.hp + heal_amount)
            self.text.config(text=f"Вы восстановили {heal_amount} HP! (Текущее HP: {self.hp})")
        else:
            self.text.config(text="Ваше здоровье уже полное.")

    def show_inventory(self):
        self.text.config(text=f"Оружие: {self.weapon}\nБроня: {self.armor}\nЗолото: {self.gold}")

    def show_status(self):
        self.text.config(text=f"HP: {self.hp}/{self.max_hp}\nАтака: {self.attack}\nЗащита: {self.defense}")

root = tk.Tk()
game = RPGGame(root)
root.mainloop()
