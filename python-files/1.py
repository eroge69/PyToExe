import random

def generate_random_number(start, end):
    return random.randint(start, end)

start = int(input("Введите начальное значение диапазона: "))
end = int(input("Введите конечно значение диапазона: "))

random_number = generate_random_number(start, end)
print(f"Случайное число между {start} и {end}: {random_number}")

