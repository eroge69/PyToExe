from multiprocessing import Value
import sys
import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, Listbox, END
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, timedelta
import shutil


data_directory = "saved_files"
os.makedirs(data_directory, exist_ok=True)

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

def get_month_end_date():
    today = datetime.today()
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day = next_month - timedelta(days=next_month.day)
    return last_day.strftime("%y%m%d")

class PyQtTable(QDialog):
    def __init__(self, branch_name, file_to_edit=None):
        super().__init__()
        self.branch_name = branch_name
        self.file_to_edit = file_to_edit
        self.setWindowTitle(f'STATEMENT_3 - {self.branch_name}')
        self.setGeometry(200, 200, 1200, 300)

        self.layout = QVBoxLayout()
        self.createTable()
        self.layout.addWidget(self.tableWidget)

        self.save_button = QPushButton("SAVE")
        self.save_button.clicked.connect(self.saveTable)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        if self.file_to_edit:
            self.loadTableData(self.file_to_edit)

    def createTable(self):
        self.tableWidget = QTableWidget(7, 11)

        headers = ["TYPE", "SOCIETY_AC", "SOCIETY_AMOUNT", "LOCAL BODY_AC", "LOCAL BODY_AMOUNT","INDIVIDUALS_AC", "INDIVIDUALS_AMOUNT", "OTHERS_AC", "OTHERS_AMOUNT","TOTAL_AC", "TOTAL_AMOUNT"]
        row_labels = ["CA", "SB", "FIX", "REC", "OTH", "TOTAL"]

        for col, text in enumerate(headers):
            item = QTableWidgetItem(text)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.tableWidget.setItem(0, col, item)
            
        for row, label in enumerate(row_labels, start=1):
            item = QTableWidgetItem(label)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.tableWidget.setItem(row, 0, item)

        for row in range(1, 7):
            for col in range(1, 11):
                item = QTableWidgetItem("0.00")
                item.setTextAlignment(Qt.AlignRight)
                self.tableWidget.setItem(row, col, item)
        for row in range(1, 7):
            for col in range(1, 11):
                item = QTableWidgetItem()

        self.tableWidget.itemChanged.connect(self.calculateTotals)

    def validate_and_calculate(self, item):
        if not item:
           return

        row, col = item.row(), item.column()

        if row == 0 or col == 0 or row >= self.tableWidget.rowCount():
           return

        value = item.text().strip()
        try:
          float_value = float(value.replace(",", ""))
          item.setText(f"{float_value:.2f}")
        except ValueError:
          messagebox.showwarning("Invalid Input", "Only numeric values are allowed!")
          item.setText("0.00")

        self.calculateTotals()
  

    def calculateTotals(self):
        self.tableWidget.blockSignals(True)

        for row in range(1, 6):
            total_ac = sum(self.getCellValue(row, col) for col in [1, 3, 5, 7])
            total_amount = sum(self.getCellValue(row, col) for col in [2, 4, 6, 8])
            self.setCellValue(row, 9, total_ac)
            self.setCellValue(row, 10, total_amount)

        for col in range(1, 11):
            col_total = sum(self.getCellValue(row, col) for row in range(1, 6))
            self.setCellValue(6, col, col_total)

        self.tableWidget.blockSignals(False)

    def getCellValue(self, row, col):
        item = self.tableWidget.item(row, col)
        return float(item.text()) if item and item.text().replace(".", "").isdigit() else 0.0

    def setCellValue(self, row, col, value):
        item = QTableWidgetItem(f"{value:.2f}")
        item.setTextAlignment(Qt.AlignRight)
        self.tableWidget.setItem(row, col, item)

    def loadTableData(self, filepath):
        with open(filepath, 'r') as file:
            lines = file.readlines()

            data_lines = lines[4:-4]

            headers = ["TYPE", "SOCIETY_AC", "SOCIETY_AMOUNT", "LOCAL BODY_AC", "LOCAL BODY_AMOUNT","INDIVIDUALS_AC", "INDIVIDUALS_AMOUNT", "OTHERS_AC", "OTHERS_AMOUNT","TOTAL_AC", "TOTAL_AMOUNT"]
            row_labels = ["CA", "SB", "FIX", "REC", "OTH", "TOTAL"]
   
            self.tableWidget.clear()
            self.tableWidget.setRowCount(7)
            self.tableWidget.setColumnCount(11)

            for col, text in enumerate(headers):
                item = QTableWidgetItem(text)
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.tableWidget.setItem(0, col, item)

            for row, label in enumerate(row_labels, start=1):
                item = QTableWidgetItem(label)
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.tableWidget.setItem(row, 0, item)


            for row_index, line in enumerate(data_lines):
                values = line.strip().split('\t')
            for col_index, value in enumerate(values):
                return
            try:
                float_value = float(value.replace(',', ''))
                item = QTableWidgetItem(f"{float_value:.2f}")
                item.setTextAlignment(Qt.AlignRight)
            except ValueError:
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignLeft)

            float_value = float(value.replace(',', ''))
            item = QTableWidgetItem(f"{float_value:.2f}")


        self.tableWidget.setItem(row_index + 1, col_index, item)



    def save_as_pdf(self, filename):
        
        pdf_filepath = os.path.join(data_directory, filename + ".pdf")

        data = []

        headers = ["TYPE", "SOCIETY_AC", "SOCIETY_AMOUNT", "LOCAL BODY_AC", "LOCAL BODY_AMOUNT", "INDIVIDUALS_AC", "INDIVIDUALS_AMOUNT", "OTHERS_AC", "OTHERS_AMOUNT", "TOTAL_AC", "TOTAL_AMOUNT"]
        wrapped_headers = [Paragraph(h, getSampleStyleSheet()['Normal']) for h in headers]
        data.append(wrapped_headers)

        for row in range(1, self.tableWidget.rowCount()):
            row_data = [self.tableWidget.item(row, col).text() if self.tableWidget.item(row, col) else "" for col in range(self.tableWidget.columnCount())]
            data.append(row_data)

        pdf = SimpleDocTemplate(pdf_filepath, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
    

        current_datetime = datetime.now().strftime("%d-%m-%y %H:%M")
        reporting_date = Paragraph(f"<b>REPORTING DATE: {datetime.today()} TIME: {current_datetime}</b>", styles['Normal'])

        header = Paragraph("<b>THE BHARUCH DISTRICT CENTRAL CO-OPERATIVE BANK LTD.BHARUCH</b>" + f"\nSTATMENT3 AS ON: {get_month_end_date()}", styles['Title'])
        reporting_date = get_month_end_date()
        subheader = Paragraph(f"Branch Name/Code: {self.branch_name} ,\n\n Reporting Date/Time: {current_datetime}", styles['Normal'])
        

        table = Table(data, colWidths=[76] * 15)
        table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.black),('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),('TEXTCOLOR', (0, 0), (-1, 0), colors.black),('ALIGN', (0, 0), (-1, -1), 'CENTER'),('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 12), ('BOTTOMPADDING', (0, 0), (-1, -1), 15), ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.white])]))
        
        footer = Paragraph(f"<b>BRANCH MANAGER</b><br/><br/><br/><b>BRANCH NAME</b>", styles['Normal'])
        pdf.build([Spacer(1, 20), header, Spacer(1, 30),subheader, Spacer(1, 10), table, Spacer(1, 30), footer])

    
    def save_as_txt(self, filename):

      txt_filepath = os.path.join(data_directory, filename + ".txt")


      with open(txt_filepath, 'w') as txt_file:
        txt_file.write("="*60+"\n")
        txt_file.write("THE BHARUCH DISTRICT CENTRAL CO-OPERATIVE BANK LTD.BHARUCH" + f"\nSTATMENT3 AS ON: {get_month_end_date()}\n")
        txt_file.write("="*60+"\n")
        txt_file.write(f"BRANCH/CODE: {self.branch_name}\n\n")
        txt_file.write(f"DATE: {datetime.today()}\n\n\n")
        current_datetime = datetime.now().strftime("%d-%m-%y %H:%M")


        col_widths = [19] * 11
        headers = [self.tableWidget.item(0, col).text() for col in range(self.tableWidget.columnCount())]
        txt_file.write("|".join(h.center(col_widths[col]) for col, h in enumerate(headers)) + "\n")
        txt_file.write("." * 217 + "\n")

        for row in range(1, self.tableWidget.rowCount()):
            row_data = [self.tableWidget.item(row, col).text() if self.tableWidget.item(row,col)else "" for col in range(self.tableWidget.columnCount())]
            txt_file.write("|".join(val.center(col_widths[col]) for col, val in enumerate(row_data)) + '\n') 

        
        txt_file.write("="* 217 + "\n")
        txt_file.write("\n\nBRANCH MANAGER\n")
        txt_file.write("\nBRANCH NAME\n")


    def saveTable(self):
       if self.file_to_edit:
            filename = os.path.splitext(os.path.basename(self.file_to_edit))[0]
       else:
            filename = get_month_end_date() + f"_{branch_var.get()}"

            self.save_as_txt(filename)
            self.save_as_pdf(filename)
            messagebox.showinfo("save", f"Table saved as {filename}.pdf and {filename}.tx!")
            self.accept()


