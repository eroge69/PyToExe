import os
import subprocess
import sys
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import threading

# Set the SVN repository URLs
PLC_URL = "https://svn.danobatgroup.com/soraluce/Automatismos/Control Numerico/Heidenhain/TNC7 & TNC640/020.-Maquinas"
PILZ_URL = "https://svn.danobatgroup.com/soraluce/Automatismos/SAFETY/External Safety Control/PNOZ Multi2/TNC640/020.-Maquinas"
OROKORRAK_URL = "O:/00-Máquinas"
folder_name = 0
maquina_carpeta = ""
machine = ""
año = datetime.now().year

# Lista de dependencias necesarias
REQUIRED_PACKAGES = ["tkinter"]

def install_packages():
    """Instala los paquetes necesarios si no están instalados."""
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)  # Intenta importar el paquete
        except ImportError:
            print(f"El paquete '{package}' no está instalado. Instalando...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Instalar dependencias necesarias
install_packages()

# Function to process repository
def process_repo(repo_url,app):
    list_dirs(repo_url,app)

def copiar_carpeta(destino,app):
    origen = "D:\\PLANTILLA1"
    excepcion = "XXXX"

    # Verificar si la carpeta de origen existe
    if not os.path.exists(origen):
        return

    # Verificar si la carpeta de destino existe, excepto la carpeta de excepción
    if os.path.exists(destino) and os.path.basename(destino) != excepcion:
        return

    # Crear la carpeta de destino si no existe
    if not os.path.exists(destino):
        os.makedirs(destino)

    # Copiar la carpeta y su contenido
    try:
        shutil.copytree(origen, destino, dirs_exist_ok=True)
        app.log_message(f"Carpeta copiada de '{origen}' a '{destino}' exitosamente.", error=False)
    except Exception as e:
        app.log_message(f"Error al copiar la carpeta: {e}", error=True)

def find_subdir_with_string(path, target_string, max_depth=2):
    """
    Escanea la ruta especificada hasta una profundidad máxima y devuelve el subdirectorio que contiene el string objetivo en su nombre.

    :param path: Ruta a escanear.
    :param target_string: String a buscar en los nombres de las carpetas.
    :param max_depth: Profundidad máxima de subdirectorios a explorar.
    :return: El subdirectorio que contiene el string objetivo, o None si no se encuentra.
    """
    if '\0' in path:
        raise ValueError("La ruta contiene un carácter nulo.")

    for root, dirs, files in os.walk(path):
        # Ordenar las carpetas: primero las que comienzan con un número
        dirs.sort(key=lambda d: (not d[0].isdigit(), d))
        # Calcular la profundidad actual
        depth = root[len(path):].count(os.sep)
        if depth >= max_depth:
            # No explorar más allá de la profundidad máxima
            dirs[:] = []
        else:
            for dir_name in dirs:
                if target_string in dir_name:
                    subdir_path = os.path.join(root, dir_name)
                    subdir_path = subdir_path.replace(os.sep, '/')
                    parts = subdir_path.split('/')
                    if len(parts) >= 2:
                        return parts[2], parts[3]
    return None

# Function to list directories
def list_dirs(repo_url,app):
    global machine
    result = subprocess.run(['svn', 'list', '--username', app.username, '--password', app.password, repo_url], capture_output=True, text=True)
    items = [item for item in result.stdout.splitlines() if item.endswith('/')]
    if not items:
        app.log_message(f"No se ha encontrado el listado de tipos de maquina.", error=False)
        return None

    subdir = get_subdir(machine,app)
    if not subdir:
        app.log_message(f"Seleccion de maquina invalida. Prueba otro numero.", error=False)
        return list_dirs(repo_url,app)

    if  machine == "0":
        return None
    if (repo_url == PILZ_URL and subdir == "FLP"):
        subdir = "FL"
    repo_url = f"{repo_url}/{subdir}"
    list_dirs_in_subdir(repo_url,app)

# Function to get subdirectory based on machine number
def get_subdir( machine,app):
    subdir_map = {
        "15": "FA", "71": "FLP", "72": "FLP", "62": "FP", "63": "FP",
        "56": "FR", "68": "FS", "58": "FXR", "23": "HGR", "10": "PM",
        "11": "PMG", "13": "PR", "16": "SA", "31": "TA", "14": "TA",
        "83": "SLP", "44": "TR"
    }
    if not  machine or len( machine) < 2:
        app.log_message(f"Numero de maquina invalido.", error=True)
        sys.exit()
        return None
    subdir = subdir_map.get( machine[:2])
    if not subdir:
        app.log_message(f"No se ha encontrado modelo de maquina para el numero introducido.", error=True)
    return subdir

# Function to list directories in the selected subdirectory
def list_dirs_in_subdir(repo_url,app):
    global machine, año, maquina_carpeta
    repo_url_aux = repo_url
    last_segment = repo_url.rstrip('/').split('/')[-1]
    if last_segment == "FL":
        last_segment = last_segment.replace("FL", "FLP")
    result = subprocess.run(['svn', 'list', '--username', app.username, '--password', app.password, f"{PLC_URL}/{last_segment}"], capture_output=True, text=True)
    items = [item for item in result.stdout.splitlines() if  machine in item]
    folder_name = items[0]
    result = subprocess.run(['svn', 'list', '--username', app.username, '--password', app.password, repo_url], capture_output=True, text=True)
    items = [item for item in result.stdout.splitlines() if  machine in item]

    if not items:
        app.log_message(f"No matching directory found in OROKORRAK for machine number { machine}.", error=False)
        return

    mc_numb = items[0]
    repo_url = f"{repo_url}/{mc_numb}"
    encoded_path = encode_url(repo_url)
    
    año, maquina_carpeta = find_subdir_with_string(OROKORRAK_URL,  machine)
    copiar_carpeta(f"D:/Machines/{año}/{get_subdir(mc_numb,app)}/{folder_name}",app)
    if(PLC_URL in repo_url_aux):
        # Esquema electrico
        copiar_archivo_mas_nuevo(f"D:/Machines/{año}/{get_subdir(mc_numb,app)}/{folder_name}",app)
        destined_path = f"D:/Machines/{año}/{get_subdir(mc_numb,app)}/{folder_name}/6_PLC-PROJECT"
    else:
        destined_path = f"D:/Machines/{año}/{get_subdir(mc_numb,app)}/{folder_name}"
        if os.path.exists(os.path.join(destined_path, "XXXX")):
            os.rename(destined_path + "/XXXX", destined_path + f"/{mc_numb}")
        destined_path = destined_path + f"/{mc_numb}"
    if app.checkout == 1:    
        subprocess.run(['svn', 'co', encoded_path, destined_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if (PLC_URL in repo_url_aux):
            app.log_message("Projecto PLC correctamente descargado.", error=False)
        elif (PILZ_URL in repo_url_aux):
            app.log_message("Projecto PILZ correctamente descargado.", error=False)

def encode_url(url):
    return url.replace(" ", "%20").replace("&", "%26")

def copiar_archivo_mas_nuevo(destino_base,app):
    global año, maquina_carpeta, machine
    origen1 = f"O:\\Hornitzaile_Partekatua\\OC-Elektra\\Maquinas en curso\\{get_subdir( machine,app)}\\{ machine}\Documentación Elektra\Esquemas eléctricos iniciales"
    origen2 = fr"O:/00-Máquinas/{año}/{maquina_carpeta}/03_TECHNICS/03-07_HW"
    origen3 = fr"O:/00-Máquinas/{año}/{maquina_carpeta}/01_TECHNICS/01-07_HW"
    # Función interna para encontrar y copiar el archivo más nuevo
    def encontrar_y_copiar(origen, tipo, destino,app):
        # Verificar si la carpeta de origen existe
        if not os.path.exists(origen):
            return False

        # Copiar parte de carpeta
        shutil.copy2(origen, destino)
        # Obtener la lista de archivos .pdf en la carpeta de origen
        archivos = [os.path.join(origen, archivo) for archivo in os.listdir(origen) if os.path.isfile(os.path.join(origen, archivo)) and archivo.endswith('.pdf')]
        # Filtrar archivos según el tipo (ED para eléctricos, FD para fluidos)
        if tipo == "ED":
            archivos = [archivo for archivo in archivos if "ED" in os.path.basename(archivo)]
        elif tipo == "FD":
            archivos = [archivo for archivo in archivos if "FD" in os.path.basename(archivo)]

        # Verificar si hay archivos .pdf en la carpeta de origen
        if not archivos:
            return False
        # Encontrar el archivo .pdf más nuevo
        archivo_mas_nuevo = max(archivos, key=os.path.getmtime)      

        # Crear la carpeta de destino si no existe
        if not os.path.exists(destino):
            os.makedirs(destino)

        # Copiar el archivo .pdf más nuevo al destino
        try:
            shutil.copy2(archivo_mas_nuevo, destino)
            return True
        except shutil.Error as e:
            app.log_message(f"Error al copiar el archivo: {e}", error=True)
            return False
        except Exception as e:
            app.log_message(f"Error al copiar el archivo: {e}", error=True)
            return False

    # Intentar copiar el esquema eléctrico desde la primera carpeta de origen
    destino_electrico = os.path.join(destino_base, "1_HWE-ED")
    if not encontrar_y_copiar(origen1, "ED", destino_electrico,app):
        # Si falla, intentar copiar el esquema eléctrico desde la segunda carpeta de origen
        if not encontrar_y_copiar(origen2, "ED", destino_electrico,app):
            # Si falla, intentar copiar el esquema eléctrico desde la tercera carpeta de origen
            if not encontrar_y_copiar(origen3, "ED", destino_electrico,app):
                app.log_message(f"No se encontró el esquema eléctrico en ninguna de las carpetas de origen.", error=True)

    # Intentar copiar el esquema de fluidos desde la segunda carpeta de origen
    destino_fluido = os.path.join(destino_base, "2_HWF-FD")
    if not encontrar_y_copiar(origen2, "FD", destino_fluido,app):
        # Si falla, intentar copiar el esquema eléctrico desde la tercera carpeta de origen
        if not encontrar_y_copiar(origen3, "FD", destino_fluido,app):
            app.log_message(f"No se encontró el esquema de fluidos en ninguna de las carpetas de origen.", error=True)



class SVNApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Soraluce Heindenhain Machine Download Tool")
        # Set application icon
        icon_path = "danobatIcono.ico"  # Replace with the path to your .ico file
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        # Instance variables for credentials and machine
        self.username = ""
        self.password = ""
        self.machine = ""
        self.checkout = 1
        self.startup = 0

        # Set background color to white and adjust window size
        self.root.configure(bg="white")  # White background
        
        # Apply ttk theme for a lighter blue color scheme
        style = ttk.Style()
        style.theme_use("clam")  # Use a modern theme
        style.configure("TLabel", background="white", foreground="#0055A4", font=("Arial", 10))  # Light blue text
        style.configure("TButton", background="#0072CE", foreground="white", font=("Arial", 10), borderwidth=0)  # Blue buttons
        style.map("TButton", background=[("active", "#0055A4")])  # Button hover color
        style.configure("TFrame", background="white")
        style.configure("TLabelframe", background="white", foreground="#0055A4", font=("Arial", 10))  # Light blue frame text
        style.configure("TLabelframe.Label", background="white", foreground="#0055A4", font=("Arial", 10))

        self.create_widgets()
        self.load_credentials()

    def create_widgets(self):
        # Frame for SVN credentials
        credentials_frame = ttk.LabelFrame(self.root, text="SVN Credentials")
        credentials_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(credentials_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.username_entry = ttk.Entry(credentials_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(credentials_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ttk.Entry(credentials_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Frame for machine selection
        machine_frame = ttk.LabelFrame(self.root, text="Machine Selection")
        machine_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(machine_frame, text="Machine Number:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.machine_entry = ttk.Entry(machine_frame, width=30)
        self.machine_entry.grid(row=0, column=1, padx=5, pady=5)

        # Frame for action selection
        action_frame = ttk.LabelFrame(self.root, text="Select Action")
        action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        def execute_command_and_log(command):
            if self.startup == 0:
                self.log_message("=====================================", error=False)
                self.startup = 1
            threading.Thread(target=command).start()

        self.pilz_button = ttk.Button(action_frame, text="Process Pilz", command=lambda: execute_command_and_log(self.process_pilz))
        self.pilz_button.grid(row=0, column=0, padx=5, pady=5)

        self.project_button = ttk.Button(action_frame, text="Process Project", command=lambda: execute_command_and_log(self.process_project))
        self.project_button.grid(row=0, column=1, padx=5, pady=5)

        self.schematics_button = ttk.Button(action_frame, text="Process Schematics", command=lambda: execute_command_and_log(self.process_schematics))
        self.schematics_button.grid(row=0, column=2, padx=5, pady=5)

        self.all_button = ttk.Button(action_frame, text="Process All", command=lambda: execute_command_and_log(self.process_all))
        self.all_button.grid(row=0, column=3, padx=5, pady=5)

        # Frame for messages
        message_frame = ttk.LabelFrame(self.root, text="Messages")
        message_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.message_text = tk.Text(message_frame, height=10, width=70, state="disabled", wrap="word")
        self.message_text.grid(row=0, column=0, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.exit_button = ttk.Button(button_frame, text="Exit", command=self.root.quit)
        self.exit_button.grid(row=0, column=0, padx=5, pady=5)

    def log_message(self, message, error=False):
        """Log a message to the message text box."""
        self.message_text.config(state="normal")
        self.message_text.insert("end", f"{'[ERROR]' if error else '[INFO]'} {message}\n")
        self.message_text.see("end")
        self.message_text.config(state="disabled")

    def load_credentials(self):
        """Load credentials from file if available."""
        if os.path.exists("svn_credentials.txt"):
            with open("svn_credentials.txt", "r") as cred_file:
                lines = cred_file.readlines()
                if len(lines) >= 2:
                    self.username_entry.insert(0, lines[0].strip())
                    self.password_entry.insert(0, lines[1].strip())

    def save_credentials(self):
        """Save credentials to file."""
        with open("svn_credentials.txt", "w") as cred_file:
            cred_file.write(f"{self.username}\n{self.password}\n")

    def validate_inputs(self):
        global machine
        """Validate user inputs."""
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        machine = self.machine_entry.get()

        if not self.username or not self.password:
            self.log_message("Por favor rellene todas las casillas.", error=True)
            return False
        return True

    def process_all(self):
        if not self.validate_inputs():
            return
        self.save_credentials()
        self.log_message("Descargando maquina entera.....", error=False)
        self.process_repositories(PLC_URL)
        self.process_repositories(PILZ_URL)
        self.log_message("Esquemas correctamente copiados", error=False)
        self.log_message("=====================================", error=False)

    def process_pilz(self):
        if not self.validate_inputs():
            return
        self.save_credentials()
        self.log_message("Descargando projecto PILZ.....", error=False)
        self.process_repositories(PILZ_URL)
        self.log_message("=====================================", error=False)

    def process_project(self):
        if not self.validate_inputs():
            return
        self.save_credentials()
        self.log_message("Descargando projecto PLC.....", error=False)
        self.process_repositories(PLC_URL)
        self.log_message("=====================================", error=False)

    def process_schematics(self):
        if not self.validate_inputs():
            return
        self.save_credentials()
        try:
            self.checkout = 0
            self.log_message("Imprimiendo Esquema Electrico e Hidraulico", error=False)
            process_repo(PLC_URL)
            self.log_message("Esquemas correctamente copiados", error=False)
            self.log_message("=====================================", error=False)
        except Exception as e:
            self.log_message(f"An error occurred: {e}", error=True)

    def process_repositories(self, repo_url):
        try:
            self.checkout = 1
            process_repo(repo_url, app=self)
        except Exception as e:
            self.log_message(f"A ocurrido un error: {e}", error=True)

if __name__ == "__main__":

    def run_app():
        root = tk.Tk()
        app = SVNApp(root)
        root.mainloop()

    # Run the application in a separate thread to prevent blocking
    app_thread = threading.Thread(target=run_app)
    app_thread.start()
