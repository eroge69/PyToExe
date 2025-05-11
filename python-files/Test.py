import tkinter as tk
from tkinter import ttk
import requests
import threading
from flask import Flask, request, jsonify

# Flask API for receiving webhooks
app = Flask(__name__)
webhook_data = {}

@app.route('/webhook/<webhook_id>', methods=['POST'])
def receive_webhook(webhook_id):
    data = request.json
    webhook_data[webhook_id] = data
    update_log()
    return jsonify({"status": "Received", "webhook_id": webhook_id})

def start_flask():
    app.run(host='0.0.0.0', port=5000)

flask_thread = threading.Thread(target=start_flask, daemon=True)
flask_thread.start()

# UI Setup
root = tk.Tk()
root.title("Webhook Manager")
root.geometry("600x600")
root.configure(bg="#1E1E1E")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Arial", 12), background="#444", foreground="white")
style.map("TButton", background=[("active", "#666")])
style.configure("Hover.TButton", background="#888")

def send_webhook(url, payload):
    response = requests.post(url, json={"content": payload})
    status_label.config(text=f"Sent: {response.status_code}")

buttons = []

def add_button():
    webhook_url = url_entry.get()
    payload = text_entry.get("1.0", tk.END).strip()
    
    if webhook_url and payload:
        btn = ttk.Button(button_frame, text=f"Send {len(buttons)+1}",
                         command=lambda: send_webhook(webhook_url, payload))
        btn.pack(pady=5, fill='x')

        btn.bind("<Enter>", lambda e: btn.config(style="Hover.TButton"))
        btn.bind("<Leave>", lambda e: btn.config(style="TButton"))

        buttons.append(btn)

def update_log():
    log_entry.delete("1.0", tk.END)
    for key, value in webhook_data.items():
        log_entry.insert(tk.END, f"Webhook [{key}]: {value}\n")

# UI Elements
url_label = tk.Label(root, text="Webhook URL:", fg="white", bg="#1E1E1E", font=("Arial", 12))
url_label.pack(pady=5)

url_entry = tk.Entry(root, width=50, font=("Arial", 12))
url_entry.pack(pady=5)

text_label = tk.Label(root, text="Message:", fg="white", bg="#1E1E1E", font=("Arial", 12))
text_label.pack(pady=5)

text_entry = tk.Text(root, width=50, height=5, font=("Arial", 12))
text_entry.pack(pady=5)

add_button_btn = ttk.Button(root, text="Add Webhook Button", command=add_button)
add_button_btn.pack(pady=10)

status_label = tk.Label(root, text="", fg="white", bg="#1E1E1E", font=("Arial", 12))
status_label.pack(pady=5)

button_frame = tk.Frame(root, bg="#1E1E1E")
button_frame.pack(fill='both', expand=True)

log_label = tk.Label(root, text="Webhook Log:", fg="white", bg="#1E1E1E", font=("Arial", 12))
log_label.pack(pady=5)

log_entry = tk.Text(root, width=50, height=10, font=("Arial", 12))
log_entry.pack(pady=5)

root.mainloop()
