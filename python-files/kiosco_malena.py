
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

productos = {}
carrito = []

def cargar_producto():
    codigo = entry_codigo.get()
    nombre = entry_nombre.get()
    precio = entry_precio.get()

    if codigo and nombre and precio:
        try:
            productos[codigo] = {"nombre": nombre, "precio": float(precio)}
            messagebox.showinfo("Éxito", f"Producto '{nombre}' cargado.")
        except ValueError:
            messagebox.showerror("Error", "Precio inválido.")
    else:
        messagebox.showerror("Error", "Faltan datos.")

def agregar_al_carrito():
    codigo = entry_codigo.get()
    if codigo in productos:
        carrito.append(productos[codigo])
        actualizar_carrito()
    else:
        messagebox.showerror("Error", "Código no encontrado.")

def actualizar_carrito():
    texto_carrito = ""
    total = 0
    for item in carrito:
        texto_carrito += f"{item['nombre']} - ${item['precio']:.2f}\n"
        total += item['precio']
    label_carrito.config(text=texto_carrito)
    label_total.config(text=f"Total: ${total:.2f}")

def confirmar_venta():
    if not carrito:
        messagebox.showerror("Error", "El carrito está vacío.")
        return
    total = sum(item["precio"] for item in carrito)
    guardar_venta(total)
    carrito.clear()
    actualizar_carrito()
    messagebox.showinfo("Venta confirmada", f"Total a pagar: ${total:.2f}")

def guardar_venta(total):
    with open("historial_ventas.txt", "a") as f:
        f.write(f"{datetime.now()} - Total: ${total:.2f}\n")

def cierre_caja():
    try:
        with open("historial_ventas.txt", "r") as f:
            ventas = f.readlines()
        total_dia = sum(float(line.split("Total: $")[1]) for line in ventas if "Total: $" in line)
        messagebox.showinfo("Cierre de caja", f"Total del día: ${total_dia:.2f}")
    except FileNotFoundError:
        messagebox.showinfo("Cierre de caja", "No hay ventas registradas.")

root = tk.Tk()
root.title("Kiosco Malena")

tk.Label(root, text="Código de producto:").pack()
entry_codigo = tk.Entry(root)
entry_codigo.pack()

tk.Label(root, text="Nombre del producto:").pack()
entry_nombre = tk.Entry(root)
entry_nombre.pack()

tk.Label(root, text="Precio:").pack()
entry_precio = tk.Entry(root)
entry_precio.pack()

tk.Button(root, text="Cargar producto", command=cargar_producto).pack()
tk.Button(root, text="Agregar al carrito", command=agregar_al_carrito).pack()
tk.Button(root, text="Confirmar venta", command=confirmar_venta).pack()
tk.Button(root, text="Cierre de caja", command=cierre_caja).pack()

label_carrito = tk.Label(root, text="", justify="left")
label_carrito.pack()

label_total = tk.Label(root, text="Total: $0.00", font=("Arial", 14))
label_total.pack()

root.mainloop()
