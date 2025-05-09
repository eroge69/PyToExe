#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mega Gestor de Descargas – Versión Modular Mejorada (sugerencias 1 a 9)
Con:
  - Modo claro/oscuro configurable.
  - Todos los botones con bordes redondeados (pill) de color cian.
  - Panel de estadísticas y gráfico en tiempo real (UI/UX mejorado).
  - Integración con Google Drive (vía PyDrive) y soporte básico para Dropbox y OneDrive.
  - Opción de asignar un icono personalizado en el que se busca el archivo "iconoxd.png" 
    (entre todos los *.png del directorio se usará ese).
  
Requisitos:
  pip install ttkbootstrap aiohttp feedparser plyer pydrive matplotlib
  (además de las dependencias estándar: sqlite3, asyncio, glob, etc.)
"""

import sys, os, time, datetime, logging, sqlite3, hashlib, asyncio, aiohttp, feedparser
import threading
import glob  # Para buscar archivos .png
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
try:
    from plyer import notification
except ImportError:
    notification = None

# Importar Matplotlib (para el panel de gráficos)
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --------------------------- Logging Avanzado ---------------------------
logging.basicConfig(level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='gestor_log.txt',
    filemode='a')

# --------------------------- 1. Configuration Manager -----------------------
class ConfigurationManager:
    """Administra la persistencia de la configuración y el historial en SQLite."""
    def __init__(self, db_path='gestor_config.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()
    
    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                filepath TEXT,
                timestamp TEXT
            )
        """)
        self.conn.commit()
    
    def get_setting(self, key, default=None):
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else default
    
    def set_setting(self, key, value):
        cur = self.conn.cursor()
        cur.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()
    
    def add_history(self, url, filepath):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO history (url, filepath, timestamp) VALUES (?, ?, ?)",
                    (url, filepath, datetime.datetime.now().isoformat()))
        self.conn.commit()

    def close(self):
        self.conn.close()


# --------------------- 7. Plugin Manager (Stub) -----------------------------
class PluginManager:
    """Carga plugins desde un directorio; aquí se muestra como un stub."""
    def __init__(self, plugins_folder='plugins'):
        self.plugins_folder = plugins_folder
        self.plugins = []
        self.load_plugins()

    def load_plugins(self):
        if not os.path.exists(self.plugins_folder):
            os.makedirs(self.plugins_folder)
        logging.info("PluginManager: No hay plugins cargados (stub).")
        self.plugins = []


# ---------------------------- 2. Download Task ------------------------------
class DownloadTask:
    """Representa una descarga asíncrona."""
    def __init__(self, url, dest, expected_md5=None, expected_sha256=None):
        self.url = url
        self.dest = dest
        self.expected_md5 = expected_md5
        self.expected_sha256 = expected_sha256
        self.progress = 0.0
        self.speed = 0.0
        self.eta = 0
        self.cancelled = False
        self.paused = False

    async def start_download(self, progress_callback=None):
        logging.info(f"Iniciando descarga: {self.url}")
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as resp:
                    total = int(resp.headers.get('Content-Length', 0))
                    os.makedirs(os.path.dirname(self.dest), exist_ok=True)
                    with open(self.dest, 'wb') as f:
                        downloaded = 0
                        async for chunk in resp.content.iter_chunked(1024):
                            if self.cancelled:
                                logging.info("Descarga cancelada.")
                                return False
                            while self.paused:
                                await asyncio.sleep(0.5)
                            f.write(chunk)
                            downloaded += len(chunk)
                            self.progress = (downloaded / total * 100) if total > 0 else 0
                            elapsed = time.time() - start_time
                            self.speed = downloaded / elapsed if elapsed > 0 else 0
                            self.eta = int((total - downloaded) / self.speed) if self.speed > 0 else 0
                            if progress_callback:
                                progress_callback(self.progress, self.speed, self.eta)
            self.verify_integrity()
            logging.info("Descarga completada.")
            return True
        except Exception as e:
            logging.error(f"Error en descarga: {e}")
            return False

    def verify_integrity(self):
        """Verifica MD5 y SHA256 si se han proporcionado."""
        if self.expected_md5:
            computed = self.compute_hash(hashlib.md5())
            if computed != self.expected_md5:
                logging.warning("MD5 no coincide.")
                notify("Verificación MD5", "El MD5 del archivo no coincide con lo esperado.")
            else:
                logging.info("MD5 verificado correctamente.")
        if self.expected_sha256:
            computed = self.compute_hash(hashlib.sha256())
            if computed != self.expected_sha256:
                logging.warning("SHA256 no coincide.")
                notify("Verificación SHA256", "El SHA256 del archivo no coincide con lo esperado.")
            else:
                logging.info("SHA256 verificado correctamente.")

    def compute_hash(self, hash_func, block_size=4096):
        hash_obj = hash_func
        try:
            with open(self.dest, "rb") as f:
                for chunk in iter(lambda: f.read(block_size), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logging.error(f"Error computando hash: {e}")
            return None

    def pause(self):
        self.paused = True
        logging.info("Descarga pausada.")

    def resume(self):
        self.paused = False
        logging.info("Descarga reanudada.")

    def cancel(self):
        self.cancelled = True
        logging.info("Descarga cancelada.")


# ----------------------- 8. Notificaciones ----------------------------
def notify(title, message):
    if notification:
        notification.notify(title=title, message=message, timeout=5)
    else:
        logging.info(f"Notificación: {title} - {message}")


# ---------------------- 3. Panel de Estadísticas y Gráficos -------------------
class StatsPanel:
    """Panel que muestra estadísticas (label) y un gráfico en tiempo real de velocidad."""
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='x', pady=2)
        self.label = ttk.Label(self.frame, text="Velocidad: 0 KB/s, ETA: 0s", font=("Helvetica", 10))
        self.label.pack(side="top", fill='x')
        self.graph_panel = GraphPanel(self.frame)
    
    def update_stats(self, speed, eta):
        text = f"Velocidad: {speed/1024:.2f} KB/s, ETA: {eta}s"
        self.label.config(text=text)
        self.graph_panel.update_graph(speed)


