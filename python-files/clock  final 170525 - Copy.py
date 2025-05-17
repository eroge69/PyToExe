import sys
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF, QTime, QUrl # Import QUrl
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QColorDialog, QCheckBox, QTimeEdit, QDialog, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox, QComboBox, QGroupBox, QLineEdit # Import QLineEdit
import math
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent # Import QMediaPlayer, QMediaContent
import sys # Ensure sys is imported for stderr
import winsound # Import winsound for playing system sounds

# Define the SetAlarmDialog class
class SetAlarmDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent # The ConcentricClock instance
        self.setWindowTitle("Set Alarm")
        self.setModal(True)
        self.setFixedSize(350, 300) # Adjust size to accommodate new field

        layout = QVBoxLayout()

        # Time picker
        time_label = QLabel("Select alarm time:")
        layout.addWidget(time_label)
        self.time_edit = QTimeEdit() # Use self.time_edit
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setFont(QFont("Arial", 20))
        self.time_edit.setButtonSymbols(QTimeEdit.UpDownArrows)
        self.time_edit.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_edit)

        # Alarm Topic input
        topic_label = QLabel("Alarm Topic/Message:")
        layout.addWidget(topic_label)
        self.topic_edit = QLineEdit() # Add QLineEdit for topic
        self.topic_edit.setPlaceholderText("e.g., Take a break, Meeting starts")
        # Set initial text if a topic was previously set
        if self.parent.alarm_topic:
            self.topic_edit.setText(self.parent.alarm_topic)
        layout.addWidget(self.topic_edit)


        # Sound selection group
        sound_group_box = QGroupBox("Alarm Sound")
        sound_layout = QVBoxLayout()

        self.sound_status_label = QLabel("Current: SystemCalendarReminder") # Initial status label
        sound_layout.addWidget(self.sound_status_label)

        calendar_btn = QPushButton("Use Calendar Reminder")
        calendar_btn.clicked.connect(self.use_calendar_reminder)
        sound_layout.addWidget(calendar_btn)

        browse_btn = QPushButton("Browse for Sound File (.wav, .mp3)")
        browse_btn.clicked.connect(self.browse_sound_file)
        sound_layout.addWidget(browse_btn)

        sound_group_box.setLayout(sound_layout)
        layout.addWidget(sound_group_box)

        # OK/Cancel buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Connect buttons
        ok_btn.clicked.connect(self.accept_alarm)
        cancel_btn.clicked.connect(self.reject) # Use reject for cancel

        # Initialize dialog state based on parent's current settings
        if self.parent.alarm_sound_path:
            self.sound_status_label.setText(f"Current: {self.parent.alarm_sound_path}")
        elif self.parent.alarm_sound_alias:
             self.sound_status_label.setText(f"Current: {self.parent.alarm_sound_alias}")
        else:
             # Default state if neither is set
             self.parent.alarm_sound_alias = "SystemCalendarReminder"
             self.parent.alarm_sound_path = None
             self.sound_status_label.setText("Current: SystemCalendarReminder")


    def use_calendar_reminder(self):
        self.parent.alarm_sound_alias = "SystemCalendarReminder"
        self.parent.alarm_sound_path = None
        self.sound_status_label.setText("Current: SystemCalendarReminder")

    def browse_sound_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Alarm Sound", "", "Audio Files (*.wav *.mp3);;All Files (*)"
        )
        if file_path:
            self.parent.alarm_sound_path = file_path
            self.parent.alarm_sound_alias = None # Clear alias if file is chosen
            self.sound_status_label.setText(f"Current: {file_path}")

    def accept_alarm(self):
        # Save the selected time and topic to the parent
        self.parent.alarm_time = self.time_edit.time()
        self.parent.alarm_topic = self.topic_edit.text() # Save the topic text
        self.parent.alarm_set = True # Set alarm_set to True when OK is clicked
        self.accept() # Close the dialog

