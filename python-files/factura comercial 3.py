import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Conexión y creación de tabla en SQLite
conn = sqlite3.connect("facturacion.db")
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS productos (
    id TEXT PRIMARY KEY,
    descripcion TEXT,
    precio_compra REAL,
    precio_venta REAL,
    existencia INTEGER
)
''')
conn.commit()

# Ventana principal y configuración del Notebook
root = tk.Tk()
root.title("Sistema de Facturación")
root.geometry("800x600")

notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill="both")

# --- Pestaña Factura ---
factura_frame = ttk.Frame(notebook)
notebook.add(factura_frame, text="Factura")

# Título de la factura
label_title = ttk.Label(factura_frame, text="FACTURA COMERCIAL", font=("Helvetica", 16, "bold"))
label_title.pack(pady=10)

# Datos del Cliente
client_frame = ttk.LabelFrame(factura_frame, text="Datos del Cliente")
client_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(client_frame, text="Nombre del Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_cliente = ttk.Entry(client_frame)
entry_cliente.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(client_frame, text="D.N.I:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_dni = ttk.Entry(client_frame)
entry_dni.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(client_frame, text="R.T.N:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_rtn = ttk.Entry(client_frame)
entry_rtn.grid(row=2, column=1, padx=5, pady=5)

# Sección para agregar productos a la factura
producto_frame = ttk.LabelFrame(factura_frame, text="Agregar Producto")
producto_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(producto_frame, text="ID Producto:").grid(row=0, column=0, padx=5, pady=5)
entry_prod_id = ttk.Entry(producto_frame)
entry_prod_id.grid(row=0, column=1, padx=5, pady=5)

# Botón para buscar producto (en base de datos)
def buscar_producto():
    pid = entry_prod_id.get()
    cursor.execute("SELECT descripcion, precio_venta FROM productos WHERE id = ?", (pid,))
    producto = cursor.fetchone()
    if producto:
        desc, precio_u = producto
        entry_desc.config(state="normal")
        entry_desc.delete(0, tk.END)
        entry_desc.insert(0, desc)
        entry_desc.config(state="readonly")
        
        entry_precio.config(state="normal")
        entry_precio.delete(0, tk.END)
        entry_precio.insert(0, f"{precio_u:.2f}")
        entry_precio.config(state="readonly")
    else:
        messagebox.showerror("Error", "Producto no encontrado")

btn_buscar = ttk.Button(producto_frame, text="Buscar", command=buscar_producto)
btn_buscar.grid(row=0, column=2, padx=5, pady=5)

ttk.Label(producto_frame, text="Descripción:").grid(row=0, column=3, padx=5, pady=5)
entry_desc = ttk.Entry(producto_frame, state="readonly")
entry_desc.grid(row=0, column=4, padx=5, pady=5)

ttk.Label(producto_frame, text="Precio Unitario:").grid(row=1, column=0, padx=5, pady=5)
entry_precio = ttk.Entry(producto_frame, state="readonly")
entry_precio.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(producto_frame, text="Cantidad:").grid(row=1, column=3, padx=5, pady=5)
entry_cantidad = ttk.Entry(producto_frame)
entry_cantidad.grid(row=1, column=4, padx=5, pady=5)

# Sección para agregar la línea de producto a la factura
def agregar_producto_factura():
    pid = entry_prod_id.get()
    desc = entry_desc.get()
    try:
        precio_u = float(entry_precio.get())
        cantidad = int(entry_cantidad.get())
    except ValueError:
        messagebox.showerror("Error", "Ingrese valores válidos para precio y cantidad")
        return
    total_linea = precio_u * cantidad
    tree_factura.insert("", tk.END, values=(pid, desc, f"{precio_u:.2f}", cantidad, f"{total_linea:.2f}"))
    # Limpiar campos
    entry_prod_id.delete(0, tk.END)
    entry_desc.config(state="normal")
    entry_desc.delete(0, tk.END)
    entry_desc.config(state="readonly")
    entry_precio.config(state="normal")
    entry_precio.delete(0, tk.END)
    entry_precio.config(state="readonly")
    entry_cantidad.delete(0, tk.END)
    actualizar_totales()

btn_agregar_producto = ttk.Button(producto_frame, text="Agregar", command=agregar_producto_factura)
btn_agregar_producto.grid(row=2, column=0, columnspan=5, pady=5)

# Treeview para mostrar los productos agregados a la factura
factura_items_frame = ttk.Frame(factura_frame)
factura_items_frame.pack(fill="both", expand=True, padx=10, pady=5)

tree_factura = ttk.Treeview(factura_items_frame, columns=("ID", "Descripción", "Precio Unitario", "Cantidad", "Total"), show="headings")
for col in ("ID", "Descripción", "Precio Unitario", "Cantidad", "Total"):
    tree_factura.heading(col, text=col)
tree_factura.pack(fill="both", expand=True)

# Totales: Subtotal, Impuesto y Total
totales_frame = ttk.Frame(factura_frame)
totales_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(totales_frame, text="Subtotal:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
var_subtotal = tk.StringVar()
entry_subtotal = ttk.Entry(totales_frame, textvariable=var_subtotal, state="readonly")
entry_subtotal.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(totales_frame, text="Impuesto (15%):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
var_impuesto = tk.StringVar()
entry_impuesto = ttk.Entry(totales_frame, textvariable=var_impuesto, state="readonly")
entry_impuesto.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(totales_frame, text="Total:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
var_total = tk.StringVar()
entry_total = ttk.Entry(totales_frame, textvariable=var_total, state="readonly")
entry_total.grid(row=0, column=5, padx=5, pady=5)

def actualizar_totales():
    subtotal = 0.0
    for child in tree_factura.get_children():
        try:
            subtotal += float(tree_factura.item(child)['values'][4])
        except:
            continue
    impuesto = subtotal * 0.15
    total = subtotal + impuesto
    var_subtotal.set(f"{subtotal:.2f} L.")
    var_impuesto.set(f"{impuesto:.2f} L.")
    var_total.set(f"{total:.2f} L.")

# Función para imprimir la factura (genera un PDF)
def imprimir_factura():
    nombre = entry_cliente.get()
    dni = entry_dni.get()
    rtn = entry_rtn.get()
    if not tree_factura.get_children():
        messagebox.showwarning("Advertencia", "No hay productos en la factura")
        return
    pdf_file = "factura.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    y = height - 40
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, "FACTURA COMERCIAL")
    y -= 40
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Cliente: {nombre}")
    y -= 20
    c.drawString(40, y, f"D.N.I: {dni}")
    y -= 20
    c.drawString(40, y, f"R.T.N: {rtn}")
    y -= 40
    c.drawString(40, y, "Productos:")
    y -= 20
    c.drawString(40, y, "ID")
    c.drawString(100, y, "Descripción")
    c.drawString(300, y, "Precio Unitario")
    c.drawString(400, y, "Cantidad")
    c.drawString(500, y, "Total")
    y -= 20
    for child in tree_factura.get_children():
        values = tree_factura.item(child)['values']
        c.drawString(40, y, str(values[0]))
        c.drawString(100, y, str(values[1]))
        c.drawString(300, y, str(values[2]))
        c.drawString(400, y, str(values[3]))
        c.drawString(500, y, str(values[4]))
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50
    y -= 20
    c.drawString(40, y, f"Subtotal: {var_subtotal.get()}")
    y -= 20
    c.drawString(40, y, f"Impuesto (15%): {var_impuesto.get()}")
    y -= 20
    c.drawString(40, y, f"Total: {var_total.get()}")
    c.save()
    messagebox.showinfo("Factura", f"Factura guardada como {pdf_file}")

btn_imprimir = ttk.Button(factura_frame, text="Imprimir factura", command=imprimir_factura)
btn_imprimir.pack(pady=10)

# --- Pestaña Productos ---
productos_frame = ttk.Frame(notebook)
notebook.add(productos_frame, text="Productos")

# Treeview para mostrar los productos registrados
tree_productos = ttk.Treeview(productos_frame, columns=("ID", "Descripción", "Precio Compra", "Precio Venta", "Existencia"), show="headings")
for col in ("ID", "Descripción", "Precio Compra", "Precio Venta", "Existencia"):
    tree_productos.heading(col, text=col)
tree_productos.pack(fill="both", expand=True, padx=10, pady=5)

# Botones de acción en la pestaña Productos
botones_frame = ttk.Frame(productos_frame)
botones_frame.pack(fill="x", padx=10, pady=5)

def registrar_producto():
    reg_win = tk.Toplevel(root)
    reg_win.title("Registrar Producto")
    ttk.Label(reg_win, text="ID:").grid(row=0, column=0, padx=5, pady=5)
    entry_id = ttk.Entry(reg_win)
    entry_id.grid(row=0, column=1, padx=5, pady=5)
    
    ttk.Label(reg_win, text="Descripción:").grid(row=1, column=0, padx=5, pady=5)
    entry_descripcion = ttk.Entry(reg_win)
    entry_descripcion.grid(row=1, column=1, padx=5, pady=5)
    
    ttk.Label(reg_win, text="Precio Compra:").grid(row=2, column=0, padx=5, pady=5)
    entry_precio_compra = ttk.Entry(reg_win)
    entry_precio_compra.grid(row=2, column=1, padx=5, pady=5)
    
    ttk.Label(reg_win, text="Precio Venta:").grid(row=3, column=0, padx=5, pady=5)
    entry_precio_venta = ttk.Entry(reg_win)
    entry_precio_venta.grid(row=3, column=1, padx=5, pady=5)
    
    ttk.Label(reg_win, text="Existencia:").grid(row=4, column=0, padx=5, pady=5)
    entry_existencia = ttk.Entry(reg_win)
    entry_existencia.grid(row=4, column=1, padx=5, pady=5)
    
    def guardar_producto():
        pid = entry_id.get()
        descripcion = entry_descripcion.get()
        try:
            precio_compra = float(entry_precio_compra.get())
            precio_venta = float(entry_precio_venta.get())
            existencia = int(entry_existencia.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores válidos")
            return
        try:
            cursor.execute(
                "INSERT INTO productos (id, descripcion, precio_compra, precio_venta, existencia) VALUES (?,?,?,?,?)",
                (pid, descripcion, precio_compra, precio_venta, existencia)
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Producto registrado correctamente")
            reg_win.destroy()
            cargar_productos()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El ID ya existe")
    
    btn_guardar = ttk.Button(reg_win, text="Guardar", command=guardar_producto)
    btn_guardar.grid(row=5, column=0, columnspan=2, pady=10)

def editar_producto():
    selected = tree_productos.focus()
    if not selected:
        messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
        return
    values = tree_productos.item(selected)['values']
    reg_win = tk.Toplevel(root)
    reg_win.title("Editar Producto")
    ttk.Label(reg_win, text="ID:").grid(row=0, column=0, padx=5, pady=5)
    entry_id = ttk.Entry(reg_win)
    entry_id.grid(row=0, column=1, padx=5, pady=5)
    entry_id.insert(0, values[0])
    entry_id.config(state="disabled")
    
    ttk.Label(reg_win, text="Descripción:").grid(row=1, column=0, padx=5, pady=5)
    entry_descripcion = ttk.Entry(reg_win)
    entry_descripcion.grid(row=1, column=1, padx=5, pady=5)
    entry_descripcion.insert(0, values[1])
    
    ttk.Label(reg_win, text="Precio Compra:").grid(row=2, column=0, padx=5, pady=5)
    entry_precio_compra = ttk.Entry(reg_win)
    entry_precio_compra.grid(row=2, column=1, padx=5, pady=5)
    entry_precio_compra.insert(0, values[2])
    
    ttk.Label(reg_win, text="Precio Venta:").grid(row=3, column=0, padx=5, pady=5)
    entry_precio_venta = ttk.Entry(reg_win)
    entry_precio_venta.grid(row=3, column=1, padx=5, pady=5)
    entry_precio_venta.insert(0, values[3])
    
    ttk.Label(reg_win, text="Existencia:").grid(row=4, column=0, padx=5, pady=5)
    entry_existencia = ttk.Entry(reg_win)
    entry_existencia.grid(row=4, column=1, padx=5, pady=5)
    entry_existencia.insert(0, values[4])
    
    def actualizar_producto():
        descripcion = entry_descripcion.get()
        try:
            precio_compra = float(entry_precio_compra.get())
            precio_venta = float(entry_precio_venta.get())
            existencia = int(entry_existencia.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores válidos")
            return
        cursor.execute(
            "UPDATE productos SET descripcion=?, precio_compra=?, precio_venta=?, existencia=? WHERE id=?",
            (descripcion, precio_compra, precio_venta, existencia, values[0])
        )
        conn.commit()
        messagebox.showinfo("Éxito", "Producto actualizado correctamente")
        reg_win.destroy()
        cargar_productos()
    
    btn_guardar = ttk.Button(reg_win, text="Actualizar", command=actualizar_producto)
    btn_guardar.grid(row=5, column=0, columnspan=2, pady=10)

def eliminar_producto():
    selected = tree_productos.focus()
    if not selected:
        messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
        return
    values = tree_productos.item(selected)['values']
    resp = messagebox.askyesno("Confirmar", f"¿Desea eliminar el producto {values[1]}?")
    if resp:
        cursor.execute("DELETE FROM productos WHERE id=?", (values[0],))
        conn.commit()
        cargar_productos()
        messagebox.showinfo("Eliminado", "Producto eliminado")

def cargar_productos():
    # Limpia el treeview y carga la tabla desde la BD
    for item in tree_productos.get_children():
        tree_productos.delete(item)
    cursor.execute("SELECT * FROM productos")
    for row in cursor.fetchall():
        tree_productos.insert("", tk.END, values=row)

# Al dar doble click en un producto se permite actualizar la existencia
def actualizar_existencia(event):
    selected_item = tree_productos.focus()
    if not selected_item:
        return
    values = tree_productos.item(selected_item)['values']
    cantidad_actual = values[4]
    # Se pregunta al usuario cuánto desea agregar (o restar)
    cantidad_nueva = simpledialog.askinteger("Actualizar Existencia",
                                               f"Existencia actual: {cantidad_actual}\nIngrese cantidad a agregar (o negativa para restar):")
    if cantidad_nueva is not None:
        nueva_existencia = cantidad_actual + cantidad_nueva
        if nueva_existencia < 0:
            messagebox.showerror("Error", "La existencia no puede ser negativa")
            return
        cursor.execute("UPDATE productos SET existencia=? WHERE id=?", (nueva_existencia, values[0]))
        conn.commit()
        cargar_productos()
        messagebox.showinfo("Éxito", "Existencia actualizada")

# Botones en la pestaña Productos
btn_registrar = ttk.Button(botones_frame, text="Registrar Productos", command=registrar_producto)
btn_registrar.grid(row=0, column=0, padx=5)

btn_editar = ttk.Button(botones_frame, text="Editar", command=editar_producto)
btn_editar.grid(row=0, column=1, padx=5)

btn_eliminar = ttk.Button(botones_frame, text="Eliminar producto", command=eliminar_producto)
btn_eliminar.grid(row=0, column=2, padx=5)

btn_actualizar = ttk.Button(botones_frame, text="Actualizar inventario", command=cargar_productos)
btn_actualizar.grid(row=0, column=3, padx=5)

tree_productos.bind("<Double-1>", actualizar_existencia)

# Inicializa la lista de productos desde la BD
cargar_productos()

root.mainloop()

# Al cerrar la aplicación, se cierra la conexión a la BD
conn.close()
