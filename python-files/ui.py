import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class ModernExcelComparisonUI:
    def __init__(self, root, app_logic):
        self.root = root
        self.app_logic = app_logic
        
        # Modern tema ayarları
        self.setup_modern_theme()
        
        # Ana pencere ayarları
        self.setup_main_window()
        
        # Arayüz bileşenlerini oluştur
        self.create_modern_interface()
        
    def setup_modern_theme(self):
        """Modern tema ve renkler"""
        self.colors = {
            'primary': '#2563eb',      # Modern mavi
            'primary_hover': '#1d4ed8', # Koyu mavi
            'secondary': '#64748b',     # Gri-mavi
            'success': '#10b981',       # Yeşil
            'warning': '#f59e0b',       # Turuncu
            'danger': '#ef4444',        # Kırmızı
            'background': '#f8fafc',    # Açık gri arka plan
            'card': '#ffffff',          # Beyaz kart
            'border': '#e2e8f0',       # Açık gri kenarlık
            'text': '#1e293b',         # Koyu gri metin
            'text_light': '#64748b'     # Açık gri metin
        }
        
        # Modern stil tanımlamaları
        style = ttk.Style()
        
        # Tema seç (mevcut temalar arasından en uygun olanı)
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # Özel stil tanımlamaları
        self.configure_modern_styles(style)
        
    def configure_modern_styles(self, style):
        """Modern stil konfigürasyonları"""
        # Ana buton stili
        style.configure(
            'Modern.TButton',
            font=('Segoe UI', 10),
            padding=(20, 12),
            relief='flat',
            borderwidth=0
        )
        
        # Vurgulu buton stili
        style.configure(
            'Accent.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=(25, 15),
            relief='flat',
            borderwidth=0
        )
        
        # İkincil buton stili
        style.configure(
            'Secondary.TButton',
            font=('Segoe UI', 10),
            padding=(20, 12),
            relief='flat',
            borderwidth=1
        )
        
        # LabelFrame stili
        style.configure(
            'Modern.TLabelframe',
            relief='flat',
            borderwidth=1,
            padding=20
        )
        
        style.configure(
            'Modern.TLabelframe.Label',
            font=('Segoe UI', 11, 'bold'),
            padding=(0, 5)
        )
        
        # Entry stili
        style.configure(
            'Modern.TEntry',
            font=('Segoe UI', 10),
            padding=10,
            relief='flat',
            borderwidth=1
        )
        
        # Checkbutton stili
        style.configure(
            'Modern.TCheckbutton',
            font=('Segoe UI', 10),
            padding=(0, 5)
        )
        
        # Radiobutton stili
        style.configure(
            'Modern.TRadiobutton',
            font=('Segoe UI', 10),
            padding=(0, 3)
        )
        
    def setup_main_window(self):
        """Ana pencere ayarları"""
        self.root.title("CAL Excel Cari Karşılaştırma")
        self.root.geometry("1000x850")  # Dikey boyutu daha da artırdım
        self.root.minsize(950, 800)
        
        # Pencereyi ortala
        self.center_window()
        
        # Arka plan rengi
        self.root.configure(bg=self.colors['background'])
        
        # İkon ayarla (varsa)
        try:
            # İkon dosyası varsa kullan
            self.root.iconbitmap('icon.ico')
        except:
            pass
            
    def center_window(self):
        """Pencereyi ekranın ortasına yerleştir"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_modern_interface(self):
        """Modern arayüz bileşenlerini oluştur"""
        # Ana konteyner
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık bölümü
        self.create_header(main_container)
        
        # İçerik container'ı
        content_frame = tk.Frame(main_container, bg=self.colors['background'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Sol panel (Dosya seçimi ve seçenekler)
        left_panel = tk.Frame(content_frame, bg=self.colors['background'])
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Sağ panel (Sonuçlar)
        right_panel = tk.Frame(content_frame, bg=self.colors['background'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Sol paneli oluştur
        self.create_left_panel(left_panel)
        
        # Sağ paneli oluştur
        self.create_right_panel(right_panel)
        
    def create_header(self, parent):
        """Başlık bölümünü oluştur"""
        header_frame = tk.Frame(parent, bg=self.colors['card'], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Başlık metni
        title_label = tk.Label(
            header_frame,
            text="Excel Cari Ünvan Karşılaştırma",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text'],
            pady=15
        )
        title_label.pack()
        
        # Alt başlık
        subtitle_label = tk.Label(
            header_frame,
            text="İki Excel dosyasındaki cari ünvanları karşılaştırır ve farklılıkları tespit eder.",
            font=('Segoe UI', 10),
            bg=self.colors['card'],
            fg=self.colors['text_light']
        )
        subtitle_label.pack()
        
    def create_left_panel(self, parent):
        """Sol panel (Dosya seçimi ve seçenekler)"""
        # Sol panel için sabit genişlik ayarla
        parent.config(width=380)
        parent.pack_propagate(False)
        
        # Dosya seçimi kartı
        self.create_file_selection_card(parent)
        
        # Boşluk - Minimal
        tk.Frame(parent, bg=self.colors['background'], height=5).pack()
        
        # Seçenekler kartı
        self.create_options_card(parent)
        
        # Boşluk - Minimal
        tk.Frame(parent, bg=self.colors['background'], height=5).pack()
        
        # İşlem butonları
        self.create_action_buttons(parent)
        
    def create_file_selection_card(self, parent):
        """Dosya seçimi kartı"""
        card_frame = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        card_frame.pack(fill=tk.X, pady=5)
        
        # Kart başlığı
        header = tk.Label(
            card_frame,
            text="📁 Dosya Seçimi",
            font=('Segoe UI', 10, 'bold'),  # Daha küçük font
            bg=self.colors['card'],
            fg=self.colors['text'],
            pady=8  # Daha az padding
        )
        header.pack(anchor=tk.W, padx=20)
        
        # Dosya seçimi içeriği
        content_frame = tk.Frame(card_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.X, padx=12, pady=(0, 12))  # Daha minimal padding
        
        # Eski dosya
        self.create_file_input(
            content_frame,
            "Eski Tarihli Excel Dosyası",
            self.app_logic.file1_path,
            self.browse_file1,
            "📄"
        )
        
        # Boşluk - Daha da küçük
        tk.Frame(content_frame, bg=self.colors['card'], height=8).pack()
        
        # Yeni dosya
        self.create_file_input(
            content_frame,
            "Yeni Tarihli Excel Dosyası",
            self.app_logic.file2_path,
            self.browse_file2,
            "📄"
        )
        
        # Boşluk
        tk.Frame(content_frame, bg=self.colors['card'], height=15).pack()
        
        # Çıktı dosyası
        self.create_file_input(
            content_frame,
            "Sonuç Dosyası",
            self.app_logic.output_path,
            self.browse_output,
            "💾"
        )
        
    def create_file_input(self, parent, label_text, text_var, browse_command, icon):
        """Dosya seçimi input grubu - Kompakt versiyon"""
        # Label
        label = tk.Label(
            parent,
            text=f"{icon} {label_text}",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        label.pack(anchor=tk.W, pady=(0, 3))  # Padding'i daha da azalttım
        
        # Input ve buton frame
        input_frame = tk.Frame(parent, bg=self.colors['card'])
        input_frame.pack(fill=tk.X)
        
        # Entry
        entry = ttk.Entry(
            input_frame,
            textvariable=text_var,
            font=('Segoe UI', 9),
            style='Modern.TEntry',
            width=30  # Daha da küçük
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Gözat butonu
        browse_btn = ttk.Button(
            input_frame,
            text="Gözat",
            command=browse_command,
            style='Secondary.TButton'
        )
        browse_btn.pack(side=tk.RIGHT, padx=(8, 0))  # Padding'i azalttım
        
    def create_options_card(self, parent):
        """Seçenekler kartı"""
        card_frame = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        card_frame.pack(fill=tk.X, pady=5)
        
        # Kart başlığı
        header = tk.Label(
            card_frame,
            text="⚙️ Seçenekler",
            font=('Segoe UI', 10, 'bold'),  # Daha küçük font
            bg=self.colors['card'],
            fg=self.colors['text'],
            pady=8  # Daha az padding
        )
        header.pack(anchor=tk.W, padx=20)
        
        # Seçenekler içeriği
        content_frame = tk.Frame(card_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.X, padx=12, pady=(0, 12))  # Daha minimal padding
        
        # Büyük/küçük harf seçeneği
        case_check = ttk.Checkbutton(
            content_frame,
            text="Büyük/Küçük Harf Duyarlı Karşılaştırma",
            variable=self.app_logic.case_sensitive,
            style='Modern.TCheckbutton'
        )
        case_check.pack(anchor=tk.W, pady=5)
        
        # Kaydetme formatı
        tk.Label(
            content_frame,
            text="💾 Kaydetme Formatı:",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(15, 5))
        
        # Format seçenekleri - Checkbox'lar
        format_frame = tk.Frame(content_frame, bg=self.colors['card'])
        format_frame.pack(anchor=tk.W, padx=10)
        
        # Excel checkbox
        self.save_excel = tk.BooleanVar(value=True)  # Varsayılan olarak seçili
        ttk.Checkbutton(
            format_frame,
            text="Excel (.xlsx)",
            variable=self.save_excel,
            style='Modern.TCheckbutton'
        ).pack(anchor=tk.W, pady=2)
        
        # Resim checkbox
        self.save_image = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            format_frame,
            text="Resim (.png)",
            variable=self.save_image,
            style='Modern.TCheckbutton'
        ).pack(anchor=tk.W, pady=2)
        
    def create_action_buttons(self, parent):
        """İşlem butonları"""
        button_frame = tk.Frame(parent, bg=self.colors['background'])
        button_frame.pack(fill=tk.X, pady=10)
        
        # Karşılaştır butonu (Ana buton)
        compare_btn = ttk.Button(
            button_frame,
            text="🔍 Karşılaştır",
            command=self.app_logic.compare_files,
            style='Accent.TButton'
        )
        compare_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Temizle butonu
        clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Temizle",
            command=self.app_logic.clear_results,
            style='Secondary.TButton'
        )
        clear_btn.pack(fill=tk.X)
        
    def create_right_panel(self, parent):
        """Sağ panel (Sonuçlar)"""
        # Sonuçlar kartı
        card_frame = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        card_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Kart başlığı
        header_frame = tk.Frame(card_frame, bg=self.colors['card'])
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(
            header_frame,
            text="📊 Sonuçlar",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        # Sonuç tablosu frame
        table_frame = tk.Frame(card_frame, bg=self.colors['card'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Treeview ve scrollbar
        tree_frame = tk.Frame(table_frame, bg=self.colors['card'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("no", "unvan")
        self.result_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=15
        )
        
        # Başlıkları ayarla
        self.result_tree.heading("no", text="#")
        self.result_tree.heading("unvan", text="Cari Ünvan")
        
        # Sütun genişlikleri
        self.result_tree.column("no", width=50, anchor=tk.CENTER)
        self.result_tree.column("unvan", width=400)
        
        self.result_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_tree.yview)
        
        # Durum bilgisi
        status_frame = tk.Frame(card_frame, bg=self.colors['card'])
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        self.status_var = tk.StringVar(value="Henüz karşılaştırma yapılmadı.")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 10, 'italic'),
            bg=self.colors['card'],
            fg=self.colors['text_light'],
            wraplength=400
        )
        status_label.pack(anchor=tk.W)
        
    def browse_file1(self):
        """Eski Excel dosyasını seç"""
        file_path = filedialog.askopenfilename(
            title="Eski Tarihli Excel Dosyasını Seç",
            filetypes=[("Excel Dosyaları", "*.xlsx *.xls"), ("Tüm Dosyalar", "*.*")]
        )
        if file_path:
            self.app_logic.file1_path.set(file_path)
            self.app_logic.update_output_filename(file_path)
            
    def browse_file2(self):
        """Yeni Excel dosyasını seç"""
        file_path = filedialog.askopenfilename(
            title="Yeni Tarihli Excel Dosyasını Seç",
            filetypes=[("Excel Dosyaları", "*.xlsx *.xls"), ("Tüm Dosyalar", "*.*")]
        )
        if file_path:
            self.app_logic.file2_path.set(file_path)
            
    def browse_output(self):
        """Sonuç dosyasını kaydet"""
        # Hangi formatların seçili olduğunu kontrol et
        excel_selected = self.save_excel.get()
        image_selected = self.save_image.get()
        
        if excel_selected and image_selected:
            # Her iki format da seçili
            filetypes = [("Tüm Dosyalar", "*.*")]
            defaultextension = ""
        elif excel_selected:
            # Sadece Excel
            filetypes = [("Excel Dosyaları", "*.xlsx"), ("Tüm Dosyalar", "*.*")]
            defaultextension = ".xlsx"
        elif image_selected:
            # Sadece Resim
            filetypes = [("PNG Dosyaları", "*.png"), ("Tüm Dosyalar", "*.*")]
            defaultextension = ".png"
        else:
            # Hiçbiri seçili değil
            filetypes = [("Tüm Dosyalar", "*.*")]
            defaultextension = ""
            
        file_path = filedialog.asksaveasfilename(
            title="Sonuç Dosyasını Kaydet",
            defaultextension=defaultextension,
            filetypes=filetypes
        )
        if file_path:
            base_name = os.path.splitext(file_path)[0] 
            self.app_logic.output_path.set(base_name)
            
    def update_results(self, results, status_text):
        """Sonuçları güncelle"""
        # Mevcut sonuçları temizle
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
            
        # Yeni sonuçları ekle
        for i, unvan in enumerate(results, 1):
            self.result_tree.insert("", tk.END, values=(i, unvan))
            
        # Durum metnini güncelle
        self.status_var.set(status_text)
        
    def clear_results(self):
        """Sonuçları temizle"""
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.status_var.set("Henüz karşılaştırma yapılmadı.")
        
    def show_info(self, title, message):
        """Bilgi mesajı göster"""
        messagebox.showinfo(title, message)
        
    def show_error(self, title, message):
        """Hata mesajı göster"""
        messagebox.showerror(title, message)
        
    def show_warning(self, title, message):
        """Uyarı mesajı göster"""
        messagebox.showwarning(title, message)