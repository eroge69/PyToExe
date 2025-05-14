import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageTk
import io
import json  # JSON !!!

# Cargar causas desde archivo JSON 
try:
    with open('causasPBA.json', 'r', encoding='utf-8') as f:
        CAUSAS = json.load(f)
except FileNotFoundError: # si no hay cuasas precargadas usar estas:
    # por defecto.
    CAUSAS = {
        "por defecto": "https://mev.scba.gov.ar/procesales.asp?nidCausa=20991&pidJuzgado=GAM2133",
              },

# Función para navegar a la causa seleccionada
def navegar_a_causa():
    # Obtener la causa seleccionada
    causa_seleccionada = combo_causas.get()
    if not causa_seleccionada:
        messagebox.showwarning("Advertencia", "Por favor, selecciona una causa.")
        return

    # Obtener el link de la causa seleccionada
    link_causa = CAUSAS.get(causa_seleccionada)
    if not link_causa:
        messagebox.showerror("Error", "La causa seleccionada no tiene un link válido.")
        return

    # Navegar al link de la causa seleccionada
    try:
        driver.get(link_causa)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo navegar a la causa: {e}")

# Función principal para iniciar el proceso
def iniciar_proceso():
    global driver

    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")  # Desactivar la aceleración de hardware
    chrome_options.add_argument("--no-sandbox")   # Desactivar el sandbox
    chrome_options.add_argument("--disable-dev-shm-usage")  # Evitar problemas de memoria

    # Iniciar Chrome con las opciones configuradas
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Navegar a la página de inicio de sesión
        driver.get("https://mev.scba.gov.ar/loguin.asp")

        # Esperar  Inicio para redirigir a "https://mev.scba.gov.ar/POSLoguin.asp"
        WebDriverWait(driver, 500).until(  #(500 segundos)
            EC.url_to_be("https://mev.scba.gov.ar/POSLoguin.asp")
        )

        # Habilitar el menú desplegable y el botón de navegación
        combo_causas.config(state="readonly")
        boton_navegar.config(state="normal")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Interfaz gráfica principal
ventana_principal = tk.Tk()
ventana_principal.title("Navegador Automático")

# Menú  para seleccionar la causa
label_causas = tk.Label(ventana_principal, text="Selecciona una causa:")
label_causas.pack(pady=5)

combo_causas = ttk.Combobox(ventana_principal, values=list(CAUSAS.keys()), state="disabled")
combo_causas.pack(pady=5)

# Botón  "navegar"
boton_navegar = tk.Button(ventana_principal, text="Navegar a la causa", command=navegar_a_causa, state="disabled")
boton_navegar.pack(pady=10)

# Botón "iniciar"
boton_iniciar = tk.Button(ventana_principal, text="Iniciar", command=iniciar_proceso)
boton_iniciar.pack(pady=20)

# Iniciar el bucle principal de la interfaz
ventana_principal.mainloop()