import sys
import os
import pdfkit
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                            QFileDialog, QProgressBar, QMessageBox, QVBoxLayout, 
                            QHBoxLayout, QWidget, QLineEdit, QSpinBox, QFormLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDir


class ConversionWorker(QThread):
    """PDF dönüştürme işlemlerini arka planda yapan iş parçacığı"""
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int, int)
    
    def __init__(self, input_folder, output_folder, wkhtmltopdf_path, margin=5):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.wkhtmltopdf_path = wkhtmltopdf_path
        self.margin = margin
        self.is_running = True
        
    def run(self):
        # wkhtmltopdf kurulu mu kontrol et
        if not os.path.exists(self.wkhtmltopdf_path):
            self.status_signal.emit(f"HATA: wkhtmltopdf bulunamadı: {self.wkhtmltopdf_path}")
            return
        
        # PDF oluşturma ayarları
        config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
        options = {
            'page-size': 'A4',                   # Sayfa boyutu A4
            'margin-top': f'{self.margin}mm',    # Üst kenar boşluğu
            'margin-right': f'{self.margin}mm',  # Sağ kenar boşluğu
            'margin-bottom': f'{self.margin}mm', # Alt kenar boşluğu
            'margin-left': f'{self.margin}mm',   # Sol kenar boşluğu
            'no-header-line': None,              # Üst bilgi yok
            'no-footer-line': None,              # Alt bilgi yok
            'orientation': 'Portrait',           # Dikey mod (portrait)
            'zoom': '1',                         # İçeriği sayfaya sığdırma
            'quiet': ''                          # Sessiz mod
        }
        
        # Çıkış klasörünü oluştur
        if not os.path.exists(self.output_folder):
            try:
                os.makedirs(self.output_folder)
                self.status_signal.emit(f"Çıkış klasörü oluşturuldu: {self.output_folder}")
            except Exception as e:
                self.status_signal.emit(f"Klasör oluşturulamadı: {str(e)}")
                return
        
        # Klasördeki tüm HTM/HTML dosyalarını al
        html_files = [f for f in os.listdir(self.input_folder) 
                     if f.lower().endswith(('.htm', '.html'))]
        
        if not html_files:
            self.status_signal.emit(f"UYARI: {self.input_folder} klasöründe HTML veya HTM dosyası bulunamadı.")
            return
        
        total_files = len(html_files)
        self.status_signal.emit(f"Toplam {total_files} dosya işlenecek...")
        
        success_count = 0
        error_count = 0
        
        # Dosyaları işle
        for i, file_name in enumerate(html_files):
            if not self.is_running:
                self.status_signal.emit("İşlem iptal edildi.")
                break
                
            input_path = os.path.join(self.input_folder, file_name)
            output_path = os.path.join(self.output_folder, f"{os.path.splitext(file_name)[0]}.pdf")
            
            self.status_signal.emit(f"İşleniyor: {file_name} ({i+1}/{total_files})")
            try:
                # PDF'e dönüştürme
                pdfkit.from_file(input_path, output_path, configuration=config, options=options)
                success_count += 1
            except Exception as e:
                error_count += 1
                self.status_signal.emit(f"HATA: {file_name} - {str(e)}")
            
            # İlerlemeyi güncelle
            progress_percent = int(((i + 1) / total_files) * 100)
            self.progress_signal.emit(progress_percent)
        
        # Özet raporu
        self.finished_signal.emit(success_count, error_count)
    
    def stop(self):
        self.is_running = False


class HTMLtoPDFConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.worker = None
        
        # wkhtmltopdf'nin muhtemel kurulum dizinleri
        self.wkhtmltopdf_paths = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe"
        ]
        self.find_wkhtmltopdf()
        
    def find_wkhtmltopdf(self):
        """wkhtmltopdf'yi otomatik olarak bulmaya çalışır"""
        for path in self.wkhtmltopdf_paths:
            if os.path.exists(path):
                self.wkhtmltopdf_edit.setText(path)
                return
                
    def init_ui(self):
        """Kullanıcı arayüzünü oluşturur"""
        self.setWindowTitle("HTML'den PDF'e Dönüştürücü")
        self.setMinimumSize(600, 400)
        
        # Ana layout
        main_layout = QVBoxLayout()
        
        # Form layout - Giriş ve çıkış dizinleri
        form_layout = QFormLayout()
        
        # Giriş klasörü
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("HTML/HTM dosyalarının bulunduğu klasör...")
        self.input_button = QPushButton("Klasör Seç")
        self.input_button.clicked.connect(self.select_input_folder)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.input_button)
        form_layout.addRow("Giriş Klasörü:", input_layout)
        
        # Çıkış klasörü
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("PDF dosyalarının kaydedileceği klasör...")
        self.output_button = QPushButton("Klasör Seç")
        self.output_button.clicked.connect(self.select_output_folder)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(self.output_button)
        form_layout.addRow("Çıkış Klasörü:", output_layout)
        
        # wkhtmltopdf yolu
        wkhtmltopdf_layout = QHBoxLayout()
        self.wkhtmltopdf_edit = QLineEdit()
        self.wkhtmltopdf_edit.setPlaceholderText("wkhtmltopdf.exe dosyasının yolu...")
        self.wkhtmltopdf_button = QPushButton("Dosya Seç")
        self.wkhtmltopdf_button.clicked.connect(self.select_wkhtmltopdf)
        wkhtmltopdf_layout.addWidget(self.wkhtmltopdf_edit)
        wkhtmltopdf_layout.addWidget(self.wkhtmltopdf_button)
        form_layout.addRow("wkhtmltopdf Yolu:", wkhtmltopdf_layout)
        
        # Kenar boşluğu ayarı
        margin_layout = QHBoxLayout()
        self.margin_spinner = QSpinBox()
        self.margin_spinner.setRange(0, 50)
        self.margin_spinner.setValue(5)  # Varsayılan 5mm
        self.margin_spinner.setSuffix(" mm")
        margin_layout.addWidget(self.margin_spinner)
        margin_layout.addStretch()
        form_layout.addRow("Kenar Boşluğu:", margin_layout)
        
        main_layout.addLayout(form_layout)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Durum etiketi
        self.status_label = QLabel("Hazır")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # İşlem düğmeleri
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Dönüştürmeyi Başlat")
        self.start_button.clicked.connect(self.start_conversion)
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        self.cancel_button = QPushButton("İptal Et")
        self.cancel_button.clicked.connect(self.cancel_conversion)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)
        
        # Ana widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
    def select_input_folder(self):
        """Giriş klasörünü seçme işlemi"""
        folder = QFileDialog.getExistingDirectory(self, "HTML/HTM Dosyalarının Bulunduğu Klasörü Seç")
        if folder:
            self.input_edit.setText(folder)
            
            # Eğer çıkış klasörü boşsa, otomatik olarak "tasar" alt klasörünü öner
            if not self.output_edit.text():
                self.output_edit.setText(os.path.join(folder, "tasar"))
    
    def select_output_folder(self):
        """Çıkış klasörünü seçme işlemi"""
        folder = QFileDialog.getExistingDirectory(self, "PDF Dosyalarının Kaydedileceği Klasörü Seç")
        if folder:
            self.output_edit.setText(folder)
    
    def select_wkhtmltopdf(self):
        """wkhtmltopdf yolunu seçme işlemi"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "wkhtmltopdf.exe Dosyasını Seç", 
            filter="Executable (*.exe)"
        )
        if file_path:
            self.wkhtmltopdf_edit.setText(file_path)
    
    def start_conversion(self):
        """PDF dönüştürme işlemini başlatır"""
        input_folder = self.input_edit.text()
        output_folder = self.output_edit.text()
        wkhtmltopdf_path = self.wkhtmltopdf_edit.text()
        margin = self.margin_spinner.value()
        
        # Gerekli alanları kontrol et
        if not input_folder:
            QMessageBox.warning(self, "Uyarı", "Lütfen giriş klasörünü seçin!")
            return
        
        if not output_folder:
            QMessageBox.warning(self, "Uyarı", "Lütfen çıkış klasörünü seçin!")
            return
        
        if not wkhtmltopdf_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen wkhtmltopdf.exe dosyasının yolunu belirtin!")
            return
        
        if not os.path.exists(wkhtmltopdf_path):
            QMessageBox.critical(self, "Hata", f"wkhtmltopdf bulunamadı: {wkhtmltopdf_path}")
            return
        
        # UI durumunu güncelle
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Başlatılıyor...")
        
        # İş parçacığını başlat
        self.worker = ConversionWorker(input_folder, output_folder, wkhtmltopdf_path, margin)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.status_signal.connect(self.update_status)
        self.worker.finished_signal.connect(self.conversion_finished)
        self.worker.finished.connect(self.worker_done)
        self.worker.start()
    
    def cancel_conversion(self):
        """Dönüştürme işlemini iptal eder"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.status_label.setText("İptal ediliyor...")
    
    def update_progress(self, value):
        """İlerleme çubuğunu günceller"""
        self.progress_bar.setValue(value)
    
    def update_status(self, message):
        """Durum etiketini günceller"""
        self.status_label.setText(message)
    
    def conversion_finished(self, success_count, error_count):
        """Dönüştürme işlemi tamamlandığında çağrılır"""
        total = success_count + error_count
        msg = f"Tamamlandı! {success_count}/{total} dosya başarıyla dönüştürüldü."
        
        if error_count > 0:
            msg += f" {error_count} dosyada hata oluştu."
            
        self.status_label.setText(msg)
        
        QMessageBox.information(self, "İşlem Tamamlandı", 
            f"HTML'den PDF'e dönüştürme işlemi tamamlandı.\n\n"
            f"Toplam dosya: {total}\n"
            f"Başarılı: {success_count}\n"
            f"Başarısız: {error_count}\n\n"
            f"PDF dosyaları şurada: {self.output_edit.text()}"
        )
    
    def worker_done(self):
        """İş parçacığı tamamlandığında UI'yı sıfırlar"""
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern görünüm için
    window = HTMLtoPDFConverter()
    window.show()
    sys.exit(app.exec_())
