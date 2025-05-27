import random

class FunpaySellerGame:
    def __init__(self):
        self.orders = 5
        self.max_orders = 5
        self.health = 100
        self.stars = 5.0
        self.money = 1000
        self.mood = 100
        self.food = 3
        self.energy_drink = 2
        self.ban_turns = 0
        self.upgrades = {
            "twin_acc": False,
            "secret_scheme": False,
            "guild": False,
            "schoolboy_worker": False
        }

    def show_status(self):
        print(f"\nЗаказы: {self.orders}/{self.max_orders}, Деньги: {self.money}₽, Здоровье: {self.health}, Звёзды: {self.stars}, Настроение: {self.mood}")
        print(f"Еда: {self.food}, Энергетики: {self.energy_drink}")
        print("Апгрейды:", ', '.join([self.upgrade_name(k) for k, v in self.upgrades.items() if v]) or "нет")

    def upgrade_name(self, key):
        names = {
            "twin_acc": "Второй аккаунт-твинк",
            "secret_scheme": "Приватная схема",
            "guild": "🌸LOGOVO NYASHEK🌸",
            "schoolboy_worker": "Школьник на подработке"
        }
        return names.get(key, key)

    def do_order(self):
        if self.orders <= 0:
            print("\nНет доступных заказов!")
            return
        print("\nВы выполняете заказ...")
        base_success = 0.8
        if self.upgrades["guild"]:
            base_success += 0.1
        success = random.random() < base_success
        profit = random.randint(200, 600)
        if self.upgrades["secret_scheme"]:
            profit = int(profit * 1.5)
        if success:
            self.money += profit
            self.orders -= 1
            self.mood = min(100, self.mood + 5)
            print(f"Заказ успешно выполнен! +{profit}₽, +5 к настроению.")
        else:
            self.stars -= 0.5
            self.mood -= 20
            print("Заказ провален! -0.5⭐, -20 к настроению.")

    def schoolboy_worker_action(self):
        if not self.upgrades["schoolboy_worker"]:
            print("У вас нет школьника на подработке.")
            return
        if self.orders <= 0:
            print("Нет заказов для выполнения!")
            return
        print("\nШкольник пытается выполнить заказ за вас...")
        # 50% успеха, иначе плохой отзыв
        if random.random() < 0.5:
            profit = random.randint(100, 300)
            self.money += profit
            self.orders -= 1
            print(f"Школьник справился! +{profit}₽")
        else:
            self.stars = max(1.0, self.stars - 1)
            self.orders -= 1
            self.mood -= 25
            print("Школьник всё испортил! -1⭐, -25 к настроению.")

    def eat(self):
        if self.food > 0:
            self.food -= 1
            self.health = min(100, self.health + 15)
            print("Вы поели! +15 к здоровью.")
        else:
            print("Нет еды!")

    def drink_energy(self):
        if self.energy_drink > 0:
            self.energy_drink -= 1
            self.mood = min(100, self.mood + 15)
            print("Вы выпили энергетик! +15 к настроению.")
        else:
            print("Нет энергетиков!")

    def buy_supplies(self):
        print("\n=== Магазин ===")
        print("1. Купить еду (50₽)")
        print("2. Купить энергетик (70₽)")
        print("0. Выйти из магазина")
        choice = input("Выберите действие: ")
        if choice == '1' and self.money >= 50:
            self.money -= 50
            self.food += 1
            print("Купили еду.")
        elif choice == '2' and self.money >= 70:
            self.money -= 70
            self.energy_drink += 1
            print("Купили энергетик.")
        elif choice == '0':
            print("Выход из магазина.")
        else:
            print("Недостаточно денег или неверный выбор.")

    def buy_upgrade(self):
        print("\n=== Магазин апгрейдов ===")
        print("1. Второй аккаунт-твинк (700₽) — +5 к макс. заказам")
        print("2. Узнать приватную схему (1200₽) — +50% к прибыли")
        print("3. Инвайт в 🌸LOGOVO NYASHEK🌸 (2000₽) — +10% к успеху заказов, открывает новые схемы")
        print("4. Нанять школьника на заказы (800₽) — школьник может выполнять заказы за вас (но иногда фейлит)")
        print("0. Выйти из магазина")
        choice = input("Выберите апгрейд (1-4, 0): ")
        if choice == '1' and not self.upgrades["twin_acc"] and self.money >= 700:
            self.money -= 700
            self.upgrades["twin_acc"] = True
            self.max_orders += 5
            self.orders += 5
            print("Второй аккаунт создан! Больше заказов!")
        elif choice == '2' and not self.upgrades["secret_scheme"] and self.money >= 1200:
            self.money -= 1200
            self.upgrades["secret_scheme"] = True
            print("Вы узнали приватную схему доната!")
        elif choice == '3' and not self.upgrades["guild"] and self.money >= 2000:
            self.money -= 2000
            self.upgrades["guild"] = True
            print("Вас приняли в 🌸LOGOVO NYASHEK🌸!")
        elif choice == '4' and not self.upgrades["schoolboy_worker"] and self.money >= 800:
            self.money -= 800
            self.upgrades["schoolboy_worker"] = True
            print("Вы наняли школьника на подработку!")
        elif choice == '0':
            print("Выход из магазина.")
        else:
            print("Нельзя купить этот апгрейд (недостаточно денег или уже куплен).")

    def random_event(self):
        events = []
        if self.upgrades["guild"]:
            events += [
                {"desc": "В чате 🌸LOGOVO NYASHEK🌸 Take the profit кидает левые фьючерсы от GromTrade. Минус настроение.", "mood": -20},
                {"desc": "Егор из 🌸LOGOVO NYASHEK🌸 пишет: 'я ебал твою мать'. Минус настроение.", "mood": -25},
                {"desc": "Killerok сделал дохуя заказов — минус настроение.", "mood": -15},
            ]
        # Абсурдные и дебильные события
        events += [
            {"desc": "Школьник оставил жалобу. Вас забанили на 1 ход!", "ban": 1},
            {"desc": "Вы забыли поесть, стало плохо. -15 к здоровью.", "health": -15},
            {"desc": "Вы забыли выпить энергетик, настроение упало. -15 к настроению.", "mood": -15},
            {"desc": "Внезапно на ваш аккаунт подписался дед-наркоман. Он требует скидку. Минус настроение.", "mood": -10},
            {"desc": "Ваша кошка пробежала по клавиатуре и отправила клиенту мат. Минус звезда.", "stars": -1},
            {"desc": "Вас добавили в чат с названием “Куплю гараж”. Потеряно 100₽ на вступительный взнос.", "money": -100},
            {"desc": "Вам позвонил мошенник и предложил купить биткоин за скины. Минус 200₽.", "money": -200},
            {"desc": "Вы случайно отправили свой паспорт школьнику. Минус настроение и деньги.", "mood": -10, "money": -150},
            {"desc": "Ваш второй аккаунт начал спорить с основным в чате. Все в шоке. Минус настроение.", "mood": -15},
            {"desc": "Вам пришёл заказ от бота, который требует “ПИВАНДРИК”. Минус 15 к настроению.", "mood": -15},
            {"desc": "Ваша бабушка нашла ваши переписки и решила сама выполнить заказ. Минус 1 заказ, минус 10 к здоровью.", "orders": -1, "health": -10},
            {"desc": "На улице начался дождь из энергетиков. +1 энергетик, но вы промокли — минус здоровье.", "energy_drink": +1, "health": -10},
            {"desc": "В чат зашел школьник с ником “Мамкин трейдер” и начал всех учить жизни. Минус настроение.", "mood": -12},
        ]
        if events and random.random() < 0.35:
            event = random.choice(events)
            print("\nСобытие! " + event["desc"])
            if "mood" in event:
                self.mood = max(0, self.mood + event["mood"])
            if "health" in event:
                self.health = max(0, self.health + event["health"])
            if "ban" in event:
                self.ban_turns = event["ban"]
            if "money" in event:
                self.money = max(0, self.money + event["money"])
            if "stars" in event:
                self.stars = max(1.0, self.stars + event["stars"])
            if "orders" in event:
                self.orders = max(0, self.orders + event["orders"])
            if "energy_drink" in event:
                self.energy_drink = max(0, self.energy_drink + event["energy_drink"])

    def next_turn(self):
        # Потребность поесть и выпить энергетик каждые 2 хода
        if random.random() < 0.5:
            if self.food > 0:
                self.food -= 1
                print("Вы поели в перерыве.")
            else:
                print("Вы голодны! -10 к здоровью.")
                self.health -= 10
            if self.energy_drink > 0:
                self.energy_drink -= 1
                print("Вы выпили энергетик в перерыве.")
            else:
                print("Вы без энергетика! -10 к настроению.")
                self.mood -= 10

    def play(self):
        print("=== Игра: Продавец FunPay и глупые школьники (апгрейды & негативные события) ===")
        while self.orders > 0 and self.health > 0 and self.stars > 1.0 and self.mood > 0:
            if self.ban_turns > 0:
                print(f"\nВы забанены! Пропуск хода. Осталось ходов бана: {self.ban_turns}")
                self.ban_turns -= 1
                self.next_turn()
                continue

            self.show_status()
            print("\nВаши действия:")
            print("1. Выполнить заказ")
            if self.upgrades["schoolboy_worker"]:
                print("2. Поручить заказ школьнику")
                print("3. Купить еду/энергетик")
                print("4. Магазин апгрейдов")
                print("5. Поесть")
                print("6. Выпить энергетик")
                choice = input("Выберите действие (1-6): ")
            else:
                print("2. Купить еду/энергетик")
                print("3. Магазин апгрейдов")
                print("4. Поесть")
                print("5. Выпить энергетик")
                choice = input("Выберите действие (1-5): ")

            if choice == '1':
                self.do_order()
            elif choice == '2' and self.upgrades["schoolboy_worker"]:
                self.schoolboy_worker_action()
            elif (choice == '2' and not self.upgrades["schoolboy_worker"]) or (choice == '3' and self.upgrades["schoolboy_worker"]):
                self.buy_supplies()
            elif (choice == '3' and not self.upgrades["schoolboy_worker"]) or (choice == '4' and self.upgrades["schoolboy_worker"]):
                self.buy_upgrade()
            elif (choice == '4' and not self.upgrades["schoolboy_worker"]) or (choice == '5' and self.upgrades["schoolboy_worker"]):
                self.eat()
            elif (choice == '5' and not self.upgrades["schoolboy_worker"]) or (choice == '6' and self.upgrades["schoolboy_worker"]):
                self.drink_energy()
            else:
                print("Неверный выбор!")

            self.random_event()
            self.next_turn()

        print("\n=== Конец игры ===")
        if self.stars <= 1.0:
            print("Вас завалили единицами. Продавец в депрессии :(")
        elif self.health <= 0:
            print("Вы умерли от голода/нервов.")
        elif self.mood <= 0:
            print("Настроение на нуле. Продавец ушёл отдыхать.")
        elif self.orders == 0:
            print("Все заказы выполнены! Успех! Ваш баланс:", self.money, "₽")
        else:
            print("Игра завершена.")

if __name__ == "__main__":
    game = FunpaySellerGame()
    game.play()