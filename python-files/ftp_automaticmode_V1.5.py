import os
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog
import threading
import queue
import ftplib
import requests
import json
import re
import time
import subprocess
from datetime import datetime
from PIL import Image, ImageTk

# Bestimme den Ordner, in dem sich das Skript befindet, und speichere ips.json dort.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IP_FILE = os.path.join(BASE_DIR, "ips.json")

# Globale Queues für Logs und Fortschrittsupdates (beide thread-sicher)
log_queue = queue.Queue()
progress_queue = queue.Queue()

# Globales Event zum Stoppen der Übertragung
stop_transfer_event = threading.Event()

# Lokale Basisverzeichnisse für den Fall, dass kein individueller Pfad angegeben wird
DEFAULT_WINDOWS_BASE = "D:/SondenDaten"
DEFAULT_LINUX_BASE = "/home/pi/SondenDaten"

# Standard-Benutzername und Passwort
DEFAULT_USERNAME = "sonden"
DEFAULT_PASSWORD = "chaser"

# Farben für die Logausgabe
LOG_COLORS = {
    "INFO": "black",
    "ERROR": "red",
    "WARNING": "orange",
    "SUCCESS": "green",
    "SUMMARY": "blue"
}

def log(message, level="INFO"):
    """Schreibt eine Lognachricht mit Zeitstempel in die Log-Queue."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_queue.put((f"[{timestamp}] {message}\n", level))

def load_ips():
    """Lädt die gespeicherten IP-Daten (Liste von Dictionaries) aus der JSON-Datei."""
    try:
        with open(IP_FILE, "r") as f:
            data = json.load(f)
            # Lade die Einstellungen für das automatische Speichern des Logs
            if "settings" in data:
                return data["ips"], data["settings"]
            return data["ips"], {}
    except Exception:
        return [], {}

def save_ips(ips_data, settings=None):
    """Speichert die übergebene Liste von IP-Daten in der JSON-Datei."""
    try:
        data = {"ips": ips_data}
        if settings:
            data["settings"] = settings
        with open(IP_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Fehler beim Speichern der IPs: {e}")

def send_ftp_mode_command(ip, command, max_retries=3, timeout=10):
    """
    Sendet einen HTTP-POST-Befehl an den Sonden-Controller, um in den FTP-Modus zu schalten.
    :param ip: Die IP-Adresse des Sonden-Controllers
    :param command: 'ftpon', 'ftpoff' oder 'reset'
    :param max_retries: Maximale Anzahl von Versuchen
    :param timeout: Timeout für die HTTP-Anfrage in Sekunden
    """
    url = f"http://{ip}/control.html"
    if command == "ftpon":
        data = {'ftpon': 'Activate FTP Mode'}
    elif command == "ftpoff":
        data = {'ftpoff': 'Deactivate FTP Mode'}
    elif command == "reset":
        data = {'reset': 'Reset'}
    else:
        log(f"Unbekannter Befehl {command} für {ip}.", level="ERROR")
        return False

    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(url, data=data, timeout=timeout)
            if response.status_code == 200:
                log(f"{command} Befehl erfolgreich an {ip} gesendet.", level="SUCCESS")
                return True
            else:
                log(f"Fehler beim Senden von {command} an {ip}: Status Code {response.status_code}.", level="ERROR")
        except requests.exceptions.RequestException as e:
            log(f"Verbindungsfehler zu {ip} für {command} (Versuch {retries + 1}/{max_retries}): {str(e)}", level="ERROR")
        retries += 1
        time.sleep(2)  # Kurze Wartezeit vor dem nächsten Versuch

    log(f"FTP-Kommando {command} für {ip} nach {max_retries} Versuchen fehlgeschlagen.", level="ERROR")
    return False

def ftp_transfer(ip, storage_path="", username=None, password=None, max_retries=255):
    """
    Baut eine FTP-Verbindung zum Server (IP) auf und überträgt Dateien.
    Gibt die Menge der übertragenen Daten in Bytes zurück oder None, wenn ein Fehler auftritt.
    """
    global app  # Zugriff auf die App-Instanz
    app.update_ampel("yellow", ip)  # Ampel auf Gelb setzen (Verbindungsaufbau)

    try:
        year = datetime.now().year
        if storage_path:
            local_path = os.path.join(storage_path, str(year))
        else:
            base = DEFAULT_WINDOWS_BASE if os.name == "nt" else DEFAULT_LINUX_BASE
            local_path = os.path.join(base, ip, str(year))
        os.makedirs(local_path, exist_ok=True)
        
        ftp = None
        retries = 0
        total_bytes = 0  # Gesamtmenge der übertragenen Daten

        # Verwende Standard-Benutzername und Passwort, falls keine angegeben wurden
        ftp_username = username if username else DEFAULT_USERNAME
        ftp_password = password if password else DEFAULT_PASSWORD

        while retries < max_retries:
            try:
                log(f"Versuche {retries + 1}/{max_retries}: Verbinde zu FTP-Server {ip}...", level="INFO")
                ftp = ftplib.FTP(ip, timeout=10)
                log("Verbindung hergestellt.", level="SUCCESS")
                app.update_ampel("green", ip)  # Ampel auf Grün setzen (verbunden)
                
                log(f"Versuche {retries + 1}/{max_retries}: Login...", level="INFO")
                ftp.login(ftp_username, ftp_password)
                log("Login erfolgreich.", level="SUCCESS")
                
                ftp.set_pasv(True)
                log("Passivmodus aktiviert.", level="INFO")
                
                log(f"Versuche {retries + 1}/{max_retries}: Wechsle in das Verzeichnis 'Sondenlog'...", level="INFO")
                ftp.cwd("Sondenlog")
                log("Verzeichnis 'Sondenlog' erreicht.", level="SUCCESS")
                
                # Abrufen der Dateiliste mit Fehlerbehandlung
                log(f"Versuche {retries + 1}/{max_retries}: Rufe Dateiliste ab...", level="INFO")
                try:
                    files = ftp.nlst()
                    log(f"Dateiliste erhalten: {files}", level="INFO")
                    if not files:
                        log(f"Keine Dateien in Sondenlog bei {ip} gefunden. Kein Transfer notwendig.", level="WARNING")
                        ftp.quit()
                        return 0  # Keine Dateien, aber kein Fehler
                    else:
                        log("Sondenliste erfolgreich geladen. Transfer beginnt in Kürze...", level="INFO")
                except Exception as e:
                    log(f"Fehler beim Abrufen der Dateiliste: {str(e)}", level="ERROR")
                    raise
                
                # Normalisiere die Dateinamen (nur Basisnamen verwenden)
                normalized_files = [os.path.basename(f) for f in files]

                # Ermitteln der Gesamtgröße aller Dateien
                total_bytes = 0
                file_sizes = {}
                for name in normalized_files:
                    try:
                        size = ftp.size(name)
                    except Exception:
                        size = 0
                    file_sizes[name] = size
                    total_bytes += size
                overall_downloaded = 0
                
                log(f"{len(normalized_files)} Datei(en) gefunden. Gesamtgröße: {total_bytes} Bytes.", level="INFO")
                
                # Versuch, Änderungszeiten via MLSD oder LIST zu ermitteln
                mod_times = {}
                try:
                    log("Versuche, MLSD-Daten abzurufen...", level="INFO")
                    entries = list(ftp.mlsd())
                    for name, facts in entries:
                        name = os.path.basename(name)
                        if 'modify' in facts:
                            mod_str = facts['modify'][:14]
                            mod_dt = datetime.strptime(mod_str, "%Y%m%d%H%M%S")
                            mod_times[name] = mod_dt
                    log("MLSD erfolgreich ausgewertet.", level="SUCCESS")
                except Exception:
                    log("MLSD nicht unterstützt, wechsle zu LIST-Parsing.", level="WARNING")
                    lines = []
                    ftp.dir(lines.append)
                    pattern = re.compile(r"^(\d{2}-\d{2}-\d{2})\s+(\d{1,2}:\d{2}[AP]M)\s+\S+\s+(.*)$")
                    for line in lines:
                        match = pattern.match(line)
                        if match:
                            date_str, time_str, fname = match.groups()
                            fname = os.path.basename(fname)
                            try:
                                dt = datetime.strptime(f"{date_str} {time_str}", "%m-%d-%y %I:%M%p")
                                mod_times[fname] = dt
                            except Exception as e2:
                                log(f"Fehler beim Parsen der Zeit für {fname}: {e2}", level="ERROR")
                    log("LIST-Parsing abgeschlossen.", level="INFO")
                
                # Warnung vor dem Start des Transfers
                log("Transfer beginnt jetzt...", level="INFO")
                
                # Download der Dateien mit Fortschrittsanzeige
                start_time = time.time()  # Startzeit für die Geschwindigkeitsberechnung
                for name in normalized_files:
                    if stop_transfer_event.is_set():
                        log(f"Übertragung für {ip} wurde abgebrochen.", level="WARNING")
                        break

                    # Aktualisiere das Label mit dem aktuellen File
                    app.current_file_label.config(text=f"Aktuelles File: {name}")

                    local_file_path = os.path.join(local_path, name)
                    temp_file_path = local_file_path + ".tmp"  # Temporäre Datei
                    
                    log(f"Starte Download von {name}...", level="INFO")
                    file_size = file_sizes[name]
                    downloaded = 0  # Bytes für diese Datei
                    
                    # Wiederholungslogik bei Fehlern
                    file_retries = 0
                    while file_retries < max_retries:
                        try:
                            with open(temp_file_path, "wb") as lf:
                                def callback(block):
                                    nonlocal downloaded, overall_downloaded
                                    downloaded += len(block)
                                    overall_downloaded += len(block)
                                    lf.write(block)
                                    
                                    # Berechne Geschwindigkeit und verbleibende Zeit
                                    elapsed_time = time.time() - start_time
                                    speed_kBs = (overall_downloaded / 1024) / elapsed_time if elapsed_time > 0 else 0
                                    current_remaining_time = (file_size - downloaded) / (speed_kBs * 1024) if speed_kBs > 0 else 0
                                    overall_remaining_time = (total_bytes - overall_downloaded) / (speed_kBs * 1024) if speed_kBs > 0 else 0
                                    
                                    file_percent = (downloaded / file_size * 100) if file_size > 0 else 100
                                    overall_percent = (overall_downloaded / total_bytes * 100) if total_bytes > 0 else 100
                                    progress_queue.put((file_percent, overall_percent, speed_kBs, current_remaining_time, overall_remaining_time))
                                ftp.retrbinary("RETR " + name, callback)
                            
                            # Erfolgreicher Download
                            log(f"Download von {name} abgeschlossen.", level="SUCCESS")
                            break
                        except Exception as e:
                            file_retries += 1
                            log(f"Fehler beim Download von {name} (Versuch {file_retries + 1}/{max_retries}): {str(e)}", level="ERROR")
                            if file_retries >= max_retries:
                                log(f"Download von {name} fehlgeschlagen nach {max_retries} Versuchen.", level="ERROR")
                                raise
                    
                    # Anhängen der Datei, falls sie bereits existiert
                    if os.path.exists(local_file_path):
                        log(f"{name} existiert bereits. Füge Inhalt an...", level="INFO")
                        with open(local_file_path, "ab") as existing_file, open(temp_file_path, "rb") as temp_file:
                            existing_file.write(temp_file.read())
                        os.remove(temp_file_path)
                    else:
                        os.rename(temp_file_path, local_file_path)
                    
                    # Setze den Zeitstempel der Datei
                    if name in mod_times:
                        mod_dt = mod_times[name]
                        mod_timestamp = mod_dt.timestamp()
                        os.utime(local_file_path, (mod_timestamp, mod_timestamp))
                        log(f"Modifikationszeit von {name} auf {mod_dt} gesetzt.", level="INFO")
                    else:
                        log(f"Keine Modifikationszeit für {name} gefunden.", level="WARNING")
                    
                    # Lösche die Datei vom Server
                    ftp.delete(name)
                    log(f"{name} von {ip} heruntergeladen und vom Server gelöscht.", level="INFO")
                
                ftp.quit()
                log(f"Übertragung für {ip} abgeschlossen.", level="SUCCESS")
                return total_bytes  # Rückgabe der Gesamtmenge der übertragenen Daten
            except Exception as e:
                retries += 1
                log(f"Fehler bei FTP-Übertragung von {ip} (Versuch {retries}/{max_retries}): {str(e)}", level="ERROR")
                if ftp:
                    try:
                        ftp.quit()
                    except Exception:
                        pass
                if retries >= max_retries:
                    log(f"FTP-Übertragung für {ip} fehlgeschlagen nach {max_retries} Versuchen.", level="ERROR")
                    app.update_ampel("violet")  # Ampel auf Violett setzen bei Fehlern
                    return None  # Rückgabe von None bei Fehlern
                time.sleep(5)  # Warte 5 Sekunden vor dem nächsten Versuch
    finally:
        app.update_ampel("red")  # Ampel auf rot setzen nach Abschluss
        app.current_file_label.config(text="Aktuelles File: -")  # Zurücksetzen des Labels nach Abschluss

class SondenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sonden FTP Manager - DL8SFG - V1.5")
        self.geometry("700x750")

        # Lade das Icon aus der Datei
        try:
            icon_path = os.path.join(BASE_DIR, "app_icon.png")
            self.icon = ImageTk.PhotoImage(Image.open(icon_path))
            self.iconphoto(True, self.icon)
        except Exception as e:
            log(f"Fehler beim Laden des Icons: {e}", level="ERROR")

        # Datenstruktur: Liste von Dictionaries mit "ip", "path", "username", "password" und "active"
        self.ips_data, self.settings = load_ips()
        # Variable für den automatischen Modus
        self.automatic_mode = tk.BooleanVar(value=False)
        # Variable für das automatische Speichern des Logs
        self.autosave_log = tk.BooleanVar(value=self.settings.get("autosave_log", False))
        # Variable für den Speicherpfad des Logs
        self.log_save_path = self.settings.get("log_save_path", os.path.join(BASE_DIR, "log.log"))
        # Neue Variable für Reset vor FTP
        self.reset_before_ftp = tk.BooleanVar(value=False)
        # Farbe für Wartezustand
        self.waiting_color = "pink"
        
        self.create_widgets()
        self.transfer_thread = None
        self.load_ips_from_file()
        self.after(100, self.update_log_widget)
        self.after(100, self.update_progress_bars)

    def create_widgets(self):
        # Rahmen für die IP- und Pfadeingabe
        input_frame = tk.LabelFrame(self, text="IP und Speicherpfad")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ip_label = tk.Label(input_frame, text="IP:")
        ip_label.grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.ip_entry = tk.Entry(input_frame)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=2, sticky="we")
        
        path_label = tk.Label(input_frame, text="Speicherpfad:")
        path_label.grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.path_entry = tk.Entry(input_frame)
        self.path_entry.grid(row=1, column=1, padx=5, pady=2, sticky="we")
        
        user_label = tk.Label(input_frame, text="Benutzername:")
        user_label.grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.user_entry = tk.Entry(input_frame)
        self.user_entry.grid(row=2, column=1, padx=5, pady=2, sticky="we")
        
        pass_label = tk.Label(input_frame, text="Passwort:")
        pass_label.grid(row=3, column=0, padx=5, pady=2, sticky="e")
        self.pass_entry = tk.Entry(input_frame, show="*")
        self.pass_entry.grid(row=3, column=1, padx=5, pady=2, sticky="we")
        
        add_button = tk.Button(input_frame, text="Hinzufügen", command=self.add_ip)
        add_button.grid(row=0, column=2, rowspan=4, padx=5, pady=2)
        
        input_frame.columnconfigure(1, weight=1)
        
        # Rahmen für die gespeicherten IP-Daten
        list_frame = tk.LabelFrame(self, text="Gespeicherte IPs")
        list_frame.pack(fill=tk.X, padx=10, pady=5)

        # Listbox mit Scrollbar
        self.ip_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=10)
        self.ip_listbox.pack(fill=tk.X, padx=5, pady=5)

        # Scrollbar für die Listbox
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.ip_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ip_listbox.config(yscrollcommand=scrollbar.set)

        # Rahmen für die Buttons
        button_frame = tk.Frame(list_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        # Buttons nebeneinander anordnen
        edit_path_button = tk.Button(button_frame, text="Pfad bearbeiten", command=self.edit_path)
        edit_path_button.pack(side=tk.LEFT, padx=5, pady=5)

        remove_button = tk.Button(button_frame, text="Entfernen", command=self.remove_ip)
        remove_button.pack(side=tk.LEFT, padx=5, pady=5)

        toggle_active_button = tk.Button(button_frame, text="Aktiv/Inaktiv umschalten", command=self.toggle_active)
        toggle_active_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Rahmen für Befehle
        cmd_frame = tk.LabelFrame(self, text="Befehle")
        cmd_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ftp_on_button = tk.Button(cmd_frame, text="FTP AN", command=lambda: self.send_command_to_selected("ftpon"))
        ftp_on_button.pack(side=tk.LEFT, padx=5, pady=5)
        ftp_off_button = tk.Button(cmd_frame, text="FTP AUS", command=lambda: self.send_command_to_selected("ftpoff"))
        ftp_off_button.pack(side=tk.LEFT, padx=5, pady=5)
        reset_button = tk.Button(cmd_frame, text="Reset", command=lambda: self.send_command_to_selected("reset"))
        reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Ping-Buttons
        ping_selected_button = tk.Button(cmd_frame, text="Ping Ausgewählte", 
                                      command=lambda: self.check_reachability(selected_only=True))
        ping_selected_button.pack(side=tk.LEFT, padx=5, pady=5)
        ping_all_button = tk.Button(cmd_frame, text="Ping Alle", 
                                 command=lambda: self.check_reachability(selected_only=False))
        ping_all_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Checkbutton für den automatischen Modus
        auto_check = tk.Checkbutton(cmd_frame, text="Automatischer Modus", variable=self.automatic_mode)
        auto_check.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Neue Checkbox für Reset vor FTP
        reset_check = tk.Checkbutton(cmd_frame, text="Reset vor FTP", variable=self.reset_before_ftp)
        reset_check.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Rahmen für die FTP-Übertragungssteuerung
        transfer_frame = tk.LabelFrame(self, text="FTP Übertragung")
        transfer_frame.pack(fill=tk.X, padx=10, pady=5)
        start_transfer_button = tk.Button(transfer_frame, text="Übertragung Starten", command=self.start_transfer)
        start_transfer_button.pack(side=tk.LEFT, padx=5, pady=5)
        stop_transfer_button = tk.Button(transfer_frame, text="Übertragung Stoppen", command=self.stop_transfer)
        stop_transfer_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Rahmen für die Fortschrittsanzeige
        progress_frame = tk.LabelFrame(self, text="Fortschritt")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Aktueller Download
        self.current_progress_label = tk.Label(progress_frame, text="Aktueller Download:")
        self.current_progress_label.pack(fill=tk.X, padx=5, pady=2)
        self.current_progress = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate', maximum=100)
        self.current_progress.pack(fill=tk.X, padx=5, pady=2)
        
        # Geschwindigkeit und verbleibende Zeit
        self.current_speed_time_label = tk.Label(progress_frame, text="Geschwindigkeit: 0 kB/s | Verbleibende Zeit: 0s")
        self.current_speed_time_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Gesamter Download
        self.overall_progress_label = tk.Label(progress_frame, text="Gesamter Download:")
        self.overall_progress_label.pack(fill=tk.X, padx=5, pady=2)
        self.overall_progress = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate', maximum=100)
        self.overall_progress.pack(fill=tk.X, padx=5, pady=2)
        
        # Geschätzte Gesamtzeit
        self.overall_remaining_time_label = tk.Label(progress_frame, text="Voraussichtliche Gesamtzeit: 0s")
        self.overall_remaining_time_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Rahmen für die Ampel und IP-Anzeige
        status_frame = tk.LabelFrame(self, text="Verbindungsstatus")
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.ampel_label = tk.Label(status_frame, text="Status:")
        self.ampel_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.ampel_canvas = tk.Canvas(status_frame, width=30, height=30)
        self.ampel_canvas.pack(side=tk.LEFT, padx=5, pady=5)
        self.ampel_light = self.ampel_canvas.create_oval(5, 5, 25, 25, fill="red")

        self.connected_ip_label = tk.Label(status_frame, text="Keine Verbindung")
        self.connected_ip_label.pack(side=tk.LEFT, padx=5, pady=5)

        # Label für das aktuelle File
        self.current_file_label = tk.Label(status_frame, text="Aktuelles File: -")
        self.current_file_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Rahmen für die Loganzeige
        log_frame = tk.LabelFrame(self, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Button zum Speichern des Logs
        log_controls_frame = tk.Frame(log_frame)
        log_controls_frame.pack(fill=tk.X, padx=5, pady=5)

        save_log_button = tk.Button(log_controls_frame, text="Log speichern", command=self.save_log)
        save_log_button.pack(side=tk.LEFT, padx=5, pady=5)

        autosave_log_check = tk.Checkbutton(log_controls_frame, text="Log automatisch speichern", 
                                         variable=self.autosave_log)
        autosave_log_check.pack(side=tk.LEFT, padx=5, pady=5)

        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text = tk.Text(log_frame, state=tk.DISABLED, yscrollcommand=scrollbar.set)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Farbige Logausgabe
        self.log_text.tag_config("INFO", foreground=LOG_COLORS["INFO"])
        self.log_text.tag_config("ERROR", foreground=LOG_COLORS["ERROR"])
        self.log_text.tag_config("WARNING", foreground=LOG_COLORS["WARNING"])
        self.log_text.tag_config("SUCCESS", foreground=LOG_COLORS["SUCCESS"])
        self.log_text.tag_config("SUMMARY", foreground=LOG_COLORS["SUMMARY"])
        
        # Sperren des Log-Fensters gegen Copy & Paste
        self.log_text.bind("<Control-c>", lambda e: "break")
        self.log_text.bind("<Control-v>", lambda e: "break")
    
    def ping_ip(self, ip, timeout=1):
        """Pingt eine IP-Adresse und gibt True zurück, wenn erreichbar."""
        try:
            param = '-n' if os.name == 'nt' else '-c'
            command = ['ping', param, '1', '-w', str(timeout), ip]
            return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
        except Exception:
            return False

    def wait_for_reboot(self, ip, timeout=60, ping_interval=2):
        """Wartet auf den Neustart des Servers durch regelmäßige Ping-Anfragen."""
        start_time = time.time()
        self.update_ampel(self.waiting_color, f"Warte auf Neustart von {ip}...")
        
        while time.time() - start_time < timeout:
            if self.ping_ip(ip):
                log(f"{ip} ist nach Reset wieder online.", level="SUCCESS")
                self.update_ampel("yellow", f"{ip} bereit für FTP")
                return True
            time.sleep(ping_interval)
        
        log(f"Timeout: {ip} nach Reset nicht zurückgekehrt (nach {timeout}s).", level="WARNING")
        return False

    def check_reachability(self, selected_only=False):
        """Überprüft die Erreichbarkeit der Empfänger."""
        items = self.get_selected_ips() if selected_only else self.ips_data
        if not items:
            messagebox.showwarning("Warnung", "Keine IP-Adressen zum Ping verfügbar.")
            return
        
        # Setze Ampel auf Orange für die Dauer des Tests
        self.update_ampel("orange", "Ping-Test läuft")
        all_reachable = True
        
        for item in items:
            if not item.get("active", True):
                continue
                
            ip = item.get("ip")
            if self.ping_ip(ip):
                log(f"{ip} ist erreichbar", level="SUCCESS")
            else:
                log(f"{ip} ist NICHT erreichbar", level="ERROR")
                all_reachable = False
            # Kurze Pause zwischen den Pings
            time.sleep(0.5)
        
        # Ergebnis anzeigen
        if all_reachable:
            log("Alle aktiven Empfänger verfügbar", level="SUCCESS")
            # Kurz Grün anzeigen, dann zurück zu Rot
            self.update_ampel("green", "Alle erreichbar")
        else:
            log("Einige Empfänger nicht erreichbar", level="ERROR")
            # Kurz Violett anzeigen
            self.update_ampel("violet", "Fehler beim Ping")
        
        # Nach 3 Sekunden automatisch auf Rot zurücksetzen
        self.after(3000, lambda: self.update_ampel("red", "Keine Verbindung"))

    def update_ampel(self, status, ip_or_message=None):
        """
        Aktualisiert die Ampel und die IP-Anzeige.
        """
        if status == "green":
            color = "green"
            status_text = f"Verbunden mit: {ip_or_message}" if ip_or_message and "." in ip_or_message else "Verbunden"
        elif status == "yellow":
            color = "yellow"
            status_text = "Verbindungsaufbau..." if ip_or_message and "." in ip_or_message else "Verbindungssuche..."
        elif status == "blue":
            color = "blue"
            status_text = "Transfer abgeschlossen (erfolgreich)"
        elif status == "violet":
            color = "violet"
            status_text = "Transfer abgeschlossen (mit Fehlern)"
        elif status == "pink":
            color = "pink"
            status_text = ip_or_message if ip_or_message else "Warte auf Neustart..."
        elif status == "orange":
            color = "orange"
            status_text = f"Einzelmodus: {ip_or_message}" if ip_or_message else "Einzel-Empfänger ausgewählt"
        else:  # status == "red"
            color = "red"
            status_text = ip_or_message if ip_or_message else "Keine Verbindung"
        
        self.ampel_canvas.itemconfig(self.ampel_light, fill=color)
        self.connected_ip_label.config(text=status_text)
    
    def flush_log_queue(self):
        """Leert die Log-Queue und schreibt alle Nachrichten ins Log-Fenster."""
        try:
            while True:
                msg, level = log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, msg, level)
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
    
    def save_log(self, autosave=False):
        """Speichert den Log in eine Datei (entweder manuell oder automatisch)."""
        try:
            self.flush_log_queue()
            log_content = self.log_text.get("1.0", tk.END).strip()
            
            if not log_content:
                return  # Keine Logs zum Speichern
                
            log_dir = os.path.join(BASE_DIR, "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            if autosave:
                # Autosave: Neue Datei mit Zeitstempel erstellen
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                autosave_path = os.path.join(log_dir, f"log_{timestamp}.log")
                try:
                    with open(autosave_path, "w", encoding='utf-8') as f:
                        f.write(log_content)
                    self.log_save_path = autosave_path
                    log(f"Log automatisch gespeichert unter: {autosave_path}", level="INFO")
                except Exception as e:
                    log(f"Autosave fehlgeschlagen: {str(e)}", level="ERROR")
            else:
                # Manueller Speichervorgang (Dialog öffnen)
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".log",
                    filetypes=[("Log files", "*.log")],
                    initialfile=f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
                    initialdir=log_dir
                )
                if file_path:
                    with open(file_path, "w", encoding='utf-8') as f:
                        f.write(log_content)
                    self.log_save_path = file_path
                    log(f"Log manuell gespeichert unter: {file_path}", level="INFO")
        
            # Einstellungen aktualisieren
            self.settings["log_save_path"] = self.log_save_path
            self.settings["autosave_log"] = self.autosave_log.get()
            save_ips(self.ips_data, self.settings)
            
        except Exception as e:
            log(f"Fehler beim Log-Speichern: {str(e)}", level="ERROR")
    
    def refresh_ip_listbox(self):
        self.ip_listbox.delete(0, tk.END)
        for item in self.ips_data:
            ip = item.get("ip", "")
            path = item.get("path", "")
            username = item.get("username", "")
            password = item.get("password", "")
            active = item.get("active", True)
            status = "Aktiv" if active else "Inaktiv"
            self.ip_listbox.insert(tk.END, f"{ip} | {path} | {username} | {'*' * len(password)} | {status}")
    
    def load_ips_from_file(self):
        self.ips_data, self.settings = load_ips()
        new_ips = []
        for item in self.ips_data:
            if isinstance(item, dict):
                new_ips.append(item)
            elif isinstance(item, str):
                new_ips.append({"ip": item, "path": "", "username": "", "password": "", "active": True})
        self.ips_data = new_ips
        self.refresh_ip_listbox()
        log(f"{len(self.ips_data)} IPs aus der Datei geladen.", level="INFO")
    
    def save_ips_to_file(self):
        save_ips(self.ips_data, self.settings)
    
    def add_ip(self):
        ip = self.ip_entry.get().strip()
        path = self.path_entry.get().strip()
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        if not ip:
            messagebox.showwarning("Warnung", "Bitte eine IP-Adresse eingeben.")
            return
        for item in self.ips_data:
            if item.get("ip") == ip:
                messagebox.showinfo("Info", "Diese IP-Adresse ist bereits vorhanden.")
                return
        new_item = {"ip": ip, "path": path, "username": username, "password": password, "active": True}
        self.ips_data.append(new_item)
        self.refresh_ip_listbox()
        self.save_ips_to_file()
        log(f"IP {ip} mit Pfad '{path}', Benutzername '{username}' und Passwort hinzugefügt.", level="INFO")
        self.ip_entry.delete(0, tk.END)
        self.path_entry.delete(0, tk.END)
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
    
    def remove_ip(self):
        selected_indices = self.ip_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warnung", "Bitte eine IP-Adresse auswählen.")
            return
        for index in reversed(selected_indices):
            removed = self.ips_data.pop(index)
            log(f"IP {removed.get('ip')} entfernt.", level="INFO")
        self.refresh_ip_listbox()
        self.save_ips_to_file()
    
    def edit_path(self):
        selected_indices = self.ip_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warnung", "Bitte eine IP-Adresse auswählen, deren Pfad bearbeitet werden soll.")
            return
        index = selected_indices[0]
        current_item = self.ips_data[index]
        current_path = current_item.get("path", "")
        new_path = simpledialog.askstring("Pfad bearbeiten", f"Geben Sie den neuen Speicherpfad für {current_item.get('ip')} ein:", initialvalue=current_path)
        if new_path is not None:
            self.ips_data[index]["path"] = new_path.strip()
            self.refresh_ip_listbox()
            self.save_ips_to_file()
            log(f"Pfad für {current_item.get('ip')} auf '{new_path.strip()}' geändert.", level="INFO")
    
    def toggle_active(self):
        selected_indices = self.ip_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warnung", "Bitte eine IP-Adresse auswählen.")
            return
        index = selected_indices[0]
        current_item = self.ips_data[index]
        current_item["active"] = not current_item.get("active", True)
        self.refresh_ip_listbox()
        self.save_ips_to_file()
        status = "aktiviert" if current_item["active"] else "deaktiviert"
        log(f"Status für {current_item.get('ip')} wurde {status}.", level="INFO")
    
    def get_selected_ips(self):
        selected_indices = self.ip_listbox.curselection()
        if not selected_indices:
            return self.ips_data  # Alle, falls nichts ausgewählt
        else:
            return [self.ips_data[i] for i in selected_indices]
    
    def send_command_to_selected(self, command):
        items = self.get_selected_ips()
        if not items:
            messagebox.showwarning("Warnung", "Keine IP-Adressen ausgewählt.")
            return
        for item in items:
            ip = item.get("ip")
            threading.Thread(target=send_ftp_mode_command, args=(ip, command), daemon=True).start()
    
    def sequential_transfer(self, items):
        total_servers = len(items)
        successful_servers = 0
        skipped_servers = 0
        failed_servers = 0
        total_data_transferred = 0

        for item in items:
            if stop_transfer_event.is_set():
                log("Transfer wurde abgebrochen.", level="WARNING")
                break
            if not item.get("active", True):
                log(f"Server {item.get('ip')} ist inaktiv und wird übersprungen.", level="WARNING")
                skipped_servers += 1
                continue
                
            ip = item.get("ip")
            storage_path = item.get("path", "")
            username = item.get("username", "")
            password = item.get("password", "")
            
            try:
                log(f"\nStarte Übertragung für {ip} ...", level="INFO")
                self.update_ampel("yellow", ip)
                
                # NEUE LOGIK: Reset vor FTP wenn aktiviert und im automatischen Modus
                if self.automatic_mode.get() and self.reset_before_ftp.get():
                    log(f"Sende Reset an {ip} vor FTP-Modus...", level="INFO")
                    if not send_ftp_mode_command(ip, "reset"):
                        log(f"Reset für {ip} fehlgeschlagen.", level="ERROR")
                        failed_servers += 1
                        continue
                    
                    # Warte auf Neustart
                    if not self.wait_for_reboot(ip):
                        log(f"Überspringe {ip} wegen fehlendem Neustart.", level="WARNING")
                        failed_servers += 1
                        continue
                
                # Rest der bestehenden Logik...
                log(f"Aktiviere FTP-Modus für {ip} ...", level="INFO")
                if not send_ftp_mode_command(ip, "ftpon"):
                    log(f"FTP-Modus für {ip} konnte nicht aktiviert werden.", level="ERROR")
                    failed_servers += 1
                    app.update_ampel("violet")
                    continue
                time.sleep(2)
                
                transferred_bytes = ftp_transfer(ip, storage_path=storage_path, 
                                              username=username, password=password)
                
                if transferred_bytes is None:
                    failed_servers += 1
                    continue
                    
                successful_servers += 1
                total_data_transferred += transferred_bytes
                time.sleep(2)
                
                log(f"Deaktiviere FTP-Modus für {ip} ...", level="INFO")
                if not send_ftp_mode_command(ip, "ftpoff"):
                    log(f"FTP-Modus für {ip} konnte nicht deaktiviert werden.", level="ERROR")
                    app.update_ampel("violet")
                time.sleep(5)
                
            except Exception as e:
                log(f"Fehler bei der Übertragung für {ip}: {str(e)}", level="ERROR")
                failed_servers += 1
            finally:
                self.update_ampel("red")
        
        # ZUSAMMENFASSUNG ERST NACH FTP OFF
        log("\n--- Zusammenfassung ---", level="SUMMARY")
        log(f"Gesamte Server: {total_servers}", level="SUMMARY")
        log(f"Erfolgreich verarbeitet: {successful_servers}", level="SUMMARY")
        log(f"Übersprungen (inaktiv): {skipped_servers}", level="SUMMARY")
        log(f"Fehlgeschlagen: {failed_servers}", level="SUMMARY")
        log(f"Gesamtmenge der übertragenen Daten: {total_data_transferred / 1024:.2f} kB", level="SUMMARY")
        log("----------------------", level="SUMMARY")

        # AUTOSAVE NUR EINMAL AM ENDE (falls aktiviert)
        if self.autosave_log.get():
            self.save_log(autosave=True)
            log("Log wurde automatisch gespeichert.", level="SUMMARY")

        time.sleep(0.5)
        self.after(0, self.update_status, failed_servers)

    def update_status(self, failed_servers):
        if failed_servers > 0:
            self.update_ampel("violet")
        else:
            self.update_ampel("blue")
    
    def start_transfer(self):
        stop_transfer_event.clear()
        items = self.get_selected_ips()
        if not items:
            messagebox.showwarning("Warnung", "Keine IP-Adressen ausgewählt.")
            return
        self.transfer_thread = threading.Thread(target=self.sequential_transfer, args=(items,), daemon=True)
        self.transfer_thread.start()
        log("FTP Übertragung gestartet.", level="INFO")
    
    def stop_transfer(self):
        stop_transfer_event.set()
        log("Anforderung zum Stoppen der Übertragung wurde gesendet.", level="WARNING")
        self.current_progress["value"] = 0
        self.overall_progress["value"] = 0
        self.current_speed_time_label.config(text="Geschwindigkeit: 0 kB/s | Verbleibende Zeit: 0s")
        self.overall_remaining_time_label.config(text="Voraussichtliche Gesamtzeit: 0s")
    
    def update_log_widget(self):
        try:
            while True:
                msg, level = log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, msg, level)
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.after(100, self.update_log_widget)
    
    def update_progress_bars(self):
        try:
            while True:
                file_percent, overall_percent, speed_kBs, current_remaining_time, overall_remaining_time = progress_queue.get_nowait()
                self.current_progress["value"] = file_percent
                self.overall_progress["value"] = overall_percent
                self.current_speed_time_label.config(text=f"Geschwindigkeit: {speed_kBs:.2f} kB/s | Verbleibende Zeit: {current_remaining_time:.1f} s")
                self.overall_remaining_time_label.config(text=f"Voraussichtliche Gesamtzeit: {overall_remaining_time:.1f} s")
        except queue.Empty:
            pass
        self.after(100, self.update_progress_bars)

if __name__ == "__main__":
    app = SondenApp()
    app.mainloop()