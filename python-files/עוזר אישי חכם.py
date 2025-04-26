import os
import json
import tkinter as tk
from tkinter import simpledialog
import webbrowser

# פונקציה לבקש API Key אם הוא לא קיים
def get_api_key():
    config_file = "config.json"
    
    # אם לא קיים קובץ קונפיגורציה, נבקש את המפתח
    if not os.path.exists(config_file):
        root = tk.Tk()
        root.withdraw()  # הסתר את החלון הראשי של tkinter
        
        # בקשת API Key
        api_key = simpledialog.askstring("הזן את ה-API Key", "הכנס את המפתח שלך:")
        
        # שמור את המפתח בקובץ config.json
        if api_key:
            with open(config_file, 'w') as config:
                json.dump({"api_key": api_key}, config)
            print("המפתח נשמר בהצלחה!")
        else:
            print("לא הוזן מפתח.")
        root.quit()

    else:
        # קרא את המפתח מקובץ הקונפיגורציה
        with open(config_file, 'r') as config:
            data = json.load(config)
            api_key = data.get("api_key", "")
        
        if api_key:
            print(f"המפתח שלך: {api_key}")
        else:
            print("לא נמצא מפתח.")
            get_api_key()

# ממשק משתמש צ'אט פשוט
def start_chat():
    root = tk.Tk()
    root.title("עוזר אישי חכם")
    
    def send_message():
        user_input = entry.get()
        if user_input.lower() == "exit":
            root.quit()
        else:
            listbox.insert(tk.END, f"אתה: {user_input}")
            listbox.insert(tk.END, f"עוזר: אני לומד אותך!")

    # עיצוב ממשק
    listbox = tk.Listbox(root, height=15, width=50)
    listbox.pack(padx=10, pady=10)

    entry = tk.Entry(root, width=40)
    entry.pack(pady=10)

    send_button = tk.Button(root, text="שלח", command=send_message)
    send_button.pack(pady=5)

    root.mainloop()

# פונקציה לפתיחה של אתר או פעולה אחרת
def open_url():
    webbrowser.open("https://www.google.com")

# הפעלת הפונקציות
if __name__ == "__main__":
    get_api_key()  # שלב ראשון: בקשת API Key
    start_chat()  # שלב שני: פתיחת צ'אט עם המשתמש
