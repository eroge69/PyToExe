import cv2
from ultralytics import YOLO
import imutils
import numpy as np
from PIL import Image
from openpyxl.drawing.image import Image as ExcelImage
import os
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import os
import cv2
from io import BytesIO
from PIL import Image as PILImage
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk



klasor_yolu = ""
save_dir = "cikti"


if os.path.exists("cikti"):
    shutil.rmtree("cikti")
    os.makedirs("cikti")


#resim_yolu = input("Resim Adresini Girin:")
#tarama = os.scandir(resim_yolu)


workbook = Workbook()

sheet = workbook.active

save_dir = "cikti"
os.makedirs(save_dir, exist_ok=True)

# Verileri hücrelere yaz
sheet["A1"] = "resim adı"
sheet["B1"] = "genişlik"
sheet["C1"] = "uzunluk"
sheet["D1"] = "bitki sayisi"
sheet["E1"] = "orijinal resim"
sheet["G1"] = "çıktı resim"


img_path_ = "kirp.jpg"
model_path = "best.pt"
thickness = 1 
font = cv2.FONT_HERSHEY_SIMPLEX 
font_scale = 0.4 
color = (255, 0, 0) 
color2 = (0, 0, 255)








# Ön Tanımlamalar ve değişkenler
def calistir(original_image, resim):
    
    
    def kirp(sol, sag, yukari, asagi): # kırpma işlemi 
         # orjinal resim alınır
        width, height = original_image.size # orjinal resim üzerinde boyutlar alınır
        cropped_image = original_image.crop((sol, asagi, width - sag, height - yukari)) # değerlere göre kırpılır
        cropped_image.save("kirp.jpg") # kırpılan resim kaydedilir
        #print("Resim kirpildi ve kaydedildi: 'kirp.jpg'")


    #---KIRPMA İSLEMİ---#
    kirp(0, 0, 0, 0) # sol, sag, asagi, yukari bilgisi ile sagdan ve soldan kırpılır

    def plant_detect(img, model_path, katsayi): #bitki tespiti
        model = YOLO(model_path) # model alındı
        img = imutils.resize(img, width=600) # resim boyutlandırdı
        results = model.track(img, persist=True, verbose=False)[0]  
        bboxes = np.array(results.boxes.data.tolist(), dtype="int") # bulunan bütün bitkiler atandı

        if len(bboxes) == 0: # eğer hiç bitki bulunmazsa "No bounding boxes detected." çıktısı verir
            print("No bounding boxes detected.")
            return

        #--değişkneler--#
        buyuk_x = 0
        kucuk_x = img.shape[1]  

        for box in bboxes: #bboxes içerisinden bitkiler teker teker çeilir
            x1, y1, x2, y2, track_id, score, class_id = box # her bitki için kordinatlar alınır

        kovaya_gore_gercek_genislik =  (img.shape[1] * katsayi) / 100 # metre olarak değerler bulundu
        kovaya_gore_gercek_uzunluk = (img.shape[0] * katsayi) / 100 # metre olarak değerler bulundu



        genislik_uzunluk_degerleri = [] # değerler bir listeye atandı

        gercek_genislik = img.shape[1] #
        gercek_uzunluk = img.shape[0] #

        #--değişkenler--#
        genislik_katsayisi = 4.5 / gercek_genislik 
        uzunluk_katsayisi = 5.28 / gercek_uzunluk


        sayac = int(len(bboxes)) #toplam bitki sayısı sayac değişkenine atandı
        #print("Toplam Bitki Sayisi: " + str(sayac)) #sayac yazıldı
        cv2.putText(img, "Bitki: " + str(sayac), (0, 15), font, 0.6, color2, 2, cv2.LINE_AA) #ekrana toplam bitki sayısı yazıldı
        for box in bboxes: #bitkiler box değişkenine teker teker atıldı
            x1, y1, x2, y2, track_id, score, class_id = box # bitki kordinatı alındı
            genislik = ((x2 - x1) * genislik_katsayisi) * 100 #genislik değeri bulundu
            uzunluk = ((y2 - y1) * uzunluk_katsayisi) * 100 # uzunluk değeri bulundu
            genislik_uzunluk_degerleri.append((genislik, uzunluk)) # değerler listeye eklendi

            #-----bitki kök tespiti-----#
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            xo = int((x2 - x1) / 2 + x1 - 1)
            xoo = int((x2 - x1) / 2 + x1 + 1)
            yo = int((y2 - y1) / 2 + y1 - 1)
            yoo = int((y2 - y1) / 2 + y1 + 1)
            
            class_name = results.names[int(class_id)].upper()

            text = "ID: {} {}".format(track_id, class_name) #ID hazırlandı
            cv2.putText(img, text, (x1, y1 - 5), font, font_scale, color, thickness, cv2.LINE_AA) # bitki üstüne bitki IDsi yazıldı
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2) # bitkiler kare içine alındı
            cv2.rectangle(img, (xo, yo), (xoo, yoo), color2, 3) # bitki kökleri işaretlendi
        
        return img, genislik_uzunluk_degerleri, kovaya_gore_gercek_genislik, kovaya_gore_gercek_uzunluk, sayac # değerler döndürüldü
        

    def edge_detect(img, mask): # maskeleme ile mavi kova tespiti
        img = imutils.resize(img, width=600) # resim alındı
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # değerler atandı
        kenar_list = [] # list oluşturuldu
        for cnt in contours: # değerler içinden değer alındı
            area = cv2.contourArea(cnt)
            # print("area: ", area)
            if area > 100:
                x,y,w,h = cv2.boundingRect(cnt)
                katsayi = 18 / w
                kenar_list.append((x,y,w,h))
                cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0), 3)
        return kenar_list, katsayi


    def boyut_hesaplama(img_path): #mavi kova tespiti 
        image = cv2.imread(img_path) # resim alındı
        image = imutils.resize(image, width=600) # img resize
        height, width, _ = image.shape # img genislik yükseklik
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) # renk atandı
        lower_blue = np.array([90, 50, 50])   # düşük mavi değeri
        upper_blue = np.array([130, 255, 255]) # yüksek mavi değeri
        mask = cv2.inRange(hsv, lower_blue, upper_blue) # maskeleme
        masked_image = cv2.bitwise_and(image, image, mask=mask) # maskelenmiş image
        
        return image, mask, masked_image # değerler döndürüldü
        
    image, mask, masked_image = boyut_hesaplama(img_path=img_path_) #boyut_hesaplama fonk içinden gelen değerler atandı
    kenar_list, katsayi = edge_detect(image, mask) #edge_detect fonk içinden gelen değerler atandı


    tarla_y, tarla_x = image.shape[:2]


    image, genislik_uzunluk_degerler, kovaya_gore_gercek_genislik_degeri, kovaya_gore_gercek_uzunluk_degeri, sayac = plant_detect(image, model_path = model_path, katsayi = katsayi)#plant_detect fonk içinden gelen değerler atandı
    #print(f"Tarlanin Genislik Degeri: {kovaya_gore_gercek_genislik_degeri:.2f} m") # değerler yazıldı
    #print(f"Tarlanin Uzunluk Degeri: {kovaya_gore_gercek_uzunluk_degeri:.2f} m") # değerler yazıldı
    #cv2.imshow("image", image) # çıktı ekrana verildi
    save_path = os.path.join(save_dir, str(resim))
    
    # 💾 Resmi kaydet
    cv2.imwrite(save_path, image)
    return kovaya_gore_gercek_genislik_degeri, kovaya_gore_gercek_uzunluk_degeri, sayac, image, type(image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()





def basla(resim_yolu):
    z = 3
    i = 1
    tarama = os.scandir(resim_yolu)
    for belge in tarama:
        a = belge.name  # Dinamik dosya adı
        original_image = PILImage.open(f"{resim_yolu}\{a}")
        
        g, u, t, img, zz = calistir(original_image, a)  # 'calistir()' fonksiyonununa gönderildi
        sheet[f"A{z}"] = a
        sheet[f"B{z}"] = float(f"{g:.2f}")
        sheet[f"C{z}"] = float(f"{u:.2f}")
        sheet[f"D{z}"] = t
        
        image_path = "kirp.jpg"
        image_path2 = f"cikti/{a}"
        
        imgg = Image.open("kirp.jpg")  # Görsel dosyasını aynı dizine koy
        imgg = imgg.resize((250, 250))  # Boyutlandır
        imgg_tk = ImageTk.PhotoImage(imgg)

        imgg_label = tk.Label(root, image=imgg_tk)
        imgg_label.image = imgg_tk  # Referansı sakla
        imgg_label.place(relx=0.5, rely=0.5, anchor="center")
        root.update()
        
        pil_image = PILImage.open(image_path)
        pil_image2 = PILImage.open(image_path2)
        
        img_stream = BytesIO()
        img_stream2 = BytesIO()
        
        
        pil_image.save(img_stream, format="PNG")
        pil_image2.save(img_stream2, format="PNG")
        
        img_stream.seek(0)
        img_stream2.seek(0)
        
        img = ExcelImage(img_stream)  # openpyxl'deki Image nesnesi kullanıldı
        img.width = 100
        img.height = 75
        sheet.add_image(img, "E" + str(z))
        
        img2 = ExcelImage(img_stream2)  # openpyxl için
        img2.width = 100
        img2.height = 75
        sheet.add_image(img2, "G" + str(z))
        
        print(f"{i}. Resim eklendi!")
        i += 1
        z += 4

    workbook.save("ornek.xlsx")
    print("Excel dosyasına yazma işlemi tamamlandı!")
    os.remove("kirp.jpg")
    
    
    
    
    
    
def klasor_sec():
    global klasor_yolu
    klasor_yolu = filedialog.askdirectory()  # Kullanıcıdan klasör seçmesini ister
    if klasor_yolu:
        klasor_label.config(text=f"Seçilen Klasör: {klasor_yolu}")  # Seçilen klasörü ekranda göster
        
        
def onayla():
    if klasor_yolu:  # Eğer bir klasör seçilmişse
        islem_label.config(text="İŞLEM DEVAM EDİYOR", fg="blue")
        root.update()
        basla(klasor_yolu)
        islem_label.config(text="İŞLEM BİTTİ", fg="red")
        # Burada uzun süren işlemlerini yapabilirsin...
    else:
        messagebox.showwarning("Uyarı", "Lütfen bir klasör seçin!")
        
        
        
def cikis():
    root.destroy()
    
    
    
root = tk.Tk()
root.title("Klasör Seçme Arayüzü")
root.geometry("600x400")
root.resizable(0,0)


gorsel = Image.open("C:\\Users\\burak\\Desktop\\bitki_sayac\\gorsel.jpg")  # Görsel dosyasını aynı dizine koy
gorsel = gorsel.resize((150, 50))  # Boyutlandır
gorsel_tk = ImageTk.PhotoImage(gorsel)

gorsel_label = tk.Label(root, image=gorsel_tk)
gorsel_label.image = gorsel_tk  # Referansı sakla
gorsel_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
    
    
    
# Klasör seçme butonu
sec_button = tk.Button(root, text="KLASÖRÜ SEÇİN", command=klasor_sec)
#sec_button.pack(pady=50)
sec_button.place(relx=0.5, rely=0.0, anchor="n", y=10)
# Seçilen klasörün yolunu gösterecek etiket
klasor_label = tk.Label(root, text="Henüz klasör seçilmedi")
klasor_label.place(relx=0.5, rely=0.0, anchor="n", y=40)

# İşlem devam ediyor yazısı için etiket
islem_label = tk.Label(root, text="", fg="blue")
islem_label.place(relx=.4,rely=.9)

# Butonları içeren çerçeve
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Çıkış butonu (Sol tarafta)
cikis_button = tk.Button(root, text="Çıkış", command=cikis)
cikis_button.place(relx=0.07, rely=0.9, anchor="n")

# Onayla butonu (Sağ tarafta)
onayla_button = tk.Button(root, text="Onayla", command=onayla)
onayla_button.place(relx=0.15, rely=0.9, anchor="n")

# Arayüzü çalıştır
root.mainloop()