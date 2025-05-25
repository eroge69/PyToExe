# Учебный макет кассовой системы для обучения кассиров на Python

import time
import random
from typing import Dict, List, Tuple


class Product:
    """Класс товара"""
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def __repr__(self):
        return f"{self.name}: {self.price:.2f}"


class Basket:
    """Корзина продуктов"""
    def __init__(self):
        self.items: List[Product] = []

    def add_product(self, product: Product):
        """Добавляет товар в корзину"""
        self.items.append(product)

    def total_price(self) -> float:
        """Вычисляет общую стоимость корзины"""
        return sum(item.price for item in self.items)

    def clear_basket(self):
        """Очищает корзину"""
        self.items.clear()


class CashierSystem:
    """Система кассира"""
    def __init__(self):
        self.basket = Basket()  # Корзина текущего заказа
        self.discount_percentage = 0  # Текущая скидка в процентах
        self.payment_methods = ["Наличные", "Банковская карта", "Оплата телефоном"]  # Способы оплаты

    def display_menu(self):
        """Отображает главное меню"""
        print("\n--- УЧЕБНАЯ КАССОВАЯ СИСТЕМА ---")
        print("1. Добавить товар в корзину")
        print("2. Посмотреть содержимое корзины")
        print("3. Применить скидку")
        print("4. Оформить покупку")
        print("5. Очистить корзину")
        print("6. Выход\n")

    def add_to_basket(self):
        """Меню добавления товаров в корзину"""
        products = [
            Product("Хлеб", 50),
            Product("Молоко", 70),
            Product("Сыр", 250),
            Product("Колбаса", 300),
            Product("Шоколад", 120),
        ]

        print("\nДоступные товары:")
        for idx, prod in enumerate(products, start=1):
            print(f"{idx}. {prod}")

        choice = int(input("Выберите товар (номер): "))
        if 1 <= choice <= len(products):
            selected_product = products[choice - 1]
            self.basket.add_product(selected_product)
            print(f"\nТовар '{selected_product.name}' добавлен в корзину.\n")
        else:
            print("\nНеверный выбор!\n")

    def view_basket(self):
        """Показывает содержимое корзины"""
        if not self.basket.items:
            print("\nКорзина пуста.\n")
        else:
            print("\nВаш заказ:\n")
            for i, item in enumerate(self.basket.items, start=1):
                print(f"{i}. {item}")
            print(f"Итого: {self.basket.total_price():.2f}\n")

    def apply_discount(self):
        """Применяет скидку"""
        discount = float(input("Введите процент скидки (%): "))
        if 0 <= discount <= 100:
            self.discount_percentage = discount / 100
            print(f"Скидка применена ({discount}%).\n")
        else:
            print("Недопустимый размер скидки.\n")

    def checkout(self):
        """Оформляет покупку"""
        total_amount = self.basket.total_price()
        discounted_total = total_amount * (1 - self.discount_percentage)
        print(f"\nОбщая сумма к оплате: {total_amount:.2f}, со скидкой: {discounted_total:.2f}")

        payment_method = None
        while payment_method not in range(len(self.payment_methods)):
            print("\nСпособы оплаты:")
            for idx, method in enumerate(self.payment_methods, start=1):
                print(f"{idx}. {method}")
            payment_choice = int(input("Выберите способ оплаты (номер): "))
            payment_method = payment_choice - 1

        print(f"\nСпособ оплаты выбран: {self.payment_methods[payment_method]}\n")
        print("Обрабатывается...")
        time.sleep(random.uniform(1, 3))  # Задержка для эффекта обработки

        print("Операция выполнена успешно!")
        self.basket.clear_basket()
        self.discount_percentage = 0

    def run(self):
        """Запуск основного цикла приложения"""
        while True:
            self.display_menu()
            action = input("Что будем делать? (1-6): ")

            if action == "1":
                self.add_to_basket()
            elif action == "2":
                self.view_basket()
            elif action == "3":
                self.apply_discount()
            elif action == "4":
                self.checkout()
            elif action == "5":
                self.basket.clear_basket()
                print("\nКорзина очищена.\n")
            elif action == "6":
                print("\nЗавершение работы... До свидания!")
                break
            else:
                print("\nНеправильный выбор команды. Попробуйте снова.\n")


if __name__ == "__main__":
    cashier_system = CashierSystem()
    cashier_system.run()