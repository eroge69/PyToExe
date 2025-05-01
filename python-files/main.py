import os
import sys
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QDateEdit, QSpinBox, QMessageBox, QToolButton,
    QCompleter, QHeaderView, QDialog, QFormLayout
)
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QStringListModel, QCoreApplication, QUrl
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
import tempfile
DB_PATH = 'invoices.db'
# Handle the path to the icon correctly in bundled executable
icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')

# Dark Theme Stylesheet (Updated for Tabs and Input Fields)
dark_stylesheet = """
    QWidget {
        background-color: #232429;
        color: #FFFFFF;
        font-family: "Times New Roman";
    }
    QPushButton {
        background-color: #339DFF;
        border-radius: 15px;
        padding: 10px;
        font-size: 14px;
        color: #FFFFFF;
    }
    QPushButton#saveButton {
        background-color: #28a745;
    }
    QPushButton#deleteButton {
        background-color: #FF6347;
    }
    QPushButton#editButton {
        background-color: #FFA500;
    }
    QLineEdit, QDateEdit, QSpinBox {
        background-color: #2E2E47;
        border-radius: 10px;
        color: white;
        padding: 5px;
    }
    QTableWidget {
        background-color: #2E2E47;
        border-radius: 10px;
        color: #FFFFFF;
    }
    QTabWidget::pane {
        border: 1px solid #339DFF;
        background-color: #232429;
    }
    QTabBar::tab:selected {
        background-color: #339DFF;
    }
    QTabBar::tab {
        background-color: #232429;
        border-radius: 12px;
        padding: 10px;
        font-size: 14px;
    }
    QLabel {
        color: #339DFF;
        font-weight: bold;
    }
    QSpinBox {
        background-color: #2E2E47;
        border-radius: 10px;
        color: white;
    }
    QLineEdit {
        background-color: #2E2E47;
        border-radius: 10px;
        color: white;
        padding: 5px;
    }
"""

