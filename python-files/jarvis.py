import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, 
                           QVBoxLayout, QPushButton, QWidget, QLineEdit,
                           QCheckBox, QHBoxLayout, QMessageBox, QFrame,
                           QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QSize, QEvent, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QFontDatabase
import threading
import pyttsx3
from google import genai
import speech_recognition as sr

# Classe d'événement personnalisée pour mettre à jour l'interface de manière thread-safe
class UpdateTextEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, text):
        super().__init__(UpdateTextEvent.EVENT_TYPE)
        self.text = text

# Signal personnalisé pour la communication thread-safe
class VoiceSignals(QObject):
    textReady = pyqtSignal(str)

# Style pour le bouton rond de micro
ROUND_BUTTON_STYLE = """
QPushButton {
    background-color: #6200EA;
    color: white;
    border-radius: 25px;
    border: none;
    font-size: 18px;
    padding: 0px;
}
QPushButton:hover {
    background-color: #7C4DFF;
}
QPushButton:pressed {
    background-color: #5502C7;
}
"""

# Style pour l'application en mode sombre
DARK_STYLE = """
QWidget {
    background-color: #121212;
    color: #E0E0E0;
    font-family: 'Segoe UI', Arial;
}
QLineEdit {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 5px;
    padding: 5px;
    color: #E0E0E0;
    selection-background-color: #6200EA;
}
QTextEdit {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 5px;
    padding: 5px;
    color: #E0E0E0;
    selection-background-color: #6200EA;
}
QPushButton {
    background-color: #3700B3;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 5px 10px;
}
QPushButton:hover {
    background-color: #6200EA;
}
QPushButton:pressed {
    background-color: #3700B3;
}
QCheckBox {
    color: #E0E0E0;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
}
QCheckBox::indicator:unchecked {
    border: 1px solid #555555;
    background-color: #1E1E1E;
}
QCheckBox::indicator:checked {
    background-color: #6200EA;
    border: 1px solid #6200EA;
}
"""

class MiniGeminiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuration de l'API Gemini
        self.api_key = "AIzaSyBO4fUK2da4HznWocfmDSAmyuHHRDtV4vc"
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash"
        
        # Configuration du moteur de synthèse vocale
        self.engine = pyttsx3.init()
        self.voice_enabled = True
        
        # Configuration pour la reconnaissance vocale
        self.recognizer = sr.Recognizer()
        self.voice_signals = VoiceSignals()
        self.voice_signals.textReady.connect(self.on_voice_recognized)
        self.listening = False
        
        # Configuration de la fenêtre
        self.setWindowTitle("Mini Gemini")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)  # Retirer la barre de titre
        self.setGeometry(0, 0, 280, 250)  # Taille réduite
        
        # Positionner la fenêtre en bas à droite de l'écran
        screen_geometry = QApplication.desktop().availableGeometry()
        window_geometry = self.frameGeometry()
        x_position = screen_geometry.width() - window_geometry.width() - 20
        y_position = screen_geometry.height() - window_geometry.height() - 20
        self.move(x_position, y_position)
        
        # Appliquer le style sombre
        self.setStyleSheet(DARK_STYLE)
        
        # Initialisation de l'interface
        self.init_ui()
        
        # Variables pour le déplacement de la fenêtre
        self.dragging = False
        self.offset = None
        
    def init_ui(self):
        # Widget central avec bordure arrondie
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Créer une ombre pour la fenêtre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        central_widget.setGraphicsEffect(shadow)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        central_widget.setLayout(layout)
        
        # Zone de texte pour la réponse (en haut)
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        self.response_display.setPlaceholderText("Les réponses apparaîtront ici...")
        self.response_display.setMinimumHeight(50)
        layout.addWidget(self.response_display)
        
        # Zone de texte pour la question (en bas)
        input_frame = QFrame()
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_frame.setLayout(input_layout)
        
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Posez votre question...")
        self.question_input.returnPressed.connect(self.get_response)
        input_layout.addWidget(self.question_input)
        
        # Bouton pour envoyer la question
        send_button = QPushButton("➤")
        send_button.setFixedSize(30, 30)
        send_button.clicked.connect(self.get_response)
        input_layout.addWidget(send_button)
        
        layout.addWidget(input_frame)
        
        # Layout pour les contrôles de voix
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        # Case à cocher pour activer/désactiver la voix
        voice_control = QFrame()
        voice_control_layout = QHBoxLayout()
        voice_control_layout.setContentsMargins(0, 0, 0, 0)
        voice_control.setLayout(voice_control_layout)
        
        self.voice_checkbox = QCheckBox("Voix")
        self.voice_checkbox.setChecked(self.voice_enabled)
        self.voice_checkbox.stateChanged.connect(self.toggle_voice)
        voice_control_layout.addWidget(self.voice_checkbox)
        
        self.stop_voice_button = QPushButton("Stop")
        self.stop_voice_button.setFixedSize(50, 25)
        self.stop_voice_button.clicked.connect(self.stop_voice)
        voice_control_layout.addWidget(self.stop_voice_button)
        
        controls_layout.addWidget(voice_control)
        
        # Bouton central pour la reconnaissance vocale
        self.voice_input_button = QPushButton("🎤")
        self.voice_input_button.setStyleSheet(ROUND_BUTTON_STYLE)
        self.voice_input_button.setFixedSize(50, 50)
        self.voice_input_button.clicked.connect(self.toggle_voice_recognition)
        controls_layout.addWidget(self.voice_input_button, alignment=Qt.AlignCenter)
        
        # Spacer pour équilibrer la mise en page
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
    
    def toggle_voice(self, state):
        self.voice_enabled = bool(state)
        if not self.voice_enabled:
            self.stop_voice()
            
    def stop_voice(self):
        self.engine.stop()
    
    def toggle_voice_recognition(self):
        if self.listening:
            # Arrêter l'écoute
            self.listening = False
            self.voice_input_button.setText("🎤")
            self.question_input.setPlaceholderText("Posez votre question...")
        else:
            # Démarrer l'écoute
            self.voice_input_button.setText("⏹️")
            self.question_input.setPlaceholderText("Écoute en cours...")
            self.listening = True
            # Lancer la reconnaissance vocale dans un thread séparé
            threading.Thread(target=self.listen_for_speech, daemon=True).start()
    
    def listen_for_speech(self):
        try:
            with sr.Microphone() as source:
                # Ajuster pour le bruit ambiant
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Écouter l'audio
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                
                # Si on a arrêté manuellement l'écoute entre-temps
                if not self.listening:
                    return
                
                # Mettre à jour le statut
                app = QApplication.instance()
                app.postEvent(self, UpdateTextEvent("status:Traitement de l'audio..."))
                
                # Convertir l'audio en texte
                text = self.recognizer.recognize_google(audio, language="fr-FR")
                
                # Envoyer le texte reconnu via un signal pour mise à jour thread-safe
                self.voice_signals.textReady.emit(text)
                
        except sr.WaitTimeoutError:
            app = QApplication.instance()
            app.postEvent(self, UpdateTextEvent("status:Temps d'écoute écoulé"))
        except sr.UnknownValueError:
            app = QApplication.instance()
            app.postEvent(self, UpdateTextEvent("status:Désolé, je n'ai pas compris"))
        except sr.RequestError as e:
            app = QApplication.instance()
            app.postEvent(self, UpdateTextEvent(f"status:Erreur: {e}"))
        except Exception as e:
            app = QApplication.instance()
            app.postEvent(self, UpdateTextEvent(f"status:Erreur: {e}"))
        finally:
            # Réinitialiser l'état
            if self.listening:
                self.listening = False
                app = QApplication.instance()
                app.postEvent(self, UpdateTextEvent("button:🎤"))
    
    def on_voice_recognized(self, text):
        # Cette méthode est appelée en toute sécurité via un signal QT
        self.question_input.setText(text)
        self.question_input.setPlaceholderText("Posez votre question...")
        self.voice_input_button.setText("🎤")
        self.listening = False
        
        # Envoyer automatiquement la question
        self.get_response()
        
    def get_response(self):
        question = self.question_input.text()
        if not question:
            return
            
        # Effacer le champ de question
        self.question_input.clear()
        
        # Mettre à jour l'interface pour montrer que la requête est en cours
        self.response_display.setPlainText("Chargement de la réponse...")
        
        # Lancer la requête dans un thread séparé pour ne pas bloquer l'interface
        threading.Thread(target=self._fetch_response, args=(question,), daemon=True).start()
    
    def _fetch_response(self, question):
        try:
            # Appel à l'API Gemini
            response = self.client.models.generate_content(
                model=self.model, 
                contents=question
            )
            
            response_text = response.text
            
            # Mettre à jour l'interface avec la réponse (thread-safe)
            app = QApplication.instance()
            app.postEvent(self, UpdateTextEvent("response:" + response_text))
            
            # Synthèse vocale dans un thread séparé si activée
            if self.voice_enabled:
                threading.Thread(target=self._speak_text, args=(response_text,), daemon=True).start()
            
        except Exception as e:
            error_message = f"Erreur: {str(e)}"
            
            # Mettre à jour l'interface avec l'erreur
            app = QApplication.instance()
            app.postEvent(self, UpdateTextEvent("response:" + error_message))
            
            # Synthèse vocale de l'erreur si activée
            if self.voice_enabled:
                threading.Thread(target=self._speak_text, args=(error_message,), daemon=True).start()
    
    def _speak_text(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Erreur de synthèse vocale: {e}")
    
    # Gestion des événements personnalisés
    def event(self, event):
        if event.type() == UpdateTextEvent.EVENT_TYPE:
            if event.text.startswith("status:"):
                self.question_input.setPlaceholderText(event.text[7:])
            elif event.text.startswith("button:"):
                self.voice_input_button.setText(event.text[7:])
            elif event.text.startswith("response:"):
                self.response_display.setPlainText(event.text[9:])
            else:
                self.response_display.setPlainText(event.text)
            return True
        return super().event(event)

    # Permettre le déplacement de la fenêtre sans barre de titre
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging and self.offset:
            self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiniGeminiApp()
    window.show()
    sys.exit(app.exec_())