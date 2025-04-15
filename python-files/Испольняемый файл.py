import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, font, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib

# Получаем путь к рабочему столу
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

@dataclass
class User:
    username: str
    password_hash: str
    is_admin: bool = False

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        return self.password_hash == self.hash_password(password)

class Auth:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        self.load_users()

        # Create admin user if no users exist
        if not self.users:
            self.register_user("admin", "admin", True)

    def load_users(self):
        try:
            with open('users.json', 'r') as f:
                users_data = json.load(f)
                self.users = {
                    username: User(username, data['password_hash'], data['is_admin'])
                    for username, data in users_data.items()
                }
        except FileNotFoundError:
            self.users = {}

    def save_users(self):
        users_data = {
            username: {
                'password_hash': user.password_hash,
                'is_admin': user.is_admin
            }
            for username, user in self.users.items()
        }
        with open('users.json', 'w') as f:
            json.dump(users_data, f)

    def register_user(self, username: str, password: str, is_admin: bool = False) -> bool:
        if username in self.users:
            return False
        
        self.users[username] = User(
            username=username,
            password_hash=User.hash_password(password),
            is_admin=is_admin
        )
        self.save_users()
        return True

    def login(self, username: str, password: str) -> bool:
        user = self.users.get(username)
        if user and user.check_password(password):
            self.current_user = user
            return True
        return False

    def is_admin(self) -> bool:
        return self.current_user is not None and self.current_user.is_admin

    def logout(self):
        self.current_user = None

@dataclass
class Product:
    id: int
    название: str
    цена: float
    категория: str
    продавец: str

    def __str__(self) -> str:
        return f"{self.название} - {self.цена} руб. (Продавец: {self.продавец})"

    def __hash__(self) -> int:
        return hash(self.id)  # Используем id как уникальный идентификатор для хеширования
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Product):
            return False
        return self.id == other.id  # Сравниваем товары по их id


class Cart:
    def __init__(self):
        self.__items: Dict[Product, int] = {}

    def добавить_товар(self, product: Product, количество: int = 1) -> None:
        self.__items[product] = self.__items.get(product, 0) + количество

    def удалить_товар(self, product: Product, количество: int = 1) -> None:
        if product in self.__items:
            self.__items[product] = max(0, self.__items[product] - количество)
            if self.__items[product] == 0:
                del self.__items[product]

    def очистить(self) -> None:
        self.__items.clear()

    def получить_сумму(self) -> float:
        return sum(product.цена * quantity for product, quantity in self.__items.items())

    def получить_товары(self) -> Dict[Product, int]:
        return self.__items.copy()

    def __str__(self) -> str:
        if not self.__items:
            return "Корзина пуста"
        items_str = "\n".join(f"{p.название} x{q} = {p.цена * q} руб." for p, q in self.__items.items())
        return f"Корзина:\n{items_str}\n\nИтого: {self.получить_сумму()} руб."


@dataclass
class Order:
    id: int
    товары: Dict[Product, int]
    дата: str
    
    @property
    def сумма(self) -> float:
        return sum(p.цена * q for p, q in self.товары.items())

    def __str__(self) -> str:
        result = f"Заказ #{self.id} от {self.дата}\n"
        for product, quantity in self.товары.items():
            result += f"{product.название} x{quantity} = {product.цена * quantity} руб.\n"
        result += f"\nИтого: {self.сумма} руб."
        return result


