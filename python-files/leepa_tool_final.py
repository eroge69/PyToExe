
import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import json

FIELD_IDS = [7050, 7045, 7044, 8159, 7046, 7043, 8163, 6938]
BASE_URL = "http://10.73.93.198:8443/leepaApi"
AUTH_KEY = "xs7kSDX9lSsWFwMYRhmRcmQYxa10LmCNhfycchbVAuOFGrXNzH88XuQpCFBbgZ7tK5VPlDQJJRIWQNa9nVNZrhvUAm0s5rmuFNHFgz3EBdcE03T3dLZjLl1lKK20jnfO6V5hEEiMOt69iVmrKMDkSrwcruTF7BZBHeQyq2mlOyeLxR7Mb32RV979W4HUID5uiopr9XtNxHT4NG4tNjud4YCnA6aA3U3KFaVwlZ3b5nrQl7VUritBusLjq7kHghSL"

def fetch_data(order_id):
    try:
        params = {
            "id": order_id,
            "authKey": AUTH_KEY
        }
        for field_id in FIELD_IDS:
            params.setdefault("fields", []).append(field_id)
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return json.dumps(response.json(), indent=4)
    except Exception as e:
        return f"Fehler beim Abrufen der Daten: {e}"

def on_fetch_click():
    order_id = entry.get()
    if not order_id.startswith("SI") or "-" not in order_id:
        messagebox.showerror("Fehler", "Bitte eine gültige Auftragsnummer im Format SIXXXXXXX-XX eingeben.")
        return
    output.delete("1.0", tk.END)
    result = fetch_data(order_id)
    output.insert(tk.END, result)

root = tk.Tk()
root.title("Leepa API Viewer")
root.geometry("800x600")

tk.Label(root, text="Auftragsnummer (z. B. SI2500089-02):").pack(pady=10)
entry = tk.Entry(root, width=30)
entry.pack(pady=5)

tk.Button(root, text="Abrufen", command=on_fetch_click).pack(pady=10)

output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30)
output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
