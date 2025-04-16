# import sys
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
#                              QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
#                              QHeaderView, QMessageBox, QDateEdit, QCalendarWidget, QDialog,
#                              QTabWidget, QComboBox, QInputDialog)
# from PyQt5.QtCore import QDate, Qt
# import sqlite3
# import locale

# # Set locale for number formatting
# locale.setlocale(locale.LC_ALL, '')

# class CalendarDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Sana tanlang")
#         self.setModal(True)
        
#         self.calendar = QCalendarWidget(self)
#         self.calendar.setGridVisible(True)
        
#         self.ok_button = QPushButton("OK", self)
#         self.ok_button.clicked.connect(self.accept)
        
#         layout = QVBoxLayout()
#         layout.addWidget(self.calendar)
#         layout.addWidget(self.ok_button)
#         self.setLayout(layout)
    
#     def selected_date(self):
#         return self.calendar.selectedDate()

# class DatabaseManager:
#     def __init__(self, db_name='yuklar.db'):
#         self.conn = sqlite3.connect(db_name)
#         self.cursor = self.conn.cursor()
#         self.create_tables()
#         self.migrate_tables()
#         self.init_yuk_nomlari()

#     def create_tables(self):
#         # Yuklar jadvali
#         self.cursor.execute('''
#             CREATE TABLE IF NOT EXISTS yuklar (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 sana TEXT NOT NULL,
#                 yuk_nomi TEXT NOT NULL,
#                 miqdori REAL NOT NULL,
#                 narxi REAL NOT NULL,
#                 umumiy_narxi REAL NOT NULL
#             )
#         ''')
        
#         # Yuk nomlari jadvali
#         self.cursor.execute('''
#             CREATE TABLE IF NOT EXISTS yuk_nomlari (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 nom TEXT NOT NULL UNIQUE
#             )
#         ''')
        
#         # Balans jadvali
#         self.cursor.execute('''
#             CREATE TABLE IF NOT EXISTS balance (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 sana TEXT NOT NULL UNIQUE,
#                 kirim REAL DEFAULT 0,
#                 qo_lda_kirim REAL DEFAULT 0,
#                 chiqim REAL DEFAULT 0,
#                 qoldiq REAL DEFAULT 0
#             )
#         ''')
        
#         self.conn.commit()

#     def migrate_tables(self):
#         # Agar qo'lda_kirim ustuni yo'q bo'lsa, qo'shamiz
#         self.cursor.execute("PRAGMA table_info(balance)")
#         columns = [column[1] for column in self.cursor.fetchall()]
        
#         if 'qo_lda_kirim' not in columns:
#             self.cursor.execute('ALTER TABLE balance ADD COLUMN qo_lda_kirim REAL DEFAULT 0')
#             self.conn.commit()

#     def init_yuk_nomlari(self):
#         default_nomlar = ['Paxta', 'Guruch', 'Bugdoy', "Kartoshka"]
#         for nom in default_nomlar:
#             try:
#                 self.cursor.execute('INSERT INTO yuk_nomlari (nom) VALUES (?)', (nom,))
#             except sqlite3.IntegrityError:
#                 pass
#         self.conn.commit()

#     def add_yuk_nomi(self, nom):
#         try:
#             self.cursor.execute('INSERT INTO yuk_nomlari (nom) VALUES (?)', (nom,))
#             self.conn.commit()
#             return True
#         except sqlite3.IntegrityError:
#             return False

#     def get_yuk_nomlari(self):
#         self.cursor.execute('SELECT nom FROM yuk_nomlari ORDER BY nom')
#         return [row[0] for row in self.cursor.fetchall()]

#     def add_yuk(self, sana, yuk_nomi, miqdori, narxi, umumiy_narxi):
#         self.cursor.execute('''
#             INSERT INTO yuklar (sana, yuk_nomi, miqdori, narxi, umumiy_narxi)
#             VALUES (?, ?, ?, ?, ?)
#         ''', (sana, yuk_nomi, miqdori, narxi, umumiy_narxi))
        
#         # Balans jadvalini yangilaymiz
#         self.cursor.execute('''
#             INSERT OR IGNORE INTO balance (sana, kirim, qo_lda_kirim, chiqim, qoldiq)
#             VALUES (?, 0, 0, 0, 0)
#         ''', (sana,))
        
#         # Avtomatik kirim va qoldiqni hisoblaymiz
#         self.cursor.execute('''
#             UPDATE balance 
#             SET kirim = (SELECT COALESCE(SUM(umumiy_narxi), 0) FROM yuklar WHERE sana = ?),
#                 qoldiq = kirim + qo_lda_kirim - chiqim
#             WHERE sana = ?
#         ''', (sana, sana))
        
#         self.conn.commit()

#     def get_all_yuklar(self):
#         self.cursor.execute('SELECT * FROM yuklar ORDER BY sana DESC')
#         return self.cursor.fetchall()

