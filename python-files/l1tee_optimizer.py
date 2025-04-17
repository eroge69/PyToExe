
import os
from tkinter import Tk
import customtkinter as ctk

class OptimizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("L1tee Optimizer Panel")
        self.root.geometry("600x400")
        self.root.configure(bg="#1a1a2e")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title_label = ctk.CTkLabel(root, text="L1tee Optimizer Panel", font=("Arial Black", 24), text_color="#bb86fc")
        self.title_label.pack(pady=20)

        self.status_label = ctk.CTkLabel(root, text="Activated", font=("Arial", 18), text_color="#03dac6")
        self.status_label.pack(pady=10)

        self.divider = ctk.CTkLabel(root, text="─" * 70, text_color="#3f3f46")
        self.divider.pack(pady=5)

        self.footer_label = ctk.CTkLabel(root, text="Dev By: @ToxicL1te", font=("Consolas", 14), text_color="#888")
        self.footer_label.pack(side="bottom", pady=10)

app = Tk()
ui = OptimizerApp(app)
app.mainloop()
