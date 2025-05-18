# -*- coding: utf-8 -*-
"""
Código de adquisición NI con mejoras para evitar el error -50103 ("resource reserved"):
 - Variable de estado para impedir tareas simultáneas.
 - Manejo de excepciones para liberar la tarea.
 - Adquisición en modo Finite (por tiempo) o Continuous (stop manual).
 - Visualización en tiempo real con Matplotlib (sólo para canales marcados con 'Plot').
 - Exportación a formato .mat o .xlsx.
 - Optimizaciones de memoria, rendimiento y thread safety.
 - Panel de ajustes integrado en la interfaz principal.
 - Streaming a disco para grabación continua extendida.

Requisitos:
  pip install nidaqmx numpy scipy pandas matplotlib psutil
"""

import sys
# sys.path.append(r'C:\Users\jaime.romero\AppData\Roaming\Python\Python39\site-packages')
import nidaqmx

# Imports completos
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from nidaqmx.constants import (
    AcquisitionType,
    TerminalConfiguration,
    ExcitationSource,
    BridgeUnits,
    BridgeConfiguration,
    ThermocoupleType,
    TemperatureUnits,
    CJCSource,
    AccelUnits,
    AccelSensitivityUnits,
    Coupling,
    StrainUnits,
    StrainGageBridgeType
)
import numpy as np
import scipy.io as sio
import pandas as pd
import time
import threading
import pickle
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# Imports adicionales para streaming
import os
import shutil
import datetime
from pathlib import Path
from queue import Queue
import json
import psutil

###############################################################################
#                 Límites de frecuencia para cada tipo de módulo             #
###############################################################################
MODULE_FREQ_LIMITS = {
    "NI 9201": {"min": 1,    "max": 500000},
    "NI 9219": {"min": 1,    "max": 100},
    "NI 9237": {"min": 100,  "max": 50000},
    "NI 9211": {"min": 1,    "max": 75},
    "NI 9234": {"min": 1652, "max": 51200}
}

# Configuración global para manejo de memoria
MAX_BUFFER_SIZE = 10000  # Máximo número de puntos en buffers de visualización

###############################################################################
#  Asegurar que existan QUARTER_BRIDGE, HALF_BRIDGE y FULL_BRIDGE en StrainGageBridgeType
###############################################################################
# Busca esta línea en el código
if not hasattr(StrainGageBridgeType, "QUARTER_BRIDGE"):
    StrainGageBridgeType.QUARTER_BRIDGE = 10372
# Añade estas líneas justo después
if not hasattr(StrainGageBridgeType, "QUARTER_BRIDGE_I"):
    StrainGageBridgeType.QUARTER_BRIDGE_I = 10271
if not hasattr(StrainGageBridgeType, "QUARTER_BRIDGE_II"):
    StrainGageBridgeType.QUARTER_BRIDGE_II = 10272

class FakeStrainGageBridgeType:
    """Permite mapear configuraciones de puente en NI 9219 (no definidas en StrainGageBridgeType)."""
    def __init__(self, value):
        self.value = value

from nidaqmx.constants import StrainGageBridgeType as SGBridgeType

NI9219_BRIDGE_MAP = {
    "Cuarto de Puente I": SGBridgeType.QUARTER_BRIDGE_I,
    "Cuarto de Puente II": SGBridgeType.QUARTER_BRIDGE_II,
    "Medio de Puente I": SGBridgeType.HALF_BRIDGE_I,
    "Medio de Puente II": SGBridgeType.HALF_BRIDGE_II,
    "Puente Completo I": SGBridgeType.FULL_BRIDGE_I,
    "Puente Completo II": SGBridgeType.FULL_BRIDGE_II,
    "Puente Completo III": SGBridgeType.FULL_BRIDGE_III
}

CUSTOM_BRIDGE_CONFIGS = {
    "Cuarto de Puente":  BridgeConfiguration.QUARTER_BRIDGE,
    "Medio de Puente":   BridgeConfiguration.HALF_BRIDGE,
    "Completo":          BridgeConfiguration.FULL_BRIDGE
}

# Mapa de configuraciones de puente para NI 9237
NI9237_BRIDGE_MAP = {
    "Quarter Bridge I": (BridgeConfiguration.QUARTER_BRIDGE, 4.0),
    "Quarter Bridge II": (BridgeConfiguration.QUARTER_BRIDGE, 4.0),
    "Half Bridge I": (BridgeConfiguration.HALF_BRIDGE, 2.0),
    "Half Bridge II": (BridgeConfiguration.HALF_BRIDGE, 2.0),
    "Full Bridge I": (BridgeConfiguration.FULL_BRIDGE, 1.0),
    "Full Bridge II": (BridgeConfiguration.FULL_BRIDGE, 1.0),
    "Full Bridge III": (BridgeConfiguration.FULL_BRIDGE, 1.0)
}

###############################################################################
#              Función para configurar canales según el tipo de módulo        #
###############################################################################
def configure_channel(task, device_name, channel_index, product_type, adv_info):
    """
    Configura el canal correspondiente en la tarea 'task', de acuerdo
    al tipo de módulo 'product_type' y los parámetros 'adv_info'.
    """
    ch_phys = f"{device_name}/ai{channel_index}"
    print(f"Configurando canal {ch_phys} - Tipo: {product_type}")

    if product_type == "NI 9201":
        task.ai_channels.add_ai_voltage_chan(
            physical_channel=ch_phys,
            min_val=-10.0,
            max_val=10.0,
            terminal_config=TerminalConfiguration.RSE
        )

    elif product_type == "NI 9219":
        mode_sel = adv_info.get("SelectedMode", "Voltage")
        if mode_sel == "Voltage":
            sel_range = adv_info.get("SelectedRange", "±15 V")
            ranges = {
                "±125 mV": (-0.125, 0.125),
                "±1 V":    (-1, 1),
                "±4 V":    (-4, 4),
                "±15 V":   (-15.0, 15.0),
                "±60 V":   (-60.0, 60.0)
            }
            min_val, max_val = ranges.get(sel_range, (-10.0, 10.0))
            task.ai_channels.add_ai_voltage_chan(ch_phys, min_val=min_val, max_val=max_val)
    
        elif mode_sel == "Current":
            # NI 9219: -0.025 a 0.025 A
            task.ai_channels.add_ai_current_chan(
                ch_phys,
                min_val=-0.025,
                max_val=0.025
            )
    
        elif mode_sel in ["2-Wire Resistance", "4-Wire Resistance"]:
            sel_range = adv_info.get("SelectedRange", "0-2000 Ω")
            ranges = {
                "0-500 Ω":   (0, 500),
                "0-2000 Ω":  (0, 2000),
                "0-10000 Ω": (0, 10000)
            }
            min_val, max_val = ranges.get(sel_range, (0, 2000))
            task.ai_channels.add_ai_resistance_chan(
                physical_channel=ch_phys,
                min_val=min_val,
                max_val=max_val,
                current_excit_source=ExcitationSource.INTERNAL,
                current_excit_val=0.0005
            )
    
        elif mode_sel == "Strain":
            # Obtener la configuración del puente
            rng = adv_info.get("SelectedRange", "Cuarto de Puente I")
            strain_config = NI9219_BRIDGE_MAP.get(rng, NI9219_BRIDGE_MAP["Cuarto de Puente I"])
            
            # Parámetros fundamentales
            nominal_r = float(adv_info.get("BridgeResistance", "120"))
            # MODIFICACIÓN: Obtener el factor de galga desde adv_info
            gage_factor = float(adv_info.get("GageFactor", "2.0"))
            
            # CORRECCIÓN: Valores dentro del rango permitido por el hardware
            # Valores seguros pero más amplios para evitar saturación
            min_val = -8.0e-3  # Ligeramente mayor que el límite mínimo (-8.333333e-3)
            max_val = 18.0e-3  # Ligeramente menor que el límite máximo (18.750000e-3)
            
            # Mantener el voltaje de excitación estándar para NI 9219
            excitation_voltage = 2.5
            
            # Guardar el gage_factor en adv_info para usarlo en el procesamiento posterior
            adv_info["GageFactor"] = gage_factor
            
            # Verificar si hay offset en adv_info
            offset_key = f"{device_name}/ai{channel_index}"
            offset_val = adv_info.get("Offset", 0.0)
            
            # Configurar el canal con los parámetros óptimos
            print(f"Configurando canal de strain {ch_phys} - Tipo: {rng}, GF: {gage_factor}, R: {nominal_r}Ω")
            strain_chan = task.ai_channels.add_ai_strain_gage_chan(
                physical_channel=ch_phys,
                min_val=min_val,
                max_val=max_val,
                units=StrainUnits.STRAIN,  # Configurar como STRAIN para que la tara funcione correctamente
                strain_config=strain_config,
                voltage_excit_source=ExcitationSource.INTERNAL,
                voltage_excit_val=excitation_voltage,
                gage_factor=gage_factor,
                nominal_gage_resistance=nominal_r,
                poisson_ratio=0.3,
                lead_wire_resistance=0.0,
                initial_bridge_voltage=0.0  # Asegurar que no hay voltaje inicial
            )
            
            print(f"Canal {ch_phys} configurado para strain con range={min_val} a {max_val}, Exc={excitation_voltage}V, Offset={offset_val}")
                                
        else:
            task.ai_channels.add_ai_voltage_chan(ch_phys, min_val=-10.0, max_val=10.0)

    elif product_type == "NI 9237":
        bm = adv_info.get("BridgeMode", "Quarter Bridge I")  # Valor predeterminado actualizado
        
        # Obtener la configuración del mapa
        bc_enum, _ = NI9237_BRIDGE_MAP.get(bm, (BridgeConfiguration.QUARTER_BRIDGE, 4.0))
        
        exc_v = float(adv_info.get("ExcitationVoltage", "2.5"))
        task.ai_channels.add_ai_bridge_chan(
            physical_channel=ch_phys,
            min_val=-25.0,
            max_val=25.0,
            units=BridgeUnits.MILLIVOLTS_PER_VOLT,
            bridge_config=bc_enum,
            voltage_excit_source=ExcitationSource.INTERNAL,
            voltage_excit_val=exc_v
        )
    
    elif product_type == "NI 9211":
        tc_type_str = adv_info.get("ThermocoupleType", "T")
        
        # Mapeo de strings a constantes ThermocoupleType
        tc_map = {
            "J": ThermocoupleType.J,
            "K": ThermocoupleType.K,
            "T": ThermocoupleType.T,
            "E": ThermocoupleType.E,
            "N": ThermocoupleType.N,
            "R": ThermocoupleType.R,
            "S": ThermocoupleType.S,
            "B": ThermocoupleType.B
        }
        
        # Convertir string a enum si es necesario
        if isinstance(tc_type_str, str):
            tc_type = tc_map.get(tc_type_str, ThermocoupleType.T)
        else:
            tc_type = tc_type_str
        
        # Rangos de temperatura para cada tipo de termopar
        thermocouple_ranges = {
            ThermocoupleType.J: (-210.0, 1200.0),
            ThermocoupleType.K: (-200.0, 1372.0),
            ThermocoupleType.T: (-200.0, 400.0),
            ThermocoupleType.E: (-200.0, 1000.0),
            ThermocoupleType.N: (-200.0, 1300.0),
            ThermocoupleType.R: (-50.0, 1768.0),
            ThermocoupleType.S: (-50.0, 1768.0),
            ThermocoupleType.B: (250.0, 1820.0)
        }
        
        # Obtener los límites para el tipo de termopar seleccionado
        min_val, max_val = thermocouple_ranges.get(tc_type, (-200.0, 400.0))
        
        print(f"Configurando termopar tipo {tc_type} con rango: {min_val}°C a {max_val}°C")
        
        task.ai_channels.add_ai_thrmcpl_chan(
            ch_phys,
            thermocouple_type=tc_type,
            min_val=min_val,
            max_val=max_val,
            units=TemperatureUnits.DEG_C,
            cjc_source=CJCSource.BUILT_IN
        )

    elif product_type == "NI 9234":
        coupling_str = adv_info.get("Coupling", "IEPE").upper()
        if coupling_str == "IEPE":
            sens = float(adv_info.get("Sensitivity", "100.0"))
            iepe_curr = float(adv_info.get("IEPECurrent", "0.004"))
            task.ai_channels.add_ai_accel_chan(
                physical_channel=ch_phys,
                min_val=-5.0,
                max_val=5.0,
                units=AccelUnits.G,
                sensitivity=sens,
                sensitivity_units=AccelSensitivityUnits.MILLIVOLTS_PER_G,
                current_excit_val=iepe_curr
            )
        elif coupling_str in ["DC", "AC"]:
            chan = task.ai_channels.add_ai_voltage_chan(ch_phys, min_val=-5.0, max_val=5.0)
            from nidaqmx.constants import Coupling
            chan.ai_coupling = Coupling.DC if coupling_str == "DC" else Coupling.AC
        else:
            task.ai_channels.add_ai_voltage_chan(ch_phys, min_val=-5.0, max_val=5.0)

    else:
        # Fallback: voltaje ±10 V
        task.ai_channels.add_ai_voltage_chan(ch_phys, min_val=-10.0, max_val=10.0)
        
    print(f"Canal {ch_phys} configurado correctamente.")