class Store:
    def __init__(self):
        self.__products: List[Product] = []
        self.__orders: List[Order] = []
        self.__next_order_id = 1
        self.__load_catalog()
        self.__load_orders()  # Загружаем историю заказов при инициализации

    def __load_catalog(self) -> None:
        # Создаем каталог из 100 товаров
        products_data = [
            # Электроника (25 товаров)
            {"id": 1, "название": "Смартфон Samsung Galaxy A54", "цена": 34999, "категория": "Электроника", "продавец": "DNS"},
            {"id": 2, "название": "Ноутбук ASUS VivoBook", "цена": 49999, "категория": "Электроника", "продавец": "М.Видео"},
            {"id": 3, "название": "Планшет iPad Air", "цена": 54999, "категория": "Электроника", "продавец": "DNS"},
            {"id": 4, "название": "Наушники Sony WH-1000XM4", "цена": 27999, "категория": "Электроника", "продавец": "М.Видео"},
            {"id": 5, "название": "Умные часы Apple Watch SE", "цена": 24999, "категория": "Электроника", "продавец": "DNS"},
            {"id": 6, "название": "Фотоаппарат Canon EOS M50", "цена": 49999, "категория": "Электроника", "продавец": "М.Видео"},
            {"id": 7, "название": "Игровая приставка PS5", "цена": 49999, "категория": "Электроника", "продавец": "DNS"},
            {"id": 8, "название": "Телевизор LG OLED C1", "цена": 89999, "категория": "Электроника", "продавец": "М.Видео"},
            {"id": 9, "название": "Монитор Samsung Odyssey G5", "цена": 29999, "категория": "Электроника", "продавец": "DNS"},
            {"id": 10, "название": "Видеокарта RTX 3060", "цена": 39999, "категория": "Электроника", "продавец": "М.Видео"},
            {"id": 11, "название": "Процессор Intel i5-12400F", "цена": 19999, "категория": "Электроника", "продавец": "DNS"},
            {"id": 12, "название": "Роутер ASUS RT-AX82U", "цена": 14999, "категория": "Электроника", "продавец": "М.Видео"},
            {"id": 13, "название": "Принтер HP LaserJet", "цена": 19999, "категория": "Электроника", "продавец": "DNS"},
            {"id": 14, "название": "Квадрокоптер DJI Mini 2", "цена": 44999, "категория": "Электроника", "продавец": "М.Видео"},
            {"id": 15, "название": "Электронная книга Kindle", "цена": 9999, "категория": "Электроника", "продавец": "DNS"},
            {"id": 16, "название": "Веб-камера Logitech C920", "цена": 7999, "категория": "Электроника", "продавец": "М.Видео"},
            {"id": 17, "название": "Клавиатура Corsair K70", "цена": 12999, "категория": "Электроника", "продавец": "DNS"},
            {"id": 18, "название": "Мышь Logitech G Pro X", "цена": 8999, "категория": "Электроника", "продавец": "М.Видео"},
            {"id": 19, "название": "Колонки JBL Charge 5", "цена": 11999, "категория": "Электроника", "продавец": "DNS"},
            {"id": 20, "название": "Сканер Epson V600", "цена": 34999, "категория": "Электроника", "продавец": "М.Видео"},
            {"id": 21, "название": "Графический планшет Wacom", "цена": 29999, "категория": "Электроника", "продавец": "DNS"},
            {"id": 22, "название": "Внешний SSD Samsung T7", "цена": 9999, "категория": "Электроника", "продавец": "М.Видео"},
            {"id": 23, "название": "Проектор BenQ TH685", "цена": 69999, "категория": "Электроника", "продавец": "DNS"},
            {"id": 24, "название": "Микрофон Blue Yeti", "цена": 12999, "категория": "Электроника", "продавец": "М.Видео"},
            {"id": 25, "название": "Смарт-часы Garmin Venu", "цена": 34999, "категория": "Электроника", "продавец": "DNS"},

            # Книги (20 товаров)
            {"id": 26, "название": "Книга 'Мастер и Маргарита'", "цена": 799, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 27, "название": "Книга 'Война и мир'", "цена": 999, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 28, "название": "Книга 'Преступление и наказание'", "цена": 699, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 29, "название": "Книга '1984'", "цена": 799, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 30, "название": "Книга 'Гарри Поттер' (комплект)", "цена": 4999, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 31, "название": "Книга 'Властелин колец'", "цена": 1299, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 32, "название": "Книга 'Маленький принц'", "цена": 499, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 33, "название": "Книга 'Три товарища'", "цена": 799, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 34, "название": "Книга 'Портрет Дориана Грея'", "цена": 699, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 35, "название": "Книга 'Идиот'", "цена": 799, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 36, "название": "Книга 'Анна Каренина'", "цена": 899, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 37, "название": "Книга 'Герой нашего времени'", "цена": 599, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 38, "название": "Книга 'Евгений Онегин'", "цена": 499, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 39, "название": "Книга 'Мёртвые души'", "цена": 699, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 40, "название": "Книга 'Отцы и дети'", "цена": 599, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 41, "название": "Книга 'Собачье сердце'", "цена": 599, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 42, "название": "Книга 'Капитанская дочка'", "цена": 499, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 43, "название": "Книга 'Ревизор'", "цена": 449, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 44, "название": "Книга 'Горе от ума'", "цена": 499, "категория": "Книги", "продавец": "Читай-город"},
            {"id": 45, "название": "Книга 'Вишнёвый сад'", "цена": 449, "категория": "Книги", "продавец": "Читай-город"},

            # Бытовая техника (20 товаров)
            {"id": 46, "название": "Чайник электрический Bosch", "цена": 2999, "категория": "Бытовая техника", "продавец": "М.Видео"},
            {"id": 47, "название": "Микроволновая печь Samsung", "цена": 8999, "категория": "Бытовая техника", "продавец": "DNS"},
            {"id": 48, "название": "Холодильник LG", "цена": 49999, "категория": "Бытовая техника", "продавец": "М.Видео"},
            {"id": 49, "название": "Стиральная машина Bosch", "цена": 34999, "категория": "Бытовая техника", "продавец": "DNS"},
            {"id": 50, "название": "Пылесос Dyson V8", "цена": 29999, "категория": "Бытовая техника", "продавец": "М.Видео"},
            {"id": 51, "название": "Мультиварка Philips", "цена": 7999, "категория": "Бытовая техника", "продавец": "DNS"},
            {"id": 52, "название": "Блендер Braun", "цена": 4999, "категория": "Бытовая техника", "продавец": "М.Видео"},
            {"id": 53, "название": "Кофеварка DeLonghi", "цена": 12999, "категория": "Бытовая техника", "продавец": "DNS"},
            {"id": 54, "название": "Утюг Philips", "цена": 3999, "категория": "Бытовая техника", "продавец": "М.Видео"},
            {"id": 55, "название": "Посудомоечная машина Bosch", "цена": 39999, "категория": "Бытовая техника", "продавец": "DNS"},
            {"id": 56, "название": "Вытяжка Elica", "цена": 19999, "категория": "Бытовая техника", "продавец": "М.Видео"},
            {"id": 57, "название": "Варочная панель Electrolux", "цена": 24999, "категория": "Бытовая техника", "продавец": "DNS"},
            {"id": 58, "название": "Духовой шкаф Siemens", "цена": 44999, "категория": "Бытовая техника", "продавец": "М.Видео"},
            {"id": 59, "название": "Измельчитель Bosch", "цена": 2999, "категория": "Бытовая техника", "продавец": "DNS"},
            {"id": 60, "название": "Тостер Smeg", "цена": 15999, "категория": "Бытовая техника", "продавец": "М.Видео"},
            {"id": 61, "название": "Миксер KitchenAid", "цена": 29999, "категория": "Бытовая техника", "продавец": "DNS"},
            {"id": 62, "название": "Мясорубка Moulinex", "цена": 8999, "категория": "Бытовая техника", "продавец": "М.Видео"},
            {"id": 63, "название": "Соковыжималка Hurom", "цена": 19999, "категория": "Бытовая техника", "продавец": "DNS"},
            {"id": 64, "название": "Сушилка для овощей", "цена": 4999, "категория": "Бытовая техника", "продавец": "М.Видео"},
            {"id": 65, "название": "Йогуртница Tefal", "цена": 3999, "категория": "Бытовая техника", "продавец": "DNS"},

            # Одежда (20 товаров)
            {"id": 66, "название": "Футболка хлопковая", "цена": 999, "категория": "Одежда", "продавец": "ZARA"},
            {"id": 67, "название": "Джинсы", "цена": 5999, "категория": "Одежда", "продавец": "ZARA"},
            {"id": 68, "название": "Куртка зимняя", "цена": 12999, "категория": "Одежда", "продавец": "DUB"},
            {"id": 69, "название": "Свитер шерстяной", "цена": 3999, "категория": "Одежда", "продавец": "DUB"},
            {"id": 70, "название": "Рубашка классическая", "цена": 2999, "категория": "Одежда", "продавец": "ZARA"},
            {"id": 71, "название": "Платье вечернее", "цена": 7999, "категория": "Одежда", "продавец": "DUB"},
            {"id": 72, "название": "Пальто демисезонное", "цена": 15999, "категория": "Одежда", "продавец": "ZARA"},
            {"id": 73, "название": "Костюм деловой", "цена": 19999, "категория": "Одежда", "продавец": "DUB"},
            {"id": 74, "название": "Юбка джинсовая", "цена": 2999, "категория": "Одежда", "продавец": "ZARA"},
            {"id": 75, "название": "Шорты спортивные", "цена": 1999, "категория": "Одежда", "продавец": "DUB"},
            {"id": 76, "название": "Пижама хлопковая", "цена": 2499, "категория": "Одежда", "продавец": "ZARA"},
            {"id": 77, "название": "Носки (набор 5 пар)", "цена": 799, "категория": "Одежда", "продавец": "DUB"},
            {"id": 78, "название": "Перчатки кожаные", "цена": 1999, "категория": "Одежда", "продавец": "ZARA"},
            {"id": 79, "название": "Шапка зимняя", "цена": 1499, "категория": "Одежда", "продавец": "DUB"},
            {"id": 80, "название": "Купальник", "цена": 2999, "категория": "Одежда", "продавец": "ZARA"},
            {"id": 81, "название": "Кроссовки", "цена": 7999, "категория": "Одежда", "продавец": "DUB"},
            {"id": 82, "название": "Ботинки зимние", "цена": 6999, "категория": "Одежда", "продавец": "ZARA"},
            {"id": 83, "название": "Сандалии летние", "цена": 2499, "категория": "Одежда", "продавец": "DUB"},
            {"id": 84, "название": "Туфли классические", "цена": 4999, "категория": "Одежда", "продавец": "ZARA"},
            {"id": 85, "название": "Шарф шерстяной", "цена": 1999, "категория": "Одежда", "продавец": "DUB"},

            # Продукты питания (15 товаров)
            {"id": 86, "название": "Чай зеленый (100 пак.)", "цена": 299, "категория": "Продукты", "продавец": "Пятёрочка"},
            {"id": 87, "название": "Кофе в зернах (1 кг)", "цена": 999, "категория": "Продукты", "продавец": "Перекрёсток"},
            {"id": 88, "название": "Шоколад горький", "цена": 199, "категория": "Продукты", "продавец": "Пятёрочка"},
            {"id": 89, "название": "Печенье сдобное", "цена": 149, "категория": "Продукты", "продавец": "Пятёрочка"},
            {"id": 90, "название": "Мед натуральный", "цена": 599, "категория": "Продукты", "продавец": "Перекрёсток"},
            {"id": 91, "название": "Орехи ассорти", "цена": 799, "категория": "Продукты", "продавец": "Перекрёсток"},
            {"id": 92, "название": "Оливковое масло", "цена": 699, "категория": "Продукты", "продавец": "Пятёрочка"},
            {"id": 93, "название": "Макароны (упаковка)", "цена": 129, "категория": "Продукты", "продавец": "Пятёрочка"},
            {"id": 94, "название": "Рис басмати", "цена": 199, "категория": "Продукты", "продавец": "Перекрёсток"},
            {"id": 95, "название": "Соус соевый", "цена": 159, "категория": "Продукты", "продавец": "Пятёрочка"},
            {"id": 96, "название": "Специи набор", "цена": 399, "категория": "Продукты", "продавец": "Перекрёсток"},
            {"id": 97, "название": "Сухофрукты микс", "цена": 299, "категория": "Продукты", "продавец": "Пятёрочка"},
            {"id": 98, "название": "Варенье клубничное", "цена": 249, "категория": "Продукты", "продавец": "Пятёрочка"},
            {"id": 99, "название": "Мюсли с орехами", "цена": 279, "категория": "Продукты", "продавец": "Перекрёсток"},
            {"id": 100, "название": "Чипсы картофельные", "цена": 129, "категория": "Продукты", "продавец": "Пятёрочка"}
        ]
        
        self.__products = [
            Product(p["id"], p["название"], p["цена"], p["категория"], p["продавец"]) 
            for p in products_data
        ]

    def получить_все_товары(self) -> List[Product]:
        return self.__products.copy()

    def получить_товары_по_категории(self, категория: str) -> List[Product]:
        return [p for p in self.__products if p.категория == категория]

    def найти_товар_по_id(self, id: int) -> Product:
        """Находит товар по его ID"""
        for product in self.__products:
            if product.id == id:
                return product
        raise ValueError(f"Товар с ID {id} не найден")

    def получить_категории(self) -> List[str]:
        return list(set(p.категория for p in self.__products))

    def получить_все_заказы(self) -> List[Order]:
        """Возвращает список всех заказов"""
        print(f"Количество заказов в системе: {len(self.__orders)}")
        for order in self.__orders:
            print(f"Заказ #{order.id} от {order.дата}")
            for product, quantity in order.товары.items():
                print(f"- {product.название} x{quantity}")
        return self.__orders.copy()

    def получить_статистику_по_продавцам(self) -> Dict[str, float]:
        статистика = {}
        for заказ in self.__orders:
            for product, quantity in заказ.товары.items():
                if product.продавец not in статистика:
                    статистика[product.продавец] = 0
                статистика[product.продавец] += quantity
        return статистика

    def __load_orders(self):
        """Загружает заказы из файла"""
        try:
            if not os.path.exists("orders.json"):
                print("Файл orders.json не существует, создаем новый")
                with open("orders.json", "w", encoding='utf-8') as f:
                    json.dump([], f)
                self.__orders = []
                self.__next_order_id = 1
                return

            with open("orders.json", "r", encoding='utf-8') as f:
                data = f.read().strip()
                if not data:
                    print("Файл orders.json пуст")
                    self.__orders = []
                    self.__next_order_id = 1
                    return
                    
                orders_data = json.loads(data)
                if isinstance(orders_data, dict):
                    orders_data = [orders_data]
                
                self.__orders = []
                max_id = 0
                
                # Создаем словарь для быстрого поиска товаров по id
                products_by_id = {str(p.id): p for p in self.__products}
                
                for order_data in orders_data:
                    try:
                        if not isinstance(order_data.get("товары"), list):
                            print(f"Неверный формат товаров в заказе {order_data.get('id')}")
                            continue
                            
                        products_dict = {}
                        for item in order_data["товары"]:
                            try:
                                product_id = str(item["id"])
                                quantity = int(item["количество"])
                                
                                # Ищем товар в словаре
                                if product_id in products_by_id:
                                    products_dict[products_by_id[product_id]] = quantity
                                else:
                                    print(f"Товар с ID {product_id} не найден")
                            except (ValueError, KeyError) as e:
                                print(f"Ошибка при обработке товара: {e}")
                                continue
                                
                        if products_dict:
                            try:
                                order_id = int(order_data["id"])
                                max_id = max(max_id, order_id)
                                order = Order(
                                    id=order_id,
                                    товары=products_dict,
                                    дата=order_data.get("дата", "Неизвестно")
                                )
                                self.__orders.append(order)
                                print(f"Загружен заказ #{order_id} с {len(products_dict)} товарами")
                            except (ValueError, KeyError) as e:
                                print(f"Ошибка при создании заказа: {e}")
                        else:
                            print(f"Нет действительных товаров в заказе {order_data.get('id')}")
                    except Exception as e:
                        print(f"Ошибка при обработке заказа: {e}")
                        continue
                        
                self.__next_order_id = max_id + 1 if self.__orders else 1
                print(f"Загружено {len(self.__orders)} заказов")
                
        except json.JSONDecodeError as e:
            print(f"Ошибка при разборе JSON: {e}")
            self.__orders = []
            self.__next_order_id = 1
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
            self.__orders = []
            self.__next_order_id = 1

    def сохранить_заказ(self, товары: Dict[Product, int], filename: str) -> None:
        """Сохранение текущего заказа в файл"""
        try:
            # Создаем новый заказ
            order = Order(
                id=self.__next_order_id,
                товары=товары,
                дата=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            print(f"Создан новый заказ #{order.id}")
            print("Товары в заказе:")
            for product, quantity in order.товары.items():
                print(f"- {product.название} x{quantity}")
            
            self.__orders.append(order)
            self.__next_order_id += 1
            
            # Подготавливаем данные заказа
            order_data = {
                'id': order.id,
                'дата': order.дата,
                'товары': [
                    {
                        'id': p.id,
                        'название': p.название,
                        'количество': q,
                        'сумма': p.цена * q
                    }
                    for p, q in order.товары.items()
                ],
                'итого': order.сумма
            }
            
            # Загружаем существующие заказы
            existing_orders = []
            try:
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:  # Проверяем, что файл не пустой
                            existing_orders = json.loads(content)
                            if isinstance(existing_orders, dict):
                                existing_orders = [existing_orders]
            except Exception as e:
                print(f"Ошибка при загрузке существующих заказов: {e}")
                existing_orders = []
            
            # Проверяем, нет ли уже такого заказа
            if not any(o.get('id') == order_data['id'] for o in existing_orders):
                existing_orders.append(order_data)
            
            # Сохраняем все заказы
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_orders, f, ensure_ascii=False, indent=2)
                print(f"Заказ #{order.id} успешно сохранен в файл")
                
        except Exception as e:
            print(f"Ошибка при сохранении заказа: {e}")
            raise Exception(f"Ошибка при сохранении заказа: {e}")

    def сохранить_все_заказы(self, filename: str) -> None:
        """Сохранение всех заказов в файл"""
        try:
            orders_data = []
            for order in self.__orders:
                order_data = {
                    'id': order.id,
                    'дата': order.дата,
                    'товары': [
                        {
                            'id': p.id,
                            'название': p.название,
                            'количество': q,
                            'сумма': p.цена * q
                        }
                        for p, q in order.товары.items()
                    ],
                    'итого': order.сумма
                }
                # Проверяем, нет ли уже такого заказа
                if not any(o.get('id') == order_data['id'] for o in orders_data):
                    orders_data.append(order_data)
                
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(orders_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise Exception(f"Ошибка при сохранении заказов: {e}")

    def получить_продавцов(self, категория: str = None) -> List[str]:
        """Возвращает список продавцов. Если указана категория, возвращает только продавцов этой категории"""
        if категория and категория != "Все":
            return list(set(p.продавец for p in self.__products if p.категория == категория))
        return list(set(p.продавец for p in self.__products))

    def получить_товары_по_продавцу(self, продавец: str) -> List[Product]:
        """Возвращает список товаров конкретного продавца"""
        return [p for p in self.__products if p.продавец == продавец]


class OnlineStore(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize Auth
        self.auth = Auth()
        
        # Hide main window and show login window
        self.withdraw()
        self.show_login_window()
    
    def show_login_window(self):
        """Show login window"""
        login_window = tk.Toplevel(self)
        login_window.title("Авторизация")
        login_window.geometry("300x200")
        
        frame = ttk.Frame(login_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Логин:").pack(pady=5)
        username_entry = ttk.Entry(frame)
        username_entry.pack(pady=5)
        
        ttk.Label(frame, text="Пароль:").pack(pady=5)
        password_entry = ttk.Entry(frame, show="*")
        password_entry.pack(pady=5)
        
        def try_login():
            if self.auth.login(username_entry.get(), password_entry.get()):
                login_window.destroy()
                self.after_login()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")
        
        ttk.Button(frame, text="Войти", command=try_login).pack(pady=5)
        ttk.Button(frame, text="Регистрация", 
                  command=lambda: self.show_register_window(login_window)).pack()
    
    def show_register_window(self, parent):
        """Show registration window"""
        reg_window = tk.Toplevel(self)
        reg_window.title("Регистрация")
        reg_window.geometry("300x250")
        
        frame = ttk.Frame(reg_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Логин:").pack(pady=5)
        username_entry = ttk.Entry(frame)
        username_entry.pack(pady=5)
        
        ttk.Label(frame, text="Пароль:").pack(pady=5)
        password_entry = ttk.Entry(frame, show="*")
        password_entry.pack(pady=5)
        
        ttk.Label(frame, text="Подтвердите пароль:").pack(pady=5)
        confirm_entry = ttk.Entry(frame, show="*")
        confirm_entry.pack(pady=5)
        
        def try_register():
            username = username_entry.get()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            if not username or not password:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            
            if password != confirm:
                messagebox.showerror("Ошибка", "Пароли не совпадают")
                return
            
            if self.auth.register_user(username, password):
                messagebox.showinfo("Успех", "Регистрация успешна")
                reg_window.destroy()
                parent.destroy()
                if self.auth.login(username, password):
                    self.after_login()
            else:
                messagebox.showerror("Ошибка", "Пользователь уже существует")
        
        ttk.Button(frame, text="Зарегистрироваться", command=try_register).pack(pady=5)
        ttk.Button(frame, text="Отмена", command=reg_window.destroy).pack()
    
    def after_login(self):
        """Initialize main window after successful login"""
        # Настройки по умолчанию
        self.settings = {
            'window_size': '1000x800',
            'background_color': '#f0f0f0',
            'font_family': 'Arial',
            'font_size': 10,
            'font_size_header': 12
        }
        
        self.title("Интернет-магазин")
        self.geometry(self.settings['window_size'])
        self.configure(bg=self.settings['background_color'])
        
        self.store = Store()
        self.cart = Cart()
        
        self.__create_menu()
        self.__create_widgets()
        self.__update_product_list()
        self.__apply_settings()
        
        # Show main window
        self.deiconify()
        
        # Создаем тестовые данные при запуске
        self.__create_test_data()

    def __create_menu(self):
        """Создание главного меню приложения"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # Подменю "Заказы"
        orders_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Заказы", menu=orders_menu)
        orders_menu.add_command(label="Открыть корзину", command=self.__open_order)
        orders_menu.add_command(label="Открыть все заказы", command=self.__open_all_orders)
        orders_menu.add_command(label="Сохранить выбранные заказы", command=self.__save_selected_orders)
        orders_menu.add_separator()
        orders_menu.add_command(label="Сохранить корзину", command=self.__save_current_order)
        orders_menu.add_command(label="Сохранить все заказы", command=self.__save_all_orders)

        # Меню "Настройки"
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Настройки", menu=settings_menu)
        settings_menu.add_command(label="Изменить размер окна", command=self.__change_window_size)
        settings_menu.add_command(label="Изменить цвет фона", command=self.__change_background_color)
        settings_menu.add_command(label="Изменить шрифт", command=self.__change_font)

        # Меню "Пользователь"
        user_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Пользователь", menu=user_menu)
        user_menu.add_command(label="Выйти", command=self.__logout)
        
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)

        # В меню "Файл", после "Заказы"
        file_menu.add_separator()
        file_menu.add_command(label="Тестовые примеры", command=self.__open_test_examples)

    def __logout(self):
        """Выход из учетной записи"""
        self.auth.logout()
        self.withdraw()  # Скрываем главное окно
        self.show_login_window()

    def __change_window_size(self):
        """Изменение размера окна"""
        dialog = tk.Toplevel(self)
        dialog.title("Изменить размер окна")
        dialog.geometry("300x150")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="Ширина:").pack(pady=5)
        width_var = tk.StringVar(value=self.winfo_width())
        width_entry = ttk.Entry(dialog, textvariable=width_var)
        width_entry.pack()

        ttk.Label(dialog, text="Высота:").pack(pady=5)
        height_var = tk.StringVar(value=self.winfo_height())
        height_entry = ttk.Entry(dialog, textvariable=height_var)
        height_entry.pack()

        def apply_size():
            try:
                width = int(width_var.get())
                height = int(height_var.get())
                if width < 800: width = 800  # Минимальная ширина
                if height < 600: height = 600  # Минимальная высота
                self.settings['window_size'] = f"{width}x{height}"
                self.geometry(self.settings['window_size'])
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числовые значения")

        ttk.Button(dialog, text="Применить", command=apply_size).pack(pady=10)

    def __change_background_color(self):
        """Изменение цвета фона"""
        color = colorchooser.askcolor(title="Выберите цвет фона", color=self.settings['background_color'])
        if color[1]:
            self.settings['background_color'] = color[1]
            self.__apply_settings()

    def __change_font(self):
        """Изменение шрифта"""
        dialog = tk.Toplevel(self)
        dialog.title("Изменить шрифт")
        dialog.geometry("300x250")
        dialog.resizable(False, False)

        # Список доступных шрифтов
        ttk.Label(dialog, text="Шрифт:").pack(pady=5)
        font_family_var = tk.StringVar(value=self.settings['font_family'])
        font_combo = ttk.Combobox(dialog, textvariable=font_family_var, values=list(font.families()))
        font_combo.pack()

        # Размер обычного текста
        ttk.Label(dialog, text="Размер обычного текста:").pack(pady=5)
        font_size_var = tk.StringVar(value=self.settings['font_size'])
        font_size_entry = ttk.Entry(dialog, textvariable=font_size_var)
        font_size_entry.pack()

        # Размер заголовков
        ttk.Label(dialog, text="Размер заголовков:").pack(pady=5)
        font_size_header_var = tk.StringVar(value=self.settings['font_size_header'])
        font_size_header_entry = ttk.Entry(dialog, textvariable=font_size_header_var)
        font_size_header_entry.pack()

        def apply_font():
            try:
                size = int(font_size_var.get())
                size_header = int(font_size_header_var.get())
                if size < 8: size = 8  # Минимальный размер
                if size_header < 10: size_header = 10  # Минимальный размер заголовков
                
                self.settings['font_family'] = font_family_var.get()
                self.settings['font_size'] = size
                self.settings['font_size_header'] = size_header
                self.__apply_settings()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числовые значения для размеров шрифта")

        ttk.Button(dialog, text="Применить", command=apply_font).pack(pady=10)

    def __apply_settings(self):
        """Применение настроек интерфейса"""
        # Применяем цвет фона
        self.configure(bg=self.settings['background_color'])
        for frame in [self.left_frame, self.middle_frame, self.right_frame]:
            frame.configure(style='Custom.TFrame')

        # Создаем стили
        style = ttk.Style()
        style.configure('Custom.TFrame', background=self.settings['background_color'])
        style.configure('Custom.TLabel', 
                       background=self.settings['background_color'],
                       font=(self.settings['font_family'], self.settings['font_size']))
        style.configure('Header.TLabel',
                       background=self.settings['background_color'],
                       font=(self.settings['font_family'], self.settings['font_size_header'], 'bold'))

        # Применяем шрифты к виджетам
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Label):
                if 'bold' in str(widget.cget('font')):
                    widget.configure(style='Header.TLabel')
                else:
                    widget.configure(style='Custom.TLabel')

        # Обновляем шрифты в списках и текстовых полях
        font_normal = (self.settings['font_family'], self.settings['font_size'])
        self.products_listbox.configure(font=font_normal, bg=self.settings['background_color'])
        self.cart_text.configure(font=font_normal, bg=self.settings['background_color'])
        self.orders_text.configure(font=font_normal, bg=self.settings['background_color'])

        # Обновляем графики
        self.__update_cart_chart()
        self.__update_sellers_chart()

    def __create_widgets(self):
        # Создаем основные фреймы
        self.left_frame = ttk.Frame(self)
        self.middle_frame = ttk.Frame(self)
        self.right_frame = ttk.Frame(self)
        
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.__create_catalog_widgets()
        self.__create_cart_widgets()
        self.__create_orders_widgets()

    def __create_catalog_widgets(self):
        # Левая панель: каталог товаров
        ttk.Label(self.left_frame, text="Каталог товаров", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # Фильтры
        filters_frame = ttk.Frame(self.left_frame)
        filters_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Фильтр по категории
        ttk.Label(filters_frame, text="Категория:").pack(anchor=tk.W)
        self.category_var = tk.StringVar(value="Все")
        categories = ["Все"] + self.store.получить_категории()
        self.category_combo = ttk.Combobox(filters_frame, textvariable=self.category_var, values=categories)
        self.category_combo.pack(fill=tk.X, pady=(0, 5))
        self.category_combo.bind("<<ComboboxSelected>>", self.__on_category_changed)
        
        # Фильтр по продавцу
        ttk.Label(filters_frame, text="Продавец:").pack(anchor=tk.W)
        self.seller_var = tk.StringVar(value="Все")
        sellers = ["Все"] + self.store.получить_продавцов()
        self.seller_combo = ttk.Combobox(filters_frame, textvariable=self.seller_var, values=sellers)
        self.seller_combo.pack(fill=tk.X)
        self.seller_combo.bind("<<ComboboxSelected>>", lambda _: self.__update_product_list())

        ttk.Label(self.left_frame, text="Доступные товары:").pack(anchor=tk.W)
        
        # Создаем фрейм для списка товаров и полосы прокрутки
        list_frame = ttk.Frame(self.left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем полосу прокрутки
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Создаем горизонтальную полосу прокрутки
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Создаем список товаров с увеличенной шириной
        self.products_listbox = tk.Listbox(list_frame, height=20, width=60,
                                         yscrollcommand=scrollbar.set,
                                         xscrollcommand=h_scrollbar.set)
        self.products_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Настраиваем полосы прокрутки
        scrollbar.config(command=self.products_listbox.yview)
        h_scrollbar.config(command=self.products_listbox.xview)

        ttk.Button(self.left_frame, text="Добавить в корзину", 
                  command=self.__add_to_cart).pack(fill=tk.X, pady=(5, 0))

    def __create_cart_widgets(self):
        # Средняя панель: корзина и график товаров
        ttk.Label(self.middle_frame, text="Корзина покупок", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.cart_text = tk.Text(self.middle_frame, height=10, width=40)
        self.cart_text.pack(fill=tk.BOTH, expand=True)

        buttons_frame = ttk.Frame(self.middle_frame)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(buttons_frame, text="Очистить корзину", 
                  command=self.__clear_cart).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Оформить заказ", 
                  command=self.__place_order).pack(side=tk.LEFT)

        ttk.Label(self.middle_frame, text="Диаграмма товаров в корзине", font=('Arial', 10, 'bold')).pack(pady=(10, 0))
        self.cart_fig, self.cart_ax = plt.subplots(figsize=(5, 3))
        self.cart_canvas = FigureCanvasTkAgg(self.cart_fig, master=self.middle_frame)
        self.cart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def __create_orders_widgets(self):
        # Правая панель: история заказов и статистика по продавцам
        ttk.Label(self.right_frame, text="История заказов", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.orders_text = tk.Text(self.right_frame, height=10, width=40)
        self.orders_text.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.right_frame, text="Статистика продаж по магазинам", font=('Arial', 10, 'bold')).pack(pady=(10, 0))
        self.sellers_fig, self.sellers_ax = plt.subplots(figsize=(5, 3))
        self.sellers_canvas = FigureCanvasTkAgg(self.sellers_fig, master=self.right_frame)
        self.sellers_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def __update_product_list(self):
        self.products_listbox.delete(0, tk.END)
        category = self.category_var.get()
        seller = self.seller_var.get()
        
        # Получаем товары с учетом обоих фильтров
        products = self.store.получить_все_товары()
        if category != "Все":
            products = [p for p in products if p.категория == category]
        if seller != "Все":
            products = [p for p in products if p.продавец == seller]
        
        for product in products:
            self.products_listbox.insert(tk.END, str(product))

    def __add_to_cart(self):
        selection = self.products_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите товар для добавления в корзину")
            return

        category = self.category_var.get()
        products = (self.store.получить_все_товары() if category == "Все" 
                   else self.store.получить_товары_по_категории(category))
        
        selected_product = products[selection[0]]
        
        # Создаем диалоговое окно для выбора количества
        dialog = tk.Toplevel(self)
        dialog.title("Выбор количества")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        # Центрируем диалоговое окно
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Добавляем элементы в диалоговое окно
        ttk.Label(dialog, text=f"Выбран товар: {selected_product.название}").pack(pady=10)
        ttk.Label(dialog, text="Введите количество:").pack()
        
        quantity_var = tk.StringVar(value="1")
        quantity_entry = ttk.Entry(dialog, textvariable=quantity_var)
        quantity_entry.pack(pady=5)
        
        def add_with_quantity():
            try:
                quantity = int(quantity_var.get())
                if quantity <= 0:
                    raise ValueError
                self.cart.добавить_товар(selected_product, quantity)
                self.__update_cart_display()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Пожалуйста, введите корректное количество (целое число больше 0)")
        
        ttk.Button(dialog, text="Добавить", command=add_with_quantity).pack(pady=10)
        
        # Устанавливаем фокус на поле ввода
        quantity_entry.focus()
        
        # Обработка нажатия Enter
        dialog.bind('<Return>', lambda e: add_with_quantity())

    def __clear_cart(self):
        self.cart.очистить()
        self.__update_cart_display()

    def __update_cart_display(self):
        self.cart_text.delete(1.0, tk.END)
        self.cart_text.insert(tk.END, str(self.cart))
        self.__update_cart_chart()
        self.__update_orders_display()
        self.__update_sellers_chart()

    def __update_cart_chart(self):
        self.cart_ax.clear()
        cart_items = self.cart.получить_товары()
        
        if cart_items:
            names = [p.название.split()[0] for p in cart_items.keys()]
            quantities = list(cart_items.values())
            
            self.cart_ax.bar(names, quantities)
            self.cart_ax.set_title("Количество товаров в корзине")
            self.cart_ax.tick_params(axis='x', rotation=45)
            
            self.cart_fig.tight_layout()
            self.cart_canvas.draw()

    def __update_orders_display(self):
        self.orders_text.delete(1.0, tk.END)
        orders = self.store.получить_все_заказы()
        if orders:
            for order in orders:
                self.orders_text.insert(tk.END, str(order) + "\n\n")
        else:
            self.orders_text.insert(tk.END, "История заказов пуста")

    def __update_sellers_chart(self):
        self.sellers_ax.clear()
        статистика = self.store.получить_статистику_по_продавцам()
        
        if статистика:
            sellers = list(статистика.keys())
            amounts = list(статистика.values())
            
            self.sellers_ax.bar(sellers, amounts)
            self.sellers_ax.set_title("Количество проданных товаров по продавцам")
            self.sellers_ax.tick_params(axis='x', rotation=45)
            
            self.sellers_fig.tight_layout()
            self.sellers_canvas.draw()

    def __place_order(self):
        if not self.cart.получить_товары():
            messagebox.showwarning("Внимание", "Корзина пуста")
            return

        try:
            self.store.сохранить_заказ(self.cart.получить_товары(), "orders.json")
            messagebox.showinfo("Успех", "Заказ успешно оформлен и сохранен")
            self.__clear_cart()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось оформить заказ: {e}")

    def __on_category_changed(self, event):
        """Обработчик изменения категории"""
        # Обновляем список продавцов в зависимости от выбранной категории
        category = self.category_var.get()
        sellers = ["Все"] + self.store.получить_продавцов(category)
        self.seller_combo['values'] = sellers
        self.seller_var.set("Все")  # Сбрасываем выбор продавца
        
        # Обновляем список товаров
        self.__update_product_list()

    def __open_order(self):
        """Открытие сохраненной корзины"""
        file_path = filedialog.askopenfilename(
            initialdir=DESKTOP_PATH,
            title="Выберите файл корзины",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Если данные пришли в виде списка, берем первый заказ
                order_data = data[0] if isinstance(data, list) else data
                
                # Создаем диалоговое окно для отображения корзины
                dialog = tk.Toplevel(self)
                dialog.title("Содержимое корзины")
                dialog.geometry("500x400")
                
                # Создаем текстовое поле с прокруткой
                text_frame = ttk.Frame(dialog)
                text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                scrollbar = ttk.Scrollbar(text_frame)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                text_widget = tk.Text(text_frame, wrap=tk.WORD, 
                                    font=(self.settings['font_family'], self.settings['font_size']),
                                    yscrollcommand=scrollbar.set)
                text_widget.pack(fill=tk.BOTH, expand=True)
                
                scrollbar.config(command=text_widget.yview)
                
                # Формируем текст для отображения
                text_widget.insert('1.0', f"Корзина от {order_data.get('дата', 'Неизвестно')}\n\n")
                
                if 'товары' in order_data and isinstance(order_data['товары'], list):
                    for item in order_data['товары']:
                        if isinstance(item, dict):
                            название = item.get('название', 'Неизвестный товар')
                            количество = item.get('количество', 0)
                            сумма = item.get('сумма', 0)
                            text_widget.insert('end', f"{название} x{количество} = {сумма} руб.\n")
                
                итого = order_data.get('итого', 0)
                text_widget.insert('end', f"\nИтого: {итого} руб.")
                
                # Делаем текстовое поле только для чтения
                text_widget.config(state='disabled')
                
                # Кнопка закрытия
                ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack(pady=10)
                
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка", "Неверный формат файла")
            except IndexError:
                messagebox.showerror("Ошибка", "Файл не содержит заказов")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def __open_all_orders(self):
        """Открытие всех сохраненных заказов"""
        file_path = filedialog.askopenfilename(
            initialdir=DESKTOP_PATH,
            title="Выберите файл со всеми заказами",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    orders_data = json.load(f)
                
                # Показываем заказы в отдельном окне
                dialog = tk.Toplevel(self)
                dialog.title("Все заказы")
                dialog.geometry("500x400")
                
                text_widget = tk.Text(dialog, wrap=tk.WORD, font=(self.settings['font_family'], self.settings['font_size']))
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Формируем текст для отображения
                for order in orders_data:
                    order_text = f"Заказ #{order['id']} от {order['дата']}\n\n"
                    for item in order['товары']:
                        order_text += f"{item['название']} x{item['количество']} = {item['сумма']} руб.\n"
                    order_text += f"\nИтого: {order['итого']} руб.\n"
                    order_text += "\n" + "-"*50 + "\n\n"
                    text_widget.insert('end', order_text)
                
                text_widget.config(state='disabled')
                
                ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack(pady=10)
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть заказы: {e}")

    def __save_current_order(self):
        """Сохранение текущей корзины"""
        if not self.cart.получить_товары():
            messagebox.showwarning("Предупреждение", "Корзина пуста!")
            return
            
        file_path = filedialog.asksaveasfilename(
            initialdir=DESKTOP_PATH,
            title="Сохранить корзину",
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        if file_path:
            try:
                self.store.сохранить_заказ(self.cart.получить_товары(), file_path)
                messagebox.showinfo("Успешно", "Корзина успешно сохранена!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить корзину: {e}")

    def __save_all_orders(self):
        """Сохранение всех заказов"""
        file_path = filedialog.asksaveasfilename(
            initialdir=DESKTOP_PATH,
            title="Сохранить все заказы",
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        if file_path:
            try:
                self.store.сохранить_все_заказы(file_path)
                messagebox.showinfo("Успех", "Все заказы успешно сохранены")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить заказы: {e}")

    def __save_selected_orders(self):
        """Сохранение выбранных заказов"""
        orders = self.store.получить_все_заказы()
        if not orders:
            messagebox.showwarning("Внимание", "Нет доступных заказов")
            return
            
        # Создаем диалоговое окно для выбора заказов
        dialog = tk.Toplevel(self)
        dialog.title("Выбор заказов для сохранения")
        dialog.geometry("800x600")
        
        # Создаем основной фрейм
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Добавляем заголовок
        ttk.Label(main_frame, text=f"Выберите заказы для сохранения ({len(orders)} заказов):", 
                 font=(self.settings['font_family'], self.settings['font_size_header'])).pack(anchor=tk.W, pady=(0, 10))
        
        # Создаем фрейм для списка заказов
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем полосу прокрутки
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Создаем список заказов
        orders_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, 
                                  yscrollcommand=scrollbar.set,
                                  font=(self.settings['font_family'], self.settings['font_size']))
        orders_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Настраиваем полосу прокрутки
        scrollbar.config(command=orders_listbox.yview)
        
        # Заполняем список заказов
        for order in orders:
            order_text = f"Заказ #{order.id} от {order.дата}\n"
            for product, quantity in order.товары.items():
                order_text += f"  - {product.название} x{quantity} = {product.цена * quantity} руб.\n"
            order_text += f"  Итого: {order.сумма} руб."
            orders_listbox.insert(tk.END, order_text)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        def save_selected():
            selected_indices = orders_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Внимание", "Не выбрано ни одного заказа")
                return
                
            file_path = filedialog.asksaveasfilename(
                initialdir=DESKTOP_PATH,
                title="Сохранить выбранные заказы",
                defaultextension=".json",
                filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
            )
            
            if file_path:
                try:
                    selected_orders = [orders[i] for i in selected_indices]
                    orders_data = []
                    for order in selected_orders:
                        order_data = {
                            'id': order.id,
                            'дата': order.дата,
                            'товары': [
                                {
                                    'id': p.id,
                                    'название': p.название,
                                    'количество': q,
                                    'сумма': p.цена * q
                                }
                                for p, q in order.товары.items()
                            ],
                            'итого': order.сумма
                        }
                        orders_data.append(order_data)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(orders_data, f, ensure_ascii=False, indent=2)
                    
                    messagebox.showinfo("Успех", "Выбранные заказы успешно сохранены")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить заказы: {e}")
        
        ttk.Button(buttons_frame, text="Сохранить выбранные", 
                  command=save_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Добавляем прокрутку мышью
        def on_mousewheel(event):
            orders_listbox.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        orders_listbox.bind_all("<MouseWheel>", on_mousewheel)
        
        # Отключаем прокрутку при закрытии окна
        def on_closing():
            orders_listbox.unbind_all("<MouseWheel>")
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_closing)

    def __create_test_data(self):
        """Создание тестовых наборов данных"""
        test_dir = os.path.join(DESKTOP_PATH, "test_orders")
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        test_cases = {
            "test1_electronics.json": {
                "id": 1,
                "дата": "2024-04-15",
                "товары": [
                    {"id": 1, "название": "Смартфон Samsung Galaxy A54", "количество": 1, "сумма": 34999},
                    {"id": 2, "название": "Ноутбук ASUS VivoBook", "количество": 1, "сумма": 49999}
                ],
                "итого": 84998
            },
            "test2_books.json": {
                "id": 2,
                "дата": "2024-04-15",
                "товары": [
                    {"id": 26, "название": "Книга 'Мастер и Маргарита'", "количество": 2, "сумма": 1598},
                    {"id": 27, "название": "Книга 'Война и мир'", "количество": 1, "сумма": 999},
                    {"id": 28, "название": "Книга 'Преступление и наказание'", "количество": 1, "сумма": 699}
                ],
                "итого": 3296
            },
            "test3_appliances.json": {
                "id": 3,
                "дата": "2024-04-15",
                "товары": [
                    {"id": 48, "название": "Холодильник LG", "количество": 1, "сумма": 49999},
                    {"id": 49, "название": "Стиральная машина Bosch", "количество": 1, "сумма": 34999}
                ],
                "итого": 84998
            },
            "test4_clothes.json": {
                "id": 4,
                "дата": "2024-04-15",
                "товары": [
                    {"id": 66, "название": "Футболка хлопковая", "количество": 3, "сумма": 2997},
                    {"id": 67, "название": "Джинсы", "количество": 2, "сумма": 11998},
                    {"id": 68, "название": "Куртка зимняя", "количество": 1, "сумма": 12999}
                ],
                "итого": 27994
            },
            "test5_food.json": {
                "id": 5,
                "дата": "2024-04-15",
                "товары": [
                    {"id": 86, "название": "Чай зеленый (100 пак.)", "количество": 2, "сумма": 598},
                    {"id": 87, "название": "Кофе в зернах (1 кг)", "количество": 1, "сумма": 999},
                    {"id": 88, "название": "Шоколад горький", "количество": 5, "сумма": 995}
                ],
                "итого": 2592
            },
            "test6_mixed.json": {
                "id": 6,
                "дата": "2024-04-15",
                "товары": [
                    {"id": 1, "название": "Смартфон Samsung Galaxy A54", "количество": 1, "сумма": 34999},
                    {"id": 26, "название": "Книга 'Мастер и Маргарита'", "количество": 1, "сумма": 799},
                    {"id": 66, "название": "Футболка хлопковая", "количество": 2, "сумма": 1998}
                ],
                "итого": 37796
            },
            "test7_big_order.json": {
                "id": 7,
                "дата": "2024-04-15",
                "товары": [
                    {"id": 8, "название": "Телевизор LG OLED C1", "количество": 1, "сумма": 89999},
                    {"id": 48, "название": "Холодильник LG", "количество": 1, "сумма": 49999},
                    {"id": 49, "название": "Стиральная машина Bosch", "количество": 1, "сумма": 34999},
                    {"id": 50, "название": "Пылесос Dyson V8", "количество": 1, "сумма": 29999}
                ],
                "итого": 204996
            }
        }

        for filename, data in test_cases.items():
            filepath = os.path.join(test_dir, filename)
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"Ошибка при создании {filename}: {e}")

    def __open_test_examples(self):
        """Открытие окна с тестовыми примерами"""
        # Создаем тестовые данные при первом открытии
        self.__create_test_data()
        
        # Создаем диалоговое окно
        dialog = tk.Toplevel(self)
        dialog.title("Тестовые примеры заказов")
        dialog.geometry("600x400")
        
        # Создаем фрейм с прокруткой
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Добавляем описание
        description = ttk.Label(frame, text="Выберите тестовый пример для просмотра:", 
                              font=(self.settings['font_family'], self.settings['font_size']))
        description.pack(pady=10)
        
        # Создаем список тестовых примеров
        test_cases = {
            "Пример 1: Электроника": "test1_electronics.json",
            "Пример 2: Книги": "test2_books.json",
            "Пример 3: Бытовая техника": "test3_appliances.json",
            "Пример 4: Одежда": "test4_clothes.json",
            "Пример 5: Продукты питания": "test5_food.json",
            "Пример 6: Смешанный заказ": "test6_mixed.json",
            "Пример 7: Крупный заказ": "test7_big_order.json"
        }
        
        for description, filename in test_cases.items():
            btn = ttk.Button(frame, text=description,
                           command=lambda f=filename: self.__open_test_file(f))
            btn.pack(fill=tk.X, pady=5)
        
        # Кнопка закрытия
        ttk.Button(frame, text="Закрыть", command=dialog.destroy).pack(pady=10)

    def __open_test_file(self, filename):
        """Открытие тестового файла"""
        filepath = os.path.join(DESKTOP_PATH, "test_orders", filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                order_data = json.load(f)
            
            # Создаем диалоговое окно для отображения содержимого
            dialog = tk.Toplevel(self)
            dialog.title(f"Тестовый пример: {filename}")
            dialog.geometry("1000x900")  # Увеличиваем размер окна
            
            # Создаем основной фрейм
            main_frame = ttk.Frame(dialog)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # Увеличиваем отступы
            
            # Создаем текстовое поле с прокруткой
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD,
                                font=(self.settings['font_family'], self.settings['font_size'] + 2),  # Увеличиваем шрифт
                                yscrollcommand=scrollbar.set)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            scrollbar.config(command=text_widget.yview)
            
            # Формируем текст для отображения
            text_widget.insert('1.0', f"Заказ #{order_data['id']} от {order_data['дата']}\n\n")
            text_widget.insert('end', "Товары в заказе:\n")
            
            # Собираем данные для диаграмм
            names = []
            quantities = []
            prices = []
            
            for item in order_data['товары']:
                название = item['название']
                количество = item['количество']
                сумма = item['сумма']
                text_widget.insert('end', f"- {название} x{количество} = {сумма} руб.\n")
                
                # Добавляем данные для диаграмм
                names.append('\n'.join(название.split()[:2]))  # Берем первые два слова названия и разбиваем на строки
                quantities.append(количество)
                prices.append(сумма)
            
            text_widget.insert('end', f"\nИтого: {order_data['итого']} руб.")
            
            # Делаем текстовое поле только для чтения
            text_widget.config(state='disabled')
            
            # Создаем фрейм для диаграмм
            charts_frame = ttk.Frame(main_frame)
            charts_frame.pack(fill=tk.BOTH, expand=True, pady=20)
            
            # Создаем диаграмму количества товаров
            quantity_fig, quantity_ax = plt.subplots(figsize=(12, 4))  # Увеличиваем размер графика
            bars = quantity_ax.bar(names, quantities)
            quantity_ax.set_title("График проданных продавцом товаров", fontsize=14, pad=20)  # Увеличиваем заголовок
            quantity_ax.tick_params(axis='x', rotation=0, labelsize=10)  # Убираем поворот подписей
            quantity_ax.tick_params(axis='y', labelsize=10)
            
            # Добавляем значения над столбцами
            for bar in bars:
                height = bar.get_height()
                quantity_ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            quantity_fig.tight_layout()
            
            quantity_canvas = FigureCanvasTkAgg(quantity_fig, master=charts_frame)
            quantity_canvas.draw()
            quantity_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            # Создаем диаграмму стоимости товаров
            price_fig, price_ax = plt.subplots(figsize=(12, 4))  # Увеличиваем размер графика
            bars = price_ax.bar(names, prices)
            price_ax.set_title("Стоимость товаров (руб.)", fontsize=14, pad=20)  # Увеличиваем заголовок
            price_ax.tick_params(axis='x', rotation=0, labelsize=10)  # Убираем поворот подписей
            price_ax.tick_params(axis='y', labelsize=10)
            
            # Добавляем значения над столбцами
            for bar in bars:
                height = bar.get_height()
                price_ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            price_fig.tight_layout()
            
            price_canvas = FigureCanvasTkAgg(price_fig, master=charts_frame)
            price_canvas.draw()
            price_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Кнопка закрытия
            ttk.Button(main_frame, text="Закрыть", command=dialog.destroy).pack(pady=10)
            
            # Очищаем фигуры matplotlib после закрытия окна
            def on_closing():
                plt.close(quantitфy_fig)
                plt.close(price_fig)
                dialog.destroy()
            
            dialog.protocol("WM_DELETE_WINDOW", on_closing)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть тестовый пример: {e}")


if __name__ == "__main__":
    app = OnlineStore()
    app.mainloop() 
