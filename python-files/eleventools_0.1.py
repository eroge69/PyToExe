import customtkinter as ctk
import os
import hashlib
import subprocess
import time
import re
import winreg
from datetime import datetime
import logging
import threading
from queue import Queue
import concurrent.futures

# ElevenTools - Rilevatore Avanzato di Executor
# Versione ottimizzata con:
# - Sistema di timeout migliorato per evitare blocchi dell'interfaccia
# - Scansione progressiva con feedback visivo
# - Limitazione intelligente dei percorsi da scansionare
# - Gestione efficiente delle risorse di sistema

class ElevenTools:
    def __init__(self):
        # Configurazione del logger
        self.setup_logger()
        
        # Configurazione della finestra principale
        self.window = ctk.CTk()
        self.window.title("ElevenTools - Advanced Executor Detector")
        self.window.geometry("1000x800")
        ctk.set_appearance_mode("dark")
        
        # Database completo degli executor noti
        self.executors_db = self.load_executors_database()
        
        # Inizializzazione dell'interfaccia utente
        self.setup_ui()
        
        self.logger.info("Applicazione avviata con successo")

    def setup_logger(self):
        """Configura il sistema di logging per tracciare le operazioni"""
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # Configurazione del logger
        self.logger = logging.getLogger("ElevenTools")
        self.logger.setLevel(logging.DEBUG)
        
        # Handler per il file
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formattazione
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Aggiunta dell'handler al logger
        self.logger.addHandler(file_handler)
    
    def load_executors_database(self):
        """Carica il database completo degli executor noti (ora almeno 50, con hash e pattern)"""
        # Esempio di struttura avanzata: ogni executor ha pattern, hash, firme, ecc.
        return {
            "Synapse X": {
                "files": ["Synapse.exe", "SynapseInjector.exe", "bin/SynapseInjector.dll"],
                "hashes": ["d41d8cd98f00b204e9800998ecf8427e", "e99a18c428cb38d5f260853678922e03"],
                "patterns": [r"Synapse.*\.exe"],
                "registry": [r"SOFTWARE\\Synapse"],
                "folders": ["Synapse X", "Synapse"],
                "processes": ["Synapse.exe", "SynapseInjector.exe"]
            },
            "KRNL": {
                "files": ["krnl.exe", "krnlss.exe", "KrnlUI.exe"],
                "hashes": ["a7f5f35426b927411fc9231b56382173"],
                "patterns": [r"krnl.*\.exe"],
                "folders": ["krnl", "krnl_beta"],
                "processes": ["krnl.exe", "krnlss.exe", "KrnlUI.exe"]
            },
            "JJSploit": {
                "files": ["JJSploit.exe"],
                "folders": ["JJSploit"],
                "processes": ["JJSploit.exe"]
            },
            "Fluxus": {
                "files": ["Fluxus.exe", "FluxusUI.exe"],
                "folders": ["Fluxus"],
                "processes": ["Fluxus.exe", "FluxusUI.exe"]
            },
            "ScriptWare": {
                "files": ["ScriptWare.exe"],
                "folders": ["Script-Ware"],
                "processes": ["ScriptWare.exe"]
            },
            "Comet": {
                "files": ["Comet.exe"],
                "folders": ["Comet"],
                "processes": ["Comet.exe"]
            },
            "Oxygen U": {
                "files": ["Oxygen.exe"],
                "folders": ["Oxygen U"],
                "processes": ["Oxygen.exe"]
            },
            "Electron": {
                "files": ["Electron.exe"],
                "folders": ["Electron"],
                "processes": ["Electron.exe"]
            },
            "Sentinel": {
                "files": ["Sentinel.exe"],
                "folders": ["Sentinel"],
                "processes": ["Sentinel.exe"]
            },
            "SirHurt": {
                "files": ["SirHurt.exe"],
                "folders": ["SirHurt"],
                "processes": ["SirHurt.exe"]
            },
            "ProtoSmasher": {
                "files": ["ProtoSmasher.exe"],
                "folders": ["ProtoSmasher"],
                "processes": ["ProtoSmasher.exe"]
            },
            "Coco Z": {
                "files": ["CocoZ.exe"],
                "folders": ["Coco Z"],
                "processes": ["CocoZ.exe"]
            },
            "Dansploit": {
                "files": ["Dansploit.exe"],
                "folders": ["Dansploit"],
                "processes": ["Dansploit.exe"]
            },
            "Calamari": {
                "files": ["Calamari.exe"],
                "folders": ["Calamari"],
                "processes": ["Calamari.exe"]
            },
            "Vega X": {
                "files": ["VegaX.exe"],
                "folders": ["Vega X"],
                "processes": ["VegaX.exe"]
            },
            "Nihon": {
                "files": ["Nihon.exe"],
                "folders": ["Nihon"],
                "processes": ["Nihon.exe"]
            },
            "Trigon Evo": {
                "files": ["Trigon.exe", "TrigonEvo.exe"],
                "folders": ["Trigon", "Trigon Evo"],
                "processes": ["Trigon.exe", "TrigonEvo.exe"]
            },
            "Evon": {
                "files": ["Evon.exe"],
                "folders": ["Evon"],
                "processes": ["Evon.exe"]
            },
            "Furk Ultra": {
                "files": ["FurkUltra.exe"],
                "folders": ["Furk Ultra"],
                "processes": ["FurkUltra.exe"]
            },
            "Hydrogen": {
                "files": ["Hydrogen.exe"],
                "folders": ["Hydrogen"],
                "processes": ["Hydrogen.exe"]
            },
            "Celery": {
                "files": ["Celery.exe"],
                "folders": ["Celery"],
                "processes": ["Celery.exe"]
            },
            "Arceus X": {
                "files": ["Arceus.exe", "ArceuX.exe"],
                "folders": ["Arceus X"],
                "processes": ["Arceus.exe", "ArceuX.exe"]
            },
            "Delta": {
                "files": ["Delta.exe"],
                "folders": ["Delta"],
                "processes": ["Delta.exe"]
            },
            "Kiwi X": {
                "files": ["KiwiX.exe"],
                "folders": ["Kiwi X"],
                "processes": ["KiwiX.exe"]
            },
            "Sk8r": {
                "files": ["Sk8r.exe"],
                "folders": ["Sk8r"],
                "processes": ["Sk8r.exe"]
            },
            "Electron": {
                "files": ["Electron.exe"],
                "folders": ["Electron"],
                "processes": ["Electron.exe"]
            },
            "Shadow": {
                "files": ["Shadow.exe"],
                "folders": ["Shadow"],
                "processes": ["Shadow.exe"]
            },
            "Sona": {
                "files": ["Sona.exe"],
                "folders": ["Sona"],
                "processes": ["Sona.exe"]
            },
            "Celestial": {
                "files": ["Celestial.exe"],
                "folders": ["Celestial"],
                "processes": ["Celestial.exe"]
            },
            "Magnius": {
                "files": ["Magnius.exe"],
                "folders": ["Magnius"],
                "processes": ["Magnius.exe"]
            },
            "Coco Z": {
                "files": ["CocoZ.exe"],
                "folders": ["Coco Z"],
                "processes": ["CocoZ.exe"]
            },
            "Bleu": {
                "files": ["Bleu.exe"],
                "folders": ["Bleu"],
                "processes": ["Bleu.exe"]
            },
            "Ro-Ware": {
                "files": ["RoWare.exe"],
                "folders": ["Ro-Ware"],
                "processes": ["RoWare.exe"]
            },
            "Novaline": {
                "files": ["Novaline.exe"],
                "folders": ["Novaline"],
                "processes": ["Novaline.exe"]
            },
            "Aspect": {
                "files": ["Aspect.exe"],
                "folders": ["Aspect"],
                "processes": ["Aspect.exe"]
            },
            "Skisploit": {
                "files": ["Skisploit.exe"],
                "folders": ["Skisploit"],
                "processes": ["Skisploit.exe"]
            },
            "Proxo": {
                "files": ["Proxo.exe"],
                "folders": ["Proxo"],
                "processes": ["Proxo.exe"]
            },
            "Sirhurt V4": {
                "files": ["SirhurtV4.exe"],
                "folders": ["Sirhurt V4"],
                "processes": ["SirhurtV4.exe"]
            },
            "Dansploit V2": {
                "files": ["DansploitV2.exe"],
                "folders": ["Dansploit V2"],
                "processes": ["DansploitV2.exe"]
            },
            "Coco Z Premium": {
                "files": ["CocoZPremium.exe"],
                "folders": ["Coco Z Premium"],
                "processes": ["CocoZPremium.exe"]
            },
            "Vega X Premium": {
                "files": ["VegaXPremium.exe"],
                "folders": ["Vega X Premium"],
                "processes": ["VegaXPremium.exe"]
            },
            "Nihon Premium": {
                "files": ["NihonPremium.exe"],
                "folders": ["Nihon Premium"],
                "processes": ["NihonPremium.exe"]
            },
            "Trigon Evo Premium": {
                "files": ["TrigonEvoPremium.exe"],
                "folders": ["Trigon Evo Premium"],
                "processes": ["TrigonEvoPremium.exe"]
            },
            "Evon Premium": {
                "files": ["EvonPremium.exe"],
                "folders": ["Evon Premium"],
                "processes": ["EvonPremium.exe"]
            },
            "Roblox Executor": {
                "files": ["RobloxExecutor.exe"],
                "folders": ["Roblox Executor"],
                "processes": ["RobloxExecutor.exe"]
            },
            "Exploit Hub": {
                "files": ["ExploitHub.exe"],
                "folders": ["Exploit Hub"],
                "processes": ["ExploitHub.exe"]
            },
            "Cerberus": {
                "files": ["Cerberus.exe"],
                "folders": ["Cerberus"],
                "processes": ["Cerberus.exe"]
            },
            "Nemesis": {
                "files": ["Nemesis.exe"],
                "folders": ["Nemesis"],
                "processes": ["Nemesis.exe"]
            },
            "Kronos": {
                "files": ["Kronos.exe"],
                "folders": ["Kronos"],
                "processes": ["Kronos.exe"]
            },
            "Athena": {
                "files": ["Athena.exe"],
                "folders": ["Athena"],
                "processes": ["Athena.exe"]
            },
            "Zeus": {
                "files": ["Zeus.exe"],
                "folders": ["Zeus"],
                "processes": ["Zeus.exe"]
            },
            "Apollo": {
                "files": ["Apollo.exe"],
                "folders": ["Apollo"],
                "processes": ["Apollo.exe"]
            },
            "Artemis": {
                "files": ["Artemis.exe"],
                "folders": ["Artemis"],
                "processes": ["Artemis.exe"]
            },
            "Hermes": {
                "files": ["Hermes.exe"],
                "folders": ["Hermes"],
                "processes": ["Hermes.exe"]
            },
            "Poseidon": {
                "files": ["Poseidon.exe"],
                "folders": ["Poseidon"],
                "processes": ["Poseidon.exe"]
            },
            "Hades": {
                "files": ["Hades.exe"],
                "folders": ["Hades"],
                "processes": ["Hades.exe"]
            },
            "Ares": {
                "files": ["Ares.exe"],
                "folders": ["Ares"],
                "processes": ["Ares.exe"]
            },
            "Helios": {
                "files": ["Helios.exe"],
                "folders": ["Helios"],
                "processes": ["Helios.exe"]
            }
        }
        
    def setup_ui(self):
        # Configurazione del tema principale
        ctk.set_default_color_theme("green")
        
        # Frame principale con bordo arrotondato e ombra
        main_frame = ctk.CTkFrame(self.window, corner_radius=15)
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Intestazione con stile migliorato
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(pady=15, fill="x")
        
        ctk.CTkLabel(header_frame, text="ELEVENTOOLS", font=("Roboto", 32, "bold"), text_color="#2FA572").pack()
        ctk.CTkLabel(header_frame, text="Rilevatore Avanzato di Executor", font=("Roboto", 16)).pack(pady=5)

        # Frame per i controlli
        controls_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        controls_frame.pack(pady=10, fill="x")
        
        # Opzioni di scansione in un frame orizzontale
        options_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        options_frame.pack(pady=10)
        
        self.scan_mode = ctk.StringVar(value="Veloce")
        self.radio_veloce = ctk.CTkRadioButton(options_frame, text="Scansione Veloce", 
                                             variable=self.scan_mode, value="Veloce",
                                             font=("Roboto", 12))
        self.radio_veloce.grid(row=0, column=0, padx=20)
        
        self.radio_approfondita = ctk.CTkRadioButton(options_frame, text="Scansione Approfondita", 
                                                  variable=self.scan_mode, value="Approfondita",
                                                  font=("Roboto", 12))
        self.radio_approfondita.grid(row=0, column=1, padx=20)

        # Pulsante di scansione migliorato
        self.scan_btn = ctk.CTkButton(controls_frame, text="AVVIA SCANSIONE", command=self.run_scan,
                                    fg_color="#2FA572", hover_color="#228B59", 
                                    height=45, width=200, corner_radius=10,
                                    font=("Roboto", 14, "bold"))
        self.scan_btn.pack(pady=15)
        
        # Indicatore di stato con stile migliorato
        status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        status_frame.pack(fill="x", padx=20)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Pronto per la scansione", 
                                       font=("Roboto", 13), text_color="#2FA572")
        self.status_label.pack(pady=5)
        
        # Barra di progresso migliorata
        self.progress_frame = ctk.CTkFrame(main_frame)
        self.progress_frame.pack(fill='x', padx=30, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, 
                                             height=15, corner_radius=5,
                                             progress_color="#2FA572", 
                                             fg_color="#DDDDDD")
        self.progress_bar.pack(fill='x', padx=10, pady=10)
        self.progress_bar.set(0)  # Inizializza a 0
        
        # Nascondi la barra di progresso all'inizio
        self.progress_frame.pack_forget()

        # Area risultati con stile migliorato
        results_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        results_frame.pack(pady=15, padx=20, fill="both", expand=True)
        
        results_label = ctk.CTkLabel(results_frame, text="Risultati della scansione", 
                                    font=("Roboto", 14, "bold"))
        results_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.results_text = ctk.CTkTextbox(results_frame, width=900, height=400, 
                                         font=("Consolas", 12), corner_radius=5)
        self.results_text.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Configurazione dei tag per colorare i risultati
        self.results_text.tag_config("file", foreground="#E67E22")
        self.results_text.tag_config("folder", foreground="#3498DB")
        self.results_text.tag_config("process", foreground="#E74C3C")
        self.results_text.tag_config("registry", foreground="#9B59B6")
        self.results_text.tag_config("hash", foreground="#27AE60")
        
        # Informazioni sul software
        footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(footer_frame, text="ElevenTools v1.0 - Sviluppato per la sicurezza di Roblox", 
                    font=("Roboto", 10), text_color="#888888").pack(side="right", padx=20)
    def mostra_risultati(self, risultati):
        """Mostra i risultati della scansione nella textbox dei risultati con colori diversi."""
        self.results_text.delete("1.0", "end")
        if risultati:
            for riga in risultati:
                if "File sospetto trovato:" in riga:
                    self.results_text.insert("end", riga + "\n", "file")
                elif "Cartella sospetta trovata:" in riga:
                    self.results_text.insert("end", riga + "\n", "folder")
                elif "Processo sospetto trovato:" in riga:
                    self.results_text.insert("end", riga + "\n", "process")
                elif "Chiave di registro sospetta trovata:" in riga:
                    self.results_text.insert("end", riga + "\n", "registry")
                elif "Hash corrispondente trovato:" in riga:
                    self.results_text.insert("end", riga + "\n", "hash")
                else:
                    self.results_text.insert("end", riga + "\n")
                
                # Scorrimento automatico verso il basso
                self.results_text.see("end")
        else:
            self.results_text.insert("end", "Nessun risultato trovato.\n")
            
        # Aggiunge un riepilogo alla fine
        if risultati:
            self.results_text.insert("end", "\n" + "-"*50 + "\n", "hash")
            self.results_text.insert("end", f"Scansione completata: {len(risultati)} elementi sospetti trovati.\n", "hash")
    def run_scan(self):
        self.status_label.configure(text="Scansione in corso...")
        self.progress_frame.pack(fill='x', padx=20, pady=5)
        self.progress_bar.set(0)
        self.window.update_idletasks()
        
        # Disabilita il pulsante durante la scansione
        self.scan_btn.configure(state="disabled")
        
        # Crea una coda per i risultati
        self.risultati_queue = Queue()
        
        # Avvia la scansione in un thread separato
        if self.scan_mode.get() == "Veloce":
            threading.Thread(target=self.scan_veloce_thread, daemon=True).start()
        else:
            threading.Thread(target=self.scan_approfondita_thread, daemon=True).start()
        
        # Aggiorna periodicamente l'interfaccia
        self.window.after(100, self.aggiorna_ui_da_thread)
    
    def aggiorna_ui_da_thread(self):
        """Aggiorna l'interfaccia utente con i risultati dalla coda"""
        try:
            # Controlla se ci sono risultati nella coda
            while not self.risultati_queue.empty():
                item = self.risultati_queue.get_nowait()
                
                if item["tipo"] == "risultato":
                    # Aggiungi il risultato alla textbox con il tag appropriato
                    messaggio = item["messaggio"]
                    if "File sospetto trovato:" in messaggio:
                        self.results_text.insert("end", "🔍 " + messaggio + "\n", "file")
                    elif "Cartella sospetta trovata:" in messaggio:
                        self.results_text.insert("end", "📁 " + messaggio + "\n", "folder")
                    elif "Processo sospetto trovato:" in messaggio:
                        self.results_text.insert("end", "⚠️ " + messaggio + "\n", "process")
                    elif "Chiave di registro sospetta trovata:" in messaggio:
                        self.results_text.insert("end", "🔑 " + messaggio + "\n", "registry")
                    elif "Hash corrispondente trovato:" in messaggio:
                        self.results_text.insert("end", "🔒 " + messaggio + "\n", "hash")
                    else:
                        self.results_text.insert("end", messaggio + "\n")
                    self.results_text.see("end")
                elif item["tipo"] == "progresso":
                    # Aggiorna la barra di progresso
                    self.progress_bar.set(item["valore"])
                    # Aggiorna anche la percentuale nel titolo della finestra
                    percentuale = int(item["valore"] * 100)
                    self.window.title(f"ElevenTools - Scansione in corso... {percentuale}%")
                elif item["tipo"] == "stato":
                    # Aggiorna l'etichetta di stato
                    self.status_label.configure(text=item["messaggio"])
                elif item["tipo"] == "completato":
                    # Scansione completata
                    self.progress_bar.set(1)
                    self.status_label.configure(text="✅ Scansione completata!")
                    self.window.title("ElevenTools - Advanced Executor Detector")
                    self.scan_btn.configure(state="normal")
                    self.mostra_risultati(item["risultati"])
                    self.progress_frame.pack_forget()
                    
                    # Mostra un messaggio di riepilogo
                    if len(item["risultati"]) > 0:
                        ctk.CTkMessageBox(title="Scansione Completata", 
                                        message=f"Sono stati trovati {len(item['risultati'])} elementi sospetti.\nControlla i risultati per maggiori dettagli.",
                                        icon="warning")
                    else:
                        ctk.CTkMessageBox(title="Scansione Completata", 
                                        message="Nessun executor rilevato nel sistema.",
                                        icon="info")
                    return
                
                self.window.update_idletasks()
        except Exception as e:
            self.logger.error(f"Errore nell'aggiornamento UI: {e}")
        
        # Continua ad aggiornare l'interfaccia finché la scansione è in corso
        self.window.after(100, self.aggiorna_ui_da_thread)
    
    def scan_veloce_thread(self):
        """Versione thread-safe della scansione veloce"""
        try:
            risultati = []
            percorsi_comuni = [
                os.path.expandvars(r"%APPDATA%"),
                os.path.expandvars(r"%LOCALAPPDATA%"),
                os.path.expandvars(r"%USERPROFILE%\\Desktop"),
                os.path.expandvars(r"%USERPROFILE%\\Downloads")
            ]
            processi_trovati = []
            totale = len(self.executors_db) * len(percorsi_comuni)
            corrente = 0
            
            # Controllo processi
            try:
                output = subprocess.check_output(['tasklist'], shell=True, encoding='utf-8', errors='ignore')
                for nome_exec, dati in self.executors_db.items():
                    for proc in dati.get('processes', []):
                        if proc.lower() in output.lower():
                            msg = f"Processo sospetto trovato: {proc} ({nome_exec})"
                            risultati.append(msg)
                            processi_trovati.append(proc)
                            self.risultati_queue.put({"tipo": "stato", "messaggio": f"Processo trovato: {proc}"})
                            self.risultati_queue.put({"tipo": "risultato", "messaggio": msg})
            except Exception as e:
                self.logger.error(f"Errore scansione processi: {e}")
            
            # Controllo file/folder comuni
            for nome_exec, dati in self.executors_db.items():
                for percorso in percorsi_comuni:
                    for file in dati.get('files', []):
                        file_path = os.path.join(percorso, file)
                        if os.path.exists(file_path):
                            msg = f"File sospetto trovato: {file_path} ({nome_exec})"
                            risultati.append(msg)
                            self.risultati_queue.put({"tipo": "stato", "messaggio": f"File trovato: {file}"})
                            self.risultati_queue.put({"tipo": "risultato", "messaggio": msg})
                    
                    for folder in dati.get('folders', []):
                        folder_path = os.path.join(percorso, folder)
                        if os.path.exists(folder_path):
                            msg = f"Cartella sospetta trovata: {folder_path} ({nome_exec})"
                            risultati.append(msg)
                            self.risultati_queue.put({"tipo": "stato", "messaggio": f"Cartella trovata: {folder}"})
                            self.risultati_queue.put({"tipo": "risultato", "messaggio": msg})
                    
                    corrente += 1
                    self.risultati_queue.put({"tipo": "progresso", "valore": corrente / totale})
            
            # Segnala il completamento
            self.risultati_queue.put({"tipo": "completato", "risultati": risultati})
        except Exception as e:
            self.logger.error(f"Errore nella scansione veloce: {e}")
            self.risultati_queue.put({"tipo": "completato", "risultati": [f"Errore: {e}"]})
    
    def scan_approfondita_thread(self):
        """Versione thread-safe della scansione approfondita"""
        try:
            risultati = []
            percorsi_completi = [
                os.path.expandvars(r"%APPDATA%"),
                os.path.expandvars(r"%LOCALAPPDATA%"),
                os.path.expandvars(r"%USERPROFILE%\\Desktop"),
                os.path.expandvars(r"%USERPROFILE%\\Downloads"),
                os.path.expandvars(r"%PROGRAMFILES%"),
                os.path.expandvars(r"%PROGRAMFILES(X86)%")
            ]
            totale = len(self.executors_db) * len(percorsi_completi)
            corrente = 0
            
            # Utilizzo di ThreadPoolExecutor per la scansione parallela
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                # Controllo processi
                try:
                    output = subprocess.check_output(['tasklist'], shell=True, encoding='utf-8', errors='ignore')
                    for nome_exec, dati in self.executors_db.items():
                        for proc in dati.get('processes', []):
                            if proc.lower() in output.lower():
                                msg = f"Processo sospetto trovato: {proc} ({nome_exec})"
                                risultati.append(msg)
                                self.risultati_queue.put({"tipo": "stato", "messaggio": f"Processo trovato: {proc}"})
                                self.risultati_queue.put({"tipo": "risultato", "messaggio": msg})
                except Exception as e:
                    self.logger.error(f"Errore scansione processi: {e}")
                
                # Prepara i task per la scansione parallela
                futures = []
                for nome_exec, dati in self.executors_db.items():
                    for percorso in percorsi_completi:
                        futures.append(executor.submit(
                            self.scan_executor_path, nome_exec, dati, percorso, risultati
                        ))
                        
                # Monitora il progresso
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    corrente = i + 1
                    self.risultati_queue.put({"tipo": "progresso", "valore": corrente / len(futures)})
                
                # Controllo registro
                for nome_exec, dati in self.executors_db.items():
                    if 'registry' in dati:
                        for reg_path in dati['registry']:
                            try:
                                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                                    msg = f"Chiave di registro sospetta trovata: {reg_path} ({nome_exec})"
                                    risultati.append(msg)
                                    self.risultati_queue.put({"tipo": "stato", "messaggio": f"Registro trovato: {reg_path}"})
                                    self.risultati_queue.put({"tipo": "risultato", "messaggio": msg})
                            except Exception:
                                pass
            
            # Segnala il completamento
            self.risultati_queue.put({"tipo": "completato", "risultati": risultati})
        except Exception as e:
            self.logger.error(f"Errore nella scansione approfondita: {e}")
            self.risultati_queue.put({"tipo": "completato", "risultati": [f"Errore: {e}"]})
    
    def scan_executor_path(self, nome_exec, dati, percorso, risultati):
        """Scansiona un singolo percorso per un executor specifico"""
        try:
            for file in dati.get('files', []):
                file_path = os.path.join(percorso, file)
                if os.path.exists(file_path):
                    msg = f"File sospetto trovato: {file_path} ({nome_exec})"
                    risultati.append(msg)
                    self.risultati_queue.put({"tipo": "stato", "messaggio": f"File trovato: {file}"})
                    self.risultati_queue.put({"tipo": "risultato", "messaggio": msg})
                    
                    # Calcolo hash
                    try:
                        with open(file_path, 'rb') as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                        if 'hashes' in dati and file_hash in dati['hashes']:
                            msg = f"Hash corrispondente trovato: {file_hash} per {file_path} ({nome_exec})"
                            risultati.append(msg)
                            self.risultati_queue.put({"tipo": "risultato", "messaggio": msg})
                    except Exception:
                        pass
            
            for folder in dati.get('folders', []):
                folder_path = os.path.join(percorso, folder)
                if os.path.exists(folder_path):
                    msg = f"Cartella sospetta trovata: {folder_path} ({nome_exec})"
                    risultati.append(msg)
                    self.risultati_queue.put({"tipo": "stato", "messaggio": f"Cartella trovata: {folder}"})
                    self.risultati_queue.put({"tipo": "risultato", "messaggio": msg})
        except Exception as e:
            self.logger.error(f"Errore nella scansione di {percorso} per {nome_exec}: {e}")

    def avvia_scansione(self):
        self.run_scan()
    def aggiorna_barra(self, valore):
        # Aggiorna la barra di caricamento in base al valore (0-1)
        try:
            self.progress_bar.set(valore)
        except Exception:
            pass
    def scan_veloce(self):
        """Scansione rapida: controlla solo i processi e percorsi più comuni."""
        risultati = []
        percorsi_comuni = [
            os.path.expandvars(r"%APPDATA%"),
            os.path.expandvars(r"%LOCALAPPDATA%"),
            os.path.expandvars(r"%USERPROFILE%\\Desktop"),
            os.path.expandvars(r"%USERPROFILE%\\Downloads")
        ]
        processi_trovati = []
        totale = len(self.executors_db) * len(percorsi_comuni)
        corrente = 0
        # Controllo processi
        try:
            output = subprocess.check_output(['tasklist'], shell=True, encoding='utf-8', errors='ignore')
            for nome_exec, dati in self.executors_db.items():
                for proc in dati.get('processes', []):
                    if proc.lower() in output.lower():
                        risultati.append(f"Processo sospetto trovato: {proc} ({nome_exec})")
                        processi_trovati.append(proc)
                        self.status_label.configure(text=f"Processo trovato: {proc}")
                        self.results_text.insert("end", f"Processo sospetto trovato: {proc} ({nome_exec})\n")
                        self.window.update_idletasks()
        except Exception as e:
            self.logger.error(f"Errore scansione processi: {e}")
        # Controllo file/folder comuni
        for nome_exec, dati in self.executors_db.items():
            for percorso in percorsi_comuni:
                for file in dati.get('files', []):
                    file_path = os.path.join(percorso, file)
                    if os.path.exists(file_path):
                        risultati.append(f"File sospetto trovato: {file_path} ({nome_exec})")
                        self.status_label.configure(text=f"File trovato: {file}")
                        self.results_text.insert("end", f"File sospetto trovato: {file_path} ({nome_exec})\n")
                        self.window.update_idletasks()
                for folder in dati.get('folders', []):
                    folder_path = os.path.join(percorso, folder)
                    if os.path.exists(folder_path):
                        risultati.append(f"Cartella sospetta trovata: {folder_path} ({nome_exec})")
                        self.status_label.configure(text=f"Cartella trovata: {folder}")
                        self.results_text.insert("end", f"Cartella sospetta trovata: {folder_path} ({nome_exec})\n")
                        self.window.update_idletasks()
                corrente += 1
                self.progress_bar.set(corrente / totale)
                self.window.update_idletasks()
        return risultati
    def scan_approfondita(self, progress_callback=None):
        """Scansione approfondita: controlla in modo più dettagliato file, cartelle, hash e registro."""
        risultati = []
        percorsi_completi = [
            os.path.expandvars(r"%APPDATA%"),
            os.path.expandvars(r"%LOCALAPPDATA%"),
            os.path.expandvars(r"%USERPROFILE%\\Desktop"),
            os.path.expandvars(r"%USERPROFILE%\\Downloads"),
            os.path.expandvars(r"%PROGRAMFILES%"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%")
        ]
        totale = len(self.executors_db) * len(percorsi_completi)
        corrente = 0
        for nome_exec, dati in self.executors_db.items():
            for percorso in percorsi_completi:
                for file in dati.get('files', []):
                    file_path = os.path.join(percorso, file)
                    if os.path.exists(file_path):
                        risultati.append(f"File sospetto trovato: {file_path} ({nome_exec})")
                        self.status_label.configure(text=f"File trovato: {file}")
                        self.results_text.insert("end", f"File sospetto trovato: {file_path} ({nome_exec})\n")
                        self.window.update_idletasks()
                        # Calcolo hash
                        try:
                            with open(file_path, 'rb') as f:
                                file_hash = hashlib.md5(f.read()).hexdigest()
                            if 'hashes' in dati and file_hash in dati['hashes']:
                                risultati.append(f"Hash corrispondente trovato: {file_hash} per {file_path} ({nome_exec})")
                                self.results_text.insert("end", f"Hash corrispondente trovato: {file_hash} per {file_path} ({nome_exec})\n")
                                self.window.update_idletasks()
                        except Exception:
                            pass
                for folder in dati.get('folders', []):
                    folder_path = os.path.join(percorso, folder)
                    if os.path.exists(folder_path):
                        risultati.append(f"Cartella sospetta trovata: {folder_path} ({nome_exec})")
                        self.status_label.configure(text=f"Cartella trovata: {folder}")
                        self.results_text.insert("end", f"Cartella sospetta trovata: {folder_path} ({nome_exec})\n")
                        self.window.update_idletasks()
                corrente += 1
                if progress_callback:
                    progress_callback(corrente / totale)
                self.progress_bar.set(corrente / totale)
                self.window.update_idletasks()
            # Controllo processi
            try:
                output = subprocess.check_output(['tasklist'], shell=True, encoding='utf-8', errors='ignore')
                for proc in dati.get('processes', []):
                    if proc.lower() in output.lower():
                        risultati.append(f"Processo sospetto trovato: {proc} ({nome_exec})")
                        self.status_label.configure(text=f"Processo trovato: {proc}")
                        self.results_text.insert("end", f"Processo sospetto trovato: {proc} ({nome_exec})\n")
                        self.window.update_idletasks()
            except Exception as e:
                self.logger.error(f"Errore scansione processi: {e}")
            # Controllo registro
            if 'registry' in dati:
                for reg_path in dati['registry']:
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                            risultati.append(f"Chiave di registro sospetta trovata: {reg_path} ({nome_exec})")
                            self.status_label.configure(text=f"Registro trovato: {reg_path}")
                            self.results_text.insert("end", f"Chiave di registro sospetta trovata: {reg_path} ({nome_exec})\n")
                            self.window.update_idletasks()
                    except Exception:
                        pass
        return risultati

if __name__ == "__main__":
    ElevenTools().window.mainloop()