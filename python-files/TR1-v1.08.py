import sys
import json
import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QRadialGradient, QFont, QPen


def adjust_color_brightness(color: QColor, factor: float) -> QColor:
    """Hellt oder dunkelt eine QColor um den Faktor (0-1) auf."""
    h, s, v, a = color.getHsvF()
    v = max(0, min(1, v * factor))
    return QColor.fromHsvF(h, s, v, a)


class GradientButton(QPushButton):
    def __init__(self, text, base_color, active_color=None, outline_color=None, smaller_height=False, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.base_color = base_color
        self.active_color = active_color or adjust_color_brightness(base_color, 0.8)
        self.outline_color = outline_color
        self.active = False
        self.smaller_height = smaller_height

        self.setFont(QFont('Arial', 10, QFont.Bold))
        self.setMinimumHeight(30 if smaller_height else 40)
        self.setMaximumHeight(30 if smaller_height else 40)
        self.setStyleSheet("border-radius: 10px;")
        self.pressed_flag = False

    def set_active(self, active: bool):
        self.active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        center = QPointF(rect.width() / 2, rect.height() / 2)
        radius = max(rect.width(), rect.height())

        if self.active:
            # Heller blauer Gradient für aktive Buttons (hellblau von vorher)
            gradient = QRadialGradient(center, radius)
            base = QColor("#87CEFA")  # hellblau
            darker = adjust_color_brightness(base, 0.8)
            gradient.setColorAt(0, base)
            gradient.setColorAt(1, darker)
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, 10, 10)
        else:
            if self.outline_color:
                # Transparenter Hintergrund, nur Rand in outline_color
                painter.setBrush(Qt.transparent)
                pen = QPen(self.outline_color, 2)
                painter.setPen(pen)
                painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 10, 10)
            else:
                # Normaler radialer Gradient
                gradient = QRadialGradient(center, radius)
                gradient.setColorAt(0, self.base_color)
                gradient.setColorAt(1, self.active_color)
                painter.setBrush(QBrush(gradient))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect, 10, 10)

        # Text zeichnen
        painter.setPen(Qt.white if not self.outline_color else self.outline_color)
        painter.setFont(self.font())
        painter.drawText(rect, Qt.AlignCenter, self.text())

    def mousePressEvent(self, event):
        self.pressed_flag = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.pressed_flag = False
        self.update()
        super().mouseReleaseEvent(event)


class TimeTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arbeitszeiterfassung")
        self.resize(400, 700)

        self.bg_color = QColor("#282D37")
        self.init_colors()
        self.projects = {}
        self.daily_times = {}
        self.time_started = {}
        self.project_buttons = {}
        self.project_adjust_layouts = {}
        self.total_time_started = None
        self.total_duration = 0
        self.total_seconds = 0

        self.setup_ui()
        self.load_data()
        self.update_time_display()
        self.start_timer()

    def init_colors(self):
        self.base_button_color = QColor("#131821")
        self.active_button_color = adjust_color_brightness(QColor("#87CEFA"), 1)  # hellblau
        self.total_button_color = QColor("#FF2600")
        self.total_button_active_color = adjust_color_brightness(self.total_button_color, 0.8)

        self.add5_outline = QColor("#00AA00")  # grün Rand
        self.sub5_outline = QColor("#CC0000")  # rot Rand

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.setStyleSheet(f"background-color: {self.bg_color.name()}; color: #F0F3F5; font-family: Arial;")

        # Projektname Eingabe
        self.project_entry = QLineEdit()
        self.project_entry.setPlaceholderText("Projektname eingeben")
        self.project_entry.setStyleSheet(f"background-color: #646973; color: #F0F3F5; border-radius: 5px; padding: 5px;")
        self.main_layout.addWidget(self.project_entry)

        # Projekt hinzufügen Button
        self.add_project_btn = GradientButton("Projekt hinzufügen", self.base_button_color)
        self.add_project_btn.clicked.connect(self.add_project)
        self.main_layout.addWidget(self.add_project_btn)

        # Gesamtarbeitszeit Button
        self.total_button = GradientButton("Gesamtarbeitszeit 00:00:00", self.total_button_color)
        self.total_button.clicked.connect(self.toggle_total_tracking)
        self.main_layout.addWidget(self.total_button)

        # +5min und -5min Buttons (kleiner, nur Rand)
        adj_layout = QHBoxLayout()
        self.add_5min_btn = GradientButton("+5 Minuten", QColor(0, 0, 0, 0), outline_color=self.add5_outline, smaller_height=True)
        self.add_5min_btn.clicked.connect(lambda: self.adjust_total_time(300))
        adj_layout.addWidget(self.add_5min_btn)

        self.sub_5min_btn = GradientButton("-5 Minuten", QColor(0, 0, 0, 0), outline_color=self.sub5_outline, smaller_height=True)
        self.sub_5min_btn.clicked.connect(lambda: self.adjust_total_time(-300))
        adj_layout.addWidget(self.sub_5min_btn)

        self.main_layout.addLayout(adj_layout)

        # Export Button
        self.export_btn = GradientButton("Exportiere Bericht nach Excel", self.base_button_color)
        self.export_btn.clicked.connect(self.export_to_excel)
        self.main_layout.addWidget(self.export_btn)

        # Datenbank löschen Button
        self.delete_btn = GradientButton("Datenbank löschen", self.base_button_color)
        self.delete_btn.clicked.connect(self.confirm_delete)
        self.main_layout.addWidget(self.delete_btn)

        # Berichtfeld
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setStyleSheet("background-color: #646973; color: #F0F3F5; border-radius: 10px; padding: 10px;")
        self.report_text.setFixedHeight(200)
        self.main_layout.addWidget(self.report_text)

        # Bereich für Projekt-Buttons **unter** dem Berichtfeld
        self.projects_layout = QVBoxLayout()
        self.main_layout.addLayout(self.projects_layout)

    def add_project(self):
        project_name = self.project_entry.text().strip()
        if not project_name:
            return
        if project_name in self.project_buttons:
            QMessageBox.warning(self, "Warnung", "Projekt existiert bereits!")
            return

        self.projects.setdefault(project_name, 0)
        self.daily_times.setdefault(project_name, {})
        self.time_started[project_name] = None

        self.create_project_button(project_name)
        self.project_entry.clear()
        self.save_data()

    def create_project_button(self, project_name):
        row_layout = QHBoxLayout()

       # Hauptbutton für Projekt
        btn = GradientButton(project_name, self.base_button_color)
        btn.clicked.connect(lambda checked, pn=project_name: self.toggle_tracking(pn))
        self.project_buttons[project_name] = btn
        row_layout.addWidget(btn, stretch=2)

        # +5m Button
        add_btn = GradientButton("+5m", QColor(0, 0, 0, 0), outline_color=self.add5_outline, smaller_height=True)
        add_btn.clicked.connect(lambda _, pn=project_name: self.adjust_project_time(pn, 300))
        row_layout.addWidget(add_btn, stretch=1)

        # -5m Button
        sub_btn = GradientButton("-5m", QColor(0, 0, 0, 0), outline_color=self.sub5_outline, smaller_height=True)
        sub_btn.clicked.connect(lambda _, pn=project_name: self.adjust_project_time(pn, -300))
        row_layout.addWidget(sub_btn, stretch=1)

        self.projects_layout.addLayout(row_layout)
        self.project_adjust_layouts[project_name] = row_layout

        # Speichere Layout zur späteren Entfernung
        self.project_adjust_layouts[project_name] = row_layout

    def toggle_tracking(self, project_name):
        if self.time_started.get(project_name):
            self.stop_project(project_name)
        else:
            # Stoppe alle anderen Projekte
            for pn, start_time in self.time_started.items():
                if start_time:
                    self.stop_project(pn)
            self.start_project(project_name)

            # Starte Gesamtzeit, falls nicht aktiv
            if not self.total_time_started:
                self.start_total_tracking()
        self.save_data()

    def start_project(self, project_name):
        self.time_started[project_name] = datetime.now()
        btn = self.project_buttons[project_name]
        btn.set_active(True)

    def stop_project(self, project_name):
        btn = self.project_buttons.get(project_name)
        if not btn:
            return
        time_ended = datetime.now()
        duration = (time_ended - self.time_started[project_name]).total_seconds()
        self.projects[project_name] += duration
        today = datetime.now().date().isoformat()
        self.daily_times[project_name][today] = self.daily_times[project_name].get(today, 0) + duration
        self.time_started[project_name] = None
        btn.set_active(False)

    def start_total_tracking(self):
        self.total_time_started = datetime.now()
        self.total_button.set_active(True)

    def stop_total_tracking(self):
        if not self.total_time_started:
            return
        time_ended = datetime.now()
        duration = (time_ended - self.total_time_started).total_seconds()
        self.total_seconds += duration

        # Stoppe alle aktiven Projekte
        for pn, start_time in self.time_started.items():
            if start_time:
                self.stop_project(pn)

        self.total_duration += self.total_seconds
        self.total_seconds = 0
        self.total_time_started = None
        self.total_button.set_active(False)
        self.save_data()

    def toggle_total_tracking(self):
        if self.total_time_started:
            self.stop_total_tracking()
        else:
            self.start_total_tracking()

    def update_time_display(self):
        # Update Gesamtarbeitszeit Button
        if self.total_time_started:
            elapsed = (datetime.now() - self.total_time_started).total_seconds() + self.total_seconds + self.total_duration
        else:
            elapsed = self.total_duration

        hrs, rem = divmod(elapsed, 3600)
        mins, secs = divmod(rem, 60)
        self.total_button.setText(f"Gesamtarbeitszeit {int(hrs):02}:{int(mins):02}:{int(secs):02}")

        # Update Projekt-Buttons – nur aktuelle Laufzeit anzeigen
        for pn, btn in self.project_buttons.items():
            if self.time_started.get(pn):
                elapsed_proj = (datetime.now() - self.time_started[pn]).total_seconds()
                h, r = divmod(elapsed_proj, 3600)
                m, s = divmod(r, 60)
                btn.setText(f"{pn} {int(h):02}:{int(m):02}:{int(s):02}")
            else:
                btn.setText(pn)

        # Bericht aktualisieren (weiterhin aufaddierte Zeiten)
        report = "Gesamtübersicht:\n"
        for proj, seconds in self.projects.items():
            h, r = divmod(seconds, 3600)
            m, s = divmod(r, 60)
            report += f"{proj}: {int(h)} Stunden, {int(m)} Minuten, {int(s)} Sekunden\n"

        total_h, total_r = divmod(self.total_duration, 3600)
        total_m, total_s = divmod(total_r, 60)
        report += f"Gesamtarbeitszeit: {int(total_h)} Stunden, {int(total_m)} Minuten, {int(total_s)} Sekunden\n"
        self.report_text.setPlainText(report)

    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_display)
        self.timer.start(1000)

    def adjust_total_time(self, seconds: int):
        # Gesamtzeit + / - anpassen
        new_total = self.total_duration + seconds
        if new_total < 0:
            new_total = 0
        self.total_duration = new_total

        # Update database und Anzeige, ohne laufende Zeiten zu beeinflussen
        self.save_data()
        self.update_time_display()

    def adjust_project_time(self, project_name: str, seconds: int):
        new_time = self.projects.get(project_name, 0) + seconds
        if new_time < 0:
            new_time = 0
        self.projects[project_name] = new_time

        today = datetime.now().date().isoformat()
        self.daily_times.setdefault(project_name, {})
        self.daily_times[project_name][today] = self.daily_times[project_name].get(today, 0) + seconds
        if self.daily_times[project_name][today] < 0:
            self.daily_times[project_name][today] = 0

        self.save_data()
        self.update_time_display()

    def export_to_excel(self):
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Projektdauer"
        ws.append(["Projekt", "Datum", "Stunden", "Minuten", "Sekunden"])

        for project, daily_data in self.daily_times.items():
            for day, seconds in daily_data.items():
                h, r = divmod(seconds, 3600)
                m, s = divmod(r, 60)
                ws.append([project, day, int(h), int(m), int(s)])

        total_h, total_r = divmod(self.total_duration, 3600)
        total_m, total_s = divmod(total_r, 60)
        ws.append(["Gesamtarbeitszeit", "", int(total_h), int(total_m), int(total_s)])

        file_path, _ = QFileDialog.getSaveFileName(self, "Datei speichern", "", "Excel Dateien (*.xlsx)")
        if file_path:
            wb.save(file_path)

    def confirm_delete(self):
        reply = QMessageBox.question(self, "Bestätigung", "Möchten Sie wirklich die gesamte Datenbank löschen?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            reply2 = QMessageBox.question(self, "Sicherheitsabfrage", "Sind Sie absolut sicher? Alle Daten gehen verloren!",
                                          QMessageBox.Yes | QMessageBox.No)
            if reply2 == QMessageBox.Yes:
                self.delete_database()

    def delete_database(self):
        self.projects = {}
        self.daily_times = {}
        self.time_started = {}
        self.total_duration = 0
        self.total_seconds = 0
        self.total_time_started = None

        # Projektbuttons löschen
        for btn in self.project_buttons.values():
            btn.deleteLater()
        self.project_buttons.clear()

        # +5/-5min Layouts löschen
        for layout in self.project_adjust_layouts.values():
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.project_adjust_layouts.clear()

        self.report_text.clear()
        if os.path.exists("projects.json"):
            os.remove("projects.json")

    def load_data(self):
        if not os.path.exists("projects.json"):
            return
        try:
            with open("projects.json", "r") as f:
                data = json.load(f)
                self.projects = {k: float(v) for k, v in data.get('projects', {}).items()}
                self.daily_times = data.get('daily_times', {})
                self.total_duration = data.get('total_duration', 0)
                self.total_seconds = 0
                self.total_time_started = None
                self.time_started = {k: None for k in self.projects.keys()}

                for project in self.projects.keys():
                    self.create_project_button(project)
        except Exception as e:
            print(f"Fehler beim Laden der Daten: {e}")

    def save_data(self):
        data = {
            'projects': self.projects,
            'daily_times': self.daily_times,
            'total_duration': self.total_duration
        }
        with open("projects.json", "w") as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec())