#     def delete_yuk(self, yuk_id):
#         # Yuk sanasini olamiz
#         self.cursor.execute('SELECT sana FROM yuklar WHERE id=?', (yuk_id,))
#         sana = self.cursor.fetchone()[0]
        
#         # Yukni o'chiramiz
#         self.cursor.execute('DELETE FROM yuklar WHERE id=?', (yuk_id,))
        
#         # Balansni yangilaymiz
#         self.cursor.execute('''
#             UPDATE balance 
#             SET kirim = (SELECT COALESCE(SUM(umumiy_narxi), 0) FROM yuklar WHERE sana = ?),
#                 qoldiq = kirim + qo_lda_kirim - chiqim
#             WHERE sana = ?
#         ''', (sana, sana))
        
#         self.conn.commit()

#     def get_balance_data(self):
#         self.cursor.execute('''
#             SELECT id, sana, kirim, qo_lda_kirim, 
#                    (kirim + qo_lda_kirim) as jami_kirim,
#                    chiqim, 
#                    (kirim + qo_lda_kirim - chiqim) as qoldiq,
#                    (SELECT SUM(kirim) FROM balance) as umumiy_kirim,
#                    (SELECT SUM(qo_lda_kirim) FROM balance) as umumiy_qo_lda_kirim,
#                    (SELECT SUM(chiqim) FROM balance) as umumiy_chiqim,
#                    (SELECT SUM(kirim + qo_lda_kirim - chiqim) FROM balance) as umumiy_qoldiq
#             FROM balance
#             ORDER BY sana DESC
#         ''')
#         return self.cursor.fetchall()

#     def update_manual_income(self, sana, amount):
#         self.cursor.execute('''
#             INSERT OR IGNORE INTO balance (sana, kirim, qo_lda_kirim, chiqim, qoldiq)
#             VALUES (?, 0, 0, 0, 0)
#         ''', (sana,))
        
#         self.cursor.execute('''
#             UPDATE balance 
#             SET qo_lda_kirim = ?,
#                 qoldiq = kirim + ? - chiqim
#             WHERE sana = ?
#         ''', (amount, amount, sana))
        
#         self.conn.commit()

#     def update_expense(self, sana, amount):
#         self.cursor.execute('''
#             INSERT OR IGNORE INTO balance (sana, kirim, qo_lda_kirim, chiqim, qoldiq)
#             VALUES (?, 0, 0, 0, 0)
#         ''', (sana,))
        
#         self.cursor.execute('''
#             UPDATE balance 
#             SET chiqim = ?,
#                 qoldiq = kirim + qo_lda_kirim - ?
#             WHERE sana = ?
#         ''', (amount, amount, sana))
        
#         self.conn.commit()

#     def __del__(self):
#         self.conn.close()

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.db = DatabaseManager()
#         self.setWindowTitle("Yuklar va Balans Boshqaruvi")
#         self.setGeometry(100, 100, 1300, 800)

#         # Tab widget yaratamiz
#         self.tabs = QTabWidget()
#         self.setCentralWidget(self.tabs)

#         # Yuklar tab
#         self.yuklar_tab = QWidget()
#         self.tabs.addTab(self.yuklar_tab, "Yuklar")
#         self.setup_yuklar_tab()

#         # Balans tab
#         self.balance_tab = QWidget()
#         self.tabs.addTab(self.balance_tab, "Kirim-Chiqim Balansi")
#         self.setup_balance_tab()

#     def setup_yuklar_tab(self):
#         layout = QVBoxLayout()
#         self.yuklar_tab.setLayout(layout)

#         # Forma qismi
#         form_layout = QHBoxLayout()
#         layout.addLayout(form_layout)

#         # Sana
#         form_layout.addWidget(QLabel("Sana:"))
#         self.sana_input = QDateEdit()
#         self.sana_input.setDate(QDate.currentDate())
#         self.sana_input.setCalendarPopup(True)
#         self.sana_input.setDisplayFormat("yyyy-MM-dd")
#         form_layout.addWidget(self.sana_input)

#         # Yuk nomi (ComboBox)
#         form_layout.addWidget(QLabel("Yuk Nomi:"))
#         self.yuk_nomi_combo = QComboBox()
#         self.yuk_nomi_combo.setEditable(True)
#         self.yuk_nomi_combo.lineEdit().setPlaceholderText("Yuk nomini tanlang yoki kiriting")
#         self.load_yuk_nomlari()
#         form_layout.addWidget(self.yuk_nomi_combo)

#         # Yuk nomi qo'shish tugmasi
#         self.add_yuk_nomi_btn = QPushButton("+")
#         self.add_yuk_nomi_btn.setFixedWidth(30)
#         self.add_yuk_nomi_btn.setToolTip("Yangi yuk turini qo'shish")
#         self.add_yuk_nomi_btn.clicked.connect(self.add_new_yuk_nomi)
#         form_layout.addWidget(self.add_yuk_nomi_btn)

