import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
import random
import string

# Generar código de reserva único
def generar_codigo_reserva(longitud=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=longitud))

# Guardar la reserva en un archivo
def guardar_reserva(nombre, apellidos, entrada, salida, noches, codigo):
    with open("reservas.txt", "a") as archivo:
        archivo.write(f"{datetime.now()} | {nombre} {apellidos} | Entrada: {entrada} | Salida: {salida} | Noches: {noches} | Código: {codigo}\n")

# Función que realiza la reserva
def realizar_reserva():
    nombre = entry_nombre.get().strip()
    apellidos = entry_apellidos.get().strip()
    entrada = entry_entrada.get().strip()
    salida = entry_salida.get().strip()

    if not nombre or not apellidos or not entrada or not salida:
        messagebox.showerror("Error", "Por favor completa todos los campos.")
        return

    try:
        fecha_entrada = datetime.strptime(entrada, "%Y-%m-%d").date()
        fecha_salida = datetime.strptime(salida, "%Y-%m-%d").date()

        if fecha_salida <= fecha_entrada:
            messagebox.showerror("Error", "La fecha de salida debe ser posterior a la de entrada.")
            return

        noches = (fecha_salida - fecha_entrada).days
        codigo = generar_codigo_reserva()

        guardar_reserva(nombre, apellidos, entrada, salida, noches, codigo)

        mensaje = f"""
        Reserva exitosa:
        Cliente: {nombre} {apellidos}
        Entrada: {entrada}
        Salida: {salida}
        Noches: {noches}
        Código: {codigo}
        """
        messagebox.showinfo("Reserva confirmada", mensaje.strip())

    except ValueError:
        messagebox.showerror("Error", "Formato de fecha incorrecto. Usa YYYY-MM-DD.")

# Mostrar todas las reservas guardadas
def ver_reservas():
    try:
        with open("reservas.txt", "r") as archivo:
            contenido = archivo.read()
    except FileNotFoundError:
        contenido = "No hay reservas registradas."

    ventana_reservas = tk.Toplevel(ventana)
    ventana_reservas.title("Todas las Reservas")
    ventana_reservas.geometry("600x400")

    area_texto = scrolledtext.ScrolledText(ventana_reservas, wrap=tk.WORD)
    area_texto.pack(expand=True, fill="both", padx=10, pady=10)
    area_texto.insert(tk.END, contenido)
    area_texto.configure(state="disabled")

    tk.Button(ventana_reservas, text="Cerrar", command=ventana_reservas.destroy).pack(pady=10)

# Interfaz principal
ventana = tk.Tk()
ventana.title("Sistema de Reservación de Hotel")
ventana.geometry("400x400")

tk.Label(ventana, text="Nombre:").pack(pady=5)
entry_nombre = tk.Entry(ventana, width=40)
entry_nombre.pack()

tk.Label(ventana, text="Apellidos:").pack(pady=5)
entry_apellidos = tk.Entry(ventana, width=40)
entry_apellidos.pack()

tk.Label(ventana, text="Fecha de Entrada (YYYY-MM-DD):").pack(pady=5)
entry_entrada = tk.Entry(ventana, width=20)
entry_entrada.pack()

tk.Label(ventana, text="Fecha de Salida (YYYY-MM-DD):").pack(pady=5)
entry_salida = tk.Entry(ventana, width=20)
entry_salida.pack()

tk.Button(ventana, text="Reservar", command=realizar_reserva).pack(pady=20)
tk.Button(ventana, text="Ver Reservas", command=ver_reservas).pack()

ventana.mainloop()