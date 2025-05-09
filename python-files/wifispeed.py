import tkinter as tk
import speedtest
import threading
import subprocess
import platform
from tkinter import ttk

class WiFiSpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WiFi Speed Test")
        self.root.geometry("500x450")
        self.root.configure(bg="#f0f4f8")
        self.stop_threads = False
        self.first_measure = False

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 16), padding=10)
        style.configure("TLabel", font=("Arial", 16), background="#f0f4f8")

        # Título principal
        self.title_label = ttk.Label(root, text="Mide la velocidad de transmisión de tu WiFi", font=("Arial", 18, "bold"), background="#f0f4f8")
        self.title_label.pack(pady=15)

        # Obtener el nombre de la red WiFi
        wifi_name = self.get_wifi_name()
        self.wifi_label = ttk.Label(root, text=f"Conectado a: {wifi_name}", font=("Arial", 14), background="#f0f4f8", foreground="darkblue")
        self.wifi_label.pack(pady=5)

        # Etiquetas de velocidad
        self.download_label = ttk.Label(root, text="Velocidad de descarga: - Mbps", style="TLabel")
        self.download_label.pack(pady=10)

        self.upload_label = ttk.Label(root, text="Velocidad de subida: - Mbps", style="TLabel")
        self.upload_label.pack(pady=10)

        # Indicador de estado
        self.status_label = ttk.Label(root, text="Estado: Esperando actualización", font=("Arial", 14), foreground="grey", background="#f0f4f8")
        self.status_label.pack(pady=10)

        # Botón único
        self.action_button = ttk.Button(root, text="Calcular", command=self.start_measurement, style="TButton")
        self.action_button.pack(pady=20)

        # Progreso
        self.progress = ttk.Progressbar(root, orient="horizontal", length=350, mode="indeterminate")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_wifi_name(self):
        try:
            os_name = platform.system()
            if os_name == "Darwin":  # macOS
                result = subprocess.run(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"], capture_output=True, text=True)
                for line in result.stdout.split("\n"):
                    if " SSID:" in line:
                        return line.split(": ")[1].strip()
            elif os_name == "Linux":
                result = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True)
                return result.stdout.strip()
            elif os_name == "Windows":
                result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
                for line in result.stdout.split("\n"):
                    if " SSID" in line:
                        return line.split(": ")[1].strip()
            return "Desconocido"
        except Exception as e:
            print(f"Error obteniendo el nombre de la WiFi: {e}")
            return "Desconocido"

    def start_measurement(self):
        self.action_button.config(text="Calculando...", state=tk.DISABLED)
        self.update_speed()

    def measure_speed(self):
        try:
            st = speedtest.Speedtest()
            servers = st.get_servers()
            best = st.get_best_server()
            print(f"Usando servidor: {best['host']} ubicado en {best['name']}, {best['country']}")
            download_speed = st.download() / 1_000_000
            upload_speed = st.upload() / 1_000_000
            return download_speed, upload_speed
        except Exception as e:
            print(f"Error al medir la velocidad: {e}")
            return 0, 0

    def update_speed(self):
        self.status_label.config(text="Estado: Midiendo...", foreground="blue")
        self.progress.pack(pady=5)
        self.progress.start()

        def run_test():
            if self.stop_threads:
                return
            download, upload = self.measure_speed()
            self.download_label.config(text=f"Velocidad de descarga: {download:.2f} Mbps")
            self.upload_label.config(text=f"Velocidad de subida: {upload:.2f} Mbps")
            self.status_label.config(text="Estado: Actualizado", foreground="green")
            self.progress.stop()
            self.progress.pack_forget()
            self.action_button.config(text="Calcular", state=tk.NORMAL)

        self.speed_thread = threading.Thread(target=run_test)
        self.speed_thread.start()

    def on_closing(self):
        self.stop_threads = True
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiSpeedTestApp(root)
    root.mainloop()

