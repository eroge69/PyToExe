import tkinter as tk
from tkinter import messagebox
import keyboard
import os

class DeathCounter:
    def __init__(self, master):
        self.master = master
        self.death_count = 0
        self.file_path = "death_count.txt"
        
        self.reset_deaths()

        self.master.title("Death Counter")
        self.master.geometry("400x300")
        self.master.config(bg="#2c3e50")
        
        self.title_label = tk.Label(master, text="Mortes", font=("Helvetica", 24, "bold"), fg="#ecf0f1", bg="#2c3e50")
        self.title_label.pack(pady=10)
        
        self.label = tk.Label(master, text="Mortes: 0", font=("Helvetica", 20), fg="#ecf0f1", bg="#34495e", padx=20, pady=10)
        self.label.pack(pady=10)
        
        self.input_frame = tk.Frame(master, bg="#2c3e50")
        self.input_frame.pack(pady=10)
        
        self.input_label = tk.Label(self.input_frame, text="Definir Mortes:", font=("Helvetica", 16), fg="#ecf0f1", bg="#2c3e50")
        self.input_label.pack(side=tk.LEFT, padx=5)
        
        self.input_entry = tk.Entry(self.input_frame, font=("Helvetica", 16), width=5)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        
        self.input_button = tk.Button(self.input_frame, text="Definir", command=self.confirm_set_deaths, font=("Helvetica", 16))
        self.input_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(master, text="Resetar Mortes", command=self.confirm_reset_deaths, font=("Helvetica", 16))
        self.reset_button.pack(pady=10)
        
        keyboard.add_hotkey('up', self.add_death)
    
    def add_death(self):
        self.death_count += 1
        self.update_text_file()
        self.label.config(text=f"Mortes: {self.death_count}")

    def set_deaths(self):
        try:
            deaths = int(self.input_entry.get())
            self.death_count = deaths
            self.update_text_file()
            self.label.config(text=f"Mortes: {self.death_count}")
        except ValueError:
            pass 

    def reset_deaths(self):
        self.death_count = 0
        self.update_text_file()
        if hasattr(self, 'label'):
            self.label.config(text=f"Mortes: {self.death_count}")

    def update_text_file(self):
        with open(self.file_path, "w") as file:
            file.write(f"Mortes: {self.death_count}")

    def confirm_reset_deaths(self):
        response = messagebox.askquestion("Confirmação", "PARA DE ROBAR, você tem certeza?", icon='warning')
        if response == 'yes':
            self.reset_deaths()

    def confirm_set_deaths(self):
        response = messagebox.askquestion("Confirmação", "PARA DE ROBAR, você tem certeza?", icon='warning')
        if response == 'yes':
            self.set_deaths()

def main():
    root = tk.Tk()
    app = DeathCounter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
