def sifreleme():
    puan=0
    sifreleme=sifre_giris.get()
    harfler="abcdefgğhıijklmnoöprsştuüvyz"
    sayilar="1234578910"
    if "!" in sifreleme or "?" in sifreleme:
        puan+=1
    if "@" in sifreleme or "*" in sifreleme:
        puan+=1
    if len (sifreleme)>=7:
        puan+=1
    if any(sayi in sifreleme for sayi in sayilar):
        puan+=1
    if  any(harf in sifreleme for harf in harfler):
        puan+=1
    if puan<=1:
        sifre_sonuc.config(text="zayif")
    elif puan==2:
       sifre_sonuc.config(text="ortalama")
    else:
       sifre_sonuc.config(text="güçlü")

    
from tkinter import *

arayüz=Tk()
arayüz.title("sifre kontrolcüsü")
arayüz.geometry("700x500")
canvas=Canvas(arayüz,height=500,width=700)
canvas.pack
frame_renk=Frame(arayüz,bg="#add8e6")
frame_renk.place(relx=0.1,rely=0.1,relwidth=0.75,relheight=0.1)
sifre_puanlama=Label(frame_renk, bg='#add8e6',text="Puanlama Yeri:")
sifre_puanlama.pack()
sifre_giris=Entry(font=("Arial",12))
sifre_giris.place(relx=0.5,rely=0.45, anchor="center")
kontrol_düğmesi=Button(arayüz,text="şifreye bak",font =("Arial",12),command=sifreleme)
kontrol_düğmesi.place(relx=0.5,rely=0.6, anchor="center")
sifre_sonuc=Label(arayüz,text="", font=("Arial",12))
sifre_sonuc.place(relx=0.5,rely=0.7, anchor="center")
arayüz.mainloop()