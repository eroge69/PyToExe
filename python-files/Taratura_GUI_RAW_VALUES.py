import tkinter as tk
from tkinter import ttk, filedialog
import csv
import random
###
import can
import matplotlib.pyplot as plt
import time
import signal
import sys
import os
import numpy as np  # Import NumPy per varianza e media
from matplotlib.widgets import Button

#inizializza vairabili e array
array_valori = np.zeros((4,4), dtype=np.uint16)
array_valori_now = np.zeros(4, dtype=np.int16)


# Inizializzazione del bus CAN
bus = can.interface.Bus(channel=0, bustype='ixxat', bitrate=20000)

# Funzione richiamata quando viene premuto il tasto di calibrazione
def read_saved_values_channel(channel):
    print(channel)
    request_msg = can.Message(
        arbitration_id= int(ID_var.get(), 16),
        data=[0x2F, 0x00, 0x65, 0x01, channel, 0x00, 0x00, 0x00],
        is_extended_id=False
    )
    try:
        bus.send(request_msg)
        time.sleep(0.01)
    except:
        print("no line")
    response_msg_R = bus.recv(timeout=10.0)

    for row in range(4):
        if response_msg_R:
            value = ((response_msg_R.data[2*row] << 8) | response_msg_R.data[2*row+1])
            print(value)
        else:
            print("Nessuna risposta per Resistenza!")
        res_vars[channel][row].set(f"{value/100:.2f}")
        array_valori[channel][row] = value
        

# Funzione richiamata quando viene premuto il tasto di scrittura dati dal csv alla scheda
def write_to_board():
    print("WRITE TO BOARD")
    ok_count = 0
    for channel in range(4):
        for utilizzatore in range(4):
            request_msg = can.Message(arbitration_id=int(ID_var.get(), 16), data=[0x2F, 0x00, 0x65, 0x65, channel, utilizzatore, ((array_valori[channel][utilizzatore] >> 8) & 0xFF), (array_valori[channel][utilizzatore] & 0xFF)], is_extended_id=False )
            try:
                bus.send(request_msg)
                time.sleep(0.01)
            except:
                print("no line")
            response_msg_R = bus.recv(timeout=10.0)
            if response_msg_R:
                if (((array_valori[channel][utilizzatore] >> 8) & 0xFF) == response_msg_R.data[6] and (array_valori[channel][utilizzatore] & 0xFF) == response_msg_R.data[7]):# and  (array_valori[channel][utilizzatore] & 0xFF) == response_msg_R.data[2*utilizzatore+1]):
                    #print("Write OK for channel - row: ", channel , utilizzatore)
                    ok_count += 1
            else:
                print("Nessuna risposta per write_to_board!")
    if ok_count == 16:
        print("Write OK for all channels")

# Funzione richiamata quando viene premuto il tasto di scrittura dati nella flash del micro
def save_in_flash():
    print("SAVE IN FLASH")
    request_msg = can.Message(arbitration_id=int(ID_var.get(), 16), data=[0x2F, 0x00, 0x65, 0x66, 0x00, 0x00, 0x00, 0x00], is_extended_id=False )
    try:
        bus.send(request_msg)
    except:
        print("no line")

# RELE' STATUS button callback
rele_status = 0
def rele_change():
    global rele_status
    print("Change RELE'")
    if rele_status == 0:
        request_msg = can.Message(
            arbitration_id=int(ID_var.get(), 16),
            data=[0x2F, 0x00, 0x62, 0x01, 0x0F, 0x00, 0x00, 0x0F],
            is_extended_id=False
        )
        rele_status = 1
    else:
        request_msg = can.Message(
            arbitration_id=int(ID_var.get(), 16),
            data=[0x2F, 0x00, 0x62, 0x01, 0x00, 0x00, 0x00, 0x0F],
            is_extended_id=False
        )
        rele_status = 0
    bus.send(request_msg)
    bus.recv(timeout=1.0)

# Funzione per salvare i valori correnti in un file CSV
def save_csv():
    filename = filename_var.get()
    if not filename.endswith(".csv"):
        filename += ".csv"
    try:
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Ingresso 0", "Ingresso 1", "Ingresso 2", "Ingresso 3"])
            for row in range(4):
                row_data = []
                for col in range(4):
                    row_data.append(res_vars[col][row].get())
                writer.writerow(row_data)
        print(f"CSV salvato come {filename}")
    except Exception as e:
        print("Errore nel salvataggio del CSV:", e)

