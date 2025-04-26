import os
import json
import tkinter as tk
from tkinter import simpledialog
import webbrowser
import openai

# --- קובץ קונפיג ---
CONFIG_FILE = "config.json"

# --- בקשת API KEY ---
def get_api_key():
    if not os.path.exists(CONFIG_FILE):
        temp_root = tk.Tk()
        temp_root.withdraw()  # מסתיר את חלון tkinter הזמני
        api_key = simpledialog.askstring("הזן את המפתח", "הכנס את ה-API Key שלך:")
        if api_key:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"api_key": api_key}, f)
            openai.api_key = api_key
        temp_root.destroy()  # סוגר את החלון הזמני
    else:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            openai.api_key = config.get("api_key", "")

# --- שליחת פקודה ל-GPT ---
def ask_gpt(user_input):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # או gpt-4 אם יש לך גישה
            prompt=f"המשתמש ביקש: {user_input}. מה עלי לעשות במחשב?",
            max_tokens=100,
            temperature=0.6
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"שגיאה בבינה מלאכותית: {e}"

# --- פעולות פשוטות ---
def open_google():
    webbrowser.open("https://www.google.com")

def send_email():
    print("שליחת מייל (דוגמה בלבד)")

# --- ממשק צ'אט ---
def start_chat():
    global chat_root, entry

    chat_root = tk.Tk()
    chat_root.title("עוזר אישי חכם")

    # תיבת הודעות
    listbox = tk.Listbox(chat_root, width=50, height=15)
    listbox.pack(padx=10, pady=10)

    # שדה קלט
    entry = tk.Entry(chat_root, width=40)
    entry.pack(pady=5)

    # פונקציה לשליחת הודעה
    def on_send():
        user_text = entry.get()
        if user_text.strip() == "":
            return  # אם אין טקסט לא שולחים כלום
        listbox.insert(tk.END, f"אתה: {user_text}")
        entry.delete(0, tk.END)

        # טיפול בפקודות בסיסיות
        if user_text.lower() == "פתח גוגל":
            listbox.insert(tk.END, "עוזר: פותח את גוגל...")
            open_google()
        elif user_text.lower() == "שלח מייל":
            listbox.insert(tk.END, "עוזר: שולח מייל...")
            send_email()
        else:
            listbox.insert(tk.END, "עוזר: לא בטוח... שואל את הבינה!")
            action = ask_gpt(user_text)
            listbox.insert(tk.END, f"עוזר: {action}")

    # כפתור שליחה
    send_button = tk.Button(chat_root, text="שלח", command=on_send)
    send_button.pack(pady=5)

    # אפשרות הדבקה עם Ctrl+V
    def paste(event):
        entry.insert(tk.END, chat_root.clipboard_get())
    entry.bind("<Control-v>", paste)

    chat_root.mainloop()

# --- הרצת התוכנה ---
if __name__ == "__main__":
    get_api_key()
    start_chat()
