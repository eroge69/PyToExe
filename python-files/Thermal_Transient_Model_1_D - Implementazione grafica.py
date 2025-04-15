# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 14:21:37 2025

@author: afatigati
"""

"""FUNZIONE MODELLO TERMICO 1-D, DUE STRATI MATERIALE"""

import numpy as np
import matplotlib.pyplot as plt

""" IMPLEMENTAZIONE INTERFACCIA GRAFICA """
import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def transient_heat_transfer_2layers_convection_adiabatic(k1, k2, S1, S2, T_ext, h_ext, rho1, rho2, cp1, cp2, T0, t_finale):
    """
    Simula il trasferimento di calore transitorio in un sistema a due strati con:
    - Carico termico esterno convettivo.
    - Due materiali diversi per gli strati.
    - Strato più interno adiabatico.
    
    Metodo alle differenze finite

    Args:
        k1 (float): Conducibilità termica del primo strato [W/mK].
        k2 (float): Conducibilità termica del secondo strato [W/mK].
        S1 (float): Spessore del primo strato [m].
        S2 (float): Spessore del secondo strato [m].
        T_ext (float): Temperatura del flusso [°C].
        h_ext (float): Coefficiente di scambio termico convettivo esterno [W/m^2K].
        rho1 (float): Densità del primo strato [kg/m^3].
        rho2 (float): Densità del secondo strato [kg/m^3].
        cp1 (float): Calore specifico del primo strato [J/kgK].
        cp2 (float): Calore specifico del secondo strato [J/kgK].
        T0 (float): Temperatura iniziale dell'intero dominio [°C].
        t_finale (float): Durata dell'applicazione del flusso [s].

    Returns:
        tuple: Una tupla contenente max_temp, max_heat_flux e i tre grafici.
    """

    # Discretizzazione spaziale e temporale
    nx = 500  # Numero di punti nello spessore
    dx = (S1 + S2) / (nx - 1)  # Passo spaziale

    # Calcolo numeri di Fourier per controllo stabilità soluzione
    dt1 = 0.5 * (rho1 * cp1 * dx**2) / k1
    dt2 = 0.5 * (rho2 * cp2 * dx**2) / k2
    dt = min(dt1, dt2)

    # Creazione degli array per la temperatura
    T = np.ones(nx) * T0  # Inizializzazione con la temperatura iniziale

    # Liste per memorizzare le temperature massime e i flussi termici
    temp_max = []
    heat_flux = []

    # Ciclo temporale
    for t in range(0, int(t_finale / dt)):
        # Calcolo del flusso termico per conduzione
        q_cond = np.zeros(nx)
        for i in range(1, nx - 1):
            if i * dx <= S1:
                q_cond[i] = -k1 * (T[i + 1] - T[i - 1]) / (2 * dx)
            else:
                q_cond[i] = -k2 * (T[i + 1] - T[i - 1]) / (2 * dx)

        # Condizioni al contorno
        q_cond[0] = h_ext * (T_ext - T[1])
        q_cond[nx - 1] = 0  # Flusso termico nullo

        # Calcolo della variazione di temperatura
        dT_dt = np.zeros(nx)
        for i in range(1, nx - 1):
            if i * dx <= S1 and i <= 2:
                dT_dt[i] = (q_cond[i - 1] - q_cond[i + 1]) / (rho1 * cp1 * 2 * dx)
            elif i * dx <= S1:
                dT_dt[i] = (q_cond[i - 1] - q_cond[i + 1]) / (rho1 * cp1 * 2 * dx)
            else:
                dT_dt[i] = (q_cond[i - 1] - q_cond[i + 1]) / (rho2 * cp2 * 2 * dx)
        dT_dt[0] = (q_cond[0] - q_cond[1]) / (rho1 * cp1 * dx)

        # Aggiornamento della temperatura
        T[1:nx - 1] = T[1:nx - 1] + dT_dt[1:nx - 1] * dt

        temp_max.append(T[1])
        heat_flux.append(h_ext * (T_ext - T[1]))

    if len(temp_max) != len(np.arange(0, t_finale, dt)):
        temp_max.append(T[1])
        heat_flux.append(h_ext * (T_ext - T[1]))

    # Calcolo dei valori massimi
    max_temp = max(temp_max)
    max_heat_flux = max(heat_flux)

    # Restituisci i dati dei grafici
    return max_temp, max_heat_flux, temp_max, heat_flux, T, nx, dx, dt

def crea_grafici(temp_max, heat_flux, T, nx, dx, dt, t_finale, S1, S2):
    """
    Crea e visualizza i grafici.
    """
    # Crea le figure e gli assi di matplotlib
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    fig3, ax3 = plt.subplots()

    # Genera i dati dei grafici
    ax1.plot(np.arange(0, t_finale, dt), temp_max)
    ax1.set_xlabel("Tempo (s)")
    ax1.set_ylabel("Temperatura massima (°C)")
    ax1.set_title("Andamento della temperatura massima nel tempo")
    ax1.grid(True)

    ax2.plot(np.linspace(0, S1 + S2, nx), T)
    ax2.set_xlabel("Spessore (m)")
    ax2.set_ylabel("Temperatura (°C)")
    ax2.set_title("Andamento della temperatura all'istante finale")
    ax2.grid(True)

    # Crea i canvas di Tkinter per i grafici
    canvas1 = FigureCanvasTkAgg(fig1, master=content_frame)
    canvas2 = FigureCanvasTkAgg(fig2, master=content_frame)

    # Posiziona i canvas nella finestra usando grid
    canvas1.get_tk_widget().grid(row=0, column=2, rowspan=7, padx=10, pady=10)  # Usa grid
    canvas2.get_tk_widget().grid(row=7, column=2, rowspan=7, padx=10, pady=10)  # Usa grid


def run_simulation():
    """
    Funzione per eseguire la simulazione e aggiornare l'interfaccia.
    """
    try:
        # Recupera i valori dai campi di input
        k1 = float(entries[0].get())  # entry_k1
        k2 = float(entries[1].get())  # entry_k2
        S1 = float(entries[2].get())  # entry_S1
        S2 = float(entries[3].get())  # entry_S2
        T_ext = float(entries[4].get())  # entry_T_ext
        h_ext = float(entries[5].get())  # entry_h_ext
        rho1 = float(entries[6].get())  # entry_rho1
        rho2 = float(entries[7].get())  # entry_rho2
        cp1 = float(entries[8].get())  # entry_cp1
        cp2 = float(entries[9].get())  # entry_cp2
        T0 = float(entries[10].get())  # entry_T0
        t_finale = float(entries[11].get())  # entry_t_finale

        # Esegue la simulazione
        max_temp, max_heat_flux, temp_max, heat_flux, T, nx, dx, dt = transient_heat_transfer_2layers_convection_adiabatic(k1, k2, S1, S2, T_ext, h_ext, rho1, rho2, cp1, cp2, T0, t_finale)

        # Aggiorna le etichette di output
        label_max_temp_result.config(text=f"{max_temp:.2f} °C")
        label_max_heat_flux_result.config(text=f"{max_heat_flux:.2f} W/m^2")

        # Crea i grafici
        crea_grafici(temp_max, heat_flux, T, nx, dx, dt, t_finale, S1, S2)  # Passa i dati necessari

    except ValueError:
        # Gestione degli errori di input
        tk.messagebox.showerror("Errore", "Inserisci valori numerici validi.")

# Crea la finestra principale
root = tk.Tk()
root.title("1-D Transient Heat Transfer Exteem - 2 layers")

# Crea un frame principale
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Crea un canvas per il contenuto
canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Crea una barra di scorrimento verticale
scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configura il canvas per utilizzare la barra di scorrimento
canvas.configure(yscrollcommand=scrollbar.set)

# Crea un frame interno per il contenuto e lo posiziona nel canvas
content_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)

# Crea le etichette e i campi di input per i parametri nel frame interno (USA SOLO GRID)
labels = ["k1 [W/m°C]", "k2 [W/m°C]", "S1 [m]", "S2 [m]", "T_ext [°C]", 
          "h_ext [W/m2°C]", "rho1 [kg/m3]", "rho2 [kg/m3]", 
          "cp1 [J/kg°C]", "cp2 [J/kg°C]", "T0 [°C]", "t_finale [s]"]
entries = []
for i, label_text in enumerate(labels):
    label = tk.Label(content_frame, text=label_text)
    label.grid(row=i, column=0, padx=5, pady=5)
    entry = tk.Entry(content_frame)
    entry.grid(row=i, column=1, padx=5, pady=5)
    entries.append(entry)

# Crea il pulsante per eseguire la simulazione nel frame interno (USA SOLO GRID)
button_run = tk.Button(content_frame, text="Esegui Simulazione", command=run_simulation)
button_run.grid(row=len(labels), column=0, columnspan=2, pady=10)

# Crea le etichette per i risultati nel frame interno (USA SOLO GRID)
label_max_temp = tk.Label(content_frame, text="Massima temperatura:")
label_max_temp.grid(row=len(labels) + 1, column=0, padx=5, pady=5)
label_max_temp_result = tk.Label(content_frame, text="")
label_max_temp_result.grid(row=len(labels) + 1, column=1, padx=5, pady=5)

label_max_heat_flux = tk.Label(content_frame, text="Massimo flusso termico:")
label_max_heat_flux.grid(row=len(labels) + 2, column=0, padx=5, pady=5)
label_max_heat_flux_result = tk.Label(content_frame, text="")
label_max_heat_flux_result.grid(row=len(labels) + 2, column=1, padx=5, pady=5)

# Aggiorna la regione di scorrimento del canvas
content_frame.update_idletasks()
canvas.configure(scrollregion=canvas.bbox(tk.ALL))

# Avvia il loop principale di Tkinter
root.mainloop()