# Funzione per caricare i valori dal file CSV
def load_csv():
    filename = filedialog.askopenfilename(title="Seleziona file CSV", filetypes=[("CSV Files", "*.csv")])
    if not filename:
        return
    try:
        with open(filename, mode="r", newline="") as file:
            reader = csv.reader(file)
            header = next(reader)  # Scarta l'intestazione
            rows = list(reader)
            if len(rows) != 4:
                print("Errore: il file CSV deve contenere 4 righe di dati.")
                return
            for row in range(4):
                if len(rows[row]) != 4:
                    print(f"Errore: la riga {row} non contiene 4 valori.")
                    continue
                for col in range(4):
                    res_vars[col][row].set(rows[row][col])
                    array_valori[col][row] = int(round(float(rows[row][col]) * 100))
        print("CSV caricato con successo")
    except Exception as e:
        print("Errore nel caricamento del CSV:", e)

# Funzione placeholder per la Taratura (da definire)
# Questa funzione legge la resistenza e, in base al range di valore,
# inserisce il dato nel campo corrispondente per ogni canale.
def taratura():
    print("Funzione di Taratura chiamata")
    try:
        bus.send(request_msg_Resistenza)
    except:
        print("no line")
    response_msg_R = bus.recv(timeout=10.0)
    for col in range(4):
        if response_msg_R:
            value = ((response_msg_R.data[2*col] << 8) | response_msg_R.data[2*col+1])
            print(value)
        else:
            print("Nessuna risposta per Resistenza!")
            continue
        idx = 0 if value < 1500 else 1 if value < 4500 else 2 if value < 10000 else 3 if value < 25000 else 4 if value < 50000 else 0
        if idx > 0:
            res_vars[col][idx-1].set(f"{value/100:.2f}")
            array_valori[col][idx-1] = value

continuous_read_status = 0
def activate_continuous_read():
    global continuous_read_status
    continuous_read_status = 1 if continuous_read_status == 0 else 0


def refresh_now_values():
    global continuous_read_status
    if(continuous_read_status):
        try:
            bus.send(request_msg_Resistenza)
        except:
            print("no line")
        response_msg_R = bus.recv(timeout=10.0)
        for col in range(4):
            if response_msg_R:
                value = ((response_msg_R.data[2*col] << 8) | response_msg_R.data[2*col+1]) 
            else:
                print("Nessuna risposta per Resistenza!")
                continue
            idx =  1 if value < 3000 else 2 if value < 10000 else 3 if value < 30000 else 4
            if idx > 0: 
                print( value , array_valori[col][idx-1])
                now_vars[col].set(f"{float(value - int(array_valori[col][idx-1]))/100:.2f}")

    # Richiama la funzione dopo 1000 ms
    root.after(1000, refresh_now_values)


# Crea la finestra principale
root = tk.Tk()
root.title("GUI Calibrazione e Lettura Resistenza")

# Lista bidimensionale di StringVar per le caselle di resistenza (4 canali x 4 righe)
res_vars = [[tk.StringVar(value="0.00") for _ in range(4)] for _ in range(4)]
now_vars = [tk.StringVar(value="0.00") for _ in range(4)] 
# Valori di riferimento per ogni riga (fissi)
ref_values = [20, 66.5, 180, 324]

# --- FRAME PER I BOTTONI DI CALIBRAZIONE ---
calib_frame = tk.Frame(root)
calib_frame.grid(row=0, column=0, padx=10, pady=5)
for col in range(4):
    calib_button = tk.Button(calib_frame, text=f"Read Saved {col}", command=lambda c=col: read_saved_values_channel(c))
    calib_button.grid(row=0, column=col, padx=5, pady=5)

# --- FRAME PER LA TABELLA DEI VALORI ---
table_frame = tk.Frame(root)
table_frame.grid(row=1, column=0, padx=10, pady=10)

# Intestazione della tabella
ref_header = tk.Label(table_frame, text="Ref. Val.", font=("TkDefaultFont", 10, "bold"))
ref_header.grid(row=0, column=0, padx=5, pady=5)
for col in range(4):
    ch_header = tk.Label(table_frame, text=f"Channel {col}", font=("TkDefaultFont", 10, "bold"))
    ch_header.grid(row=0, column=col+1, padx=5, pady=5)
sep = ttk.Separator(table_frame, orient="horizontal")
sep.grid(row=1, column=0, columnspan=5, sticky="ew", padx=5)

# Righe di dati: per ciascuna riga vengono mostrati il ref value (in grassetto) e le entry dei canali
for i in range(4):
    data_row = 2 + i * 2  # Righe: 2, 4, 6, 8
    ref_label = tk.Label(table_frame, text=str(ref_values[i]), font=("TkDefaultFont", 10, "bold"))
    ref_label.grid(row=data_row, column=0, padx=5, pady=5)
    for col in range(4):
        entry = tk.Entry(table_frame, textvariable=res_vars[col][i], width=10, justify="center", state="readonly")
        entry.grid(row=data_row, column=col+1, padx=5, pady=5)
    sep = ttk.Separator(table_frame, orient="horizontal")
    sep.grid(row=data_row+1, column=0, columnspan=5, sticky="ew", padx=5)