#         # Miqdori
#         form_layout.addWidget(QLabel("Miqdori:"))
#         self.miqdori_input = QLineEdit()
#         self.miqdori_input.textChanged.connect(self.calculate_total)
#         form_layout.addWidget(self.miqdori_input)

#         # Narxi
#         form_layout.addWidget(QLabel("Narxi:"))
#         self.narxi_input = QLineEdit()
#         self.narxi_input.textChanged.connect(self.calculate_total)
#         form_layout.addWidget(self.narxi_input)

#         # Umumiy narx
#         form_layout.addWidget(QLabel("Umumiy Narxi:"))
#         self.umumiy_narxi_input = QLineEdit()
#         self.umumiy_narxi_input.setReadOnly(True)
#         form_layout.addWidget(self.umumiy_narxi_input)

#         # Qo'shish tugmasi
#         self.add_btn = QPushButton("Qo'shish")
#         self.add_btn.clicked.connect(self.add_yuk)
#         form_layout.addWidget(self.add_btn)

#         # Jadval
#         self.table = QTableWidget()
#         self.table.setColumnCount(6)
#         self.table.setHorizontalHeaderLabels(["ID", "Sana", "Yuk Nomi", "Miqdori", "Narxi", "Umumiy Narxi"])
#         self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         layout.addWidget(self.table)

#         # O'chirish tugmasi
#         self.delete_btn = QPushButton("Tanlangan yukni o'chirish")
#         self.delete_btn.clicked.connect(self.delete_yuk)
#         layout.addWidget(self.delete_btn)

#         # Ma'lumotlarni yuklash
#         self.load_yuklar_data()

#     def setup_balance_tab(self):
#         layout = QVBoxLayout()
#         self.balance_tab.setLayout(layout)

#         # Forma qismi
#         form_layout = QHBoxLayout()
#         layout.addLayout(form_layout)

#         # Sana
#         form_layout.addWidget(QLabel("Sana:"))
#         self.balance_date_input = QDateEdit()
#         self.balance_date_input.setDate(QDate.currentDate())
#         self.balance_date_input.setCalendarPopup(True)
#         self.balance_date_input.setDisplayFormat("yyyy-MM-dd")
#         form_layout.addWidget(self.balance_date_input)

#         # Qo'lda kirim
#         form_layout.addWidget(QLabel("Qo'lda Kirim:"))
#         self.manual_income_input = QLineEdit()
#         form_layout.addWidget(self.manual_income_input)

#         # Kirim qo'shish tugmasi
#         self.add_income_btn = QPushButton("Kirim qo'shish")
#         self.add_income_btn.clicked.connect(self.add_manual_income)
#         form_layout.addWidget(self.add_income_btn)

#         # Chiqim
#         form_layout.addWidget(QLabel("Chiqim:"))
#         self.expense_input = QLineEdit()
#         form_layout.addWidget(self.expense_input)

#         # Chiqim qo'shish tugmasi
#         self.add_expense_btn = QPushButton("Chiqim qo'shish")
#         self.add_expense_btn.clicked.connect(self.add_expense)
#         form_layout.addWidget(self.add_expense_btn)

#         # Balans jadvali
#         self.balance_table = QTableWidget()
#         self.balance_table.setColumnCount(11)
#         self.balance_table.setHorizontalHeaderLabels([
#             "ID", "Sana", "Avto Kirim", "Qo'lda Kirim", 
#             "Jami Kirim", "Chiqim", "Qoldiq",
#             "Umumiy Kirim", "Umumiy Qo'lda Kirim", 
#             "Umumiy Chiqim", "Umumiy Qoldiq"
#         ])
#         self.balance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         layout.addWidget(self.balance_table)

#         # Ma'lumotlarni yuklash
#         self.load_balance_data()

#     def load_yuk_nomlari(self):
#         self.yuk_nomi_combo.clear()
#         nomlar = self.db.get_yuk_nomlari()
#         for nom in nomlar:
#             self.yuk_nomi_combo.addItem(nom)

#     def add_new_yuk_nomi(self):
#         text, ok = QInputDialog.getText(
#             self, 
#             "Yangi yuk turi", 
#             "Yangi yuk turini kiriting:",
#             QLineEdit.Normal
#         )
        
#         if ok and text:
#             success = self.db.add_yuk_nomi(text)
#             if success:
#                 self.load_yuk_nomlari()
#                 index = self.yuk_nomi_combo.findText(text)
#                 if index >= 0:
#                     self.yuk_nomi_combo.setCurrentIndex(index)
#                 QMessageBox.information(self, "Muvaffaqiyatli", "Yangi yuk turi qo'shildi!")
#             else:
#                 QMessageBox.warning(self, "Xatolik", "Bu yuk turi allaqachon mavjud!")

