import tkinter as tk
from tkinter import ttk # Importar la librería tkinter y ttk para crear la interfaz gráfica.
# ttk es un módulo de tkinter que proporciona una interfaz más moderna y estilizada para crear widgets.

def convertir_temperatura():
    celsius = float(caja_temp_celsius.get()) # Obtener el valor de la caja de texto y convertirlo a float, viene en string.
    kelvin = celsius + 273.15 # Convertir Celsius a Kelvin.
    fahrenheit = (celsius * 9/5) + 32 # Convertir Celsius a Fahrenheit.
    etiqueta_kelvin.config(text=f"Temperatura en Kelvin: {kelvin:.2f}") # Actualizar la etiqueta de Kelvin con el resultado. La primera f es para formatear el texto, la segunda es para formatear el número a dos decimales.
    etiqueta_fahrenheit.config(text=f"Temperatura en Fahrenheit: {fahrenheit:.2f}")
    
ventana = tk.Tk()
ventana.title("Calculadora de Temperatura")
ventana.geometry("500x300")
ventana.resizable(True,True) #a lo ancho, a lo alto
ventana.config(bg="lightgreen") #color de fondo (background)
ventana.iconbitmap(r"C:\Users\danar\OneDrive\Escritorio\Raúl\Python\tempcalc\termometro.ico") #icono de la ventana

etiqueta_temp_celsius = tk.Label(ventana, text="Ingrese la temperatura en grados Celsius:", bg="white", font=("Times New Roman", 12), fg="red") #ttk no tiene bg
etiqueta_temp_celsius.place(x=20, y=20)

caja_temp_celsius = tk.Entry(ventana, width=10, font=("Times New Roman", 12))
caja_temp_celsius.place(x=20, y=60)

boton_convertir = tk.Button(text="Convertir", fg="darkblue", font="Trebuchet 12", command=convertir_temperatura)
boton_convertir.place(x=20, y=100)

etiqueta_kelvin = tk.Label(text="Temperatura en Kelvin: N/A", font=("Times New Roman", 12), bg="lightgreen")
etiqueta_kelvin.place(x=20, y=140)
etiqueta_fahrenheit = tk.Label(text="Temperatura en Fahrenheit: N/A", font=("Times New Roman", 12), bg="lightgreen")
etiqueta_fahrenheit.place(x=20, y=180)

ventana.mainloop()