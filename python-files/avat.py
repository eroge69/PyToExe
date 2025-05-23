// نویسنده: avat

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import os, json, base64, hashlib, time, threading, re, smtplib
from email.message import EmailMessage

# رمزنگاری ساده
key = b's3cr3tk3y'
def encrypt(data):
    return base64.b64encode(data.encode()).decode()

def decrypt(data):
    try:
        return base64.b64decode(data.encode()).decode()
    except:
        return ""

# مسیر ذخیره
DATA_FILE = "secure_notes.json"
BACKUP_DIR = "backups"
USERS_FILE = "users.json"

# ایمیل ارسال تایید
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASS = "your_email_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# رابط اصلی
class SecureNotebookApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Secure Notebook")
        self.root.configure(bg='#222')
        self.authenticated_user = None

        self.load_users()
        self.build_login_ui()

    def load_users(self):
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w') as f:
                json.dump({}, f)
        with open(USERS_FILE, 'r') as f:
            self.users = json.load(f)

    def save_users(self):
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f)

    def build_login_ui(self):
        for widget in self.root.winfo_children(): widget.destroy()

        tk.Label(self.root, text="Secure Notebook", bg='#222', fg='white', font=('Arial', 18)).pack(pady=10)
        tk.Button(self.root, text="ورود", command=self.login_ui).pack(pady=5)
        tk.Button(self.root, text="ثبت‌نام", command=self.register_ui).pack(pady=5)
        tk.Button(self.root, text="بازیابی رمز", command=self.reset_password_ui).pack(pady=5)

    def login_ui(self):
        def do_login():
            email = email_entry.get()
            pwd = password_entry.get()
            user = self.users.get(email)
            if user and user['password'] == encrypt(pwd):
                self.authenticated_user = email
                self.load_notes()
                self.build_main_ui()
            else:
                messagebox.showerror("خطا", "اطلاعات نادرست")

        self.clear_window()
        tk.Label(self.root, text="ورود", bg='#222', fg='white').pack()
        email_entry = tk.Entry(self.root)
        password_entry = tk.Entry(self.root, show="*")
        email_entry.pack(); password_entry.pack()
        tk.Button(self.root, text="ورود", command=do_login).pack()
        tk.Button(self.root, text="بازگشت", command=self.build_login_ui).pack(pady=5)

    def register_ui(self):
        def send_email_code(email, code):
            msg = EmailMessage()
            msg.set_content(f"کد تایید: {code}")
            msg['Subject'] = 'تایید ایمیل'
            msg['From'] = EMAIL_SENDER
            msg['To'] = email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
                s.starttls()
                s.login(EMAIL_SENDER, EMAIL_PASS)
                s.send_message(msg)

        def do_register():
            email = email_entry.get()
            pwd = password_entry.get()
            if email in self.users:
                messagebox.showerror("خطا", "کاربر وجود دارد")
                return
            code = str(hashlib.md5(email.encode()).hexdigest())[:6]
            send_email_code(email, code)
            entered = simpledialog.askstring("تایید ایمیل", "کد ارسال‌شده را وارد کنید:")
            if entered == code:
                self.users[email] = {'password': encrypt(pwd), 'notes': []}
                self.save_users()
                messagebox.showinfo("ثبت شد", "ثبت‌نام موفق بود")
                self.build_login_ui()
            else:
                messagebox.showerror("ناموفق", "کد اشتباه بود")

        self.clear_window()
        tk.Label(self.root, text="ثبت‌نام", bg='#222', fg='white').pack()
        email_entry = tk.Entry(self.root)
        password_entry = tk.Entry(self.root, show="*")
        email_entry.pack(); password_entry.pack()
        tk.Button(self.root, text="ثبت‌نام", command=do_register).pack()
        tk.Button(self.root, text="بازگشت", command=self.build_login_ui).pack(pady=5)

    def reset_password_ui(self):
        def do_reset():
            email = email_entry.get()
            if email not in self.users:
                messagebox.showerror("خطا", "کاربر یافت نشد")
                return
            new = simpledialog.askstring("تغییر رمز", "رمز جدید:")
            self.users[email]['password'] = encrypt(new)
            self.save_users()
            messagebox.showinfo("انجام شد", "رمز تغییر کرد")

        self.clear_window()
        tk.Label(self.root, text="بازیابی رمز", bg='#222', fg='white').pack()
        email_entry = tk.Entry(self.root)
        email_entry.pack()
        tk.Button(self.root, text="بازیابی", command=do_reset).pack()
        tk.Button(self.root, text="بازگشت", command=self.build_login_ui).pack(pady=5)

    def build_main_ui(self):
        self.clear_window()
        tk.Label(self.root, text=f"خوش‌آمدید {self.authenticated_user}", bg='#222', fg='white').pack()

        self.search_entry = tk.Entry(self.root)
        self.search_entry.pack()
        self.search_entry.bind("<KeyRelease>", self.update_notes_display)

        self.notes_box = tk.Listbox(self.root, width=50)
        self.notes_box.pack()

        tk.Button(self.root, text="افزودن", command=self.add_note).pack(pady=2)
        tk.Button(self.root, text="خواندن", command=self.read_note).pack(pady=2)
        tk.Button(self.root, text="خروج", command=self.logout).pack(pady=2)

        self.load_notes()
        self.update_notes_display()
        self.schedule_backup()

    def add_note(self):
        title = simpledialog.askstring("عنوان", "عنوان یادداشت:")
        text = simpledialog.askstring("متن", "متن:")
        if title and text:
            self.notes.append({"title": title, "text": encrypt(text)})
            self.save_notes()
            self.update_notes_display()

    def read_note(self):
        selected = self.notes_box.curselection()
        if not selected: return
        index = selected[0]
        note = self.notes[index]
        messagebox.showinfo(note['title'], decrypt(note['text']))

    def logout(self):
        self.authenticated_user = None
        self.build_login_ui()

    def load_notes(self):
        self.notes = self.users[self.authenticated_user].get('notes', [])

    def save_notes(self):
        self.users[self.authenticated_user]['notes'] = self.notes
        self.save_users()

    def update_notes_display(self, event=None):
        self.notes_box.delete(0, tk.END)
        query = self.search_entry.get().lower()
        for note in self.notes:
            if query in note['title'].lower() or query in decrypt(note['text']).lower():
                self.notes_box.insert(tk.END, note['title'])

    def schedule_backup(self):
        def backup():
            if not os.path.exists(BACKUP_DIR):
                os.makedirs(BACKUP_DIR)
            while True:
                timestamp = int(time.time())
                fname = f"{BACKUP_DIR}/backup_{self.authenticated_user}_{timestamp}.json"
                with open(fname, 'w') as f:
                    json.dump(self.users[self.authenticated_user]['notes'], f)
                time.sleep(300)  # هر ۵ دقیقه

        threading.Thread(target=backup, daemon=True).start()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

root = tk.Tk()
app = SecureNotebookApp(root)
root.mainloop()