import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox
import webbrowser
import requests

CONFIG_FILE = "config.json"

def save_api_key(api_key):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"api_key": api_key}, f)

def load_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return data.get("api_key", "")
    return ""

def get_or_ask_api_key():
    api_key = load_api_key()
    if not api_key:
        root = tk.Tk()
        root.withdraw()
        api_key = simpledialog.askstring("הזן את ה-API Key", "הכנס את המפתח שלך:")
        if api_key:
            save_api_key(api_key)
        else:
            messagebox.showerror("שגיאה", "לא הוזן מפתח.")
            exit()
        root.destroy()
    return api_key

def ask_openai(prompt, api_key):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 300
        }
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"שגיאה: {e}"

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
            listbox.delete(tk.END)
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

if __name__ == "__main__":
    try:
        api_key = get_or_ask_api_key()
        start_chat(api_key)
    except Exception as e:
        messagebox.showerror("שגיאה כללית", str(e))
