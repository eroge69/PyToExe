import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from scipy.interpolate import interp1d

def load_data():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Выберите файл Excel",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not file_path:
        raise FileNotFoundError("Файл не выбран.")
    data = pd.read_excel(file_path)
    lambda_arr = data.iloc[:, 0].values  # мкм
    alpha_arr = data.iloc[:, 1].values   # см^-1
    R_arr = data.iloc[:, 2].values       # коэффициент отражения
    return lambda_arr, alpha_arr, R_arr

def create_grid(n, d):
    x = np.zeros(n)
    dxd = d / (n - 1)
    for i in range(1, n):
        x[i] = x[i-1] + dxd
    return x, dxd

def calculate_concentration(G, n, sp1, dxd, D, tau, Vrec):
    a = np.zeros(n)
    b = np.zeros(n)
    dd = np.zeros(n)
    rr = np.zeros(n)
    delta = np.zeros(n)
    lam = np.zeros(n)
    cp = np.zeros(n)

    a[0] = Vrec * dxd / D - 1
    b[0] = 1
    dd[0] = 0
    rr[0] = 0
    delta[0] = -dd[0] / a[0]
    lam[0] = rr[0] / a[0]

    a[sp1] = 1
    b[sp1] = 0
    dd[sp1] = 0
    rr[sp1] = 0

    for i in range(1, sp1):
        a[i] = -2 - (dxd ** 2) / (D * tau)
        b[i] = 1
        dd[i] = 1
        rr[i] = -dxd ** 2 * G[i] / D

    for i in range(1, sp1 + 1):
        delta[i] = -dd[i] / (a[i] + b[i] * delta[i-1])
        lam[i] = (rr[i] - b[i] * lam[i-1]) / (a[i] + b[i] * delta[i-1])

    cp[sp1] = lam[sp1]
    for i in range(sp1-1, -1, -1):
        cp[i] = delta[i] * cp[i+1] + lam[i]

    return cp

def run_noviy():
    n = 1000
    d = 5e-4
    q = 1.60e-19
    I0 = 1.00e15
    tau = 1e-8
    Dn = 6.5
    Dp = 3.9
    Vrec = 1e4
    xj = 6.00e-5
    xp = 1.60e-7
    xn = 1.60e-5

    params = (n, d, q, I0, tau, Dn, Dp, Vrec, xj, xp, xn)

    lambda_arr, alpha_arr, R_arr = load_data()
    kol = len(lambda_arr)

    Sn = np.zeros(kol)
    Sp = np.zeros(kol)
    Sw = np.zeros(kol)
    Scom = np.zeros(kol)

    x, dxd = create_grid(n, d)

    sp1 = int((xj - xp) * n / d)
    sn1 = int((d - xj - xn) * n / d)
    sw1 = n - sp1 - sn1

    for j in range(kol):
        R = R_arr[j]
        alfa = alpha_arr[j]
        G = I0 * (1 - R) * alfa * np.exp(-alfa * x)

        cp = calculate_concentration(G, n, sp1, dxd, Dn, tau, Vrec)
        jn = q * Dn * (cp[sp1] - cp[sp1-1]) / dxd
        P = I0 * q * 1.24 / lambda_arr[j]
        Sn[j] = abs(jn / P)

        G_shifted = I0 * (1 - R) * alfa * np.exp(-alfa * x)
        cn = calculate_concentration(G_shifted[sw1+sp1:], n, sn1, dxd, Dp, tau, Vrec)
        jp = q * Dp * (cn[1] - cn[0]) / dxd

        jw = q * I0 * (1 - R) * (np.exp(-alfa * (xj - xp)) - np.exp(-alfa * (xj + xn)))

        Sp[j] = abs(jp / P)
        Sw[j] = abs(jw / P)

    Scom = Sn + Sp + Sw

    Smax = np.max(Scom)
    dense_lambda = np.linspace(lambda_arr.min(), lambda_arr.max(), 5000)

    plt.figure(figsize=(10, 6))
    plt.plot(lambda_arr, Sn / Smax, label='Sn')
    plt.plot(lambda_arr, Sp / Smax, label='Sp')
    plt.plot(lambda_arr, Sw / Smax, label='Sw')
    plt.plot(lambda_arr, Scom / Smax, label='Scom')
    plt.xlabel('Длина волны (λ), мкм')
    plt.ylabel('Нормированная фоточувствительность')
    plt.legend()
    plt.grid(True)
    plt.xlim(0.2, 0.6)
    plt.show()

