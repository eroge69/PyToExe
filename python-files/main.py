import sys
from PyQt5 import QtWidgets
import mammoth
from pathlib import Path
from docx2pdf import convert
import img2pdf
from PIL import Image
from tkinter import filedialog
from untitled import Ui_MainWindow
#Основные настройки
class untitled(QtWidgets.QMainWindow):
    def __init__(self):
        super(untitled, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.W_PDF)
        self.ui.pushButton_2.clicked.connect(self.j_PDF)
        self.ui.pushButton_3.clicked.connect(self.W_HTML)
    def W_PDF(self):
        fil = filedialog.askopenfilename(title ="Открыть файл", filetypes=[("Выбрать файл для преоброзования Из WORD в PDF", "*.docx"), ("Все файлы", "*.*")])
        convert(fil, 'WORD_PDF')
    def j_PDF(self):
        img_path = filedialog.askopenfilename(title ="Открыть файл", filetypes=[("Выбрать файл для преоброзования Из jpg в PDF", "*.jpg"), ("Все файлы", "*.*")])
        rash = (Path(img_path).stem)
        pdf_path = "JPG_PDF/" + rash  + ".PDF"
        image = Image.open(img_path)
        pdf_bytes = img2pdf.convert(image.filename)
        file = open(pdf_path, "wb")
        file.write(pdf_bytes)
        image.close()
        file.close()
    def W_HTML(self):
        f = filedialog.askopenfilename(title ="Открыть файл", filetypes=[("Выбрать файл для преоброзования Из WORD в PDF", "*.docx"), ("Все файлы", "*.*")])
        rash1 = (Path(f).stem)
        b = open('WORD_HTML/' + rash1 + '.html', 'wb')
        document = mammoth.convert_to_html(f)
        b.write(document.value.encode('utf8'))
        b.close()
# ******************************Конец программы запуск рамка ограничений************************************
def create_app():
    app = QtWidgets.QApplication(sys.argv)
    win = untitled()
    win.show()
    win.setFixedWidth(440) # *********Ширина******************
    win.setFixedHeight(90) # *********Высота******************
    sys.exit(app.exec_())
create_app()
