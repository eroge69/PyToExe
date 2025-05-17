import tkinter as tk
from tkinter import messagebox
import heapq

# Mapa parcial de la Línea 1 del Metro
metro = {
    'Pantitlán': ['Zaragoza', 'Agrícola Oriental'],
    'Zaragoza': ['Pantitlán', 'Gómez Farías'],
    'Gómez Farías': ['Zaragoza', 'Boulevard Puerto Aéreo'],
    'Boulevard Puerto Aéreo': ['Gómez Farías', 'Balbuena'],
    'Balbuena': ['Boulevard Puerto Aéreo', 'Moctezuma', 'Agrícola Oriental'],
    'Moctezuma': ['Balbuena'],
    'Agrícola Oriental': ['Pantitlán', 'Balbuena']
}

# Heurística artificial (simulando distancia al destino)
heuristica = {
    'Pantitlán': 4,
    'Zaragoza': 3,
    'Gómez Farías': 2,
    'Boulevard Puerto Aéreo': 2,
    'Balbuena': 1,
    'Moctezuma': 0,
    'Agrícola Oriental': 2
}

# Algoritmo A*
def a_star(inicio, destino, cerradas):
    frontera = []
    heapq.heappush(frontera, (heuristica[inicio], 0, inicio, [inicio]))
    visitados = set()

    while frontera:
        estimado_total, costo_actual, nodo, camino = heapq.heappop(frontera)

        if nodo in visitados:
            continue
        visitados.add(nodo)

        if nodo == destino:
            return camino

        for vecino in metro.get(nodo, []):
            if vecino not in cerradas and vecino not in visitados:
                nuevo_costo = costo_actual + 1
                estimado_total = nuevo_costo + heuristica[vecino]
                heapq.heappush(frontera, (estimado_total, nuevo_costo, vecino, camino + [vecino]))

    return None

# Interfaz gráfica con Tkinter
def calcular_ruta():
    origen = entrada_origen.get().strip()
    destino = entrada_destino.get().strip()
    cerradas = entrada_cerradas.get().strip().split(',') if entrada_cerradas.get().strip() else []

    origen = origen.title()
    destino = destino.title()
    cerradas = [est.strip().title() for est in cerradas]

    for est in [origen, destino] + cerradas:
        if est not in metro:
            messagebox.showerror("Error", f"Estación no válida: {est}")
            return

    ruta = a_star(origen, destino, cerradas)
    if ruta:
        messagebox.showinfo("Ruta encontrada", " ➔ ".join(ruta))
    else:
        messagebox.showwarning("Sin ruta", "No se pudo encontrar una ruta disponible.")

# Crear la ventana
ventana = tk.Tk()
ventana.title("Metro CDMX - Buscador de Ruta A*")
ventana.geometry("400x200")

tk.Label(ventana, text="Estación de origen:").grid(row=0, column=0, sticky="e")
entrada_origen = tk.Entry(ventana)
entrada_origen.grid(row=0, column=1)

tk.Label(ventana, text="Estación de destino:").grid(row=1, column=0, sticky="e")
entrada_destino = tk.Entry(ventana)
entrada_destino.grid(row=1, column=1)

tk.Label(ventana, text="Estaciones cerradas (separadas por coma):").grid(row=2, column=0, columnspan=2)
entrada_cerradas = tk.Entry(ventana, width=40)
entrada_cerradas.grid(row=3, column=0, columnspan=2)

boton = tk.Button(ventana, text="Calcular ruta", command=calcular_ruta)
boton.grid(row=4, column=0, columnspan=2, pady=10)

ventana.mainloop()
