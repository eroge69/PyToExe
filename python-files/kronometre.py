import time

def enter_bekle():
    while True:
        giris = input("Enter tuşuna basın: ")
        if giris == "":
            break
        else:
            print("Sadece Enter tuşuna basın.")

print("Kronometre başlatılacak.")
enter_bekle()
baslangic = time.time()

print("Kronometre başladı. Durdurmak için tekrar Enter'a basın.")
enter_bekle()
bitis = time.time()

gecen_sure = bitis - baslangic
dakika = int(gecen_sure // 60)
saniye = int(gecen_sure % 60)

print(f"Geçen süre: {dakika} dakika {saniye} saniye")

input("Kapatmak için Enter'a basın.")

