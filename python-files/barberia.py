import tkinter as tk
from tkinter import messagebox, ttk
import csv
from datetime import datetime, timedelta
import os

ARCHIVO_RESERVAS = "reservas.csv"
ARCHIVO_CLIENTES = "clientes_frecuentes.csv"


def inicializar_archivos():
    for archivo, campos in [
        (ARCHIVO_RESERVAS, ["Nombre", "Apellido", "Telefono", "Fecha", "Hora", "Barbero"]),
        (ARCHIVO_CLIENTES, ["Nombre", "Apellido", "Telefono"])
    ]:
        if not os.path.exists(archivo):
            with open(archivo, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(campos)


def eliminar_reservas_pasadas():
    reservas_activas = []
    ahora = datetime.now()

    with open(ARCHIVO_RESERVAS, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            fecha_hora = datetime.strptime(f"{row['Fecha']} {row['Hora']}", "%Y-%m-%d %H:%M")
            if fecha_hora >= ahora:
                reservas_activas.append(row)

    with open(ARCHIVO_RESERVAS, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(reservas_activas)


def guardar_cliente_frecuente(nombre, apellido, telefono):
    existentes = []
    with open(ARCHIVO_CLIENTES, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            existentes.append((row['Nombre'], row['Apellido'], row['Telefono']))

    if (nombre, apellido, telefono) not in existentes:
        with open(ARCHIVO_CLIENTES, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([nombre, apellido, telefono])


def verificar_disponibilidad(fecha, hora, barbero):
    with open(ARCHIVO_RESERVAS, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Fecha"] == fecha and row["Hora"] == hora and row["Barbero"] == barbero:
                return False
    return True


def guardar_reserva(nombre, apellido, telefono, fecha, hora, barbero):
    with open(ARCHIVO_RESERVAS, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([nombre, apellido, telefono, fecha, hora, barbero])


def limpiar_campos():
    entry_nombre.delete(0, tk.END)
    entry_apellido.delete(0, tk.END)
    entry_telefono.delete(0, tk.END)
    combo_hora.set("")
    entry_barbero.delete(0, tk.END)


def generar_horas_disponibles():
    horas = []
    inicio = datetime.strptime("10:00", "%H:%M")
    fin = datetime.strptime("20:00", "%H:%M")
    while inicio < fin:
        horas.append(inicio.strftime("%H:%M"))
        inicio += timedelta(minutes=40)
    return horas


def realizar_reserva():
    nombre = entry_nombre.get().strip().title()
    apellido = entry_apellido.get().strip().title()
    telefono = entry_telefono.get().strip()
    barbero = entry_barbero.get().strip().title()
    hora = combo_hora.get()
    fecha = datetime.now().strftime("%Y-%m-%d")
    dia_semana = datetime.now().weekday()

    if dia_semana >= 6:
        messagebox.showwarning("Cerrado", "La barbería no abre los domingos.")
        return

    if not (nombre and apellido and telefono and hora):
        messagebox.showwarning("Campos incompletos", "Completa todos los campos obligatorios.")
        return

    if barbero and not verificar_disponibilidad(fecha, hora, barbero):
        messagebox.showerror("No disponible", f"{barbero} ya tiene una reserva a esa hora.")
        return

    guardar_reserva(nombre, apellido, telefono, fecha, hora, barbero)
    guardar_cliente_frecuente(nombre, apellido, telefono)
    messagebox.showinfo("Reserva exitosa", "Tu cita ha sido agendada.")
    limpiar_campos()


def cancelar_o_editar_reserva():
    ventana = tk.Toplevel(root)
    ventana.title("Gestionar Reservas")
    ventana.grab_set()
    ventana.configure(bg="#111111")

    tree = ttk.Treeview(ventana, columns=("Nombre", "Apellido", "Telefono", "Fecha", "Hora", "Barbero"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill="both", expand=True)

    with open(ARCHIVO_RESERVAS, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            tree.insert("", tk.END, values=(row["Nombre"], row["Apellido"], row["Telefono"], row["Fecha"], row["Hora"], row["Barbero"]))

    def eliminar_seleccion():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Nada seleccionado", "Selecciona una reserva.")
            return

        datos = tree.item(seleccion[0])["values"]
        tree.delete(seleccion[0])

        reservas_restantes = []
        with open(ARCHIVO_RESERVAS, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if list(row.values()) != list(map(str, datos)):
                    reservas_restantes.append(row)

        with open(ARCHIVO_RESERVAS, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(reservas_restantes)

        messagebox.showinfo("Cancelada", "La reserva fue cancelada correctamente.")

    def editar_seleccion():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Nada seleccionado", "Selecciona una reserva.")
            return

        datos = tree.item(seleccion[0])["values"]
        ventana_editar = tk.Toplevel(ventana)
        ventana_editar.title("Editar Reserva")
        ventana_editar.grab_set()
        ventana_editar.configure(bg="#111111")

        campos = ["Nombre", "Apellido", "Telefono", "Hora", "Barbero"]
        entradas = []

        for i, campo in enumerate(campos):
            tk.Label(ventana_editar, text=campo, bg="#111111", fg="white").grid(row=i, column=0)
            if campo == "Hora":
                hora_var = tk.StringVar(ventana_editar)
                hora_combo = ttk.Combobox(ventana_editar, textvariable=hora_var, values=generar_horas_disponibles(), state="readonly")
                hora_combo.set(datos[4])
                hora_combo.grid(row=i, column=1)
                entradas.append(hora_combo)
            else:
                entry = tk.Entry(ventana_editar)
                entry.insert(0, datos[i])
                entry.grid(row=i, column=1)
                entradas.append(entry)

        def guardar_edicion():
            nuevos_datos = [e.get().strip().title() if isinstance(e, tk.Entry) else e.get() for e in entradas]
            nuevos_datos.insert(3, datos[3])

            reservas_actualizadas = []
            with open(ARCHIVO_RESERVAS, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if list(row.values()) != list(map(str, datos)):
                        reservas_actualizadas.append(row)

            reservas_actualizadas.append({
                "Nombre": nuevos_datos[0],
                "Apellido": nuevos_datos[1],
                "Telefono": nuevos_datos[2],
                "Fecha": nuevos_datos[3],
                "Hora": nuevos_datos[4],
                "Barbero": nuevos_datos[5]
            })

            with open(ARCHIVO_RESERVAS, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(reservas_actualizadas)

            messagebox.showinfo("Editado", "La reserva fue editada correctamente.")
            ventana_editar.destroy()
            ventana.destroy()

        tk.Button(ventana_editar, text="Guardar cambios", command=guardar_edicion).grid(row=len(campos), column=0, columnspan=2, pady=10)

    tk.Button(ventana, text="Cancelar reserva seleccionada", command=eliminar_seleccion).pack(pady=5)
    tk.Button(ventana, text="Editar reserva seleccionada", command=editar_seleccion).pack(pady=5)


inicializar_archivos()
eliminar_reservas_pasadas()

root = tk.Tk()
root.title("Caliking Barbershop - Reservas")
root.configure(bg="#000000")

frame = tk.Frame(root, bg="#000000")
frame.pack(expand=True)

style = ttk.Style()
style.configure("TCombobox", fieldbackground="#333", background="#222", foreground="white")

labels = ["Nombre:", "Apellido:", "Telefono:", "Hora:", "Barbero (opcional):"]
for i, text in enumerate(labels):
    tk.Label(frame, text=text, fg="white", bg="#000000").grid(row=i, column=0, sticky="e")

entry_nombre = tk.Entry(frame)
entry_apellido = tk.Entry(frame)
entry_telefono = tk.Entry(frame)
combo_hora = ttk.Combobox(frame, values=generar_horas_disponibles(), state="readonly")
entry_barbero = tk.Entry(frame)

entries = [entry_nombre, entry_apellido, entry_telefono, combo_hora, entry_barbero]
for i, entry in enumerate(entries):
    entry.grid(row=i, column=1)

btn_reservar = tk.Button(frame, text="Reservar", command=realizar_reserva, bg="#222", fg="white")
btn_reservar.grid(row=5, column=0, columnspan=2, pady=10)

btn_gestionar = tk.Button(frame, text="Gestionar reservas", command=cancelar_o_editar_reserva, bg="#444", fg="white")
btn_gestionar.grid(row=6, column=0, columnspan=2)


def centrar_ventana(ventana):
    ventana.update_idletasks()
    w = ventana.winfo_width()
    h = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (w // 2)
    y = (ventana.winfo_screenheight() // 2) - (h // 2)
    ventana.geometry(f"+{x}+{y}")

centrar_ventana(root)
root.mainloop()
