import tkinter as tk
from tkinter import filedialog, messagebox
import os
import io
from google.oauth2 import service_account
from google.cloud import vision
from PIL import Image

def analyze_image(image_path, credentials_path):
    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = vision.ImageAnnotatorClient(credentials=credentials)
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.label_detection(image=image)
        labels = response.label_annotations
        if response.error.message:
            raise Exception(response.error.message)
        return ', '.join(label.description for label in labels[:3])
    except Exception as e:
        return f"Błąd: {e}"

def show_splash(root):
    splash = tk.Toplevel()
    splash.overrideredirect(True)
    splash.geometry("300x150+600+350")
    label = tk.Label(splash, text="Wczytywanie...", font=("Helvetica", 16))
    label.pack(expand=True)
    splash.after(2500, splash.destroy)
    root.withdraw()
    root.after(2500, root.deiconify)

class VisionApp:
    def __init__(self, master):
        self.master = master
        master.title("Vision App z Google API")
        master.geometry("600x300")
        self.folder_path = ""
        self.key_path = ""

        self.label = tk.Label(master, text="Wybierz folder ze zdjęciami:")
        self.label.pack()
        self.select_folder_button = tk.Button(master, text="Wybierz folder", command=self.select_folder)
        self.select_folder_button.pack()
        self.key_label = tk.Label(master, text="Wybierz plik klucza Google (.json):")
        self.key_label.pack()
        self.select_key_button = tk.Button(master, text="Wybierz klucz", command=self.select_key)
        self.select_key_button.pack()
        self.location_label = tk.Label(master, text="Dodaj lokalizację (np. Seville, Spain):")
        self.location_label.pack()
        self.location_entry = tk.Entry(master, width=50)
        self.location_entry.pack()
        self.run_button = tk.Button(master, text="Rozpocznij analizę", command=self.run_analysis)
        self.run_button.pack(pady=10)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            messagebox.showinfo("Folder", f"Wybrano folder:
{self.folder_path}")

    def select_key(self):
        self.key_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if self.key_path:
            messagebox.showinfo("Klucz API", f"Załadowano klucz:
{self.key_path}")

    def run_analysis(self):
        if not self.folder_path or not self.key_path:
            messagebox.showerror("Błąd", "Musisz wybrać folder i plik z kluczem.")
            return
        location = self.location_entry.get().strip()
        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(self.folder_path, filename)
                description = analyze_image(filepath, self.key_path)
                if "Błąd" not in description:
                    new_name = f"{description} {location}".strip().replace(" ", "_")
                    new_path = os.path.join(self.folder_path, new_name + os.path.splitext(filename)[1])
                    os.rename(filepath, new_path)
        messagebox.showinfo("Gotowe", "Analiza zakończona. Nazwy plików zostały zmienione.")

if __name__ == "__main__":
    root = tk.Tk()
    show_splash(root)
    app = VisionApp(root)
    root.mainloop()
