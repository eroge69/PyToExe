import random
import datetime
import json
import csv

KDA_DOSYASI = "kda_gecmisi.json"
ANTRENMAN_DOSYASI = "antrenman_sirasi.json"
RANK_DOSYASI = "rank_gecmisi.json"
ANTRENMAN_PLANI = [
    {"ad": "Isınma", "sure": 5, "detay": "Atış poligonunda temel hedef alıştırmaları."},
    {"ad": "Aim Geliştirme", "sure": 15, "detay": "Ölüm maçında nişan odaklı oyun."},
    {"ad": "Refleks Çalışması", "sure": 10, "detay": "Atış poligonunda ani tepki alıştırmaları."},
    {"ad": "Spike Kurma/Çözme", "sure": 10, "detay": "Derecesiz veya özel oyunda spike senaryoları."},
    {"ad": "Harita Bilgisi", "sure": 15, "detay": "Belirli bir haritada keşif ve pozisyon alma."},
    {"ad": "Taktiksel Analiz", "sure": 20, "detay": "Son maçın tekrarını izleyip hataları/geliştirilebilecek yönleri belirleme."},
]
ANTRENMAN_SURESI = 30

def kda_gecmisini_yukle():
    """KDA geçmişini dosyadan yükler."""
    try:
        with open(KDA_DOSYASI, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def kda_gecmisini_kaydet(gecmis):
    """KDA geçmişini dosyaya kaydeder."""
    with open(KDA_DOSYASI, 'w') as f:
        json.dump(gecmis, f)

def antrenman_sirasini_yukle():
    """Antrenman sırasını dosyadan yükler."""
    try:
        with open(ANTRENMAN_DOSYASI, 'r') as f:
            data = json.load(f)
            return data.get('index', 0)
    except FileNotFoundError:
        return 0

def antrenman_sirasini_kaydet(index):
    """Antrenman sırasını dosyaya kaydeder."""
    with open(ANTRENMAN_DOSYASI, 'w') as f:
        json.dump({'index': index}, f)

def rank_gecmisini_yukle():
    """Rank geçmişini dosyadan yükler."""
    try:
        with open(RANK_DOSYASI, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def rank_gecmisini_kaydet(gecmis):
    """Rank geçmişini dosyaya kaydeder."""
    with open(RANK_DOSYASI, 'w') as f:
        json.dump(gecmis, f)

def gunluk_antrenman_plani_olustur():
    """Sıralı bir şekilde günlük antrenman planı oluşturur."""
    index = antrenman_sirasini_yukle()
    bugunun_plani = []
    for i in range(random.randint(2, 4)): # 2 ile 4 arasında rastgele aktivite seç
        secilen_index = (index + i) % len(ANTRENMAN_PLANI)
        bugunun_plani.append(ANTRENMAN_PLANI[secilen_index])

    print("\n--- Günlük Antrenman Planı ({}) ---".format(datetime.date.today().strftime("%d.%m.%Y")))
    for aktivite in bugunun_plani:
        print(f"- {aktivite['ad']}: {aktivite['sure']} dakika ({aktivite['detay']})")
    print("İyi antrenmanlar!")

    antrenman_sirasini_kaydet((index + len(bugunun_plani)) % len(ANTRENMAN_PLANI))

def kda_ve_headshot_kaydet():
    """Kullanıcıdan KDA ve headshot bilgilerini alır ve kaydeder."""
    while True:
        try:
            kills = int(input("Kazanılan öldürme sayısı: "))
            deaths = int(input("Verilen ölüm sayısı: "))
            assists = int(input("Yapılan asist sayısı: "))
            headshot_orani = float(input("Headshot oranı (0-1 arası): "))
            if 0 <= headshot_orani <= 1:
                break
            else:
                print("Lütfen 0 ile 1 arasında bir değer girin.")
        except ValueError:
            print("Lütfen sayısal değerler girin.")

    kda_gecmis = kda_gecmisini_yukle()
    kda_gecmis.append({"tarih": datetime.date.today().strftime("%d.%m.%Y"), "kills": kills, "deaths": deaths, "assists": assists, "headshot": headshot_orani})

    # Son 30 günü koru
    if len(kda_gecmis) > 30:
        kda_gecmis = kda_gecmis[-30:]

    kda_gecmisini_kaydet(kda_gecmis)
    print("KDA ve headshot bilgileri kaydedildi.")
    kda_ortalama_hesapla()

def kda_ortalama_hesapla(gecmis=None):
    """Verilen geçmişteki KDA bilgilerinin ortalamasını hesaplar (varsayılan son 30 gün)."""
    if gecmis is None:
        gecmis = kda_gecmisini_yukle()[-30:]
        if not gecmis:
            print("Henüz KDA bilgisi girilmedi.")
            return
        print("\n--- Son 30 Günün Ortalama KDA'sı ---")
    else:
        if not gecmis:
            print("Belirtilen tarih aralığında KDA bilgisi bulunamadı.")
            return
        print(f"\n--- {gecmis[0]['tarih']} - {gecmis[-1]['tarih']} Arası Ortalama KDA ---")

    toplam_k = sum(kayit["kills"] for kayit in gecmis)
    toplam_d = sum(kayit["deaths"] for kayit in gecmis)
    toplam_a = sum(kayit["assists"] for kayit in gecmis)
    toplam_mac = len(gecmis)

    ortalama_k = toplam_k / toplam_mac if toplam_mac > 0 else 0
    ortalama_d = toplam_d / toplam_mac if toplam_mac > 0 else 0
    ortalama_a = toplam_a / toplam_mac if toplam_mac > 0 else 0

    print(f"Toplam Maç: {toplam_mac}")
    print(f"Ortalama Öldürme: {ortalama_k:.2f}")
    print(f"Ortalama Ölüm: {ortalama_d:.2f}")
    print(f"Ortalama Asist: {ortalama_a:.2f}")

def headshot_ortalama_hesapla(gecmis=None):
    """Verilen geçmişteki headshot oranlarının ortalamasını hesaplar (varsayılan son 30 gün)."""
    if gecmis is None:
        gecmis = kda_gecmisini_yukle()[-30:]
        if not gecmis:
            print("Henüz KDA bilgisi girilmedi.")
            return
        print("\n--- Son 30 Günün Ortalama Headshot Oranı ---")
    else:
        if not gecmis:
            print("Belirtilen tarih aralığında headshot bilgisi bulunamadı.")
            return
        print(f"\n--- {gecmis[0]['tarih']} - {gecmis[-1]['tarih']} Arası Ortalama Headshot Oranı ---")

    toplam_headshot = sum(kayit["headshot"] for kayit in gecmis if "headshot" in kayit)
    kayit_sayisi = sum(1 for kayit in gecmis if "headshot" in kayit)

    if kayit_sayisi > 0:
        ortalama_headshot = toplam_headshot / kayit_sayisi
        print(f"Ortalama Headshot Oranı: {ortalama_headshot:.2f}")
    else:
        print("Henüz headshot bilgisi girilmedi.")

def rank_bilgisi_gir():
    """Kullanıcıdan mevcut rank ve maç bilgilerini alır."""
    mevcut_rank = input("Mevcut rankınız (örneğin: Iron 1, Gold 3): ")
    while True:
        try:
            gecen_sure_gun = int(input("Bu rankta kaç gündür bulunuyorsunuz? "))
            oynanan_mac = int(input("Bu rankta kaç maç oynadınız? "))
            kazanilan_mac = int(input("Bu rankta kaç maç kazandınız? "))
            kaybedilen_mac = oynanan_mac - kazanilan_mac
            kazanma_orani = (kazanilan_mac / oynanan_mac) * 100 if oynanan_mac > 0 else 0
            kaybetme_orani = (kaybedilen_mac / oynanan_mac) * 100 if oynanan_mac > 0 else 0
            break
        except ValueError:
            print("Lütfen sayısal değerler girin.")
        except ZeroDivisionError:
            print("Oynanan maç sayısı sıfır olamaz.")

    rank_gecmis = rank_gecmisini_yukle()
    rank_gecmis.append({
        "tarih": datetime.date.today().strftime("%d.%m.%Y"),
        "rank": mevcut_rank,
        "gecen_sure": gecen_sure_gun,
        "oynanan": oynanan_mac,
        "kazanilan": kazanilan_mac,
        "kaybedilen": kaybedilen_mac,
        "kazanma_orani": kazanma_orani,
        "kaybetme_orani": kaybetme_orani
    })
    rank_gecmisini_kaydet(rank_gecmis)
    print("\nRank bilgileri kaydedildi.")

def rank_gecmisini_goster():
    """Kaydedilen rank geçmişini gösterir."""
    rank_gecmis = rank_gecmisini_yukle()
    if not rank_gecmis:
        print("Henüz rank bilgisi girilmedi.")
        return

    print("\n--- Rank Geçmişi ---")
    for kayit in rank_gecmis:
        print(f"Tarih: {kayit['tarih']}")
        print(f"Rank: {kayit['rank']}")
        print(f"Geçen Süre: {kayit['gecen_sure']} gün")
        print(f"Oynanan Maç: {kayit['oynanan']}")
        print(f"Kazanılan Maç: {kayit['kazanilan']}")
        print(f"Kaybedilen Maç: {kayit['kaybedilen']}")
        print(f"Kazanma Oranı: {kayit['kazanma_orani']:.2f}%")
        print(f"Kaybetme Oranı: {kayit['kaybetme_orani']:.2f}%")
        print("-" * 20)

def kda_gecmisini_csv_aktar():
    """KDA geçmişini CSV dosyasına aktarır."""
    kda_gecmis = kda_gecmisini_yukle()
    if not kda_gecmis:
        print("Henüz KDA bilgisi girilmedi.")
        return

    dosya_adi = "kda_gecmisi.csv"
    alan_adlari = kda_gecmis[0].keys() if kda_gecmis else ["tarih", "kills", "deaths", "assists", "headshot"]

    with open(dosya_adi, 'w', newline='') as csvfile:
        yazici = csv.DictWriter(csvfile, fieldnames=alan_adlari)
        yazici.writeheader()
        yazici.writerows(kda_gecmis)

    print(f"\nKDA geçmişi '{dosya_adi}' dosyasına aktarıldı.")

def kda_gecmisini_tarih_araligina_gore_goster():
    """Belirli bir tarih aralığındaki KDA geçmişini gösterir."""
    kda_gecmis = kda_gecmisini_yukle()
    if not kda_gecmis:
        print("Henüz KDA bilgisi girilmedi.")
        return

    baslangic_str = input("Başlangıç tarihi (YYYY-MM-DD): ")
    bitis_str = input("Bitiş tarihi (YYYY-MM-DD): ")

    try:
        baslangic_tarih = datetime.datetime.strptime(baslangic_str, "%Y-%m-%d").date()
        bitis_tarih = datetime.datetime.strptime(bitis_str, "%Y-%m-%d").date()
    except ValueError:
        print("Geçersiz tarih formatı. Lütfen YYYY-MM-DD formatında girin.")
        return

    secilen_gecmis = [kayit for kayit in kda_gecmis if baslangic_tarih <= datetime.datetime.strptime(kayit['tarih'], "%d.%m.%Y").date() <= bitis_tarih]

    if secilen_gecmis:
        print("\n--- Belirtilen Tarih Aralığındaki KDA Geçmişi ---")
        for kayit in secilen_gecmis:
            print(f"Tarih: {kayit['tarih']}")
            print(f"Öldürme: {kayit['kills']}")
            print(f"Ölüm: {kayit['deaths']}")
            print(f"Asist: {kayit['assists']}")
            if "headshot" in kayit:
                print(f"Headshot Oranı: {kayit['headshot']:.2f}")
            print("-" * 20)
        kda_ortalama_hesapla(secilen_gecmis)
        headshot_ortalama_hesapla(secilen_gecmis)
    else:
        print("Belirtilen tarih aralığında KDA bilgisi bulunamadı.")

def menu():
    """Kullanıcıya seçenekler sunan ana menü."""
    while True:
        print("\nValorant Günlük Takip Botu")
        print("1. Günlük Antrenman Planı Oluştur")
        print("2. KDA ve Headshot Bilgisi Gir")
        print("3. Son 30 Günün Ortalama KDA'sını Göster")
        print("4. Son 30 Günün Ortalama Headshot Oranını Göster")
        print("5. Rank Bilgisi Gir")
        print("6. Rank Geçmişini Göster")
        print("7. KDA Geçmişini CSV'ye Aktar")
        print("8. KDA Geçmişini Tarih Aralığına Göre Göster")
        print("9. Çıkış")

        secim = input("Seçiminizi yapın: ")

        if secim == '1':
            gunluk_antrenman_plani_olustur()
        elif secim == '2':
            kda_ve_headshot_kaydet()
        elif secim == '3':
            kda_ortalama_hesapla()
        elif secim == '4':
            headshot_ortalama_hesapla()
        elif secim == '5':
            rank_bilgisi_gir()
        elif secim == '6':
            rank_gecmisini_goster()
        elif secim == '7':
            kda_gecmisini_csv_aktar()
        elif secim == '8':
            kda_gecmisini_tarih_araligina_gore_goster()
        elif secim == '9':
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.")

if __name__ == "__main__":
    menu()