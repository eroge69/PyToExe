import tkinter as tk
from tkinter import simpledialog, messagebox
import time
import threading
import sys
import os

def fake_delete_sequence(text_widget, foldername):
    text_widget.insert(tk.END, f"Lösche {foldername}...\n")
    text_widget.see(tk.END)
    text_widget.update()
    for i in range(1, 11):
        text_widget.insert(tk.END, f"  Datei {i}/10 gelöscht...\n")
        text_widget.see(tk.END)
        text_widget.update()
        time.sleep(0.3)

def fake_format_c(text_widget):
    text_widget.insert(tk.END, "Formatiere Laufwerk C: Schnellformat...\n")
    for i in range(0, 101, 10):
        text_widget.insert(tk.END, f"  Fortschritt: {i}%\n")
        text_widget.see(tk.END)
        text_widget.update()
        time.sleep(0.2)

def show_prank():
    root = tk.Tk()
    root.configure(bg="black")
    root.attributes('-fullscreen', True)
    root.title("Systemvorgang")

    text = tk.Text(root, bg="black", fg="lime", font=("Courier", 14))
    text.pack(expand=True, fill="both")
    
    def run_sequence():
        # Eingabe
        username = simpledialog.askstring("Sicherheitshinweis", "Ihr Name bitte:", parent=root)
        if username is None:
            root.destroy()
            return

        messagebox.showwarning("Warnung", f"Wahrscheinlich haben Sie sich gerade einen Computervirus eingefangen.")
        messagebox.askquestion("Virus löschen?", "Soll der Virus sofort gelöscht werden?")

        # Simulation
        fake_delete_sequence(text, "Downloads")
        time.sleep(1)
        fake_delete_sequence(text, "Bilder")
        time.sleep(1)
        text.insert(tk.END, "\nVirus entfernt.\n")
        text.update()
        time.sleep(2)

        fake_format_c(text)
        time.sleep(2)

        # Spaßmeldung
        text.delete("1.0", tk.END)
        text.insert(tk.END, "\nWar alles nur ein Spaß! 😄")
        text.tag_configure("center", justify='center')
        text.tag_add("center", "1.0", "end")
        text.update()
        time.sleep(3)

        root.destroy()

    threading.Thread(target=run_sequence).start()
    root.mainloop()

if __name__ == "__main__":
    show_prank()
