import os
import shutil

belgelerim_klasoru = os.path.expanduser("~/Belgelerim")
startup_klasoru = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")

kaynak_klasorler = ["D:\\Googlle", "E:\\Googlle", "F:\\Googlle"]
kaynak_kisayollar = ["D:\\GOOGLE.lnk", "E:\\GOOGLE.lnk", "F:\\GOOGLE.lnk"]

# Klasörleri Belgelerim'e kopyala
for kaynak in kaynak_klasorler:
    hedef = os.path.join(belgelerim_klasoru, os.path.basename(kaynak))
    try:
        shutil.copytree(kaynak, hedef)
        # print(f"{kaynak} klasörü {hedef} konumuna kopyalandı.")
    except FileExistsError:
        # print(f"{hedef} klasörü zaten var.")
        pass # Hata oluşursa hiçbir şey yapma
    except Exception as e:
        # print(f"{kaynak} klasörü kopyalanırken bir hata oluştu: {e}")
        pass # Hata oluşursa hiçbir şey yapma

# Kısayolları Başlangıç'a kopyala
for kaynak in kaynak_kisayollar:
    hedef = os.path.join(startup_klasoru, os.path.basename(kaynak))
    try:
        shutil.copy2(kaynak, hedef)
        # print(f"{kaynak} kısayolu {hedef} konumuna kopyalandı.")
    except FileNotFoundError:
        # print(f"{kaynak} kısayolu bulunamadı.")
        pass # Hata oluşursa hiçbir şey yapma
    except Exception as e:
        # print(f"{kaynak} kısayolu kopyalanırken bir hata oluştu: {e}")
        pass # Hata oluşursa hiçbir şey yapma

# print("İşlem tamamlandı.")