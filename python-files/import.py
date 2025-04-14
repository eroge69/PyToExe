import numpy as np
from math import sin, cos, sqrt, pow

def f(x):
    if -2 <= x <= 0:
        return x**2 * sin(-pow(abs(x), 1/3) - 3)  # Была пропущена закрывающая скобка
    elif 0 < x <= 1:
        return sqrt(x) * cos(2*x)
    else:
        raise ValueError("x is out of the defined domain")

def rectangle_method(a, b, n):
    h = (b - a) / n
    integral = 0
    for i in range(n):
        x = a + (i + 0.5) * h
        integral += f(x)
    return integral * h

def trapezoidal_method(a, b, n):
    h = (b - a) / n
    integral = (f(a) + f(b)) / 2
    for i in range(1, n):
        x = a + i * h
        integral += f(x)
    return integral * h

def simpson_method(a, b, n):
    if n % 2 != 0:
        n += 1
    h = (b - a) / n
    integral = f(a) + f(b)
    for i in range(1, n):
        x = a + i * h
        if i % 2 == 0:
            integral += 2 * f(x)
        else:
            integral += 4 * f(x)
    return integral * h / 3

# Основная часть программы
if __name__ == "__main__":
    a, b = -2, 1
    n = 10000  # Увеличили количество разбиений для точности
    
    # Разбиваем интеграл на две части из-за особенности функции в x=0
    rect = rectangle_method(a, 0, n//2) + rectangle_method(0, b, n//2)
    trap = trapezoidal_method(a, 0, n//2) + trapezoidal_method(0, b, n//2)
    simp = simpson_method(a, 0, n//2) + simpson_method(0, b, n//2)
    
    print("Результаты интегрирования:")
    print(f"Метод прямоугольников: {rect:.6f}")
    print(f"Метод трапеций:       {trap:.6f}")
    print(f"Метод Симпсона:       {simp:.6f}")
    print(f"Контрольное значение:  2.424170")
    print("\nПогрешности:")
    print(f"Прямоугольников: {abs(rect - 2.424170):.6f}")
    print(f"Трапеций:        {abs(trap - 2.424170):.6f}")
    print(f"Симпсона:        {abs(simp - 2.424170):.6f}")