#     def calculate_total(self):
#         try:
#             miqdori_text = self.miqdori_input.text().replace(',', '')
#             narxi_text = self.narxi_input.text().replace(',', '')
            
#             if miqdori_text and narxi_text:
#                 miqdori = float(miqdori_text)
#                 narxi = float(narxi_text)
#                 umumiy_narxi = miqdori * narxi
#                 formatted_total = locale.format_string("%.2f", umumiy_narxi, grouping=True)
#                 self.umumiy_narxi_input.setText(formatted_total)
#         except ValueError:
#             self.umumiy_narxi_input.clear()

#     def add_yuk(self):
#         sana = self.sana_input.date().toString("yyyy-MM-dd")
#         yuk_nomi = self.yuk_nomi_combo.currentText()
#         miqdori = self.miqdori_input.text().replace(',', '')
#         narxi = self.narxi_input.text().replace(',', '')
#         umumiy_narxi = self.umumiy_narxi_input.text().replace(',', '')

#         if not all([sana, yuk_nomi, miqdori, narxi, umumiy_narxi]):
#             QMessageBox.warning(self, "Xato", "Barcha maydonlarni to'ldiring!")
#             return

#         if self.yuk_nomi_combo.findText(yuk_nomi) == -1:
#             success = self.db.add_yuk_nomi(yuk_nomi)
#             if success:
#                 self.load_yuk_nomlari()
#                 index = self.yuk_nomi_combo.findText(yuk_nomi)
#                 if index >= 0:
#                     self.yuk_nomi_combo.setCurrentIndex(index)
#             else:
#                 QMessageBox.warning(self, "Xatolik", "Yuk turini qo'shishda xatolik yuz berdi!")
#                 return

#         try:
#             self.db.add_yuk(sana, yuk_nomi, float(miqdori), float(narxi), float(umumiy_narxi))
#             self.load_yuklar_data()
#             self.load_balance_data()
#             self.clear_inputs()
#             QMessageBox.information(self, "Muvaffaqiyatli", "Yuk muvaffaqiyatli qo'shildi!")
#         except ValueError:
#             QMessageBox.warning(self, "Xato", "Miqdor, narx va umumiy narx raqam bo'lishi kerak!")
#         except Exception as e:
#             QMessageBox.critical(self, "Xato", f"Xatolik yuz berdi: {str(e)}")

#     def add_manual_income(self):
#         sana = self.balance_date_input.date().toString("yyyy-MM-dd")
#         amount = self.manual_income_input.text().replace(',', '')

#         if not amount:
#             QMessageBox.warning(self, "Xato", "Kirim miqdorini kiriting!")
#             return

#         try:
#             amount = float(amount)
#             self.db.update_manual_income(sana, amount)
#             self.load_balance_data()
#             self.manual_income_input.clear()
#             QMessageBox.information(self, "Muvaffaqiyatli", "Qo'lda kirim qo'shildi!")
#         except ValueError:
#             QMessageBox.warning(self, "Xato", "Kirim miqdori raqam bo'lishi kerak!")

#     def add_expense(self):
#         sana = self.balance_date_input.date().toString("yyyy-MM-dd")
#         amount = self.expense_input.text().replace(',', '')

#         if not amount:
#             QMessageBox.warning(self, "Xato", "Chiqim miqdorini kiriting!")
#             return

#         try:
#             amount = float(amount)
#             self.db.update_expense(sana, amount)
#             self.load_balance_data()
#             self.expense_input.clear()
#             QMessageBox.information(self, "Muvaffaqiyatli", "Chiqim qo'shildi!")
#         except ValueError:
#             QMessageBox.warning(self, "Xato", "Chiqim miqdori raqam bo'lishi kerak!")

#     def format_number(self, num):
#         try:
#             return locale.format_string("%.2f", float(num), grouping=True)
#         except (ValueError, TypeError):
#             return str(num)

#     def load_yuklar_data(self):
#         yuklar = self.db.get_all_yuklar()
#         self.table.setRowCount(len(yuklar))
        
#         for row, yuk in enumerate(yuklar):
#             for col, data in enumerate(yuk):
#                 if col in [3, 4, 5]:  # Raqamli ustunlar
#                     item = QTableWidgetItem(self.format_number(data))
#                 else:
#                     item = QTableWidgetItem(str(data))
                
#                 self.table.setItem(row, col, item)

#     def load_balance_data(self):
#         balance_data = self.db.get_balance_data()
#         self.balance_table.setRowCount(len(balance_data))
        
#         for row, record in enumerate(balance_data):
#             for col, data in enumerate(record):
#                 if col in [2, 3, 4, 5, 6, 7, 8, 9, 10]:  # Pul miqdorlari
#                     item = QTableWidgetItem(self.format_number(data))
                    
