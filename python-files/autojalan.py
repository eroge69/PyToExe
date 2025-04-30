import os
import subprocess
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class LDLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LDPlayer Launcher")
        self.root.geometry("600x700")
        self.root.config(bg="#f4f4f9")  # Latar belakang default yang lebih lembut

        self.setup_widgets()
        self.log_file = "ldplayer_log.txt"

    def setup_widgets(self):
        # Frame utama untuk background gradasi
        self.background_frame = ttk.Frame(self.root, padding=(10, 10), style="TFrame")
        self.background_frame.pack(fill='both', expand=True)

        # Label judul di bagian atas
        ttk.Label(self.background_frame, text="Masukkan Rentang Instance (misal: 1-7):", font=("Arial", 12, "bold"), background="#f4f4f9").pack(pady=15)

        # Entry untuk rentang instance dengan style lebih elegan
        self.range_var = tk.StringVar()
        self.range_entry = ttk.Entry(self.background_frame, textvariable=self.range_var, font=("Arial", 12), width=20, justify='center')
        self.range_entry.insert(0, "Masukkan rentang...")
        self.range_entry.bind("<FocusIn>", self.clear_placeholder)
        self.range_entry.bind("<FocusOut>", self.set_placeholder)
        self.range_entry.pack(pady=10, ipady=5)

        # Frame untuk tombol agar berjajar secara horizontal dan rapi
        button_frame = ttk.Frame(self.background_frame)
        button_frame.pack(pady=15, fill='x', anchor='center')  # Mengatur posisi frame di tengah

        # Tombol Launch LDPlayer
        self.launch_button = tk.Button(button_frame, text="Launch LDPlayer", command=self.launch_ldplayers_thread, font=("Arial", 12, "bold"))
        self.launch_button.config(bg="#28a745", fg="white", relief="solid", bd=2, highlightbackground="#28a745", highlightcolor="#28a745")
        self.launch_button.grid(row=0, column=0, padx=20, pady=5)  # Menambahkan grid agar bisa berjajar di tengah

        # Tombol Kill All LDPlayer
        self.kill_button = tk.Button(button_frame, text="Kill All LDPlayer", command=self.kill_ldplayers, font=("Arial", 12, "bold"))
        self.kill_button.config(bg="#dc3545", fg="white", relief="solid", bd=2, highlightbackground="#dc3545", highlightcolor="#dc3545")
        self.kill_button.grid(row=0, column=1, padx=20, pady=5)  # Menambahkan grid agar bisa berjajar di tengah

        # Menambahkan teks "by @artharezkyy"
        self.footer_label = ttk.Label(self.background_frame, text="by @artharezkyy", font=("Arial", 10, "italic"), foreground="#6c757d", background="#f4f4f9")
        self.footer_label.pack(pady=10)

        # Tombol Show Daftar Instance
        self.show_button = tk.Button(self.background_frame, text="Tampilkan Daftar Instance", command=self.show_available_instances, font=("Arial", 12, "bold"))
        self.show_button.config(bg="#17a2b8", fg="white", relief="solid", bd=2, highlightbackground="#17a2b8", highlightcolor="#17a2b8")
        self.show_button.pack(pady=10, fill='x')

        # Tombol Clear Log
        self.clear_button = tk.Button(self.background_frame, text="Clear Log", command=self.clear_log, font=("Arial", 12, "bold"))
        self.clear_button.config(bg="#ffc107", fg="black", relief="solid", bd=2, highlightbackground="#ffc107", highlightcolor="#ffc107")
        self.clear_button.pack(pady=5, fill='x')

        # Listbox untuk menampilkan instance yang tersedia
        self.instance_listbox = tk.Listbox(self.background_frame, height=5, font=("Courier New", 12), bd=0, bg="#e0e0e0")
        self.instance_listbox.pack(padx=10, pady=(5, 0), fill='x')

        # Widget Text untuk log dengan pengaturan warna dan font
        self.log_text = tk.Text(self.background_frame, height=12, state='disabled', wrap=tk.WORD, width=60, bg="#f5f5f5", fg="black", font=("Courier New", 10))
        self.log_text.pack(padx=10, pady=10, fill='both', expand=True)

    def log(self, message):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        full_message = f"{timestamp} {message}"
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{full_message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")

    def clear_log(self):
        """Membersihkan isi dari area log."""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)  # Menghapus semua teks
        self.log_text.config(state='disabled')
        self.log("Log telah dibersihkan.")

    def launch_ldplayers_thread(self):
        thread = threading.Thread(target=self.launch_ldplayers)
        thread.start()

    def launch_ldplayers(self):
        try:
            instance_range = self.range_var.get()
            start, end = self.parse_range(instance_range)

            max_instance = self.get_available_instance_count()

            if max_instance == 0:
                messagebox.showerror("Error", "Tidak dapat mendeteksi instance LDPlayer.")
                return

            if start < 1 or end > max_instance or start > end:
                messagebox.showerror(
                    "Rentang Tidak Valid",
                    f"Hanya ada {max_instance} instance. Masukkan rentang yang valid (misal: 1-7)."
                )
                return

            for i in range(start, end + 1):
                name = f".-{i}"
                self.log(f"Launching LDPlayer instance {name}...")
                subprocess.run(["ldconsole.exe", "launch", "--name", name])
                time.sleep(2)

            time.sleep(3)
            self.log("✅ Semua LDPlayer dalam rentang berhasil diluncurkan.")
        except ValueError:
            messagebox.showerror("Error", "Masukkan rentang yang valid.")

    def parse_range(self, instance_range):
        """Mengonversi rentang instance dari string ke tuple (start, end)."""
        try:
            start, end = map(int, instance_range.split('-'))
            return start, end
        except ValueError:
            messagebox.showerror("Error", "Masukkan rentang dalam format yang benar (misal: 1 sampai bebas).")
            return 0, 0

    def get_available_instance_count(self):
        try:
            result = subprocess.run(["ldconsole.exe", "list2"], capture_output=True, text=True)
            lines = result.stdout.strip().splitlines()
            self.log(f"Daftar instance yang terdeteksi: {lines}")
            return len(lines)
        except Exception:
            return 0

    def show_available_instances(self):
        try:
            result = subprocess.run(["ldconsole.exe", "list2"], capture_output=True, text=True)
            instances = result.stdout.strip().splitlines()
            self.instance_listbox.delete(0, tk.END)

            if not instances:
                self.log("❌ Tidak ada instance ditemukan.")
                return

            tasklist = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq dnplayer.exe'], capture_output=True, text=True)
            running = tasklist.stdout.lower()

            self.log("📋 Daftar Instance LDPlayer:")
            for name in instances:
                name = name.strip()
                tag = "(Sedang running 🟢)" if self.is_instance_running(name, running) else ""
                display = f"{name} {tag}"
                self.instance_listbox.insert(tk.END, display)
                self.log(f"• {display}")

        except Exception as e:
            self.log(f"⚠️ Gagal mendapatkan daftar instance: {e}")

    def is_instance_running(self, instance_name, running_output):
        """Cek apakah instance sedang running berdasarkan namanya."""
        instance_name_lower = instance_name.lower()
        return any(instance_name_lower in line for line in running_output.splitlines())

    def get_selected_instance(self):
        selection = self.instance_listbox.curselection()
        if not selection:
            messagebox.showwarning("Tidak Ada Pilihan", "Pilih instance terlebih dahulu dari daftar.")
            return None
        line = self.instance_listbox.get(selection[0])
        return line.split()[0].strip()  # Ambil nama instance saja (tanpa tag)

    def launch_selected_instance(self):
        name = self.get_selected_instance()
        if name:
            self.log(f"🚀 Meluncurkan instance: {name}")

            # Verifikasi nama instance dengan daftar instance yang terdaftar
            result = subprocess.run(["ldconsole.exe", "list2"], capture_output=True, text=True)
            instances = result.stdout.strip().splitlines()
            instances = [instance.strip() for instance in instances]
            
            if name not in instances:
                messagebox.showerror("Error", f"Instance '{name}' tidak ditemukan.")
                self.log(f"❌ Instance {name} tidak ditemukan.")
                return
            
            # Jika instance ditemukan, jalankan
            self.log(f"Meluncurkan perintah: ldconsole.exe launch --name {name}")
            subprocess.run(["ldconsole.exe", "launch", "--name", name])
            self.log(f"✅ Instance {name} berhasil diluncurkan.")

    def kill_ldplayers(self):
        self.log("Menutup semua instance dnplayer.exe...")
        os.system("taskkill /F /IM dnplayer.exe")
        self.log("☠️ Semua LDPlayer telah ditutup.")

    def clear_placeholder(self, event):
        """Hapus placeholder saat entry di-klik."""
        if self.range_entry.get() == "Masukkan rentang...":
            self.range_entry.delete(0, tk.END)

    def set_placeholder(self, event):
        """Set placeholder jika entry kosong."""
        if not self.range_entry.get():
            self.range_entry.insert(0, "Masukkan rentang...")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("TFrame", background="#f4f4f9")
    app = LDLauncherApp(root)
    root.mainloop()
