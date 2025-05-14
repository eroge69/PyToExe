import tkinter as tk
from tkinter import messagebox

class AntrianApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pemanggil Antrian")
        self.nomor = 0

        self.label = tk.Label(root, text=f"Nomor Antrian\n{self.nomor}", font=("Arial", 36), fg="blue")
        self.label.pack(pady=40)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=20)

        self.next_btn = tk.Button(btn_frame, text="Berikutnya", font=("Arial", 14), command=self.berikutnya)
        self.next_btn.grid(row=0, column=0, padx=10)

        self.ulangi_btn = tk.Button(btn_frame, text="Ulangi", font=("Arial", 14), command=self.ulangi)
        self.ulangi_btn.grid(row=0, column=1, padx=10)

        self.reset_btn = tk.Button(btn_frame, text="Reset", font=("Arial", 14), command=self.reset)
        self.reset_btn.grid(row=0, column=2, padx=10)

    def update_label(self):
        self.label.config(text=f"Nomor Antrian\n{self.nomor}")

    def berikutnya(self):
        self.nomor += 1
        self.update_label()
        self.panggil_suara()

    def ulangi(self):
        self.panggil_suara()

    def reset(self):
        if messagebox.askyesno("Reset", "Apakah Anda yakin ingin mereset nomor antrian?"):
            self.nomor = 0
            self.update_label()

    def panggil_suara(self):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(f"Nomor antrian {self.nomor}")
            engine.runAndWait()
        except:
            messagebox.showwarning("Peringatan", "Modul pyttsx3 tidak tersedia. Suara tidak akan diputar.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AntrianApp(root)
    root.mainloop()
