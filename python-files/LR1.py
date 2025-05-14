import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QFont

en_small = 'abcdefghijklmnopqrstuvwxyz'
en_big = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
rus_small = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
rus_big = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

def Encryption(mes):
    crypted_mes = ''
    for i in range (len(mes)):
        if en_small.find(mes[i]) != -1:
            crypted_mes += en_small[26 - en_small.find(mes[i]) - 1]
        elif en_big.find(mes[i]) != -1:
            crypted_mes += en_big[26 - en_big.find(mes[i]) - 1]
        elif rus_small.find(mes[i]) != -1:
            crypted_mes += rus_small[33 - rus_small.find(mes[i]) - 1]
        elif rus_big.find(mes[i]) != -1:
            crypted_mes += rus_big[33 - rus_big.find(mes[i]) - 1]
        else:
            crypted_mes += mes[i]
    return crypted_mes


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.setFont(QFont('Arial', 14))

        self.Label1 = QLabel(self) 
        self.Label1.setText( 'Введите сообщение:' )
        self.Label1.move(50 , 50)
        
        self.Label2 = QLabel(self) 
        self.Label2.setText( 'Результат:' )
        self.Label2.move(50, 210)

        self.le1 = QTextEdit(self)
        self.le1.move(50, 85)
        self.le1.resize(480, 55)

        self.le2 = QTextBrowser(self)
        self.le2.move(50, 245)
        self.le2.resize(480, 55)         

        self.btn1 = QPushButton('Шифрование', self)
        self.btn1.move(150, 170)
        self.btn1.clicked.connect(self.Encryption)
        
        self.btn2 = QPushButton('↓↑', self)
        self.btn2.move(300, 170)
        self.btn2.resize(30,30)
        self.btn2.clicked.connect(self.exchange)
        
        self.btn3 = QPushButton('Сброс', self)
        self.btn3.move(355, 170)
        self.btn3.clicked.connect(self.clear)

        self.setWindowTitle('Шифр Атбаш')
        self.setFixedSize(580, 380)

    def Encryption(self):
        text = self.le1.toPlainText()
        text = Encryption(text)
        self.le2.setText(text)

    def exchange(self):
        tmp = self.le1.toPlainText()
        self.le1.setText(self.le2.toPlainText())
        self.le2.setText(tmp)
        
    def clear(self):
        self.le1.setText('')
        self.le2.setText('')

app = QApplication([])
window = Window()
window.show()
sys.exit(app.exec())