class GraphPanel:
    """Panel que contiene un gráfico en tiempo real de la velocidad de descarga usando Matplotlib."""
    def __init__(self, parent):
        self.fig = Figure(figsize=(4,2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Velocidad de descarga (KB/s)")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("KB/s")
        self.xdata = []
        self.ydata = []
        self.line, = self.ax.plot([], [], "c-")  # Línea en color cian
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.start_time = time.time()
    
    def update_graph(self, speed):
        t = time.time() - self.start_time
        self.xdata.append(t)
        self.ydata.append(speed/1024)  # Convertir a KB/s
        self.line.set_data(self.xdata, self.ydata)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()


# ------------------------- 4. Download Manager ---------------------------
class DownloadManager:
    """Administra la cola de descargas asíncronas y actualiza callbacks en el GUI."""
    def __init__(self, config: ConfigurationManager):
        self.config = config
        self.tasks = []
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.run_loop, daemon=True).start()
    
    def run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def add_download(self, url, destination, expected_md5=None, expected_sha256=None, progress_callback=None):
        task = DownloadTask(url, destination, expected_md5, expected_sha256)
        self.tasks.append(task)
        asyncio.run_coroutine_threadsafe(task.start_download(progress_callback=progress_callback), self.loop)
        return task


# ----------------------- 1. Configuración UI Avanzada ------------------------
class ConfigWindow(ttk.Toplevel):
    """Ventana de Configuración para elegir el tema (modo claro/oscuro) y otros parámetros."""
    def __init__(self, master, config: ConfigurationManager, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Configuración")
        self.config_manager = config
        self.resizable(False, False)
        self.geometry("300x250")
        # Selección de tema: flatly (claro) o cyborg (oscuro)
        ttk.Label(self, text="Tema:").pack(pady=5)
        self.theme_var = tk.StringVar(value=self.config_manager.get_setting("theme", "flatly"))
        self.theme_combo = ttk.Combobox(self, textvariable=self.theme_var, values=["flatly", "cyborg"], state="readonly")
        self.theme_combo.pack(pady=5)
        # Velocidad predeterminada
        ttk.Label(self, text="Velocidad predeterminada (KB/s):").pack(pady=5)
        self.speed_var = tk.StringVar(value=self.config_manager.get_setting("speed", "1024"))
        self.speed_entry = ttk.Entry(self, textvariable=self.speed_var)
        self.speed_entry.pack(pady=5)
        # Modo oscuro (checkbutton)
        self.dark_mode = tk.BooleanVar(value=self.config_manager.get_setting("dark_mode", "False")=="True")
        self.dark_check = ttk.Checkbutton(self, text="Modo Oscuro", variable=self.dark_mode)
        self.dark_check.pack(pady=5)
        ttk.Button(self, text="Guardar", command=self.save_config, bootstyle="info pill").pack(pady=10)
    
    def save_config(self):
        self.config_manager.set_setting("theme", self.theme_var.get())
        self.config_manager.set_setting("speed", self.speed_var.get())
        self.config_manager.set_setting("dark_mode", str(self.dark_mode.get()))
        messagebox.showinfo("Configuración", "Configuración guardada. Reinicia la aplicación para aplicar cambios.")
        self.destroy()


# ---------------------------- UI Principal --------------------------
class GestorDescargasGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mega Gestor de Descargas")
        self.config_manager = ConfigurationManager()
        self.plugin_manager = PluginManager()
        self.download_manager = DownloadManager(self.config_manager)

        # Menú superior (sin bootstyle, ya que Menu no lo admite)
        menubar = ttk.Menu(root)
        config_menu = ttk.Menu(menubar, tearoff=0)
        config_menu.add_command(label="Configuración", command=self.open_config)
        menubar.add_cascade(label="Opciones", menu=config_menu)
        root.config(menu=menubar)
        
        # Panel superior: ingreso de URL
        top_frame = ttk.Frame(root, padding=10)
        top_frame.pack(fill="x")
        self.url_entry = ttk.Entry(top_frame, width=60)
        self.url_entry.pack(side="left", padx=5)
        ttk.Button(top_frame, text="Agregar URL", command=self.agregar_descarga, bootstyle="info pill").pack(side="left", padx=5)
        
        # Panel de Estadísticas y gráfico
        self.stats_panel = StatsPanel(top_frame)
        
        # Vista en árbol para mostrar descargas activas
        self.tree = ttk.Treeview(root, columns=("URL", "Progreso"), show="headings")
        self.tree.heading("URL", text="Enlace")
        self.tree.heading("Progreso", text="Progreso (%)")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Botones de control de descarga
        control_frame = ttk.Frame(root, padding=10)
        control_frame.pack(fill="x")
        ttk.Button(control_frame, text="Pausar", command=self.pause_selected, bootstyle="info pill").pack(side="left", padx=5)
        ttk.Button(control_frame, text="Reanudar", command=self.resume_selected, bootstyle="info pill").pack(side="left", padx=5)
        ttk.Button(control_frame, text="Cancelar", command=self.cancel_selected, bootstyle="info pill").pack(side="left", padx=5)
        
        # Historial: obtenido de la DB
        hist_frame = ttk.Frame(root, padding=10)
        hist_frame.pack(fill="both", expand=True)
        ttk.Label(hist_frame, text="Historial de Descargas").pack()
        self.hist_list = tk.Listbox(hist_frame, height=5)
        self.hist_list.pack(fill="both", expand=True)
        self.load_history()
        
        # Panel de integración en la nube
        cloud_frame = ttk.Frame(root, padding=10)
        cloud_frame.pack(fill="x")
        ttk.Label(cloud_frame, text="Integración en la Nube:").pack(side="left")
        self.cloud_provider_var = tk.StringVar(value="Dropbox")
        self.cloud_provider_combo = ttk.Combobox(cloud_frame, textvariable=self.cloud_provider_var, 
                                                 values=["Dropbox", "Google Drive", "OneDrive"], state="readonly")
        self.cloud_provider_combo.pack(side="left", padx=5)
        self.token_entry = ttk.Entry(cloud_frame, width=30)
        self.token_entry.pack(side="left", padx=5)
        ttk.Button(cloud_frame, text="Subir Archivo", command=self.upload_selected_file, bootstyle="info pill").pack(side="left", padx=5)
    
    def open_config(self):
        ConfigWindow(self.root, self.config_manager)
    
    def agregar_descarga(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Advertencia", "Ingrese una URL")
            return
        speed = int(self.config_manager.get_setting("speed", "1024"))
        dest_dir = os.path.join("descargas", datetime.date.today().isoformat())
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, url.split("/")[-1])
        item = self.tree.insert("", "end", values=(url, "0.00"))
        
        def progress_cb(prog, spd, eta):
            self.tree.item(item, values=(url, f"{prog:.2f}"))
            self.stats_panel.update_stats(spd, eta)
        
        self.download_manager.add_download(url, dest, progress_callback=progress_cb)
        self.config_manager.add_history(url, dest)
        self.hist_list.insert(tk.END, f"{datetime.datetime.now().isoformat()} - {url}")
        notify("Descarga Agregada", f"La descarga de {url} ha iniciado.")
        self.url_entry.delete(0, tk.END)
    
    def pause_selected(self):
        messagebox.showinfo("Función", "Pausa: (función stub; implementar asignación de tareas)")
        
    def resume_selected(self):
        messagebox.showinfo("Función", "Reanudar: (función stub)")
    
    def cancel_selected(self):
        messagebox.showinfo("Función", "Cancelar: (función stub)")
    
    def load_history(self):
        cur = self.config_manager.conn.cursor()
        cur.execute("SELECT timestamp, url, filepath FROM history ORDER BY id DESC LIMIT 10")
        for ts, url, path in cur.fetchall():
            self.hist_list.insert(tk.END, f"{ts} - {url}")
    
    # ----------------- Integración en la Nube -----------------
    def upload_selected_file(self):
        file = filedialog.askopenfilename(title="Seleccione archivo para subir")
        if file:
            self.upload_archivo(file)
    
    def upload_archivo(self, archivo):
        provider = self.cloud_provider_var.get()
        token = self.token_entry.get().strip()
        if provider == "Dropbox":
            try:
                import dropbox
                dbx = dropbox.Dropbox(token)
                dest_path = "/" + os.path.basename(archivo)
                with open(archivo, "rb") as f:
                    dbx.files_upload(f.read(), dest_path, mode=dropbox.files.WriteMode.overwrite)
                messagebox.showinfo("Subida", f"{archivo} subido a Dropbox exitosamente.")
            except Exception as e:
                messagebox.showerror("Error en Dropbox", str(e))
        elif provider == "Google Drive":
            self.upload_to_gdrive(archivo)
        elif provider == "OneDrive":
            messagebox.showinfo("Subida", "Integración con OneDrive no implementada aún.")
        else:
            messagebox.showinfo("Subida", "No se ha seleccionado un proveedor de nube.")
    
    def upload_to_gdrive(self, archivo):
        try:
            from pydrive.auth import GoogleAuth
            from pydrive.drive import GoogleDrive
        except ImportError:
            messagebox.showerror("Error", "PyDrive no está instalado. Instala pydrive")
            return
        try:
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
            drive = GoogleDrive(gauth)
            drive_file = drive.CreateFile({'title': os.path.basename(archivo)})
            drive_file.SetContentFile(archivo)
            drive_file.Upload()
            messagebox.showinfo("Subida", f"{archivo} subido a Google Drive correctamente.")
        except Exception as e:
            messagebox.showerror("Error en Google Drive", str(e))


# --------------------- 9. Pruebas Unitarias (Esqueleto) ---------------------
def run_tests():
    import unittest

    class TestDownloadTask(unittest.TestCase):
        def test_compute_hash_md5(self):
            filename = "temp_test.txt"
            with open(filename, "w") as f:
                f.write("Prueba de hash.")
            task = DownloadTask("http://example.com", filename)
            computed = task.compute_hash(hashlib.md5)
            expected = hashlib.md5(b"Prueba de hash.").hexdigest()
            self.assertEqual(computed, expected)
            os.remove(filename)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestDownloadTask)
    unittest.TextTestRunner(verbosity=2).run(suite)


# --------------------------- Main de la Aplicación ---------------------------
def main_gui():
    # Recuperamos la configuración para determinar el tema
    cm_temp = ConfigurationManager()
    dark = cm_temp.get_setting("dark_mode", "False") == "True"
    theme = "cyborg" if dark else "flatly"
    cm_temp.close()
    root = ttk.Window(themename=theme)
    
    # Opción para asignar icono personalizado:
    # Usamos glob para buscar todos los archivos *.png y se verifica si existe uno llamado "iconoxd.png"
    png_files = glob.glob("*.png")
    icon_path = None
    for file in png_files:
        if file.lower() == "iconoxd.png":
            icon_path = file
            break
    if icon_path and os.path.exists(icon_path):
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon)
        # Alternativamente, si tienes un icono .ico, podrías usar:
        # root.iconbitmap(icon_path)
    
    # Configuramos globalmente la variante "info" para TButton: fondo cian y bordes redondeados (pill)
    style = ttk.Style()
    style.configure("TButton.info", background="#00FFFF", foreground="black", bordercolor="#00FFFF")
    
    app = GestorDescargasGUI(root)
    root.mainloop()


def main_cli():
    import argparse
    parser = argparse.ArgumentParser(description="Gestor de Descargas CLI")
    parser.add_argument("url", help="URL del archivo")
    parser.add_argument("--dest", help="Directorio de destino", default="descargas")
    parser.add_argument("--md5", help="Valor MD5 esperado", default=None)
    args = parser.parse_args()
    dest_dir = os.path.join(args.dest, datetime.date.today().isoformat())
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, args.url.split("/")[-1])
    task = DownloadTask(args.url, dest, expected_md5=args.md5)
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(task.start_download())
    if success:
        print("Descarga completada.")
    else:
        print("Error en la descarga.")


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_tests()
    elif len(sys.argv) > 1 and sys.argv[1].startswith("http"):
        main_cli()
    else:
        main_gui()