# End of SetAlarmDialog class

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setFixedSize(300, 400)
        self.parent = parent

        layout = QVBoxLayout()

        # Theme toggle
        self.theme_btn = QPushButton(self.theme_btn_text())
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)

        # Analog toggle
        self.analog_btn = QPushButton(self.analog_btn_text())
        self.analog_btn.clicked.connect(self.toggle_analog)
        layout.addWidget(self.analog_btn)

        # Digital toggle
        self.digital_btn = QPushButton(self.digital_btn_text())
        self.digital_btn.clicked.connect(self.toggle_digital)
        layout.addWidget(self.digital_btn)

        # Color pickers
        self.color_btn = QPushButton("Hand Colors")
        self.color_btn.clicked.connect(self.pick_colors)
        layout.addWidget(self.color_btn)

        # Alarm feature
        self.alarm_btn = QPushButton("Set Alarm")
        self.alarm_btn.clicked.connect(parent.set_alarm) # Connect to parent's set_alarm
        layout.addWidget(self.alarm_btn)

        # Remove the Browse sound button from here - it's now in the SetAlarmDialog
        # self.browse_sound_btn = QPushButton("Browse Sound")
        # self.browse_sound_btn.clicked.connect(parent.browse_sound)
        # layout.addWidget(self.browse_sound_btn)

        # 12/24-hour format
        self.time24_btn = QPushButton(self.time24_btn_text())
        self.time24_btn.clicked.connect(self.toggle_time24)
        layout.addWidget(self.time24_btn)

        # Date format option
        self.date_fmt_btn = QPushButton(self.date_fmt_btn_text())
        self.date_fmt_btn.clicked.connect(self.toggle_datefmt)
        layout.addWidget(self.date_fmt_btn)

        self.setLayout(layout)
        self.update_widget_styles()

    # Helper methods for button text
    def theme_btn_text(self):
        return "Theme: Dark" if self.parent.dark_theme else "Theme: Light"
    def analog_btn_text(self):
        return "Analog: ON" if self.parent.show_analog else "Analog: OFF"
    def digital_btn_text(self):
        return "Digital: ON" if self.parent.show_digital else "Digital: OFF"
    def time24_btn_text(self):
        return "24-Hour: ON" if self.parent.time24_chk.isChecked() else "24-Hour: OFF"
    def date_fmt_btn_text(self):
        return "Date: DD-MM-YYYY" if self.parent.date_fmt_chk.isChecked() else "Date: Full"

    # Button slot methods
    def toggle_theme(self):
        self.parent.dark_theme = not self.parent.dark_theme
        self.theme_btn.setText(self.theme_btn_text())
        self.parent.update_widget_styles()
        self.update_widget_styles()
        self.parent.update()

    def toggle_analog(self):
        self.parent.show_analog = not self.parent.show_analog
        self.analog_btn.setText(self.analog_btn_text())
        self.parent.update()

    def toggle_digital(self):
        self.parent.show_digital = not self.parent.show_digital
        self.digital_btn.setText(self.digital_btn_text())
        self.parent.update()

    def pick_colors(self):
        self.parent.pick_colors()
        self.parent.update()

    def toggle_time24(self):
        self.parent.time24_chk.setChecked(not self.parent.time24_chk.isChecked())
        self.time24_btn.setText(self.time24_btn_text())
        self.parent.update()

    def toggle_datefmt(self):
        self.parent.date_fmt_chk.setChecked(not self.parent.date_fmt_chk.isChecked())
        self.date_fmt_btn.setText(self.date_fmt_btn_text())
        self.parent.update()

    def update_widget_styles(self):
        if self.parent.dark_theme:
            btn_style = """
                QPushButton {
                    background-color: #222;
                    color: white;
                    border-radius: 6px;
                    border: 1px solid #555;
                    padding: 10px 0px;
                    font-size: 16px;
                    min-width: 160px;
                }
                QPushButton:hover {
                    background-color: #444;
                    border: 1.5px solid #1E90FF;
                }
            """
            self.setStyleSheet("background-color: #222;")
        else:
            btn_style = """
                QPushButton {
                    background-color: #fff;
                    color: black;
                    border-radius: 6px;
                    border: 1px solid #aaa;
                    padding: 10px 0px;
                    font-size: 16px;
                    min-width: 160px;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                    border: 1.5px solid #1E90FF;
                }
            """
            self.setStyleSheet("background-color: #fff;")
        self.theme_btn.setStyleSheet(btn_style)
        self.analog_btn.setStyleSheet(btn_style)
        self.digital_btn.setStyleSheet(btn_style)
        self.color_btn.setStyleSheet(btn_style)
        self.alarm_btn.setStyleSheet(btn_style)
        self.time24_btn.setStyleSheet(btn_style)
        self.date_fmt_btn.setStyleSheet(btn_style)