def calculate_junction_width(fik, U, Na, Nd, eps_r, q):
    eps0 = 8.854e-14  # Ф/см
    W = np.sqrt(2 * eps_r * eps0 / q * (Na + Nd) / (Na * Nd) * (fik + abs(U)))
    xp = Nd / (Na + Nd) * W
    xn = Na / (Na + Nd) * W
    return xp, xn

def run_xxx():
    n = 1000
    d = 5e-4
    q = 1.602e-19
    I0 = 1.00e15
    tau = 1e-8
    Dn = 6.5
    Dp = 3.9
    Vrec = 1e4
    xj = 6.00e-5
    fik = 2.12
    Na = 1.00e19
    Nd = 1.00e17
    eps_r = 11.1

    params = (n, d, q, I0, tau, Dn, Dp, Vrec, xj, fik, Na, Nd, eps_r)

    lambda_arr, alpha_arr, R_arr = load_data()

    U_list = np.arange(0, 10, 2)
    all_results = {}

    for U in U_list:
        xp, xn = calculate_junction_width(fik, U, Na, Nd, eps_r, q)
        kol = len(lambda_arr)

        Sn = np.zeros(kol)
        Sp = np.zeros(kol)
        Sw = np.zeros(kol)

        x, dxd = create_grid(n, d)

        sp1 = int((xj - xp) * n / d)
        sn1 = int((d - xj - xn) * n / d)
        sw1 = n - sp1 - sn1

        for j in range(kol):
            R = R_arr[j]
            alfa = alpha_arr[j]
            G = I0 * (1 - R) * alfa * np.exp(-alfa * x)

            cp = calculate_concentration(G, n, sp1, dxd, Dn, tau, Vrec)
            jn = q * Dn * (cp[sp1] - cp[sp1-1]) / dxd
            P = I0 * q * 1.24 / lambda_arr[j]
            Sn[j] = abs(jn / P)

            G_shifted = I0 * (1 - R) * alfa * np.exp(-alfa * x)
            cn = calculate_concentration(G_shifted[sw1+sp1:], n, sn1, dxd, Dp, tau, Vrec)
            jp = q * Dp * (cn[1] - cn[0]) / dxd

            jw = q * I0 * (1 - R) * (np.exp(-alfa * (xj - xp)) - np.exp(-alfa * (xj + xn)))

            Sp[j] = abs(jp / P)
            Sw[j] = abs(jw / P)

        Scom = Sn + Sp + Sw
        all_results[U] = (lambda_arr, Scom)

    plt.figure(figsize=(10, 6))

    for U, (lambda_arr, Scom) in all_results.items():
        plt.plot(lambda_arr, Scom, label=f'U = {U:.1f} V')

    plt.xlabel('Длина волны (λ), мкм')
    plt.ylabel('Фоточувствительность, А/Вт')
    plt.legend()
    plt.grid(True)
    plt.xlim(0.2, 0.6)
    plt.show()

def main():
    root = tk.Tk()
    root.title("Выберите расчет")

    button1 = tk.Button(root, text="Спектральная характеристика относительной фоточувствительности фотодиода", command=run_noviy)
    button1.pack(pady=10)

    button2 = tk.Button(root, text="Зависимость спектральной характеристики и фототока от обратного смещения", command=run_xxx)
    button2.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()