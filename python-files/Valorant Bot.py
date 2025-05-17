import random
import datetime
import json

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
            print("Lütfen 0 ile 1 arasında bir değer girin.")

    kda_gecmis = kda_gecmisini_yukle()
    kda_gecmis.append({"tarih": datetime.date.today().strftime("%d.%m.%Y"), "kills": kills, "deaths": deaths, "assists": assists, "headshot": headshot_orani})

    # Son 30 günü koru
    if len(kda_gecmis) > 30:
        kda_gecmis = kda_gecmis[-30:]

    kda_gecmisini_kaydet(kda_gecmis)
    print("KDA ve headshot bilgileri kaydedildi.")
    kda_ortalama_hesapla()

def kda_ortalama_hesapla():
    """Kaydedilen son 30 günlük KDA bilgilerinin ortalamasını hesaplar."""
    kda_gecmis = kda_gecmisini_yukle()
    if not kda_gecmis:
        print("Henüz KDA bilgisi girilmedi.")
        return

    son_30_gun = kda_gecmis[-30:]

    toplam_k = sum(kayit["kills"] for kayit in son_30_gun)
    toplam_d = sum(kayit["deaths"] for kayit in son_30_gun)
    toplam_a = sum(kayit["assists"] for kayit in son_30_gun)
    toplam_mac = len(son_30_gun)

    ortalama_k = toplam_k / toplam_mac if toplam_mac > 0 else 0
    ortalama_d = toplam_d / toplam_mac if toplam_mac > 0 else 0
    ortalama_a = toplam_a / toplam_mac if toplam_mac > 0 else 0

    print("\n--- Son 30 Günün Ortalama KDA'sı ---")
    print(f"Toplam Maç (Son 30 Gün): {toplam_mac}")
    print(f"Ortalama Öldürme: {ortalama_k:.2f}")
    print(f"Ortalama Ölüm: {ortalama_d:.2f}")
    print(f"Ortalama Asist: {ortalama_a:.2f}")

def headshot_ortalama_hesapla():
    """Kaydedilen son 30 günlük headshot oranlarının ortalamasını hesaplar."""
    kda_gecmis = kda_gecmisini_yukle()
    if not kda_gecmis:
        print("Henüz KDA bilgisi girilmedi.")
        return

    son_30_gun = kda_gecmis[-30:]
    toplam_headshot = sum(kayit["headshot"] for kayit in son_30_gun if "headshot" in kayit)
    kayit_sayisi = sum(1 for kayit in son_30_gun if "headshot" in kayit)

    if kayit_sayisi > 0:
        ortalama_headshot = toplam_headshot / kayit_sayisi
        print("\n--- Son 30 Günün Ortalama Headshot Oranı ---")
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
        print("7. Çıkış")

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
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.")

if _name_ == "_main_":
    menu()