class ConcentricClock(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Concentric Analog Clock')
        self.resize(600, 700)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 60)  # 60 FPS

        self.setMouseTracking(True)

        # Theme and display options
        self.dark_theme = True
        self.show_analog = True
        self.show_digital = True

        # Accent colors
        self.hour_color = '#1E90FF'
        self.minute_color = '#00FA9A'
        self.second_color = '#FF4500'

        # Initialize alarm-related attributes
        self.alarm_set = False
        self.alarm_time = None
        self.alarm_topic = "" # Initialize alarm topic
        self.alarm_sound_alias = "SystemCalendarReminder" # Default to Calendar Reminder
        self.alarm_sound_path = None # Initialize custom path to None
        self.media_player = None # Keep for QMediaPlayer

        # Add About button
        self.about_btn = QPushButton("About", self)
        self.about_btn.setFixedSize(80, 28)
        self.about_btn.setStyleSheet("QPushButton { background-color: #222; color: white; border-radius: 6px; }")
        self.about_btn.setToolTip("Designed and developed by Creativebuzz Media Production\ncreativebuzzindia@gmail.com")

        # Add Settings button
        self.settings_btn = QPushButton("Settings", self)
        self.settings_btn.setFixedSize(80, 28)
        self.settings_btn.setStyleSheet("QPushButton { background-color: #222; color: white; border-radius: 6px; }")
        self.settings_btn.clicked.connect(self.open_settings)

        # Hidden checkboxes for settings dialog to sync state
        self.time24_chk = QCheckBox()
        self.time24_chk.setChecked(False)
        self.date_fmt_chk = QCheckBox()
        self.date_fmt_chk.setChecked(False)

        self.update_widget_styles()

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec_()

    def update_widget_styles(self):
        if self.dark_theme:
            btn_style = "QPushButton { background-color: #222; color: white; border-radius: 6px; }"
        else:
            btn_style = "QPushButton { background-color: #fff; color: black; border-radius: 6px; border: 1px solid #aaa; }"
        self.about_btn.setStyleSheet(btn_style)
        self.settings_btn.setStyleSheet(btn_style)

    def resizeEvent(self, event):
        # Place About and Settings buttons side by side at the bottom center
        spacing = 10
        total_width = self.about_btn.width() + self.settings_btn.width() + spacing
        start_x = (self.width() - total_width) // 2
        btn_y = self.height() - self.about_btn.height() - 15
        self.about_btn.move(start_x, btn_y)
        self.settings_btn.move(start_x + self.about_btn.width() + spacing, btn_y)
        super().resizeEvent(event)

    def paintEvent(self, event):
        from datetime import datetime
        dt = datetime.now()
        hour = dt.hour % 12 + dt.minute / 60.0
        minute = dt.minute + dt.second / 60.0
        second = dt.second + dt.microsecond / 1_000_000.0

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fill background
        if self.dark_theme:
            painter.fillRect(self.rect(), Qt.black)
            fg_color = Qt.white
        else:
            painter.fillRect(self.rect(), Qt.white)
            fg_color = Qt.black

        # Display "Alarm is set" message if alarm is active
        if self.alarm_set and self.alarm_time:
            alarm_font = QFont('SansSerif', 10)
            painter.setFont(alarm_font)
            painter.setPen(QColor("red"))
            alarm_text = "Alarm is set"
            text_width = painter.fontMetrics().width(alarm_text)
            painter.drawText(QPointF(self.width() - text_width - 10, 20), alarm_text)
            # Reset pen for other drawings if necessary, though fg_color is set later
            # For safety, you might reset it here or ensure all subsequent drawings set their own pen.

        w, h = self.width(), self.height()
        cx, cy = w / 2, h * 0.4
        painter.translate(cx, cy)
        R = min(w, h*0.8) / 2 * 0.85

        # draw rings of ticks
        def draw_ticks(radius, light_color, dark_color):
            pen_light = QPen(QColor(light_color), 2)
            pen_dark = QPen(QColor(dark_color), 1)
            font = QFont('SansSerif', max(8, int(radius*0.03)))
            painter.setFont(font)
            for i in range(60):
                angle = 2 * math.pi * i / 60 - math.pi/2
                x1 = radius * math.cos(angle)
                y1 = radius * math.sin(angle)
                length = 14 if i % 5 == 0 else 7
                x2 = (radius - length) * math.cos(angle)
                y2 = (radius - length) * math.sin(angle)
                painter.setPen(pen_light if i % 5 == 0 else pen_dark)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
                if i % 5 == 0:
                    label = f"{(i*5)%60:02d}"
                    lx = (radius - length - radius*0.1) * math.cos(angle)
                    ly = (radius - length - radius*0.1) * math.sin(angle)
                    painter.drawText(QPointF(lx-10, ly+10), label)

        if self.show_analog:
            draw_ticks(R, '#AAA' if self.dark_theme else '#444', '#888' if self.dark_theme else '#BBB')
            draw_ticks(R*0.7, '#888' if self.dark_theme else '#BBB', '#666' if self.dark_theme else '#DDD')
            draw_ticks(R*0.45, '#666' if self.dark_theme else '#DDD', '#444' if self.dark_theme else '#EEE')

            # draw hands
            def draw_hand(angle, length, width, color):
                painter.save()
                painter.rotate(angle)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(color)))
                from PyQt5.QtGui import QPainterPath
                path = QPainterPath()
                path.moveTo(-width/2, 0)
                path.lineTo(-width/2, -length)
                path.lineTo(width/2, -length)
                path.lineTo(width/2, 0)
                path.closeSubpath()
                painter.drawPath(path)
                painter.restore()

            draw_hand((hour/12)*360, R*0.45, 12, self.hour_color)
            draw_hand((minute/60)*360, R*0.60, 8, self.minute_color)
            draw_hand((second/60)*360, R*0.85, 4, self.second_color)

            # center dot
            painter.setBrush(QBrush(fg_color))
            painter.drawEllipse(QPointF(0,0), 6, 6)

        # digital time 12/24-hour
        if self.show_digital:
            if self.time24_chk.isChecked():
                hour_display = dt.hour
                ampm = ""
            else:
                ampm = 'AM' if dt.hour < 12 else 'PM'
                hour_display = dt.hour % 12 or 12
            time_str = f"{hour_display:02d} : {dt.minute:02d} : {dt.second:02d} {ampm}"
            font_time = QFont('SansSerif', 30, QFont.Bold)
            painter.setFont(font_time)
            painter.setPen(fg_color)
            time_rect = painter.boundingRect(self.rect(), Qt.AlignCenter, time_str)
            painter.drawText(QPointF(-time_rect.width()/2, R + 60), time_str)

            # date
            if self.date_fmt_chk.isChecked():
                date_str = dt.strftime("%d-%m-%Y")  # <-- Changed here
            else:
                days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
                months = [ 'January','February','March','April','May','June','July','August',
                        'September','October','November','December' ]
                date_str = f"{days[dt.weekday()]}, {months[dt.month-1]} {dt.day}, {dt.year}"
            font_date = QFont('SansSerif', 18)
            painter.setFont(font_date)
            date_rect = painter.boundingRect(self.rect(), Qt.AlignCenter, date_str)
            painter.drawText(QPointF(-date_rect.width()/2, R + 95), date_str)

        painter.end()

        # Add this line to check alarm every frame
        self.check_alarm(dt)

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.update()

    def toggle_analog(self, state):
        self.show_analog = bool(state)
        self.update()

    def toggle_digital(self, state):
        self.show_digital = bool(state)
        self.update()

    def pick_colors(self):
        color = QColorDialog.getColor(QColor(self.hour_color), self, "Pick Hour Hand Color")
        if color.isValid():
            self.hour_color = color.name()
        color = QColorDialog.getColor(QColor(self.minute_color), self, "Pick Minute Hand Color")
        if color.isValid():
            self.minute_color = color.name()
        color = QColorDialog.getColor(QColor(self.second_color), self, "Pick Second Hand Color")
        if color.isValid():
            self.second_color = color.name()
        self.update()

    def set_alarm(self):
        # Use the new SetAlarmDialog class
        dialog = SetAlarmDialog(self)
        dialog.exec_()
        # The dialog updates self.alarm_time, self.alarm_sound_alias, self.alarm_sound_path, and self.alarm_set directly

    # Removed: This method is now handled within the SetAlarmDialog class
    # def browse_sound(self):
    #     file_path, _ = QFileDialog.getOpenFileName(
    #         self, "Select Alarm Sound", "", "Audio Files (*.wav *.mp3)"
    #     )
    #     if file_path:
    #         self.parent.alarm_sound_path = file_path

    def check_alarm(self, dt):
        if self.alarm_set and self.alarm_time:
            now = QTime(dt.hour, dt.minute, dt.second)
            # Compare only hour, minute, and second
            if now.hour() == self.alarm_time.hour() and \
               now.minute() == self.alarm_time.minute() and \
               now.second() == self.alarm_time.second():
                self.alarm_set = False # Alarm triggered, so unset it
                self.play_alarm_sound()
                self.show_stop_alarm_dialog()

    def show_stop_alarm_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Alarm")
        layout = QVBoxLayout()
        # Display the alarm topic if set, otherwise a default message
        alarm_message = self.alarm_topic if self.alarm_topic else "Alarm time reached!"
        label = QLabel(alarm_message) # Use the topic/message here
        label.setFont(QFont("SansSerif", 12)) # Make the message slightly larger
        label.setAlignment(Qt.AlignCenter) # Center the message
        layout.addWidget(label)
        stop_btn = QPushButton("Stop Alarm Sound")
        layout.addWidget(stop_btn)
        dialog.setLayout(layout)

        def stop_alarm():
            self.stop_alarm_sound()
            dialog.accept()

        stop_btn.clicked.connect(stop_alarm)
        dialog.exec_() # Use exec_() to make it modal

    def stop_alarm_sound(self):
        # Stop winsound playback
        try:
            import winsound
            winsound.PlaySound(None, winsound.SND_PURGE) # Stop any currently playing winsound
        except Exception:
            pass
        # Stop mp3 sound (QMediaPlayer)
        if hasattr(self, 'media_player') and self.media_player and self.media_player.state() == QMediaPlayer.PlayingState:
             self.media_player.stop()
             # Optional: Release the media player if not needed anymore
             # self.media_player.setMedia(QMediaContent())
             # self.media_player = None


    def play_alarm_sound(self):
        # Play the selected sound (file or alias) in a loop
        if self.alarm_sound_path:
            # Play custom file using QMediaPlayer
            try:
                if not hasattr(self, 'media_player') or self.media_player is None:
                    self.media_player = QMediaPlayer()
                url = QUrl.fromLocalFile(self.alarm_sound_path)
                self.media_player.setMedia(QMediaContent(url))
                self.media_player.setVolume(100) # Set volume
                self.media_player.setLoopCount(QMediaPlayer.Infinite) # Loop indefinitely
                self.media_player.play()
            except Exception as e:
                 print(f"Error playing custom sound file '{self.alarm_sound_path}': {e}", file=sys.stderr)
                 # Fallback to default if custom file fails
                 self.play_windows_sound_alias("SystemAsterisk", loop=True)
        elif self.alarm_sound_alias:
            # Play winsound alias, looping
            self.play_windows_sound_alias(self.alarm_sound_alias, loop=True)
        else:
            # Fallback if somehow neither is set (shouldn't happen with default init)
            self.play_windows_sound_alias("SystemAsterisk", loop=True)


    # Renamed and modified the method to play a specific alias with optional looping
    def play_windows_sound_alias(self, alias="SystemAsterisk", loop=False):
        try:
            import winsound
            flags = winsound.SND_ALIAS | winsound.SND_ASYNC
            if loop:
                flags |= winsound.SND_LOOP
            winsound.PlaySound(alias, flags)
        except ImportError:
            print("Error: winsound module not found. Cannot play Windows sound.", file=sys.stderr)
        except RuntimeError as e:
            print(f"Error playing Windows sound alias '{alias}' (winsound.PlaySound failed): {e}", file=sys.stderr)
        except Exception as e:
            print(f"An unexpected error occurred while trying to play Windows sound alias '{alias}': {e}", file=sys.stderr)


if __name__ == '__main__':
    # To package as an executable:
    # 1) pip install PyQt5 pyinstaller
    # 2) pyinstaller --onefile clock_app.py
    app = QApplication(sys.argv)
    clock = ConcentricClock()
    clock.show()
    sys.exit(app.exec_())
