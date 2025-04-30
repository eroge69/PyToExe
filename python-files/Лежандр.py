import numpy as np
import matplotlib.pyplot as plt
from scipy.special import legendre
from scipy.integrate import quad


def legendre_exponential(n, c, x):
    """
    Вычисляет ортогональную экспоненту Лежандра: e^{c x} * P_n(x)

    Параметры:
        n (int): степень полинома Лежандра
        c (float): коэффициент экспоненты
        x (float или массив): точка(и) вычисления

    Возвращает:
        Значение экспоненты Лежандра в точке x
    """
    Pn = legendre(n)  # Полином Лежандра степени n
    return np.exp(c * x) * Pn(x)


def weighted_inner_product(n, m, c):
    """
    Вычисляет взвешенное скалярное произведение:
    ∫_{-1}^{1} e^{2c x} P_n(x) P_m(x) dx

    Параметры:
        n, m (int): степени полиномов Лежандра
        c (float): коэффициент экспоненты

    Возвращает:
        Значение интеграла (должно быть ~0 при n != m)
    """
    integrand = lambda x: np.exp(2 * c * x) * legendre(n)(x) * legendre(m)(x)
    integral, _ = quad(integrand, -1, 1)
    return integral


def plot_legendre_exponentials(max_degree, c):
    """
    Рисует графики ортогональных экспонент Лежандра для степеней от 0 до max_degree

    Параметры:
        max_degree (int): максимальная степень полинома
        c (float): коэффициент экспоненты
    """
    x = np.linspace(-1, 1, 500)
    plt.figure(figsize=(10, 6))

    for n in range(max_degree + 1):
        y = legendre_exponential(n, c, x)
        plt.plot(x, y, label=f"n = {n}")

    plt.title(f"Ортогональные экспоненты Лежандра ($e^{{{c}x}} P_n(x)$)")
    plt.xlabel("x")
    plt.ylabel("$\phi_n(x)$")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    c = 0.5  # Параметр экспоненты
    max_degree = 3  # Максимальная степень полинома

    # Проверка ортогональности (должно быть ~0 для n != m)
    print("Проверка ортогональности:")
    print(f"n=2, m=3: ∫(e^{2 * c}x P_2 P_3) dx = {weighted_inner_product(2, 3, c):.5f}")
    print(f"n=1, m=1: ∫(e^{2 * c}x P_1 P_1) dx = {weighted_inner_product(1, 1, c):.5f}")

    # Построение графиков
    plot_legendre_exponentials(max_degree, c)