import os
import json
import tkinter as tk
from tkinter import simpledialog
import webbrowser
import requests

# פונקציה לקרוא את ה-API Key
def get_api_key():
    config_file = "config.json"
    if not os.path.exists(config_file):
        root = tk.Tk()
        root.withdraw()
        api_key = simpledialog.askstring("API Key", "הכנס את ה-API Key שלך:")
        if api_key:
            with open(config_file, 'w') as f:
                json.dump({"api_key": api_key}, f)
            print("API Key נשמר בהצלחה!")
        else:
            print("לא הוזן API Key.")
        root.quit()
    else:
        with open(config_file, 'r') as f:
            data = json.load(f)
            api_key = data.get("api_key", "")
            if not api_key:
                get_api_key()
    return api_key

# פונקציה ששולחת שאלה ל-OpenAI ומקבלת תשובה
def ask_openai(prompt, api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 200
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"שגיאה בחיבור ל-GPT: {response.status_code}\n{response.text}"

# ממשק הצ'אט
def start_chat(api_key):
    root = tk.Tk()
    root.title("עוזר אישי חכם - מחובר ל-GPT")

    def send_message():
        user_input = entry.get()
        if user_input.lower() == "exit":
            root.quit()
        else:
            listbox.insert(tk.END, f"אתה: {user_input}")
            listbox.insert(tk.END, "עוזר: מחכה לתשובה...")
            root.update()
            response = ask_openai(user_input, api_key)
            listbox.delete(tk.END)  # מחק את "מחכה לתשובה"
            listbox.insert(tk.END, f"עוזר: {response}")
            entry.delete(0, tk.END)

    listbox = tk.Listbox(root, height=20, width=70)
    listbox.pack(padx=10, pady=10)

    entry = tk.Entry(root, width=50)
    entry.pack(pady=10)
    entry.bind('<Return>', lambda event: send_message())

    send_button = tk.Button(root, text="שלח", command=send_message)
    send_button.pack(pady=5)

    root.mainloop()

# הפעלת הכל
if __name__ == "__main__":
    api_key = get_api_key()
    start_chat(api_key)
