
import tkinter as tk
from tkinter import messagebox, simpledialog
import json, os, random, time, threading, string
from instagrapi import Client
import winsound

ACC_FILE = "accounts.json"
PASSWORD = "wxero"

def play_music_loop():
    while True:
        winsound.Beep(440, 200)
        time.sleep(0.1)
        winsound.Beep(660, 200)
        time.sleep(0.1)

def click_sound():
    winsound.Beep(1000, 50)

def save_account(acc):
    lst = load_accounts()
    lst.append(acc)
    with open(ACC_FILE, 'w', encoding='utf-8') as f:
        json.dump(lst, f, ensure_ascii=False, indent=4)

def load_accounts():
    if not os.path.exists(ACC_FILE):
        return []
    with open(ACC_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def gen_data():
    name = ''.join(random.choices(string.ascii_lowercase, k=7)).capitalize()
    email = f"{name.lower()}{random.randint(100,999)}@gmail.com"
    username = f"{name.lower()}{random.randint(100,9999)}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return {"username": username, "password": password}

def cmd_click(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=click_sound, daemon=True).start()
        return fn(*args, **kwargs)
    return wrapper

@cmd_click
def create_account():
    data = gen_data()
    save_account(data)
    messagebox.showinfo("تم الإنشاء",
                        f"حساب جديد:\n{data['username']} / {data['password']}")
    app.update_count()

@cmd_click
def create_multiple():
    n = simpledialog.askinteger("عدد الحسابات", "كم حساب تريد إنشاءه؟")
    if n:
        for _ in range(n):
            create_account()

@cmd_click
def send_followers():
    accounts = load_accounts()
    if not accounts:
        messagebox.showwarning("لا توجد حسابات", "أنشئ حسابات أولاً.")
        return
    target = simpledialog.askstring("المستهدف", "أدخل اسم الحساب المستهدف:")
    num = simpledialog.askinteger("المتابعين", "كم عدد المتابعين؟")
    if not target or not num:
        return

    sent = 0
    for acc in accounts:
        if sent >= num:
            break
        try:
            cl = Client()
            cl.login(acc["username"], acc["password"])
            uid = cl.user_id_from_username(target)
            cl.user_follow(uid)
            cl.logout()
            sent += 1
        except Exception:
            continue
    messagebox.showinfo("تم الإرسال", f"أُرسل {sent} متابع إلى @{target}")

@cmd_click
def show_accounts():
    lst = load_accounts()
    if not lst:
        messagebox.showinfo("الحسابات", "لا توجد حسابات.")
        return
    text = "\n".join(f"{a['username']} | {a['password']}" for a in lst)
    messagebox.showinfo("الحسابات المخزنة", text)

class App:
    def __init__(self, root):
        root.title("Insta Followers Booster")
        root.geometry("600x450")
        root.configure(bg="#0f0f0f")

        threading.Thread(target=play_music_loop, daemon=True).start()

        tk.Label(root, text="لوحة التحكم", font=("Helvetica", 22, "bold"),
                 fg="#00FFAA", bg="#0f0f0f").pack(pady=10)
        self.count_label = tk.Label(root, text=self.get_count(),
                                    font=("Helvetica", 12), fg="#cccccc", bg="#0f0f0f")
        self.count_label.pack(pady=5)

        buttons = [
            ("إنشاء حساب", create_account),
            ("إنشاء عدة حسابات", create_multiple),
            ("إرسال متابعين", send_followers),
            ("عرض الحسابات", show_accounts),
            ("خروج", root.quit)
        ]
        for txt, cmd in buttons:
            btn = tk.Button(root, text=txt, command=cmd,
                            font=("Helvetica", 12), bg="#222", fg="#00ffaa", width=30)
            btn.pack(pady=5)

        self.footer = tk.Label(root, text="تواصل مع المطور: Instagram @wx.ero",
                               font=("Consolas", 10, "bold"), bg="#0f0f0f")
        self.footer.pack(side="bottom", pady=10)
        self.color_footer()

    def get_count(self):
        return f"عدد الحسابات المخزنة: {len(load_accounts())}"

    def update_count(self):
        self.count_label.config(text=self.get_count())

    def color_footer(self):
        colors = ["#ff0055", "#00ffaa", "#00aaff", "#ffaa00", "#aa00ff"]
        def anim():
            while True:
                for color in colors:
                    self.footer.config(fg=color)
                    time.sleep(0.2)
        threading.Thread(target=anim, daemon=True).start()

def ask_password():
    root = tk.Tk()
    root.withdraw()
    pwd = simpledialog.askstring("كلمة السر", "أدخل كلمة السر:", show="*")
    root.destroy()
    return pwd == PASSWORD

if __name__ == "__main__":
    if ask_password():
        root = tk.Tk()
        global app
        app = App(root)
        root.mainloop()
    else:
        messagebox.showerror("خطأ", "كلمة السر خاطئة")
