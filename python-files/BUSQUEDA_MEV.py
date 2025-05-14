import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageTk
import os
import json
import sys

# Fixed resource_path function
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load cases from JSON file
try:
    with open(resource_path('causasPBA.json'), 'r', encoding='utf-8') as f:
        CAUSAS = json.load(f)
except FileNotFoundError:
    CAUSAS = {
        "Ejemplo 1": "https://mev.scba.gov.ar/procesales.asp?nidCausa=20991&pidJuzgado=GAM2133",
        "Ejemplo 2": "https://mev.scba.gov.ar/procesales.asp?nidCausa=12345&pidJuzgado=GAM2133"
    }

def navegar_a_causa():
    causa_seleccionada = combo_causas.get()
    if not causa_seleccionada:
        messagebox.showwarning("Advertencia", "Selecciona una causa primero")
        return

    link_causa = CAUSAS.get(causa_seleccionada)
    if not link_causa:
        messagebox.showerror("Error", "Link no encontrado para esta causa")
        return

    try:
        driver.get(link_causa)
        messagebox.showinfo("Éxito", f"Navegando a: {causa_seleccionada}")
    except Exception as e:
        messagebox.showerror("Error", f"Fallo al navegar:\n{str(e)}")

def iniciar_proceso():
    global driver
    
    try:
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        # Fixed ChromeDriver initialization
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        driver.get("https://mev.scba.gov.ar/loguin.asp")
        
        WebDriverWait(driver, 30).until(
            EC.url_to_be("https://mev.scba.gov.ar/POSLoguin.asp")
        )
        
        combo_causas.config(state="readonly")
        boton_navegar.config(state="normal")
        boton_iniciar.config(state="disabled")
        
    except Exception as e:
        messagebox.showerror("Error", f"Fallo al iniciar:\n{str(e)}")
        if 'driver' in globals():
            driver.quit()

# GUI setup
ventana_principal = tk.Tk()
ventana_principal.title("Navegador Automático MEV")
ventana_principal.geometry("400x250")

style = ttk.Style()
style.configure('TButton', font=('Arial', 10), padding=5)
style.configure('TCombobox', font=('Arial', 10))

label_causas = ttk.Label(ventana_principal, text="Selecciona una causa:", font=('Arial', 11))
label_causas.pack(pady=10)

combo_causas = ttk.Combobox(ventana_principal, values=list(CAUSAS.keys()), state="disabled")
combo_causas.pack(pady=5, padx=20, fill=tk.X)

frame_botones = ttk.Frame(ventana_principal)
frame_botones.pack(pady=10)

boton_iniciar = ttk.Button(frame_botones, text="Iniciar Navegador", command=iniciar_proceso)
boton_iniciar.pack(side=tk.LEFT, padx=5)

boton_navegar = ttk.Button(frame_botones, text="Navegar", command=navegar_a_causa, state="disabled")
boton_navegar.pack(side=tk.LEFT, padx=5)

def on_closing():
    if 'driver' in globals():
        driver.quit()
    ventana_principal.destroy()

ventana_principal.protocol("WM_DELETE_WINDOW", on_closing)
ventana_principal.mainloop()