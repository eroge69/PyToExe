import os
import sys
import time
import threading
import tkinter as tk
import keyboard
import pyautogui
import requests

templates_folder = "moblar"
all_templates = [os.path.join(templates_folder, f) for f in os.listdir(templates_folder) if f.lower().endswith(".png")]
collect_folder = "toplancaklar"
all_collectables = [
    os.path.join(collect_folder, f)
    for f in os.listdir(collect_folder)
    if f.lower().endswith(".png")
]




oldu_image = "oldu.png"
hp_image = "hp_bar.png"
hp_region = (730, 970, 150, 30)
oldu_region = (30, 200, 130, 50)
isik_image = "isik.png"

automation_running = False
automation_thread = None


def log_message(message):
    print(message)
    text_box.after(0, lambda: (text_box.insert(tk.END, message + "\n"), text_box.see(tk.END)))


def is_valid_location(loc):
    return loc is not None and loc[2] > 0 and loc[3] > 0


def process_collect():
    for img_path in all_collectables:
        try:
            loc = pyautogui.locateOnScreen(img_path, confidence=0.9)
        except:
            loc = None
        if is_valid_location(loc):
            log_message(f"'{img_path}' bulundu at {loc}")
            cx, cy = pyautogui.center(loc)
            pyautogui.click(cx, cy)
            log_message(f"'{img_path}' tıklandı, 10 saniye bekleniyor.")
            time.sleep(10)
            break
    else:
        log_message("Toplanacak hiçbir görsel bulunamadı.")



def automation_loop():
    global automation_running

    if automation_running:
        try:
            initial_hp_loc = pyautogui.locateOnScreen(hp_image, confidence=0.9, region=hp_region)
        except pyautogui.ImageNotFoundException:
            initial_hp_loc = None
        if is_valid_location(initial_hp_loc):
            center_hp = pyautogui.center(initial_hp_loc)
            pyautogui.click(center_hp[0], center_hp[1] - 100)
            time.sleep(3)
            pyautogui.press("r")
            log_message("Can doluyor: 'r' tuşuna basıldı.")
            time.sleep(rpr_time_var.get())
        else:
            pass

    unsuccessful_count = 0

    while automation_running:
        if mode_var.get() == "all":
            current_templates = all_templates
        else:
            selected_template = mob_var.get()
            current_templates = [selected_template] if selected_template else []

        if not current_templates:
            log_message("Seçili template bulunamadı. Lütfen en az bir template seçin...")
            time.sleep(0.5)
            continue

        found_location = None
        found_template = None

        for template in current_templates:
            if not automation_running:
                break
            try:
                location = pyautogui.locateOnScreen(template, confidence=0.8)
            except pyautogui.ImageNotFoundException:
                location = None
            if location is not None:
                found_location = location
                found_template = template
                break

        if not automation_running:
            break

        if found_location is not None:
            unsuccessful_count = 0

            center_x, center_y = pyautogui.center(found_location)
            pyautogui.click(center_x, center_y - 30)
            log_message(f"Moba tıklandı({center_x}, {center_y - 30}) on {found_template}")
            pyautogui.click(center_x, center_y)
            pyautogui.click(center_x, center_y)
            log_message(f"Moba gidiliyor ({center_x}, {center_y}) on {found_template}")
            pyautogui.press("space")
            found_mob_can = False
            for _ in range(10):
                try:
                    loc = pyautogui.locateOnScreen("mob_can.png", confidence=0.8,region=oldu_region)
                except:
                    loc = None
                if is_valid_location(loc):
                    log_message(f"'mob_can.png' bulundu at {loc}")
                    found_mob_can = True
                    break
                time.sleep(1)
            if not found_mob_can:
                log_message("'mob_can.png' bulunamadı, mob bulma işlemine dönülüyor.")
                continue

            pyautogui.press("space")
            time.sleep(3)


            if rpr_mode.get() == "Hemen Rpr":
                while automation_running:
                    try:
                        hp_loc = pyautogui.locateOnScreen(hp_image, confidence=0.9, region=hp_region)
                    except pyautogui.ImageNotFoundException:
                        hp_loc = None
                    try:
                        oldu_loc = pyautogui.locateOnScreen(oldu_image, confidence=0.9, region=oldu_region)
                    except pyautogui.ImageNotFoundException:
                        oldu_loc = None

                    if is_valid_location(hp_loc):
                        center_hp = pyautogui.center(hp_loc)
                        pyautogui.click(center_hp[0], center_hp[1] - 100)
                        log_message("Hemen RPR modu: Canın 100 px üstüne tıklandı.")
                        time.sleep(5)
                        pyautogui.press("r")
                        log_message("HP azaldığından  'q' tuşuna basıldı.")
                        time.sleep(rpr_time_var.get())
                        break
                    elif oldu_loc is not None:
                        log_message("'Mob öldü' tespit edildi (Hemen RPR).")
                        if isik_option.get() == "Alınsın":
                            process_collect()
                        break
                    else:
                        log_message(f"'Mob ölümü  bekleniyor...")
                    time.sleep(0.2)
            else:
                while automation_running:
                    try:
                        oldu_location = pyautogui.locateOnScreen(oldu_image, confidence=0.9, region=oldu_region)
                    except pyautogui.ImageNotFoundException:
                        oldu_location = None

                    if oldu_location is not None:
                        log_message(f"'Mob öldü  şimdi sorgulama yapılacak (tek seferlik).")
                        if isik_option.get() == "Alınsın":
                            process_collect()
                        else:
                            try:
                                hp_loc = pyautogui.locateOnScreen(hp_image, confidence=0.9, region=hp_region)
                            except pyautogui.ImageNotFoundException:
                                hp_loc = None
                            if is_valid_location(hp_loc):
                                log_message(f"'Can azaldı {hp_loc} .")
                                center_hp = pyautogui.center(hp_loc)
                                pyautogui.click(center_hp[0], center_hp[1] - 100)
                                time.sleep(3)
                                pyautogui.press("r")
                                log_message("HP bar bulunduğundan 'r' tuşuna basıldı.")
                                time.sleep(rpr_time_var.get())
                            else:
                                log_message(f"RPR işlemi gerçekleştirilmedi.")
                        break
                    else:
                        log_message(f"Mob ölümü bekleniyor...")
                    time.sleep(0.2)
        else:
            unsuccessful_count += 1
            log_message(f"Mob Bulunamadı, yeniden denenecek... (Arama Sayısı: {unsuccessful_count})")
            if unsuccessful_count >= 5:
                log_message("Mide gidiliyor.")
                pyautogui.click(1737, 178)
                time.sleep(1)
                pyautogui.click(971, 480)
                time.sleep(1)
                pyautogui.press("e")
                time.sleep(3)
                unsuccessful_count = 0
        time.sleep(0.2)
    log_message("Otomasyon durdu.")


