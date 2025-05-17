
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
import threading
import time
import json
import os
import pyautogui
import random
import pytesseract

running = False
loop_mode = False
path = []
map_filename = ""
mouse_button = "left"
monster_count = 0
kill_log = []

def load_map():
    global map_img, tk_map_img, canvas, path, map_filename
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not file_path:
        return
    map_filename = os.path.splitext(os.path.basename(file_path))[0]
    path.clear()
    canvas.delete("all")
    map_img = Image.open(file_path)
    map_img = map_img.resize((960, 600), Image.ANTIALIAS)
    tk_map_img = ImageTk.PhotoImage(map_img)
    canvas.config(width=960, height=600)
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_map_img)
    canvas.bind("<Button-1>", on_click)
    load_path()

def on_click(event):
    x, y = event.x, event.y
    path.append((x, y))
    canvas.create_oval(x-3, y-3, x+3, y+3, fill='red')
    if len(path) > 1:
        canvas.create_line(*path[-2], *path[-1], fill='blue', width=2)

def save_path():
    if not map_filename:
        return
    with open(f"{map_filename}_path.json", "w") as f:
        json.dump(path, f)

def load_path():
    if not map_filename:
        return
    try:
        with open(f"{map_filename}_path.json", "r") as f:
            loaded_path = json.load(f)
            for x, y in loaded_path:
                path.append((x, y))
                canvas.create_oval(x-3, y-3, x+3, y+3, fill='red')
            for i in range(len(path)-1):
                canvas.create_line(*path[i], *path[i+1], fill='blue', width=2)
    except:
        pass

def use_xp_skill():
    skill = xp_var.get()
    if skill == "cyclone":
        pyautogui.press("f9")
    elif skill == "fly":
        pyautogui.press("f10")

def detect_monster():
    screenshot = ImageGrab.grab()
    text = pytesseract.image_to_string(screenshot)
    return any(char.isalpha() for char in text)

def bot_logic():
    global running, monster_count, kill_log
    while running:
        use_xp_skill()
        monster_count = 0
        kill_log = []
        for x, y in path:
            if not running:
                break
            pyautogui.moveTo(x, y)
            if detect_monster():
                pyautogui.click(button=mouse_button)
                kills = random.randint(1, 3)
                monster_count += kills
                kill_log.append(f"({x},{y}) : قتل {kills} وحوش")
            update_monster_count()
            update_log()
            time.sleep(0.5)
        if not loop_mode:
            break

def update_monster_count():
    monster_label.config(text=f"عدد الوحوش المقتولة: {monster_count}")

def update_log():
    log_text.config(state='normal')
    log_text.delete(1.0, tk.END)
    for entry in kill_log[-10:]:
        log_text.insert(tk.END, entry + "\n")
    log_text.config(state='disabled')

def start_bot():
    global running, mouse_button, loop_mode
    if not path:
        messagebox.showerror("خطأ", "يجب تحميل خريطة وتحديد مسار.")
        return
    mouse_button = mouse_choice.get()
    loop_mode = loop_check.get()
    running = True
    threading.Thread(target=bot_logic).start()

def stop_bot():
    global running
    running = False

root = tk.Tk()
root.title("بوت دقة عالية + كشف وحوش")
root.geometry("1100x820")

control_frame = tk.Frame(root)
control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

tk.Button(control_frame, text="تحميل خريطة", command=load_map, bg="blue", fg="white").pack(pady=5)
tk.Button(control_frame, text="حفظ المسار", command=save_path).pack(pady=5)

tk.Label(control_frame, text="زر الماوس للهجوم:").pack()
mouse_choice = tk.StringVar(value="left")
tk.OptionMenu(control_frame, mouse_choice, "left", "right").pack()

loop_check = tk.BooleanVar()
tk.Checkbutton(control_frame, text="تكرار المسار باستمرار", variable=loop_check).pack()

tk.Label(control_frame, text="اسكله XP:").pack()
xp_var = tk.StringVar(value="none")
tk.OptionMenu(control_frame, xp_var, "none", "cyclone", "fly").pack()

monster_label = tk.Label(control_frame, text="عدد الوحوش المقتولة: 0")
monster_label.pack(pady=5)

tk.Button(control_frame, text="تشغيل", command=start_bot, bg="green", fg="white").pack(pady=5)
tk.Button(control_frame, text="إيقاف", command=stop_bot, bg="red", fg="white").pack(pady=5)

right_frame = tk.Frame(root)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

canvas = tk.Canvas(right_frame, width=960, height=600, bg="gray")
canvas.pack()

tk.Label(right_frame, text="تقرير القتل (مصغر):").pack()
log_text = tk.Text(right_frame, height=10, state='disabled')
log_text.pack(fill=tk.BOTH, expand=True)

root.mainloop()
