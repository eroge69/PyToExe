import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox
import webbrowser
import openai

# קובץ הקונפיגורציה
CONFIG_FILE = "config.json"

def get_api_key(root):
    """
    מפעיל תיבת דיאלוג לבקשת ה-API KEY ושומר אותו ב-config.json.
    """
    # אם הקובץ לא קיים, מבקשים את המפתח ושומרים
    if not os.path.exists(CONFIG_FILE):
        api_key = simpledialog.askstring(
            "הזן את ה-API Key",
            "הכנס את ה-API Key שלך (ניתן להדביק עם Ctrl+V):",
            parent=root
        )
        if not api_key:
            messagebox.showerror("שגיאה", "לא הוזן API Key. התוכנה תיסגר.")
            root.destroy()
            return False
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"api_key": api_key}, f)
    # טוענים את המפתח
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    openai.api_key = data.get("api_key", "")
    if not openai.api_key:
        messagebox.showerror("שגיאה", "המפתח ריק. נסה שוב.")
        root.destroy()
        return False
    return True

def ask_gpt(user_input):
    """
    שולח את הטקסט ל-GPT ומחזיר את התשובה.
    """
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "אתה עוזר אישי חכם שמבין עברית."},
                {"role": "user",   "content": user_input}
            ],
            temperature=0.6,
            max_tokens=150,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[שגיאה ב-GPT]: {e}"

def open_google():
    webbrowser.open("https://www.google.com")

def send_email():
    # כאן תוכל לממש send via smtplib
    messagebox.showinfo("שליחת מייל", "המייל נשלח (דמה).")

def build_ui(root):
    root.title("עוזר אישי חכם")
    root.geometry("500x400")

    # רשימת שיחות
    listbox = tk.Listbox(root, width=60, height=18)
    listbox.pack(padx=10, pady=(10,0))

    # שדה קלט
    entry = tk.Entry(root, width=50)
    entry.pack(padx=10, pady=5)
    entry.focus()

    # כפתור שליחה
    def on_send():
        txt = entry.get().strip()
        if not txt:
            return
        listbox.insert(tk.END, f"אתה: {txt}")
        entry.delete(0, tk.END)

        # פקודות בסיסיות
        cmd = txt.lower()
        if cmd == "פתח גוגל":
            listbox.insert(tk.END, "עוזר: פותח את Google…")
            open_google()
        elif cmd == "שלח מייל":
            listbox.insert(tk.END, "עוזר: שולח מייל…")
            send_email()
        else:
            listbox.insert(tk.END, "עוזר: לא בטוח… שואל את GPT")
            res = ask_gpt(txt)
            listbox.insert(tk.END, f"עוזר: {res}")

    send_btn = tk.Button(root, text="שלח", command=on_send)
    send_btn.pack(pady=(0,10))

    # תמיכה ב-Ctrl+V להדבקה
    def paste(event):
        entry.insert(tk.END, root.clipboard_get())
    entry.bind("<Control-v>", paste)
    entry.bind("<Return>", lambda e: on_send())

def main():
    # צור את החלון הראשי
    root = tk.Tk()
    root.withdraw()  # מסתיר אותו זמנית

    # בקש API Key
    ok = get_api_key(root)
    if not ok:
        return

    # בנה את הממשק, הצג ושמור על החלון פתוח
    root.deiconify()
    build_ui(root)
    root.mainloop()

if __name__ == "__main__":
    # כדאי להריץ מ-CMD: 
    #  python main.py
    main()
