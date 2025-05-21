
def hesapla_rt(r0, alpha, t):
    """a şıkkı: Sıcaklıktan RT hesaplama"""
    return r0 * (1 + alpha * t)

def hesapla_t(r0, alpha, rt):
    """b şıkkı: RT'den sıcaklık hesaplama"""
    return (rt - r0) / (r0 * alpha)

def main():
    print("RTD (Direnç Sıcaklık Dedektörü) Hesaplayıcı")
    print("-------------------------------------------")
    
    r0 = float(input("R₀ (örn: 100): "))
    
    # Kullanıcıdan α seçimi
    print("α (sıcaklık katsayısı) seçiniz:")
    print("1 - 0.00385 (PT100)")
    print("2 - 0.00391")
    print("3 - 0.00392")
    secim = input("Seçim (1/2/3): ")
    alpha_dict = {"1": 0.00385, "2": 0.00391, "3": 0.00392}
    alpha = alpha_dict.get(secim, 0.00385)

    # İşlem seçimi
    print("\nHangi hesaplamayı yapmak istiyorsunuz?")
    print("a - T'den RT hesapla")
    print("b - RT'den T hesapla")
    tercih = input("Tercih (a/b): ")

    if tercih == 'a':
        t = float(input("Sıcaklık T (°C): "))
        rt = hesapla_rt(r0, alpha, t)
        print(f"RT = {rt:.3f} Ω")

    elif tercih == 'b':
        rt = float(input("Direnç RT (Ω): "))
        t = hesapla_t(r0, alpha, rt)
        print(f"T = {t:.2f} °C")

    else:
        print("Geçersiz tercih.")

if __name__ == "__main__":
    main()
