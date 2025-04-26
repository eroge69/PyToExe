import os
import json
import tkinter as tk
from tkinter import simpledialog
import webbrowser
import openai  # השתמש ב-API של OpenAI
import pyautogui  # יכול לשמש עבור פעולות במחשב

# הגדרת המפתח של OpenAI
openai.api_key = "הכנס את המפתח שלך כאן"

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

# הוספתי תמיכה בהדבקה עבור Entry
def paste(event):
    text = root.clipboard_get()  # קבל את התוכן מהקליפבורד
    entry.insert(tk.END, text)   # הדבק בשדה ה-Entry

# הפונקציה שתשאל את GPT מה לעשות אם הוא לא מבין את הפקודה
def ask_gpt_for_action(user_input):
    try:
        # שלח את הפקודה ל-GPT
        response = openai.Completion.create(
            engine="text-davinci-003",  # בחר את המנוע של GPT-3 (או GPT-4 אם יש לך גישה)
            prompt=f"אני עוזר אישי חכם. הפקודה היא: {user_input}. מה עלי לעשות?",
            max_tokens=150,
            temperature=0.7
        )
        action = response.choices[0].text.strip()  # קבל את התשובה מ-GPT
        return action
    except Exception as e:
        print(f"לא הצלחנו לשאול את GPT: {e}")
        return "הייתה בעיה בשיחה עם הבינה המלאכותית."

# ממשק משתמש צ'אט
def start_chat():
    global root, entry
    root = tk.Tk()
    root.title("עוזר אישי חכם")
    
    def send_message():
        user_input = entry.get()
        if user_input.lower() == "exit":
            root.quit()
        elif user_input.lower() == "פתח אתר":
            listbox.insert(tk.END, f"אתה: {user_input}")
            listbox.insert(tk.END, "עוזר: פותח את האתר...")
            open_url()  # פונקציה שתפתח אתר
        elif user_input.lower() == "שלח מייל":
            listbox.insert(tk.END, f"אתה: {user_input}")
            listbox.insert(tk.END, "עוזר: שולח את המייל...")
            send_email()  # תוכל להוסיף פונקציה לשליחת מייל
        else:
            listbox.insert(tk.END, f"אתה: {user_input}")
            listbox.insert(tk.END, "עוזר: לא הבנתי את הפקודה, שואל את GPT...")
            action = ask_gpt_for_action(user_input)  # פנה ל-GPT לקבלת תשובה
            listbox.insert(tk.END, f"עוזר: {action}")

    # עיצוב ממשק
    listbox = tk.Listbox(root, height=15, width=50)
    listbox.pack(padx=10, pady=10)

    entry = tk.Entry(root, width=40)
    entry.pack(pady=10)

    send_button = tk.Button(root, text="שלח", command=send_message)
    send_button.pack(pady=5)

    # הוספת אפשרות להדבקה
    entry.bind("<Control-v>", paste)
    
    root.mainloop()

# פונקציה לפתיחה של אתר
def open_url():
    webbrowser.open("https://www.google.com")

# פונקציה לשליחת מייל (דוגמה - תצטרך להוסיף את הפרטים שלך)
def send_email():
    print("שליחת המייל בוצעה בהצלחה!")

# הפעלת הפונקציות
if __name__ == "__main__":
    get_api_key()  # שלב ראשון: בקשת API Key
    start_chat()  # שלב שני: פתיחת צ'אט עם המשתמש
