import numpy as np
import scipy.stats as stats
from scipy import special
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re
from matplotlib import cm  # Para esquemas de colores
import math

def format_fraction(numerator, denominator):
    """Formatea una fracción con línea horizontal usando caracteres Unicode con mejor alineación"""
    # Convertir numerador y denominador a cadenas
    num_str = str(numerator)
    denom_str = str(denominator)
    
    # Determinar el ancho necesario para la línea de fracción
    width = max(len(num_str), len(denom_str))
    
    # Añadir espacio adicional para mejor visualización
    width += 10  # Aumentado para mejor centrado
    
    # Centrar el numerador y denominador perfectamente
    num_str = num_str.center(width)
    denom_str = denom_str.center(width)
    
    # Línea horizontal (caracteres de dibujo Unicode)
    line = "─" * width
    
    # Retornar la fracción formateada en múltiples líneas
    return f"{num_str}\n{line}\n{denom_str}"
    
def format_math_formula(formula_text):
    """Añadir formato especial para fórmulas matemáticas con símbolos Unicode"""
    # Reemplazar operadores y símbolos básicos
    formula_text = formula_text.replace("*", "×")
    formula_text = formula_text.replace("sum", "∑")
    formula_text = formula_text.replace("sqrt", "√")
    
    # Reemplazar fracciones comunes
    formula_text = formula_text.replace("1/2", "½")
    formula_text = formula_text.replace("1/4", "¼")
    formula_text = formula_text.replace("3/4", "¾")
    
    # Reemplazar superíndices
    for i in range(10):
        formula_text = formula_text.replace(f"^{i}", f"⁽{i}⁾")
    
    # Reemplazar subíndices
    for i in range(10):
        formula_text = formula_text.replace(f"_{i}", f"₍{i}₎")
    
    return formula_text

class AnovaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Varianza (ANOVA) - Herramienta Estadística")
        self.root.geometry("1000x750")
        self.root.minsize(900, 700)
        
        # Paleta de colores
        self.colors = {
            'primary': '#3498db',       # Azul principal
            'secondary': '#2ecc71',     # Verde para elementos secundarios
            'accent': '#f39c12',        # Naranja para acentos
            'warning': '#e74c3c',       # Rojo para errores/advertencias
            'background': '#f5f5f5',    # Fondo ligero
            'text': '#2c3e50',          # Color de texto principal
            'light_text': '#7f8c8d',    # Color de texto secundario
            'frame': '#ecf0f1'          # Color de fondo para frames
        }
        
        # Configurar estilo
        self.configure_style()
        
        # Variables
        self.groups = []
        self.group_names = []
        self.current_group_entries = []
        
        # Crear frame principal
        main_frame = ttk.Frame(root, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Crear cabecera
        self.create_header(main_frame)
        
        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=15, pady=(5, 15))
        
        # Pestaña de Entrada de Datos
        self.data_frame = ttk.Frame(self.notebook, style='Tab.TFrame')
        self.notebook.add(self.data_frame, text="Entrada de Datos")
        
        # Pestaña de Resultados
        self.results_frame = ttk.Frame(self.notebook, style='Tab.TFrame')
        self.notebook.add(self.results_frame, text="Resultados")
        
        # Pestaña de Fórmulas y Cálculos Detallados (NUEVA)
        self.formulas_frame = ttk.Frame(self.notebook, style='Tab.TFrame')
        self.notebook.add(self.formulas_frame, text="Cálculos Detallados")
        
        # Pestaña de Gráficos
        self.graphs_frame = ttk.Frame(self.notebook, style='Tab.TFrame')
        self.notebook.add(self.graphs_frame, text="Gráficos")
        
        # Pestaña de información sobre ANOVA
        self.info_frame = ttk.Frame(self.notebook, style='Tab.TFrame')
        self.notebook.add(self.info_frame, text="Acerca de ANOVA")
        
        # Configurar pestaña de entrada de datos
        self.setup_data_tab()
        
        # Configurar pestaña de información
        self.setup_info_tab()
        
        # Crear barra de estado
        self.status_var = tk.StringVar(value="Listo para recibir datos")
        self.status_bar = ttk.Label(
            main_frame, 
            textvariable=self.status_var, 
            style='Status.TLabel',
            anchor='w'
        )
        self.status_bar.pack(fill='x', side='bottom', padx=15, pady=(0, 10))
        
        # Funciones de formato para fórmulas matemáticas
        self.format_fraction = format_fraction
        self.format_math_formula = format_math_formula
        
    def configure_style(self):
        """Configurar estilos personalizados para los widgets"""
        style = ttk.Style()
        
        # Fuente base
        default_font = ('Segoe UI', 10)
        heading_font = ('Segoe UI', 12, 'bold')
        
        # Configurar el tema base y personalizarlo
        style.theme_use('clam')  # Usar 'clam' como base (más moderno)
        
        # Estilos para frames
        style.configure('Main.TFrame', background=self.colors['background'])
        style.configure('Tab.TFrame', background=self.colors['frame'])
        style.configure('Header.TFrame', background=self.colors['primary'])
        
        # Estilos para botones
        style.configure(
            'TButton', 
            font=default_font, 
            background=self.colors['primary'],
            foreground='white'
        )
        style.configure(
            'Accent.TButton', 
            font=default_font, 
            background=self.colors['accent'],
            foreground='white'
        )
        style.configure(
            'Secondary.TButton', 
            font=default_font, 
            background=self.colors['secondary'],
            foreground='white'
        )
        style.configure(
            'Warning.TButton', 
            font=default_font, 
            background=self.colors['warning'],
            foreground='white'
        )
        style.map(
            'TButton',
            background=[('active', self.colors['primary'])],
            foreground=[('active', 'white')]
        )
        style.map(
            'Accent.TButton',
            background=[('active', self.colors['accent'])],
            foreground=[('active', 'white')]
        )
        style.map(
            'Secondary.TButton',
            background=[('active', self.colors['secondary'])],
            foreground=[('active', 'white')]
        )
        style.map(
            'Warning.TButton',
            background=[('active', self.colors['warning'])],
            foreground=[('active', 'white')]
        )
        
        # Estilos para etiquetas
        style.configure(
            'TLabel', 
            font=default_font, 
            background=self.colors['frame'],
            foreground=self.colors['text']
        )
        style.configure(
            'Header.TLabel', 
            font=heading_font, 
            background=self.colors['primary'],
            foreground='white'
        )
        style.configure(
            'Status.TLabel', 
            font=default_font, 
            background=self.colors['background'],
            foreground=self.colors['light_text'],
            padding=5
        )
        
        # Estilos para campos de entrada
        style.configure(
            'TEntry', 
            font=default_font, 
            fieldbackground='white'
        )
        
        # Estilos para spinbox
        style.configure(
            'TSpinbox', 
            font=default_font, 
            fieldbackground='white',
            arrowsize=13
        )
        
        # Estilos para el notebook y las pestañas
        style.configure(
            'Custom.TNotebook', 
            background=self.colors['background'],
            tabmargins=[2, 5, 2, 0]
        )
        style.configure(
            'Custom.TNotebook.Tab', 
            font=default_font,
            padding=[10, 5],
            background=self.colors['background'],
            foreground=self.colors['text']
        )
        style.map(
            'Custom.TNotebook.Tab',
            background=[('selected', self.colors['primary'])],
            foreground=[('selected', 'white')]
        )
        
        # Estilos para LabelFrame
        style.configure(
            'TLabelframe', 
            font=default_font,
            background=self.colors['frame'],
            foreground=self.colors['text']
        )
        style.configure(
            'TLabelframe.Label', 
            font=('Segoe UI', 11, 'bold'),
            background=self.colors['frame'],
            foreground=self.colors['accent']
        )
        
    def create_header(self, parent):
        """Crear cabecera con título e información"""
        header_frame = ttk.Frame(parent, style='Header.TFrame')
        header_frame.pack(fill='x', padx=15, pady=(15, 5))
        
        # Título de la aplicación
        title_label = ttk.Label(
            header_frame, 
            text="ANÁLISIS DE VARIANZA (ANOVA)", 
            style='Header.TLabel'
        )
        title_label.pack(side='left', padx=10, pady=10)
        
        # Descripción 
        info_text = "Versión 2.1 | Herramienta Estadística con Fórmulas Detalladas"
        info_label = ttk.Label(
            header_frame, 
            text=info_text, 
            style='Header.TLabel',
            font=('Segoe UI', 9)
        )
        info_label.pack(side='right', padx=10, pady=10)
    
    def setup_data_tab(self):
        """Configurar la pestaña de entrada de datos"""
        # Contenedor principal con padding
        main_container = ttk.Frame(self.data_frame, style='Tab.TFrame')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Frame para controles de grupos
        group_ctrl_frame = ttk.LabelFrame(
            main_container, 
            text="Configuración de Grupos", 
            style='TLabelframe'
        )
        group_ctrl_frame.pack(fill='x', pady=(0, 15))
        
        # Contenedor interno con padding
        ctrl_inner = ttk.Frame(group_ctrl_frame, style='Tab.TFrame')
        ctrl_inner.pack(fill='x', padx=15, pady=15)
        
        # Número de grupos
        group_label_frame = ttk.Frame(ctrl_inner, style='Tab.TFrame')
        group_label_frame.pack(side='left')
        
        ttk.Label(
            group_label_frame, 
            text="Número de grupos:",
            style='TLabel'
        ).pack(side='left', padx=(0, 5))
        
        self.num_groups_var = tk.StringVar(value="3")
        self.num_groups_spinbox = ttk.Spinbox(
            group_label_frame, 
            from_=2, 
            to=10, 
            textvariable=self.num_groups_var,
            width=5,
            style='TSpinbox'
        )
        self.num_groups_spinbox.pack(side='left', padx=(0, 20))
        
        # Botones de acción para grupos
        ttk.Button(
            ctrl_inner, 
            text="Crear campos para grupos", 
            command=self.create_group_fields,
            style='TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            ctrl_inner,
            text="Usar datos de ejemplo",
            command=self.load_example_data,
            style='Secondary.TButton'
        ).pack(side='left')
        
        # Frame para los campos de grupo (se llenará dinámicamente)
        self.groups_container = ttk.Frame(main_container, style='Tab.TFrame')
        self.groups_container.pack(fill='both', expand=True)
        
        self.groups_frame = ttk.LabelFrame(
            self.groups_container, 
            text="Datos de los grupos",
            style='TLabelframe'
        )
        self.groups_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Mensaje inicial
        self.empty_message = ttk.Label(
            self.groups_frame, 
            text="Seleccione el número de grupos y haga clic en 'Crear campos para grupos'",
            style='TLabel',
            foreground=self.colors['light_text'],
            font=('Segoe UI', 10, 'italic')
        )
        self.empty_message.pack(padx=20, pady=40)
        
        # Frame para botones de acción
        action_frame = ttk.Frame(main_container, style='Tab.TFrame')
        action_frame.pack(fill='x')
        
        ttk.Button(
            action_frame, 
            text="Calcular ANOVA", 
            command=self.calculate_and_show_results,
            style='Accent.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            action_frame, 
            text="Limpiar todos los datos", 
            command=self.clear_all_data,
            style='Warning.TButton'
        ).pack(side='left')
    
    def setup_info_tab(self):
        """Configurar la pestaña de información sobre ANOVA"""
        # Contenedor principal con padding
        info_container = ttk.Frame(self.info_frame, style='Tab.TFrame')
        info_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Encabezado
        header_frame = ttk.Frame(info_container, style='Tab.TFrame')
        header_frame.pack(fill='x', pady=(0, 15))
        
        header_label = ttk.Label(
            header_frame, 
            text="¿Qué es el Análisis de Varianza (ANOVA)?",
            font=('Segoe UI', 14, 'bold'),
            foreground=self.colors['primary']
        )
        header_label.pack(side='left')
        
        # Área de texto principal
        info_text = scrolledtext.ScrolledText(
            info_container,
            wrap=tk.WORD,
            font=('Segoe UI', 11),
            background='white',
            foreground=self.colors['text'],
            padx=20,
            pady=20
        )
        info_text.pack(fill='both', expand=True)
        
        # Configurar etiquetas para formato
        info_text.tag_configure('title', font=('Segoe UI', 12, 'bold'), foreground=self.colors['primary'])
        info_text.tag_configure('subtitle', font=('Segoe UI', 11, 'bold'), foreground=self.colors['secondary'])
        info_text.tag_configure('normal', font=('Segoe UI', 11))
        info_text.tag_configure('bullet', font=('Segoe UI', 11))
        info_text.tag_configure('highlight', font=('Segoe UI', 11), foreground=self.colors['accent'])
        
        # Contenido sobre ANOVA
        info_text.insert(tk.END, "Análisis de Varianza (ANOVA) de una vía\n\n", 'title')
        
        info_text.insert(tk.END, "Definición:\n", 'subtitle')
        info_text.insert(tk.END, """El Análisis de Varianza (ANOVA) es una técnica estadística utilizada para comparar las medias de tres o más grupos. Permite determinar si existen diferencias estadísticamente significativas entre las medias de diferentes poblaciones.\n\n""", 'normal')
        
        info_text.insert(tk.END, "Fundamento del ANOVA:\n", 'subtitle')
        info_text.insert(tk.END, """El ANOVA divide la variabilidad total observada en los datos en dos componentes:\n\n""", 'normal')
        info_text.insert(tk.END, "• Variabilidad entre grupos: ", 'bullet')
        info_text.insert(tk.END, """diferencias entre las medias de los distintos grupos.\n""", 'normal')
        info_text.insert(tk.END, "• Variabilidad dentro de grupos: ", 'bullet')
        info_text.insert(tk.END, """variabilidad natural dentro de cada grupo (error).\n\n""", 'normal')
        
        info_text.insert(tk.END, "Hipótesis del ANOVA:\n", 'subtitle')
        info_text.insert(tk.END, """• Hipótesis nula (H₀): """, 'bullet')
        info_text.insert(tk.END, """Todas las medias poblacionales son iguales (μ₁ = μ₂ = ... = μₖ).\n""", 'normal')
        info_text.insert(tk.END, """• Hipótesis alternativa (H₁): """, 'bullet')
        info_text.insert(tk.END, """Al menos una media poblacional es diferente de las demás.\n\n""", 'normal')
        
        info_text.insert(tk.END, "El estadístico F:\n", 'subtitle')
        info_text.insert(tk.END, """El ANOVA utiliza el estadístico F, que es la razón entre la variabilidad entre grupos y la variabilidad dentro de grupos:\n\n""", 'normal')
        info_text.insert(tk.END, """F = Variabilidad entre grupos / Variabilidad dentro de grupos\n\n""", 'highlight')
        info_text.insert(tk.END, """• Si F es grande, sugiere que hay más variabilidad entre los grupos que dentro de ellos, lo que podría indicar diferencias significativas entre las medias.\n""", 'normal')
        info_text.insert(tk.END, """• El valor p asociado a F determina si las diferencias son estadísticamente significativas.\n\n""", 'normal')
        
        info_text.insert(tk.END, "Interpretación de los gráficos:\n", 'subtitle')
        
        info_text.insert(tk.END, """1. Boxplot (Diagrama de caja y bigotes):\n""", 'bullet')
        info_text.insert(tk.END, """   • Muestra la distribución completa de cada grupo.\n""", 'normal')
        info_text.insert(tk.END, """   • La caja representa el rango intercuartílico (IQR, del percentil 25 al 75).\n""", 'normal')
        info_text.insert(tk.END, """   • La línea dentro de la caja es la mediana.\n""", 'normal')
        info_text.insert(tk.END, """   • Los bigotes muestran el rango de datos excluyendo valores atípicos.\n""", 'normal')
        info_text.insert(tk.END, """   • Cuando hay poco solapamiento entre cajas, sugiere diferencias entre grupos.\n\n""", 'normal')
        
        info_text.insert(tk.END, """2. Distribución F:\n""", 'bullet')
        info_text.insert(tk.END, """   • Muestra la distribución teórica F con los grados de libertad del análisis.\n""", 'normal')
        info_text.insert(tk.END, """   • La línea vertical azul es el valor F calculado de los datos.\n""", 'normal')
        info_text.insert(tk.END, """   • La línea vertical naranja es el valor F crítico para α=0.05.\n""", 'normal')
        info_text.insert(tk.END, """   • Si F calculado > F crítico, se rechaza la hipótesis nula.\n\n""", 'normal')
        
        info_text.insert(tk.END, """3. Gráfico de medias:\n""", 'bullet')
        info_text.insert(tk.END, """   • Muestra las medias de cada grupo como barras.\n""", 'normal')
        info_text.insert(tk.END, """   • La línea roja punteada representa la media global.\n""", 'normal')
        info_text.insert(tk.END, """   • Ofrece una comparación visual directa entre grupos.\n""", 'normal')
        info_text.insert(tk.END, """   • Es importante recordar que diferencias visualmente grandes no siempre son estadísticamente significativas.\n\n""", 'normal')
        
        info_text.insert(tk.END, "Supuestos del ANOVA:\n", 'subtitle')
        info_text.insert(tk.END, """Para que los resultados del ANOVA sean válidos, se deben cumplir ciertos supuestos:\n\n""", 'normal')
        info_text.insert(tk.END, """• Independencia: Las observaciones deben ser independientes entre sí.\n""", 'bullet')
        info_text.insert(tk.END, """• Normalidad: Los datos en cada grupo deben seguir aproximadamente una distribución normal.\n""", 'bullet')
        info_text.insert(tk.END, """• Homocedasticidad: Las varianzas de los grupos deben ser similares (homogéneas).\n\n""", 'bullet')
        
        info_text.insert(tk.END, "Aplicaciones del ANOVA:\n", 'subtitle')
        info_text.insert(tk.END, """• Investigación científica: Comparar la eficacia de diferentes tratamientos.\n""", 'bullet')
        info_text.insert(tk.END, """• Control de calidad: Evaluar si diferentes procesos de fabricación producen resultados similares.\n""", 'bullet')
        info_text.insert(tk.END, """• Medicina: Comparar la eficacia de diferentes medicamentos o terapias.\n""", 'bullet')
        info_text.insert(tk.END, """• Agricultura: Evaluar el rendimiento de diferentes variedades de cultivos.\n""", 'bullet')
        info_text.insert(tk.END, """• Psicología: Comparar el desempeño de diferentes grupos en pruebas cognitivas.\n""", 'bullet')
        
        # Hacer el texto de solo lectura
        info_text.configure(state='disabled')
        
    def create_group_fields(self):
        """Crear campos para ingreso de datos por grupo"""
        # Limpiar el frame de grupos
        for widget in self.groups_frame.winfo_children():
            widget.destroy()
        
        self.current_group_entries = []
        
        try:
            num_groups = int(self.num_groups_var.get())
            if num_groups < 2:
                raise ValueError("Debe haber al menos 2 grupos")
            
            # Crear un canvas con scrollbar para manejar muchos grupos
            canvas_frame = ttk.Frame(self.groups_frame, style='Tab.TFrame')
            canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            canvas = tk.Canvas(canvas_frame, bg=self.colors['frame'], highlightthickness=0)
            scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
            
            # Frame dentro del canvas para los grupos
            groups_inner_frame = ttk.Frame(canvas, style='Tab.TFrame')
            
            # Configurar scrolling
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Crear una ventana en el canvas con el frame
            canvas_window = canvas.create_window((0, 0), window=groups_inner_frame, anchor="nw")
            
            # Asegurar que el frame se expanda al ancho del canvas
            def configure_canvas(event):
                canvas.itemconfig(canvas_window, width=event.width)
            canvas.bind('<Configure>', configure_canvas)
            
            # Actualizar el scroll cuando cambia el tamaño del frame interior
            def on_frame_configure(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
            groups_inner_frame.bind('<Configure>', on_frame_configure)
                
            # Crear campos para cada grupo
            for i in range(num_groups):
                group_frame = ttk.Frame(groups_inner_frame, style='Tab.TFrame')
                group_frame.pack(fill='x', pady=8)
                
                # Usar Grid para mejor alineación
                group_frame.columnconfigure(0, weight=0)  # Etiqueta nombre
                group_frame.columnconfigure(1, weight=1)  # Campo nombre
                group_frame.columnconfigure(2, weight=0)  # Etiqueta datos
                group_frame.columnconfigure(3, weight=3)  # Campo datos
                
                # Nombre del grupo
                name_label = ttk.Label(
                    group_frame, 
                    text=f"Nombre del grupo {i+1}:",
                    style='TLabel'
                )
                name_label.grid(row=0, column=0, padx=(5, 5), pady=5, sticky='w')
                
                name_entry = ttk.Entry(group_frame, width=15, style='TEntry')
                name_entry.insert(0, f"Grupo {i+1}")
                name_entry.grid(row=0, column=1, padx=(0, 15), pady=5, sticky='w')
                
                # Datos del grupo
                data_label = ttk.Label(
                    group_frame, 
                    text="Datos (números separados por espacios):",
                    style='TLabel'
                )
                data_label.grid(row=0, column=2, padx=(5, 5), pady=5, sticky='w')
                
                data_entry = ttk.Entry(group_frame, width=40, style='TEntry')
                data_entry.grid(row=0, column=3, padx=(0, 5), pady=5, sticky='ew')
                
                self.current_group_entries.append((name_entry, data_entry))
            
            # Actualizar barra de estado
            self.status_var.set(f"Se han creado campos para {num_groups} grupos")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def load_example_data(self):
        """Cargar datos de ejemplo en los campos"""
        # Datos de ejemplo actualizados
        example_data = [
            ("Método A", "78 82 85 80 79"),
            ("Método B", "88 90 85 87 89"),
            ("Método C", "75 77 74 76 73")
        ]
        
        # Asegurarse de que hay suficientes campos
        self.num_groups_var.set(str(len(example_data)))
        self.create_group_fields()
        
        # Llenar los campos con los datos de ejemplo
        for i, (name, data) in enumerate(example_data):
            if i < len(self.current_group_entries):
                name_entry, data_entry = self.current_group_entries[i]
                name_entry.delete(0, tk.END)
                name_entry.insert(0, name)
                data_entry.delete(0, tk.END)
                data_entry.insert(0, data)
        
        # Actualizar barra de estado
        self.status_var.set("Datos de ejemplo cargados correctamente")
    
    def clear_all_data(self):
        """Limpiar todos los datos ingresados"""
        for name_entry, data_entry in self.current_group_entries:
            name_entry.delete(0, tk.END)
            name_entry.insert(0, f"Grupo {self.current_group_entries.index((name_entry, data_entry))+1}")
            data_entry.delete(0, tk.END)
        
        # Limpiar resultados y gráficos
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        for widget in self.formulas_frame.winfo_children():
            widget.destroy()
            
        for widget in self.graphs_frame.winfo_children():
            widget.destroy()
        
        # Actualizar barra de estado
        self.status_var.set("Todos los datos han sido eliminados")
    
    def parse_group_data(self):
        """Validar y convertir datos de entrada"""
        self.groups = []
        self.group_names = []
        
        for name_entry, data_entry in self.current_group_entries:
            group_name = name_entry.get().strip() or f"Grupo {self.current_group_entries.index((name_entry, data_entry))+1}"
            data_text = data_entry.get().strip()
            
            # Validar y convertir los datos
            try:
                # Acepta números separados por espacios o comas
                data_text = re.sub(r',', ' ', data_text)  # Reemplazar comas por espacios
                data_text = re.sub(r'\s+', ' ', data_text)  # Normalizar espacios
                
                data_values = [float(x) for x in data_text.split()]
                
                if len(data_values) < 2:
                    messagebox.showerror(
                        "Error", 
                        f"El grupo '{group_name}' debe tener al menos 2 observaciones.",
                        icon='error'
                    )
                    return False
                
                self.groups.append(np.array(data_values))
                self.group_names.append(group_name)
                
            except ValueError:
                messagebox.showerror(
                    "Error", 
                    f"Datos inválidos para el grupo '{group_name}'. Ingrese solo números.",
                    icon='error'
                )
                return False
        
        if len(self.groups) < 2:
            messagebox.showerror(
                "Error", 
                "Se necesitan al menos 2 grupos para realizar ANOVA.",
                icon='error'
            )
            return False
            
        return True
    
    def calculate_anova(self):
        """Calcula ANOVA de una vía para los grupos proporcionados con detalles paso a paso."""
        # Número de grupos y observaciones por grupo
        k = len(self.groups)
        n_i = [len(group) for group in self.groups]
        N = sum(n_i)  # Total de observaciones

        # Crear listas para almacenar todos los datos y cálculos intermedios
        all_data = [val for group in self.groups for val in group]  # Todos los valores en una lista
        group_sums = [np.sum(group) for group in self.groups]       # Suma de cada grupo
        group_means = [np.mean(group) for group in self.groups]     # Media de cada grupo
        grand_mean = np.mean(all_data)                              # Media global
        
        # Calcular suma de cuadrados total (SCT)
        SS_total = sum((x - grand_mean)**2 for x in all_data)
        
        # Calcular suma de cuadrados entre grupos (SCE)
        SS_between = sum(n_i[i] * (group_means[i] - grand_mean)**2 for i in range(k))
        
        # Calcular suma de cuadrados dentro de grupos (SCD) 
        SS_within_by_group = []
        for i, group in enumerate(self.groups):
            ss_within_group = sum((x - group_means[i])**2 for x in group)
            SS_within_by_group.append(ss_within_group)
        
        SS_within = sum(SS_within_by_group)
        
        # Verificar que SCT = SCE + SCD (con tolerancia para errores de redondeo)
        ss_check = abs(SS_total - (SS_between + SS_within)) < 1e-10
        
        # Grados de libertad
        df_between = k - 1
        df_within = N - k
        df_total = N - 1
        
        # Medias cuadráticas
        MS_between = SS_between / df_between if df_between > 0 else 0
        MS_within = SS_within / df_within if df_within > 0 else 0
        
        # Estadístico F
        F = MS_between / MS_within if MS_within > 0 else 0
        
        # Valor p y valor crítico
        p_value = stats.f.sf(F, df_between, df_within)
        alpha = 0.05
        F_crit = stats.f.ppf(1 - alpha, df_between, df_within)
        
        # Calcular varianza dentro de cada grupo
        group_variances = [np.var(group, ddof=1) for group in self.groups]
        
        # Calcular residuos (para mostrar en la tabla de datos)
        residuals = []
        for i, group in enumerate(self.groups):
            group_residuals = [val - group_means[i] for val in group]
            residuals.append(group_residuals)
        
        # Calcular varianza combinada
        pooled_variance = SS_within / df_within
        
        # Calcular error estándar de la media (SEM)
        SEM = [math.sqrt(pooled_variance / n) for n in n_i]
        
        # Calcular coeficiente de determinación (R²)
        r_squared = SS_between / SS_total if SS_total > 0 else 0
        
        # Información para cada observación
        observation_details = []
        for i, group in enumerate(self.groups):
            for j, value in enumerate(group):
                observation_details.append({
                    'group': self.group_names[i],
                    'value': value,
                    'group_mean': group_means[i],
                    'residual': value - group_means[i],
                    'residual_squared': (value - group_means[i])**2,
                    'deviation_from_grand_mean': group_means[i] - grand_mean,
                    'total_deviation': value - grand_mean,
                    'total_deviation_squared': (value - grand_mean)**2
                })
        
        # Detalles de cálculo de la suma de cuadrados para cada grupo
        group_details = []
        for i in range(k):
            group_details.append({
                'name': self.group_names[i],
                'size': n_i[i],
                'sum': group_sums[i],
                'mean': group_means[i],
                'variance': group_variances[i],
                'sum_squared_deviations': SS_within_by_group[i],
                'squared_mean_difference': (group_means[i] - grand_mean)**2,
                'sum_squared_between': n_i[i] * (group_means[i] - grand_mean)**2
            })
        
        # Devolver todos los resultados calculados
        return {
            # Resultados estándar de ANOVA
            'F': F,
            'p_value': p_value,
            'F_crit': F_crit,
            'df_between': df_between,
            'df_within': df_within,
            'df_total': df_total,
            'group_means': group_means,
            'grand_mean': grand_mean,
            'SS_between': SS_between,
            'SS_within': SS_within,
            'SS_total': SS_total,
            'MS_between': MS_between,
            'MS_within': MS_within,
            'alpha': alpha,
            'n_i': n_i,
            'N': N,
            
            # Información adicional para la pestaña de cálculos detallados
            'group_sums': group_sums,
            'group_variances': group_variances,
            'all_data': all_data,
            'r_squared': r_squared,
            'pooled_variance': pooled_variance,
            'SEM': SEM,
            'ss_check': ss_check,
            'residuals': residuals,
            'group_details': group_details,
            'observation_details': observation_details,
            'SS_within_by_group': SS_within_by_group
        }
    
    def calculate_and_show_results(self):
        """Calcular ANOVA y mostrar resultados"""
        if not self.parse_group_data():
            return
        
        # Actualizar estado
        self.status_var.set("Calculando resultados...")
        self.root.update_idletasks()  # Forzar actualización de la UI
        
        try:
            # Calcular ANOVA con detalles
            results = self.calculate_anova()
            
            # Mostrar resultados en la pestaña de resultados
            self.display_results(results)
            
            # Mostrar fórmulas y cálculos detallados en la nueva pestaña
            self.display_detailed_calculations(results)
            
            # Crear gráficos en la pestaña de gráficos
            self.create_graphs(results)
            
            # Actualizar barra de estado
            self.status_var.set("Análisis ANOVA completado con éxito")
            
            # Cambiar a la pestaña de resultados
            self.notebook.select(1)  # Índice 1 es la pestaña de resultados
            
            # Mostrar mensaje de éxito
            messagebox.showinfo(
                "Análisis Completado", 
                "El análisis ANOVA se ha completado correctamente."
            )
        except Exception as e:
            self.status_var.set("Error al calcular ANOVA")
            messagebox.showerror("Error en cálculos", f"Se produjo un error: {str(e)}")
    
    def display_results(self, results):
        """Mostrar los resultados del análisis ANOVA"""
        # Limpiar el frame de resultados
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Crear un frame con padding para mejor visualización
        results_container = ttk.Frame(self.results_frame, style='Tab.TFrame')
        results_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header para los resultados
        header_frame = ttk.Frame(results_container, style='Tab.TFrame')
        header_frame.pack(fill='x', pady=(0, 15))
        
        header_label = ttk.Label(
            header_frame, 
            text="Resultados del Análisis de Varianza (ANOVA)",
            font=('Segoe UI', 12, 'bold'),
            foreground=self.colors['primary']
        )
        header_label.pack(side='left')
        
        # Crear un widget de texto desplazable con estilo mejorado
        text_frame = ttk.LabelFrame(
            results_container, 
            text="Resumen de resultados",
            style='TLabelframe'
        )
        text_frame.pack(fill='both', expand=True)
        
        text_area = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20,
            font=('Consolas', 10),
            background='white',
            foreground=self.colors['text']
        )
        text_area.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Insertar resultados en el área de texto con formato
        text_area.tag_configure('title', font=('Consolas', 11, 'bold'), foreground=self.colors['primary'])
        text_area.tag_configure('subtitle', font=('Consolas', 10, 'bold'), foreground=self.colors['secondary'])
        text_area.tag_configure('highlight', foreground=self.colors['accent'], font=('Consolas', 10, 'bold'))
        text_area.tag_configure('normal', font=('Consolas', 10))
        text_area.tag_configure('warning', foreground=self.colors['warning'], font=('Consolas', 10, 'bold'))
        text_area.tag_configure('conclusion', font=('Consolas', 11, 'bold'))
        
        # Título
        text_area.insert(tk.END, "ANÁLISIS DE VARIANZA (ANOVA) DE UNA VÍA\n", 'title')
        text_area.insert(tk.END, "==========================================\n\n", 'title')
        
        # Información general
        text_area.insert(tk.END, "Información general:\n", 'subtitle')
        text_area.insert(tk.END, f"  • Número de grupos: {len(self.groups)}\n", 'normal')
        text_area.insert(tk.END, f"  • Tamaño total de la muestra: {results['N']} observaciones\n", 'normal')
        text_area.insert(tk.END, f"  • Nivel de significancia (α): {results['alpha']}\n\n", 'normal')
        
        # Medias de los grupos
        text_area.insert(tk.END, "Medias de los grupos:\n", 'subtitle')
        for i, (name, mean, n) in enumerate(zip(self.group_names, results['group_means'], results['n_i'])):
            text_area.insert(tk.END, f"  • {name} (n={n}): ", 'normal')
            text_area.insert(tk.END, f"{mean:.4f}\n", 'highlight')
        
        text_area.insert(tk.END, f"  • Media global: ", 'normal')
        text_area.insert(tk.END, f"{results['grand_mean']:.4f}\n\n", 'highlight')
        
        # Tabla ANOVA
        text_area.insert(tk.END, "Tabla ANOVA:\n", 'subtitle')
        text_area.insert(tk.END, "  Fuente de         Suma de      Grados de    Media           \n", 'normal')
        text_area.insert(tk.END, "  variación        cuadrados     libertad     cuadrática      F       p-valor\n", 'normal')
        text_area.insert(tk.END, "  --------------------------------------------------------------------------\n", 'normal')
        text_area.insert(tk.END, f"  Entre grupos     {results['SS_between']:10.4f}      {results['df_between']:4d}         {results['MS_between']:10.4f}     {results['F']:6.4f}   {results['p_value']:8.6f}\n", 'normal')
        text_area.insert(tk.END, f"  Dentro de grupos {results['SS_within']:10.4f}      {results['df_within']:4d}         {results['MS_within']:10.4f}\n", 'normal')
        text_area.insert(tk.END, f"  Total            {results['SS_total']:10.4f}      {results['df_total']:4d}\n", 'normal')
        text_area.insert(tk.END, "  --------------------------------------------------------------------------\n\n", 'normal')
        
        # Valores críticos
        text_area.insert(tk.END, "Información estadística:\n", 'subtitle')
        text_area.insert(tk.END, f"  • Estadístico F calculado: ", 'normal')
        text_area.insert(tk.END, f"{results['F']:.4f}\n", 'highlight')
        text_area.insert(tk.END, f"  • Valor crítico F (α={results['alpha']}): ", 'normal')
        text_area.insert(tk.END, f"{results['F_crit']:.4f}\n", 'highlight')
        text_area.insert(tk.END, f"  • Valor p: ", 'normal')
        text_area.insert(tk.END, f"{results['p_value']:.6f}\n", 'highlight')
        text_area.insert(tk.END, f"  • Coeficiente de determinación (R²): ", 'normal')
        text_area.insert(tk.END, f"{results['r_squared']:.4f}\n\n", 'highlight')
        
        # Decisión estadística
        text_area.insert(tk.END, "Decisión estadística:\n", 'subtitle')
        if results['F'] > results['F_crit']:
            text_area.insert(tk.END, f"  F = {results['F']:.4f} > F crítico = {results['F_crit']:.4f}\n", 'warning')
        else:
            text_area.insert(tk.END, f"  F = {results['F']:.4f} ≤ F crítico = {results['F_crit']:.4f}\n", 'normal')
            
        if results['p_value'] < results['alpha']:
            text_area.insert(tk.END, f"  p-valor = {results['p_value']:.6f} < α = {results['alpha']}\n\n", 'warning')
        else:
            text_area.insert(tk.END, f"  p-valor = {results['p_value']:.6f} ≥ α = {results['alpha']}\n\n", 'normal')
        
        # Conclusión
        text_area.insert(tk.END, "Conclusión:\n", 'subtitle')
        if results['p_value'] < results['alpha']:
            conclusion = "Se rechaza la hipótesis nula (H₀)."
            text_area.insert(tk.END, f"  {conclusion}\n", 'warning')
            text_area.insert(tk.END, "  Existe evidencia estadística significativa para concluir que hay diferencias\n", 'normal')
            text_area.insert(tk.END, "  entre las medias de los grupos analizados.\n\n", 'normal')
        else:
            conclusion = "No se rechaza la hipótesis nula (H₀)."
            text_area.insert(tk.END, f"  {conclusion}\n", 'normal')
            text_area.insert(tk.END, "  No hay evidencia estadística suficiente para concluir que existen diferencias\n", 'normal')
            text_area.insert(tk.END, "  significativas entre las medias de los grupos analizados.\n\n", 'normal')
        
        # Interpretación
        text_area.insert(tk.END, "Interpretación:\n", 'subtitle')
        if results['p_value'] < results['alpha']:
            text_area.insert(tk.END, "  Los resultados sugieren que al menos una de las medias de los grupos es\n", 'normal')
            text_area.insert(tk.END, "  estadísticamente diferente de las demás. Para determinar qué grupos difieren\n", 'normal')
            text_area.insert(tk.END, "  entre sí, se recomienda realizar pruebas post hoc (como Tukey HSD o Bonferroni).\n", 'normal')
        else:
            text_area.insert(tk.END, "  Los resultados sugieren que no hay diferencias estadísticamente significativas\n", 'normal')
            text_area.insert(tk.END, "  entre las medias de los grupos analizados. Los grupos pueden considerarse\n", 'normal')
            text_area.insert(tk.END, "  estadísticamente similares en términos de la variable analizada.\n", 'normal')
        
        # Hacer que el texto sea de solo lectura
        text_area.configure(state='disabled')
        
        # Crear botones de acción
        action_frame = ttk.Frame(results_container, style='Tab.TFrame')
        action_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Button(
            action_frame, 
            text="Ver Cálculos Detallados", 
            command=lambda: self.notebook.select(2),
            style='Secondary.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            action_frame, 
            text="Ver Gráficos", 
            command=lambda: self.notebook.select(3),
            style='Secondary.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            action_frame, 
            text="Realizar Nuevo Análisis", 
            command=lambda: self.notebook.select(0),
            style='TButton'
        ).pack(side='left')
    
    def display_detailed_calculations(self, results):
        """Mostrar los cálculos detallados del análisis ANOVA con las fórmulas explícitas"""
        # Limpiar el frame de fórmulas
        for widget in self.formulas_frame.winfo_children():
            widget.destroy()
        
        # Crear un frame con padding para mejor visualización
        formulas_container = ttk.Frame(self.formulas_frame, style='Tab.TFrame')
        formulas_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header para los cálculos detallados
        header_frame = ttk.Frame(formulas_container, style='Tab.TFrame')
        header_frame.pack(fill='x', pady=(0, 15))
        
        header_label = ttk.Label(
            header_frame, 
            text="Cálculos Detallados del Análisis de Varianza (ANOVA)",
            font=('Segoe UI', 12, 'bold'),
            foreground=self.colors['primary']
        )
        header_label.pack(side='left')
        
        # Crear notebook para organizar los cálculos detallados
        calc_notebook = ttk.Notebook(formulas_container, style='Custom.TNotebook')
        calc_notebook.pack(fill='both', expand=True)
        
        # --- Pestaña 1: Formato Excel ---
        excel_frame = ttk.Frame(calc_notebook, style='Tab.TFrame')
        calc_notebook.add(excel_frame, text="Formato Excel")
        
        # Crear área de texto para mostrar el formato Excel
        excel_text = scrolledtext.ScrolledText(
            excel_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 10),
            background='white',
            foreground=self.colors['text']
        )
        excel_text.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Configurar etiquetas para formato
        excel_text.tag_configure('title', font=('Consolas', 11, 'bold'), foreground=self.colors['primary'])
        excel_text.tag_configure('subtitle', font=('Consolas', 10, 'bold'), foreground=self.colors['secondary'])
        excel_text.tag_configure('header', font=('Consolas', 10, 'bold'), foreground='#000000', background='#FFFF00')
        excel_text.tag_configure('normal', font=('Consolas', 10))
        excel_text.tag_configure('table_cell', font=('Consolas', 10), background='#FFFF00')
        excel_text.tag_configure('table_header', font=('Consolas', 10, 'italic'), background='#FFFF00')
        
        # Título
        excel_text.insert(tk.END, "Análisis de varianza de un factor\n\n", 'title')
        
        # RESUMEN
        excel_text.insert(tk.END, "RESUMEN\n", 'header')
        
        # Cabecera de la tabla de resumen
        excel_text.insert(tk.END, "{:<20}".format("Grupos"), 'table_header')
        excel_text.insert(tk.END, "{:<20}".format("Cuenta"), 'table_header')
        excel_text.insert(tk.END, "{:<20}".format("Suma"), 'table_header')
        excel_text.insert(tk.END, "{:<20}".format("Promedio"), 'table_header')
        excel_text.insert(tk.END, "{:<20}".format("Varianza"), 'table_header')
        excel_text.insert(tk.END, "\n", 'table_header')
        
        # Datos de cada grupo
        for i, group_name in enumerate(self.group_names):
            excel_text.insert(tk.END, "{:<20}".format(group_name), 'table_cell')
            excel_text.insert(tk.END, "{:<20d}".format(results['n_i'][i]), 'table_cell')
            excel_text.insert(tk.END, "{:<20.1f}".format(results['group_sums'][i]), 'table_cell')
            excel_text.insert(tk.END, "{:<20.1f}".format(results['group_means'][i]), 'table_cell')
            excel_text.insert(tk.END, "{:<20.1f}".format(results['group_variances'][i]), 'table_cell')
            excel_text.insert(tk.END, "\n", 'table_cell')
        
        excel_text.insert(tk.END, "\n", 'normal')
        
        # ANÁLISIS DE VARIANZA
        excel_text.insert(tk.END, "ANÁLISIS DE VARIANZA\n", 'header')
        
        # Cabecera de la tabla ANOVA con espaciado mejorado
        # Aumentar el ancho de la primera columna y ajustar las demás para mejorar la separación
        excel_text.insert(tk.END, "{:<30}".format("Origen de las variaciones"), 'table_header')
        excel_text.insert(tk.END, "{:<25}".format("Suma de cuadrados"), 'table_header')
        excel_text.insert(tk.END, "{:<22}".format("Grados de libertad"), 'table_header')
        excel_text.insert(tk.END, "{:<28}".format("Promedio de los cuadrados"), 'table_header')
        excel_text.insert(tk.END, "{:<18}".format("F"), 'table_header')
        excel_text.insert(tk.END, "{:<18}".format("Probabilidad"), 'table_header')
        excel_text.insert(tk.END, "{:<25}".format("Valor crítico para F"), 'table_header')
        excel_text.insert(tk.END, "\n", 'table_header')
        
        # Entre grupos - con espaciado mejorado
        excel_text.insert(tk.END, "{:<30}".format("Entre grupos"), 'table_cell')
        excel_text.insert(tk.END, "{:<25.1f}".format(results['SS_between']), 'table_cell')
        excel_text.insert(tk.END, "{:<22d}".format(results['df_between']), 'table_cell')
        excel_text.insert(tk.END, "{:<28.1f}".format(results['MS_between']), 'table_cell')
        excel_text.insert(tk.END, "{:<18.7f}".format(results['F']), 'table_cell')
        
        # Formato científico para valores pequeños de p
        if results['p_value'] < 0.001:
            p_value_str = "{:<18.4E}".format(results['p_value'])
        else:
            p_value_str = "{:<18.8f}".format(results['p_value'])
        
        excel_text.insert(tk.END, p_value_str, 'table_cell')
        excel_text.insert(tk.END, "{:<25.8f}".format(results['F_crit']), 'table_cell')
        excel_text.insert(tk.END, "\n", 'table_cell')
        
        # Dentro de grupos - con espaciado mejorado
        excel_text.insert(tk.END, "{:<30}".format("Dentro de los grupos"), 'table_cell')
        excel_text.insert(tk.END, "{:<25.1f}".format(results['SS_within']), 'table_cell')
        excel_text.insert(tk.END, "{:<22d}".format(results['df_within']), 'table_cell')
        excel_text.insert(tk.END, "{:<28.10f}".format(results['MS_within']), 'table_cell')
        excel_text.insert(tk.END, "{:<18}".format(""), 'table_cell')
        excel_text.insert(tk.END, "{:<18}".format(""), 'table_cell')
        excel_text.insert(tk.END, "{:<25}".format(""), 'table_cell')
        excel_text.insert(tk.END, "\n", 'table_cell')
        
        # Total - con espaciado mejorado
        excel_text.insert(tk.END, "{:<30}".format("Total"), 'table_cell')
        excel_text.insert(tk.END, "{:<25.1f}".format(results['SS_total']), 'table_cell')
        excel_text.insert(tk.END, "{:<22d}".format(results['df_total']), 'table_cell')
        excel_text.insert(tk.END, "{:<28}".format(""), 'table_cell')
        excel_text.insert(tk.END, "{:<18}".format(""), 'table_cell')
        excel_text.insert(tk.END, "{:<18}".format(""), 'table_cell')
        excel_text.insert(tk.END, "{:<25}".format(""), 'table_cell')
        excel_text.insert(tk.END, "\n", 'table_cell')
        
        # Hacer que el texto sea de solo lectura
        excel_text.configure(state='disabled')
        
        # --- Pestaña 2: Datos y Estadísticas Básicas ---
        basic_frame = ttk.Frame(calc_notebook, style='Tab.TFrame')
        calc_notebook.add(basic_frame, text="Datos y Estadísticas Básicas")
        
        # Crear área de texto para mostrar datos y estadísticas
        basic_text = scrolledtext.ScrolledText(
            basic_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 10),
            background='white',
            foreground=self.colors['text']
        )
        basic_text.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Configurar etiquetas para formato
        basic_text.tag_configure('title', font=('Consolas', 11, 'bold'), foreground=self.colors['primary'])
        basic_text.tag_configure('subtitle', font=('Consolas', 10, 'bold'), foreground=self.colors['secondary'])
        basic_text.tag_configure('formula', font=('Consolas', 10, 'italic'), foreground=self.colors['accent'])
        basic_text.tag_configure('normal', font=('Consolas', 10))
        basic_text.tag_configure('highlight', foreground=self.colors['accent'], font=('Consolas', 10, 'bold'))
        
        # Tabla de datos por grupo
        basic_text.insert(tk.END, "DATOS POR GRUPO\n", 'title')
        basic_text.insert(tk.END, "==============\n\n", 'title')
        
        # Mostrar los datos de cada grupo con sus estadísticas básicas
        for i, group_name in enumerate(self.group_names):
            basic_text.insert(tk.END, f"GRUPO: {group_name}\n", 'subtitle')
            basic_text.insert(tk.END, f"Tamaño de muestra (n): {results['n_i'][i]}\n", 'normal')
            
            # Datos individuales
            basic_text.insert(tk.END, "Observaciones: ", 'normal')
            for j, value in enumerate(self.groups[i]):
                basic_text.insert(tk.END, f"{value:.4f}", 'normal')
                if j < len(self.groups[i]) - 1:
                    basic_text.insert(tk.END, ", ", 'normal')
            basic_text.insert(tk.END, "\n", 'normal')
            
            # Estadísticas del grupo
            basic_text.insert(tk.END, f"Suma: ", 'normal')
            basic_text.insert(tk.END, f"{results['group_sums'][i]:.4f}\n", 'highlight')
            
            basic_text.insert(tk.END, f"Media: ", 'normal')
            basic_text.insert(tk.END, f"{results['group_means'][i]:.4f}\n", 'highlight')
            
            basic_text.insert(tk.END, f"Varianza: ", 'normal')
            basic_text.insert(tk.END, f"{results['group_variances'][i]:.4f}\n", 'highlight')
            
            # Fórmula de la media
            basic_text.insert(tk.END, "Fórmula de la media:\n", 'normal')
            
            # Crear y centrar la fracción
            numerator = "∑X"
            denominator = "n"
            fraction_lines = self.format_fraction(numerator, denominator).split('\n')
            
            for line in fraction_lines:
                # Centrar la línea de la fracción
                centered_line = "    " + line
                basic_text.insert(tk.END, f"{centered_line}\n", 'formula')
            
            basic_text.insert(tk.END, "\n", 'normal')
            
            basic_text.insert(tk.END, "Cálculo:\n", 'normal')
            
            # Crear y centrar la fracción de valores
            numerator = f"{results['group_sums'][i]:.4f}"
            denominator = f"{results['n_i'][i]}"
            fraction_lines = self.format_fraction(numerator, denominator).split('\n')
            
            for line in fraction_lines:
                # Centrar la línea de la fracción
                centered_line = "    " + line
                basic_text.insert(tk.END, f"{centered_line}\n", 'highlight')
            
            basic_text.insert(tk.END, f"\n    X̄ = {results['group_means'][i]:.4f}\n\n", 'highlight')
            
            # Fórmula de la varianza
            basic_text.insert(tk.END, "Fórmula de la varianza:\n", 'normal')
            
            # Crear y centrar la fracción
            numerator = "∑(X - X̄)²"
            denominator = "n - 1"
            fraction_lines = self.format_fraction(numerator, denominator).split('\n')
            
            for line in fraction_lines:
                # Centrar la línea de la fracción
                centered_line = "    " + line
                basic_text.insert(tk.END, f"{centered_line}\n", 'formula')
            
            basic_text.insert(tk.END, "\n", 'normal')
            
            basic_text.insert(tk.END, "Cálculo:\n", 'normal')
            
            # Crear y centrar la fracción de valores
            numerator = f"{results['SS_within_by_group'][i]:.4f}"
            denominator = f"{results['n_i'][i] - 1}"
            fraction_lines = self.format_fraction(numerator, denominator).split('\n')
            
            for line in fraction_lines:
                # Centrar la línea de la fracción
                centered_line = "    " + line
                basic_text.insert(tk.END, f"{centered_line}\n", 'highlight')
            
            basic_text.insert(tk.END, f"\n    s² = {results['group_variances'][i]:.4f}\n\n", 'highlight')
        
        # Estadísticas globales
        basic_text.insert(tk.END, "ESTADÍSTICAS GLOBALES\n", 'title')
        basic_text.insert(tk.END, "====================\n\n", 'title')
        
        basic_text.insert(tk.END, f"Número total de observaciones (N): {results['N']}\n", 'normal')
        basic_text.insert(tk.END, f"Número de grupos (k): {len(self.groups)}\n", 'normal')
        basic_text.insert(tk.END, f"Media global: ", 'normal')
        basic_text.insert(tk.END, f"{results['grand_mean']:.4f}\n", 'highlight')
        
        # Fórmula de la media global
        basic_text.insert(tk.END, "Fórmula de la media global:\n", 'normal')
        
        # Crear y centrar la fracción
        numerator = "∑X"
        denominator = "N"
        fraction_lines = self.format_fraction(numerator, denominator).split('\n')
        
        for line in fraction_lines:
            # Centrar la línea de la fracción
            centered_line = "    " + line
            basic_text.insert(tk.END, f"{centered_line}\n", 'formula')
        
        basic_text.insert(tk.END, "\n", 'normal')
        
        basic_text.insert(tk.END, "Cálculo:\n", 'normal')
        
        # Crear y centrar la fracción de valores
        numerator = f"{sum(results['group_sums']):.4f}"
        denominator = f"{results['N']}"
        fraction_lines = self.format_fraction(numerator, denominator).split('\n')
        
        for line in fraction_lines:
            # Centrar la línea de la fracción
            centered_line = "    " + line
            basic_text.insert(tk.END, f"{centered_line}\n", 'highlight')
        
        basic_text.insert(tk.END, f"\n    X̄ₜₒₜₐₗ = {results['grand_mean']:.4f}\n\n", 'highlight')
        
        # Hacer que el texto sea de solo lectura
        basic_text.configure(state='disabled')
        
        # --- Pestaña 3: Cálculos ANOVA ---
        anova_calc_frame = ttk.Frame(calc_notebook, style='Tab.TFrame')
        calc_notebook.add(anova_calc_frame, text="Cálculos ANOVA")
        
        # Crear área de texto para mostrar los cálculos ANOVA con desplazamiento
        anova_text = scrolledtext.ScrolledText(
            anova_calc_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 10),
            background='white',
            foreground=self.colors['text']
        )
        anova_text.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Configurar etiquetas para formato
        anova_text.tag_configure('title', font=('Consolas', 11, 'bold'), foreground=self.colors['primary'])
        anova_text.tag_configure('paso', font=('Consolas', 11, 'bold'), background='#FFFF00', foreground='black')
        anova_text.tag_configure('subtitle', font=('Consolas', 10, 'bold'), foreground=self.colors['secondary'])
        anova_text.tag_configure('formula', font=('Consolas', 10, 'italic'), foreground=self.colors['accent'])
        anova_text.tag_configure('normal', font=('Consolas', 10))
        anova_text.tag_configure('highlight', foreground=self.colors['accent'], font=('Consolas', 10, 'bold'))
        anova_text.tag_configure('resultado', foreground='red', font=('Consolas', 10, 'bold'))
        
        # Título general
        anova_text.insert(tk.END, "CÁLCULOS DEL ANÁLISIS DE VARIANZA (ANOVA)\n", 'title')
        anova_text.insert(tk.END, "========================================\n\n", 'title')
        
        # PASO 1: Cálculo de las medias de cada grupo y la media global
        anova_text.insert(tk.END, "PASO 1: CÁLCULO DE LAS MEDIAS DE CADA GRUPO Y LA MEDIA GLOBAL\n", 'paso')
        
        anova_text.insert(tk.END, "\nCálculo de las medias de cada grupo:\n", 'subtitle')
        
        # Mostrar el cálculo para cada grupo
        for i, group_name in enumerate(self.group_names):
            anova_text.insert(tk.END, f"\n• Media de {group_name}:\n", 'normal')
            anova_text.insert(tk.END, "  Datos: ", 'normal')
            
            # Mostrar los datos del grupo
            for j, value in enumerate(self.groups[i]):
                anova_text.insert(tk.END, f"{value}", 'normal')
                if j < len(self.groups[i]) - 1:
                    anova_text.insert(tk.END, ", ", 'normal')
            
            anova_text.insert(tk.END, "\n\n", 'normal')
            
            # Fórmula de la media con los valores actuales
            anova_text.insert(tk.END, "  Fórmula: Media = \n", 'formula')
            
            # Fracción matemática para la fórmula general
            numerator = "∑X"
            denominator = "n"
            fraction_lines = self.format_fraction(numerator, denominator).split('\n')
            
            # Asegurar que la fracción esté bien centrada
            width = 50  # Ancho fijo para la columna
            for line in fraction_lines:
                padded_line = line.center(width)
                anova_text.insert(tk.END, f"{padded_line}\n", 'formula')
            
            # Aplicación a este grupo específico - fracción con valores
            anova_text.insert(tk.END, "\n  Aplicación a los datos:\n", 'normal')
            
            # Crear fracción para la sumatorio / n con valores reales
            numerator = str(results['group_sums'][i])
            denominator = str(len(self.groups[i]))
            fraction_lines = self.format_fraction(numerator, denominator).split('\n')
            
            anova_text.insert(tk.END, "  Media = \n", 'normal')
            for line in fraction_lines:
                padded_line = line.center(width)
                anova_text.insert(tk.END, f"{padded_line}\n", 'normal')
                
            anova_text.insert(tk.END, f"\n  Media de {group_name} = {results['group_means'][i]:.4f}\n", 'resultado')
        
        # Cálculo de la media global
        anova_text.insert(tk.END, "\nCálculo de la media global:\n", 'subtitle')
        
        # Mostrar todos los datos combinados
        anova_text.insert(tk.END, "  Todos los datos: ", 'normal')
        for i, val in enumerate(results['all_data']):
            anova_text.insert(tk.END, f"{val}", 'normal')
            if i < len(results['all_data']) - 1:
                anova_text.insert(tk.END, ", ", 'normal')
        
        anova_text.insert(tk.END, "\n\n", 'normal')
        
        # Fórmula de la media global con fracción
        anova_text.insert(tk.END, "  Fórmula: Media global = \n", 'formula')
        
        # Fracción matemática para la fórmula general
        numerator = "∑X"
        denominator = "N"
        fraction_lines = self.format_fraction(numerator, denominator).split('\n')
        
        # Centrar la fracción
        width = 50  # Ancho fijo para la columna
        for line in fraction_lines:
            padded_line = line.center(width)
            anova_text.insert(tk.END, f"{padded_line}\n", 'formula')
            
        # Aplicación a todos los datos - fracción con valores
        anova_text.insert(tk.END, "\n  Aplicación a los datos:\n", 'normal')
        
        # Crear fracción para la sumatorio / N con valores
        numerator = str(sum(results['group_sums']))
        denominator = str(results['N'])
        fraction_lines = self.format_fraction(numerator, denominator).split('\n')
        
        anova_text.insert(tk.END, "  Media global = \n", 'normal')
        for line in fraction_lines:
            padded_line = line.center(width)
            anova_text.insert(tk.END, f"{padded_line}\n", 'normal')
            
        anova_text.insert(tk.END, f"\n  Media global = {results['grand_mean']:.4f}\n\n", 'resultado')
        
        # PASO 2: Cálculo de la suma de cuadrados entre grupos (SSentre)
        anova_text.insert(tk.END, "PASO 2: CÁLCULO DE LA SUMA DE CUADRADOS ENTRE GRUPOS (SSentre)\n", 'paso')
        
        anova_text.insert(tk.END, "\nSuma de cuadrados entre grupos (SCE o SSentre):\n", 'subtitle')
        anova_text.insert(tk.END, "  Fórmula: SCE = ∑ nᵢ·(X̄ᵢ - X̄ₜₒₜₐₗ)²\n", 'formula')
        anova_text.insert(tk.END, "  Donde:\n", 'normal')
        anova_text.insert(tk.END, "  - nᵢ: tamaño de la muestra del grupo i\n", 'normal')
        anova_text.insert(tk.END, "  - X̄ᵢ: media del grupo i\n", 'normal')
        anova_text.insert(tk.END, "  - X̄ₜₒₜₐₗ: media global\n\n", 'normal')
        
        # Cálculo detallado para cada grupo
        anova_text.insert(tk.END, "  Cálculo detallado:\n\n", 'normal')
        
        total_between = 0
        for i, group_name in enumerate(self.group_names):
            squared_diff = (results['group_means'][i] - results['grand_mean'])**2
            group_contribution = results['n_i'][i] * squared_diff
            total_between += group_contribution
            
            anova_text.insert(tk.END, f"  • Para {group_name}:\n", 'normal')
            anova_text.insert(tk.END, f"    n₍{i+1}₎ × (X̄₍{i+1}₎ - X̄ₜₒₜₐₗ)² = {results['n_i'][i]} × ({results['group_means'][i]:.4f} - {results['grand_mean']:.4f})²\n", 'normal')
            anova_text.insert(tk.END, f"    = {results['n_i'][i]} × {squared_diff:.6f}\n", 'normal')
            anova_text.insert(tk.END, f"    = {group_contribution:.6f}\n\n", 'normal')
        
        anova_text.insert(tk.END, "  Suma total:\n", 'normal')
        anova_text.insert(tk.END, f"  SCE = {' + '.join([f'{results['n_i'][i]} × ({results['group_means'][i]:.4f} - {results['grand_mean']:.4f})²' for i in range(len(self.groups))])}\n", 'normal')
        anova_text.insert(tk.END, f"  SCE = {results['SS_between']:.6f}\n\n", 'resultado')
        
        # PASO 3: Cálculo de la suma de cuadrados dentro de los grupos (SSdentro)
        anova_text.insert(tk.END, "PASO 3: CÁLCULO DE LA SUMA DE CUADRADOS DENTRO DE LOS GRUPOS (SSdentro)\n", 'paso')
        
        anova_text.insert(tk.END, "\nSuma de cuadrados dentro de grupos (SCD o SSdentro):\n", 'subtitle')
        anova_text.insert(tk.END, "  Fórmula: SCD = ∑∑(Xᵢⱼ - X̄ᵢ)²\n", 'formula')
        anova_text.insert(tk.END, "  Donde:\n", 'normal')
        anova_text.insert(tk.END, "  - Xᵢⱼ: valor j del grupo i\n", 'normal')
        anova_text.insert(tk.END, "  - X̄ᵢ: media del grupo i\n\n", 'normal')
        
        # Cálculo detallado para cada grupo
        anova_text.insert(tk.END, "  Cálculo detallado:\n\n", 'normal')
        
        for i, group_name in enumerate(self.group_names):
            anova_text.insert(tk.END, f"  • Para {group_name} (media = {results['group_means'][i]:.4f}):\n", 'normal')
            
            sum_squared_diff = 0
            for j, val in enumerate(self.groups[i]):
                diff = val - results['group_means'][i]
                squared_diff = diff**2
                sum_squared_diff += squared_diff
                
                anova_text.insert(tk.END, f"    (X₍{j+1}₎ - X̄)² = ({val} - {results['group_means'][i]:.4f})² = {diff:.4f}² = {squared_diff:.6f}\n", 'normal')
            
            anova_text.insert(tk.END, f"    Suma para {group_name} = {sum_squared_diff:.6f}\n\n", 'normal')
        
        # Suma total dentro de grupos
        anova_text.insert(tk.END, "  Suma total dentro de grupos:\n", 'normal')
        anova_text.insert(tk.END, f"  SCD = {' + '.join([f'{results['SS_within_by_group'][i]:.6f}' for i in range(len(self.groups))])}\n", 'normal')
        anova_text.insert(tk.END, f"  SCD = {results['SS_within']:.6f}\n\n", 'resultado')
        
        # Suma de cuadrados total (SCT)
        anova_text.insert(tk.END, "Suma de cuadrados total (SCT):\n", 'subtitle')
        anova_text.insert(tk.END, "  SCT = SCE + SCD\n", 'formula')
        anova_text.insert(tk.END, f"  SCT = {results['SS_between']:.6f} + {results['SS_within']:.6f}\n", 'normal')
        anova_text.insert(tk.END, f"  SCT = {results['SS_total']:.6f}\n\n", 'resultado')
        
        # Grados de libertad
        anova_text.insert(tk.END, "Grados de libertad:\n", 'subtitle')
        anova_text.insert(tk.END, f"  • Entre grupos (k-1): {len(self.groups)} - 1 = {results['df_between']}\n", 'normal')
        anova_text.insert(tk.END, f"  • Dentro de grupos (N-k): {results['N']} - {len(self.groups)} = {results['df_within']}\n", 'normal')
        anova_text.insert(tk.END, f"  • Total (N-1): {results['N']} - 1 = {results['df_total']}\n\n", 'normal')
        
        # Media cuadrática entre grupos - usando la función format_fraction para representar fracciones
        anova_text.insert(tk.END, "Cálculo de las medias cuadráticas:\n", 'subtitle')
        anova_text.insert(tk.END, "  • Media cuadrática entre grupos (CME):\n", 'normal')
        anova_text.insert(tk.END, "    Fórmula: CME = \n", 'formula')
        
        # Fracción para CME
        numerator = "SCE"
        denominator = "GL_entre"
        fraction_lines = self.format_fraction(numerator, denominator).split('\n')
        
        # Centrar la fracción
        width = 50  # Ancho fijo para la columna
        for line in fraction_lines:
            padded_line = line.center(width)
            anova_text.insert(tk.END, f"{padded_line}\n", 'formula')
            
        # Valores para esta fracción
        numerator = f"{results['SS_between']:.6f}"
        denominator = str(results['df_between'])
        fraction_lines = self.format_fraction(numerator, denominator).split('\n')
        
        anova_text.insert(tk.END, "\n    Aplicación a los datos:\n    CME = \n", 'normal')
        for line in fraction_lines:
            padded_line = line.center(width)
            anova_text.insert(tk.END, f"{padded_line}\n", 'normal')
            
        anova_text.insert(tk.END, f"\n    CME = {results['MS_between']:.6f}\n\n", 'resultado')
        
        # Media cuadrática dentro de grupos - con fracciones
        anova_text.insert(tk.END, "  • Media cuadrática dentro de grupos (CMD):\n", 'normal')
        anova_text.insert(tk.END, "    Fórmula: CMD = \n", 'formula')
        
        # Fracción para CMD
        numerator = "SCD"
        denominator = "GL_dentro"
        fraction_lines = self.format_fraction(numerator, denominator).split('\n')
        
        for line in fraction_lines:
            padded_line = line.center(width)
            anova_text.insert(tk.END, f"{padded_line}\n", 'formula')
            
        # Valores para esta fracción
        numerator = f"{results['SS_within']:.6f}"
        denominator = str(results['df_within'])
        fraction_lines = self.format_fraction(numerator, denominator).split('\n')
        
        anova_text.insert(tk.END, "\n    Aplicación a los datos:\n    CMD = \n", 'normal')
        for line in fraction_lines:
            padded_line = line.center(width)
            anova_text.insert(tk.END, f"{padded_line}\n", 'normal')
            
        anova_text.insert(tk.END, f"\n    CMD = {results['MS_within']:.6f}\n\n", 'resultado')
        
        # PASO 4: Cálculo del estadístico F
        anova_text.insert(tk.END, "PASO 4: CÁLCULO DEL ESTADÍSTICO F\n", 'paso')
        
        anova_text.insert(tk.END, "\nEstadístico F:\n", 'subtitle')
        anova_text.insert(tk.END, "  Fórmula: F = \n", 'formula')
        
        # Fracción para F
        numerator = "CME"
        denominator = "CMD"
        fraction_lines = self.format_fraction(numerator, denominator).split('\n')
        
        # Centrar la fracción
        width = 50  # Ancho fijo para la columna
        for line in fraction_lines:
            padded_line = line.center(width)
            anova_text.insert(tk.END, f"{padded_line}\n", 'formula')
            
        # Valores para esta fracción
        numerator = f"{results['MS_between']:.6f}"
        denominator = f"{results['MS_within']:.6f}"
        fraction_lines = self.format_fraction(numerator, denominator).split('\n')
        
        anova_text.insert(tk.END, "\n  Aplicación a los datos:\n  F = \n", 'normal')
        for line in fraction_lines:
            padded_line = line.center(width)
            anova_text.insert(tk.END, f"{padded_line}\n", 'normal')
            
        anova_text.insert(tk.END, f"\n  F = {results['F']:.6f}\n\n", 'resultado')
        
        anova_text.insert(tk.END, "Valor crítico de F (para α = 0.05):\n", 'subtitle')
        anova_text.insert(tk.END, f"  F crítico (GL_entre = {results['df_between']}, GL_dentro = {results['df_within']}) = {results['F_crit']:.6f}\n\n", 'normal')
        
        anova_text.insert(tk.END, "Valor p:\n", 'subtitle')
        anova_text.insert(tk.END, f"  p-valor = {results['p_value']:.6f}\n\n", 'normal')
        
        # PASO 5: Interpretación y conclusión
        anova_text.insert(tk.END, "PASO 5: INTERPRETACIÓN Y CONCLUSIÓN\n", 'paso')
        
        anova_text.insert(tk.END, "\nComparación del estadístico F con el valor crítico:\n", 'subtitle')
        if results['F'] > results['F_crit']:
            anova_text.insert(tk.END, f"  F calculado ({results['F']:.6f}) > F crítico ({results['F_crit']:.6f})\n", 'normal')
            anova_text.insert(tk.END, "  Por lo tanto, SE RECHAZA la hipótesis nula (H₀)\n\n", 'resultado')
        else:
            anova_text.insert(tk.END, f"  F calculado ({results['F']:.6f}) ≤ F crítico ({results['F_crit']:.6f})\n", 'normal')
            anova_text.insert(tk.END, "  Por lo tanto, NO SE RECHAZA la hipótesis nula (H₀)\n\n", 'resultado')
        
        anova_text.insert(tk.END, "Comparación del valor p con el nivel de significancia (α = 0.05):\n", 'subtitle')
        if results['p_value'] < results['alpha']:
            anova_text.insert(tk.END, f"  p-valor ({results['p_value']:.6f}) < α ({results['alpha']})\n", 'normal')
            anova_text.insert(tk.END, "  Por lo tanto, SE RECHAZA la hipótesis nula (H₀)\n\n", 'resultado')
        else:
            anova_text.insert(tk.END, f"  p-valor ({results['p_value']:.6f}) ≥ α ({results['alpha']})\n", 'normal')
            anova_text.insert(tk.END, "  Por lo tanto, NO SE RECHAZA la hipótesis nula (H₀)\n\n", 'resultado')
        
        anova_text.insert(tk.END, "Conclusión:\n", 'subtitle')
        if results['p_value'] < results['alpha']:
            anova_text.insert(tk.END, "  Existe evidencia estadística significativa para concluir que hay diferencias\n", 'normal')
            anova_text.insert(tk.END, "  entre al menos dos de las medias de los grupos analizados.\n\n", 'normal')
        else:
            anova_text.insert(tk.END, "  No hay evidencia estadística suficiente para concluir que existen diferencias\n", 'normal')
            anova_text.insert(tk.END, "  significativas entre las medias de los grupos analizados.\n\n", 'normal')
        
        # Coeficiente de determinación (R²) - con fracción
        anova_text.insert(tk.END, "Información adicional - Coeficiente de determinación (R²):\n", 'subtitle')
        anova_text.insert(tk.END, "  Fórmula: R² = \n", 'formula')
        
        # Fracción para R²
        numerator = "SCE"
        denominator = "SCT"
        fraction_lines = self.format_fraction(numerator, denominator).split('\n')
        
        # Centrar la fracción
        width = 50  # Ancho fijo para la columna
        for line in fraction_lines:
            padded_line = line.center(width)
            anova_text.insert(tk.END, f"{padded_line}\n", 'formula')
            
        # Valores para esta fracción
        numerator = f"{results['SS_between']:.6f}"
        denominator = f"{results['SS_total']:.6f}"
        fraction_lines = self.format_fraction(numerator, denominator).split('\n')
        
        anova_text.insert(tk.END, "\n  Aplicación a los datos:\n  R² = \n", 'normal')
        for line in fraction_lines:
            padded_line = line.center(width)
            anova_text.insert(tk.END, f"{padded_line}\n", 'normal')
            
        anova_text.insert(tk.END, f"\n  R² = {results['r_squared']:.4f}\n", 'resultado')
        anova_text.insert(tk.END, f"  Interpretación: El {results['r_squared']*100:.2f}% de la variabilidad total es explicada por las diferencias entre grupos.\n\n", 'normal')
        
        # Hacer que el texto sea de solo lectura
        anova_text.configure(state='disabled')
        
        
        
        # Botones para navegar a otras pestañas
        btn_frame = ttk.Frame(formulas_container, style='Tab.TFrame')
        btn_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Button(
            btn_frame, 
            text="Ver Resultados", 
            command=lambda: self.notebook.select(1),
            style='Secondary.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame, 
            text="Ver Gráficos", 
            command=lambda: self.notebook.select(3),
            style='Secondary.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame, 
            text="Realizar Nuevo Análisis", 
            command=lambda: self.notebook.select(0),
            style='TButton'
        ).pack(side='left')
    
    def create_graphs(self, results):
        """Crear gráficos para visualizar los resultados"""
        # Limpiar el frame de gráficos
        for widget in self.graphs_frame.winfo_children():
            widget.destroy()
        
        # Crear un contenedor principal con padding
        graph_container = ttk.Frame(self.graphs_frame, style='Tab.TFrame')
        graph_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header para los gráficos
        header_frame = ttk.Frame(graph_container, style='Tab.TFrame')
        header_frame.pack(fill='x', pady=(0, 15))
        
        header_label = ttk.Label(
            header_frame, 
            text="Visualización de Resultados",
            font=('Segoe UI', 12, 'bold'),
            foreground=self.colors['primary']
        )
        header_label.pack(side='left')
        
        # Crear un notebook para las pestañas de gráficos
        graph_notebook = ttk.Notebook(graph_container, style='Custom.TNotebook')
        graph_notebook.pack(fill='both', expand=True)
        
        # Pestaña para el boxplot
        boxplot_frame = ttk.Frame(graph_notebook, style='Tab.TFrame')
        graph_notebook.add(boxplot_frame, text="Boxplot")
        
        # Pestaña para la distribución F
        f_dist_frame = ttk.Frame(graph_notebook, style='Tab.TFrame')
        graph_notebook.add(f_dist_frame, text="Distribución F")
        
        # Pestaña para medias de grupo
        means_frame = ttk.Frame(graph_notebook, style='Tab.TFrame')
        graph_notebook.add(means_frame, text="Medias de Grupo")
        
        # Configurar estilo de matplotlib
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Colores para los gráficos (estilo consistente)
        box_colors = [self.colors['primary'], self.colors['secondary'], self.colors['accent']]
        while len(box_colors) < len(self.groups):
            # Añadir más colores si hay más grupos que colores definidos
            box_colors.append(plt.cm.tab10(len(box_colors)))
        
        # ------------- BOXPLOT -------------
        # Dividir el frame en dos partes: gráfico y explicación
        boxplot_top_frame = ttk.Frame(boxplot_frame, style='Tab.TFrame')
        boxplot_top_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        boxplot_bottom_frame = ttk.LabelFrame(
            boxplot_frame, 
            text="¿CÓMO INTERPRETAR ESTE GRÁFICO?",
            style='TLabelframe'
        )
        boxplot_bottom_frame.pack(fill='x', expand=False, padx=10, pady=(0, 10), ipady=5)
        
        # Crear el boxplot
        fig_boxplot = plt.Figure(figsize=(10, 6), dpi=100)
        ax_boxplot = fig_boxplot.add_subplot(111)
        
        # Configurar boxplot con colores personalizados
        boxplot = ax_boxplot.boxplot(
            self.groups, 
            labels=self.group_names,
            patch_artist=True,
            showmeans=True,
            meanline=True
        )
        
        # Personalizar colores del boxplot
        for i, box in enumerate(boxplot['boxes']):
            box_color = box_colors[i % len(box_colors)]
            box.set(facecolor=box_color, alpha=0.5)
            box.set(edgecolor=box_color, linewidth=1.5)
        
        for i, median in enumerate(boxplot['medians']):
            median.set(color=box_colors[i % len(box_colors)], linewidth=1.5)
        
        for i, cap in enumerate(boxplot['caps']):
            cap.set(color=box_colors[(i//2) % len(box_colors)], linewidth=1.5)
            
        for i, whisker in enumerate(boxplot['whiskers']):
            whisker.set(color=box_colors[(i//2) % len(box_colors)], linewidth=1.5)
            
        for i, flier in enumerate(boxplot['fliers']):
            flier.set(marker='o', markerfacecolor=box_colors[i % len(box_colors)], 
                     markeredgecolor=box_colors[i % len(box_colors)], alpha=0.5)
        
        # Añadir referencia a la media global
        ax_boxplot.axhline(
            y=results['grand_mean'], 
            color='red', 
            linestyle='--', 
            linewidth=1.5,
            alpha=0.7
        )
        ax_boxplot.text(
            len(self.groups) + 0.1, 
            results['grand_mean'], 
            f'Media global: {results["grand_mean"]:.3f}', 
            verticalalignment='center',
            color='red'
        )
        
        # Configurar aspecto del gráfico
        ax_boxplot.set_title('Distribución de los datos por grupo', fontsize=14, pad=20)
        ax_boxplot.set_ylabel('Valores', fontsize=12)
        ax_boxplot.set_xlabel('Grupos', fontsize=12)
        ax_boxplot.grid(True, axis='y', alpha=0.3)
        
        # Añadir anotación con información sobre el resultado
        if results['p_value'] < results['alpha']:
            note = f"p = {results['p_value']:.4f} < {results['alpha']} (Diferencias significativas)"
            note_color = self.colors['warning']
        else:
            note = f"p = {results['p_value']:.4f} ≥ {results['alpha']} (No hay diferencias significativas)"
            note_color = self.colors['text']
            
        ax_boxplot.annotate(
            note, 
            xy=(0.5, 0.01), 
            xycoords='figure fraction',
            horizontalalignment='center', 
            verticalalignment='bottom',
            fontsize=10,
            color=note_color,
            bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8, edgecolor=note_color)
        )
        
        fig_boxplot.tight_layout()
        
        # Añadir boxplot al frame
        canvas_boxplot = FigureCanvasTkAgg(fig_boxplot, boxplot_top_frame)
        canvas_boxplot.draw()
        canvas_boxplot.get_tk_widget().pack(fill='both', expand=True)
        
        # Añadir texto explicativo para el boxplot
        boxplot_explanation = scrolledtext.ScrolledText(
            boxplot_bottom_frame,
            wrap=tk.WORD,
            height=8,
            font=('Segoe UI', 10, 'bold'),
            background='#f8f9fa',
            foreground=self.colors['text']
        )
        boxplot_explanation.pack(fill='both', expand=True, padx=10, pady=10)
        
        boxplot_explanation.insert(tk.END, """
• Un diagrama de caja y bigotes (boxplot) muestra la distribución completa de cada grupo analizado.
• La caja central representa el rango intercuartílico (IQR) que contiene el 50% central de los datos.
• La línea horizontal dentro de la caja es la mediana (percentil 50).
• Los "bigotes" se extienden hasta los valores máximos y mínimos que no son considerados atípicos.
• Los puntos fuera de los bigotes son valores atípicos (outliers).
• La línea roja punteada horizontal representa la media global de todos los datos.

Interpretación en el ANOVA:
• Cuando hay poco solapamiento entre las cajas, sugiere diferencias significativas entre los grupos.
• Cuando hay mucho solapamiento, sugiere que no hay diferencias significativas.
• La altura de las cajas muestra la variabilidad interna de cada grupo, un factor crucial en ANOVA.
• Si un grupo tiene muchos outliers o una gran dispersión, puede afectar los resultados del análisis.
        """)
        boxplot_explanation.configure(state='disabled')
        
        # ------------- DISTRIBUCIÓN F -------------
        # Dividir el frame en dos partes: gráfico y explicación
        f_dist_top_frame = ttk.Frame(f_dist_frame, style='Tab.TFrame')
        f_dist_top_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        f_dist_bottom_frame = ttk.LabelFrame(
            f_dist_frame, 
            text="¿CÓMO INTERPRETAR ESTE GRÁFICO?",
            style='TLabelframe'
        )
        f_dist_bottom_frame.pack(fill='x', expand=False, padx=10, pady=(0, 10), ipady=5)
        
        # Crear el gráfico de distribución F
        fig_f_dist = plt.Figure(figsize=(10, 6), dpi=100)
        ax_f_dist = fig_f_dist.add_subplot(111)
        
        # Rango de valores para la distribución F
        if results['F'] > results['F_crit']:
            x_max = max(results['F'] * 1.5, results['F_crit'] * 2)
        else:
            x_max = max(results['F'] * 2, results['F_crit'] * 1.5)
            
        x = np.linspace(0, x_max, 1000)
        y = stats.f.pdf(x, results['df_between'], results['df_within'])
        
        # Sombrear área crítica
        critical_x = np.linspace(results['F_crit'], x_max, 500)
        critical_y = stats.f.pdf(critical_x, results['df_between'], results['df_within'])
        ax_f_dist.fill_between(
            critical_x, 
            critical_y, 
            alpha=0.2, 
            color=self.colors['warning'],
            label=f'Región crítica (α={results["alpha"]})'
        )
        
        # Sombrear área del estadístico F si cae en región crítica
        if results['F'] > results['F_crit']:
            f_x = np.linspace(0, results['F'], 500)
            f_y = stats.f.pdf(f_x, results['df_between'], results['df_within'])
            ax_f_dist.fill_between(
                f_x, 
                f_y, 
                alpha=0.2, 
                color=self.colors['primary']
            )
        
        # Gráfico de distribución F
        ax_f_dist.plot(x, y, color=self.colors['text'], linewidth=2, label='Distribución F')
        
        # Líneas para F calculado y F crítico
        ax_f_dist.axvline(
            results['F'], 
            color=self.colors['primary'], 
            linestyle='--', 
            linewidth=2,
            label=f'F calculado = {results["F"]:.3f}'
        )
        ax_f_dist.axvline(
            results['F_crit'], 
            color=self.colors['warning'], 
            linestyle='--', 
            linewidth=2,
            label=f'F crítico = {results["F_crit"]:.3f}'
        )
        
        # Añadir valor p
        ax_f_dist.annotate(
            f'p-valor = {results["p_value"]:.6f}', 
            xy=(0.7, 0.9), 
            xycoords='axes fraction',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8)
        )
        
        # Configurar aspecto del gráfico
        ax_f_dist.set_title(f'Distribución F con {results["df_between"]} y {results["df_within"]} grados de libertad', fontsize=14, pad=20)
        ax_f_dist.set_xlabel('Valor F', fontsize=12)
        ax_f_dist.set_ylabel('Densidad', fontsize=12)
        ax_f_dist.legend(loc='upper right', frameon=True, framealpha=0.9)
        ax_f_dist.grid(True, alpha=0.3)
        fig_f_dist.tight_layout()
        
        # Añadir gráfico de distribución F al frame
        canvas_f_dist = FigureCanvasTkAgg(fig_f_dist, f_dist_top_frame)
        canvas_f_dist.draw()
        canvas_f_dist.get_tk_widget().pack(fill='both', expand=True)
        
        # Añadir texto explicativo para la distribución F
        f_dist_explanation = scrolledtext.ScrolledText(
            f_dist_bottom_frame,
            wrap=tk.WORD,
            height=8,
            font=('Segoe UI', 10, 'bold'),
            background='#f8f9fa',
            foreground=self.colors['text']
        )
        f_dist_explanation.pack(fill='both', expand=True, padx=10, pady=10)
        
        f_dist_explanation.insert(tk.END, """
• La distribución F es el fundamento teórico del análisis ANOVA y muestra la prueba de hipótesis gráficamente.
• La curva muestra la distribución F teórica según los grados de libertad del análisis.
• La línea vertical azul representa el valor F calculado de los datos analizados.
• La línea vertical naranja muestra el valor F crítico (determinado por el nivel de significancia α=0.05).
• El área sombreada en naranja es la región crítica (región de rechazo de la hipótesis nula).

Interpretación en el ANOVA:
• Si el valor F calculado (línea azul) cae dentro de la región sombreada, se rechaza la hipótesis nula.
• Esto significa que hay diferencias estadísticamente significativas entre los grupos.
• Cuanto más a la derecha esté el valor F calculado, mayor evidencia hay de diferencias entre grupos.
• El p-valor mostrado indica la probabilidad de obtener un valor F igual o más extremo bajo la hipótesis nula.
• Un p-valor menor que α (típicamente 0.05) lleva a rechazar la hipótesis nula.
        """)
        f_dist_explanation.configure(state='disabled')
        
        # ------------- MEDIAS DE GRUPO -------------
        # Dividir el frame en dos partes: gráfico y explicación
        means_top_frame = ttk.Frame(means_frame, style='Tab.TFrame')
        means_top_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        means_bottom_frame = ttk.LabelFrame(
            means_frame, 
            text="¿CÓMO INTERPRETAR ESTE GRÁFICO?",
            style='TLabelframe'
        )
        means_bottom_frame.pack(fill='x', expand=False, padx=10, pady=(0, 10), ipady=5)
        
        # Crear gráfico de barras de medias de grupo
        fig_means = plt.Figure(figsize=(10, 6), dpi=100)
        ax_means = fig_means.add_subplot(111)
        
        # Colores para las barras, con alpha para transparencia
        bar_colors = [self.colors['primary'], self.colors['secondary'], self.colors['accent']]
        while len(bar_colors) < len(self.groups):
            bar_colors.append(plt.cm.tab10(len(bar_colors)))
        
        # Crear barras
        bars = ax_means.bar(
            self.group_names, 
            results['group_means'],
            color=bar_colors[:len(self.groups)],
            alpha=0.7,
            edgecolor='black',
            linewidth=1
        )
        
        # Añadir línea para la media global
        ax_means.axhline(
            y=results['grand_mean'], 
            color='red', 
            linestyle='--', 
            linewidth=1.5,
            alpha=0.7,
            label=f'Media global: {results["grand_mean"]:.3f}'
        )
        
        # Añadir valores sobre las barras
        for bar, mean in zip(bars, results['group_means']):
            height = bar.get_height()
            ax_means.text(
                bar.get_x() + bar.get_width() / 2., 
                height + 0.02 * (max(results['group_means']) - min(results['group_means'])),
                f'{mean:.3f}',
                ha='center', 
                va='bottom',
                fontsize=9,
                color='black'
            )
        
        # Configurar aspecto del gráfico
        ax_means.set_title('Medias por grupo', fontsize=14, pad=20)
        ax_means.set_ylabel('Valor promedio', fontsize=12)
        ax_means.set_xlabel('Grupos', fontsize=12)
        ax_means.grid(True, axis='y', alpha=0.3)
        ax_means.legend()
        
        # Añadir anotación con información sobre el resultado
        if results['p_value'] < results['alpha']:
            note = f"p = {results['p_value']:.4f} < {results['alpha']} (Diferencias significativas)"
            note_color = self.colors['warning']
        else:
            note = f"p = {results['p_value']:.4f} ≥ {results['alpha']} (No hay diferencias significativas)"
            note_color = self.colors['text']
            
        ax_means.annotate(
            note, 
            xy=(0.5, 0.01), 
            xycoords='figure fraction',
            horizontalalignment='center', 
            verticalalignment='bottom',
            fontsize=10,
            color=note_color,
            bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8, edgecolor=note_color)
        )
        
        fig_means.tight_layout()
        
        # Añadir gráfico de medias al frame
        canvas_means = FigureCanvasTkAgg(fig_means, means_top_frame)
        canvas_means.draw()
        canvas_means.get_tk_widget().pack(fill='both', expand=True)
        
        # Añadir texto explicativo para el gráfico de medias
        means_explanation = scrolledtext.ScrolledText(
            means_bottom_frame,
            wrap=tk.WORD,
            height=8,
            font=('Segoe UI', 10, 'bold'),
            background='#f8f9fa',
            foreground=self.colors['text']
        )
        means_explanation.pack(fill='both', expand=True, padx=10, pady=10)
        
        means_explanation.insert(tk.END, """
• El gráfico de barras muestra la comparación de las medias de cada grupo analizado.
• Cada barra representa el valor medio de un grupo, con su valor numérico exacto indicado sobre ella.
• La línea roja punteada horizontal indica la media global de todos los datos combinados.
• La parte inferior del gráfico muestra si las diferencias observadas son estadísticamente significativas.

Interpretación en el ANOVA:
• Este gráfico ofrece la comparación más directa e intuitiva entre las medias de los grupos.
• Diferencias visualmente grandes entre barras no siempre implican significancia estadística.
• La significancia depende también de la variabilidad dentro de cada grupo y del tamaño de muestra.
• Cuando p < 0.05, podemos concluir que al menos una de las medias es significativamente diferente.
• Este gráfico es útil para comunicar resultados, especialmente a audiencias no técnicas.
        """)
        means_explanation.configure(state='disabled')
        
        # Botones para navegar por los resultados
        btn_frame = ttk.Frame(graph_container, style='Tab.TFrame')
        btn_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Button(
            btn_frame, 
            text="Ver Resultados", 
            command=lambda: self.notebook.select(1),
            style='Secondary.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame, 
            text="Ver Cálculos Detallados", 
            command=lambda: self.notebook.select(2),
            style='Secondary.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame, 
            text="Nuevo Análisis", 
            command=lambda: self.notebook.select(0),
            style='TButton'
        ).pack(side='left')

if __name__ == "__main__":
    root = tk.Tk()
    app = AnovaApp(root)
    root.mainloop()