#                     # Qoldiqni rang bilan ko'rsatish
#                     if col in [6, 10]:  # Qoldiq va Umumiy Qoldiq ustunlari
#                         try:
#                             num = float(str(data).replace(',', ''))
#                             if num < 0:
#                                 item.setForeground(Qt.red)
#                             elif num > 0:
#                                 item.setForeground(Qt.darkGreen)
#                         except ValueError:
#                             pass
#                 else:
#                     item = QTableWidgetItem(str(data))
                
#                 self.balance_table.setItem(row, col, item)

#     def delete_yuk(self):
#         selected_row = self.table.currentRow()
#         if selected_row == -1:
#             QMessageBox.warning(self, "Xato", "Iltimos, o'chirish uchun yukni tanlang!")
#             return
        
#         yuk_id = self.table.item(selected_row, 0).text()
        
#         reply = QMessageBox.question(
#             self, 
#             "O'chirish", 
#             "Haqiqatan ham bu yukni o'chirmoqchimisiz?",
#             QMessageBox.Yes | QMessageBox.No, 
#             QMessageBox.No
#         )
        
#         if reply == QMessageBox.Yes:
#             self.db.delete_yuk(yuk_id)
#             self.load_yuklar_data()
#             self.load_balance_data()
#             QMessageBox.information(self, "Muvaffaqiyatli", "Yuk o'chirildi!")

#     def clear_inputs(self):
#         self.sana_input.setDate(QDate.currentDate())
#         self.miqdori_input.clear()
#         self.narxi_input.clear()
#         self.umumiy_narxi_input.clear()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())




import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDateEdit, QCalendarWidget, QDialog,
                             QTabWidget, QComboBox, QInputDialog)
from PyQt5.QtCore import QDate, Qt
import sqlite3
import locale

# Set locale for number formatting
locale.setlocale(locale.LC_ALL, '')

class CalendarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sana tanlang")
        self.setModal(True)
        
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        
        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)
    
    def selected_date(self):
        return self.calendar.selectedDate()