def start_automation(event=None):
    global automation_running, automation_thread
    if not automation_running:
        automation_running = True
        automation_thread = threading.Thread(target=automation_loop, daemon=True)
        automation_thread.start()
        log_message("Otomasyon başladı.")

def stop_automation(event=None):
    global automation_running
    automation_running = False
    log_message("Otomasyon durduruluyor...")


root = tk.Tk()
root.title("SF BOT")
root.attributes("-topmost", True)
root.iconbitmap("thinker.ico")

mode_frame = tk.LabelFrame(root, text="Mode Seçimi")
mode_frame.pack(padx=10, pady=10, fill="x")
mode_var = tk.StringVar(value="all")
tk.Radiobutton(mode_frame, text="Tüm Moblar", variable=mode_var, value="all").pack(anchor="w", padx=10, pady=2)
tk.Radiobutton(mode_frame, text="Seçilen Moblar", variable=mode_var, value="selected").pack(anchor="w", padx=10, pady=2)

mob_frame = tk.LabelFrame(root, text="Mob Seçimi")
mob_frame.pack(padx=10, pady=10, fill="x")
mob_var = tk.StringVar(value=all_templates[0] if all_templates else "")
mob_options = tk.OptionMenu(mob_frame, mob_var, *all_templates)
mob_options.pack(padx=10, pady=5)

rpr_frame = tk.LabelFrame(root, text="RPR Seçimi")
rpr_frame.pack(padx=10, pady=10, fill="x")
rpr_mode = tk.StringVar(value="Hemen Rpr")
rpr_options = tk.OptionMenu(rpr_frame, rpr_mode, "Kill Sonrası Rpr", "Hemen Rpr")
rpr_options.pack(padx=10, pady=5)

isik_frame = tk.LabelFrame(root, text="Işık Seçimi")
isik_frame.pack(padx=10, pady=10, fill="x")
isik_option = tk.StringVar(value="Alınmasın")
isik_options = tk.OptionMenu(isik_frame, isik_option, "Alınsın", "Alınmasın")
isik_options.pack(padx=10, pady=5)

buttons_frame = tk.Frame(root)
buttons_frame.pack(padx=10, pady=10)
start_button = tk.Button(buttons_frame, text="Başlat", command=start_automation)
start_button.pack(side="left", padx=10)
stop_button = tk.Button(buttons_frame, text="Durdur", command=stop_automation)
stop_button.pack(side="left", padx=10)

log_frame = tk.LabelFrame(root, text="Log")
log_frame.pack(padx=10, pady=10, fill="both", expand=True)
text_box = tk.Text(log_frame, height=10)
text_box.pack(side="left", fill="both", expand=True)
scrollbar = tk.Scrollbar(log_frame, command=text_box.yview)
scrollbar.pack(side="right", fill="y")
text_box.config(yscrollcommand=scrollbar.set)
tk.Label(rpr_frame, text="RPR Süresi (s):").pack(anchor="w", padx=10, pady=(5,0))
rpr_time_var = tk.IntVar(value=15)
rpr_spin = tk.Spinbox(
    rpr_frame,
    from_=5, to=60, increment=1,
    textvariable=rpr_time_var,
    width=5
)
rpr_spin.pack(anchor="w", padx=10, pady=(0,5))


def hotkey_listener():
    keyboard.add_hotkey('f9', start_automation)
    keyboard.add_hotkey('f8', stop_automation)
    keyboard.wait()
threading.Thread(target=hotkey_listener, daemon=True).start()

root.mainloop()
