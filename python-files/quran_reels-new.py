import sys
import os
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QLabel, QProgressBar, QMessageBox, QLineEdit,
                             QComboBox, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDir
from PyQt5.QtGui import QIcon, QFont

# الثوابت للوصول إلى API القرآن
QURAN_CHAPTERS_URL = "https://api.quran.com/api/v4/chapters"
QURAN_RECITATIONS_URL = "https://api.quran.com/api/v4/chapter_recitations"

# القارئين المتاحين (يمكن توسيعها لاحقاً)
RECITERS = {
    "عبد الباسط عبد الصمد": 1,
    "محمود خليل الحصري": 2,
    "محمد صديق المنشاوي": 3,
    "مشاري راشد العفاسي": 7,
    "أبو بكر الشاطري": 10
}


class DownloadThread(QThread):
    """فئة منفصلة لتحميل الملفات في خلفية البرنامج"""
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, surah_id, output_path, reciter_id=7):
        super().__init__()
        self.surah_id = surah_id
        self.output_path = output_path
        self.reciter_id = reciter_id

    def run(self):
        try:
            # الحصول على رابط التلاوة للسورة المحددة
            recitation_url = f"{QURAN_RECITATIONS_URL}/{self.reciter_id}/by_chapter/{self.surah_id}"
            response = requests.get(recitation_url)
            response.raise_for_status()

            data = response.json()

            # التحقق من وجود البيانات المطلوبة
            if 'audio_files' in data:
                # نأخذ الرابط المتاح للتلاوة
                audio_url = data['audio_files'][0]['audio_url']
            else:
                self.finished_signal.emit(False, "لم يتم العثور على رابط الصوت في البيانات")
                return

            # تنزيل الملف الصوتي مع إظهار التقدم
            response = requests.get(audio_url, stream=True)
            response.raise_for_status()

            # حجم الملف الكلي
            total_size = int(response.headers.get('content-length', 0))

            if total_size == 0:
                self.finished_signal.emit(False, "حجم الملف غير معروف")
                return

            # كتابة البيانات في الملف مع تحديث التقدم
            downloaded = 0
            with open(self.output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # تحديث شريط التقدم
                        progress = int(100 * downloaded / total_size)
                        self.progress_signal.emit(progress)

            self.finished_signal.emit(True, "تم تحميل السورة بنجاح")

        except Exception as e:
            self.finished_signal.emit(False, f"حدث خطأ أثناء تحميل السورة: {str(e)}")


class QuranDownloaderApp(QMainWindow):
    """التطبيق الرئيسي لتحميل السور القرآنية"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("برنامج تحميل سور القرآن الكريم")
        self.setMinimumSize(800, 600)

        # تهيئة واجهة المستخدم
        self.init_ui()

        # تحميل قائمة السور
        self.load_surahs()

    def init_ui(self):
        """إنشاء عناصر واجهة المستخدم"""
        # الخط العربي
        arabic_font = QFont("Arial", 12)

        # القسم الرئيسي
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)

        # العنوان
        title_label = QLabel("🕌 برنامج تحميل سور القرآن الكريم")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # قسم البحث
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث عن سورة...")
        self.search_input.setFont(arabic_font)
        self.search_input.textChanged.connect(self.filter_surahs)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # قائمة السور
        list_label = QLabel("قائمة السور:")
        list_label.setFont(arabic_font)
        main_layout.addWidget(list_label)

        self.surah_list = QListWidget()
        self.surah_list.setFont(arabic_font)
        self.surah_list.setMinimumHeight(300)
        main_layout.addWidget(self.surah_list)

        # اختيار القارئ
        reciter_layout = QHBoxLayout()
        reciter_label = QLabel("اختر القارئ:")
        reciter_label.setFont(arabic_font)
        reciter_layout.addWidget(reciter_label)

        self.reciter_combo = QComboBox()
        self.reciter_combo.setFont(arabic_font)
        for reciter in RECITERS.keys():
            self.reciter_combo.addItem(reciter)
        reciter_layout.addWidget(self.reciter_combo)
        main_layout.addLayout(reciter_layout)

        # مسار الحفظ
        path_layout = QHBoxLayout()
        path_label = QLabel("مسار الحفظ:")
        path_label.setFont(arabic_font)
        path_layout.addWidget(path_label)

        self.path_input = QLineEdit("downloads")
        self.path_input.setFont(arabic_font)
        path_layout.addWidget(self.path_input)

        browse_button = QPushButton("تصفح...")
        browse_button.setFont(arabic_font)
        browse_button.clicked.connect(self.browse_folder)
        path_layout.addWidget(browse_button)
        main_layout.addLayout(path_layout)

        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # زر التحميل
        self.download_button = QPushButton("تحميل السورة")
        self.download_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.download_button.setMinimumHeight(50)
        self.download_button.clicked.connect(self.start_download)
        main_layout.addWidget(self.download_button)

        # معلومات التطبيق
        info_label = QLabel("تم تطويره بواسطة Claude & PyQt5")
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)

        # البيانات المؤقتة
        self.surahs = []
        self.download_thread = None

    def load_surahs(self):
        """تحميل قائمة السور من API"""
        try:
            self.surah_list.clear()
            self.download_button.setEnabled(False)
            self.surah_list.addItem("جاري تحميل قائمة السور...")

            # استخدام requests للحصول على بيانات السور
            response = requests.get(QURAN_CHAPTERS_URL)
            response.raise_for_status()

            chapters = response.json().get('chapters', [])
            if not chapters:
                self.surah_list.clear()
                self.surah_list.addItem("لم يتم العثور على سور")
                return

            # حفظ البيانات وعرضها في القائمة
            self.surahs = [(chapter['id'], f"{chapter['id']}. {chapter['name_arabic']} - {chapter['name_simple']}")
                           for chapter in chapters]

            self.surah_list.clear()
            for _, surah_text in self.surahs:
                self.surah_list.addItem(surah_text)

            self.download_button.setEnabled(True)

        except Exception as e:
            self.surah_list.clear()
            self.surah_list.addItem(f"حدث خطأ: {str(e)}")

    def filter_surahs(self, text):
        """تصفية السور حسب النص المدخل"""
        self.surah_list.clear()
        search_text = text.lower()

        for _, surah_text in self.surahs:
            if search_text in surah_text.lower():
                self.surah_list.addItem(surah_text)

    def browse_folder(self):
        """اختيار مجلد لحفظ الملفات"""
        folder = QFileDialog.getExistingDirectory(self, "اختر مجلد الحفظ",
                                                  QDir.homePath())
        if folder:
            self.path_input.setText(folder)

    def start_download(self):
        """بدء عملية تحميل السورة"""
        # التحقق من اختيار سورة
        current_item = self.surah_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار سورة أولاً")
            return

        # الحصول على بيانات السورة المختارة
        surah_text = current_item.text()
        surah_id = surah_text.split('.')[0]

        # استخراج اسم السورة العربي
        surah_name = surah_text.split('.')[1].split('-')[0].strip()

        # الحصول على معرف القارئ المختار
        reciter_name = self.reciter_combo.currentText()
        reciter_id = RECITERS[reciter_name]

        # التحقق من مسار الحفظ
        output_dir = self.path_input.text()
        if not output_dir:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد مسار الحفظ")
            return

        # إنشاء المجلد إذا لم يكن موجوداً
        os.makedirs(output_dir, exist_ok=True)

        # تحديد اسم ملف الصوت
        audio_output = os.path.join(output_dir, f"{surah_name} - {reciter_name}.mp3")

        # تعطيل عناصر الواجهة أثناء التحميل
        self.download_button.setEnabled(False)
        self.surah_list.setEnabled(False)
        self.reciter_combo.setEnabled(False)
        self.search_input.setEnabled(False)

        # إظهار وتصفير شريط التقدم
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # بدء عملية التحميل في خلفية البرنامج
        self.download_thread = DownloadThread(surah_id, audio_output, reciter_id)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.start()

    def update_progress(self, value):
        """تحديث قيمة شريط التقدم"""
        self.progress_bar.setValue(value)

    def download_finished(self, success, message):
        """معالجة انتهاء التحميل"""
        # إعادة تفعيل عناصر الواجهة
        self.download_button.setEnabled(True)
        self.surah_list.setEnabled(True)
        self.reciter_combo.setEnabled(True)
        self.search_input.setEnabled(True)

        # إظهار رسالة بنتيجة التحميل
        if success:
            QMessageBox.information(self, "نجاح", message)
        else:
            QMessageBox.critical(self, "خطأ", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # تعيين RTL للدعم العربي
    app.setLayoutDirection(Qt.RightToLeft)

    # تشغيل التطبيق
    window = QuranDownloaderApp()
    window.show()

    sys.exit(app.exec_())