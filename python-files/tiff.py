import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

# Mevcut işlevsellik
def convert_to_tiff(input_path, output_folder, compression='tiff_lzw'):
    try:
        img = Image.open(input_path)
        
        filename = os.path.basename(input_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        output_path = os.path.join(output_folder, f"{name_without_ext}.tiff")
        
        img.save(output_path, format='TIFF', compression=compression)
        return True, output_path
    except Exception as e:
        return False, str(e)

class TiffConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TIFF Dönüştürücü")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Ana tema renkleri
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.text_color = "#ecf0f1"
        self.bg_color = "#f5f5f5"
        self.success_color = "#2ecc71"
        self.error_color = "#e74c3c"
        
        # Değişkenler
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.status_text = tk.StringVar(value="Hazır")
        self.progress_var = tk.DoubleVar(value=0)
        self.compression_type = tk.StringVar(value="tiff_lzw")
        
        # Desteklenen formatlar
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tif')
        
        self.create_widgets()
        self.file_list = []
        self.conversion_active = False
        
    def create_widgets(self):
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Stil ayarları
        style = ttk.Style()
        style.configure("TFrame", background=self.bg_color)
        style.configure("TButton", background=self.secondary_color, foreground=self.text_color, font=("Arial", 10, "bold"))
        style.configure("TLabel", background=self.bg_color, font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 18, "bold"))
        style.configure("Status.TLabel", font=("Arial", 10, "italic"))
        
        # Başlık
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="TIFF Dönüştürücü", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        author_label = ttk.Label(header_frame, text="Made by Oseyan", style="Status.TLabel")
        author_label.pack(side=tk.RIGHT)
        
        # Klasör seçimi çerçevesi
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=10)
        
        # Giriş klasörü
        input_frame = ttk.Frame(folder_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        input_label = ttk.Label(input_frame, text="Kaynak Klasör:")
        input_label.pack(side=tk.LEFT, padx=(0, 10))
        
        input_entry = ttk.Entry(input_frame, textvariable=self.input_folder)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        input_button = ttk.Button(input_frame, text="Gözat", command=self.select_input_folder)
        input_button.pack(side=tk.RIGHT)
        
        # Çıkış klasörü
        output_frame = ttk.Frame(folder_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        output_label = ttk.Label(output_frame, text="Hedef Klasör:")
        output_label.pack(side=tk.LEFT, padx=(0, 10))
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_folder)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        output_button = ttk.Button(output_frame, text="Gözat", command=self.select_output_folder)
        output_button.pack(side=tk.RIGHT)
        
        # Sıkıştırma seçenekleri
        compression_frame = ttk.Frame(main_frame)
        compression_frame.pack(fill=tk.X, pady=10)
        
        compression_label = ttk.Label(compression_frame, text="Sıkıştırma Türü:")
        compression_label.pack(side=tk.LEFT, padx=(0, 10))
        
        compression_options = ["tiff_lzw", "tiff_deflate", "tiff_adobe_deflate", "none"]
        compression_menu = ttk.Combobox(compression_frame, textvariable=self.compression_type, values=compression_options)
        compression_menu.pack(side=tk.LEFT, padx=(0, 10))
        
        # Dosya listesi alanı
        list_frame = ttk.LabelFrame(main_frame, text="Dönüştürülecek Dosyalar")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar ve Listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=tk.EXTENDED, bg="white", font=("Arial", 9))
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar.config(command=self.file_listbox.yview)
        
        # Kontrol düğmeleri
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        scan_button = ttk.Button(control_frame, text="Dosyaları Tara", command=self.scan_files)
        scan_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_button = ttk.Button(control_frame, text="Listeyi Temizle", command=self.clear_list)
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.convert_button = ttk.Button(control_frame, text="Dönüştür", command=self.start_conversion)
        self.convert_button.pack(side=tk.RIGHT)
        
        # İlerleme çubuğu
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate', variable=self.progress_var)
        self.progress_bar.pack(fill=tk.X)
        
        # Durum çubuğu
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        status_label = ttk.Label(status_frame, textvariable=self.status_text, style="Status.TLabel")
        status_label.pack(side=tk.LEFT)
        
        # Sonuç çerçevesi
        self.result_frame = ttk.Frame(main_frame)
        self.result_frame.pack(fill=tk.X, pady=5)
        
        self.success_var = tk.StringVar(value="Başarılı: 0")
        self.fail_var = tk.StringVar(value="Başarısız: 0")
        
        success_label = ttk.Label(self.result_frame, textvariable=self.success_var, foreground=self.success_color)
        success_label.pack(side=tk.LEFT, padx=(0, 20))
        
        fail_label = ttk.Label(self.result_frame, textvariable=self.fail_var, foreground=self.error_color)
        fail_label.pack(side=tk.LEFT)
    
    def select_input_folder(self):
        folder = filedialog.askdirectory(title="Dönüştürülecek görsellerin bulunduğu klasörü seçin")
        if folder:
            self.input_folder.set(folder)
            self.scan_files()
    
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="TIFF dosyalarının kaydedileceği klasörü seçin")
        if folder:
            self.output_folder.set(folder)
    
    def scan_files(self):
        input_folder = self.input_folder.get()
        if not input_folder or not os.path.isdir(input_folder):
            messagebox.showerror("Hata", "Lütfen geçerli bir kaynak klasör seçin!")
            return
        
        self.file_list = []
        self.file_listbox.delete(0, tk.END)
        
        for filename in os.listdir(input_folder):
            if filename.lower().endswith(self.supported_formats):
                full_path = os.path.join(input_folder, filename)
                self.file_list.append(full_path)
                self.file_listbox.insert(tk.END, filename)
        
        self.status_text.set(f"{len(self.file_list)} dosya bulundu.")
    
    def clear_list(self):
        self.file_list = []
        self.file_listbox.delete(0, tk.END)
        self.status_text.set("Liste temizlendi.")
    
    def start_conversion(self):
        if self.conversion_active:
            return
            
        if not self.file_list:
            messagebox.showwarning("Uyarı", "Dönüştürülecek dosya bulunamadı. Lütfen önce dosyaları tarayın.")
            return
            
        output_folder = self.output_folder.get()
        if not output_folder:
            messagebox.showerror("Hata", "Lütfen geçerli bir hedef klasör seçin!")
            return
            
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
            except Exception as e:
                messagebox.showerror("Hata", f"Hedef klasör oluşturulamadı: {str(e)}")
                return
        
        # Aynı klasör kontrolü
        if self.input_folder.get() == output_folder:
            response = messagebox.askyesno("Uyarı", "Kaynak ve hedef klasörler aynı. Devam etmek istiyor musunuz?")
            if not response:
                return
        
        # Dönüştürme işlemini ayrı bir thread'de başlat
        self.conversion_active = True
        self.convert_button.config(state=tk.DISABLED)
        conversion_thread = threading.Thread(target=self.convert_files)
        conversion_thread.daemon = True
        conversion_thread.start()
    
    def convert_files(self):
        output_folder = self.output_folder.get()
        compression = self.compression_type.get()
        total_files = len(self.file_list)
        success_count = 0
        fail_count = 0
        
        for i, file_path in enumerate(self.file_list):
            self.status_text.set(f"Dönüştürülüyor: {os.path.basename(file_path)}")
            
            success, result = convert_to_tiff(file_path, output_folder, compression)
            
            if success:
                success_count += 1
                # Listboxta başarılı öğeleri yeşil yapabiliriz (isteğe bağlı)
                # self.file_listbox.itemconfig(i, {'bg': self.success_color})
            else:
                fail_count += 1
                # Listboxta başarısız öğeleri kırmızı yapabiliriz (isteğe bağlı)
                # self.file_listbox.itemconfig(i, {'bg': self.error_color})
            
            # İlerleme çubuğunu güncelle
            progress = (i + 1) / total_files * 100
            self.progress_var.set(progress)
            
            # Sonuç sayacını güncelle
            self.success_var.set(f"Başarılı: {success_count}")
            self.fail_var.set(f"Başarısız: {fail_count}")
            
            # GUI güncellemesi için kısa bekleme
            self.root.update_idletasks()
        
        self.status_text.set("Dönüştürme tamamlandı!")
        messagebox.showinfo("İşlem Tamamlandı", 
                          f"Dönüştürme tamamlandı!\nBaşarılı: {success_count}\nBaşarısız: {fail_count}")
        
        # Dönüştürme işlemini tamamlandı olarak işaretle
        self.conversion_active = False
        self.convert_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = TiffConverterApp(root)
    root.mainloop()