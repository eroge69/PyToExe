import os
import subprocess
import sys
import ctypes
import time
import tkinter as tk
from tkinter import ttk, messagebox

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

def run_command(command, output_text=None):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output and output_text:
                output_text.insert(tk.END, output)
                output_text.see(tk.END)
                output_text.update()
        return True
    except Exception as e:
        if output_text:
            output_text.insert(tk.END, f"Fehler: {str(e)}\n")
            output_text.see(tk.END)
        return False

class NetworkFixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internet-Probleme Beheben")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Styling
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Internet-Probleme Beheben", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Output text area
        self.output_text = tk.Text(main_frame, height=15, width=70, wrap=tk.WORD)
        self.output_text.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Scrollbar for output text
        scrollbar = ttk.Scrollbar(self.output_text, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=10, fill=tk.X)
        
        # Fix buttons
        self.create_button(buttons_frame, "IP-Konfiguration zurücksetzen", self.reset_ip_config, 0, 0)
        self.create_button(buttons_frame, "DNS-Cache leeren", self.flush_dns, 0, 1)
        self.create_button(buttons_frame, "Netzwerkadapter neustarten", self.restart_adapter, 1, 0)
        self.create_button(buttons_frame, "Netzwerkdiagnose starten", self.run_network_diagnostics, 1, 1)
        self.create_button(buttons_frame, "System-Dateien prüfen", self.run_sfc_scan, 2, 0)
        self.create_button(buttons_frame, "Windows Update öffnen", self.open_windows_update, 2, 1)
        
        # Fix all button
        fix_all_button = ttk.Button(main_frame, text="Alle Probleme beheben", command=self.fix_all)
        fix_all_button.pack(pady=10, fill=tk.X)
        
        # Welcome message
        self.output_text.insert(tk.END, "Willkommen beim Internet-Problem-Beheber!\n\n")
        self.output_text.insert(tk.END, "Dieses Tool hilft dir, typische Netzwerkprobleme zu beheben.\n")
        self.output_text.insert(tk.END, "Wähle eine der Optionen oder klicke auf 'Alle Probleme beheben'.\n\n")
        self.output_text.insert(tk.END, "Hinweis: Einige Funktionen erfordern einen Neustart des Computers.\n")
    
    def create_button(self, parent, text, command, row, column):
        button = ttk.Button(parent, text=text, command=command)
        button.grid(row=row, column=column, padx=5, pady=5, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
    
    def reset_ip_config(self):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "IP-Konfiguration wird zurückgesetzt...\n")
        
        run_command("ipconfig /release", self.output_text)
        run_command("ipconfig /renew", self.output_text)
        run_command("netsh int ip reset", self.output_text)
        run_command("netsh winsock reset", self.output_text)
        
        self.output_text.insert(tk.END, "\nIP-Konfiguration wurde zurückgesetzt. Ein Neustart wird empfohlen.\n")
    
    def flush_dns(self):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "DNS-Cache wird geleert...\n")
        
        run_command("ipconfig /flushdns", self.output_text)
        
        self.output_text.insert(tk.END, "\nDNS-Cache wurde geleert.\n")
    
    def restart_adapter(self):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Netzwerkadapter werden neu gestartet...\n")
        
        run_command('powershell -Command "Get-NetAdapter | Where-Object Status -eq \'Up\' | Disable-NetAdapter -Confirm:$false"', self.output_text)
        time.sleep(3)
        run_command('powershell -Command "Get-NetAdapter | Where-Object Status -eq \'Disabled\' | Enable-NetAdapter -Confirm:$false"', self.output_text)
        
        self.output_text.insert(tk.END, "\nNetzwerkadapter wurden neu gestartet.\n")
    
    def run_network_diagnostics(self):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Netzwerkdiagnose wird gestartet...\n")
        
        run_command("msdt.exe /id NetworkDiagnosticsNetworkAdapter", self.output_text)
        
        self.output_text.insert(tk.END, "\nNetzwerkdiagnose wurde gestartet. Folge den Anweisungen im Diagnosefenster.\n")
    
    def run_sfc_scan(self):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "System-Dateien werden überprüft...\n")
        self.output_text.insert(tk.END, "Dies kann einige Minuten dauern...\n\n")
        
        run_command("sfc /scannow", self.output_text)
        
        self.output_text.insert(tk.END, "\nSystem-Dateien wurden überprüft.\n")
    
    def open_windows_update(self):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Windows Update wird geöffnet...\n")
        
        run_command("start ms-settings:windowsupdate", self.output_text)
        
        self.output_text.insert(tk.END, "\nWindows Update wurde geöffnet. Suche nach Updates und installiere sie.\n")
    
    def fix_all(self):
        if messagebox.askyesno("Alle Probleme beheben", "Dies wird alle Netzwerkeinstellungen zurücksetzen und kann einige Minuten dauern. Fortfahren?"):
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Alle Probleme werden behoben...\n\n")
            
            self.output_text.insert(tk.END, "1. DNS-Cache leeren...\n")
            run_command("ipconfig /flushdns", self.output_text)
            
            self.output_text.insert(tk.END, "\n2. IP-Konfiguration zurücksetzen...\n")
            run_command("ipconfig /release", self.output_text)
            run_command("ipconfig /renew", self.output_text)
            run_command("netsh int ip reset", self.output_text)
            run_command("netsh winsock reset", self.output_text)
            
            self.output_text.insert(tk.END, "\n3. Netzwerkadapter neustarten...\n")
            run_command('powershell -Command "Get-NetAdapter | Where-Object Status -eq \'Up\' | Disable-NetAdapter -Confirm:$false"', self.output_text)
            time.sleep(3)
            run_command('powershell -Command "Get-NetAdapter | Where-Object Status -eq \'Disabled\' | Enable-NetAdapter -Confirm:$false"', self.output_text)
            
            self.output_text.insert(tk.END, "\n4. Netzwerkdiagnose starten...\n")
            run_command("msdt.exe /id NetworkDiagnosticsNetworkAdapter", self.output_text)
            
            self.output_text.insert(tk.END, "\n5. Windows Update öffnen...\n")
            run_command("start ms-settings:windowsupdate", self.output_text)
            
            self.output_text.insert(tk.END, "\nAlle Problembehebungen wurden durchgeführt.\n")
            self.output_text.insert(tk.END, "Ein Neustart des Computers wird empfohlen, um alle Änderungen zu übernehmen.\n")

def main():
    # Check for admin rights
    run_as_admin()
    
    # Create GUI
    root = tk.Tk()
    app = NetworkFixApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
