import tkinter as tk
from tkinter import messagebox
import requests
import threading
import datetime
import time

# === JSONBIN Ayarları ===
BIN_ID = "682afee98a456b7966a0ff80"
API_KEY = "$2a$10$oLCHkWeUH.Cnzy6zU.BiOury3pHRa4CJu2oLMzm6F5XVStJu0rF4a"
API_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"

headers = {
    "X-Master-Key": API_KEY
}

# === Ürün limiti ayarları (varsayılan değerler) ===
urun_limitleri = {
    "Un": 300,
    "Şeker": 300,
    "Tuz": 300
}

# === Otomatik kontrol saati ===
otomatik_saat = "16:00"  # Varsayılan

# === Stok verisini jsonbin'den çek ===
def stok_durumu_getir():
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        return response.json()["record"]
    except requests.RequestException as e:
        messagebox.showerror("Hata", f"Veri alınamadı:\n{e}")
        return []

# === Otomatik kontrol ===
def otomatik_kontrol():
    while True:
        simdi = datetime.datetime.now().strftime("%H:%M")
        if simdi == otomatik_saat:
            veri = stok_durumu_getir()
            eksikler = []
            for urun in veri:
                if urun['miktar'] < urun_limitleri.get(urun['urun'], 1000):
                    eksikler.append(urun['urun'])
            if eksikler:
                messagebox.showinfo("Eksilen Ürün Uyarısı", f"Eksik ürünler: {', '.join(eksikler)}")
            time.sleep(60)  # Aynı dakikada tekrar etmesin
        time.sleep(30)

# === Sayfa değiştir ===
def sayfa_goster(sayfa):
    for widget in root.winfo_children():
        widget.pack_forget()
    sayfa()

# === Ana Sayfa ===
def ana_sayfa():
    buton_stok = tk.Button(root, text="Stok Durumu", command=lambda: sayfa_goster(stok_durumu_sayfasi), width=25, height=2)
    buton_stok.pack(pady=10)

    buton_liste = tk.Button(root, text="Alışveriş Listesi", command=lambda: sayfa_goster(alisveris_listesi_sayfasi), width=25, height=2)
    buton_liste.pack(pady=10)

    buton_ayar = tk.Button(root, text="Ayarlar", command=lambda: sayfa_goster(ayarlar_sayfasi), width=25, height=2)
    buton_ayar.pack(pady=10)

    buton_cikis = tk.Button(root, text="Çıkış", command=root.destroy, width=25, height=2)
    buton_cikis.pack(pady=10)

# === Stok Durumu Sayfası ===
def stok_durumu_sayfasi():
    veri = stok_durumu_getir()

    lbl = tk.Label(root, text="Stok Durumu", font=("Arial", 14))
    lbl.pack(pady=10)

    liste = tk.Listbox(root, width=40)
    liste.pack(pady=10)

    for urun in veri:
        satir = f"{urun['urun']} - {urun['miktar']} gr"
        liste.insert(tk.END, satir)

    btn_geri = tk.Button(root, text="Ana Sayfa", command=lambda: sayfa_goster(ana_sayfa))
    btn_geri.pack(pady=10)

# === Alışveriş Listesi Sayfası ===
def alisveris_listesi_sayfasi():
    veri = stok_durumu_getir()
    alisveris_listesi = []

    for urun in veri:
        ad = urun['urun']
        miktar = urun['miktar']
        limit = urun_limitleri.get(ad, 1000)
        if miktar < limit:
            alisveris_listesi.append(f"{ad} - {miktar} gr (Limit: {limit} gr)")

    lbl = tk.Label(root, text="Alışveriş Listesi", font=("Arial", 14))
    lbl.pack(pady=10)

    liste = tk.Listbox(root, width=50)
    liste.pack(pady=10)

    if alisveris_listesi:
        for item in alisveris_listesi:
            liste.insert(tk.END, item)
    else:
        liste.insert(tk.END, "Tüm ürünler yeterli miktarda.")

    btn_geri = tk.Button(root, text="Ana Sayfa", command=lambda: sayfa_goster(ana_sayfa))
    btn_geri.pack(pady=10)

# === Ayarlar Sayfası ===
def ayarlar_sayfasi():
    global otomatik_saat
    lbl = tk.Label(root, text="Ayarlar - Limit Belirleme", font=("Arial", 14))
    lbl.pack(pady=10)

    entryler = {}

    for urun, limit in urun_limitleri.items():
        frame = tk.Frame(root)
        frame.pack(pady=5)
        tk.Label(frame, text=urun, width=10, anchor="w").pack(side=tk.LEFT)
        entry = tk.Entry(frame, width=10)
        entry.insert(0, str(limit))
        entry.pack(side=tk.LEFT)
        entryler[urun] = entry

    # Otomatik saat girişi
    saat_frame = tk.Frame(root)
    saat_frame.pack(pady=10)
    tk.Label(saat_frame, text="Otomatik Kontrol Saati (HH:MM):").pack(side=tk.LEFT)
    saat_entry = tk.Entry(saat_frame, width=10)
    saat_entry.insert(0, otomatik_saat)
    saat_entry.pack(side=tk.LEFT)

    def kaydet():
        global otomatik_saat
        for urun, entry in entryler.items():
            try:
                yeni_limit = int(entry.get())
                urun_limitleri[urun] = yeni_limit
            except ValueError:
                messagebox.showerror("Hata", f"{urun} için geçersiz değer girdiniz.")
                return
        otomatik_saat = saat_entry.get()
        messagebox.showinfo("Başarılı", "Ayarlar güncellendi.")

    tk.Button(root, text="Güncelle ve Kaydet", command=kaydet).pack(pady=10)
    tk.Button(root, text="Ana Sayfa", command=lambda: sayfa_goster(ana_sayfa)).pack(pady=10)

# === Uygulama başlat ===
root = tk.Tk()
root.title("Akıllı Mutfak Rafı")
root.geometry("400x550")

# Arka planda otomatik kontrol thread'i başlat
kontrol_thread = threading.Thread(target=otomatik_kontrol, daemon=True)
kontrol_thread.start()

sayfa_goster(ana_sayfa)

root.mainloop()
