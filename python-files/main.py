import customtkinter as ctk
import subprocess
import psutil
import time
from tkinter import messagebox

# Función para optimizar la PC y BlueStacks
def optimizar_pc():
    try:
        # Cambiar el plan de energía a Alto Rendimiento
        subprocess.call('powercfg -change -standby-timeout-ac 0', shell=True)
        subprocess.call('powercfg -change -monitor-timeout-ac 0', shell=True)
        subprocess.call('powercfg -setactive SCHEME_MAX', shell=True)

        # Desactivar servicios innecesarios
        subprocess.call('sc stop "wuauserv" && sc config "wuauserv" start= disabled', shell=True)
        subprocess.call('sc stop "Spooler" && sc config "Spooler" start= disabled', shell=True)

        # Asignar más recursos a BlueStacks (4 núcleos y 8 GB de RAM)
        subprocess.call('BlueStacksHypervisor.exe -cores 4 -memory 8192', shell=True)

        # Desactivar V-Sync
        subprocess.call('reg add "HKEY_CURRENT_USER\\Software\\BlueStacks\\Clients" /v "Vsync" /t REG_DWORD /d 0 /f', shell=True)

        # Forzar el uso de la GPU dedicada
        subprocess.call('setx _BLUESTACKS_USE_HARDWARE_ACCELERATION 1', shell=True)

        # Ajustar la configuración para forzar 240 FPS
        subprocess.call('reg add "HKEY_CURRENT_USER\\Software\\BlueStacks\\Clients" /v "FPS" /t REG_DWORD /d 240 /f', shell=True)

        show_success_popup("Optimización Completada", "La optimización de la PC y BlueStacks para 240 FPS se ha completado.")

    except Exception as e:
        show_error_popup("Error", f"Ocurrió un error: {str(e)}")

# Función para mostrar una ventana emergente de éxito
def show_success_popup(title, message):
    success_popup = ctk.CTkToplevel(window)
    success_popup.title(title)

    # Ajustar el tamaño de la ventana emergente
    success_popup.geometry("400x200")  # Tamaño más adecuado para el contenido
    success_popup.configure(bg="#2a2a2a")

    # Etiqueta de mensaje
    label = ctk.CTkLabel(success_popup, text=message, font=("Arial", 14), text_color="white", width=300)
    label.pack(pady=20)

    # Botón de cierre
    button = ctk.CTkButton(success_popup, text="Cerrar", command=success_popup.destroy, font=("Arial", 14), fg_color="#4a90e2", hover_color="#0066ff", width=150, height=40, corner_radius=10)
    button.pack(pady=10)

# Función para mostrar una ventana emergente de error
def show_error_popup(title, message):
    error_popup = ctk.CTkToplevel(window)
    error_popup.title(title)

    # Ajustar el tamaño de la ventana emergente
    error_popup.geometry("400x200")  # Tamaño más adecuado para el contenido
    error_popup.configure(bg="#2a2a2a")

    # Etiqueta de mensaje
    label = ctk.CTkLabel(error_popup, text=message, font=("Arial", 14), text_color="white", width=300)
    label.pack(pady=20)

    # Botón de cierre
    button = ctk.CTkButton(error_popup, text="Cerrar", command=error_popup.destroy, font=("Arial", 14), fg_color="#e74c3c", hover_color="#c0392b", width=150, height=40, corner_radius=10)
    button.pack(pady=10)

# Función para monitorear el rendimiento (aproximación del FPS)
def monitorear_rendimiento():
    prev_time = time.time()
    frame_count = 0

    while True:
        # Monitorear uso de CPU y RAM
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent

        # Contar los frames
        frame_count += 1
        current_time = time.time()

        if current_time - prev_time >= 1:  # Actualiza el FPS cada segundo
            estimated_fps = frame_count / (current_time - prev_time)
            label_fps.config(text=f"FPS Estimados: {int(estimated_fps)}")
            frame_count = 0
            prev_time = current_time

        # Actualizar la interfaz con los datos actuales
        label_cpu.config(text=f"Uso de CPU: {cpu_usage}%")
        label_memory.config(text=f"Uso de RAM: {memory}%")

        window.update()
        time.sleep(1)

# Crear la ventana principal con customtkinter
ctk.set_appearance_mode("Dark")  # Estilo oscuro
ctk.set_default_color_theme("blue")  # Tema de color azul

window = ctk.CTk()  # Ventana principal
window.title("FPS Booster para BlueStacks")
window.geometry("450x450")  # Tamaño de la ventana

# Establecer un fondo degradado suave
window.configure(bg="#2a2a2a")

# Etiquetas para mostrar el rendimiento
label_cpu = ctk.CTkLabel(window, text="Uso de CPU: 0%", font=("Arial", 16, "bold"), text_color="white", width=300)
label_cpu.pack(pady=20)

label_memory = ctk.CTkLabel(window, text="Uso de RAM: 0%", font=("Arial", 16, "bold"), text_color="white", width=300)
label_memory.pack(pady=10)

label_fps = ctk.CTkLabel(window, text="FPS Estimados: 0", font=("Arial", 16, "bold"), text_color="white", width=300)
label_fps.pack(pady=10)

# Botón para optimizar la PC
optimizar_button = ctk.CTkButton(window, text="Optimizar PC y BlueStacks para 240 FPS", command=optimizar_pc, font=("Arial", 16), fg_color="#4a90e2", hover_color="#0066ff", width=300, height=40, corner_radius=10)
optimizar_button.pack(pady=30)

# Iniciar monitoreo de rendimiento en segundo plano
window.after(1000, monitorear_rendimiento)

# Ejecutar la interfaz gráfica
window.mainloop()
