import tkinter as tk
from tkinter import ttk
import random
import ctypes
import webbrowser
import pyautogui
import time
from typing import Tuple, List
import keyboard
import winsound

class TrollApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Troll Spy App")
        self.root.geometry("400x450")  # Yüksekliği artırdık
        self.setup_ui()
        
    def setup_ui(self):
        # Ana tema ayarları
        self.root.configure(bg="#2E2E2E")
        style = ttk.Style()
        style.configure("Custom.TButton", 
                       padding=10, 
                       font=('Helvetica', 10))

        # Frame oluştur
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Butonlar
        ttk.Button(main_frame, 
                  text="🎲 Rasgele Hata Gönder",
                  command=self.send_random_error,
                  style="Custom.TButton").pack(pady=10, fill=tk.X)
                  
        ttk.Button(main_frame,
                  text="🔐 Lingo Bulmacası",
                  command=self.geometry_dash_challenge,
                  style="Custom.TButton").pack(pady=10, fill=tk.X)

        # Yeni butonlar ekleyelim
        ttk.Button(main_frame,
                  text="🖱️ Mouse Kaçır",
                  command=self.troll_mouse,
                  style="Custom.TButton").pack(pady=10, fill=tk.X)
                  
        ttk.Button(main_frame,
                  text="🔊 Ses Bombası",
                  command=self.sound_troll,
                  style="Custom.TButton").pack(pady=10, fill=tk.X)
                  
        ttk.Button(main_frame,
                  text="⌨️ Klavye Karıştır",
                  command=self.keyboard_troll,
                  style="Custom.TButton").pack(pady=10, fill=tk.X)

        ttk.Button(main_frame,
                  text="📤 Komut Gönder",
                  command=self.send_command_to_worker_ui,
                  style="Custom.TButton").pack(pady=10, fill=tk.X)

    def show_error_message(self, title: str, message: str) -> None:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)

    def simple_input_box(self, title: str, prompt: str) -> str:
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        result = {"value": ""}
        
        ttk.Label(dialog, text=prompt, padding=10).pack()
        entry = ttk.Entry(dialog, width=30)
        entry.pack(pady=10)
        
        def submit():
            result["value"] = entry.get()
            dialog.destroy()
        
        ttk.Button(dialog, text="Gönder", command=submit).pack(pady=10)
        
        dialog.grab_set()
        self.root.wait_window(dialog)
        return result["value"]

    def trigger_200_errors(self) -> None:
        for i in range(200):
            self.show_error_message("Sistem Hatası", f"Bir sorun oluştu! Kod: {i+1}")

    def geometry_dash_challenge(self) -> None:
        ANSWERS = ["ANAHTAR", "ŞİFRE", "KUTU", "KAPI", "GEOMETRİ", "TROLL", "HACKED"]
        answer = random.choice(ANSWERS)
        guess = self.simple_input_box("Lingo Bulmacası", "Anahtarı Tahmin Et:")
        
        if guess.upper() == answer:
            self.show_error_message("Tebrikler", "Doğru cevap! Ama yine de kaybettin!")
            self.trigger_200_errors()
        else:
            self.show_error_message("Kaybettin", f"Cevap {answer} olacaktı.")
            # Birden fazla tarayıcı sekmesi aç
            for _ in range(5):
                webbrowser.open("https://www.youtube.com/@eOStheX")

    def send_random_error(self) -> None:
        # Yeni hata mesajları ekleyelim
        new_errors = [
            ("CPU Hatası", "CPU'nuz kahve molasında..."),
            ("Sistem Hatası", "Windows Blue Screen'i özledin mi?"),
            ("Hafıza Hatası", "Beyin.exe çalışmayı durdurdu"),
            ("Kritik Hata", "Alt+F4 tuşlarına basarak düzeltebilirsin!"),
            ("Güvenlik İhlali", "Hacklenmek üzeresin! Şaka şaka 😄"),
        ]
        
        ERROR_MESSAGES: List[Tuple[str, str]] = [
            ("Windows Hatası", "Bilgisayarınız tekrar başlatılacaktır."),
            ("Güncelleme Gerekli", "Sistem 1999'a geri döndürülüyor..."),
            ("RAM Eksik", "RAM'iniz erimekte..."),
            ("İzin Reddedildi", "Kendine bilgisayar al o zaman!"),
            ("Donanım Hatası", "Mouse dondu, şimdi çözülmeye çalışılıyor..."),
            ("Dikkat", "Daha fazla hata için tıklamaya devam et!")
        ]
        ERROR_MESSAGES.extend([(f"Hata {i}", f"Bu {i}. hata oldu.") 
                             for i in range(7, 201)])
        ERROR_MESSAGES.extend(new_errors)
        
        index = random.randint(0, len(ERROR_MESSAGES) - 1)
        title, message = ERROR_MESSAGES[index]
        self.show_error_message(title, message)
        
        if index == 198:  # 199. indeks yerine 198 kullanıyoruz (0-bazlı indeksleme)
            self.trigger_200_errors()

    def troll_mouse(self):
        """Mouse'u rasgele hareket ettir"""
        def move_mouse():
            for _ in range(10):
                x = random.randint(0, 1920)
                y = random.randint(0, 1080)
                pyautogui.moveTo(x, y, duration=0.5)
            self.show_error_message("Mouse Kontrolü", "Mouse'un kontrolünü kaybettin!")
        
        self.root.after(1000, move_mouse)

    def sound_troll(self):
        """Rahatsız edici sesler çıkar"""
        frequencies = [2500, 1500, 3000, 2000]
        for freq in frequencies:
            winsound.Beep(freq, 500)
        self.show_error_message("Ses Hatası", "Hoparlörler bozuldu!")

    def keyboard_troll(self):
        """Klavye kısayollarını karıştır"""
        def swap_keys():
            keyboard.remap_key('w', 's')
            keyboard.remap_key('a', 'd')
            time.sleep(10)  # 10 saniye boyunca karışık kalsın
            keyboard.unhook_all()
        
        self.show_error_message("Klavye Hatası", "Klavyen 10 saniye boyunca ters çalışacak!")
        self.root.after(100, swap_keys)

    def send_command_to_worker(self, cmd: str):
        with open("troll_command.txt", "w") as f:
            f.write(cmd)

    def send_command_to_worker_ui(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Komut Seç")
        dialog.geometry("300x200")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="Çalıştırılacak komutu seçin:", padding=10).pack()

        command_var = tk.StringVar(value="mouse")
        commands = ["mouse", "ses", "klavye", "hata", "lingo"]

        for cmd in commands:
            ttk.Radiobutton(dialog, text=cmd.capitalize(), variable=command_var, value=cmd).pack(anchor=tk.W, padx=20)

        def submit():
            selected_command = command_var.get()
            self.send_command_to_worker(selected_command)
            self.show_error_message("Başarılı", f"{selected_command} komutu gönderildi!")
            dialog.destroy()

        ttk.Button(dialog, text="Gönder", command=submit).pack(pady=10)

        dialog.grab_set()
        self.root.wait_window(dialog)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TrollApp()
    app.run()
