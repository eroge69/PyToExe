class BankAccount:
    def __init__(self, card_number, pin_code, initial_balance=0):
        self.card_number = card_number      # номер карты
        self.pin_code = pin_code            # ПИН-код
        self.balance = initial_balance      # баланс счета
    
    def authenticate(self, entered_card, entered_pin):
        """Метод проверки подлинности данных."""
        return (entered_card == self.card_number and entered_pin == self.pin_code)
    
    def check_balance(self):
        """Возвращает текущий баланс."""
        return f"Текущий баланс: {self.balance:.2f} руб."
    
    def withdraw(self, amount):
        """Операция снятия наличных."""
        if amount > self.balance:
            return "Недостаточно средств."
        else:
            self.balance -= amount
            return f"Сняли {amount:.2f} руб., остаток: {self.balance:.2f} руб."
    
    def deposit(self, amount):
        """Операция внесения наличных."""
        self.balance += amount
        return f"Внесли {amount:.2f} руб., новый баланс: {self.balance:.2f} руб."

def main():
    # Тестовые данные аккаунта
    account = BankAccount('2020254616423416', '45663', 350000)
    
    print("Добро пожаловать в виртуальный банкомат!")
    
    # Вход в систему
    for _ in range(3):
        card_input = input("Введите номер карты: ")
        pin_input = input("Введите PIN-код: ")
        
        if account.authenticate(card_input, pin_input):
            print("Доступ разрешен!")
            break
        else:
            print("Неверный номер карты или PIN-код. Попробуйте ещё раз.")
    else:
        print("Превышено максимальное количество попыток входа.")
        return
    
    # Меню действий после успешной авторизации
    while True:
        print("\nЧто хотите сделать?")
        print("1. Проверить баланс")
        print("2. Снять деньги")
        print("3. Положить деньги")
        print("4. Выход")
        
        action = input("Выберите действие (1-4): ")
        
        if action == '1':
            print(account.check_balance())
        elif action == '2':
            try:
                amount = float(input("Введите сумму снятия: "))
                print(account.withdraw(amount))
            except ValueError:
                print("Ошибка! Введены некорректные данные.")
        elif action == '3':
            try:
                amount = float(input("Введите сумму взноса: "))
                print(account.deposit(amount))
            except ValueError:
                print("Ошибка! Введены некорректные данные.")
        elif action == '4':
            print("Приятного дня! До встречи!")
            break
        else:
            print("Невалидный выбор. Выберите один из предложенных вариантов.")

if __name__ == "__main__":
    main()