def view_saved_files():
    saved_window = tk.Toplevel(login_window)
    saved_window.title("View Saved Files")
    saved_window.geometry("600x400")

    listbox = Listbox(saved_window, width=70, height=10)
    listbox.pack(pady=10)

    for file in os.listdir(data_directory):
        listbox.insert(END, file)

    def download_file():
        selected = listbox.get(listbox.curselection())
        if selected:
                   source = os.path.join(data_directory, selected)
                   destination = filedialog.asksaveasfilename(initialfile=selected)
        if destination:
            shutil.copy(source, destination)
            messagebox.showinfo("Download", "File downloaded successfully!")

    def re_edit_file():
        selected = listbox.get(listbox.curselection())
        if selected.endswith(".txt"):
            filepath = os.path.join(data_directory, selected)
            filename = os.path.splitext(os.path.basename(filepath))[0]
            dialog = PyQtTable(branch_var.get(), filepath)
            if dialog.exec_():
                dialog.save_as_txt(filename)
                dialog.save_as_pdf(filename)
                messagebox.showinfo("File Edited Successfully", f"File re-saved as {filename}.pdf and {filename}.txt")
            
            float_value = float(Value.replace(',', ''))
            item = QTableWidgetItem(f"{float_value:.2f}")

    tk.Button(saved_window, text="Download", command=download_file).pack(pady=5)
    tk.Button(saved_window, text="Edit File", command=re_edit_file).pack(pady=5)

