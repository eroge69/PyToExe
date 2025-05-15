import random
import tkinter as tk
from tkinter import messagebox
import os

# IMPORTANTE: Para girar la pantalla, se puede usar PowerShell o teclas, pero aquí lo simularemos
# Apagar el equipo sí funciona con shutdown

def jugar_ruleta():
    try:
        seleccion = int(entry.get())
        if seleccion < 1 or seleccion > 6:
            messagebox.showwarning("Advertencia", "Por favor elige un número del 1 al 6.")
            return
    except ValueError:
        messagebox.showwarning("Advertencia", "Debes ingresar un número.")
        return

    bala = random.randint(1, 6)
    print(f"Tu elección: {seleccion} | Cámara con bala: {bala}")

    if seleccion == bala:
        messagebox.showerror("¡BOOM!", "¡Perdiste! Girando pantalla y apagando el sistema... 😈")

        # Simulación de caos antes del apagado
        os.system("powershell -command \"(Add-Type -MemberDefinition '[DllImport(\\\"user32.dll\\\")]public static extern bool SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);' -Name NativeMethods -Namespace Win32 -PassThru)::SystemParametersInfo(0x0073, 0, 'C:\\\\Windows\\\\web\\\\wallpaper\\\\Windows\\\\img0.jpg', 3)\"")
        
        # Girar pantalla (esto depende del driver de video y puede no funcionar en todos los sistemas)
        os.system("powershell /c \"(Get-WmiObject -Namespace root\\wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,10)\"")
        
        # Apagar en 5 segundos
        os.system("shutdown /s /t 5")
    else:
        messagebox.showinfo("¡Te salvaste!", "La bala no estaba ahí. Sobreviviste. 😜")

# Crear la ventana
ventana = tk.Tk()
ventana.title("Ruleta Rusa")
ventana.geometry("400x350")
ventana.config(bg="black")

# Título principal
titulo = tk.Label(ventana, text="🎯 Ruleta Rusa", fg="red", bg="black", font=("Helvetica", 24, "bold"))
titulo.pack(pady=(10, 5))

# Cara demoníaca
demonio = tk.Label(ventana, text="😈", fg="white", bg="black", font=("Helvetica", 40))
demonio.pack(pady=(0, 10))

# Instrucción
label = tk.Label(ventana, text="Elige un número entre (1-6):", fg="white", bg="black", font=("Helvetica", 14))
label.pack()

# Entrada del usuario
entry = tk.Entry(ventana, justify="center", font=("Helvetica", 16))
entry.pack(pady=10)

# Botón de jugar
boton = tk.Button(ventana, text="Jugar", command=jugar_ruleta, bg="red", fg="white", font=("Helvetica", 14, "bold"))
boton.pack(pady=10)

# Iniciar la app
ventana.mainloop()
