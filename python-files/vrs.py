import os
import webbrowser
import time
import tkinter as tk
from tkinter import messagebox
from threading import Thread

def muzik_ac():
    webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

def not_defterine_yaz():
    with open("hacklendin.txt", "w", encoding="utf-8") as dosya:
        dosya.write("Hacklendin! 😄\n")
        dosya.write("Bu sadece eğlenceli bir script.\n")
        dosya.write("Endişelenme, hiçbir şeyine zarar vermedim.\n")
    os.system("notepad hacklendin.txt")

def sonsuz_popup():
    while True:
        time.sleep(0.5)
        messagebox.showwarning("Hacklendin!", "Bilgisayarın hacklendi! 😱")

def virusu_kapat():
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle
    
    cevap = messagebox.askyesno("Virüs Uyarısı", "Virüsü kapatmak ister misiniz?")
    
    if cevap:
        # Evet'e basılırsa 2 yeni popup aç
        Thread(target=sonsuz_popup).start()
        Thread(target=sonsuz_popup).start()
        messagebox.showinfo("Haha", "Şaka şaka! Daha çok popup geliyor! 😈")
    else:
        # Hayır'a basılırsa
        messagebox.showinfo("Cevap", "Sen bilirsin! :)")

def zararsiz_virus():
    print("🎵 Müzik açılıyor... 🎵")
    Thread(target=muzik_ac).start()
    
    print("📝 Not defterine mesaj bırakılıyor...")
    Thread(target=not_defterine_yaz).start()
    
    print("🖼️ Popup pencereleri hazırlanıyor...")
    time.sleep(1)
    
    virusu_kapat()
    
    print("🔥 Hack tamamlandı! (Şaka şaka 😜)")
    print("Bu tamamen zararsız bir eğlence scriptidir. 🤗")

if __name__ == "__main__":
    zararsiz_virus()