###############################################################################
#                 Clase para ventana emergente de visualización                #
###############################################################################
class PlotWindow(tk.Toplevel):
    """
    Ventana emergente para mostrar gráficos en tiempo real.
    """
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app  # Guardar referencia a la app principal
        self.title("Visualización en Tiempo Real")
        self.geometry("800x600")
        
        # Configuración para cerrar ventana sin detener actualización
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Indicador de si la ventana está visible o no
        self.is_visible = True
        
        # Frame para botones/controles
        control_frame = ttk.Frame(self)
        control_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        # Botón para exportar imagen
        self.btn_export_img = ttk.Button(
            control_frame, 
            text="Exportar Imagen", 
            command=self.export_plot_image
        )
        self.btn_export_img.pack(side="left", padx=5)
        
        # Botón para limpiar/reiniciar gráficos
        self.btn_clear = ttk.Button(
            control_frame, 
            text="Limpiar Gráficos", 
            command=self.clear_plots
        )
        self.btn_clear.pack(side="left", padx=5)
        
        # MODIFICACIÓN: Reemplazar selector de puntos con límites temporales
        ttk.Label(control_frame, text="Rango temporal (s):").pack(side="left", padx=5)
        
        # Campo para tiempo mínimo
        self.time_min_var = tk.StringVar(value="0.0")
        self.time_min_entry = ttk.Entry(
            control_frame, 
            textvariable=self.time_min_var,
            width=6
        )
        self.time_min_entry.pack(side="left", padx=2)
        
        ttk.Label(control_frame, text="a").pack(side="left", padx=2)
        
        # Campo para tiempo máximo
        self.time_max_var = tk.StringVar(value="10.0")
        self.time_max_entry = ttk.Entry(
            control_frame, 
            textvariable=self.time_max_var,
            width=6
        )
        self.time_max_entry.pack(side="left", padx=2)
        
        # Botón para aplicar límites temporales
        self.btn_apply_limits = ttk.Button(
            control_frame, 
            text="Aplicar", 
            command=self.apply_time_limits
        )
        self.btn_apply_limits.pack(side="left", padx=5)
        
        # Botón para mostrar todo el rango temporal
        self.btn_show_all = ttk.Button(
            control_frame, 
            text="Mostrar Todo", 
            command=self.show_all_time_range
        )
        self.btn_show_all.pack(side="left", padx=5)
        
        # Frame para gráficos
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear figura y canvas de matplotlib
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Añadir toolbar de navegación
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        
        # Lista para almacenar los ejes
        self.plot_axes = []
        
        # Rango temporal actualmente aplicado (None para todo el rango disponible)
        self.current_time_min = None
        self.current_time_max = None
    
    def on_close(self):
        """Se llama cuando el usuario cierra la ventana."""
        self.is_visible = False
        self.withdraw()  # Ocultar en lugar de destruir
    
    def export_plot_image(self):
        """Exporta los gráficos actuales como imagen."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Exportar Gráfico", f"Imagen guardada en {file_path}")
    
    def clear_plots(self):
        """Limpia los gráficos actuales."""
        # Limpiar los buffers de la aplicación principal de forma segura
        with self.app.data_lock:
            # Hacer una copia de las claves para evitar modificar durante iteración
            buffer_keys = list(self.app.plot_buffers.keys())
            for key in buffer_keys:
                self.app.plot_buffers[key] = []
        
        # Actualizar los gráficos con los buffers vacíos
        if hasattr(self, 'plot_axes') and self.plot_axes:
            for ax in self.plot_axes:
                ax.clear()
                ax.text(0.5, 0.5, "No hay datos para mostrar", ha="center", va="center")
            self.fig.tight_layout()
            self.canvas.draw()
    
    def apply_time_limits(self):
        """Aplica los límites temporales especificados en los campos de entrada."""
        try:
            time_min = float(self.time_min_var.get())
            time_max = float(self.time_max_var.get())
            
            if time_min >= time_max:
                messagebox.showerror("Error", "El tiempo mínimo debe ser menor que el tiempo máximo.")
                return
            
            self.current_time_min = time_min
            self.current_time_max = time_max
            
            # Actualizar gráficos con los nuevos límites
            with self.app.data_lock:
                valid_display_buffers = {}
                for key, data in self.app.results.items():
                    if isinstance(data, np.ndarray) and data.size > 0:
                        valid_display_buffers[key] = data.copy()
            
            if valid_display_buffers:
                self.update_plots(valid_display_buffers)
                
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduzca valores numéricos válidos para los límites temporales.")
    
    def show_all_time_range(self):
        """Muestra todo el rango temporal disponible en los datos."""
        self.current_time_min = None
        self.current_time_max = None
        
        # Actualizar los campos de entrada con el rango completo de los datos
        self.time_min_var.set("0.0")
        
        # Intentar determinar el tiempo máximo de los datos actuales
        max_time = 10.0  # Valor por defecto
        with self.app.data_lock:
            for key, data in self.app.results.items():
                if isinstance(data, np.ndarray) and data.size > 0:
                    # Calcular tiempo máximo basado en frecuencia de muestreo
                    sampling_rate = getattr(self.app, 'current_rate', 1000.0)
                    time_max = data.size / sampling_rate
                    max_time = max(max_time, time_max)
        
        self.time_max_var.set(f"{max_time:.1f}")
        
        # Actualizar gráficos con todo el rango
        with self.app.data_lock:
            valid_display_buffers = {}
            for key, data in self.app.results.items():
                if isinstance(data, np.ndarray) and data.size > 0:
                    valid_display_buffers[key] = data.copy()
        
        if valid_display_buffers:
            self.update_plots(valid_display_buffers)    
    
    def update_plots(self, buffers):
        """
        Actualiza los gráficos con los datos proporcionados, aplicando los límites temporales.
        
        Args:
            buffers: Diccionario con los buffers de datos a graficar
        """
        try:
            # Verificaciones de seguridad
            if self.app is None:
                return
                
            if not buffers:
                return
                
            plotted_keys = list(buffers.keys())
            n_plots = len(plotted_keys)
            
            # Solo recrear los subplots si ha cambiado el número de canales
            if len(self.plot_axes) != n_plots:
                self.fig.clf()
                self.plot_axes = []
                if n_plots > 0:
                    for i in range(n_plots):
                        ax = self.fig.add_subplot(n_plots, 1, i + 1)
                        self.plot_axes.append(ax)
            
            # Si no hay nada que graficar, limpiar el gráfico
            if n_plots == 0:
                return
            
            # Obtener la frecuencia de muestreo efectiva desde la app principal
            sampling_rate = getattr(self.app, 'current_rate', 1000.0)
            print(f"Usando frecuencia de muestreo para gráficos: {sampling_rate} Hz")
            
            # Actualizar cada subplot existente
            for i, key in enumerate(plotted_keys):
                if i >= len(self.plot_axes):
                    continue  # Protección contra índices fuera de rango
                    
                ax = self.plot_axes[i]
                ax.clear()  # Limpiar solo los datos, no recrear el subplot
                
                # Verificar que los datos existan y sean válidos
                if key not in buffers:
                    ax.text(0.5, 0.5, f"No hay datos para visualizar en este canal", 
                           ha="center", va="center")
                    continue
                    
                # Verificar si el buffer tiene datos de forma segura
                data_valid = False
                if isinstance(buffers[key], np.ndarray):
                    data_valid = buffers[key].size > 0
                else:
                    data_valid = bool(buffers[key])
                    
                if not data_valid:
                    ax.text(0.5, 0.5, f"No hay datos para visualizar en este canal", 
                           ha="center", va="center")
                    continue
                
                # Obtener datos completos para procesamiento
                try:
                    if isinstance(buffers[key], np.ndarray):
                        data = buffers[key].copy()
                    else:
                        data = np.array(list(buffers[key]), dtype=float)
                    
                    # Crear vector de tiempo para todos los datos
                    full_time = np.arange(data.size) / sampling_rate
                    
                    # Aplicar filtrado por límites temporales si están establecidos
                    if self.current_time_min is not None and self.current_time_max is not None:
                        # Encontrar índices que corresponden al rango temporal
                        time_mask = (full_time >= self.current_time_min) & (full_time <= self.current_time_max)
                        
                        # Verificar si hay datos en el rango seleccionado
                        if np.any(time_mask):
                            # Filtrar datos y tiempo
                            filtered_data = data[time_mask]
                            filtered_time = full_time[time_mask]
                        else:
                            # No hay datos en el rango seleccionado
                            ax.text(0.5, 0.5, f"No hay datos en el rango temporal seleccionado", 
                                  ha="center", va="center")
                            continue
                    else:
                        # Usar todos los datos disponibles
                        filtered_data = data
                        filtered_time = full_time
                    
                except Exception as e:
                    ax.text(0.5, 0.5, f"Error al procesar datos: {str(e)[:50]}...", 
                           ha="center", va="center")
                    continue
                
                # Obtener el nombre personalizado si existe
                display_name = self.app.channel_names.get(key, key) if hasattr(self.app, 'channel_names') else key
                
                # Verificar datos para graficar
                if len(filtered_data) > 0:
                    try:
                        # Graficar datos con línea más visible
                        ax.plot(filtered_time, filtered_data, label=display_name, linewidth=1.5, color='blue')
                        
                        # Ajustar leyenda y título
                        ax.legend(loc="upper right", fontsize=9)
                        ax.set_title(display_name, fontsize=10)
                        ax.grid(True, linestyle='--', alpha=0.7)
                        
                        # Añadir etiqueta al eje X y formato adecuado
                        ax.set_xlabel('Tiempo (s)', fontsize=9)
                        
                        # Establecer límites del eje X al rango seleccionado
                        if self.current_time_min is not None and self.current_time_max is not None:
                            ax.set_xlim(self.current_time_min, self.current_time_max)
                        
                        # Optimizar visualización de etiquetas de tiempo dependiendo del rango
                        time_range = filtered_time[-1] - filtered_time[0]
                        if time_range < 1:
                            # Para tiempos menores a 1 segundo, mostrar milisegundos
                            ax.xaxis.set_major_formatter(lambda x, pos: f"{x*1000:.0f} ms")
                        elif time_range < 60:
                            # Para tiempos entre 1 segundo y 1 minuto
                            ax.xaxis.set_major_formatter(lambda x, pos: f"{x:.1f} s")
                        else:
                            # Para tiempos mayores a 1 minuto, mostrar minutos:segundos
                            ax.xaxis.set_major_formatter(lambda x, pos: f"{int(x/60):d}m {int(x%60):02d}s")
                        
                        # Ajustar los límites automáticamente para el eje Y
                        if len(filtered_data) > 1:
                            y_min = np.min(filtered_data)
                            y_max = np.max(filtered_data)
                            
                            # Añadir margen del 10% para mejor visualización
                            y_range = y_max - y_min
                            if abs(y_range) < 1e-10:
                                y_range = abs(y_min) * 0.1 if y_min != 0 else 0.1
                                
                            y_min -= y_range * 0.1
                            y_max += y_range * 0.1
                            
                            ax.set_ylim(y_min, y_max)
                        
                        # Añadir estadísticas con verificación de datos
                        if len(filtered_data) > 1:
                            try:
                                stats_text = (f"Máx: {np.max(filtered_data):.3f}  Mín: {np.min(filtered_data):.3f}  "
                                             f"Media: {np.mean(filtered_data):.3f}  Desv: {np.std(filtered_data):.3f}")
                                ax.text(0.02, 0.02, stats_text, transform=ax.transAxes, 
                                        fontsize=8, bbox=dict(facecolor='white', alpha=0.7))
                            except Exception as stat_error:
                                pass
                    except Exception as plot_error:
                        ax.text(0.5, 0.5, f"Error al visualizar datos: {str(plot_error)[:50]}...", 
                               ha="center", va="center")
                else:
                    ax.text(0.5, 0.5, f"No hay datos válidos para {display_name}", 
                           ha="center", va="center")
            
            # Ajustar layout y dibujar
            self.fig.tight_layout()
            self.canvas.draw()
        except Exception as e:
            import traceback
            traceback.print_exc()

def generate_valid_frequencies(module_type):
    """
    Genera una lista de frecuencias válidas según el tipo de módulo.
    
    Args:
        module_type: String con el tipo de módulo ("NI 9233", "NI 9234" o "NI 9237")
        
    Returns:
        Lista de frecuencias válidas como strings
    """
    valid_freqs = []
    
    if module_type == "NI 9234":
        # Fórmula para NI 9234: Fs = (Fm / 256) / N, donde N es un entero 1..31
        # Fm (base de tiempo interna) = 13.1072 MHz
        Fm = 13107200
        base_fs = Fm / 256
        for N in range(1, 32):
            fs = base_fs / N
            valid_freqs.append(round(fs))
            
    elif module_type == "NI 9237":
        # Fórmula para NI 9237: Fs = 50kS/s / N, donde N es un entero 1..31
        base_fs = 50000
        for N in range(1, 32):
            fs = base_fs / N
            valid_freqs.append(round(fs))
            
    elif module_type == "NI 9233":
        # Valores similares a los mostrados en la tabla
        base_fs = 50000
        for N in range(1, 32):
            fs = base_fs / N
            valid_freqs.append(round(fs))
    
    # Convertir a string y ordenar de mayor a menor
    valid_freqs = sorted(valid_freqs, reverse=True)
    return [str(freq) for freq in valid_freqs]  


###############################################################################
#                 Clase principal de la Interfaz de Usuario (Tkinter)         #
###############################################################################
class AcquisitionGUI:
    
    def zero_from_current_value(self, cfg, ch):
        """Realiza un cerado manual basado en el valor actual de la señal"""
        if cfg["ProductType"] != "NI 9219":
            return
            
        device_name = cfg["DeviceName"]
        key = f"{device_name}/ai{ch}"
        
        # Verificar si hay datos disponibles
        current_value = None
        with self.data_lock:
            if key in self.results and isinstance(self.results[key], np.ndarray) and self.results[key].size > 0:
                # Tomar la media para mayor estabilidad
                current_value = np.mean(self.results[key]) / 1e6  # Convertir de μstrain a strain
        
        if current_value is None:
            messagebox.showerror("Error", "No hay datos disponibles para realizar cerado manual")
            return
        
        # Recuperar la configuración original (offset actual)
        st = cfg["channel_settings"][ch]
        original_offset = st.get("offset_val", 0.0)
        
        # Calcular el nuevo offset (offset original + valor actual convertido a strain)
        new_offset = original_offset + current_value
        
        # Guardar el nuevo offset
        st["offset_val"] = new_offset
        
        # Guardar también en el diccionario global
        if not hasattr(self, 'strain_offsets'):
            self.strain_offsets = {}
        self.strain_offsets[key] = new_offset
        
        # Mostrar información del cerado
        messagebox.showinfo(
            "Cerado Manual Completado",
            f"Canal: {key}\n\n"
            f"Offset original: {original_offset:.6e}V ({original_offset*1e6:.2f} μstrain)\n"
            f"Valor actual: {current_value:.6e}V ({current_value*1e6:.2f} μstrain)\n"
            f"Nuevo offset: {new_offset:.6e}V ({new_offset*1e6:.2f} μstrain)\n\n"
            f"La señal debería estar próxima a cero en la siguiente adquisición."
        )    
    
    def diagnose_strain_channel(self, device_name, channel_index):
        """
        Función de diagnóstico para verificar el estado de cerado de un canal
        """
        key = f"{device_name}/ai{channel_index}"
        
        # Buscar información del canal
        channel_info = None
        cfg = None
        for c in self.device_configs:
            if c["DeviceName"] == device_name:
                cfg = c
                if channel_index in c["channel_settings"]:
                    channel_info = c["channel_settings"][channel_index]
                    break
        
        if not channel_info:
            messagebox.showerror("Error", f"No se encontró información para el canal {key}")
            return
            
        # Verificar offset almacenado
        offset_val = channel_info.get("offset_val", "No establecido")
        if offset_val == "No establecido":
            offset_val = self.strain_offsets.get(key, "No establecido") if hasattr(self, 'strain_offsets') else "No establecido"
        
        # Verificar datos actuales
        current_data = None
        with self.data_lock:
            if key in self.results and hasattr(self.results[key], 'size') and self.results[key].size > 0:
                current_data = self.results[key].copy()
        
        # Mostrar información de diagnóstico
        info = f"Diagnóstico para canal {key}:\n\n"
        info += f"Offset almacenado: {offset_val}\n"
        if isinstance(offset_val, (int, float)):
            info += f"Equivalente a ~{offset_val*1e6:.1f} μstrain sin procesar\n\n"
        
        if current_data is not None:
            info += f"Datos actuales (μstrain):\n"
            info += f"Min: {np.min(current_data):.1f}\n"
            info += f"Max: {np.max(current_data):.1f}\n"
            info += f"Media: {np.mean(current_data):.1f}\n"
            info += f"Desviación: {np.std(current_data):.1f}\n"
        else:
            info += "No hay datos disponibles actualmente."
        
        messagebox.showinfo("Diagnóstico de Strain", info)    
    
    ############################################################################
    #                 Métodos para construir la GUI de cada módulo             #
    ############################################################################
    def build_ni9201_gui(self, cfg, frame):
        device_frame = ttk.LabelFrame(frame, text="NI 9201 (voltaje ±10 V, RSE)")
        device_frame.pack(fill="x", pady=5, padx=5)
        
        # Crear una tabla para los canales
        channel_frame = ttk.Frame(device_frame)
        channel_frame.pack(fill="x", pady=5)
        
        # Cabeceras
        ttk.Label(channel_frame, text="Canal", width=8).grid(row=0, column=0, padx=5)
        ttk.Label(channel_frame, text="Activar", width=8).grid(row=0, column=1, padx=5)
        ttk.Label(channel_frame, text="Graficar", width=8).grid(row=0, column=2, padx=5)
        ttk.Label(channel_frame, text="Nombre", width=15).grid(row=0, column=3, padx=5)
        
        # Canales
        for i, ch in enumerate(cfg["AIChannels"]):
            # Canal original
            ch_key = f"{cfg['DeviceName']}/ai{ch}"
            
            ttk.Label(channel_frame, text=f"ai{ch}").grid(row=i+1, column=0, padx=5, pady=2)
            
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(channel_frame, variable=var)
            chk.grid(row=i+1, column=1, padx=5, pady=2)
            
            plot_var = tk.BooleanVar(value=False)
            chk_plot = ttk.Checkbutton(channel_frame, variable=plot_var)
            chk_plot.grid(row=i+1, column=2, padx=5, pady=2)
            
            # Campo para nombre personalizado - MODIFICADO: Formato "9201 ai0"
            name_entry = ttk.Entry(channel_frame, width=15)
            default_name = f"9201 ai{ch}"  # Nuevo formato
            name_entry.insert(0, default_name)
            name_entry.grid(row=i+1, column=3, padx=5, pady=2)
            
            # Inicializar el nombre en el diccionario global
            self.channel_names[ch_key] = default_name
            
            # Función para actualizar el nombre cuando cambia
            def update_name(event, key=ch_key, entry=name_entry):
                self.channel_names[key] = entry.get()
            
            name_entry.bind("<FocusOut>", update_name)  # Actualizar al perder el foco
            name_entry.bind("<Return>", update_name)    # Actualizar al presionar Enter
            
            cfg["channel_vars"][ch] = var
            cfg["channel_settings"][ch] = {
                "var": var, 
                "plot_var": plot_var,
                "name_entry": name_entry
            }

    def build_ni9219_gui(self, cfg, frame):
        device_frame = ttk.LabelFrame(frame, text="NI 9219 (Múltiples modos)")
        device_frame.pack(fill="x", pady=5, padx=5)
        
        # Información sobre la frecuencia dividida
        freq_info_frame = ttk.Frame(device_frame)
        freq_info_frame.pack(fill="x", pady=2)
        
        info_label = ttk.Label(
            freq_info_frame, 
            text="⚠️ Nota: La frecuencia máxima (100 Hz) se divide entre el número de canales activos",
            font=("Arial", 9, "italic"), foreground="darkred"
        )
        info_label.pack(anchor="w", padx=5, pady=2)
        
        # Variable para mostrar la frecuencia efectiva
        cfg["effective_freq_var"] = tk.StringVar(value="Frecuencia efectiva: 100 Hz (1 canal)")
        effective_freq_label = ttk.Label(
            freq_info_frame, 
            textvariable=cfg["effective_freq_var"],
            font=("Arial", 9)
        )
        effective_freq_label.pack(anchor="w", padx=5, pady=2)
        
        # Crear un frame para cada canal
        for ch in cfg["AIChannels"]:
            # Canal original
            ch_key = f"{cfg['DeviceName']}/ai{ch}"
            
            channel_frame = ttk.LabelFrame(device_frame, text=f"Canal ai{ch}")
            channel_frame.pack(fill="x", pady=5, padx=5)
            
            # Fila superior con checkbox de activación y graficar
            top_row = ttk.Frame(channel_frame)
            top_row.pack(fill="x", pady=2)
            
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(top_row, text="Activar", variable=var, style='TCheckbutton')
            chk.pack(side="left", padx=5)
            cfg["channel_vars"][ch] = var
            
            plot_var = tk.BooleanVar(value=False)
            chk_plot = ttk.Checkbutton(top_row, text="Graficar", variable=plot_var, style='TCheckbutton')
            chk_plot.pack(side="left", padx=5)
            
            # Campo para nombre personalizado
            name_label = ttk.Label(top_row, text="Nombre:")
            name_label.pack(side="left", padx=5)
            
            name_entry = ttk.Entry(top_row, width=20)
            default_name = f"9219 ai{ch}"  # Formato modificado
            name_entry.insert(0, default_name)
            name_entry.pack(side="left", padx=5)
            
            # Inicializar el nombre en el diccionario global
            self.channel_names[ch_key] = default_name
            
            # Función para actualizar el nombre cuando cambia
            def update_name(event, key=ch_key, entry=name_entry):
                self.channel_names[key] = entry.get()
            
            # Función para actualizar la frecuencia efectiva cuando se activa/desactiva un canal
            def update_ni9219_frequency(event=None, cf=cfg):
                self.calculate_ni9219_effective_rate(cf)
            
            name_entry.bind("<FocusOut>", update_name)
            name_entry.bind("<Return>", update_name)
            var.trace_add("write", lambda *args, cf=cfg: update_ni9219_frequency(cf=cf))  # Usar trace_add en lugar de config(command)
    
            # Selección de modo
            mode_frame = ttk.Frame(channel_frame)
            mode_frame.pack(fill="x", pady=2)
            ttk.Label(mode_frame, text="Modo:").pack(side="left", padx=5)
            
            mode_var = tk.StringVar(value="Voltage")
            combo_mode = ttk.Combobox(
                mode_frame,
                textvariable=mode_var,
                values=["Voltage", "Current", "2-Wire Resistance",
                        "4-Wire Resistance", "Strain"],
                state="readonly", width=20
            )
            combo_mode.pack(side="left", padx=5)
    
            # Frame para configuraciones específicas
            config_frame = ttk.Frame(channel_frame)
            config_frame.pack(fill="x", pady=2)
            
            # Widgets para modo Voltage
            range_label = ttk.Label(config_frame, text="Rango:")
            range_label.pack(side="left", padx=5)
            
            range_var = tk.StringVar(value="±15 V")
            combo_range = ttk.Combobox(
                config_frame,
                textvariable=range_var,
                values=["±125 mV", "±1 V", "±4 V", "±15 V", "±60 V"],
                state="readonly", width=15
            )
            combo_range.pack(side="left", padx=5)
            
            units_label = ttk.Label(config_frame, text="V")
            units_label.pack(side="left", padx=5)
            
            # Widgets para modo Strain
            bridge_frame = ttk.Frame(channel_frame)
            
            bridge_label = ttk.Label(bridge_frame, text="Puente:")
            bridge_label.pack(side="left", padx=5)
            
            bridge_combo = ttk.Combobox(
                bridge_frame, 
                values=["Cuarto de Puente I", "Cuarto de Puente II", 
                        "Medio de Puente I", "Medio de Puente II",
                        "Puente Completo I", "Puente Completo II", "Puente Completo III"],
                state="readonly", width=15
            )
            bridge_combo.set("Cuarto de Puente I")  # Cambiar a "Cuarto de Puente I"
            bridge_combo.pack(side="left", padx=5)
            
            resist_label = ttk.Label(bridge_frame, text="Resist(Ω):")
            resist_label.pack(side="left", padx=5)
            
            r_entry = ttk.Entry(bridge_frame, width=8)
            r_entry.insert(0, "120")
            r_entry.pack(side="left", padx=5)
            
            gf_label = ttk.Label(bridge_frame, text="Factor Galga:")
            gf_label.pack(side="left", padx=5)
            
            gf_entry = ttk.Entry(bridge_frame, width=6)
            gf_entry.insert(0, "2.0")  # Valor predeterminado para factor de galga
            gf_entry.pack(side="left", padx=5)
            
            zero_btn = ttk.Button(
                bridge_frame,
                text="Cero Galga",
                command=lambda c=ch, cf=cfg: self.zero_gauge_channel_ni9219(cf, c)
            )
            zero_btn.pack(side="left", padx=5)
    
            # Inicialmente ocultar widgets de Strain
            bridge_frame.pack_forget()
    
            # Función para manejar el cambio de modo
            def on_mode_change_9219(event=None, mv=mode_var, cf=config_frame, bf=bridge_frame, rv=range_var, cr=combo_range, ul=units_label, key=ch_key, ne=name_entry):
                sel_mode = mv.get()
                
                # Modificar esta sección para actualizar el nombre correctamente
                current_name = ne.get()
                # Comprobar si el nombre actual es el formato del módulo o comienza con cualquier modo
                if current_name == f"9219 ai{ch}" or current_name.startswith(f"Voltage ai{ch}") or current_name.startswith(f"Current ai{ch}") or current_name.startswith(f"Strain ai{ch}") or current_name.startswith(f"2-Wire Resistance ai{ch}") or current_name.startswith(f"4-Wire Resistance ai{ch}"):
                    # Actualizar al formato del módulo
                    new_name = f"9219 ai{ch}"
                    ne.delete(0, tk.END)
                    ne.insert(0, new_name)
                    self.channel_names[key] = new_name
                
                # Gestionar la visibilidad de los frames según el modo seleccionado
                if sel_mode == "Strain":
                    cf.pack_forget()
                    bf.pack(fill="x", pady=2)
                else:
                    bf.pack_forget()
                    cf.pack(fill="x", pady=2)
                    if sel_mode == "Voltage":
                        cr["values"] = ["±125 mV", "±1 V", "±4 V", "±15 V", "±60 V"]
                        rv.set("±15 V")
                        ul.config(text="V")
                    elif sel_mode == "Current":
                        cr["values"] = ["±25 mA"]
                        rv.set("±25 mA")
                        ul.config(text="mA")
                    elif sel_mode in ["2-Wire Resistance", "4-Wire Resistance"]:
                        cr["values"] = ["0-500 Ω", "0-2000 Ω", "0-10000 Ω"]
                        rv.set("0-2000 Ω")
                        ul.config(text="Ω")
                    else:
                        cr["values"] = ["±10 V"]
                        rv.set("±10 V")
                        ul.config(text="V")
            
            # Bind the event handler to the combobox
            combo_mode.bind("<<ComboboxSelected>>", on_mode_change_9219)
            
            # Almacenar las referencias de los widgets
            cfg["channel_settings"][ch] = {
                "var": var,
                "plot_var": plot_var, 
                "mode_var": mode_var,
                "range_var": range_var,
                "bridge_combo": bridge_combo,
                "r_entry": r_entry,
                "gf_entry": gf_entry,
                "name_entry": name_entry,
                # Almacenar la función para poder llamarla externamente si es necesario
                "on_mode_change": on_mode_change_9219
            }
            
            # Añadir también referencia al combobox para poder acceder a él
            cfg.setdefault("widgets", []).append(combo_mode)
            combo_mode.identifier = f"combo_mode_{ch}"  # Para poder identificarlo
    

    
    def zero_gauge_channel_ni9219(self, cfg, ch):
        """
        Realiza la función de 'Cero Galga' para un canal Strain en NI 9219.
        Usa una frecuencia fija para el cerado, independientemente de la frecuencia de adquisición.
        """
        if cfg["ProductType"] != "NI 9219":
            return
        
        device_name = cfg["DeviceName"]
        
        # Usar una frecuencia fija óptima para el cerado (25 Hz)
        # Este valor debe estar dentro del rango permitido para el NI 9219 (1-100 Hz)
        calibration_rate = 25.0
        
        st = cfg["channel_settings"][ch]
        mode_sel = st["mode_var"].get()
        if mode_sel != "Strain":
            messagebox.showerror("Error", "Cero Galga solo en modo Strain (NI 9219).")
            return
        
        rng = st["bridge_combo"].get()
        try:
            nominal_r = float(st["r_entry"].get())
        except:
            nominal_r = 120.0
            st["r_entry"].delete(0, tk.END)
            st["r_entry"].insert(0, "120")
        
                    # Obtener el factor de galga del campo gf_entry
            try:
                gage_factor = float(st["gf_entry"].get())
            except (ValueError, KeyError):
                gage_factor = 2.0  # Valor predeterminado si hay error
                # Actualizar el campo si está disponible
                if "gf_entry" in st:
                    st["gf_entry"].delete(0, tk.END)
                    st["gf_entry"].insert(0, "2.0")
        
        # Actualizar estado
        self.status_var.set(f"Calibrando Galga en {device_name}/ai{ch}...")
        self.root.update_idletasks()
        
        import nidaqmx
        from nidaqmx.constants import AcquisitionType
        try:
            with nidaqmx.Task() as task:
                ch_phys = f"{device_name}/ai{ch}"
                
                # Obtener más muestras para mejor precisión con la frecuencia fija
                # Recopilamos datos durante aproximadamente 2 segundos
                desired_samples = max(200, int(calibration_rate * 2.0))
                
                # Obtener el factor de galga (default: 2.0)
                gage_factor = 2.0
                
                # CORRECCIÓN: Valores dentro del rango permitido por el hardware
                min_val = -8.0e-3  # Ligeramente mayor que el límite mínimo
                max_val = 18.0e-3  # Ligeramente menor que el límite máximo
                
                # Configurar el canal con parámetros óptimos para estabilidad
                strain_chan = task.ai_channels.add_ai_strain_gage_chan(
                    physical_channel=ch_phys,
                    min_val=min_val,
                    max_val=max_val,
                    units=StrainUnits.STRAIN,
                    strain_config=NI9219_BRIDGE_MAP[rng],
                    voltage_excit_source=ExcitationSource.INTERNAL,
                    voltage_excit_val=2.5,
                    gage_factor=gage_factor,
                    nominal_gage_resistance=nominal_r,
                    poisson_ratio=0.3,
                    lead_wire_resistance=0.0,
                    initial_bridge_voltage=0.0  # Asegurar que no hay voltaje inicial
                )
                
                # Configurar timing con la frecuencia fija para calibración
                task.timing.cfg_samp_clk_timing(
                    rate=calibration_rate,  # Usar frecuencia fija en lugar de sr
                    sample_mode=AcquisitionType.FINITE,
                    samps_per_chan=desired_samples
                )
                    
                # Esperar explícitamente para estabilización antes de adquirir
                task.start()
                time.sleep(0.5)  # 500 ms para mejor estabilización
                
                # Calcular timeout adecuado basado en la frecuencia de calibración
                timeout_seconds = 5.0 + (desired_samples / calibration_rate)
                
                data = task.read(
                    number_of_samples_per_channel=desired_samples,
                    timeout=timeout_seconds
                )
                task.stop()
                
                # Convertir a array y calcular offset con método robusto
                arr = np.array(data, dtype=float)
                
                # Usar filtrado más robusto con percentiles 5-95
                if arr.size > 10:
                    low_p, high_p = np.percentile(arr, [5, 95])
                    filtered_arr = arr[(arr >= low_p) & (arr <= high_p)]
                    if filtered_arr.size > 0:
                        offset_strain = np.mean(filtered_arr)
                    else:
                        offset_strain = np.mean(arr)
                else:
                    offset_strain = np.mean(arr)
                
                # ==== MODIFICACIÓN: Impresión completa para diagnóstico ====
                print(f"\n==== CERADO NI 9219 ====")
                print(f"Canal: {device_name}/ai{ch}")
                print(f"Frecuencia de calibración: {calibration_rate} Hz")
                print(f"Muestras adquiridas: {arr.size}")
                print(f"Datos raw: min={np.min(arr):.6e}, max={np.max(arr):.6e}")
                print(f"Offset calculado: {offset_strain:.6e}V ({offset_strain*1e6:.2f} μstrain)")
                
                # ==== CORRECCIÓN: Guardar el offset de manera coherente ====
                # 1. Crear una clave única para identificar el canal
                key = f"{device_name}/ai{ch}"
                print(f"Clave del canal para almacenar offset: '{key}'")
                
                # 2. Guardar en la configuración del canal actual
                st["offset_val"] = offset_strain
                print(f"Guardado offset en st['offset_val']: {offset_strain:.6e}")
                
                # 3. Guardar también en el diccionario global para mayor seguridad
                if not hasattr(self, 'strain_offsets'):
                    self.strain_offsets = {}
                self.strain_offsets[key] = offset_strain
                print(f"Guardado offset en strain_offsets['{key}']: {offset_strain:.6e}")
                
                # 4. Guardar en la configuración avanzada para usar durante adquisición
                # Aquí guardamos el offset directamente en el parámetro adv_info
                for cfg_device in self.device_configs:
                    if cfg_device["DeviceName"] == device_name and cfg_device["ProductType"] == "NI 9219":
                        if ch in cfg_device["channel_settings"]:
                            ch_settings = cfg_device["channel_settings"][ch]
                            # Guardar el offset
                            ch_settings["offset_val"] = offset_strain
                            print(f"Guardado offset en channel_settings[{ch}]['offset_val']: {offset_strain:.6e}")
                            
                            # NOTA IMPORTANTE: También actualizar el offset en el modo visual
                            if "mode_var" in ch_settings and ch_settings["mode_var"].get() == "Strain":
                                # Esto lo usaremos en la configuración del canal durante la adquisición
                                print(f"Canal configurado en modo Strain, configuración guardada")
                
                # ==== AÑADIDO: Verificación de offset ====
                # Verificar configuración guardada
                is_ok = False
                for cfg_device in self.device_configs:
                    if cfg_device["DeviceName"] == device_name:
                        if ch in cfg_device["channel_settings"]:
                            ch_settings = cfg_device["channel_settings"][ch]
                            if "offset_val" in ch_settings:
                                offset_check = ch_settings["offset_val"]
                                print(f"Verificación: offset guardado = {offset_check:.6e}")
                                is_ok = abs(offset_check - offset_strain) < 1e-10
                
                print(f"Verificación de guardado: {'OK' if is_ok else 'FALLÓ'}")
                print(f"==== FIN CERADO ====\n")
                
                # Restaurar estado
                self.status_var.set("Listo")
                
                # Información más detallada en el mensaje
                messagebox.showinfo(
                    "Cerado Completado",
                    f"Canal: {device_name}/ai{ch}\n\n"
                    f"Frecuencia de calibración: {calibration_rate} Hz\n"
                    f"Offset medido: {offset_strain:.6e} V\n"
                    f"Aprox. {offset_strain*1e6:.1f} μstrain sin procesar\n\n"
                    f"Estadísticas de la señal en reposo:\n"
                    f"Min={np.min(arr):.6e}V, Max={np.max(arr):.6e}V\n"
                    f"Media={np.mean(arr):.6e}V, Desv={np.std(arr):.6e}V"
                )
            
        except Exception as e:
            self.status_var.set("Error")
            messagebox.showerror("Error", f"Error al cerar la galga NI 9219:\n{e}")
            import traceback
            traceback.print_exc()

   
    def build_ni9237_gui(self, cfg, frame):
        """
        Construye la interfaz gráfica para el módulo NI 9237 con configuración 
        independiente de tipo de puente para cada canal.
        """
        device_frame = ttk.LabelFrame(frame, text="NI 9237 (Strain/Bridge)")
        device_frame.pack(fill="x", pady=5, padx=5)
        
        # Nota informativa sobre configuración independiente
        info_label = ttk.Label(
            device_frame, 
            text="Cada canal puede configurarse de forma independiente",
            font=("Arial", 9, "italic"), foreground="darkblue"
        )
        info_label.pack(anchor="w", padx=5, pady=2)
        
        # MODIFICACIÓN: Reemplazar entry por combobox para frecuencias
        rate_frame = ttk.Frame(device_frame)
        rate_frame.pack(fill="x", pady=5, padx=5)
        ttk.Label(rate_frame, text="Frecuencia de muestreo (Hz):").pack(side="left", padx=5)
        
        # Generar lista de frecuencias válidas
        valid_freqs = generate_valid_frequencies("NI 9237")
        
        # Crear combobox en lugar de entry
        rate_combo = ttk.Combobox(
            rate_frame,
            values=valid_freqs,
            state="readonly",
            width=10
        )
        # Seleccionar un valor por defecto (por ejemplo, 10000 Hz)
        default_freq = "10000" if "10000" in valid_freqs else valid_freqs[0]
        rate_combo.set(default_freq)
        rate_combo.pack(side="left", padx=5)
        
        # Guardarlo en la configuración
        cfg["rate_combo"] = rate_combo
        
        # Informar al usuario del rango válido
        if valid_freqs:
            min_freq = valid_freqs[-1]
            max_freq = valid_freqs[0]
            freq_info = ttk.Label(
                rate_frame, 
                text=f"Rango: {min_freq}-{max_freq} Hz",
                font=("Arial", 9, "italic"),
                foreground="darkblue"
            )
            freq_info.pack(side="left", padx=10)
        
        # Grid para los canales
        channel_frame = ttk.Frame(device_frame)
        channel_frame.pack(fill="x", pady=5)
        
        # Cabeceras
        ttk.Label(channel_frame, text="Canal", width=6).grid(row=0, column=0, padx=2)
        ttk.Label(channel_frame, text="Activar", width=8).grid(row=0, column=1, padx=2)
        ttk.Label(channel_frame, text="Graficar", width=8).grid(row=0, column=2, padx=2)
        ttk.Label(channel_frame, text="Tipo Puente", width=14).grid(row=0, column=3, padx=2)
        ttk.Label(channel_frame, text="Exc(V)", width=6).grid(row=0, column=4, padx=2)
        ttk.Label(channel_frame, text="GF", width=6).grid(row=0, column=5, padx=2)
        ttk.Label(channel_frame, text="Res(Ω)", width=6).grid(row=0, column=6, padx=2)
        ttk.Label(channel_frame, text="Offset(mV/V)", width=10).grid(row=0, column=7, padx=2)
        ttk.Label(channel_frame, text="Nombre", width=15).grid(row=0, column=8, padx=2)
        ttk.Label(channel_frame, text="Cero", width=6).grid(row=0, column=9, padx=2)
        
        for i, ch in enumerate(cfg["AIChannels"]):
            # Canal original
            ch_key = f"{cfg['DeviceName']}/ai{ch}"
            
            ttk.Label(channel_frame, text=f"ai{ch}").grid(row=i+1, column=0, padx=2, pady=2)
            
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(channel_frame, variable=var)
            chk.grid(row=i+1, column=1, padx=2, pady=2)
            
            plot_var = tk.BooleanVar(value=False)
            chk_plot = ttk.Checkbutton(channel_frame, variable=plot_var)
            chk_plot.grid(row=i+1, column=2, padx=2, pady=2)
            
            # NUEVO: Selector de tipo de puente por canal
            bridge_var = tk.StringVar(value="Quarter Bridge I")
            bridge_combo = ttk.Combobox(
                channel_frame,
                textvariable=bridge_var,
                values=[
                    "Quarter Bridge I", 
                    "Quarter Bridge II", 
                    "Half Bridge I", 
                    "Half Bridge II", 
                    "Full Bridge I", 
                    "Full Bridge II", 
                    "Full Bridge III"
                ],
                state="readonly", width=14
            )
            bridge_combo.grid(row=i+1, column=3, padx=2, pady=2)
            
            exc_entry = ttk.Entry(channel_frame, width=6)
            exc_entry.insert(0, "2.5")
            exc_entry.grid(row=i+1, column=4, padx=2, pady=2)
            
            gf_entry = ttk.Entry(channel_frame, width=6)
            gf_entry.insert(0, "2.0")
            gf_entry.grid(row=i+1, column=5, padx=2, pady=2)
            
            rn_entry = ttk.Entry(channel_frame, width=6)
            rn_entry.insert(0, "120")
            rn_entry.grid(row=i+1, column=6, padx=2, pady=2)
            
            off_entry = ttk.Entry(channel_frame, width=10)
            off_entry.insert(0, "0")
            off_entry.grid(row=i+1, column=7, padx=2, pady=2)
            
            # Campo para nombre personalizado
            name_entry = ttk.Entry(channel_frame, width=15)
            default_name = f"9237 ai{ch}"
            name_entry.insert(0, default_name)
            name_entry.grid(row=i+1, column=8, padx=2, pady=2)
               
            # Inicializar el nombre en el diccionario global
            self.channel_names[ch_key] = default_name
            
            # Función para actualizar el nombre cuando cambia
            def update_name(event, key=ch_key, entry=name_entry):
                self.channel_names[key] = entry.get()
            
            name_entry.bind("<FocusOut>", update_name)
            name_entry.bind("<Return>", update_name)
            
            zero_btn = ttk.Button(
                channel_frame, text="Cero",
                command=lambda c=ch, cf=cfg: self.zero_gauge_channel_9237(cf, c)
            )
            zero_btn.grid(row=i+1, column=9, padx=2, pady=2)
            
            cfg["channel_vars"][ch] = var
            cfg["channel_settings"][ch] = {
                "var": var,
                "plot_var": plot_var,
                "bridge_var": bridge_var,  # NUEVO: configuración de puente por canal
                "exc_entry": exc_entry,
                "gf_entry": gf_entry,
                "rn_entry": rn_entry,
                "off_entry": off_entry,
                "name_entry": name_entry
            }

    def zero_gauge_channel_9237(self, cfg, ch):
        """
        Realiza la función de 'Cero Galga' para un canal en NI 9237.
        Implementa soporte para configuración independiente de puente por canal,
        filtrado robusto y diagnóstico detallado.
        """
        if cfg["ProductType"] != "NI 9237":
            return
        device_name = cfg["DeviceName"]
        
        try:
            # Obtener la frecuencia configurada por el usuario
            sr = float(cfg["rate_entry"].get())
        except:
            messagebox.showerror("Error", f"Frecuencia inválida en {device_name}")
            return
        
        st = cfg["channel_settings"][ch]
        
        # Actualizar estado en la UI
        self.status_var.set(f"Calibrando Galga en {device_name}/ai{ch}...")
        self.root.update_idletasks()
        
        # MODIFICADO: Obtener configuración de puente DEL CANAL específico
        bridge_mode = st.get("bridge_var", tk.StringVar(value="Quarter Bridge I"))
        if hasattr(bridge_mode, "get"):
            bridge_mode = bridge_mode.get()
        
        # Obtener la configuración del mapa
        # Definición de NI9237_BRIDGE_MAP (asegúrate de tenerlo definido)
        NI9237_BRIDGE_MAP = {
            "Quarter Bridge I": (BridgeConfiguration.QUARTER_BRIDGE, 4.0),
            "Quarter Bridge II": (BridgeConfiguration.QUARTER_BRIDGE, 4.0),
            "Half Bridge I": (BridgeConfiguration.HALF_BRIDGE, 2.0),
            "Half Bridge II": (BridgeConfiguration.HALF_BRIDGE, 2.0),
            "Full Bridge I": (BridgeConfiguration.FULL_BRIDGE, 1.0),
            "Full Bridge II": (BridgeConfiguration.FULL_BRIDGE, 1.0),
            "Full Bridge III": (BridgeConfiguration.FULL_BRIDGE, 1.0)
        }
        
        bc_enum, bridge_factor = NI9237_BRIDGE_MAP.get(bridge_mode, (BridgeConfiguration.QUARTER_BRIDGE, 4.0))
        
        # Obtener valor de excitación
        exc_str = st["exc_entry"].get()
        
        # Clave única para identificar el canal
        ch_phys = f"{device_name}/ai{ch}"
        
        import nidaqmx
        from nidaqmx.constants import AcquisitionType
        try:
            # Crear una tarea dedicada para el cerado
            with nidaqmx.Task() as task:
                # Aumentar el número de muestras para mejor promediado (mínimo 100)
                desired_samples = max(100, int(sr))
                
                # Configurar el canal
                task.ai_channels.add_ai_bridge_chan(
                    physical_channel=ch_phys,
                    min_val=-25.0,
                    max_val=25.0,
                    units=BridgeUnits.MILLIVOLTS_PER_VOLT,
                    bridge_config=bc_enum,  # Usar la configuración del canal específico
                    voltage_excit_source=ExcitationSource.INTERNAL,
                    voltage_excit_val=float(exc_str)
                )
                
                # Configurar timing
                task.timing.cfg_samp_clk_timing(
                    rate=sr,
                    sample_mode=AcquisitionType.FINITE,
                    samps_per_chan=desired_samples
                )
                
                # Iniciar tarea con tiempo de estabilización
                task.start()
                time.sleep(0.2)  # Tiempo de estabilización de 200ms
                
                # Calcular timeout adecuado con margen de seguridad
                timeout_seconds = 5.0 + (desired_samples / sr)
                
                # Leer datos
                data = task.read(
                    number_of_samples_per_channel=desired_samples,
                    timeout=timeout_seconds
                )
                task.stop()
            
            # Convertir datos a array para procesamiento
            arr = np.array(data, dtype=float)
            
            # Implementar filtrado robusto por percentiles (eliminar outliers)
            if arr.size > 10:
                # Usar percentiles 5-95 para eliminar valores extremos
                low_p, high_p = np.percentile(arr, [5, 95])
                filtered_arr = arr[(arr >= low_p) & (arr <= high_p)]
                if filtered_arr.size > 0:
                    offset_mean = np.mean(filtered_arr)
                else:
                    offset_mean = np.mean(arr)  # Fallback
            else:
                offset_mean = np.mean(arr)
            
            # Información de diagnóstico
            print(f"\n==== CERADO NI 9237 ====")
            print(f"Canal: {ch_phys}")
            print(f"Configuración: {bridge_mode} (factor: {bridge_factor})")
            print(f"Excitación: {exc_str}V")
            print(f"Frecuencia: {sr} Hz")
            print(f"Muestras adquiridas: {arr.size}")
            print(f"Estadísticas datos raw: min={np.min(arr):.6f}, max={np.max(arr):.6f}, mean={np.mean(arr):.6f}")
            if 'filtered_arr' in locals():
                print(f"Datos después de filtrado: {filtered_arr.size} muestras")
                print(f"Estadísticas filtradas: min={np.min(filtered_arr):.6f}, max={np.max(filtered_arr):.6f}")
            print(f"Offset calculado (mV/V): {offset_mean:.6f}")
            
            # Almacenar offset en múltiples ubicaciones para mayor robustez
            
            # 1. En el objeto de configuración del canal
            st["off_entry"].delete(0, tk.END)
            st["off_entry"].insert(0, f"{offset_mean:.4f}")
            
            # 2. Almacenar internamente en la configuración del canal
            st["offset_val"] = offset_mean
            
            # 3. En diccionario global para mayor disponibilidad
            if not hasattr(self, 'bridge_offsets'):
                self.bridge_offsets = {}
            self.bridge_offsets[ch_phys] = offset_mean
            
            # 4. Guardar también la configuración de puente para uso posterior
            if not hasattr(self, 'bridge_configs'):
                self.bridge_configs = {}
            self.bridge_configs[ch_phys] = {
                'mode': bridge_mode,
                'factor': bridge_factor
            }
            
            # Restaurar estado en la UI
            self.status_var.set("Listo")
            
            # Mostrar información detallada al usuario
            messagebox.showinfo(
                "Cero Galga",
                f"Offset (mV/V) en {device_name} ai{ch}:\n\n"
                f"Configuración: {bridge_mode}\n"
                f"Valor: {offset_mean:.6f} mV/V\n"
                f"Muestras procesadas: {arr.size}\n"
                f"Rango: {np.min(arr):.6f} a {np.max(arr):.6f} mV/V\n\n"
                f"La galga ha sido tarada correctamente."
            )
            
            print(f"==== FIN CERADO 9237 ====\n")
            
        except Exception as e:
            self.status_var.set("Error")
            messagebox.showerror(
                "Error",
                f"Error al cerar la galga en {device_name} ai{ch}:\n{e}"
            )
            import traceback
            traceback.print_exc()

    def build_ni9211_gui(self, cfg, frame):
        device_frame = ttk.LabelFrame(frame, text="NI 9211 (Termopares)")
        device_frame.pack(fill="x", pady=5, padx=5)
        
        # Configuración de termopares
        tc_frame = ttk.Frame(device_frame)
        tc_frame.pack(fill="x", pady=5)
        
        ttk.Label(tc_frame, text="Tipo termopar:").pack(side="left", padx=5)
        cfg["tc_var"] = tk.StringVar(value="T")
        combo_tc = ttk.Combobox(
            tc_frame,
            textvariable=cfg["tc_var"],
            values=["J", "K", "T", "E", "N", "R", "S", "B"],
            state="readonly",
            width=5
        )
        combo_tc.pack(side="left", padx=5)
        
        # Añadir una etiqueta para mostrar el rango de temperatura
        cfg["tc_range_var"] = tk.StringVar(value="Rango: -200.0°C a 400.0°C")
        ttk.Label(tc_frame, textvariable=cfg["tc_range_var"]).pack(side="left", padx=10)
        
        # Función para actualizar el rango cuando cambia el tipo de termopar
        def update_tc_range(event=None):
            tc_type = cfg["tc_var"].get()
            # Rangos de temperatura para cada tipo de termopar
            tc_ranges = {
                "J": (-210.0, 1200.0),
                "K": (-200.0, 1372.0),
                "T": (-200.0, 400.0),
                "E": (-200.0, 1000.0),
                "N": (-200.0, 1300.0),
                "R": (-50.0, 1768.0),
                "S": (-50.0, 1768.0),
                "B": (250.0, 1820.0)
            }
            min_val, max_val = tc_ranges.get(tc_type, (-200.0, 400.0))
            cfg["tc_range_var"].set(f"Rango: {min_val}°C a {max_val}°C")
        
        # Asociar el evento de selección con la función
        combo_tc.bind("<<ComboboxSelected>>", update_tc_range)
        # Inicializar el rango
        update_tc_range()
        
        
        # Grid para los canales
        channel_frame = ttk.Frame(device_frame)
        channel_frame.pack(fill="x", pady=5)
        
        # Cabeceras
        ttk.Label(channel_frame, text="Canal", width=8).grid(row=0, column=0, padx=5)
        ttk.Label(channel_frame, text="Activar", width=8).grid(row=0, column=1, padx=5)
        ttk.Label(channel_frame, text="Graficar", width=8).grid(row=0, column=2, padx=5)
        ttk.Label(channel_frame, text="Nombre", width=15).grid(row=0, column=3, padx=5)
        
        for i, ch in enumerate(cfg["AIChannels"]):
            # Canal original
            ch_key = f"{cfg['DeviceName']}/ai{ch}"
            
            ttk.Label(channel_frame, text=f"ai{ch}").grid(row=i+1, column=0, padx=5, pady=2)
            
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(channel_frame, variable=var)
            chk.grid(row=i+1, column=1, padx=5, pady=2)
            
            plot_var = tk.BooleanVar(value=False)
            chk_plot = ttk.Checkbutton(channel_frame, variable=plot_var)
            chk_plot.grid(row=i+1, column=2, padx=5, pady=2)
            
            # Campo para nombre personalizado
            name_entry = ttk.Entry(channel_frame, width=15)
            default_name = f"9211 ai{ch}"  # Formato modificado
            name_entry.insert(0, default_name)
            name_entry.grid(row=i+1, column=3, padx=5, pady=2)
            
            # Inicializar el nombre en el diccionario global
            self.channel_names[ch_key] = default_name
            
            # Función para actualizar el nombre cuando cambia
            def update_name(event, key=ch_key, entry=name_entry):
                self.channel_names[key] = entry.get()
                
            name_entry.bind("<FocusOut>", update_name)
            name_entry.bind("<Return>", update_name)
            
            cfg["channel_vars"][ch] = var
            cfg["channel_settings"][ch] = {
                "var": var,
                "plot_var": plot_var,
                "name_entry": name_entry
            }
    

    
    def build_ni9234_gui(self, cfg, frame):
        device_frame = ttk.LabelFrame(frame, text="NI 9234 (IEPE/DC/AC)")
        device_frame.pack(fill="x", pady=5, padx=5)
        
        # Configuración IEPE
        iepe_frame = ttk.LabelFrame(device_frame, text="Configuración IEPE")
        iepe_frame.pack(fill="x", pady=5)
        
        cfg["iepe_var"] = tk.BooleanVar(value=True)
        chk_iepe = ttk.Checkbutton(iepe_frame, text="Activar IEPE", variable=cfg["iepe_var"])
        chk_iepe.pack(anchor="w", padx=5, pady=2)
        
        sens_frame = ttk.Frame(iepe_frame)
        sens_frame.pack(fill="x", pady=2)
        ttk.Label(sens_frame, text="Sensibilidad (mV/g):").pack(side="left", padx=5)
        sens_entry = ttk.Entry(sens_frame, width=10)
        sens_entry.insert(0, "100.0")
        sens_entry.pack(side="left", padx=5)
        cfg["sens_entry"] = sens_entry
        
        curr_frame = ttk.Frame(iepe_frame)
        curr_frame.pack(fill="x", pady=2)
        ttk.Label(curr_frame, text="Corriente IEPE (A):").pack(side="left", padx=5)
        iepe_curr_entry = ttk.Entry(curr_frame, width=10)
        iepe_curr_entry.insert(0, "0.004")
        iepe_curr_entry.pack(side="left", padx=5)
        cfg["iepe_curr_entry"] = iepe_curr_entry
        
        # MODIFICACIÓN: Reemplazar entry por combobox para frecuencias
        rate_frame = ttk.Frame(device_frame)
        rate_frame.pack(fill="x", pady=5, padx=5)
        ttk.Label(rate_frame, text="Frecuencia de muestreo (Hz):").pack(side="left", padx=5)
        
        # Generar lista de frecuencias válidas
        valid_freqs = generate_valid_frequencies("NI 9234")
        
        # Crear combobox en lugar de entry
        rate_combo = ttk.Combobox(
            rate_frame,
            values=valid_freqs,
            state="readonly",
            width=10
        )
        # Seleccionar un valor por defecto (por ejemplo, 25600 Hz)
        default_freq = "25600" if "25600" in valid_freqs else valid_freqs[0]
        rate_combo.set(default_freq)
        rate_combo.pack(side="left", padx=5)
        
        # Guardarlo en la configuración
        cfg["rate_combo"] = rate_combo
        
        # Informar al usuario del rango válido
        if valid_freqs:
            min_freq = valid_freqs[-1]
            max_freq = valid_freqs[0]
            freq_info = ttk.Label(
                rate_frame, 
                text=f"Rango: {min_freq}-{max_freq} Hz",
                font=("Arial", 9, "italic"),
                foreground="darkblue"
            )
            freq_info.pack(side="left", padx=10)
        
        # Grid para los canales
        channel_frame = ttk.Frame(device_frame)
        channel_frame.pack(fill="x", pady=5)
        
        # Cabeceras
        ttk.Label(channel_frame, text="Canal", width=8).grid(row=0, column=0, padx=5)
        ttk.Label(channel_frame, text="Activar", width=8).grid(row=0, column=1, padx=5)
        ttk.Label(channel_frame, text="Graficar", width=8).grid(row=0, column=2, padx=5)
        ttk.Label(channel_frame, text="Nombre", width=15).grid(row=0, column=3, padx=5)
        
        for i, ch in enumerate(cfg["AIChannels"]):
            # Canal original
            ch_key = f"{cfg['DeviceName']}/ai{ch}"
            
            ttk.Label(channel_frame, text=f"ai{ch}").grid(row=i+1, column=0, padx=5, pady=2)
            
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(channel_frame, variable=var)
            chk.grid(row=i+1, column=1, padx=5, pady=2)
            
            plot_var = tk.BooleanVar(value=False)
            chk_plot = ttk.Checkbutton(channel_frame, variable=plot_var)
            chk_plot.grid(row=i+1, column=2, padx=5, pady=2)
            
            # Campo para nombre personalizado
            name_entry = ttk.Entry(channel_frame, width=15)
            default_name = f"9234 ai{ch}"  # Formato modificado
            name_entry.insert(0, default_name)
            name_entry.grid(row=i+1, column=3, padx=5, pady=2)
            
            # Inicializar el nombre en el diccionario global
            self.channel_names[ch_key] = default_name
            
            # Función para actualizar el nombre cuando cambia
            def update_name(event, key=ch_key, entry=name_entry):
                self.channel_names[key] = entry.get()
            
            name_entry.bind("<FocusOut>", update_name)
            name_entry.bind("<Return>", update_name)
            
            cfg["channel_vars"][ch] = var
            cfg["channel_settings"][ch] = {
                "var": var,
                "plot_var": plot_var,
                "name_entry": name_entry
                }    
    def load_device_configs(self):
        """
        Recorre los dispositivos del sistema. Si el product_type está en la lista
        de soportados, crea un frame con su configuración y muestra el rango
        [min, max] de frecuencia.
        """
        supported_products = ["NI 9201", "NI 9219", "NI 9237", "NI 9211", "NI 9234"]
        for dev in self.system.devices:
            if dev.product_type in supported_products:
                cfg = {
                    "DeviceName": dev.name,
                    "ProductType": dev.product_type,
                    "AIChannels": list(range(len(dev.ai_physical_chans)))
                }
                self.device_configs.append(cfg)
    
                # Crear una pestaña para este dispositivo
                frame = ttk.Frame(self.notebook)
                self.frames[cfg["DeviceName"]] = frame
                self.notebook.add(frame, text=f"{cfg['ProductType']} - {cfg['DeviceName']}")
    
                cfg["channel_vars"] = {}
                cfg["channel_settings"] = {}
    
                # Rango de frecuencia
                freq_limits = MODULE_FREQ_LIMITS.get(cfg["ProductType"], {"min": 1, "max": 1e6})
                min_freq = freq_limits["min"]
                max_freq = freq_limits["max"]
    
                # Para NI 9234 y NI 9237 no creamos el campo de frecuencia aquí, ya que
                # lo hacemos en sus funciones específicas
                if cfg["ProductType"] not in ["NI 9234", "NI 9237"]:
                    rate_frame = ttk.Frame(frame)
                    rate_frame.pack(anchor="w", pady=5)
                    ttk.Label(
                        rate_frame,
                        text=f"Frecuencia deseada (Hz) [Rango: {min_freq}-{max_freq}]:"
                    ).pack(side="left")
                    rate_entry = ttk.Entry(rate_frame, width=10)
                    rate_entry.insert(0, str(min_freq))  # valor inicial = mínimo
                    rate_entry.pack(side="left", padx=5)
                    cfg["rate_entry"] = rate_entry
    
                # Construir la GUI específica para cada módulo
                if cfg["ProductType"] == "NI 9219":
                    self.build_ni9219_gui(cfg, frame)
                elif cfg["ProductType"] == "NI 9237":
                    self.build_ni9237_gui(cfg, frame)
                elif cfg["ProductType"] == "NI 9211":
                    self.build_ni9211_gui(cfg, frame)
                elif cfg["ProductType"] == "NI 9234":
                    self.build_ni9234_gui(cfg, frame)
                else:
                    self.build_ni9201_gui(cfg, frame)
    
        # Si no hay dispositivos soportados
        if not self.device_configs:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="Sin dispositivos")
            ttk.Label(frame, text="No se encontraron dispositivos NI soportados.").pack(pady=20)   
    
    # Método para detener la adquisición, ahora con manejo de streaming independiente del modo
    def stop_acquisition(self):
        """
        Detiene la adquisición (si está en marcha) activando self.stop_event.
        Funciona tanto para modo Continuous como para interrumpir una adquisición Finite.
        """
        print("Solicitando detener la adquisición...")
        self.stop_event.set()
        self.status_var.set("Deteniendo adquisición...")
        
        # Restaurar texto del botón de detener
        self.btn_stop.config(text="Detener Adquisición")
        
        # Actualizar el estado de adquisición
        with self.data_lock:
            self.acquisition_status["message"] = "Deteniendo adquisición..."
        
        # Si streaming está activo, mostrar mensaje de que se están finalizando archivos
        if hasattr(self, 'streaming_active') and self.streaming_active:
            messagebox.showinfo(
                "Grabación Continua", 
                "La adquisición se ha detenido. Finalizando archivos de grabación continua...\n"
                "Esto puede tomar unos momentos si hay muchos datos pendientes."
            )
        else:
            messagebox.showinfo("Acquisition", "Se ha solicitado detener la adquisición.")
        
        # Si estamos en modo Finite, ocultar el botón de detener cuando se complete
        if self.acq_mode.get() == "Finite":
            # Verificamos si la adquisición ya terminó
            if not (self.acquisition_thread and self.acquisition_thread.is_alive()):
                self.btn_stop.pack_forget()
    
    def calculate_ni9219_effective_rate(self, cfg):
        """
        Calcula la frecuencia efectiva por canal para el NI 9219 basada en el número
        de canales activos. El NI 9219 divide su frecuencia máxima entre los canales activos.
        
        Args:
            cfg: Configuración del dispositivo NI 9219
            
        Returns:
            tuple: (frecuencia_efectiva, num_canales_activos)
        """
        if cfg["ProductType"] != "NI 9219":
            return None, 0
            
        active_channels = [ch for ch in cfg["AIChannels"] 
                         if cfg["channel_vars"].get(ch, tk.BooleanVar()).get()]
        num_active = len(active_channels)
        
        if num_active == 0:
            return 100.0, 0  # Valor máximo por defecto si no hay canales activos
            
        # Frecuencia máxima dividida por el número de canales activos
        effective_max = MODULE_FREQ_LIMITS["NI 9219"]["max"] / num_active
        
        # Actualizar la etiqueta informativa si existe
        if "effective_freq_var" in cfg:
            cfg["effective_freq_var"].set(
                f"Frecuencia efectiva: {effective_max:.2f} Hz ({num_active} {'canal' if num_active == 1 else 'canales'})")
        
        return effective_max, num_active
        
    def update_acq_param(self, event=None):
        """Actualiza el modo de adquisición y elementos visibles de la interfaz."""
        mode = self.acq_mode.get()
        
        # Ocultar todos los elementos primero
        self.param_frame.pack_forget()
        self.progress_frame.pack_forget()
        self.btn_stop.pack_forget()
    
        # Mostrar elementos según el modo
        if mode == "Finite":
            # En modo Finite, mostrar campo de tiempo y barra de progreso
            self.param_frame.pack(pady=5)
            self.progress_frame.pack(pady=5)
        elif mode == "Continuous":
            # En modo Continuous, mostrar botón de detener
            self.btn_stop.pack(pady=5)
            
        # Actualizar también el panel de ajustes
        self.update_settings()
        
    def close_app(self):
        """
        Método para cerrar correctamente la aplicación y todas sus ventanas.
        """
        # Si hay una adquisición en curso, detenerla
        if self.acquisition_thread is not None and self.acquisition_thread.is_alive():
            self.stop_event.set()
            self.acquisition_thread.join(timeout=1.0)
        
        # Detener streaming si está activo
        if hasattr(self, 'streaming_status') and self.streaming_status.get("active", False):
            self.stop_streaming_writer()
        
        # Limpiar explícitamente referencias a variables Tkinter
        with self.data_lock:
            self.plot_buffers.clear()
            self.results.clear()
        
        # Cancelar cualquier timer activo
        if self.update_timer is not None:
            self.root.after_cancel(self.update_timer)
            self.update_timer = None
        
        # Cancelar monitoreo de espacio en disco
        if hasattr(self, 'disk_space_timer') and self.disk_space_timer is not None:
            self.root.after_cancel(self.disk_space_timer)
            self.disk_space_timer = None
        
        # Cerrar la ventana de gráficos si está abierta
        if self.plot_window is not None and self.plot_window.winfo_exists():
            self.plot_window.destroy()
        
        # Cerrar la ventana principal
        self.root.destroy()

    def clear_all_fields(self):
        """
        Limpia todos los campos de configuración y restablece los valores por defecto.
        """
        # Preguntar confirmación
        confirm = messagebox.askyesno("Limpiar configuración", 
                                    "¿Está seguro de limpiar toda la configuración?\nEsta acción no se puede deshacer.")
        if not confirm:
            return
            
        try:
            # Restaurar valores por defecto para cada dispositivo
            for cfg in self.device_configs:
                # Restablecer frecuencia
                prod_type = cfg["ProductType"]
                freq_limits = MODULE_FREQ_LIMITS.get(prod_type, {"min": 1, "max": 1e6})
                min_freq = freq_limits["min"]
                cfg["rate_entry"].delete(0, tk.END)
                cfg["rate_entry"].insert(0, str(min_freq))
                
                # Limpiar canales
                for ch in cfg["AIChannels"]:
                    # Desmarcar checkbox de activación y visualización
                    if ch in cfg["channel_vars"]:
                        cfg["channel_vars"][ch].set(False)
                    
                    if ch in cfg["channel_settings"]:
                        ch_settings = cfg["channel_settings"][ch]
                        
                        # Desmarcar visualización
                        if "plot_var" in ch_settings:
                            ch_settings["plot_var"].set(False)
                        
                        # Restablecer nombre
                        if "name_entry" in ch_settings:
                            # MODIFICADO: Usar solo el número del módulo y el canal
                            module_num = prod_type.split()[1]  # Obtiene "9201", "9219", etc.
                            default_name = f"{module_num} ai{ch}"
                            
                            ch_settings["name_entry"].delete(0, tk.END)
                            ch_settings["name_entry"].insert(0, default_name)
                            
                            # Actualizar en el diccionario global de nombres
                            ch_key = f"{cfg['DeviceName']}/ai{ch}"
                            self.channel_names[ch_key] = default_name
                        
                        # Restablecer valores específicos según el tipo de módulo
                        if prod_type == "NI 9237":
                            if "exc_entry" in ch_settings:
                                ch_settings["exc_entry"].delete(0, tk.END)
                                ch_settings["exc_entry"].insert(0, "2.5")
                            if "gf_entry" in ch_settings:
                                ch_settings["gf_entry"].delete(0, tk.END)
                                ch_settings["gf_entry"].insert(0, "2.0")
                            if "rn_entry" in ch_settings:
                                ch_settings["rn_entry"].delete(0, tk.END)
                                ch_settings["rn_entry"].insert(0, "120")
                            if "off_entry" in ch_settings:
                                ch_settings["off_entry"].delete(0, tk.END)
                                ch_settings["off_entry"].insert(0, "0")
                        
                        elif prod_type == "NI 9219":
                            if "mode_var" in ch_settings:
                                ch_settings["mode_var"].set("Voltage")
                            if "range_var" in ch_settings:
                                ch_settings["range_var"].set("±15 V")
                            if "bridge_combo" in ch_settings:
                                ch_settings["bridge_combo"].set("Cuarto de Puente")
                            if "r_entry" in ch_settings:
                                ch_settings["r_entry"].delete(0, tk.END)
                                ch_settings["r_entry"].insert(0, "120")
                                
                # Configuraciones específicas por dispositivo
                if prod_type == "NI 9219":
                    if "effective_freq_var" in cfg:
                        cfg["effective_freq_var"].set("Frecuencia efectiva: 100 Hz (1 canal)")
                        
                elif prod_type == "NI 9237":
                    if "bridge_mode_var" in cfg:
                        cfg["bridge_mode_var"].set("Completo")
                        
                elif prod_type == "NI 9211":
                    if "tc_var" in cfg:
                        cfg["tc_var"].set("T")
                        
                elif prod_type == "NI 9234":
                    if "iepe_var" in cfg:
                        cfg["iepe_var"].set(True)
                    if "sens_entry" in cfg:
                        cfg["sens_entry"].delete(0, tk.END)
                        cfg["sens_entry"].insert(0, "100.0")
                    if "iepe_curr_entry" in cfg:
                        cfg["iepe_curr_entry"].delete(0, tk.END)
                        cfg["iepe_curr_entry"].insert(0, "0.004")
                
            # Restablecer tiempo de adquisición
            self.acq_param.delete(0, tk.END)
            self.acq_param.insert(0, "10")
            
            # Modo de adquisición y formato de exportación
            self.acq_mode.set("Finite")
            self.export_format.set("xlsx")
            
            # Restablecer configuración de streaming
            if hasattr(self, 'streaming_enabled'):
                self.streaming_enabled.set(True)
                self.streaming_interval.set(60)
                
            # Actualizar elementos visibles según modo
            self.update_acq_param()
            
            # Limpiar resultados y buffers
            with self.data_lock:
                self.results.clear()
                self.plot_buffers.clear()
            
            # Actualizar estado
            self.status_var.set("Configuración limpiada")
            
            # Actualizar panel de ajustes
            self.update_settings()
            
            messagebox.showinfo("Limpiar", "Se ha restablecido la configuración por defecto.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al limpiar configuración: {e}")

    def save_setup(self):
        """
        Guarda la configuración actual en un archivo.
        """
        # Obtener ruta de archivo
        filename = filedialog.asksaveasfilename(
            defaultextension=".nistp",
            filetypes=[("NI Setup files", "*.nistp"), ("All files", "*.*")]
        )
        if not filename:
            return
            
        try:
            # Crear diccionario con la configuración
            setup_data = {
                "acq_mode": self.acq_mode.get(),
                "acq_time": self.acq_param.get(),
                "export_format": self.export_format.get(),
                "devices": []
            }
            
            # Guardar configuración de streaming si existe
            if hasattr(self, 'streaming_enabled'):
                setup_data["streaming"] = {
                    "enabled": self.streaming_enabled.get(),
                    "interval": self.streaming_interval.get(),
                    "path": self.streaming_path if hasattr(self, 'streaming_path') else None
                }
            
            # Guardar configuración de cada dispositivo
            for cfg in self.device_configs:
                device_config = {
                    "DeviceName": cfg["DeviceName"],
                    "ProductType": cfg["ProductType"],
                    "rate": cfg["rate_entry"].get(),
                    "channels": {}
                }
                
                # Guardar configuraciones específicas por tipo de dispositivo
                if cfg["ProductType"] == "NI 9219":
                    if "effective_freq_var" in cfg:
                        device_config["effective_freq"] = cfg["effective_freq_var"].get()
                
                elif cfg["ProductType"] == "NI 9237":
                    if "bridge_mode_var" in cfg and hasattr(cfg["bridge_mode_var"], "get"):
                        device_config["bridge_mode"] = cfg["bridge_mode_var"].get()
                
                elif cfg["ProductType"] == "NI 9211":
                    if "tc_var" in cfg and hasattr(cfg["tc_var"], "get"):
                        device_config["tc_type"] = cfg["tc_var"].get()
                
                elif cfg["ProductType"] == "NI 9234":
                    if "iepe_var" in cfg and hasattr(cfg["iepe_var"], "get"):
                        device_config["iepe_enabled"] = cfg["iepe_var"].get()
                    if "sens_entry" in cfg:
                        device_config["sensitivity"] = cfg["sens_entry"].get()
                    if "iepe_curr_entry" in cfg:
                        device_config["iepe_current"] = cfg["iepe_curr_entry"].get()
                
                # Guardar configuración de cada canal
                for ch in cfg["AIChannels"]:
                    if ch in cfg["channel_settings"]:
                        ch_settings = cfg["channel_settings"][ch]
                        ch_config = {
                            "enabled": cfg["channel_vars"][ch].get() if ch in cfg["channel_vars"] else False,
                            "plot": ch_settings["plot_var"].get() if "plot_var" in ch_settings else False
                        }
                        
                        # Guardar nombre personalizado
                        if "name_entry" in ch_settings:
                            ch_config["name"] = ch_settings["name_entry"].get()
                        
                        # Guardar configuraciones específicas según el tipo de módulo
                        if cfg["ProductType"] == "NI 9237":
                            if "exc_entry" in ch_settings:
                                ch_config["excitation"] = ch_settings["exc_entry"].get()
                            if "gf_entry" in ch_settings:
                                ch_config["gage_factor"] = ch_settings["gf_entry"].get()
                            if "rn_entry" in ch_settings:
                                ch_config["resistance"] = ch_settings["rn_entry"].get()
                            if "off_entry" in ch_settings:
                                ch_config["offset"] = ch_settings["off_entry"].get()
                        
                        elif cfg["ProductType"] == "NI 9219":
                            if "mode_var" in ch_settings and hasattr(ch_settings["mode_var"], "get"):
                                ch_config["mode"] = ch_settings["mode_var"].get()
                            if "range_var" in ch_settings and hasattr(ch_settings["range_var"], "get"):
                                ch_config["range"] = ch_settings["range_var"].get()
                            if "bridge_combo" in ch_settings and hasattr(ch_settings["bridge_combo"], "get"):
                                ch_config["bridge_type"] = ch_settings["bridge_combo"].get()
                            if "r_entry" in ch_settings:
                                ch_config["resistance"] = ch_settings["r_entry"].get()
                        
                        device_config["channels"][ch] = ch_config
                
                setup_data["devices"].append(device_config)
            
            # Guardar el diccionario en el archivo
            with open(filename, 'wb') as f:
                pickle.dump(setup_data, f)
                
            self.status_var.set(f"Configuración guardada en {filename}")
            messagebox.showinfo("Guardar Setup", f"Configuración guardada exitosamente en {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar configuración: {e}")

    def load_setup(self):
        """
        Carga una configuración desde un archivo.
        """
        # Obtener ruta de archivo
        filename = filedialog.askopenfilename(
            filetypes=[("NI Setup files", "*.nistp"), ("All files", "*.*")]
        )
        if not filename:
            return
            
        try:
            # Preguntar confirmación
            confirm = messagebox.askyesno("Cargar configuración", 
                                         "La configuración actual se perderá. ¿Continuar?")
            if not confirm:
                return
                
            # Leer configuración del archivo
            with open(filename, 'rb') as f:
                setup_data = pickle.load(f)
            
            # Aplicar configuraciones generales
            if "acq_mode" in setup_data:
                self.acq_mode.set(setup_data["acq_mode"])
            
            if "acq_time" in setup_data:
                self.acq_param.delete(0, tk.END)
                self.acq_param.insert(0, setup_data["acq_time"])
            
            if "export_format" in setup_data:
                self.export_format.set(setup_data["export_format"])
            
            # Cargar configuración de streaming si existe
            if "streaming" in setup_data and hasattr(self, 'streaming_enabled'):
                streaming_config = setup_data["streaming"]
                self.streaming_enabled.set(streaming_config.get("enabled", True))
                self.streaming_interval.set(streaming_config.get("interval", 60))
                if streaming_config.get("path") and os.path.exists(streaming_config["path"]):
                    self.streaming_path = streaming_config["path"]
                    self.streaming_path_var.set(f"Carpeta: {self.streaming_path}")
                    self.update_disk_space_info()
                
            # Primero, restablezca todo
            self.clear_all_fields()
            
            # Aplicar configuración por dispositivo
            for dev_config in setup_data.get("devices", []):
                # Buscar el dispositivo correspondiente
                dev_name = dev_config.get("DeviceName")
                matching_configs = [cfg for cfg in self.device_configs if cfg["DeviceName"] == dev_name]
                
                if matching_configs:
                    cfg = matching_configs[0]
                    
                    # Aplicar frecuencia
                    if "rate" in dev_config:
                        cfg["rate_entry"].delete(0, tk.END)
                        cfg["rate_entry"].insert(0, dev_config["rate"])
                    
                    # Aplicar configuraciones específicas por tipo de dispositivo
                    if cfg["ProductType"] == "NI 9237":
                        if "bridge_mode" in dev_config and "bridge_mode_var" in cfg:
                            cfg["bridge_mode_var"].set(dev_config["bridge_mode"])
                    
                    elif cfg["ProductType"] == "NI 9211":
                        if "tc_type" in dev_config and "tc_var" in cfg:
                            cfg["tc_var"].set(dev_config["tc_type"])
                    
                    elif cfg["ProductType"] == "NI 9234":
                        if "iepe_enabled" in dev_config and "iepe_var" in cfg:
                            cfg["iepe_var"].set(dev_config["iepe_enabled"])
                        if "sensitivity" in dev_config and "sens_entry" in cfg:
                            cfg["sens_entry"].delete(0, tk.END)
                            cfg["sens_entry"].insert(0, dev_config["sensitivity"])
                        if "iepe_current" in dev_config and "iepe_curr_entry" in cfg:
                            cfg["iepe_curr_entry"].delete(0, tk.END)
                            cfg["iepe_curr_entry"].insert(0, dev_config["iepe_current"])
                    
                    # Aplicar configuración por canal
                    for ch_str, ch_config in dev_config.get("channels", {}).items():
                        try:
                            ch = int(ch_str)
                            if ch in cfg["channel_vars"] and "enabled" in ch_config:
                                cfg["channel_vars"][ch].set(ch_config["enabled"])
                            
                            if ch in cfg["channel_settings"]:
                                ch_settings = cfg["channel_settings"][ch]
                                
                                # Aplicar visualización
                                if "plot" in ch_config and "plot_var" in ch_settings:
                                    ch_settings["plot_var"].set(ch_config["plot"])
                                
                                # Aplicar nombre personalizado
                                if "name" in ch_config and "name_entry" in ch_settings:
                                    ch_settings["name_entry"].delete(0, tk.END)
                                    ch_settings["name_entry"].insert(0, ch_config["name"])
                                    
                                    # Actualizar en el diccionario global de nombres
                                    ch_key = f"{cfg['DeviceName']}/ai{ch}"
                                    self.channel_names[ch_key] = ch_config["name"]
                                
                                # Aplicar configuraciones específicas según el tipo de módulo
                                if cfg["ProductType"] == "NI 9237":
                                    if "excitation" in ch_config and "exc_entry" in ch_settings:
                                        ch_settings["exc_entry"].delete(0, tk.END)
                                        ch_settings["exc_entry"].insert(0, ch_config["excitation"])
                                    if "gage_factor" in ch_config and "gf_entry" in ch_settings:
                                        ch_settings["gf_entry"].delete(0, tk.END)
                                        ch_settings["gf_entry"].insert(0, ch_config["gage_factor"])
                                    if "resistance" in ch_config and "rn_entry" in ch_settings:
                                        ch_settings["rn_entry"].delete(0, tk.END)
                                        ch_settings["rn_entry"].insert(0, ch_config["resistance"])
                                    if "offset" in ch_config and "off_entry" in ch_settings:
                                        ch_settings["off_entry"].delete(0, tk.END)
                                        ch_settings["off_entry"].insert(0, ch_config["offset"])
                                
                                elif cfg["ProductType"] == "NI 9219":
                                    if "mode" in ch_config and "mode_var" in ch_settings:
                                        ch_settings["mode_var"].set(ch_config["mode"])
                                        
                                        # Forzar un evento para actualizar la interfaz
                                        # (muestra/oculta los campos según el modo)
                                        for widget in cfg.get("widgets", []):
                                            if hasattr(widget, "identifier") and widget.identifier == f"combo_mode_{ch}":
                                                widget.event_generate("<<ComboboxSelected>>")
                                                break
                                    
                                    if "range" in ch_config and "range_var" in ch_settings:
                                        ch_settings["range_var"].set(ch_config["range"])
                                    
                                    if "bridge_type" in ch_config and "bridge_combo" in ch_settings:
                                        ch_settings["bridge_combo"].set(ch_config["bridge_type"])
                                    
                                    if "resistance" in ch_config and "r_entry" in ch_settings:
                                        ch_settings["r_entry"].delete(0, tk.END)
                                        ch_settings["r_entry"].insert(0, ch_config["resistance"])
                                    
                        except (ValueError, KeyError) as e:
                            print(f"Error al cargar configuración del canal {ch_str}: {e}")
                            continue
            
            # Actualizar elementos visibles según modo
            self.update_acq_param()
            
            # Actualizar panel de ajustes
            self.update_settings()
            
            # Verificar NI 9219 para frecuencia efectiva
            for cfg in self.device_configs:
                if cfg["ProductType"] == "NI 9219":
                    self.calculate_ni9219_effective_rate(cfg)
            
            # Actualizar estado
            self.status_var.set(f"Configuración cargada desde {filename}")
            messagebox.showinfo("Cargar Setup", f"Configuración cargada exitosamente desde {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar configuración: {e}\n{type(e)}")

    def process_strain_ni9219(self, raw, offset_val, bridge_type, gage_factor, channel_key=None):
        """
        Procesa datos de strain del NI 9219 aplicando la fórmula correcta de conversión.
        
        Args:
            raw: Datos brutos de la adquisición (en Voltios)
            offset_val: Valor de offset obtenido durante el cerado (en Voltios)
            bridge_type: Tipo de configuración del puente (string)
            gage_factor: Factor de galga
            channel_key: Identificador único del canal (para diagnóstico)
        
        Returns:
            Array NumPy con los valores de strain procesados (en μstrain)
        """
        # Verificación de entrada básica
        if not isinstance(raw, np.ndarray):
            raw = np.array(raw, dtype=float)
        
        if raw.size == 0:
            return np.array([])
        
        # Convertir parámetros a float de manera segura
        try:
            offset_val = float(offset_val)
        except (ValueError, TypeError):
            offset_val = 0.0
                
        try:
            gage_factor = float(gage_factor)
            if gage_factor <= 0:
                gage_factor = 2.14  # Valor por defecto si el gage factor es inválido
        except:
            gage_factor = 2.14
        
        # Determinar el factor de puente según el tipo
        bridge_factor = 2.0  # Valor por defecto para Cuarto de Puente (más habitual)
        
        if bridge_type:
            if "Cuarto de Puente I" in bridge_type:
                bridge_factor = 2.0
            elif "Cuarto de Puente II" in bridge_type:
                bridge_factor = 2.0
            elif "Medio de Puente I" in bridge_type:
                bridge_factor = 2.0
            elif "Medio de Puente II" in bridge_type:
                bridge_factor = 2.0
            elif "Puente Completo" in bridge_type:
                bridge_factor = 4.0
        
        # IMPORTANTE: Diagnóstico específico por canal
        print(f"\n==== PROCESAMIENTO CANAL: {channel_key} ====")
        print(f"Offset aplicado: {offset_val:.6e}V ({offset_val*1e6:.2f} μstrain)")
        print(f"Factor de galga: {gage_factor}")
        print(f"Tipo de puente: {bridge_type}, factor: {bridge_factor}")
        print(f"Datos brutos min/max: {np.min(raw):.6e}V / {np.max(raw):.6e}V")
        
        # 1. Aplicar el offset (tara)
        raw_offset = raw - offset_val
        
        # 2. Convertir de voltios a strain usando la fórmula correcta
        # Fórmula general: strain = (raw_voltage - offset) * bridge_factor / (excitation_voltage * gage_factor)
        # El NI 9219 normaliza internamente los valores, así que no necesitamos excitation_voltage
        # y podemos usar la fórmula simplificada:
        strain = raw_offset * bridge_factor / gage_factor
        
        # 3. Convertir a μstrain (multiplicar por 1e6)
        processed_strain = strain * 1e6
        
        # Resultados para este canal específico
        if np.size(processed_strain) > 0:
            print(f"Resultado μstrain: {np.min(processed_strain):.1f} / {np.max(processed_strain):.1f}")
        print(f"==== FIN PROCESAMIENTO {channel_key} ====\n")
        
        return processed_strain
        
    ###########################################################################
    #                 Nuevos métodos para streaming                           #
    ###########################################################################
    def init_streaming_controls(self, parent_frame):
        """Inicializa controles de UI para configuración de streaming de datos"""
        # Crear un frame para configuración de streaming
        streaming_frame = ttk.LabelFrame(parent_frame, text="Grabación Continua")
        streaming_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        # Checkbox para habilitar/deshabilitar streaming
        streaming_chk = ttk.Checkbutton(
            streaming_frame, 
            text="Guardar datos en disco", 
            variable=self.streaming_enabled
        )
        streaming_chk.pack(anchor="w", padx=5, pady=2)
        
        # Frame para configuración de intervalo
        interval_frame = ttk.Frame(streaming_frame)
        interval_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(interval_frame, text="Intervalo de guardado (seg):").pack(side="left")
        
        interval_entry = ttk.Spinbox(
            interval_frame,
            from_=10,
            to=3600,
            increment=10,
            textvariable=self.streaming_interval,
            width=5
        )
        interval_entry.pack(side="left", padx=5)
        
        # Botón para seleccionar carpeta
        folder_btn = ttk.Button(
            streaming_frame,
            text="Carpeta de destino",
            command=self.select_streaming_folder
        )
        folder_btn.pack(anchor="w", padx=5, pady=2)
        
        # Etiqueta para mostrar la ruta
        self.streaming_path_var = tk.StringVar(value="Seleccione una carpeta para grabación")
        path_label = ttk.Label(
            streaming_frame,
            textvariable=self.streaming_path_var,
            wraplength=300
        )
        path_label.pack(anchor="w", padx=5, pady=2)

    def select_streaming_folder(self):
        """Abre un diálogo para seleccionar la carpeta donde guardar los datos de streaming"""
        folder_path = filedialog.askdirectory(
            title="Seleccione carpeta para grabación continua"
        )
        
        if folder_path:
            # Verificar que la carpeta tiene permisos de escritura
            if os.access(folder_path, os.W_OK):
                self.streaming_path = folder_path
                self.streaming_path_var.set(f"Carpeta: {folder_path}")
                
                # Analizar y mostrar espacio en disco disponible
                self.update_disk_space_info()
            else:
                messagebox.showerror(
                    "Error",
                    f"No tiene permisos de escritura en la carpeta seleccionada:\n{folder_path}"
                )

    def update_disk_space_info(self):
        """Actualiza información sobre espacio en disco disponible para streaming"""
        if not self.streaming_path:
            return
            
        try:
            # Obtener información de uso de disco
            disk_usage = shutil.disk_usage(self.streaming_path)
            free_gb = disk_usage.free / (1024**3)  # Convertir a GB
            total_gb = disk_usage.total / (1024**3)
            
            # Estimar tiempo máximo de grabación
            max_time = self.estimate_streaming_capacity()
            
            # Actualizar la etiqueta
            self.streaming_path_var.set(
                f"Carpeta: {self.streaming_path}\n"
                f"Espacio disponible: {free_gb:.1f} GB de {total_gb:.1f} GB\n"
                f"Tiempo estimado máximo: {max_time}"
            )
        except Exception as e:
            self.streaming_path_var.set(
                f"Carpeta: {self.streaming_path}\n"
                f"Error al verificar espacio en disco: {str(e)}"
            )

    def estimate_streaming_capacity(self):
        """Estima el tiempo máximo de grabación basado en espacio en disco y parámetros de adquisición"""
        if not self.streaming_path:
            return "N/A"
            
        # Obtener espacio libre en bytes
        free_bytes = shutil.disk_usage(self.streaming_path).free
        
        # Calcular canales activos
        active_channels = 0
        for cfg in self.device_configs:
            active_channels += sum(1 for ch in cfg["AIChannels"] 
                                 if cfg["channel_vars"].get(ch, tk.BooleanVar()).get())
        
        if active_channels == 0:
            return "∞"  # Sin canales, tiempo ilimitado
        
        # Obtener tasa de muestreo (usar la menor entre dispositivos)
        try:
            rates = []
            for cfg in self.device_configs:
                selected_chs = [ch for ch in cfg["AIChannels"] 
                             if cfg["channel_vars"].get(ch, tk.BooleanVar()).get()]
                if selected_chs:
                    rates.append(float(cfg["rate_entry"].get()))
            
            sampling_rate = min(rates) if rates else 0
        except:
            sampling_rate = 0
        
        if sampling_rate == 0:
            return "∞"  # Sin muestreo, tiempo ilimitado
        
        # Cada muestra se almacena como float de 64 bits (8 bytes)
        bytes_per_sample = 8
        
        # Añadir overhead por formato y metadatos (aproximadamente 20%)
        bytes_per_sample *= 1.2
        
        # Calcular bytes por segundo
        bytes_per_second = bytes_per_sample * active_channels * sampling_rate
        
        # Estimar máximo de segundos (usar 90% del espacio disponible para seguridad)
        usable_space = free_bytes * 0.9
        max_seconds = usable_space / bytes_per_second
        
        # Convertir a formato legible
        if max_seconds > 86400:  # Más de un día
            days = max_seconds / 86400
            return f"{days:.1f} días"
        elif max_seconds > 3600:  # Más de una hora
            hours = max_seconds / 3600
            return f"{hours:.1f} horas"
        else:
            minutes = max_seconds / 60
            return f"{minutes:.1f} minutos"

    def start_streaming_writer(self):
        """Inicia el thread en segundo plano para escritura de datos a disco"""
        if self.streaming_thread is not None and self.streaming_thread.is_alive():
            return  # Ya está corriendo
            
        # Crear carpeta destino con timestamp
        if not self.streaming_path:
            messagebox.showerror(
                "Error",
                "Por favor seleccione una carpeta de destino para grabación continua"
            )
            return False
        
        # Crear subcarpeta con timestamp para esta sesión
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_folder = os.path.join(self.streaming_path, f"NI_Session_{timestamp}")
        
        try:
            os.makedirs(session_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo crear la carpeta para grabación:\n{str(e)}"
            )
            return False
        
        # Guardar la carpeta de sesión
        self.streaming_session_folder = session_folder
        
        # Crear archivo de metadatos con parámetros de adquisición
        try:
            self.create_session_metadata(session_folder)
        except Exception as e:
            print(f"Error al crear metadatos: {e}")
        
        # Reiniciar estado de streaming
        self.streaming_status = {
            "active": True,
            "files": 0,
            "total_samples": 0,
            "disk_usage": 0,
            "start_time": time.time()
        }
        
        # Iniciar thread de escritura en segundo plano
        self.streaming_queue = Queue()
        self.streaming_thread = threading.Thread(
            target=self.streaming_writer_thread,
            args=(session_folder,),
            daemon=True
        )
        self.streaming_thread.start()
        
        # Iniciar monitoreo de espacio en disco
        self.start_disk_space_monitoring()
        
        return True

    def create_session_metadata(self, session_folder):
        """Crea un archivo de metadatos con parámetros de adquisición"""
        metadata = {
            "timestamp": datetime.datetime.now().isoformat(),
            "sample_rate": self.current_rate,
            "channels": []
        }
        
        # Añadir información de canales
        for cfg in self.device_configs:
            selected_chs = [
                ch for ch in cfg["AIChannels"]
                if cfg["channel_vars"].get(ch, tk.BooleanVar()).get()
            ]
            
            for ch in selected_chs:
                ch_key = f"{cfg['DeviceName']}/ai{ch}"
                ch_info = {
                    "device": cfg["DeviceName"],
                    "product_type": cfg["ProductType"],
                    "channel": f"ai{ch}",
                    "name": self.channel_names.get(ch_key, ch_key)
                }
                
                # Añadir configuraciones específicas por módulo
                if cfg["ProductType"] == "NI 9237":
                    st = cfg["channel_settings"][ch]
                    ch_info.update({
                        "bridge_mode": cfg.get("bridge_mode_var", "Completo").get(),
                        "excitation": st["exc_entry"].get(),
                        "gage_factor": st["gf_entry"].get(),
                        "resistance": st["rn_entry"].get(),
                        "offset": st["off_entry"].get()
                    })
                elif cfg["ProductType"] == "NI 9219":
                    st = cfg["channel_settings"][ch]
                    ch_info.update({
                        "mode": st["mode_var"].get()
                    })
                    if st["mode_var"].get() == "Strain":
                        ch_info.update({
                            "bridge_type": st["bridge_combo"].get(),
                            "resistance": st["r_entry"].get(),
                            "offset": st.get("offset_val", 0.0)
                        })
                
                metadata["channels"].append(ch_info)
        
        # Escribir metadatos a archivo JSON
        with open(os.path.join(session_folder, "session_metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

    def start_disk_space_monitoring(self):
        """Inicia monitoreo periódico de espacio en disco durante streaming"""
        if self.disk_space_timer is not None:
            self.root.after_cancel(self.disk_space_timer)
        
        def check_disk_space():
            if not self.streaming_status["active"]:
                return
                
            # Verificar espacio en disco solo si streaming está activo
            if self.streaming_path:
                try:
                    # Actualizar info de uso de disco
                    disk_usage = shutil.disk_usage(self.streaming_path)
                    free_gb = disk_usage.free / (1024**3)
                    
                    # Actualizar estado de streaming
                    self.streaming_status["disk_usage"] = (disk_usage.total - disk_usage.free) / (1024**3)
                    
                    # Advertencia si queda poco espacio (menos de 1 GB)
                    if free_gb < 1.0:
                        messagebox.showwarning(
                            "Poco espacio en disco",
                            f"Queda menos de 1 GB de espacio libre en la carpeta de grabación.\n"
                            f"La grabación podría detenerse pronto."
                        )
                except Exception as e:
                    print(f"Error al verificar espacio en disco: {e}")
            
            # Programar próxima verificación
            self.disk_space_timer = self.root.after(30000, check_disk_space)  # Verificar cada 30 segundos
        
        # Iniciar primera verificación
        check_disk_space()

    def streaming_writer_thread(self, session_folder):
        """Thread en segundo plano que procesa datos de la cola y escribe a disco"""
        print(f"Iniciando thread de escritura en {session_folder}")
        file_counter = 0
        
        while self.streaming_status["active"] or not self.streaming_queue.empty():
            try:
                # Esperar datos con timeout
                try:
                    data_packet = self.streaming_queue.get(timeout=1.0)
                except Queue.Empty:
                    # No hay datos disponibles, verificar si debemos seguir esperando
                    if not self.streaming_status["active"]:
                        break  # Salir si streaming ya no está activo y la cola está vacía
                    continue
                
                # Procesar el paquete de datos (timestamp, channel_data)
                timestamp, channel_data = data_packet
                
                # Crear nombre de archivo único
                filename = f"data_{timestamp}_{file_counter:06d}.npz"
                file_path = os.path.join(session_folder, filename)
                
                # Guardar datos a disco
                try:
                    np.savez_compressed(file_path, **channel_data)
                    file_size = os.path.getsize(file_path) / (1024**2)  # Tamaño en MB
                    
                    print(f"Archivo guardado: {filename} ({file_size:.2f} MB)")
                    
                    # Actualizar estadísticas
                    with self.data_lock:
                        self.streaming_status["files"] += 1
                        self.streaming_status["total_samples"] += sum(
                            len(data) for data in channel_data.values() if hasattr(data, '__len__')
                        )
                    
                    file_counter += 1
                except Exception as save_error:
                    print(f"Error al guardar archivo {filename}: {save_error}")
            
            except Exception as e:
                print(f"Error en thread de escritura: {e}")
        
        print("Thread de escritura finalizado")

    def stop_streaming_writer(self):
        """Detiene el thread de escritura de streaming de forma segura"""
        if not self.streaming_status["active"]:
            return
            
        # Indicar al thread que debe detenerse
        self.streaming_status["active"] = False
        
        # Detener monitoreo de espacio en disco
        if self.disk_space_timer is not None:
            self.root.after_cancel(self.disk_space_timer)
            self.disk_space_timer = None
        
        # Esperar a que el thread termine con los datos pendientes
        if self.streaming_thread and self.streaming_thread.is_alive():
            self.streaming_thread.join(timeout=5.0)
        
        # Crear archivo de resumen
        if hasattr(self, 'streaming_session_folder') and os.path.exists(self.streaming_session_folder):
            try:
                self.create_streaming_summary()
            except Exception as e:
                print(f"Error al crear resumen de grabación: {e}")
        
        print("Grabación continua detenida")

    def create_streaming_summary(self):
        """Crea un archivo de resumen de la sesión de streaming"""
        if not hasattr(self, 'streaming_session_folder'):
            return
            
        try:
            # Calcular duración de sesión
            end_time = time.time()
            start_time = self.streaming_status.get("start_time", end_time)
            duration_seconds = end_time - start_time
            
            # Formatear duración
            hours, remainder = divmod(duration_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
            
            # Crear contenido del resumen
            summary = {
                "session_end": datetime.datetime.now().isoformat(),
                "duration": duration_str,
                "duration_seconds": duration_seconds,
                "files_created": self.streaming_status["files"],
                "total_samples": self.streaming_status["total_samples"],
                "disk_usage_gb": self.streaming_status["disk_usage"]
            }
            
            # Escribir resumen a archivo JSON
            with open(os.path.join(self.streaming_session_folder, "session_summary.json"), "w") as f:
                json.dump(summary, f, indent=2)
            
            # También crear versión de texto legible
            with open(os.path.join(self.streaming_session_folder, "session_summary.txt"), "w") as f:
                f.write("RESUMEN DE GRABACIÓN CONTINUA\n")
                f.write("============================\n\n")
                f.write(f"Finalizada: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duración: {duration_str}\n")
                f.write(f"Archivos creados: {self.streaming_status['files']}\n")
                f.write(f"Muestras totales: {self.streaming_status['total_samples']}\n")
                f.write(f"Espacio en disco: {self.streaming_status['disk_usage']:.2f} GB\n")
        
        except Exception as e:
            print(f"Error al crear archivo de resumen: {e}")

    def process_streaming_buffer(self, all_channels, data_buffers):
        """Procesa búferes de datos y los añade a la cola de streaming"""
        if not self.streaming_status["active"]:
            return
        
        # Crear timestamp para este paquete de datos
        timestamp = int(time.time())
        
        # Procesar datos para cada canal
        channel_data = {}
        
        for i, (dev, ch, ptype, adv, key) in enumerate(all_channels):
            # Omitir si no hay datos para este canal
            if i >= len(data_buffers) or not data_buffers[i]:
                continue
                
            # Convertir a array numpy para procesamiento
            try:
                raw_data = np.array(data_buffers[i], dtype=float)
                if raw_data.size == 0:
                    continue
                    
                # Procesar datos según tipo de módulo
                if ptype == "NI 9237":
                    gf = float(adv.get("GageFactor", 2.0))
                    offset = float(adv.get("Offset", 0.0))
                    processed_data = 4.0 * ((raw_data - offset) * 1e6) / gf
                elif ptype == "NI 9219" and adv.get("SelectedMode", "") == "Strain":
                    offset_val = float(adv.get("Offset", 0.0))
                    bridge_type = adv.get("SelectedRange", "")
                    gage_factor = float(adv.get("GageFactor", 2.0))
                    processed_data = self.process_strain_ni9219(
                        raw_data, offset_val, bridge_type, gage_factor, key
                    )
                else:
                    processed_data = raw_data
                    
                # Usar nombre personalizado si está disponible
                display_name = self.channel_names.get(key, key)
                
                # Añadir al paquete de datos
                channel_data[display_name] = processed_data
                
            except Exception as e:
                print(f"Error al procesar datos para streaming en canal {key}: {e}")
        
        # Solo encolar datos si hay canales procesados
        if channel_data:
            try:
                self.streaming_queue.put((timestamp, channel_data))
            except Exception as e:
                print(f"Error al encolar datos para streaming: {e}")
    
    def __init__(self, root):
        self.root = root
        self.root.title("Adquisición NI – Optimizada")
        default_font = ("Arial", 12)
        self.root.option_add("*Font", default_font)
        
        # Para almacenar resultados y buffers de visualización
        self.results = {}
        self.plot_buffers = {}
        
        # Mutex para acceso seguro desde múltiples hilos
        self.data_lock = threading.Lock()
        
        # Evento para detener adquisición en modo continuo
        self.stop_event = threading.Event()
        
        # Variable para controlar si ya hay una adquisición corriendo
        self.acquisition_thread = None
        
        # Diccionario para almacenar los nombres personalizados de los canales
        self.channel_names = {}
        
        # Diccionario para almacenar configuraciones de dispositivos específicas
        self.device_specific_configs = {}
        
        # Ventana de gráficos (inicialmente None)
        self.plot_window = None
        
        # Variables de la GUI
        self.acq_mode = tk.StringVar(value="Finite")   # "Finite" o "Continuous"
        self.export_format = tk.StringVar(value="xlsx") # "xlsx" o "mat"
        
        # Variables para comunicación segura entre hilos
        self.acquisition_status = {"running": False, "samples": 0, "message": "Listo"}
        
        # Timer para actualización segura de UI
        self.update_timer = None
        
        # NUEVO: Configuración de streaming
        self.streaming_enabled = tk.BooleanVar(value=True)
        self.streaming_interval = tk.IntVar(value=60)  # Segundos entre guardados
        self.streaming_path = None
        self.streaming_status = {"active": False, "files": 0, "total_samples": 0, "disk_usage": 0}
        self.streaming_queue = Queue()  # Para escritura en segundo plano
        self.streaming_thread = None
        self.disk_space_timer = None
        
        # Panel principal que contiene todo
        main_panel = ttk.PanedWindow(root, orient="horizontal")
        main_panel.pack(fill="both", expand=True)
        
        # Panel izquierdo para la configuración de dispositivos
        left_frame = ttk.Frame(main_panel)
        main_panel.add(left_frame, weight=2)
        
        # Panel derecho para ajustes
        self.right_frame = ttk.Frame(main_panel)
        main_panel.add(self.right_frame, weight=1)
        
        # Frame de selección de modo
        mode_frame = ttk.Frame(left_frame)
        mode_frame.pack(pady=5)
        ttk.Label(mode_frame, text="Modo de adquisición:").pack(side="left")
        mode_combo = ttk.Combobox(
            mode_frame,
            textvariable=self.acq_mode,
            values=["Finite", "Continuous"],
            state="readonly",
            width=12
        )
        mode_combo.pack(side="left", padx=5)
        mode_combo.bind("<<ComboboxSelected>>", self.update_acq_param)

        # Frame para la duración en modo Finite
        self.param_frame = ttk.Frame(left_frame)
        self.param_label = ttk.Label(self.param_frame, text="Tiempo de adquisición (seg):")
        self.param_label.pack(side="left")
        self.acq_param = ttk.Entry(self.param_frame, width=10)
        self.acq_param.insert(0, "10")
        self.acq_param.pack(side="left", padx=5)
        self.param_frame.pack(pady=5)  # Mostramos este frame por defecto
        
        # Barra de progreso para adquisición finita
        self.progress_frame = ttk.Frame(left_frame)
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            variable=self.progress_var, 
            maximum=100, 
            length=400
        )
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        
        # Indicador de estado
        self.status_var = tk.StringVar(value="Listo")
        status_label = ttk.Label(self.progress_frame, textvariable=self.status_var)
        status_label.pack(pady=5)
        self.progress_frame.pack(pady=5)  # Mostramos este frame por defecto
        
        # Botón para detener adquisición (modo continuo)
        self.btn_stop = ttk.Button(left_frame, text="Detener Adquisición", command=self.stop_acquisition)
        self.btn_stop.pack_forget()  # Inicialmente oculto

        # Contenedor con scrollbar para configurar los módulos
        container = ttk.Frame(left_frame)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.content_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Crear notebook para organizar dispositivos en pestañas
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Listado de dispositivos del sistema NI
        self.system = nidaqmx.system.System.local()
        self.device_configs = []
        self.frames = {}

        # Cargar la configuración de cada dispositivo soportado
        self.load_device_configs()
        
        # Frame para controles principales
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(pady=10)

        # Botón para iniciar adquisición
        btn_start = ttk.Button(control_frame, text="Iniciar Adquisición", 
                             command=self.start_acquisition, width=20)
        btn_start.pack(side="left", padx=10)

        # Botón para exportar datos
        btn_export = ttk.Button(control_frame, text="Exportar Datos", 
                               command=self.export_data, width=15)
        btn_export.pack(side="left", padx=10)

        export_frame = ttk.Frame(control_frame)
        export_frame.pack(side="left", padx=10)
        ttk.Label(export_frame, text="Formato:").pack(side="left")
        export_combo = ttk.Combobox(
            export_frame,
            textvariable=self.export_format,
            values=["mat", "xlsx"],
            state="readonly",
            width=5
        )
        export_combo.pack(side="left", padx=5)
        
        # Añadir controles de streaming después del combo de exportación
        self.init_streaming_controls(control_frame)
        
        # Botón para abrir la ventana de visualización (SOLO UNA VEZ)
        btn_plot_window = ttk.Button(control_frame, text="Ver Gráficos", command=self.toggle_plot_window)
        btn_plot_window.pack(side="left", padx=10)
        
        # Botón para limpiar configuración
        btn_clear = ttk.Button(control_frame, text="Limpiar Config", command=self.clear_all_fields)
        btn_clear.pack(side="left", padx=10)
        
        # Botón para guardar setup
        btn_save_setup = ttk.Button(control_frame, text="Guardar Setup", command=self.save_setup)
        btn_save_setup.pack(side="left", padx=10)
        
        # Botón para cargar setup
        btn_load_setup = ttk.Button(control_frame, text="Cargar Setup", command=self.load_setup)
        btn_load_setup.pack(side="left", padx=10)
        
        # Inicializar el panel de ajustes
        self.init_settings_panel()
      
        # Ajustar interfaz según modo seleccionado
        self.update_acq_param()
    
    def update_ui_from_thread(self):
        """Actualiza la UI desde el hilo principal usando un timer"""
        if self.acquisition_status["running"]:
            with self.data_lock:
                # Actualizar elementos UI con información segura
                self.status_var.set(self.acquisition_status["message"])
                
                # Si la ventana de gráficos está visible, actualizarla con los datos más recientes
                if self.plot_window is not None and self.plot_window.winfo_exists() and self.plot_window.is_visible:
                    # Verificación IMPORTANTE: asegurarse de que hay resultados válidos
                    valid_display_buffers = {}
                    
                    for key, data in self.results.items():
                        # Solo incluir arrays con datos válidos
                        if isinstance(data, np.ndarray) and data.size > 0:
                            # Hacer copia segura para evitar conflictos
                            valid_display_buffers[key] = data.copy()
                    
                    # Solo actualizar si hay datos válidos
                    if valid_display_buffers:
                        self.plot_window.update_plots(valid_display_buffers)
            
            # Programar la próxima actualización con mayor frecuencia (50ms en lugar de 100ms)
            self.update_timer = self.root.after(50, self.update_ui_from_thread)
        else:
            self.update_timer = None
    
    def init_settings_panel(self):
        """Inicializa el panel de ajustes en el lado derecho"""
        # Crear un frame con scroll para el panel de ajustes
        settings_container = ttk.Frame(self.right_frame)
        settings_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título del panel
        ttk.Label(settings_container, text="Panel de Ajustes", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)
        
        # Canvas con scrollbar para contenido extenso
        canvas = tk.Canvas(settings_container)
        scrollbar = ttk.Scrollbar(settings_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        self.settings_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=self.settings_frame, anchor="nw")
        
        # Configurar el scrolling
        self.settings_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width) if e.width > 0 else None)
        
        # Botón para actualizar ajustes
        update_btn = ttk.Button(self.settings_frame, text="Actualizar Ajustes", command=self.update_settings)
        update_btn.pack(fill="x", pady=5)
        
        # Inicializar ajustes
        self.update_settings()
    
    def update_settings(self):
        """Actualiza la información mostrada en el panel de ajustes lateral"""
        # Limpiar frame anterior
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        # Botón para actualizar ajustes
        update_btn = ttk.Button(self.settings_frame, text="Actualizar Ajustes", command=self.update_settings)
        update_btn.pack(fill="x", pady=5)
        
        # Sección: Ajustes Generales
        general_frame = ttk.LabelFrame(self.settings_frame, text="Ajustes Generales")
        general_frame.pack(fill="x", padx=5, pady=5)
        
        # Modo adquisición 
        acq_mode = self.acq_mode.get()
        ttk.Label(general_frame, text=f"Modo de adquisición: {acq_mode}").pack(anchor="w", padx=10, pady=2)
        
        if acq_mode == "Finite":
            try:
                acq_time = float(self.acq_param.get())
                ttk.Label(general_frame, text=f"Tiempo de adquisición: {acq_time} segundos").pack(anchor="w", padx=10, pady=2)
            except:
                ttk.Label(general_frame, text="Tiempo de adquisición: [Valor inválido]").pack(anchor="w", padx=10, pady=2)
        
        ttk.Label(general_frame, text=f"Formato de exportación: {self.export_format.get()}").pack(anchor="w", padx=10, pady=2)
        
        # Información sobre streaming en el panel de ajustes
        if hasattr(self, 'streaming_enabled'):
            streaming_status = "Habilitado" if self.streaming_enabled.get() else "Deshabilitado"
            ttk.Label(general_frame, text=f"Grabación continua: {streaming_status}").pack(anchor="w", padx=10, pady=2)
            
            if self.streaming_enabled.get():
                ttk.Label(general_frame, text=f"Intervalo de guardado: {self.streaming_interval.get()} segundos").pack(anchor="w", padx=10, pady=2)
                
                if hasattr(self, 'streaming_path') and self.streaming_path:
                    ttk.Label(general_frame, text=f"Carpeta: {self.streaming_path}").pack(anchor="w", padx=10, pady=2)
                else:
                    ttk.Label(general_frame, text="Carpeta: No seleccionada", foreground="red").pack(anchor="w", padx=10, pady=2)
        
        # Sección: Dispositivos y Canales
        active_channels = []
        module_rates = {}
        
        # Recopilar información de dispositivos y canales
        for cfg in self.device_configs:
            dev_name = cfg["DeviceName"]
            prod_type = cfg["ProductType"]
            
            # Solo mostrar dispositivos con canales seleccionados
            selected_chs = [
                ch for ch in cfg["AIChannels"]
                if cfg["channel_vars"].get(ch, tk.BooleanVar()).get()
            ]
            
            if selected_chs:
                try:
                    # MODIFICACIÓN: Obtener frecuencia del combobox para NI 9234 y NI 9237
                    if prod_type in ["NI 9234", "NI 9237"] and "rate_combo" in cfg:
                        rate = float(cfg["rate_combo"].get())
                    else:
                        rate = float(cfg["rate_entry"].get())
                    module_rates[f"{prod_type} - {dev_name}"] = rate
                except:
                    module_rates[f"{prod_type} - {dev_name}"] = "ERROR"
                
                device_frame = ttk.LabelFrame(self.settings_frame, text=f"{prod_type} - {dev_name}")
                device_frame.pack(fill="x", padx=5, pady=5)
                
                # Mostrar frecuencia de muestreo
                ttk.Label(device_frame, text=f"Frecuencia de muestreo: {rate} Hz").pack(anchor="w", padx=10, pady=2)
                
                # Si es NI 9219, mostrar frecuencia efectiva
                if prod_type == "NI 9219" and len(selected_chs) > 0:
                    effective_rate, num_ch = self.calculate_ni9219_effective_rate(cfg)
                    ttk.Label(device_frame, 
                             text=f"Frecuencia efectiva por canal: {effective_rate:.2f} Hz",
                             foreground="darkblue").pack(anchor="w", padx=10, pady=2)
                
                # Lista compacta de canales
                channels_text = ", ".join([f"ai{ch}" for ch in selected_chs])
                ttk.Label(device_frame, text=f"Canales activos: {channels_text}").pack(anchor="w", padx=10, pady=2)
                
                # Mostrar más detalles de canales si se solicitan
                details_frame = ttk.Frame(device_frame)
                details_frame.pack(fill="x", padx=10, pady=2)
                
                for ch in selected_chs:
                    ch_key = f"{dev_name}/ai{ch}"
                    display_name = self.channel_names.get(ch_key, f"Canal ai{ch}")
                    plot_status = "Visualizado" if cfg["channel_settings"][ch]["plot_var"].get() else "No visualizado"
                    
                    # Añadir los detalles del canal
                    ch_details = ttk.LabelFrame(device_frame, text=f"ai{ch}: {display_name}")
                    ch_details.pack(fill="x", padx=10, pady=2)
                    
                    ttk.Label(ch_details, text=f"Estado: {plot_status}").pack(anchor="w", padx=5)
                    
                    # Mostrar configuración específica según el tipo de módulo
                    if prod_type == "NI 9237":
                        st = cfg["channel_settings"][ch]
                        # MODIFICACIÓN: Obtener tipo de puente de cada canal específico
                        if "bridge_var" in st and hasattr(st["bridge_var"], "get"):
                            bridge_mode = st["bridge_var"].get()
                            ttk.Label(ch_details, text=f"Puente: {bridge_mode}").pack(anchor="w", padx=5)
                        
                        # Obtener valores de cada campo específico del canal
                        if "exc_entry" in st:
                            ttk.Label(ch_details, text=f"Excitación: {st['exc_entry'].get()} V").pack(anchor="w", padx=5)
                        if "gf_entry" in st:
                            ttk.Label(ch_details, text=f"Factor de Galga: {st['gf_entry'].get()}").pack(anchor="w", padx=5)
                        if "rn_entry" in st:
                            ttk.Label(ch_details, text=f"Resistencia: {st['rn_entry'].get()} Ω").pack(anchor="w", padx=5)
                        if "off_entry" in st:
                            ttk.Label(ch_details, text=f"Offset: {st['off_entry'].get()} mV/V").pack(anchor="w", padx=5)
                    
                    # ADICIÓN: Configuración específica para NI 9234
                    elif prod_type == "NI 9234":
                        if "iepe_var" in cfg and hasattr(cfg["iepe_var"], "get"):
                            iepe_status = "Activado" if cfg["iepe_var"].get() else "Desactivado"
                            ttk.Label(ch_details, text=f"IEPE: {iepe_status}").pack(anchor="w", padx=5)
                        if "sens_entry" in cfg:
                            ttk.Label(ch_details, text=f"Sensibilidad: {cfg['sens_entry'].get()} mV/g").pack(anchor="w", padx=5)
                    
                    # Agregar a lista de canales activos
                    active_channels.append(
                        (dev_name, ch, prod_type, display_name, cfg["channel_settings"][ch]["plot_var"].get())
                    )
        
        # Si no hay dispositivos con canales seleccionados
        if not active_channels:
            no_channels_frame = ttk.Frame(self.settings_frame)
            no_channels_frame.pack(fill="x", padx=5, pady=20)
            
            ttk.Label(
                no_channels_frame,
                text="No hay canales seleccionados para adquisición.",
                foreground="darkred",
                font=("Arial", 12, "bold")
            ).pack(pady=10)
        
        # Resumen
        summary_frame = ttk.LabelFrame(self.settings_frame, text="Resumen")
        summary_frame.pack(fill="x", padx=5, pady=5)
        
        total_devices = len([k for k in module_rates.keys()])
        total_channels = len(active_channels)
        plot_channels = sum(1 for ch in active_channels if ch[4])
        
        ttk.Label(summary_frame, text=f"Dispositivos activos: {total_devices}").pack(anchor="w", padx=10, pady=2)
        ttk.Label(summary_frame, text=f"Canales totales: {total_channels}").pack(anchor="w", padx=10, pady=2)
        ttk.Label(summary_frame, text=f"Canales visualizados: {plot_channels}").pack(anchor="w", padx=10, pady=2)
        
        # Tasa de muestreo más baja (la que realmente se utiliza)
        if module_rates:
            min_rate = min([r for r in module_rates.values() if isinstance(r, (int, float))])
            ttk.Label(
                summary_frame,
                text=f"Frecuencia de muestreo efectiva: {min_rate} Hz",
                font=("Arial", 10, "bold")
            ).pack(anchor="w", padx=10, pady=2)

    def toggle_plot_window(self):
        """Muestra u oculta la ventana emergente de visualización."""
        try:
            if self.plot_window is None or not self.plot_window.winfo_exists():
                self.plot_window = PlotWindow(self.root, self)
                self.plot_window.is_visible = True
                
                # DIAGNÓSTICO: Verificar datos disponibles
                with self.data_lock:
                    print(f"toggle_plot_window: results tiene {len(self.results)} elementos")
                    valid_data_count = 0
                    for key, data in self.results.items():
                        if isinstance(data, np.ndarray):
                            print(f"  - {key}: array NumPy, shape={data.shape}, size={data.size}")
                            if data.size > 0:
                                valid_data_count += 1
                                print(f"    rango: [{np.min(data):.3f}, {np.max(data):.3f}]")
                    
                    print(f"toggle_plot_window: {valid_data_count} canales con datos válidos")
                
                # Actualizar gráficos al abrir la ventana
                try:
                    with self.data_lock:
                        # Filtrar solo arrays con datos
                        display_buffers = {}
                        for key, data in self.results.items():
                            if isinstance(data, np.ndarray) and data.size > 0:
                                # Hacer copia segura
                                display_buffers[key] = data.copy()
                        
                        # CORRECCIÓN: Si no hay datos en self.results, intentar obtenerlos de plot_buffers
                        if not display_buffers and self.plot_buffers:
                            for key, buffer in self.plot_buffers.items():
                                if buffer and len(buffer) > 0:
                                    # Convertir a array NumPy
                                    raw_data = np.array(buffer, dtype=float)
                                    if raw_data.size > 0:
                                        display_buffers[key] = raw_data
                                        print(f"Usando datos de plot_buffers para {key}: {raw_data.size} puntos")
                    
                        # Si hay datos para mostrar, actualizamos los gráficos
                        if display_buffers:
                            print(f"toggle_plot_window: Mostrando {len(display_buffers)} canales con datos")
                            self.plot_window.update_plots(display_buffers)
                        else:
                            print("toggle_plot_window: No hay datos para mostrar")
                except Exception as update_error:
                    print(f"Error al actualizar gráficos iniciales: {update_error}")
                    import traceback
                    traceback.print_exc()
            else:
                # Gestionar la visibilidad de la ventana
                if self.plot_window.is_visible:
                    self.plot_window.withdraw()
                    self.plot_window.is_visible = False
                else:
                    self.plot_window.deiconify()
                    self.plot_window.is_visible = True
                    
                    # Actualizar gráficos al restaurar la ventana
                    try:
                        with self.data_lock:
                            # Filtrar solo arrays con datos
                            display_buffers = {}
                            for key, data in self.results.items():
                                if isinstance(data, np.ndarray) and data.size > 0:
                                    # Hacer copia segura
                                    display_buffers[key] = data.copy()
                            
                            # CORRECCIÓN: Si no hay datos en self.results, intentar obtenerlos de plot_buffers
                            if not display_buffers and self.plot_buffers:
                                for key, buffer in self.plot_buffers.items():
                                    if buffer and len(buffer) > 0:
                                        # Convertir a array NumPy y procesar si es necesario
                                        raw_data = np.array(buffer, dtype=float)
                                        if raw_data.size > 0:
                                            # Buscar el canal correspondiente
                                            channel_info = None
                                            for dev, ch, ptype, adv, k in [c for c in getattr(self, 'all_channels', [])]:
                                                if k == key:
                                                    channel_info = (ptype, adv)
                                                    break
                                            
                                            # Si encontramos info del canal, procesar según el tipo
                                            if channel_info:
                                                ptype, adv = channel_info
                                                if ptype == "NI 9219" and adv.get("SelectedMode", "") == "Strain":
                                                    offset_val = float(adv.get("Offset", 0.0))
                                                    bridge_type = adv.get("SelectedRange", "")
                                                    gage_factor = float(adv.get("GageFactor", 2.0))
                                                    display_buffers[key] = self.process_strain_ni9219(
                                                        raw_data, offset_val, bridge_type, gage_factor
                                                    )
                                                elif ptype == "NI 9237":
                                                    gf = float(adv.get("GageFactor", 2.0))
                                                    offset = float(adv.get("Offset", 0.0))
                                                    display_buffers[key] = 4.0 * ((raw_data - offset) * 1e6) / gf
                                                else:
                                                    display_buffers[key] = raw_data
                                            else:
                                                # Si no encontramos info, mostrar los datos crudos
                                                display_buffers[key] = raw_data
                                                
                                            print(f"Usando datos de plot_buffers para {key}: {raw_data.size} puntos")
                        
                            # Si hay datos para mostrar, actualizamos los gráficos
                            if display_buffers:
                                print(f"toggle_plot_window (restore): Mostrando {len(display_buffers)} canales")
                                self.plot_window.update_plots(display_buffers)
                            else:
                                print("toggle_plot_window (restore): No hay datos para mostrar")
                    except Exception as update_error:
                        print(f"Error al actualizar gráficos al restaurar: {update_error}")
                        import traceback
                        traceback.print_exc()
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana de gráficos: {e}")
            import traceback
            traceback.print_exc()

    def start_acquisition(self):
        """
        Inicia la adquisición en un hilo separado, evitando que se lance
        otra adquisición si ya hay una en curso (para prevenir -50103).
        """
        # Verificar si ya hay una adquisición en progreso
        if self.acquisition_thread is not None and self.acquisition_thread.is_alive():
            messagebox.showwarning(
                "Adquisición en progreso",
                "Ya hay una adquisición en marcha. Detén la anterior antes de iniciar otra."
            )
            return
            
        # En modo Finite, conservar el campo de tiempo y la barra de progreso,
        # pero necesitamos mostrar también el botón de detener
        mode = self.acq_mode.get()
        if mode == "Finite":
            # Asegurar que el botón de detener sea visible durante la adquisición
            self.btn_stop.pack(pady=5)
    
        # Recolectar info SOLO de los módulos con canales seleccionados
        all_channels = []
        freq_list = []
    
        print("Configurando canales para adquisición...")
        for cfg in self.device_configs:
            selected_chs = [
                ch for ch in cfg["AIChannels"]
                if cfg["channel_vars"].get(ch, tk.BooleanVar()).get()
            ]
            if not selected_chs:
                continue
    
            # Validar la frecuencia
            freq_limits = MODULE_FREQ_LIMITS.get(cfg["ProductType"], {"min": 1, "max": 1e6})
            try:
                # MODIFICACIÓN: Obtener frecuencia del combobox para módulos específicos
                if cfg["ProductType"] in ["NI 9234", "NI 9237"] and "rate_combo" in cfg:
                    sr = float(cfg["rate_combo"].get())
                else:
                    sr = float(cfg["rate_entry"].get())
            except:
                messagebox.showerror("Error", f"Frecuencia inválida en {cfg['DeviceName']}")
                return
            if sr < freq_limits["min"] or sr > freq_limits["max"]:
                messagebox.showerror(
                    "Error",
                    f"Frecuencia en {cfg['DeviceName']} ({cfg['ProductType']}) debe estar entre "
                    f"{freq_limits['min']} y {freq_limits['max']} Hz."
                )
                return
            freq_list.append(sr)
    
        if not freq_list:
            messagebox.showerror("Error", "No se han seleccionado canales en ningún dispositivo.")
            return
    
        final_rate = min(freq_list)
        print(f"Frecuencia efectiva para adquisición: {final_rate} Hz")
        
        # Verificar que la frecuencia efectiva sea válida para todos los módulos activos
        active_device_configs = []
        for cfg in self.device_configs:
            selected_chs = [
                ch for ch in cfg["AIChannels"]
                if cfg["channel_vars"].get(ch, tk.BooleanVar()).get()
            ]
            if selected_chs:
                active_device_configs.append(cfg)
    
        for cfg in active_device_configs:
            freq_limits = MODULE_FREQ_LIMITS.get(cfg["ProductType"], {"min": 1, "max": 1e6})
            if final_rate < freq_limits["min"]:
                messagebox.showerror(
                    "Error",
                    f"La frecuencia efectiva ({final_rate} Hz) es menor que el mínimo " +
                    f"requerido por {cfg['DeviceName']} ({cfg['ProductType']}): {freq_limits['min']} Hz.\n\n" +
                    "Aumente la frecuencia del módulo con la menor frecuencia o desactive este módulo."
                )
                return
                
        self.current_rate = final_rate  # Guardar para actualización del gráfico
        mode = self.acq_mode.get()
    
        if mode == "Finite":
            try:
                acq_time = float(self.acq_param.get())
                print(f"Modo Finite: Tiempo de adquisición = {acq_time} segundos")
            except:
                messagebox.showerror("Error", "Tiempo de adquisición inválido.")
                return
            # Calcular n_samples basado en la frecuencia y tiempo
            n_samples = max(1, int(final_rate * acq_time))

            print(f"Número de muestras a adquirir: {n_samples}")
        else:
            n_samples = None
            print("Modo Continuous: Adquisición continua hasta detener manualmente")
    
        # Construir la lista (dev, ch, ptype, adv_info, key)
        for cfg in self.device_configs:
            dev_name = cfg["DeviceName"]
            prod_type = cfg["ProductType"]
            selected_chs = [
                ch for ch in cfg["AIChannels"]
                if cfg["channel_vars"].get(ch, tk.BooleanVar()).get()
            ]
            if not selected_chs:
                continue
    
            print(f"Configurando dispositivo {dev_name} ({prod_type}): {len(selected_chs)} canales")
            
            if prod_type == "NI 9237":
                for ch in selected_chs:
                    st = cfg["channel_settings"][ch]
                    adv_info = {}
                    bm_val = cfg.get("bridge_mode_var", "Completo")
                    if hasattr(bm_val, "get"):
                        bm_val = bm_val.get()
                    adv_info["BridgeMode"] = bm_val
                    adv_info["ExcitationVoltage"] = st["exc_entry"].get()
                    adv_info["GageFactor"] = st["gf_entry"].get()
                    adv_info["BridgeResistance"] = st["rn_entry"].get()
                    adv_info["Offset"] = st["off_entry"].get()
                    adv_info["plot"] = st["plot_var"].get()
                    key = f"{dev_name}/ai{ch}"
                    all_channels.append((dev_name, ch, prod_type, adv_info, key))
                    if adv_info["plot"]:
                        with self.data_lock:
                            self.plot_buffers[key] = []
            elif prod_type == "NI 9219":
                for ch in selected_chs:
                    st_data = cfg["channel_settings"][ch]
                    mode_sel = st_data["mode_var"].get()
                    if mode_sel == "Strain":
                        offset_val = st_data.get("offset_val", 0.0)
                        # Obtener el factor de galga del campo de entrada
                        try:
                            gage_factor = float(st_data["gf_entry"].get())
                        except (ValueError, KeyError):
                            gage_factor = 2.0  # Valor predeterminado si hay error
                            # Actualizar el campo si está disponible
                            if "gf_entry" in st_data:
                                st_data["gf_entry"].delete(0, tk.END)
                                st_data["gf_entry"].insert(0, "2.0")
                        
                        adv_info = {
                            "SelectedMode": "Strain",
                            "SelectedRange": st_data["bridge_combo"].get(),
                            "BridgeResistance": st_data["r_entry"].get(),
                            "Offset": offset_val,
                            "GageFactor": gage_factor  # Usar el valor del campo
                        }
                    else:
                        adv_info = {
                            "SelectedMode": mode_sel,
                            "SelectedRange": st_data["range_var"].get()
                        }
                    adv_info["plot"] = st_data["plot_var"].get()
                    key = f"{dev_name}/ai{ch}"
                    all_channels.append((dev_name, ch, prod_type, adv_info, key))
                    if adv_info["plot"]:
                        with self.data_lock:
                                        self.plot_buffers[key] = []
            elif prod_type == "NI 9211":
                from nidaqmx.constants import ThermocoupleType
                tc_map = {
                    "J": ThermocoupleType.J,
                    "K": ThermocoupleType.K,
                    "T": ThermocoupleType.T,
                    "E": ThermocoupleType.E,
                    "N": ThermocoupleType.N,
                    "R": ThermocoupleType.R,
                    "S": ThermocoupleType.S,
                    "B": ThermocoupleType.B
                }
                tc_var = cfg.get("tc_var", None)
                if tc_var and hasattr(tc_var, "get"):
                    tc_sel = tc_var.get()
                else:
                    tc_sel = "T"
                
                # Verificar que el tipo seleccionado sea válido
                if tc_sel not in tc_map:
                    print(f"Advertencia: Tipo de termopar '{tc_sel}' no reconocido. Usando tipo T.")
                    tc_sel = "T"
                    
                for c in selected_chs:
                    adv_info = {"ThermocoupleType": tc_sel}  # Guardar el string, no el enum
                    plot_flag = cfg["channel_settings"][c]["plot_var"].get()
                    adv_info["plot"] = plot_flag
                    key = f"{dev_name}/ai{c}"
                    all_channels.append((dev_name, c, prod_type, adv_info, key))
                    if plot_flag:
                        with self.data_lock:
                            self.plot_buffers[key] = []
                            
            elif prod_type == "NI 9234":
                for c in selected_chs:
                    adv_info = {}
                    iepe_var = cfg.get("iepe_var", tk.BooleanVar())
                    if isinstance(iepe_var, tk.BooleanVar) and iepe_var.get():
                        adv_info["Coupling"] = "IEPE"
                        adv_info["Sensitivity"] = cfg["sens_entry"].get()
                        adv_info["IEPECurrent"] = cfg["iepe_curr_entry"].get()
                    else:
                        adv_info["Coupling"] = "DC"
                    plot_flag = cfg["channel_settings"][c]["plot_var"].get()
                    adv_info["plot"] = plot_flag
                    key = f"{dev_name}/ai{c}"
                    all_channels.append((dev_name, c, prod_type, adv_info, key))
                    if plot_flag:
                        with self.data_lock:
                            self.plot_buffers[key] = []
            else:
                # NI 9201
                for c in selected_chs:
                    adv_info = {"SelectedMode": "Voltage"}
                    plot_flag = cfg["channel_settings"][c]["plot_var"].get()
                    adv_info["plot"] = plot_flag
                    key = f"{dev_name}/ai{c}"
                    all_channels.append((dev_name, c, prod_type, adv_info, key))
                    if plot_flag:
                        with self.data_lock:
                            self.plot_buffers[key] = []
    
        if not all_channels:
            messagebox.showerror("Error", "No se han seleccionado canales en ningún dispositivo.")
            return
    
        print(f"Total de canales configurados: {len(all_channels)}")
        for i, (dev, ch, ptype, adv, key) in enumerate(all_channels):
            plot_status = "visualizado" if adv.get("plot") else "no visualizado"
            print(f"  Canal {i+1}: {key} ({ptype}) - {plot_status}")
    
        # Limpiar el stop_event y lanzar el hilo
        self.stop_event.clear()
        with self.data_lock:
            # No limpiar completamente los resultados para mantener compatibilidad
            # with self.data_lock:
            #    self.results = {}
            self.plot_buffers = {k: [] for k in self.plot_buffers.keys()}
        
        # NUEVO: Inicializar arrays para todos los canales a visualizar
        for dev, ch, ptype, adv, key in all_channels:
            if adv.get("plot", False):
                self.plot_buffers[key] = []
                # Inicializar también los resultados con array vacío
                self.results[key] = np.array([])    
    
        # Preparar la interfaz
        self.progress_var.set(0)
        
        # Inicializar estado de adquisición
        with self.data_lock:
            self.acquisition_status["running"] = True
            self.acquisition_status["samples"] = 0
            
        # Añadir un indicador visual claro de adquisición en progreso
        if mode == "Continuous":
            self.btn_stop.config(text="⚠️ DETENER ADQUISICIÓN ⚠️")
            self.status_var.set("Adquisición continua en progreso...")
        else:
            self.status_var.set(f"Adquisición por {self.acq_param.get()} segundos...")
        
        # Iniciar streaming si está habilitado (MODIFICADO: Independiente del modo de adquisición)
        streaming_active = False
        if hasattr(self, 'streaming_enabled') and self.streaming_enabled.get():
            if not hasattr(self, 'streaming_path') or not self.streaming_path:
                messagebox.showwarning(
                    "Grabación continua",
                    "No se ha seleccionado carpeta para grabación continua.\n"
                    "Los datos no se guardarán en disco."
                )
            else:
                streaming_active = self.start_streaming_writer()
                print(f"Grabación continua iniciada: {streaming_active}")
                
        # Guardar estado de streaming en variable de instancia para uso posterior
        self.streaming_active = streaming_active
            
        # Iniciar el timer para actualización segura de UI
        self.update_ui_from_thread()
            
        # Crear hilo de adquisición
        t = threading.Thread(
            target=lambda: self.run_task(all_channels, final_rate, mode, n_samples),
            daemon=True
        )
        self.acquisition_thread = t
        t.start()
        
        print("Hilo de adquisición iniciado")


    def run_task(self, all_channels, final_rate, mode, n_samples):
        """
        Función en segundo plano para realizar la adquisición con NI-DAQmx.
        Maneja excepciones para evitar quedar con el recurso reservado (-50103).
        """
        import nidaqmx
        from nidaqmx.errors import DaqError
    
        try:
            # Almacenar all_channels para acceso desde otras funciones
            self.all_channels = all_channels
            
            # Limpiar buffers y resultados antes de iniciar
            with self.data_lock:
                self.results.clear()
                self.plot_buffers.clear()
                # Inicializar los buffers para todos los canales marcados para visualización
                for dev, ch, ptype, adv, key in all_channels:
                    if adv.get("plot", False):
                        self.plot_buffers[key] = []
                        # IMPORTANTE: Inicializar también los resultados
                        self.results[key] = np.array([])
            
            print(f"Iniciando adquisición en modo {mode}, rate={final_rate} Hz")
            print(f"Canales configurados: {len(all_channels)}")
            
            # Recuperar el estado de streaming desde el inicio de la adquisición
            streaming_active = getattr(self, 'streaming_active', False)
            last_streaming_time = time.time()
            streaming_interval = self.streaming_interval.get() if hasattr(self, 'streaming_interval') else 60
            buffer_for_streaming = [[] for _ in all_channels]
            
            if mode == "Finite":
                # Crear matrices para almacenar los resultados
                result_data = [[] for _ in all_channels]
                
                print(f"Creando tarea para {len(all_channels)} canales, {n_samples} muestras")
                
                try:
                    with nidaqmx.Task() as task:
                        # Configurar canales
                        for i, (dev, ch, ptype, adv, key) in enumerate(all_channels):
                            print(f"Configurando canal {i+1}/{len(all_channels)}: {dev}/ai{ch} - {ptype}")
                            configure_channel(task, dev, ch, ptype, adv)
                        
                        # Verificar que los canales se hayan configurado
                        num_channels = len(task.ai_channels)
                        if num_channels == 0:
                            raise ValueError("No se han configurado canales en la tarea")
                        print(f"Se configuraron {num_channels} canales correctamente")
                        
                        # Configurar timing
                        print(f"Configurando timing: rate={final_rate} Hz, samples={n_samples}")
                        task.timing.cfg_samp_clk_timing(
                            rate=final_rate,
                            sample_mode=AcquisitionType.FINITE,
                            samps_per_chan=n_samples
                        )
                        
                        # Iniciar la tarea
                        print("Iniciando tarea...")
                        task.start()
                        
                        # Parámetros para la adquisición
                        block_size = min(100, max(1, int(final_rate * 0.1)))  # 0.1 segundos por bloque
                        samples_read = 0
                        acq_time_seconds = float(self.acq_param.get())
                        
                        # Informar del inicio de la adquisición
                        self.root.after_idle(lambda msg=f"Adquisición por {acq_time_seconds} segundos ({n_samples} muestras)": 
                                            self.status_var.set(msg))
                        
                        start_time = time.time()
                        elapsed_time = 0
                        
                        print(f"Iniciando bucle principal. Block size: {block_size}")
                        
                        # Bucle principal de adquisición
                        while samples_read < n_samples and elapsed_time < acq_time_seconds and not self.stop_event.is_set():
                            # Determinar cuántos puntos quedan por leer
                            remaining = min(block_size, n_samples - samples_read)
                            
                            # Leer datos
                            try:
                                print(f"Leyendo {remaining} muestras...")
                                block_data = task.read(
                                    number_of_samples_per_channel=remaining,
                                    timeout=5 + remaining / final_rate
                                )
                                print(f"Datos leídos para {len(block_data) if isinstance(block_data, list) else 1} canales")
                            except Exception as e:
                                print(f"Error leyendo datos: {e}")
                                break
                            
                            # Actualizar tiempo transcurrido
                            elapsed_time = time.time() - start_time
                            
                            # Actualizar barra de progreso (en el hilo principal)
                            samples_read += remaining
                            progress_pct = min(100, int((elapsed_time / acq_time_seconds) * 100))
                            self.root.after_idle(lambda p=progress_pct: self.progress_var.set(p))
                            
                            # Procesar los datos leídos según el número de canales
                            if len(all_channels) == 1:
                                # Un solo canal
                                if isinstance(block_data, list):
                                    result_data[0].extend(block_data)
                                    if streaming_active:
                                        buffer_for_streaming[0].extend(block_data)
                                else:
                                    result_data[0].append(block_data)
                                    if streaming_active:
                                        buffer_for_streaming[0].append(block_data)
                                    
                                # Actualizar buffer para visualización
                                with self.data_lock:
                                    if all_channels[0][3].get("plot"):
                                        # Obtener información del canal para procesamiento
                                        key = all_channels[0][4]
                                        ptype = all_channels[0][2]
                                        adv = all_channels[0][3]
                                        
                                        # Actualizar el buffer de datos crudos 
                                        if isinstance(block_data, list):
                                            self.plot_buffers[key].extend(block_data)
                                        else:
                                            self.plot_buffers[key].append(block_data)
                                        
                                        # Limitar tamaño del buffer
                                        if len(self.plot_buffers[key]) > MAX_BUFFER_SIZE:
                                            self.plot_buffers[key] = self.plot_buffers[key][-MAX_BUFFER_SIZE:]
                                        
                                        # CRÍTICO: Procesar y actualizar results en tiempo real
                                        try:
                                            # Convertir a numpy array para procesamiento
                                            raw = np.array(self.plot_buffers[key], dtype=float)
                                            
                                            # Procesar según tipo de módulo
                                            if ptype == "NI 9237":
                                                gf = float(adv.get("GageFactor", 2.0))
                                                offset = float(adv.get("Offset", 0.0))
                                                # Usar 4.0 en lugar de -4.0 para corregir la polaridad
                                                self.results[key] = 4.0 * ((raw - offset) * 1e6) / gf
                                                print(f"Update NI 9237 - shape: {self.results[key].shape}, min: {np.min(self.results[key]):.3f}, max: {np.max(self.results[key]):.3f}")
                                            elif ptype == "NI 9219" and adv.get("SelectedMode", "") == "Strain":
                                                offset_val = float(adv.get("Offset", 0.0))
                                                bridge_type = adv.get("SelectedRange", "")
                                                gage_factor = float(adv.get("GageFactor", 2.0))
                                                # Usar la función específica para procesar strain
                                                self.results[key] = self.process_strain_ni9219(
                                                    raw, offset_val, bridge_type, gage_factor
                                                )
                                                print(f"Update NI 9219 Strain - shape: {self.results[key].shape}, min: {np.min(self.results[key]):.3f}, max: {np.max(self.results[key]):.3f}")
                                            else:
                                                # Para otros tipos, guardar los datos crudos
                                                self.results[key] = raw
                                                print(f"Update Other - shape: {self.results[key].shape}, min: {np.min(self.results[key]):.3f}, max: {np.max(self.results[key]):.3f}")
                                        except Exception as e:
                                            print(f"Error al procesar datos en tiempo real: {e}")
                            else:
                                # Múltiples canales
                                for i, arr in enumerate(block_data):
                                    if isinstance(arr, list):
                                        result_data[i].extend(arr)
                                        if streaming_active and i < len(buffer_for_streaming):
                                            buffer_for_streaming[i].extend(arr)
                                    else:
                                        result_data[i].append(arr)
                                        if streaming_active and i < len(buffer_for_streaming):
                                            buffer_for_streaming[i].append(arr)
                                        
                                    # Actualizar buffer para visualización
                                    with self.data_lock:
                                        if i < len(all_channels) and all_channels[i][3].get("plot"):
                                            key = all_channels[i][4]
                                            ptype = all_channels[i][2]
                                            adv = all_channels[i][3]
                                            
                                            # Actualizar buffer de datos crudos
                                            if isinstance(arr, list):
                                                self.plot_buffers[key].extend(arr)
                                            else:
                                                self.plot_buffers[key].append(arr)
                                            
                                            # Limitar tamaño del buffer
                                            if len(self.plot_buffers[key]) > MAX_BUFFER_SIZE:
                                                self.plot_buffers[key] = self.plot_buffers[key][-MAX_BUFFER_SIZE:]
                                            
                                            # CRÍTICO: Procesar y actualizar results en tiempo real
                                            try:
                                                # Convertir a numpy array para procesamiento
                                                raw = np.array(self.plot_buffers[key], dtype=float)
                                                
                                                # Procesar según tipo de módulo
                                                if ptype == "NI 9237":
                                                    gf = float(adv.get("GageFactor", 2.0))
                                                    offset = float(adv.get("Offset", 0.0))
                                                    # Usar 4.0 en lugar de -4.0 para corregir la polaridad
                                                    self.results[key] = 4.0 * ((raw - offset) * 1e6) / gf
                                                    print(f"Update NI 9237 - shape: {self.results[key].shape}, min: {np.min(self.results[key]):.3f}, max: {np.max(self.results[key]):.3f}")
                                                elif ptype == "NI 9219" and adv.get("SelectedMode", "") == "Strain":
                                                    offset_val = float(adv.get("Offset", 0.0))
                                                    bridge_type = adv.get("SelectedRange", "")
                                                    gage_factor = float(adv.get("GageFactor", 2.0))
                                                    # Usar la función específica para procesar strain
                                                    self.results[key] = self.process_strain_ni9219(
                                                        raw, offset_val, bridge_type, gage_factor
                                                    )
                                                    print(f"Update NI 9219 Strain - shape: {self.results[key].shape}, min: {np.min(self.results[key]):.3f}, max: {np.max(self.results[key]):.3f}")
                                                else:
                                                    # Para otros tipos, guardar los datos crudos
                                                    self.results[key] = raw
                                                    print(f"Update Other - shape: {self.results[key].shape}, min: {np.min(self.results[key]):.3f}, max: {np.max(self.results[key]):.3f}")
                                            except Exception as e:
                                                print(f"Error al procesar datos en tiempo real para canal {i}: {e}")
                            
                            # NUEVO: Verificar si es momento de guardar un archivo de streaming para modo Finite
                            if streaming_active:
                                current_time = time.time()
                                if current_time - last_streaming_time >= streaming_interval:
                                    # Procesar y encolar datos para streaming
                                    self.process_streaming_buffer(all_channels, buffer_for_streaming)
                                    
                                    # Reiniciar buffer de streaming y actualizar tiempo
                                    buffer_for_streaming = [[] for _ in all_channels]
                                    last_streaming_time = current_time
                                    
                                    # Actualizar info de espacio en disco ocasionalmente
                                    if self.streaming_status["files"] % 10 == 0:
                                        self.root.after_idle(self.update_disk_space_info)
                        
                        # Asegurar que la tarea se detiene correctamente
                        print("Deteniendo tarea...")
                        task.stop()
                    
                    # IMPORTANTE: Procesar los datos fuera del bloque with pero dentro del if mode == "Finite"
                    try:
                        print("Procesando datos finales...")
                        self.process_data_and_store(all_channels, result_data)
                        print("Datos procesados y almacenados correctamente al finalizar")
                        
                        # NUEVO: Procesar datos restantes para streaming en modo Finite
                        if streaming_active and any(len(buf) > 0 for buf in buffer_for_streaming):
                            print("Guardando datos finales de streaming...")
                            self.process_streaming_buffer(all_channels, buffer_for_streaming)
                            
                    except Exception as e:
                        print(f"Error al procesar datos finales: {e}")
                    
                    # NUEVO: Detener streaming si está activo
                    if streaming_active:
                        self.stop_streaming_writer()
                    
                    # Actualizar la UI desde el hilo principal
                    self.root.after_idle(lambda: self.status_var.set("Adquisición completada"))
                    self.root.after_idle(lambda: self.btn_stop.pack_forget())
                    self.root.after_idle(lambda: messagebox.showinfo("Acquisition", 
                                        f"Adquisición Finite completada ({samples_read} muestras)."))
                    
                    # Actualizar estado de adquisición
                    with self.data_lock:
                        self.acquisition_status["running"] = False
                    
                except Exception as task_error:
                    print(f"Error en configuración o ejecución de tarea (Finite): {task_error}")
                    self.root.after_idle(lambda e=task_error: messagebox.showerror("Error", f"Error en la adquisición: {e}"))
                    with self.data_lock:
                        self.acquisition_status["running"] = False
                        
                    # NUEVO: Detener streaming si hay error
                    if streaming_active:
                        self.stop_streaming_writer()
            
            # Modo Continuous con soporte de streaming
            else:  # Modo Continuous
                # Crear los buffers antes de iniciar la tarea
                channel_buffers = [[] for _ in all_channels]
                samples_read = 0
                
                try:
                    with nidaqmx.Task() as task:
                        # CORRECCIÓN: Añadir configuración de diagnóstico y depuración
                        print(f"Configurando {len(all_channels)} canales para adquisición continua")
                        
                        # Configurar canales
                        try:
                            for i, (dev, ch, ptype, adv, key) in enumerate(all_channels):
                                print(f"Configurando canal {i+1}/{len(all_channels)}: {dev}/ai{ch} - {ptype}")
                                configure_channel(task, dev, ch, ptype, adv)
                        except Exception as chan_error:
                            print(f"Error al configurar canales: {chan_error}")
                            raise  # Re-lanzar para manejo en bloque principal
                        
                        # Verificar que se han configurado canales correctamente
                        num_channels = len(task.ai_channels)
                        if num_channels == 0:
                            raise ValueError("No se han configurado canales en la tarea")
                        print(f"Se configuraron {num_channels} canales correctamente")
                        
                        # Configurar timing
                        print(f"Configurando timing: rate={final_rate} Hz, modo=CONTINUOUS")
                        task.timing.cfg_samp_clk_timing(
                            rate=final_rate,
                            sample_mode=AcquisitionType.CONTINUOUS,
                            samps_per_chan=1000  # Buffer interno del dispositivo
                        )
                        
                        # Iniciar la tarea
                        print("Iniciando tarea de adquisición...")
                        task.start()
                        
                        # Parámetros para la adquisición
                        block_size = max(10, min(100, int(final_rate / 10)))  # Ajustado para mejor rendimiento
                        dynamic_timeout = (block_size / final_rate) * 2.0 + 1.0  # Timeout más robusto
                        
                        # CORRECCIÓN: Actualizar el estado de adquisición
                        with self.data_lock:
                            self.acquisition_status["running"] = True
                            self.acquisition_status["message"] = "Adquisición continua iniciada"
                        
                        # Bucle principal de adquisición
                        print(f"Entrando en bucle de adquisición, block_size={block_size}, timeout={dynamic_timeout:.2f}s")
                        while not self.stop_event.is_set():
                            try:
                                # Leer datos en bloques
                                block_data = task.read(
                                    number_of_samples_per_channel=block_size,
                                    timeout=dynamic_timeout
                                )
                                
                                # Verificar que se recibieron datos
                                if isinstance(block_data, list):
                                    if len(block_data) == 0:
                                        print("WARNING: Se recibió una lista vacía")
                                        continue
                                    
                                    if isinstance(block_data[0], list) and len(block_data[0]) > 0:
                                        print(f"Datos recibidos: {len(block_data)} canales, {len(block_data[0])} muestras/canal")
                                        samples_read += len(block_data[0])
                                    elif isinstance(block_data[0], (int, float)):
                                        print(f"Datos recibidos: 1 muestra por canal")
                                        samples_read += 1
                                    else:
                                        print(f"Datos recibidos con formato desconocido: {type(block_data[0])}")
                                else:
                                    print(f"Datos recibidos con formato inesperado: {type(block_data)}")
                                
                                # Actualizar estado
                                with self.data_lock:
                                    self.acquisition_status["samples"] = samples_read
                                    self.acquisition_status["message"] = f"Adquisición continua: {samples_read} muestras"
                                
                                # Procesar datos según el número de canales
                                if len(all_channels) == 1:
                                    # Solo un canal
                                    if isinstance(block_data, list):
                                        channel_buffers[0].extend(block_data)
                                        if streaming_active:
                                            buffer_for_streaming[0].extend(block_data)
                                    else:
                                        channel_buffers[0].append(block_data)
                                        if streaming_active:
                                            buffer_for_streaming[0].append(block_data)
                                    
                                    # Limitar tamaño del buffer
                                    if len(channel_buffers[0]) > MAX_BUFFER_SIZE * 10:
                                        channel_buffers[0] = channel_buffers[0][-MAX_BUFFER_SIZE * 5:]
                                    
                                    # Actualizar buffer para gráficos
                                    with self.data_lock:
                                        if all_channels[0][3].get("plot"):
                                            key = all_channels[0][4]
                                            buffer = self.plot_buffers.get(key, [])
                                            if isinstance(block_data, list):
                                                buffer.extend(block_data)
                                            else:
                                                buffer.append(block_data)
                                            # Limitar tamaño del buffer
                                            if len(buffer) > MAX_BUFFER_SIZE:
                                                buffer = buffer[-MAX_BUFFER_SIZE:]
                                            self.plot_buffers[key] = buffer
                                            
                                            # CORRECCIÓN: Procesar datos para visualización
                                            if len(buffer) > 0:
                                                ptype = all_channels[0][2]
                                                adv = all_channels[0][3]
                                                
                                                # Crear un array NumPy con los datos acumulados
                                                raw = np.array(buffer, dtype=float)
                                                
                                                # Procesar según tipo de módulo
                                                if ptype == "NI 9237":
                                                    gf = float(adv.get("GageFactor", 2.0))
                                                    offset = float(adv.get("Offset", 0.0))
                                                    self.results[key] = 4.0 * ((raw - offset) * 1e6) / gf
                                                elif ptype == "NI 9219" and adv.get("SelectedMode", "") == "Strain":
                                                    offset_val = float(adv.get("Offset", 0.0))
                                                    bridge_type = adv.get("SelectedRange", "")
                                                    gage_factor = float(adv.get("GageFactor", 2.0))
                                                    self.results[key] = self.process_strain_ni9219(
                                                        raw, offset_val, bridge_type, gage_factor
                                                    )
                                                else:
                                                    self.results[key] = raw
                                                    
                                                # Diagnosticar datos procesados
                                                if len(self.results[key]) > 0:
                                                    print(f"Datos procesados para {key}: {len(self.results[key])} puntos")
                                else:
                                    # Varios canales
                                    for i, arr in enumerate(block_data):
                                        if i >= len(channel_buffers):
                                            print(f"WARNING: Índice de canal {i} fuera de rango ({len(channel_buffers)})")
                                            continue
                                            
                                        if isinstance(arr, list):
                                            channel_buffers[i].extend(arr)
                                            if streaming_active and i < len(buffer_for_streaming):
                                                buffer_for_streaming[i].extend(arr)
                                        else:
                                            channel_buffers[i].append(arr)
                                            if streaming_active and i < len(buffer_for_streaming):
                                                buffer_for_streaming[i].append(arr)
                                        
                                        # Limitar tamaño del buffer
                                        if len(channel_buffers[i]) > MAX_BUFFER_SIZE * 10:
                                            channel_buffers[i] = channel_buffers[i][-MAX_BUFFER_SIZE * 5:]
                                        
                                        # Actualizar buffer para gráficos y resultados
                                        with self.data_lock:
                                            if i < len(all_channels) and all_channels[i][3].get("plot"):
                                                key = all_channels[i][4]
                                                buffer = self.plot_buffers.get(key, [])
                                                if isinstance(arr, list):
                                                    buffer.extend(arr)
                                                else:
                                                    buffer.append(arr)
                                                # Limitar tamaño del buffer
                                                if len(buffer) > MAX_BUFFER_SIZE:
                                                    buffer = buffer[-MAX_BUFFER_SIZE:]
                                                self.plot_buffers[key] = buffer
                                                
                                                # CORRECCIÓN: Procesar datos para visualización
                                                if len(buffer) > 0:
                                                    ptype = all_channels[i][2]
                                                    adv = all_channels[i][3]
                                                    
                                                    # Crear un array NumPy con los datos acumulados
                                                    raw = np.array(buffer, dtype=float)
                                                    
                                                    # Procesar según tipo de módulo
                                                    if ptype == "NI 9237":
                                                        gf = float(adv.get("GageFactor", 2.0))
                                                        offset = float(adv.get("Offset", 0.0))
                                                        self.results[key] = 4.0 * ((raw - offset) * 1e6) / gf
                                                    elif ptype == "NI 9219" and adv.get("SelectedMode", "") == "Strain":
                                                        offset_val = float(adv.get("Offset", 0.0))
                                                        bridge_type = adv.get("SelectedRange", "")
                                                        gage_factor = float(adv.get("GageFactor", 2.0))
                                                        self.results[key] = self.process_strain_ni9219(
                                                            raw, offset_val, bridge_type, gage_factor
                                                        )
                                                    else:
                                                        self.results[key] = raw
                                                        
                                                    # Diagnosticar datos procesados
                                                    if len(self.results[key]) > 0:
                                                        print(f"Datos procesados para {key}: {len(self.results[key])} puntos")
                                
                                # STREAMING: Verificar si es momento de guardar un archivo de streaming
                                if streaming_active:
                                    current_time = time.time()
                                    if current_time - last_streaming_time >= streaming_interval:
                                        # Procesar y encolar datos para streaming
                                        self.process_streaming_buffer(all_channels, buffer_for_streaming)
                                        
                                        # Reiniciar buffer de streaming y actualizar tiempo
                                        buffer_for_streaming = [[] for _ in all_channels]
                                        last_streaming_time = current_time
                                        
                                        # Actualizar info de espacio en disco ocasionalmente
                                        if self.streaming_status["files"] % 10 == 0:
                                            self.root.after_idle(self.update_disk_space_info)
                                
                            except nidaqmx.errors.DaqError as e:
                                # Manejo específico de errores DAQmx
                                print(f"Error DAQmx en lectura continua: {e.error_code} - {e}")
                                with self.data_lock:
                                    self.acquisition_status["message"] = f"Error DAQmx: {e.error_code}"
                                break
                                
                            except Exception as e:
                                # Manejo general de errores
                                print(f"Error inesperado en lectura continua: {e}")
                                with self.data_lock:
                                    self.acquisition_status["message"] = f"Error: {str(e)[:50]}..."
                                break
                        
                        # Asegurar que la tarea se detiene
                        print("Deteniendo tarea...")
                        task.stop()
                        print(f"Tarea detenida después de recolectar {samples_read} muestras")
                        
                except Exception as task_error:
                    # Manejo de errores durante la creación o configuración de la tarea
                    print(f"Error al configurar la tarea: {task_error}")
                    with self.data_lock:
                        self.acquisition_status["running"] = False
                        self.acquisition_status["message"] = f"Error de configuración: {str(task_error)[:50]}..."
                
                # Detener streaming writer si está activo
                if streaming_active:
                    self.stop_streaming_writer()
                
                # Final: marcar la adquisición como detenida
                with self.data_lock:
                    self.acquisition_status["running"] = False
                
                # Diagnóstico
                print(f"Datos recopilados en modo continuo: {[len(buf) for buf in channel_buffers]} muestras")
                
                # Procesar los datos solo si hay algo que procesar
                has_data = False
                for buf in channel_buffers:
                    if buf and len(buf) > 0:
                        has_data = True
                        break
                
                if has_data:
                    try:
                        # Convertir los buffers a arrays numpy para procesamiento
                        numpy_data = []
                        for buf in channel_buffers:
                            if buf and len(buf) > 0:
                                numpy_data.append(np.array(buf, dtype=float))
                            else:
                                numpy_data.append(np.array([]))
                        
                        # Procesar y almacenar
                        self.process_data_and_store(all_channels, numpy_data)
                        print("Datos procesados y almacenados correctamente")
                    except Exception as proc_error:
                        print(f"Error al procesar datos continuos: {proc_error}")
                else:
                    print("No se recolectaron datos en modo continuo")
        
        except DaqError as e:
            # Manejo de errores general
            print(f"Error en run_task: {e}")
            self.root.after_idle(lambda e=e: messagebox.showerror("Error", f"Error en DAQmx: {e}"))
            
            # Asegurar que el streaming se detenga
            if getattr(self, 'streaming_active', False):
                self.stop_streaming_writer()

    def process_data_and_store(self, all_channels, data_matrix):
        """
        Post-procesado de datos vectorizado:
         - Aplica offset en NI 9237 (mV/V) y NI 9219 (Strain) si corresponde.
         - Almacena los datos en self.results con la clave "Device/aiX".
        """
        # Añadir diagnóstico al inicio
        print(f"Procesando datos: {[len(d) if hasattr(d, '__len__') else 'item único' for d in data_matrix]}")
        
        # Si algún buffer está vacío, imprimirlo
        empty_channels = [i for i, buf in enumerate(data_matrix) if not (buf is not None and len(buf) > 0)]
        if empty_channels:
            print(f"Aviso: Los siguientes canales no tienen datos: {empty_channels}")
        
        with self.data_lock:
            # No limpiar resultados anteriores si tienen datos válidos
            # self.results.clear()  # Esto eliminaría datos que ya se están mostrando
            
            for i, (dev, ch, ptype, adv, key) in enumerate(all_channels):
                # Verificar que el índice está dentro del rango y los datos no estén vacíos
                if i >= len(data_matrix) or data_matrix[i] is None or len(data_matrix[i]) == 0:
                    print(f"Advertencia: No hay datos para {key}")
                    # No sobreescribir si ya hay datos en self.results[key]
                    if key not in self.results or (hasattr(self.results.get(key, []), 'size') and self.results[key].size == 0):
                        self.results[key] = np.array([])
                    continue
                
                try:
                    # Convertir a array numpy para procesamiento vectorizado
                    raw = np.array(data_matrix[i], dtype=float)
                    
                    # En process_data_and_store o donde proceses los datos del NI 9237
                    if ptype == "NI 9237":
                        try:
                            # Obtener configuración de puente DEL CANAL específico
                            bridge_mode = adv.get("BridgeMode", "Quarter Bridge I")
                            
                            # Obtener factor según configuración específica del canal
                            bc_enum, bridge_factor = NI9237_BRIDGE_MAP.get(bridge_mode, (BridgeConfiguration.QUARTER_BRIDGE, 4.0))
                            
                            gf = float(adv.get("GageFactor", 2.0))
                            offset = float(adv.get("Offset", 0.0))
                            
                            # Aplicar el factor correcto según el tipo de puente del canal
                            data_converted = bridge_factor * ((raw - offset) * 1e6) / gf
                            self.results[key] = data_converted
                            print(f"Procesados datos NI 9237 ({bridge_mode}) para {key}: {len(data_converted)} puntos")
                        except Exception as e:
                            print(f"Error al procesar datos NI 9237 para {key}: {e}")
                            self.results[key] = raw  # Fallback
                    
                    elif ptype == "NI 9219" and adv.get("SelectedMode", "") == "Strain":
                        try:
                            # ==== MODIFICADO: Recuperar offset de múltiples fuentes ====
                            # Intentar obtener el offset del dispositivo primero
                            offset_val = None
                            
                            # 1. Intentar obtener de adv directamente
                            offset_val = adv.get("Offset", None)
                            
                            # 2. Si no está en adv, buscar en la configuración del canal
                            if offset_val is None:
                                for cfg in self.device_configs:
                                    if cfg["DeviceName"] == dev and cfg["ProductType"] == ptype:
                                        if ch in cfg["channel_settings"]:
                                            offset_val = cfg["channel_settings"][ch].get("offset_val", None)
                                            break
                            
                            # 3. Si aún no lo encontramos, buscar en el diccionario global
                            if offset_val is None and hasattr(self, 'strain_offsets'):
                                offset_val = self.strain_offsets.get(key, None)
                            
                            # 4. Si todo lo anterior falla, usar 0.0
                            if offset_val is None:
                                offset_val = 0.0
                                print(f"WARNING: No se encontró offset para {key}, usando 0.0")
                            
                            # Convertir a float para seguridad
                            offset_val = float(offset_val)
                            
                            # ==== AÑADIDO: Impresión de diagnóstico ====
                            print(f"\n==== PROCESANDO {key} (NI 9219 Strain) ====")
                            print(f"Offset recuperado: {offset_val:.6e}V ({offset_val*1e6:.2f} μstrain)")
                            print(f"Datos brutos min/max: {np.min(raw):.6e}/{np.max(raw):.6e}")
                            
                            # Resto del procesamiento como estaba
                            bridge_type = adv.get("SelectedRange", "")
                            gage_factor = float(adv.get("GageFactor", 2.0))
                            
                            # Usar la función específica para procesar strain
                            self.results[key] = self.process_strain_ni9219(
                                raw, offset_val, bridge_type, gage_factor
                            )
                            
                            # Mostrar resultado
                            print(f"Datos procesados min/max: {np.min(self.results[key]):.2f}/{np.max(self.results[key]):.2f}")
                            print(f"==== FIN PROCESAMIENTO ====\n")
                            
                        except Exception as e:
                            print(f"Error al procesar datos NI 9219 para {key}: {e}")
                            self.results[key] = raw  # Fallback
                    else:
                        self.results[key] = raw
                        print(f"Datos procesados para {key}: {len(raw)} puntos")
                        
                except Exception as e:
                    print(f"Error general al procesar datos para {key}: {e}")
                    # Intentar almacenar los datos crudos como última opción
                    try:
                        if not (key in self.results and len(self.results[key]) > 0):
                            self.results[key] = np.array(data_matrix[i])
                    except:
                        if not (key in self.results and len(self.results[key]) > 0):
                            self.results[key] = np.array([])
            
            # Verificar si hay datos almacenados
            data_count = sum(len(arr) for arr in self.results.values() if hasattr(arr, '__len__'))
            print(f"Total de datos almacenados: {data_count} puntos en {len(self.results)} canales")

    def export_data(self):
        """
        Exporta los datos de self.results a XLSX o MAT, según self.export_format.
        La exportación se realiza en un hilo separado para no bloquear la interfaz.
        Utiliza los nombres personalizados de los canales para las columnas de datos.
        """
        # Verificar que haya datos para exportar
        with self.data_lock:
            # Diagnóstico
            print(f"export_data: self.results tiene {len(self.results)} claves")
            valid_data_count = 0
            for k, v in self.results.items():
                if hasattr(v, 'size'):
                    # Es un array NumPy
                    print(f"  - {k}: array NumPy, shape={v.shape}, size={v.size}")
                    if v.size > 0:
                        valid_data_count += 1
                elif hasattr(v, '__len__'):
                    # Es una lista u otro iterable
                    print(f"  - {k}: {type(v)}, len={len(v)}")
                    if len(v) > 0:
                        valid_data_count += 1
                else:
                    # Otro tipo de dato
                    print(f"  - {k}: {type(v)}")
                    
            print(f"export_data: {valid_data_count} canales con datos válidos")
                    
            # Verificar si hay datos válidos para exportar
            valid_data = False
            for v in self.results.values():
                # Verificar si es un array NumPy no vacío
                if hasattr(v, 'size') and v.size > 0:
                    valid_data = True
                    break
                # O una lista u otro iterable no vacío
                elif hasattr(v, '__len__') and len(v) > 0:
                    valid_data = True
                    break
                    
            if not valid_data:
                print("export_data: self.results está vacío o no contiene datos válidos")
                
                # CORRECCIÓN: Verificar si hay datos en plot_buffers que puedan ser usados
                if self.plot_buffers:
                    print("Verificando datos en plot_buffers para exportación...")
                    for key, buffer in self.plot_buffers.items():
                        if buffer and len(buffer) > 0:
                            # Convertir buffer a array NumPy
                            try:
                                data = np.array(buffer, dtype=float)
                                if data.size > 0:
                                    # Buscar información del canal para procesamiento
                                    channel_info = None
                                    for dev, ch, ptype, adv, k in getattr(self, 'all_channels', []):
                                        if k == key:
                                            channel_info = (ptype, adv)
                                            break
                                            
                                    # Procesar si encontramos info
                                    if channel_info:
                                        ptype, adv = channel_info
                                        # Procesar según tipo
                                        if ptype == "NI 9219" and adv.get("SelectedMode", "") == "Strain":
                                            offset_val = float(adv.get("Offset", 0.0))
                                            bridge_type = adv.get("SelectedRange", "")
                                            gage_factor = float(adv.get("GageFactor", 2.0))
                                            self.results[key] = self.process_strain_ni9219(
                                                data, offset_val, bridge_type, gage_factor
                                            )
                                            valid_data = True
                                            print(f"Datos de {key} procesados para exportación: {len(self.results[key])} puntos")
                                        elif ptype == "NI 9237":
                                            gf = float(adv.get("GageFactor", 2.0))
                                            offset = float(adv.get("Offset", 0.0))
                                            self.results[key] = 4.0 * ((data - offset) * 1e6) / gf
                                            valid_data = True
                                            print(f"Datos de {key} procesados para exportación: {len(self.results[key])} puntos")
                                        else:
                                            self.results[key] = data
                                            valid_data = True
                                            print(f"Datos de {key} añadidos para exportación: {len(self.results[key])} puntos")
                                    else:
                                        # Usar datos crudos si no hay info
                                        self.results[key] = data
                                        valid_data = True
                                        print(f"Datos crudos de {key} añadidos para exportación: {len(self.results[key])} puntos")
                            except Exception as proc_error:
                                print(f"Error procesando datos de {key} para exportación: {proc_error}")
            
            # Verificar de nuevo después de procesar plot_buffers
            if not valid_data:
                messagebox.showerror("Exportar", "No hay datos para exportar.")
                return
                
            # Hacer una copia de los datos para el hilo de exportación
            results_copy = {}
            for k, v in self.results.items():
                if hasattr(v, 'copy'):
                    results_copy[k] = v.copy()
                else:
                    results_copy[k] = v
                
            # Obtener una copia de los nombres personalizados
            channel_names_copy = self.channel_names.copy()
        
        # Obtener el formato y el archivo destino
        fmt = self.export_format.get()
        ext = ".xlsx" if fmt == "xlsx" else ".mat"
        filename = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[(f"{fmt.upper()} files", f"*{ext}")]
        )
        if not filename:
            return
        
        # Actualizar estado
        self.status_var.set(f"Exportando datos a {fmt.upper()}...")
        self.root.update_idletasks()
        
        # Función para exportar en un hilo separado
        def export_thread_func(results_data, channel_names, file_name, format_type):
            try:
                if format_type == "mat":
                    # Para el formato MAT, usamos nombres personalizados como claves
                    renamed_results = {}
                    for key, data in results_data.items():
                        # Verificar que hay datos antes de exportar
                        if hasattr(data, 'size') and data.size == 0:
                            continue
                        elif hasattr(data, '__len__') and len(data) == 0:
                            continue
                            
                        # Asegurar que los datos sean arrays NumPy
                        if not isinstance(data, np.ndarray):
                            try:
                                data = np.array(data, dtype=float)
                            except:
                                print(f"No se pudo convertir {key} a array NumPy, omitiendo")
                                continue
                                
                        # Usar el nombre personalizado o el original si no existe
                        new_key = channel_names.get(key, key)
                        # Asegurar que el nombre es válido como clave en MATLAB
                        # (sin caracteres especiales, espacios convertidos a guiones bajos)
                        new_key = "".join(c if c.isalnum() else "_" for c in new_key)
                        renamed_results[new_key] = data
                    
                    if not renamed_results:
                        raise ValueError("No hay datos válidos para exportar")
                        
                    sio.savemat(file_name, renamed_results)
                else:  # xlsx
                    # Filtrar canales sin datos
                    keys = []
                    for k, v in results_data.items():
                        if hasattr(v, 'size') and v.size > 0:
                            keys.append(k)
                        elif hasattr(v, '__len__') and len(v) > 0:
                            keys.append(k)
                            
                    if not keys:
                        raise ValueError("No hay datos para exportar.")
                        
                    # Preparar datos para DataFrame con nombres personalizados
                    max_len = 0
                    data_dict = {}
                    
                    # Primero encontramos la longitud máxima
                    for k in keys:
                        data = results_data[k]
                        if not isinstance(data, np.ndarray):
                            try:
                                data = np.array(data, dtype=float)
                            except:
                                print(f"No se pudo convertir {k} a array NumPy, omitiendo")
                                continue
                                
                        arr = data.ravel()  # Aplanar el array
                        max_len = max(max_len, len(arr))
                    
                    # Creamos el diccionario con los nombres personalizados como claves
                    for k in keys:
                        data = results_data[k]
                        if not isinstance(data, np.ndarray):
                            try:
                                data = np.array(data, dtype=float)
                            except:
                                print(f"No se pudo convertir {k} a array NumPy, omitiendo")
                                continue
                                
                        arr = data.ravel()  # Aplanar el array
                        if len(arr) < max_len:
                            arr = np.pad(arr, (0, max_len - len(arr)), constant_values=np.nan)
                        
                        # Usar el nombre personalizado como clave en el DataFrame
                        column_name = channel_names.get(k, k)
                        data_dict[column_name] = arr
                    
                    # Crear DataFrame y exportar
                    df = pd.DataFrame(data_dict)
                    df.to_excel(file_name, index=False)
                
                # Actualizar UI en el hilo principal
                self.root.after_idle(lambda: self._update_export_status("Exportación completada", True, file_name))
            except Exception as export_error:
                # Mostrar error en el hilo principal
                error_str = str(export_error)
                print(f"Error en exportación: {error_str}")
                import traceback
                traceback.print_exc()
                self.root.after_idle(lambda msg=error_str: self._update_export_status(f"Error: {msg}", False))
        
        # Iniciar el hilo de exportación
        export_thread = threading.Thread(
            target=export_thread_func,
            args=(results_copy, channel_names_copy, filename, fmt),
            daemon=True
        )
        export_thread.start()
        
    def _update_export_status(self, message, success, filename=None):
        """Método auxiliar para actualizar la interfaz después de la exportación"""
        self.status_var.set(message)
        if success:
            messagebox.showinfo("Exportar", f"Datos exportados en {filename}")
        else:
            messagebox.showerror("Error de exportación", message)


###############################################################################
#                                Ejecución                                    #
###############################################################################
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x800")
    app = AcquisitionGUI(root)
    
    # Configurar cierre adecuado de la aplicación
    root.protocol("WM_DELETE_WINDOW", app.close_app)
    
    root.mainloop()