from tkinter import *
layar = Tk()
layar.title("Rumus Listrik 3 Pahse")
layar.geometry("410x300")


c = 1.73    # Akar 3
d = 0.8  # Factor daya
e = 1000   # Satuan daya dalam Watt
g = 56  # Daya hantar jenis tembaga
h = 380 # sumber twegangan 3 phase
l = 0.000000017 # Tahanan Jenis ( rho = 1,7 x 10 pangkat-8)
m = 1000000 # konversi dari KM ke meter

#Menu = LabelFrame(layar,text="Made in ME", padx=10, pady=10 )
Menu = LabelFrame(layar,text="MADE IN TEAM ELECTRICAL", height=110, width= 375 )
Menu.place(y = 6, x = 20)


Volt = Label(Menu,text="Volt  :")
Volt.place(x = 13, y= 20)
Arus = Label(Menu,text="Arus      :")
Arus.place(x = 110, y= 20)
Daya = Label(Menu,text="Daya :")
Daya.place(x = 13, y= 50)
Pkbl = Label(Menu,text="P.Kabel     :")
Pkbl.place(x = 222, y= 20)
Dkbl = Label(Menu,text="D.Kabel :")
Dkbl.place(x = 110, y= 50)
Thilang = Label(Menu,text="Tg.Hilang :")
Thilang.place(x = 222, y= 50)

Volt_1 = Entry(Menu, width=7)
Volt_1.place(x = 51,y = 20)
Arus_1 = Entry(Menu,width=7)
Arus_1.place(x = 165,y = 20)
Daya_1 = Entry(Menu,width=7)
Daya_1.place(x = 52,y = 50)
Pkbl_1 = Entry(Menu,width=7)
Pkbl_1.place(x = 285,y = 20)
Dkbl_1 = Entry(Menu,width=7)
Dkbl_1.place(x = 165,y = 50)
Thilang_1 = Entry(Menu,width=7)
Thilang_1.place(x = 285,y = 50)

display = LabelFrame(layar,height=110, width= 375 )
display.place(y = 170, x = 20)
Text_display = Label(layar,text="HASIL",).place(y = 160, x = 175)

Textdisplay_1 = Label(layar)
Textdisplay_1.place(y = 185, x = 25)
Textdisplay_2 = Label(layar)
Textdisplay_2.place(y = 210, x = 25)

chek = {"rumus","yes"}

def rumus(rm):
  kotaksatu = cliked.get()
  
  global Volt,Arus,Daya,Pkbl,Dkbl,Thilang,Volt_1,Arus_1,Daya_1,Pkbl_1,Dkbl_1,Thilang_1,Textdisplay_1,Textdisplay_2
  if "rumus" in chek:
    Volt.place_forget()
    Arus.place_forget()
    Daya.place_forget()
    Pkbl.place_forget()
    Dkbl.place_forget()
    Thilang.place_forget()
    Volt_1.place_forget()
    Arus_1.place_forget()
    Daya_1.place_forget()
    Pkbl_1.place_forget()
    Dkbl_1.place_forget()
    Thilang_1.place_forget()
    Textdisplay_1.place_forget()
    Textdisplay_2.place_forget()
    
  if kotaksatu=="Mencari nilai daya":
    Volt.place(x = 13, y= 20)
    Volt_1.place(x = 51,y = 20)
    Arus.place(x = 110, y= 20)
    Arus_1.place(x = 165,y = 20)
    input_1 = int(Volt_1.get())
    input_2 = int(Arus_1.get()) 
    hitungan = (input_1*input_2*c*d/e)
    hasil1 = "Dayanya adalah : " + "%.2f"%hitungan + " KW"
      
  elif kotaksatu=="Mencari nilai arus":
    Volt.place(x = 13, y= 20)
    Volt_1.place(x = 51,y = 20)
    Daya.place(x = 110, y= 20)
    Daya_1.place(x = 165,y = 20)
    input_1 = int(Volt_1.get())
    input_3 = int(Daya_1.get())
    hitungan = (input_3*e)/(input_1*c*d)
    Factor_safety = hitungan*1.25 
    hasil1 = "Besar arus yang mengalir adalah : " + "%.2f"%hitungan + "  Amper" 
    hasil2 = "Nilai MCB dengan factor safety 125% adalah : " + "%.2f"%Factor_safety + "  Amper"
     
  elif kotaksatu=="Mencari diameter kabel":
    Daya.place(x = 247, y= 20)
    Daya_1.place(x = 285,y = 20)
    Pkbl.place(x = 13, y= 20)
    Pkbl_1.place(x = 76,y = 20)
    Thilang.place(x = 130, y= 20)
    Thilang_1.place(x = 193,y = 20)
    input_3 = int(Daya_1.get())
    input_4 = int(Pkbl_1.get())
    input_5 = int(Thilang_1.get())
    hitungan = (input_4*(input_3*e)/(input_5*h*g))
    Factor_safety = hitungan*1.25
    hasil1 = "Diameter kabel adalah : " + "%.2f"%hitungan + " mm"
    hasil2 = "Diameter kabel dengan factor safety 125% adalah : " + "%.2f"%Factor_safety + " mm"
    Menu.place(y = 6, x = 20)
  elif kotaksatu=="Mencari drop tegangan":
    Pkbl.place(x = 222, y= 20)
    Pkbl_1.place(x = 285,y = 20)
    Arus.place(x = 117, y= 20)
    Arus_1.place(x = 170,y = 20)
    Dkbl.place(x = 13, y= 20)
    Dkbl_1.place(x = 65,y = 20)
    input_2 = int(Arus_1.get())
    input_4 = int(Pkbl_1.get())
    input_6 = int(Dkbl_1.get())
    hitungan = (c*l*input_4*input_2*d/(input_6/m))
    Drop_tegangan = h - hitungan
    hasil1 = "Tegangan hilang adalah : " + "%.2f"%hitungan + " volt"
    hasil2 = "Drop tegangan adalah : " + "%.2f"%Drop_tegangan + " volt"
  
  Textdisplay_1 = Label(layar,text=hasil1)
  Textdisplay_1.place(y = 185, x = 25)
  Textdisplay_2 = Label(layar,text=hasil2)
  Textdisplay_2.place(y = 210, x = 25)
            
# memasukkan nilai untuk membuat pilihan temperatur
option = ["Mencari nilai daya","Mencari nilai arus","Mencari diameter kabel","Mencari drop tegangan"]
cliked = StringVar()
cliked.set(option[0])
drop = OptionMenu(layar,cliked,*option,command=rumus)
drop.config(width=22)
drop.place(x = 20, y = 120)

#membuat tombol menghitung
btn = Button(layar,text="Start",command=lambda:rumus("hitung"))
btn.config(width=10)
btn.place(x = 200, y = 122)

layar.mainloop()