class DatabaseManager:
    def __init__(self, db_name='yuklar.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.migrate_tables()
        self.init_yuk_nomlari()

    def create_tables(self):
        # Yuklar jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS yuklar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sana TEXT NOT NULL,
                yuk_nomi TEXT NOT NULL,
                miqdori REAL NOT NULL,
                narxi REAL NOT NULL,
                umumiy_narxi REAL NOT NULL
            )
        ''')
        
        # Yuk nomlari jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS yuk_nomlari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Balans jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sana TEXT NOT NULL UNIQUE,
                kirim REAL DEFAULT 0,
                qo_lda_kirim REAL DEFAULT 0,
                chiqim REAL DEFAULT 0,
                qoldiq REAL DEFAULT 0
            )
        ''')
        
        self.conn.commit()

    def migrate_tables(self):
        # Agar qo'lda_kirim ustuni yo'q bo'lsa, qo'shamiz
        self.cursor.execute("PRAGMA table_info(balance)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        if 'qo_lda_kirim' not in columns:
            self.cursor.execute('ALTER TABLE balance ADD COLUMN qo_lda_kirim REAL DEFAULT 0')
            self.conn.commit()

    def init_yuk_nomlari(self):
        default_nomlar = ['Paxta', 'Guruch', 'Bugdoy', "Kartoshka"]
        for nom in default_nomlar:
            try:
                self.cursor.execute('INSERT INTO yuk_nomlari (nom) VALUES (?)', (nom,))
            except sqlite3.IntegrityError:
                pass
        self.conn.commit()

    def add_yuk_nomi(self, nom):
        try:
            self.cursor.execute('INSERT INTO yuk_nomlari (nom) VALUES (?)', (nom,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_yuk_nomlari(self):
        self.cursor.execute('SELECT nom FROM yuk_nomlari ORDER BY nom')
        return [row[0] for row in self.cursor.fetchall()]

    def add_yuk(self, sana, yuk_nomi, miqdori, narxi, umumiy_narxi):
        self.cursor.execute('''
            INSERT INTO yuklar (sana, yuk_nomi, miqdori, narxi, umumiy_narxi)
            VALUES (?, ?, ?, ?, ?)
        ''', (sana, yuk_nomi, miqdori, narxi, umumiy_narxi))
        
        # Balans jadvalini yangilaymiz
        self.cursor.execute('''
            INSERT OR IGNORE INTO balance (sana, kirim, qo_lda_kirim, chiqim, qoldiq)
            VALUES (?, 0, 0, 0, 0)
        ''', (sana,))
        
        # Avtomatik kirim va qoldiqni hisoblaymiz
        self.cursor.execute('''
            UPDATE balance 
            SET kirim = (SELECT COALESCE(SUM(umumiy_narxi), 0) FROM yuklar WHERE sana = ?),
                qoldiq = kirim + qo_lda_kirim - chiqim
            WHERE sana = ?
        ''', (sana, sana))
        
        self.conn.commit()

    def get_all_yuklar(self):
        self.cursor.execute('SELECT * FROM yuklar ORDER BY sana DESC')
        return self.cursor.fetchall()

    def delete_yuk(self, yuk_id):
        # Yuk sanasini olamiz
        self.cursor.execute('SELECT sana FROM yuklar WHERE id=?', (yuk_id,))
        sana = self.cursor.fetchone()[0]
        
        # Yukni o'chiramiz
        self.cursor.execute('DELETE FROM yuklar WHERE id=?', (yuk_id,))
        
        # Balansni yangilaymiz
        self.cursor.execute('''
            UPDATE balance 
            SET kirim = (SELECT COALESCE(SUM(umumiy_narxi), 0) FROM yuklar WHERE sana = ?),
                qoldiq = kirim + qo_lda_kirim - chiqim
            WHERE sana = ?
        ''', (sana, sana))
        
        self.conn.commit()

    def get_balance_data(self):
        self.cursor.execute('''
            SELECT id, sana, kirim, qo_lda_kirim, 
                   (kirim + qo_lda_kirim) as jami_kirim,
                   chiqim, 
                   (kirim + qo_lda_kirim - chiqim) as qoldiq,
                   (SELECT SUM(kirim) FROM balance) as umumiy_kirim,
                   (SELECT SUM(qo_lda_kirim) FROM balance) as umumiy_qo_lda_kirim,
                   (SELECT SUM(chiqim) FROM balance) as umumiy_chiqim,
                   (SELECT SUM(kirim + qo_lda_kirim - chiqim) FROM balance) as umumiy_qoldiq
            FROM balance
            ORDER BY sana DESC
        ''')
        return self.cursor.fetchall()

    def update_manual_income(self, sana, amount):
        self.cursor.execute('''
            INSERT OR IGNORE INTO balance (sana, kirim, qo_lda_kirim, chiqim, qoldiq)
            VALUES (?, 0, 0, 0, 0)
        ''', (sana,))
        
        self.cursor.execute('''
            UPDATE balance 
            SET qo_lda_kirim = ?,
                qoldiq = kirim + ? - chiqim
            WHERE sana = ?
        ''', (amount, amount, sana))
        
        self.conn.commit()

    def update_expense(self, sana, amount):
        self.cursor.execute('''
            INSERT OR IGNORE INTO balance (sana, kirim, qo_lda_kirim, chiqim, qoldiq)
            VALUES (?, 0, 0, 0, 0)
        ''', (sana,))
        
        self.cursor.execute('''
            UPDATE balance 
            SET chiqim = ?,
                qoldiq = kirim + qo_lda_kirim - ?
            WHERE sana = ?
        ''', (amount, amount, sana))
        
        self.conn.commit()

    def __del__(self):
        self.conn.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setWindowTitle("Yuklar va Balans Boshqaruvi")
        self.setGeometry(100, 100, 1300, 800)

        # Tab widget yaratamiz
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Yuklar tab
        self.yuklar_tab = QWidget()
        self.tabs.addTab(self.yuklar_tab, "Yuklar")
        self.setup_yuklar_tab()

        # Balans tab
        self.balance_tab = QWidget()
        self.tabs.addTab(self.balance_tab, "Kirim-Chiqim Balansi")
        self.setup_balance_tab()

    def setup_yuklar_tab(self):
        layout = QVBoxLayout()
        self.yuklar_tab.setLayout(layout)

        # Forma qismi
        form_layout = QHBoxLayout()
        layout.addLayout(form_layout)

        # Sana
        form_layout.addWidget(QLabel("Sana:"))
        self.sana_input = QDateEdit()
        self.sana_input.setDate(QDate.currentDate())
        self.sana_input.setCalendarPopup(True)
        self.sana_input.setDisplayFormat("yyyy-MM-dd")
        form_layout.addWidget(self.sana_input)

        # Yuk nomi (ComboBox)
        form_layout.addWidget(QLabel("Yuk Nomi:"))
        self.yuk_nomi_combo = QComboBox()
        self.yuk_nomi_combo.setEditable(True)
        self.yuk_nomi_combo.lineEdit().setPlaceholderText("Yuk nomini tanlang yoki kiriting")
        self.load_yuk_nomlari()
        form_layout.addWidget(self.yuk_nomi_combo)

        # Yuk nomi qo'shish tugmasi
        self.add_yuk_nomi_btn = QPushButton("+")
        self.add_yuk_nomi_btn.setFixedWidth(30)
        self.add_yuk_nomi_btn.setToolTip("Yangi yuk turini qo'shish")
        self.add_yuk_nomi_btn.clicked.connect(self.add_new_yuk_nomi)
        form_layout.addWidget(self.add_yuk_nomi_btn)

        # Miqdori
        form_layout.addWidget(QLabel("Miqdori:"))
        self.miqdori_input = QLineEdit()
        self.miqdori_input.textChanged.connect(self.calculate_total)
        form_layout.addWidget(self.miqdori_input)

        # Narxi
        form_layout.addWidget(QLabel("Narxi:"))
        self.narxi_input = QLineEdit()
        self.narxi_input.textChanged.connect(self.calculate_total)
        form_layout.addWidget(self.narxi_input)

        # Umumiy narx
        form_layout.addWidget(QLabel("Umumiy Narxi:"))
        self.umumiy_narxi_input = QLineEdit()
        self.umumiy_narxi_input.setReadOnly(True)
        form_layout.addWidget(self.umumiy_narxi_input)

        # Qo'shish tugmasi
        self.add_btn = QPushButton("Qo'shish")
        self.add_btn.clicked.connect(self.add_yuk)
        form_layout.addWidget(self.add_btn)

        # Jadval
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Sana", "Yuk Nomi", "Miqdori", "Narxi", "Umumiy Narxi"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # O'chirish tugmasi
        self.delete_btn = QPushButton("Tanlangan yukni o'chirish")
        self.delete_btn.clicked.connect(self.delete_yuk)
        layout.addWidget(self.delete_btn)

        # Ma'lumotlarni yuklash
        self.load_yuklar_data()

    def setup_balance_tab(self):
        layout = QVBoxLayout()
        self.balance_tab.setLayout(layout)

        # Forma qismi
        form_layout = QHBoxLayout()
        layout.addLayout(form_layout)

        # Sana
        form_layout.addWidget(QLabel("Sana:"))
        self.balance_date_input = QDateEdit()
        self.balance_date_input.setDate(QDate.currentDate())
        self.balance_date_input.setCalendarPopup(True)
        self.balance_date_input.setDisplayFormat("yyyy-MM-dd")
        form_layout.addWidget(self.balance_date_input)

        # Qo'lda kirim
        form_layout.addWidget(QLabel("Qo'lda Kirim:"))
        self.manual_income_input = QLineEdit()
        form_layout.addWidget(self.manual_income_input)

        # Kirim qo'shish tugmasi
        self.add_income_btn = QPushButton("Kirim qo'shish")
        self.add_income_btn.clicked.connect(self.add_manual_income)
        form_layout.addWidget(self.add_income_btn)

        # Chiqim
        form_layout.addWidget(QLabel("Chiqim:"))
        self.expense_input = QLineEdit()
        form_layout.addWidget(self.expense_input)

        # Chiqim qo'shish tugmasi
        self.add_expense_btn = QPushButton("Chiqim qo'shish")
        self.add_expense_btn.clicked.connect(self.add_expense)
        form_layout.addWidget(self.add_expense_btn)

        # Balans jadvali
        self.balance_table = QTableWidget()
        self.balance_table.setColumnCount(11)
        self.balance_table.setHorizontalHeaderLabels([
            "ID", "Sana", "Avto Kirim", "Qo'lda Kirim", 
            "Jami Kirim", "Chiqim", "Qoldiq",
            "Umumiy Kirim", "Umumiy Qo'lda Kirim", 
            "Umumiy Chiqim", "Umumiy Qoldiq"
        ])
        self.balance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.balance_table)

        # Ma'lumotlarni yuklash
        self.load_balance_data()

    def load_yuk_nomlari(self):
        self.yuk_nomi_combo.clear()
        nomlar = self.db.get_yuk_nomlari()
        for nom in nomlar:
            self.yuk_nomi_combo.addItem(nom)

    def add_new_yuk_nomi(self):
        text, ok = QInputDialog.getText(
            self, 
            "Yangi yuk turi", 
            "Yangi yuk turini kiriting:",
            QLineEdit.Normal
        )
        
        if ok and text:
            success = self.db.add_yuk_nomi(text)
            if success:
                self.load_yuk_nomlari()
                index = self.yuk_nomi_combo.findText(text)
                if index >= 0:
                    self.yuk_nomi_combo.setCurrentIndex(index)
                QMessageBox.information(self, "Muvaffaqiyatli", "Yangi yuk turi qo'shildi!")
            else:
                QMessageBox.warning(self, "Xatolik", "Bu yuk turi allaqachon mavjud!")

    def calculate_total(self):
        try:
            miqdori_text = self.miqdori_input.text().replace(',', '')
            narxi_text = self.narxi_input.text().replace(',', '')
            
            if miqdori_text and narxi_text:
                miqdori = float(miqdori_text)
                narxi = float(narxi_text)
                umumiy_narxi = miqdori * narxi
                formatted_total = locale.format_string("%.2f", umumiy_narxi, grouping=True)
                self.umumiy_narxi_input.setText(formatted_total)
        except ValueError:
            self.umumiy_narxi_input.clear()

    def add_yuk(self):
        sana = self.sana_input.date().toString("yyyy-MM-dd")
        yuk_nomi = self.yuk_nomi_combo.currentText()
        miqdori = self.miqdori_input.text().replace(',', '')
        narxi = self.narxi_input.text().replace(',', '')
        umumiy_narxi = self.umumiy_narxi_input.text().replace(',', '')

        if not all([sana, yuk_nomi, miqdori, narxi, umumiy_narxi]):
            QMessageBox.warning(self, "Xato", "Barcha maydonlarni to'ldiring!")
            return

        if self.yuk_nomi_combo.findText(yuk_nomi) == -1:
            success = self.db.add_yuk_nomi(yuk_nomi)
            if success:
                self.load_yuk_nomlari()
                index = self.yuk_nomi_combo.findText(yuk_nomi)
                if index >= 0:
                    self.yuk_nomi_combo.setCurrentIndex(index)
            else:
                QMessageBox.warning(self, "Xatolik", "Yuk turini qo'shishda xatolik yuz berdi!")
                return

        try:
            self.db.add_yuk(sana, yuk_nomi, float(miqdori), float(narxi), float(umumiy_narxi))
            self.load_yuklar_data()
            self.load_balance_data()
            self.clear_inputs()
            QMessageBox.information(self, "Muvaffaqiyatli", "Yuk muvaffaqiyatli qo'shildi!")
        except ValueError:
            QMessageBox.warning(self, "Xato", "Miqdor, narx va umumiy narx raqam bo'lishi kerak!")
        except Exception as e:
            QMessageBox.critical(self, "Xato", f"Xatolik yuz berdi: {str(e)}")

    def add_manual_income(self):
        sana = self.balance_date_input.date().toString("yyyy-MM-dd")
        amount = self.manual_income_input.text().replace(',', '')

        if not amount:
            QMessageBox.warning(self, "Xato", "Kirim miqdorini kiriting!")
            return

        try:
            amount = float(amount)
            self.db.update_manual_income(sana, amount)
            self.load_balance_data()
            self.manual_income_input.clear()
            QMessageBox.information(self, "Muvaffaqiyatli", "Qo'lda kirim qo'shildi!")
        except ValueError:
            QMessageBox.warning(self, "Xato", "Kirim miqdori raqam bo'lishi kerak!")

    def add_expense(self):
        sana = self.balance_date_input.date().toString("yyyy-MM-dd")
        amount = self.expense_input.text().replace(',', '')

        if not amount:
            QMessageBox.warning(self, "Xato", "Chiqim miqdorini kiriting!")
            return

        try:
            amount = float(amount)
            self.db.update_expense(sana, amount)
            self.load_balance_data()
            self.expense_input.clear()
            QMessageBox.information(self, "Muvaffaqiyatli", "Chiqim qo'shildi!")
        except ValueError:
            QMessageBox.warning(self, "Xato", "Chiqim miqdori raqam bo'lishi kerak!")

    def format_number(self, num):
        try:
            return locale.format_string("%d", round(float(num)), grouping=True)
        except (ValueError, TypeError):
            return str(num)

    def load_yuklar_data(self):
        yuklar = self.db.get_all_yuklar()
        self.table.setRowCount(len(yuklar))
        
        for row, yuk in enumerate(yuklar):
            for col, data in enumerate(yuk):
                if col in [3, 4, 5]:  # Raqamli ustunlar
                    item = QTableWidgetItem(self.format_number(data))
                else:
                    item = QTableWidgetItem(str(data))
                
                self.table.setItem(row, col, item)

    def load_balance_data(self):
        balance_data = self.db.get_balance_data()
        self.balance_table.setRowCount(len(balance_data))
        
        for row, record in enumerate(balance_data):
            for col, data in enumerate(record):
                if col in [2, 3, 4, 5, 6, 7, 8, 9, 10]:  # Pul miqdorlari
                    item = QTableWidgetItem(self.format_number(data))
                    
                    # Qoldiqni rang bilan ko'rsatish
                    if col in [6, 10]:  # Qoldiq va Umumiy Qoldiq ustunlari
                        try:
                            num = float(str(data).replace(',', ''))
                            if num < 0:
                                item.setForeground(Qt.red)
                            elif num > 0:
                                item.setForeground(Qt.darkGreen)
                        except ValueError:
                            pass
                else:
                    item = QTableWidgetItem(str(data))
                
                self.balance_table.setItem(row, col, item)

    def delete_yuk(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Xato", "Iltimos, o'chirish uchun yukni tanlang!")
            return
        
        yuk_id = self.table.item(selected_row, 0).text()
        
        reply = QMessageBox.question(
            self, 
            "O'chirish", 
            "Haqiqatan ham bu yukni o'chirmoqchimisiz?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.delete_yuk(yuk_id)
            self.load_yuklar_data()
            self.load_balance_data()
            QMessageBox.information(self, "Muvaffaqiyatli", "Yuk o'chirildi!")

    def clear_inputs(self):
        self.sana_input.setDate(QDate.currentDate())
        self.miqdori_input.clear()
        self.narxi_input.clear()
        self.umumiy_narxi_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())