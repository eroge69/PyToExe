
import tkinter as tk
from tkinter import messagebox

# Tabla de conversión para hombres
conversion_hombres = {
    'Conciencia Social': [(0, 8, 52), (9, 12, 58), (13, 17, 65), (18, 100, 72)],
    'Cognición Social': [(0, 10, 53), (11, 14, 58), (15, 20, 65), (21, 100, 72)],
    'Comunicación Social': [(0, 9, 53), (10, 13, 58), (14, 19, 65), (20, 100, 72)],
    'Motivación Social': [(0, 7, 52), (8, 11, 58), (12, 16, 65), (17, 100, 72)],
    'Manejo de Manerismos': [(0, 6, 52), (7, 10, 58), (11, 15, 65), (16, 100, 72)]
}

interpretacion_t = [
    (0, 59, "Normal: Dentro del rango típico."),
    (60, 65, "Leve: Rasgos leves de TEA."),
    (66, 75, "Moderado: Síntomas significativos de TEA."),
    (76, 200, "Severo: Alto grado de afectación (TEA).")
]

def convertir_a_T(subescala, directa, genero):
    tabla = conversion_hombres[subescala]
    if genero == "Mujer":
        ajuste = -3
    else:
        ajuste = 0
    for rango in tabla:
        if rango[0] <= directa <= rango[1]:
            return max(50, rango[2] + ajuste)
    return ""

def interpretar_T(t):
    for rango in interpretacion_t:
        if rango[0] <= t <= rango[1]:
            return rango[2]
    return "Sin datos"

def calcular():
    try:
        genero = genero_var.get()
        t_total = 0
        count = 0
        for i, subescala in enumerate(subescalas):
            directa = int(entradas[i].get())
            t = convertir_a_T(subescala, directa, genero)
            resultados[i].config(text=f"Punt. T: {t} ({interpretar_T(t)})")
            t_total += t
            count += 1
        promedio_t = round(t_total / count)
        interpretacion_final.config(text=f"Punt. T promedio: {promedio_t} → {interpretar_T(promedio_t)}")
    except ValueError:
        messagebox.showerror("Error", "Por favor, introduce todas las puntuaciones directas como números enteros.")

# Interfaz
ventana = tk.Tk()
ventana.title("Interpretador SRS-2 (4 a 18 años)")
ventana.geometry("600x450")

tk.Label(ventana, text="Género del evaluado:", font=("Arial", 12)).pack()
genero_var = tk.StringVar(value="Hombre")
tk.Radiobutton(ventana, text="Hombre", variable=genero_var, value="Hombre").pack()
tk.Radiobutton(ventana, text="Mujer", variable=genero_var, value="Mujer").pack()

subescalas = [
    "Conciencia Social",
    "Cognición Social",
    "Comunicación Social",
    "Motivación Social",
    "Manejo de Manerismos"
]
entradas = []
resultados = []

tk.Label(ventana, text="Ingrese las puntuaciones directas:", font=("Arial", 12, "bold")).pack()

for subescala in subescalas:
    frame = tk.Frame(ventana)
    frame.pack(pady=3)
    tk.Label(frame, text=subescala + ":", width=30, anchor="w").pack(side="left")
    entry = tk.Entry(frame, width=5)
    entry.pack(side="left")
    label = tk.Label(frame, text="Punt. T: ")
    label.pack(side="left")
    entradas.append(entry)
    resultados.append(label)

tk.Button(ventana, text="Calcular interpretación", command=calcular, bg="lightblue").pack(pady=10)

interpretacion_final = tk.Label(ventana, text="", font=("Arial", 12, "bold"), fg="darkblue")
interpretacion_final.pack()

ventana.mainloop()