def logout(dashboard):
    dashboard.destroy()
    login_window.deiconify()

def login():
    username = entry_username.get()
    password = entry_password.get()
    branch = branch_var.get()
    
    if username == "user" and password == "1234" and branch:
        login_window.withdraw()
        open_dashboard(branch)
    else:
        messagebox.showerror("Login Failed", "Invalid credentials or branch selection")


def open_dashboard(branch):
    dashboard = tk.Toplevel(login_window)
    dashboard.title("Dashboard")
    dashboard.geometry("400x300")

    tk.Button(dashboard, text="SELECT STATEMENT LETTER", command=lambda: PyQtTable(branch).exec_()).pack(pady=10)
    tk.Button(dashboard, text="View Saved Files", command=view_saved_files).pack(pady=10)
    tk.Button(dashboard, text="Logout", command=lambda: logout(dashboard)).pack(pady=10)

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x250")

tk.Label(login_window, text="Username").pack()
entry_username = tk.Entry(login_window)
entry_username.pack()

tk.Label(login_window, text="Password").pack()
entry_password = tk.Entry(login_window, show="*")
entry_password.pack()

tk.Label(login_window, text="Select Branch").pack()
branch_var = tk.StringVar()
branch_dropdown = ttk.Combobox(login_window, textvariable=branch_var)
branch_dropdown['values'] = ["HO","Branch1", "Branch2"]
branch_dropdown.pack()

tk.Button(login_window, text="Login", command=login).pack(pady=10)

login_window.mainloop()