#aggiungi riga per i valori letti istantaneamente
data_row = 10 # Righe: 10
ref_label = tk.Label(table_frame, text="Delta now", font=("TkDefaultFont", 10, "bold"))
ref_label.grid(row=data_row, column=0, padx=5, pady=5)
for col in range(4):
    entry = tk.Entry(table_frame, textvariable=now_vars[col], width=10, justify="center", state="readonly")
    entry.grid(row=data_row, column=col+1, padx=5, pady=5)
sep = ttk.Separator(table_frame, orient="horizontal")
sep.grid(row=data_row+1, column=0, columnspan=5, sticky="ew", padx=5)


# --- FRAME PER LA SEZIONE CSV E TARATURA ---
csv_frame = tk.Frame(root)
csv_frame.grid(row=2, column=0, padx=10, pady=10)

# Campo per il nome del file
filename_label = tk.Label(csv_frame, text="Nome file:")
filename_label.grid(row=0, column=0, padx=5, pady=5)
filename_var = tk.StringVar(value="dati")
filename_entry = tk.Entry(csv_frame, textvariable=filename_var, width=20)
filename_entry.grid(row=0, column=1, padx=5, pady=5)

# Bottone per attivare/disattivare la lettura della resistenza ogni secondo
save_button = tk.Button(csv_frame, text="Continuous Read", command=activate_continuous_read)
save_button.grid(row=0, column=3, columnspan=2, padx=5, pady=5)

# Bottone per salvare il CSV
save_button = tk.Button(csv_frame, text="Salva CSV", command=save_csv)
save_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
# Bottone per caricare il CSV

load_button = tk.Button(csv_frame, text="Carica CSV", command=load_csv)
load_button.grid(row=1, column=2, columnspan=2, padx=5, pady=5)

rele_button = tk.Button(csv_frame, text="RELE", command=rele_change)
rele_button.grid(row=1, column=4, columnspan=2, padx=5, pady=5)

# Bottone per la taratura
taratura_button = tk.Button(csv_frame, text="Refresh Channels", command=taratura)
taratura_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Bottone per la taratura
write_to_board_button = tk.Button(csv_frame, text="Write CSV to Board", command=write_to_board)
write_to_board_button.grid(row=2, column=2, columnspan=2, padx=5, pady=5)

# Bottone per salvare in FLASH
write_to_board_button = tk.Button(csv_frame, text="SAVE IN FLASH", command=save_in_flash)
write_to_board_button.grid(row=2, column=4, columnspan=2, padx=5, pady=5)

# Campo per la configurazione da mandare alla scheda
config_label = tk.Label(csv_frame, text="Config:")
config_label.grid(row=3, column=0, padx=5, pady=5)
config_var = tk.StringVar(value="2F 00 63 01 08 04 02 01")
config_entry = tk.Entry(csv_frame, textvariable=config_var, width=20)
config_entry.grid(row=3, column=1, padx=5, pady=5)
# Bottone per mandare la configurazione alla scheda
def send_config():
    data = [int(x, 16) for x in config_var.get().split()]
    request_msg = can.Message(arbitration_id=int(ID_var.get(), 16), data=data, is_extended_id=False)
    print(request_msg)
    try:
        bus.send(request_msg)
    except:
        print("no line")
    response_msg = bus.recv(timeout=10.0)
    if response_msg:
        print(response_msg)
send_config_button = tk.Button(csv_frame, text="SEND CONFIG", command=send_config)
send_config_button.grid(row=3, column=2, columnspan=2, padx=5, pady=5)

# Campo per L'ID della scheda
ID_label = tk.Label(csv_frame, text="CAN ID (hex):")
ID_label.grid(row=4, column=0, padx=5, pady=5)
ID_var = tk.StringVar(value="601")
ID_entry = tk.Entry(csv_frame, textvariable=ID_var, width=20)
ID_entry.grid(row=4, column=1, padx=5, pady=5)

#print(ID_var.get(),int(ID_var.get(), 16))

# Messaggi di richiesta per corrente e resistenza
request_msg_mA = can.Message(
    arbitration_id=int(ID_var.get(), 16),
    data=[0x01, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    is_extended_id=False
)
request_msg_mV = can.Message(
    arbitration_id=int(ID_var.get(), 16),
    data=[0x01, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    is_extended_id=False
)
request_msg_Resistenza = can.Message(
    arbitration_id=int(ID_var.get(), 16),
    data=[0x2F, 0x00, 0x65, 0x00, 0x00, 0x00, 0x00, 0x00],
    is_extended_id=False
)

# Avvia l'aggiornamento periodico dei valori NOW
refresh_now_values()

root.mainloop()
