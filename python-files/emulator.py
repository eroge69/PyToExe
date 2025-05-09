import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import zipfile
import tempfile

# Sabit yollar (Miraç için)
EMULATOR_EXE = "C:/Users/Miraç/AppData/Local/Android/Sdk/emulator/emulator.exe"
ADB_EXE = "C:/Users/Miraç/AppData/Local/Android/Sdk/platform-tools/adb.exe"

def log(message):
    log_area.insert(tk.END, message + "\n")
    log_area.see(tk.END)

def select_file():
    filepath = filedialog.askopenfilename(filetypes=[("APK/XAPK files", "*.apk *.xapk")])
    if filepath:
        file_path.set(filepath)
        log(f"📦 Seçilen dosya: {filepath}")

def start_emulator():
    try:
        subprocess.Popen([EMULATOR_EXE, "-avd", "Pixel_API_30"])  # AVD adını kendine göre ayarla
        log("🚀 Emülatör başlatıldı.")
    except Exception as e:
        log(f"❌ Emülatör başlatılamadı: {e}")

def install_apk(path):
    try:
        subprocess.run([ADB_EXE, "install", path], check=True)
        log("✅ APK başarıyla yüklendi.")
    except Exception as e:
        log(f"❌ APK yüklenemedi: {e}")

def install_xapk(path):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(tempdir)
                log(f"📂 XAPK içeriği çıkartıldı: {tempdir}")

                apk_file = None
                for f in os.listdir(tempdir):
                    if f.endswith(".apk"):
                        apk_file = os.path.join(tempdir, f)
                        break

                if not apk_file:
                    raise Exception("XAPK içinde .apk bulunamadı.")

                # OBB varsa cihaza kopyala
                obb_path = os.path.join(tempdir, "Android", "obb")
                if os.path.isdir(obb_path):
                    log("📁 OBB bulundu, cihaza kopyalanıyor...")
                    for root, dirs, files in os.walk(obb_path):
                        for file in files:
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, tempdir)
                            device_path = f"/sdcard/{rel_path.replace(os.sep, '/')}"
                            subprocess.run([ADB_EXE, "push", full_path, device_path])
                    log("✅ OBB kopyalandı.")

                install_apk(apk_file)
    except Exception as e:
        log(f"❌ XAPK yüklenemedi: {e}")

def install_selected():
    path = file_path.get()
    if not os.path.isfile(path):
        messagebox.showerror("Hata", "Geçerli bir dosya seçilmedi.")
        return

    if path.endswith(".apk"):
        install_apk(path)
    elif path.endswith(".xapk"):
        install_xapk(path)
    else:
        log("❓ Desteklenmeyen dosya türü.")

# GUI Arayüzü
root = tk.Tk()
root.title("📱 Miraç Emülatör Arayüzü")
root.geometry("600x460")
root.configure(bg="#2b2b2b")

file_path = tk.StringVar()

# Dikdörtgen butonlar için fonksiyon
def create_rectangle_button(parent, text, command):
    return tk.Button(parent, text=text, command=command, bg="#3a86ff", fg="white", font=("Arial", 12),
                     relief="solid", bd=2, width=20, height=2, activebackground="#56CCF2", activeforeground="white",
                     highlightthickness=0)

tk.Label(root, text="APK / XAPK Dosyası Seç:", fg="white", bg="#2b2b2b", font=("Arial", 12)).pack(pady=5)
tk.Entry(root, textvariable=file_path, width=60).pack(padx=10)

# Dikdörtgen butonlar
create_rectangle_button(root, "📂 Dosya Seç", select_file).pack(pady=5)
create_rectangle_button(root, "🚀 Emülatörü Başlat", start_emulator).pack(pady=5)
create_rectangle_button(root, "📱 Yüklemeyi Başlat", install_selected).pack(pady=10)

log_area = scrolledtext.ScrolledText(root, width=70, height=10, bg="#1e1e1e", fg="lime", font=("Courier", 10))
log_area.pack(padx=10, pady=5)

root.mainloop()
