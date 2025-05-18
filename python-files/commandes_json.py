import sys
import json
import re
import xlsxwriter
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QMessageBox

class JSONExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Extractor")
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()

        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("Paste your JSON code here...")
        layout.addWidget(self.input_edit)

        self.extract_btn = QPushButton("Extract & Print")
        self.extract_btn.clicked.connect(self.extract_json)
        layout.addWidget(self.extract_btn)

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText("Extracted data will appear here.")
        layout.addWidget(self.output_edit)
        
        self.export_btn = QPushButton("Exporter en Excel")
        self.export_btn.clicked.connect(self.export_to_excel)
        layout.addWidget(self.export_btn)
        self.setLayout(layout)

    def extract_json(self):
        text = self.input_edit.toPlainText().strip()
        try:
            objects = re.findall(r'\{.*?\}', text, re.DOTALL)
            data = []
            for obj_str in objects:
                try:
                    fixed_obj_str = re.sub(r"(\w+):", r'"\1":', obj_str)
                    data.append(json.loads(fixed_obj_str))
                except Exception:
                    try:
                        data.append(json.loads(obj_str))
                    except Exception:
                        continue
            if not data:
                raise Exception("No valid JSON objects found.")
            output_lines = []
            for obj in data:
                name = obj.get("name", "")
                phone = obj.get("phone", "")
                wilaya = obj.get("wilaya", "")
                baladia = obj.get("baladia", "")
                output_lines.append(f"Name: {name} | Phone: {phone} | Wilaya: {wilaya} | Baladia: {baladia}")
            self.output_edit.setPlainText("\n".join(output_lines))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Invalid JSON: {e}")
    def export_to_excel(self):
            # Récupère les lignes extraites
        lines = self.output_edit.toPlainText().splitlines()
        if not lines:
            QMessageBox.warning(self, "Aucune donnée", "Aucune donnée à exporter.")
            return
    
        # Demande où sauvegarder le fichier
        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter en Excel", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
    
        # Création du fichier Excel
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet("Commandes")
    
        # En-têtes
        headers = ["Name", "Phone", "Wilaya", "Baladia"]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
    
        # Données
        for row, line in enumerate(lines, start=1):
            # Découpe la ligne selon le format affiché
            parts = [part.split(":", 1)[1].strip() if ":" in part else "" for part in line.split("|")]
            for col, value in enumerate(parts):
                worksheet.write(row, col, value)
    
        workbook.close()
        QMessageBox.information(self, "Succès", "Exportation terminée !")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JSONExtractor()
    window.show()
    sys.exit(app.exec_())