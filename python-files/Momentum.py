import tkinter as tk
from tkinter import messagebox

# Hesaplama fonksiyonları
def esnek_carpisma(m1, v1i, m2, v2i):
    v1f = ((m1 - m2) / (m1 + m2)) * v1i + ((2 * m2) / (m1 + m2)) * v2i
    v2f = ((2 * m1) / (m1 + m2)) * v1i + ((m2 - m1) / (m1 + m2)) * v2i
    return v1f, v2f

def esnek_olmayan_carpisma(m1, v1i, m2, v2i):
    vf = (m1 * v1i + m2 * v2i) / (m1 + m2)
    return vf

def momentum_hesapla(m, v):
    return m * v

def enerji_hesapla(m, v):
    return 0.5 * m * v ** 2

# Hesapla butonuna basıldığında çalışan fonksiyon
def hesapla():
    try:
        m1 = float(entry_m1.get())
        v1i = float(entry_v1.get())
        m2 = float(entry_m2.get())
        v2i = float(entry_v2.get())
        secim = carpisma_turu.get()

        p_once = momentum_hesapla(m1, v1i) + momentum_hesapla(m2, v2i)
        e_once = enerji_hesapla(m1, v1i) + enerji_hesapla(m2, v2i)

        if secim == "1":
            v1f, v2f = esnek_carpisma(m1, v1i, m2, v2i)
            p_sonra = momentum_hesapla(m1, v1f) + momentum_hesapla(m2, v2f)
            e_sonra = enerji_hesapla(m1, v1f) + enerji_hesapla(m2, v2f)
            sonuc = f"Esnek Çarpışma\nCisim 1 Son Hız: {v1f:.2f} m/s\nCisim 2 Son Hız: {v2f:.2f} m/s"
        elif secim == "2":
            vf = esnek_olmayan_carpisma(m1, v1i, m2, v2i)
            p_sonra = momentum_hesapla(m1 + m2, vf)
            e_sonra = enerji_hesapla(m1 + m2, vf)
            sonuc = f"Esnek Olmayan Çarpışma\nOrtak Hız: {vf:.2f} m/s"
        else:
            messagebox.showerror("Hata", "Lütfen çarpışma türünü seçiniz!")
            return

        momentum_kontrol = "✅ Momentum korunmuş." if abs(p_once - p_sonra) < 0.01 else "❌ Momentum korunmamış."
        enerji_kontrol = "⚡ Enerji korunmuş." if abs(e_once - e_sonra) < 0.01 else "🔥 Enerji korunmamış."

        sonuc += f"\n\nToplam Momentum (önce): {p_once:.2f} kg·m/s"
        sonuc += f"\nToplam Momentum (sonra): {p_sonra:.2f} kg·m/s"
        sonuc += f"\nToplam Enerji (önce): {e_once:.2f} J"
        sonuc += f"\nToplam Enerji (sonra): {e_sonra:.2f} J"
        sonuc += f"\n\n{momentum_kontrol}\n{enerji_kontrol}"

        sonuc_label.config(text=sonuc)

    except ValueError:
        messagebox.showerror("Geçersiz Giriş", "Lütfen tüm alanları doğru şekilde doldurunuz!")

# Arayüz Oluşturma
pencere = tk.Tk()

# Menü çubuğu oluştur
menubar = tk.Menu(pencere)

def yardim_goster():
    bilgi_mesaji = (
        "Momentum ve Enerji Formülleri:\n"
        "\nMomentum (p) = m * v"
        "\nToplam Momentum = m1 * v1 + m2 * v2"
        "\n- m: Kütle (kg), v: Hız (m/s)"
        "\n\nKinetik Enerji (E) = 0.5 * m * v²"
        "\nToplam Enerji = 0.5 * m1 * v1² + 0.5 * m2 * v2²"
        "\n\nSon Hız Formülleri:\n"
        "\nEsnek Çarpışma:\n"
        "v1f = ((m1 - m2)/(m1 + m2)) * v1i + ((2 * m2)/(m1 + m2)) * v2i\n"
        "v2f = ((2 * m1)/(m1 + m2)) * v1i + ((m2 - m1)/(m1 + m2)) * v2i"
        "\n\nEsnek Olmayan Çarpışma:\n"
        "vf = (m1 * v1i + m2 * v2i) / (m1 + m2)"
        "\n\nBu simülasyon, çarpışmalardaki enerji ve momentum değişimini anlamak için tasarlanmıştır."
    )
    messagebox.showinfo("Yardım - Formüller", bilgi_mesaji)

# Yardım menüsü oluştur ve menü çubuğuna ekle
yardim_menusu = tk.Menu(menubar, tearoff=0)
yardim_menusu.add_command(label="Formüller ve Bilgi", command=yardim_goster)
menubar.add_cascade(label="Yardım", menu=yardim_menusu)

# Menü çubuğunu pencereye ata
pencere.config(menu=menubar)
pencere.title("Momentum Simülasyonu")
pencere.geometry("450x500")
pencere.configure(bg="#f0f0f0")

frame = tk.Frame(pencere, padx=10, pady=10, bg="#f0f0f0")
frame.pack()

tk.Label(frame, text="Cisim 1 Kütlesi (kg):").grid(row=0, column=0, sticky="w")
entry_m1 = tk.Entry(frame)
entry_m1.grid(row=0, column=1)

tk.Label(frame, text="Cisim 1 Hızı (m/s):").grid(row=1, column=0, sticky="w")
entry_v1 = tk.Entry(frame)
entry_v1.grid(row=1, column=1)

tk.Label(frame, text="Cisim 2 Kütlesi (kg):").grid(row=2, column=0, sticky="w")
entry_m2 = tk.Entry(frame)
entry_m2.grid(row=2, column=1)

tk.Label(frame, text="Cisim 2 Hızı (m/s):").grid(row=3, column=0, sticky="w")
entry_v2 = tk.Entry(frame)
entry_v2.grid(row=3, column=1)

carpisma_turu = tk.StringVar()
tk.Label(frame, text="Çarpışma Türü:").grid(row=4, column=0, sticky="w")
tk.Radiobutton(frame, text="Esnek", variable=carpisma_turu, value="1").grid(row=4, column=1, sticky="w")
tk.Radiobutton(frame, text="Esnek Olmayan", variable=carpisma_turu, value="2").grid(row=5, column=1, sticky="w")

tk.Button(frame, text="Hesapla", command=hesapla, bg="#4CAF50", fg="white").grid(row=6, columnspan=2, pady=10)

sonuc_label = tk.Label(pencere, text="", justify="left", bg="#f0f0f0", font=("Arial", 10), wraplength=400)
sonuc_label.pack(pady=10)

pencere.mainloop()
