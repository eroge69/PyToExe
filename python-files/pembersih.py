import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
from datetime import datetime, timedelta
import traceback

try:
    import darkdetect
    from send2trash import send2trash
except ImportError:
    messagebox.showerror("Error", "Modul 'darkdetect' dan 'send2trash' dibutuhkan. Install dengan:\n\npip install darkdetect send2trash")
    raise

# Konfigurasi ekstensi preset
EXTENSION_PRESETS = {
    "Word": [".docx", ".docm", ".dotx", ".dotm", ".doc", ".rtf", ".odt"],
    "Excel": [".xlsx", ".xlsm", ".xls", ".xlsb", ".xltx", ".xltm", ".csv", ".ods"],
    "PowerPoint": [".pptx", ".ppsx", ".ppt", ".odp", ".pps", ".potx"],
    "PDF": [".pdf", ".xps"]
}

CONFIG = {
    "teks": {
        "judul": "Pembersih File Simple",
        "folder": "Folder Target",
        "jelajah": "Jelajahi...",
        "hari": "Hapus file lebih lama dari (hari):",
        "ukuran": "Hapus file lebih besar dari (MB):",
        "tipe": "Ekstensi file (pisahkan dengan koma):",
        "preset": "Preset Ekstensi:",
        "metode": "Metode penghapusan:",
        "sampah": "Ke Recycle Bin",
        "hapus": "Hapus Permanen",
        "preview": "Mode preview (tidak hapus file)",
        "scan": "Scan",
        "bersih": "Hapus",
        "status": "Siap",
        "konfirmasi": "Yakin ingin menghapus {n} file?",
        "selesai": "Hapus selesai: {ok} berhasil, {err} gagal",
        "opsi_hari": "Gunakan filter waktu",
        "opsi_ukuran": "Gunakan filter ukuran",
        "opsi_ekstensi": "Gunakan filter ekstensi",
        "sembunyikan": "Sembunyikan detail proses",
        "konfirmasi_tutup": "Sudah selesai kah, Pembersihannya?",
        "pesan_berhasil": "Berhasil memindahkan {jumlah} file ke Recycle Bin",
        "pesan_hapus": "Berhasil menghapus permanen {jumlah} file",
        "credit": "Dibuat oleh (Ipin) dengan harapan (Digunakan sebaik baiknya)"
    },
    "warna": {
        "light": {"bg": "#f5f5f5", "fg": "#333"},
        "dark": {"bg": "#333", "fg": "#f5f5f5"}
    }
}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(CONFIG["teks"]["judul"])
        self.files = []
        self.hide_details = False
        
        # Inisialisasi font sebelum digunakan
        self.default_font = font.nametofont("TkDefaultFont")
        self.bold_font = font.Font(weight="bold")
        
        # Sembunyikan main window sementara
        self.root.withdraw()
        
        # Tampilkan credit saat aplikasi dibuka
        self.show_credit()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.tema = "dark" if darkdetect.isDark() else "light"
        self.root.configure(bg=CONFIG["warna"][self.tema]["bg"])
        
        self.frame = ttk.Frame(root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Folder
        ttk.Label(self.frame, text=CONFIG["teks"]["folder"]).grid(row=0, column=0, sticky=tk.W)
        self.folder = tk.StringVar()
        ttk.Entry(self.frame, textvariable=self.folder, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(self.frame, text=CONFIG["teks"]["jelajah"], command=self.browse).grid(row=0, column=2)
        
        # Checkbox untuk mengaktifkan filter
        self.use_hari = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.frame, text=CONFIG["teks"]["opsi_hari"], variable=self.use_hari,
                       command=self.toggle_hari_field).grid(row=1, column=0, sticky=tk.W)
        
        # Hari
        self.hari_frame = ttk.Frame(self.frame)
        self.hari_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        self.hari = tk.StringVar(value="30")
        hari_options = ["7", "14", "30", "60", "90", "180", "365"]
        self.hari_combo = ttk.Combobox(self.hari_frame, textvariable=self.hari, values=hari_options, width=10, state="disabled")
        self.hari_combo.grid(row=0, column=0, padx=5)
        self.hari_combo.set("30")
        
        # Checkbox untuk ukuran
        self.use_ukuran = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.frame, text=CONFIG["teks"]["opsi_ukuran"], variable=self.use_ukuran,
                       command=self.toggle_ukuran_field).grid(row=2, column=0, sticky=tk.W)
        
        # Ukuran file dalam MB
        self.ukuran_frame = ttk.Frame(self.frame)
        self.ukuran_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        self.ukuran = tk.StringVar(value="10")
        ukuran_options = ["1", "5", "10", "50", "100", "500"]
        self.ukuran_combo = ttk.Combobox(self.ukuran_frame, textvariable=self.ukuran, values=ukuran_options, width=10, state="disabled")
        self.ukuran_combo.grid(row=0, column=0, padx=5)
        self.ukuran_combo.set("10")
        
        ttk.Label(self.ukuran_frame, text="MB").grid(row=0, column=1)
        
        # Checkbox untuk ekstensi
        self.use_ekstensi = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.frame, text=CONFIG["teks"]["opsi_ekstensi"], variable=self.use_ekstensi,
                       command=self.toggle_ekstensi_field).grid(row=3, column=0, sticky=tk.W)
        
        # Ekstensi
        self.ekstensi = tk.StringVar()
        self.ekstensi_entry = ttk.Entry(self.frame, textvariable=self.ekstensi, width=50, state="disabled")
        self.ekstensi_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Preset Ekstensi
        self.preset_frame = ttk.Frame(self.frame)
        self.preset_frame.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(self.preset_frame, text=CONFIG["teks"]["preset"]).grid(row=0, column=0, sticky=tk.W)
        
        self.preset_vars = {}
        col = 1
        for name, exts in EXTENSION_PRESETS.items():
            self.preset_vars[name] = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(self.preset_frame, text=name, variable=self.preset_vars[name],
                               command=self.update_preset_extensions)
            cb.grid(row=0, column=col, padx=5, sticky=tk.W)
            col += 1
        
        # Metode
        ttk.Label(self.frame, text=CONFIG["teks"]["metode"]).grid(row=5, column=0, sticky=tk.W)
        self.metode = tk.StringVar(value="sampah")
        ttk.Radiobutton(self.frame, text=CONFIG["teks"]["sampah"], variable=self.metode, 
                       value="sampah").grid(row=5, column=1, sticky=tk.W)
        ttk.Radiobutton(self.frame, text=CONFIG["teks"]["hapus"], variable=self.metode, 
                       value="hapus").grid(row=6, column=1, sticky=tk.W)
        
        # Preview
        self.preview = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.frame, text=CONFIG["teks"]["preview"], 
                       variable=self.preview).grid(row=7, column=1, sticky=tk.W)
        
        # Sembunyikan detail proses
        self.hide_details_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.frame, text=CONFIG["teks"]["sembunyikan"], 
                       variable=self.hide_details_var).grid(row=7, column=0, sticky=tk.W)
        
        # Tombol
        self.btn_frame = ttk.Frame(self.frame)
        self.btn_frame.grid(row=8, column=1, pady=10)
        ttk.Button(self.btn_frame, text=CONFIG["teks"]["scan"], 
                  command=self.scan).grid(row=0, column=0, padx=5)
        ttk.Button(self.btn_frame, text=CONFIG["teks"]["bersih"], 
                  command=self.clean).grid(row=0, column=1, padx=5)
        
        # Status
        self.status = tk.StringVar(value=CONFIG["teks"]["status"])
        ttk.Label(self.frame, textvariable=self.status).grid(row=9, column=0, columnspan=3, pady=5)
        
        # Output
        self.output = tk.Text(self.frame, height=10, width=60)
        self.output.grid(row=10, column=0, columnspan=3, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.output.yview)
        scrollbar.grid(row=10, column=3, sticky=(tk.N, tk.S))
        self.output['yscrollcommand'] = scrollbar.set
        
        # Credit
        credit_frame = ttk.Frame(self.frame)
        credit_frame.grid(row=11, column=0, columnspan=3, pady=5)
        
        credit_text = CONFIG["teks"]["credit"]
        parts = credit_text.split("(")
        for i, part in enumerate(parts):
            if ")" in part:
                text, rest = part.split(")", 1)
                label = ttk.Label(credit_frame, text="(" + text + ")", font=self.bold_font)
                label.pack(side="left")
                if rest:
                    ttk.Label(credit_frame, text=rest).pack(side="left")
            else:
                ttk.Label(credit_frame, text=part).pack(side="left")

    def show_credit(self):
        """Menampilkan credit saat aplikasi pertama dibuka"""
        credit_text = CONFIG["teks"]["credit"]
        
        credit_window = tk.Toplevel(self.root)
        credit_window.title("Credit")
        credit_window.geometry("400x150")
        credit_window.resizable(False, False)
        
        # Pusatkan window
        window_width = 400
        window_height = 150
        screen_width = credit_window.winfo_screenwidth()
        screen_height = credit_window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        credit_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        frame = ttk.Frame(credit_window, padding="20")
        frame.pack(expand=True, fill="both")
        
        text_frame = ttk.Frame(frame)
        text_frame.pack(pady=10)
        
        parts = credit_text.split("(")
        for i, part in enumerate(parts):
            if ")" in part:
                text, rest = part.split(")", 1)
                label = ttk.Label(text_frame, text="(" + text + ")", font=self.bold_font)
                label.pack(side="left")
                if rest:
                    ttk.Label(text_frame, text=rest).pack(side="left")
            else:
                ttk.Label(text_frame, text=part).pack(side="left")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame, 
            text="OK", 
            command=lambda: [credit_window.destroy(), self.root.deiconify()],
            width=15
        ).pack()
        
        credit_window.grab_set()
        credit_window.wait_window()

    def on_close(self):
        """Handle ketika window ditutup"""
        response = messagebox.askquestion(
            "Konfirmasi", 
            CONFIG["teks"]["konfirmasi_tutup"],
            icon='question',
            type=messagebox.YESNO,
            default=messagebox.NO
        )
        if response == 'yes':
            self.root.destroy()
        else:
            return

    def toggle_hari_field(self):
        if self.use_hari.get():
            self.hari_combo.config(state="normal")
        else:
            self.hari_combo.config(state="disabled")
            self.hari.set("30")

    def toggle_ukuran_field(self):
        if self.use_ukuran.get():
            self.ukuran_combo.config(state="normal")
        else:
            self.ukuran_combo.config(state="disabled")
            self.ukuran.set("10")

    def toggle_ekstensi_field(self):
        if self.use_ekstensi.get():
            self.ekstensi_entry.config(state="normal")
        else:
            self.ekstensi_entry.config(state="disabled")
            self.ekstensi.set("")
            for var in self.preset_vars.values():
                var.set(False)

    def browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder.set(os.path.normpath(folder))
    
    def update_preset_extensions(self):
        selected_exts = []
        for name, var in self.preset_vars.items():
            if var.get():
                selected_exts.extend(EXTENSION_PRESETS[name])
        
        if selected_exts:
            self.ekstensi.set(", ".join(set(selected_exts)))
        else:
            self.ekstensi.set("")
            
    def scan(self):
        folder = self.folder.get()
        if not folder:
            messagebox.showwarning("Peringatan", "Pilih folder terlebih dahulu!")
            return
            
        self.files = []
        self.output.delete(1.0, tk.END)
        
        try:
            hari = int(self.hari.get()) if self.use_hari.get() else None
        except ValueError:
            messagebox.showerror("Error", "Masukkan angka valid untuk hari!")
            return
            
        try:
            min_size = int(self.ukuran.get()) * 1024 * 1024 if self.use_ukuran.get() else 0
        except ValueError:
            messagebox.showerror("Error", "Masukkan angka valid untuk ukuran!")
            return
            
        ekstensi = [ext.strip().lower() for ext in self.ekstensi.get().split(",") if ext.strip()] if self.use_ekstensi.get() else []
        batas = datetime.now() - timedelta(days=hari) if hari else None
        
        for root, dirs, files in os.walk(folder):
            for file in files:
                try:
                    path = os.path.normpath(os.path.join(root, file))
                    if not os.path.exists(path):
                        continue
                        
                    stat = os.stat(path)
                    
                    if hari and batas and datetime.fromtimestamp(stat.st_mtime) > batas:
                        continue
                        
                    if self.use_ukuran.get() and stat.st_size < min_size:
                        continue
                        
                    if self.use_ekstensi.get() and ekstensi and not any(file.lower().endswith(ext) for ext in ekstensi):
                        continue
                        
                    self.files.append(path)
                    size_mb = stat.st_size / (1024 * 1024)
                    self.output.insert(tk.END, f"{os.path.basename(path)} ({size_mb:.2f} MB)\n")
                except Exception as e:
                    self.output.insert(tk.END, f"Error scanning {file}: {str(e)}\n")
                    continue
                    
        self.status.set(f"Ditemukan {len(self.files)} file siap dibersihkan.")
            
    def clean(self):
        if self.preview.get():
            messagebox.showinfo("Preview", "Mode preview aktif. Tidak ada file dihapus.")
            return
            
        if not self.files:
            messagebox.showinfo("Kosong", "Belum ada file yang discan atau ditemukan.")
            return
            
        if not messagebox.askyesno("Konfirmasi", CONFIG["teks"]["konfirmasi"].format(n=len(self.files))):
            return
            
        self.hide_details = self.hide_details_var.get()
        ok, err = 0, 0
        
        for path in self.files:
            try:
                path = os.path.normpath(path)
                if not os.path.exists(path):
                    if not self.hide_details:
                        self.output.insert(tk.END, "File tidak ditemukan\n")
                    err += 1
                    continue
                    
                if self.metode.get() == 'sampah':
                    try:
                        send2trash(path)
                        if not self.hide_details:
                            self.output.insert(tk.END, "Berhasil memindahkan ke Recycle Bin untuk File ini\n")
                        ok += 1
                    except Exception as e:
                        try:
                            os.remove(path)
                            if not self.hide_details:
                                self.output.insert(tk.END, "Berhasil menghapus permanen untuk File ini\n")
                            ok += 1
                        except Exception as e_inner:
                            err += 1
                            self.output.insert(tk.END, f"Gagal menghapus file: {str(e_inner)}\n")
                else:
                    os.remove(path)
                    if not self.hide_details:
                        self.output.insert(tk.END, "Berhasil menghapus permanen untuk File ini\n")
                    ok += 1
            except Exception as e:
                err += 1
                self.output.insert(tk.END, f"Gagal menghapus file: {str(e)}\n")
                
        if self.metode.get() == 'sampah':
            summary_msg = CONFIG["teks"]["pesan_berhasil"].format(jumlah=ok)
        else:
            summary_msg = CONFIG["teks"]["pesan_hapus"].format(jumlah=ok)
            
        self.output.insert(tk.END, f"\n{summary_msg}\n")
        self.status.set(CONFIG["teks"]["selesai"].format(ok=ok, err=err))
        self.output.see(tk.END)

        if ok > 0:
            if ok == 1:
                msg = "1 file telah berhasil diproses"
            else:
                msg = f"{ok} file telah berhasil diproses"
                
            if self.hide_details:
                messagebox.showinfo("Berhasil", msg)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()