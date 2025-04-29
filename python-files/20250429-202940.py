class Satis:
    def __init__(self, urun_adi, adet, fiyat, odeme_tipi, kime_cekildi=None):
        self.urun_adi = urun_adi
        self.adet = adet
        self.fiyat = fiyat
        self.odeme_tipi = odeme_tipi
        self.kime_cekildi = kime_cekildi

    def toplam_tutar(self):
        return self.adet * self.fiyat

    def __str__(self):
        bilgi = f"{self.urun_adi} x {self.adet} = {self.toplam_tutar()} TL | Ödeme: {self.odeme_tipi}"
        if self.odeme_tipi.lower() == "kredi kartı" and self.kime_cekildi:
            bilgi += f" | Kime çekildi: {self.kime_cekildi}"
        return bilgi


class Magaza:
    def __init__(self):
        self.satislar = []

    def satis_ekle(self, satis):
        self.satislar.append(satis)
        print("Satış eklendi!")

    def rapor_goster(self):
        print("\n--- Günlük Satış Raporu ---")
        toplam = 0
        for s in self.satislar:
            print(s)
            toplam += s.toplam_tutar()
        print(f"Toplam Satış Tutarı: {toplam} TL")


magaza = Magaza()

while True:
    print("\nYeni satış için bilgiler girin (Çıkmak için 'çıkış' yazın):")
    urun_adi = input("Ürün adı: ")
    if urun_adi.lower() == "çıkış":
        break

    try:
        adet = int(input("Adet: "))
        fiyat = float(input("Birim fiyat (TL): "))
    except ValueError:
        print("Lütfen sayısal değer giriniz.")
        continue

    print("Ödeme türü seçin: Nakit / İbana / Kredi Kartı")
    odeme_tipi = input("Ödeme tipi: ").strip().lower()

    kime_cekildi = None
    if odeme_tipi == "kredi kartı":
        kime_cekildi = input("Kime çekildi? (Boş bırakabilirsiniz): ").strip() or None

    satis = Satis(urun_adi, adet, fiyat, odeme_tipi.title(), kime_cekildi)
    magaza.satis_ekle(satis)

    print("Satış başarıyla kaydedildi!")

# Program sonunda rapor
magaza.rapor_goster()