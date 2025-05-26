
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import os

# Base de datos
conn = sqlite3.connect('instituto.db')
c = conn.cursor()

# Crear tablas
c.execute('''CREATE TABLE IF NOT EXISTS alumnos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                dni TEXT NOT NULL,
                curso TEXT NOT NULL,
                celular TEXT,
                fecha_inscripcion TEXT NOT NULL
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_alumno INTEGER NOT NULL,
                mes TEXT NOT NULL,
                monto REAL NOT NULL,
                fecha_pago TEXT NOT NULL,
                FOREIGN KEY (id_alumno) REFERENCES alumnos(id)
            )''')

conn.commit()

# Interfaz
root = tk.Tk()
root.title("Sistema de Inscripción y Pagos - Instituto")
root.geometry("800x600")

# Funciones
def inscribir_alumno():
    datos = (entry_nombre.get(), entry_apellido.get(), entry_dni.get(), entry_curso.get(), entry_celular.get(), entry_fecha.get())
    if all(datos):
        c.execute("INSERT INTO alumnos (nombre, apellido, dni, curso, celular, fecha_inscripcion) VALUES (?, ?, ?, ?, ?, ?)", datos)
        conn.commit()
        messagebox.showinfo("Éxito", "Alumno inscripto correctamente")
        actualizar_lista()
    else:
        messagebox.showerror("Error", "Completá todos los campos")

def registrar_pago():
    alumno_id = tree.selection()
    if alumno_id:
        id_alumno = tree.item(alumno_id)['values'][0]
        c.execute("INSERT INTO pagos (id_alumno, mes, monto, fecha_pago) VALUES (?, ?, ?, ?)",
                  (id_alumno, entry_mes.get(), entry_monto.get(), entry_fecha_pago.get()))
        conn.commit()
        messagebox.showinfo("Éxito", "Pago registrado")
    else:
        messagebox.showerror("Error", "Seleccioná un alumno")

def actualizar_lista():
    for row in tree.get_children():
        tree.delete(row)
    for row in c.execute("SELECT * FROM alumnos"):
        tree.insert("", tk.END, values=row)

# Widgets
frame = tk.Frame(root)
frame.pack(pady=10)

labels = ["Nombre", "Apellido", "DNI", "Curso", "Celular", "Fecha inscripción"]
entries = []
for i, label in enumerate(labels):
    tk.Label(frame, text=label).grid(row=0, column=i)
entry_nombre = tk.Entry(frame); entry_nombre.grid(row=1, column=0)
entry_apellido = tk.Entry(frame); entry_apellido.grid(row=1, column=1)
entry_dni = tk.Entry(frame); entry_dni.grid(row=1, column=2)
entry_curso = tk.Entry(frame); entry_curso.grid(row=1, column=3)
entry_celular = tk.Entry(frame); entry_celular.grid(row=1, column=4)
entry_fecha = tk.Entry(frame); entry_fecha.grid(row=1, column=5)

btn_inscribir = tk.Button(root, text="Inscribir alumno", command=inscribir_alumno)
btn_inscribir.pack(pady=5)

columns = ("ID", "Nombre", "Apellido", "DNI", "Curso", "Celular", "Fecha")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.pack(fill=tk.BOTH, expand=True)

# Pagos
frame_pago = tk.Frame(root)
frame_pago.pack(pady=10)

tk.Label(frame_pago, text="Mes").grid(row=0, column=0)
entry_mes = tk.Entry(frame_pago); entry_mes.grid(row=0, column=1)

tk.Label(frame_pago, text="Monto").grid(row=0, column=2)
entry_monto = tk.Entry(frame_pago); entry_monto.grid(row=0, column=3)

tk.Label(frame_pago, text="Fecha pago").grid(row=0, column=4)
entry_fecha_pago = tk.Entry(frame_pago); entry_fecha_pago.grid(row=0, column=5)

btn_pago = tk.Button(root, text="Registrar pago", command=registrar_pago)
btn_pago.pack(pady=5)

actualizar_lista()
root.mainloop()
