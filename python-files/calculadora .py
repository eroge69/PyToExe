import tkinter as tk

def calcular():
    try:
        resultado = eval(entrada.get())
        entrada.delete(0, tk.END)
        entrada.insert(tk.END, str(resultado))
    except:
        entrada.delete(0, tk.END)
        entrada.insert(tk.END, "Error")

def agregar_texto(texto):
    entrada.insert(tk.END, texto)

# Configuración de la ventana
ventana = tk.Tk()
ventana.title("Calculadora Simple")
ventana.geometry("300x400")

# Entrada de texto
entrada = tk.Entry(ventana, font=("Arial", 18), justify="right")
entrada.pack(fill=tk.X, padx=10, pady=10)

# Botones (números y operadores)
botones = [
    '7', '8', '9', '/',
    '4', '5', '6', '*',
    '1', '2', '3', '-',
    '0', '.', '=', '+'
]

marco = tk.Frame(ventana)
marco.pack()

for i, texto_boton in enumerate(botones):
    fila = i // 4
    columna = i % 4
    if texto_boton == "=":
        boton = tk.Button(marco, text=texto_boton, font=("Arial", 14), command=calcular)
    else:
        boton = tk.Button(marco, text=texto_boton, font=("Arial", 14), 
                          command=lambda t=texto_boton: agregar_texto(t))
    boton.grid(row=fila, column=columna, padx=5, pady=5, ipadx=10, ipady=10)

ventana.mainloop()