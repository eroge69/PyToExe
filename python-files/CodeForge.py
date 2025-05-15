import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

# Ana pencere
root = tk.Tk()
root.title("CodeForge EXE Builder - by Mr.SenihX")
root.geometry("700x500")
root.configure(bg="#1e1e1e")
root.resizable(False, False)

# Başlık
title = tk.Label(
    root,
    text="CodeForge EXE Builder",
    font=("Segoe UI", 22, "bold"),
    fg="white",
    bg="#1e1e1e"
)
title.pack(pady=20)

subtitle = tk.Label(
    root,
    text="📦 Kodlarını tek tıklamayla .exe dosyasına dönüştür!",
    font=("Segoe UI", 12),
    fg="gray",
    bg="#1e1e1e"
)
subtitle.pack()

# Seçilen dosya yolu
selected_file = tk.StringVar()

# Dosya seçme fonksiyonu
def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Supported Files", "*.py *.c *.cpp *.js")]
    )
    if file_path:
        selected_file.set(file_path)

# Dönüştürme fonksiyonu (şimdilik sadece .py desteğiyle başlıyoruz)
def convert_to_exe():
    file_path = selected_file.get()
    if not file_path:
        messagebox.showerror("Hata", "Lütfen bir dosya seçin.")
        return

    ext = os.path.splitext(file_path)[1]

    if ext == ".py":
        try:
            subprocess.run(["pyinstaller", "--onefile", file_path], check=True)
            messagebox.showinfo("Başarılı", ".exe dosyası başarıyla oluşturuldu!")
        except subprocess.CalledProcessError:
            messagebox.showerror("Hata", ".exe oluşturulamadı. PyInstaller kurulu mu?")
    else:
        messagebox.showwarning("Desteklenmeyen", f"{ext} uzantısı şu an desteklenmiyor.")

# Dosya Seç Butonu
select_btn = tk.Button(
    root,
    text="📂 Dosya Seç",
    command=select_file,
    font=("Segoe UI", 10),
    bg="#0078D7",
    fg="white",
    padx=10,
    pady=5,
    relief="flat"
)
select_btn.pack(pady=20)

# Dosya Yolu Gösterimi
file_label = tk.Label(
    root,
    textvariable=selected_file,
    font=("Segoe UI", 9),
    bg="#1e1e1e",
    fg="white"
)
file_label.pack()

# Dönüştür Butonu
convert_btn = tk.Button(
    root,
    text="⚙️ EXE'ye Dönüştür",
    command=convert_to_exe,
    font=("Segoe UI", 11, "bold"),
    bg="#28a745",
    fg="white",
    padx=20,
    pady=10,
    relief="flat"
)
convert_btn.pack(pady=30)

# Alt bilgi
footer = tk.Label(
    root,
    text="Mr.SenihX tarafından tasarlanmıştır\n"
         "🌐 GitHub: https://github.com/SenihX   "
         "🛡️ TryHackMe: https://tryhackme.com/p/Mr.SenihX   "
         "𝕏 Twitter: https://x.com/SenihX_",
    font=("Segoe UI", 8),
    fg="gray",
    bg="#1e1e1e",
    justify="center",
    wraplength=650
)
footer.pack(side="bottom", pady=10)

root.mainloop()
