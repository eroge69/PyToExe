
import tkinter as tk
from tkinter import messagebox
import requests
import time

def scarica_pdf():
    base_url = "https://www.ow6.rassegnestampa.it/fidal/temp/"
    prefix = "051120242323"
    current_num = 99
    delay = 1
    i = 1

    while True:
        file_id = f"{prefix}{current_num:02d}"
        url = f"{base_url}{file_id}.pdf"
        filename = f"file_{i:02d}.pdf"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
                i += 1
                current_num -= 1
            elif response.status_code == 404:
                messagebox.showinfo("Download completato", f"{i-1} file scaricati.")
                break
            else:
                messagebox.showerror("Errore", f"Errore HTTP {response.status_code}")
                break
        except Exception as e:
            messagebox.showerror("Errore", f"Errore di rete: {e}")
            break

        time.sleep(delay)

# GUI
root = tk.Tk()
root.title("Scaricatore PDF FIDAL")
root.geometry("300x150")

label = tk.Label(root, text="Clicca per scaricare i PDF in ordine decrescente")
label.pack(pady=20)

button = tk.Button(root, text="Scarica PDF", command=scarica_pdf)
button.pack(pady=10)

root.mainloop()