class InvoiceApp(QMainWindow):
    def __init__(self):
        super().__init__()
    
        self.setWindowTitle('Invoicing System')
        self.setGeometry(100, 100, 900, 600)
        # Set base font
        font = QFont('Montserrat', 10)
        self.setFont(font)
        # Completer for item names
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self.init_db()
        self.init_ui()
        self.apply_theme(dark=True)  # Apply Dark Theme

    def apply_theme(self, dark=True):
        self.setStyleSheet(dark_stylesheet)

    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        price REAL NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        invoice_no TEXT UNIQUE NOT NULL,
                        date TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS invoice_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        invoice_id INTEGER,
                        item_name TEXT,
                        qty INTEGER,
                        price REAL,
                        FOREIGN KEY(invoice_id) REFERENCES invoices(id))''')
        conn.commit()
        conn.close()

    def init_ui(self):
        # Central widget and main layout
        central_widget = QWidget()

        main_layout = QVBoxLayout(central_widget)
     
        # Create and set the header above the tabs
        header_label = QLabel("Bismillah Communication Networks\nInvoicing System\n")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)

        # Create the QTabWidget for tabs
        self.tabs = QTabWidget()

        # Create individual tabs
        self.invoice_tab = QWidget()
        self.inventory_tab = QWidget()
        self.accounts_tab = QWidget()

        # Add tabs to the tab widget
        self.tabs.addTab(self.invoice_tab, 'Invoice')
        self.tabs.addTab(self.inventory_tab, 'Inventory')
        self.tabs.addTab(self.accounts_tab, 'Accounts')

        # Call functions to build content for each tab
        self.build_invoice_tab()
        self.build_inventory_tab()
        self.build_accounts_tab()
        # Insert HTML content in QLabel
       # Write ad code to a temporary file
        ad_html = """
        <!DOCTYPE html>
        <html><head><meta charset="UTF-8"><style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }
        iframe {
            border: none;
            width: 728px;
            height: 90px;
        }
    </style></head><body>
        <script type="text/javascript">
            atOptions = {
                'key' : '33044b7e955fa9aca59e431f1122e14b',
                'format' : 'iframe',
                'height' : 90,
                'width' : 728,
                'params' : {}
            };
        </script>
        <script type="text/javascript" src="https://highperformanceformat.com/33044b7e955fa9aca59e431f1122e14b/invoke.js"></script>
        </body></html>
        """

        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            f.write(ad_html)
            temp_path = f.name

        # Load the ad via file:// URL
        web_view = QWebEngineView()
        web_view.setFixedSize(728, 90)
        # Enable JavaScript for the QWebEngineView
        web_view.page().settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
                # Add the web view just above the footer
        web_view.load(QUrl.fromLocalFile(temp_path))
        # main_layout.addWidget(web_view)
        web_layout = QHBoxLayout()
        web_layout.addStretch(1)  # Add stretch before the web view
        web_layout.addWidget(web_view)
        web_layout.addStretch(1)  # Add stretch after the web view
        main_layout.addLayout(web_layout)
        # Add the tabs and footer to the main layout
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.add_footer())

        # Set the central widget
        self.setCentralWidget(central_widget)



    def build_invoice_tab(self):
        layout = QVBoxLayout()
        form = QHBoxLayout()

        # Item input with completer
        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText('Item name')
        self.item_input.setStyleSheet("""
        QLineEdit {
            background-color: #232429;
            color: white;
            padding: 5px;
            border: 1px solid #339DFF;
            border-radius: 5px;
        }
        QCompleter-popup {
            border: 1px solid #339DFF;
            background-color: #232429;
            color: white;
        }
        QAbstractItemView {
            background-color: #232429;
            color: white;
        }
        QCompleter-popup::item {
            padding: 5px;
            border-radius: 5px;
        }
        QCompleter-popup::item:selected {
            background-color: #339DFF;
            color: white;
        }
        """)
        self.item_input.setCompleter(self.completer)
        self.completer.activated[str].connect(self.on_item_selected)
        form.addWidget(self.item_input)

        # Quantity and Price inputs
        self.qty_input = QSpinBox()
        self.qty_input.setMinimum(1)
        form.addWidget(self.qty_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText('Price')
        form.addWidget(self.price_input)

        # Invoice number & date
        self.invoice_no = QLineEdit(self.generate_invoice_no())
        self.invoice_no.setReadOnly(True)
        form.addWidget(self.invoice_no)

        self.date_input = QDateEdit(datetime.now())
        self.date_input.setCalendarPopup(True)
        form.addWidget(self.date_input)

        # Add button
        add_btn = QPushButton('Add')
        add_btn.setObjectName("saveButton")
        add_btn.clicked.connect(self.add_item_to_invoice)
        form.addWidget(add_btn)

        layout.addLayout(form)

        # Items table with actions
        self.items_table = QTableWidget(0, 5)
        self.items_table.setHorizontalHeaderLabels(['Item', 'Qty', 'Price', 'Total', 'Actions'])
        self.items_table.verticalHeader().setVisible(False) 
        # Set custom background color for header
        header = self.items_table.horizontalHeader()
        header.setStyleSheet("QHeaderView::section { background-color: #232429; color: white; font-weight: bold;  }")

        # Adjust the size of the Actions column (column index 4)
        self.items_table.setColumnWidth(4, 250)  # Increase width of the Actions column

        # Create space between buttons and layout for them
        self.items_table.setStyleSheet("""
            QTableWidget {
                background-color: #232429;
                color: white;
            }
            QTableWidget::item {
                background-color: #232429;
                
            }
        """)

        layout.addWidget(self.items_table)

        # Generate button
        gen_btn = QPushButton('Generate Invoice')
        gen_btn.setObjectName("saveButton")
        gen_btn.clicked.connect(self.save_invoice)
        layout.addWidget(gen_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.invoice_tab.setLayout(layout)
        self.update_item_completer()


    def build_inventory_tab(self):
        layout = QVBoxLayout()
        form = QHBoxLayout()
        self.inv_name = QLineEdit()
        self.inv_name.setPlaceholderText('Item Name')
        form.addWidget(self.inv_name)
        self.inv_price = QLineEdit()
        self.inv_price.setPlaceholderText('Price')
        form.addWidget(self.inv_price)

        save_btn = QPushButton('Save')
        save_btn.setObjectName("saveButton")
        save_btn.clicked.connect(self.save_inventory_item)
        form.addWidget(save_btn)
        layout.addLayout(form)
        # Inventory table
        self.inv_table = QTableWidget(0, 4)
        self.inv_table.setHorizontalHeaderLabels(
            ['ID', 'Name', 'Price', 'Actions']
        )
        header = self.inv_table.horizontalHeader()
        self.inv_table.setColumnWidth(3, 250)
        self.inv_table.setRowHeight(3, 50)
        self.inv_table.verticalHeader().setVisible(False) 
        header.setStyleSheet("QHeaderView::section { background-color: #232429; color: white; font-weight: bold; }")
    
        layout.addWidget(self.inv_table)
        self.inventory_tab.setLayout(layout)
        self.load_inventory()

    def build_accounts_tab(self):
        layout = QVBoxLayout()
        self.acc_table = QTableWidget(0, 3)
        self.acc_table.setHorizontalHeaderLabels(
            ['Date', 'Invoice No', 'Actions']
        )
        # Set custom background color for header
        header = self.acc_table.horizontalHeader()
        self.acc_table.setColumnWidth(2, 390)
        header.setStyleSheet("QHeaderView::section { background-color: #232429; color: white; font-weight: bold; }")
    
        layout.addWidget(self.acc_table)
        self.accounts_tab.setLayout(layout)
        self.load_accounts()

    def generate_invoice_no(self):
        return f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def update_item_completer(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT name FROM inventory')
        names = [row[0] for row in c.fetchall()]
        conn.close()
        model = QStringListModel(names)
        self.completer.setModel(model)

    def on_item_selected(self, text):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT price FROM inventory WHERE name = ?', (text,))
        row = c.fetchone()
        conn.close()
        if row:
            self.price_input.setText(str(row[0]))

    def add_item_to_invoice(self):
        name = self.item_input.text().strip()
        if not name:
            return
        try:
            qty = self.qty_input.value()
            price = float(self.price_input.text())
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Invalid price')
            return
        total = qty * price
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        self.items_table.setItem(row, 0, QTableWidgetItem(name))
        self.items_table.setItem(row, 1, QTableWidgetItem(str(qty)))
        self.items_table.setItem(row, 2, QTableWidgetItem(f"{price:.2f}"))
        self.items_table.setItem(row, 3, QTableWidgetItem(f"{total:.2f}"))
        # Actions
        btn_edit = QPushButton("Edit")
        btn_edit.setObjectName("editButton")
        btn_edit.setFixedSize(80, 30)
        btn_edit.clicked.connect(lambda _, r=row: self.edit_item(r))

        btn_del = QPushButton("Delete")
        btn_del.setObjectName("deleteButton")
        btn_del.setFixedSize(80, 30)
        btn_del.clicked.connect(lambda _, r=row: self.remove_item(r))

        widget = QWidget()
        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(btn_edit)
        lay.addWidget(btn_del)
        widget.setLayout(lay)
        self.items_table.setCellWidget(row, 4, widget)
        # Clear inputs
        self.item_input.clear(); self.price_input.clear(); self.qty_input.setValue(1)

    def edit_item(self, row):
        item_name_item = self.items_table.item(row, 0)
        quantity_item = self.items_table.item(row, 1)
        price_item = self.items_table.item(row, 2)

        if item_name_item and quantity_item and price_item:
            name = item_name_item.text()
            quantity = quantity_item.text()
            price = price_item.text()
            self.item_input.setText(name)
            self.qty_input.setValue(int(quantity))
            self.price_input.setText(price)

            # Remove the item row from the table temporarily
            self.items_table.removeRow(row)

    def remove_item(self, row):
        self.items_table.removeRow(row)

    def save_invoice(self):
        inv_no = self.invoice_no.text()
        date_str = self.date_input.date().toString('yyyy-MM-dd')
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO invoices (invoice_no, date) VALUES (?, ?)', (inv_no, date_str))
        inv_id = c.lastrowid
        for r in range(self.items_table.rowCount()):
            name = self.items_table.item(r, 0).text()
            qty = int(self.items_table.item(r, 1).text())
            price = float(self.items_table.item(r, 2).text())
            c.execute(
                'INSERT INTO invoice_items (invoice_id, item_name, qty, price) VALUES (?, ?, ?, ?)',
                (inv_id, name, qty, price)
            )
            # update inventory
            
        conn.commit()
        conn.close()
        self.export_pdf(inv_no)
        QMessageBox.information(self, 'Success', 'Invoice saved and PDF created.')
        # reset
        self.items_table.setRowCount(0)
        self.invoice_no.setText(self.generate_invoice_no())
        self.load_inventory()
        self.load_accounts()

    def export_pdf(self, inv_no):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Get invoice ID and date
        c.execute('SELECT id, date FROM invoices WHERE invoice_no = ?', (inv_no,))
        invoice = c.fetchone()
        if not invoice:
            QMessageBox.warning(self, 'Error', 'Invoice not found.')
            return

        invoice_id, date_str = invoice

        # Get invoice items
        c.execute('SELECT item_name, qty, price FROM invoice_items WHERE invoice_id = ?', (invoice_id,))
        items = c.fetchall()
        conn.close()

        # Generate PDF
        pdf_file = f"{inv_no}.pdf"
        c = canvas.Canvas(pdf_file, pagesize=A4)
        width, height = A4

        font_name = "Helvetica-Bold"
        font_size = 24
        c.setFont(font_name, font_size)

        # The text you want to display
        text = "Bismillah Communication Networks"

        # Calculate the width of the text
        text_width = c.stringWidth(text, font_name, font_size)

        # Calculate x position to center the text horizontally
        x_position = (width - text_width) / 2

        # Set y position (40 units from the bottom of the page)
        y_position = height - 40

        # Draw the centered text
        c.drawString(x_position, y_position, text)
        
        y = height - 80
        c.setFont('Helvetica-Bold', 14)
        c.drawString(40, y, f"Invoice No: {inv_no}")
        y -= 20
        c.setFont('Helvetica', 12)
        c.drawString(40, y, f"Date: {date_str}")
        y -= 40

        # Table headers
        c.setFont('Helvetica-Bold', 12)
        c.drawString(40, y, "Item")
        c.drawString(240, y, "Qty")
        c.drawString(300, y, "Price")
        c.drawString(400, y, "Total")
        y -= 20
        c.setFont('Helvetica', 12)

        grand_total = 0
        for name, qty, price in items:
            total = qty * price
            grand_total += total
            c.drawString(40, y, name)
            c.drawString(240, y, str(qty))
            c.drawString(300, y, f"{price:.2f}")
            c.drawString(400, y, f"{total:.2f}")
            y -= 20
            if y < 50:  # Avoid writing off the page
                c.showPage()
                y = height - 40

        # Total
        y -= 20
        c.setFont('Helvetica-Bold', 12)
        c.drawString(300, y, "Grand Total:")
        c.drawString(400, y, f"{grand_total:.2f}")

        c.save()

    def save_inventory_item(self):
        name = self.inv_name.text().strip()
        try:
            price = float(self.inv_price.text())
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Invalid data')
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'REPLACE INTO inventory (name, price) VALUES (?, ?)',
            (name, price)
        )
        conn.commit()
        conn.close()
        self.inv_name.clear(); self.inv_price.clear();
        self.load_inventory()
        self.update_item_completer()

    def load_inventory(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, name, price FROM inventory')
        rows = c.fetchall()
        conn.close()

        self.inv_table.setRowCount(0)
        for id_, name, price in rows:
            r = self.inv_table.rowCount()
            self.inv_table.insertRow(r)
            self.inv_table.setItem(r, 0, QTableWidgetItem(str(id_)))
            self.inv_table.setItem(r, 1, QTableWidgetItem(name))
            self.inv_table.setItem(r, 2, QTableWidgetItem(f"{price:.2f}"))

            # Edit & Delete buttons
            btn_edit = QPushButton("Edit")
            btn_del = QPushButton("Delete")
            btn_edit.setObjectName("editButton")
            btn_del.setObjectName("deleteButton")
            btn_edit.setFixedSize(80, 30)
            btn_del.setFixedSize(80, 30)
            btn_edit.clicked.connect(lambda _, r=r, id_=id_: self.edit_inventory_item(r, id_))
            btn_del.clicked.connect(lambda _, r=r, id_=id_: self.delete_inventory_item(id_))
            
            widget = QWidget()
            lay = QHBoxLayout()
            lay.addWidget(btn_edit)
            lay.addWidget(btn_del)
            widget.setLayout(lay)
            self.inv_table.setRowHeight(r, 50)
            self.inv_table.setCellWidget(r, 3, widget)

    def edit_inventory_item(self, row, inv_id):
        name = self.inv_table.item(row, 1).text()
        price = self.inv_table.item(row, 2).text()

        self.inv_name.setText(name)
        self.inv_price.setText(price)

        # Delete the item from the table for editing
        self.inv_table.removeRow(row)

    def delete_inventory_item(self, inv_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM inventory WHERE id = ?', (inv_id,))
        conn.commit()
        conn.close()
        self.load_inventory()

    def load_accounts(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT invoices.date, invoices.invoice_no FROM invoices')
        rows = c.fetchall()
        conn.close()

        self.acc_table.setRowCount(0)
        for date_str, inv_no in rows:
            row = self.acc_table.rowCount()
            self.acc_table.insertRow(row)
            self.acc_table.setItem(row, 0, QTableWidgetItem(date_str))
            self.acc_table.setItem(row, 1, QTableWidgetItem(inv_no))
            self.acc_table.verticalHeader().setVisible(False)


            view_btn = QPushButton("View")
            view_btn.setObjectName("viewButton")
            view_btn.setFixedSize(80, 30)
            view_btn.clicked.connect(lambda _, inv=inv_no: self.view_invoice(inv))

            edit_btn = QPushButton("Edit")
            edit_btn.setObjectName("editButton")
            edit_btn.setFixedSize(80, 30)
            edit_btn.clicked.connect(lambda _, inv=inv_no: self.edit_invoice(inv))

            del_btn = QPushButton("Delete")
            del_btn.setObjectName("deleteButton")
            del_btn.setFixedSize(80, 30)
            del_btn.clicked.connect(lambda _, inv=inv_no: self.delete_invoice(inv))

            regen_btn = QPushButton("Regenerate")
            regen_btn.setFixedSize(100, 30)
            regen_btn.clicked.connect(lambda _, inv=inv_no: self.export_pdf(inv))

            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)
            action_layout.addWidget(view_btn)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(del_btn)
            action_layout.addWidget(regen_btn)
            action_widget.setLayout(action_layout)

            self.acc_table.setCellWidget(row, 2, action_widget)

    def view_invoice(self, inv_no):
        pdf_file = f"{inv_no}.pdf"
        if os.path.exists(pdf_file):
            os.system(f'"{pdf_file}"')  # Opens with default viewer
        else:
            QMessageBox.warning(self, "Missing PDF", f"PDF file '{pdf_file}' not found.")
    
    def delete_invoice(self, inv_no):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM invoice_items WHERE invoice_id IN(SELECT id FROM invoices WHERE invoice_no=?)', (inv_no,))
        c.execute('DELETE FROM invoices WHERE invoice_no=?', (inv_no,))
        conn.commit()
        conn.close()
    
        pdf_file = f"{inv_no}.pdf"
        if os.path.exists(pdf_file):
            os.remove(pdf_file)
    
        self.load_accounts()
        QMessageBox.information(self, "Deleted", f"Invoice {inv_no} and its PDF have been deleted.")
    
    

    def edit_invoice(self, inv_no):
        # Implement your logic to load and edit the invoice
        dialog = EditInvoiceDialog(inv_no, self)
        dialog.exec()


    def add_footer(self):
        footer_frame = QtWidgets.QWidget()
        footer_layout = QtWidgets.QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(10, 5, 10, 5)
        footer_layout.setSpacing(10)

        # Left side: Visit Website (styled as hyperlink)
        footer_left_label = QtWidgets.QLabel()
        footer_left_label.setText('<a href="https://khilji.web.app" style="color:#339DFF;">Visit Website</a>')
        footer_left_label.setOpenExternalLinks(True)
        footer_left_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)

        # Right side: Designer credit
        footer_right_label = QtWidgets.QLabel("Designed and Created by KHILJI")
        footer_right_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        footer_right_label.setStyleSheet("color: #339DFF;")

        footer_layout.addWidget(footer_left_label)
        footer_layout.addStretch()
        footer_layout.addWidget(footer_right_label)

        footer_frame.setStyleSheet("background-color: #232429; padding: 5px;")
        return footer_frame
    
class EditInvoiceDialog(QDialog):
    def __init__(self, inv_no, parent=None):
        super().__init__(parent)
        self.inv_no = inv_no
        self.setWindowTitle(f"Edit Invoice {inv_no}")
        
        # Layout for the form
        self.layout = QVBoxLayout(self)
        
        # Form layout for editing invoice items
        self.form_layout = QFormLayout()
        
        # Widgets for editing invoice fields (add more fields if necessary)
        self.item_name_edit = QLineEdit()
        self.qty_edit = QSpinBox()
        self.qty_edit.setRange(1, 1000)  # Quantity range (can be adjusted)
        self.price_edit = QLineEdit()

        # Add form fields
        self.form_layout.addRow("Item Name:", self.item_name_edit)
        self.form_layout.addRow("Quantity:", self.qty_edit)
        self.form_layout.addRow("Price:", self.price_edit)
        
        # Button for saving changes
        self.save_button = QPushButton("Save Changes")
        self.save_button.setStyleSheet("background-color: #28a745; color: white;")
        self.save_button.clicked.connect(self.save_changes)
        
        # Adding widgets to the layout
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.save_button)
        
        self.load_invoice_data()
    
    def load_invoice_data(self):
        """Load the invoice data to the form for editing."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT item_name, qty, price FROM invoice_items WHERE invoice_id IN(SELECT id FROM invoices WHERE invoice_no=?)', (self.inv_no,))
        rows = c.fetchall()
        conn.close()

        # Assuming one item per invoice for simplicity
        if rows:
            item_name, qty, price = rows[0]  # Get the first row (adjust if needed for multiple items)
            self.item_name_edit.setText(item_name)
            self.qty_edit.setValue(qty)
            self.price_edit.setText(str(price))
    def save_changes(self):
        """Save the edited data back to the database."""
        item_name = self.item_name_edit.text()
        qty = self.qty_edit.value()
        price = float(self.price_edit.text())
        
        # Update the invoice item in the database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE invoice_items SET item_name=?, qty=?, price=? WHERE invoice_id IN(SELECT id FROM invoices WHERE invoice_no=?)', (item_name, qty, price, self.inv_no))
        conn.commit()
        conn.close()

        # Inform the user that the changes have been saved
        QMessageBox.information(self, "Success", f"Invoice {self.inv_no} has been updated.")
        self.accept()  # Close the dialog

import os
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --allow-running-insecure-content --disable-web-security"
os.environ["QT_QUICK_BACKEND"] = "software"
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    # Set attribute to disable high DPI scaling
    
    window = InvoiceApp()
    window.setWindowTitle('Bismillah Communication Networks')
    window.setWindowIcon(QIcon(icon_path))
    window.show()
    sys.exit(app.exec())
