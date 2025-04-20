import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel

class ChatClient(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def initUI(self):
        self.setWindowTitle('Deg Chat')
        self.setGeometry(100, 100, 400, 500)

        self.layout = QVBoxLayout()

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Kullanıcı adınızı girin")
        self.layout.addWidget(self.name_input)

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        self.message_input = QLineEdit(self)
        self.message_input.setPlaceholderText("Mesajınızı yazın...")
        self.layout.addWidget(self.message_input)

        self.send_button = QPushButton('Gönder', self)
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.setLayout(self.layout)

    def connect_to_server(self, host='127.0.0.1', port=12345):
        try:
            self.client_socket.connect((host, port))
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.chat_display.append(f"Sunucuya bağlanılamadı: {e}")

    def send_message(self):
        msg = self.message_input.text()
        name = self.name_input.text() or "Anonim"
        if msg:
            full_message = f"{name}: {msg}"
            self.client_socket.send(full_message.encode())
            self.message_input.clear()

    def receive_messages(self):
        while True:
            try:
                msg = self.client_socket.recv(1024).decode()
                self.chat_display.append(msg)
            except:
                break

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = ChatClient()
    client.show()
    client.connect_to_server()
    sys.exit(app.exec_())
