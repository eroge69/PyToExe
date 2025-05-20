import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class HotelReservationSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reservas de Hotel")
        
        self.create_database()
        self.setup_ui()
        self.view_reservations()

    def create_database(self):
        conn = sqlite3.connect('hotel_reservations.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            check_in DATE NOT NULL,
            check_out DATE NOT NULL,
            room_type TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

    def add_reservation(self):
        name = self.entry_name.get()
        check_in = self.entry_check_in.get()
        check_out = self.entry_check_out.get()
        room_type = self.entry_room_type.get()
        
        # Validación de fechas
        try:
            datetime.strptime(check_in, "%Y-%m-%d")
            datetime.strptime(check_out, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto. Use YYYY-MM-DD.")
            return
        
        conn = sqlite3.connect('hotel_reservations.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO reservations (name, check_in, check_out, room_type)
        VALUES (?, ?, ?, ?)
        ''', (name, check_in, check_out, room_type))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Reserva agregada correctamente.")
        self.view_reservations()

    def view_reservations(self):
        conn = sqlite3.connect('hotel_reservations.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reservations')
        reservations = cursor.fetchall()
        conn.close()

        # Limpiar tabla antes de actualizar
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Insertar datos en tabla
        for reservation in reservations:
            self.tree.insert("", "end", values=reservation)

    def delete_reservation(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione una reserva para eliminar.")
            return
        
        reservation_id = self.tree.item(selected_item)['values'][0]
        conn = sqlite3.connect('hotel_reservations.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Reserva eliminada correctamente.")
        self.view_reservations()

    def edit_reservation(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione una reserva para editar.")
            return
        
        reservation_data = self.tree.item(selected_item)['values']
        reservation_id, name, check_in, check_out, room_type = reservation_data

        # Crear ventana emergente para editar
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Reserva")

        tk.Label(edit_window, text="Nombre:").grid(row=0, column=0)
        entry_name = tk.Entry(edit_window)
        entry_name.grid(row=0, column=1)
        entry_name.insert(0, name)

        tk.Label(edit_window, text="Fecha de entrada (YYYY-MM-DD):").grid(row=1, column=0)
        entry_check_in = tk.Entry(edit_window)
        entry_check_in.grid(row=1, column=1)
        entry_check_in.insert(0, check_in)

        tk.Label(edit_window, text="Fecha de salida (YYYY-MM-DD):").grid(row=2, column=0)
        entry_check_out = tk.Entry(edit_window)
        entry_check_out.grid(row=2, column=1)
        entry_check_out.insert(0, check_out)

        tk.Label(edit_window, text="Tipo de habitación:").grid(row=3, column=0)
        entry_room_type = tk.Entry(edit_window)
        entry_room_type.grid(row=3, column=1)
        entry_room_type.insert(0, room_type)

        def update_reservation():
            new_name = entry_name.get()
            new_check_in = entry_check_in.get()
            new_check_out = entry_check_out.get()
            new_room_type = entry_room_type.get()

            # Validar fechas
            try:
                datetime.strptime(new_check_in, "%Y-%m-%d")
                datetime.strptime(new_check_out, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha incorrecto. Use YYYY-MM-DD.")
                return
            
            conn = sqlite3.connect('hotel_reservations.db')
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE reservations
            SET name=?, check_in=?, check_out=?, room_type=?
            WHERE id=?
            ''', (new_name, new_check_in, new_check_out, new_room_type, reservation_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Reserva actualizada correctamente.")
            edit_window.destroy()
            self.view_reservations()

        tk.Button(edit_window, text="Guardar Cambios", command=update_reservation).grid(row=4, column=0, columnspan=2)

    def setup_ui(self):
        # Campos de entrada
        tk.Label(self.root, text="Nombre:").grid(row=0, column=0)
        self.entry_name = tk.Entry(self.root)
        self.entry_name.grid(row=0, column=1)

        tk.Label(self.root, text="Fecha de entrada (YYYY-MM-DD):").grid(row=1, column=0)
        self.entry_check_in = tk.Entry(self.root)
        self.entry_check_in.grid(row=1, column=1)

        tk.Label(self.root, text="Fecha de salida (YYYY-MM-DD):").grid(row=2, column=0)
        self.entry_check_out = tk.Entry(self.root)
        self.entry_check_out.grid(row=2, column=1)

        tk.Label(self.root, text="Tipo de habitación:").grid(row=3, column=0)
        self.entry_room_type = tk.Entry(self.root)
        self.entry_room_type.grid(row=3, column=1)

        # Botones
        tk.Button(self.root, text="Agregar Reserva", command=self.add_reservation).grid(row=4, column=0, columnspan=2)
        tk.Button(self.root, text="Eliminar Reserva", command=self.delete_reservation).grid(row=5, column=0, columnspan=2)
        tk.Button(self.root, text="Editar Reserva", command=self.edit_reservation).grid(row=6, column=0, columnspan=2)

        # Tabla de reservas
        columns = ("ID", "Nombre", "Check-in", "Check-out", "Tipo de habitación")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.grid(row=7, column=0, columnspan=2)

# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = HotelReservationSystem(root)
    root.mainloop()