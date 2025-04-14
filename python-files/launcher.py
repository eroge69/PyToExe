import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import json
import os
import sys

# Elrejtett hely (AppData) a szerverek és MTA:SA elérési út mentéséhez
app_data_path = os.path.join(os.getenv("APPDATA"), "MTA_SA_Server_Connect")

# MTA:SA elérési útvonal (kezdésként üres, ezt a felhasználó választhatja ki)
mta_path = ""

# Szerverek fájl neve és MTA:SA elérési út fájl
servers_file = os.path.join(app_data_path, "servers.json")
mta_path_file = os.path.join(app_data_path, "mta_path.txt")

# Szerver adatokat tároló lista
servers = []

def load_servers():
    """Betölti a mentett szervereket, ha létezik a fájl."""
    global servers
    if os.path.exists(servers_file):
        try:
            with open(servers_file, "r") as file:
                servers = json.load(file)
                # Töltse be a szervereket a listába
                for server in servers:
                    listbox_servers.insert(tk.END, f"{server['name']} ({server['ip']}:{server['port']})")
        except Exception as e:
            print(f"Probléma a szerverek betöltésekor: {str(e)}")

def save_servers():
    """Elmenti a szervereket a fájlba."""
    try:
        if not os.path.exists(app_data_path):
            os.makedirs(app_data_path)
        with open(servers_file, "w") as file:
            json.dump(servers, file)
    except Exception as e:
        print(f"Probléma a szerverek mentésekor: {str(e)}")

def load_mta_path():
    """Betölti az MTA:SA elérési útját, ha létezik a fájl."""
    global mta_path
    if os.path.exists(mta_path_file):
        try:
            with open(mta_path_file, "r") as file:
                mta_path = file.read().strip()
        except Exception as e:
            print(f"Probléma az MTA:SA elérési út betöltésekor: {str(e)}")

def save_mta_path():
    """Elmenti az MTA:SA elérési útját."""
    try:
        if not os.path.exists(app_data_path):
            os.makedirs(app_data_path)
        with open(mta_path_file, "w") as file:
            file.write(mta_path)
    except Exception as e:
        print(f"Probléma az MTA:SA elérési út mentésekor: {str(e)}")

def select_mta_path():
    """Fájlválasztó ablakot nyit, ahol a felhasználó kiválaszthatja az MTA:SA elérési útját."""
    global mta_path
    mta_path = filedialog.askopenfilename(title="Válaszd ki az MTA:SA elérési útját",
                                          filetypes=[("Executable Files", "*.exe")])
    if mta_path:
        save_mta_path()
        messagebox.showinfo("MTA:SA elérési út", f"Az MTA:SA elérési útja beállítva: {mta_path}")
    else:
        messagebox.showwarning("Figyelem", "Nem választottál ki fájlt. Az alkalmazás nem fog működni.")

def add_server():
    """Hozzáad egy új szervert a listához."""
    name = entry_name.get()
    ip = entry_ip.get()
    port = entry_port.get()

    if not name or not ip or not port:
        messagebox.showerror("Hiba", "Minden mezőt ki kell tölteni!")
        return
    
    servers.append({"name": name, "ip": ip, "port": port})
    listbox_servers.insert(tk.END, f"{name} ({ip}:{port})")

def delete_server():
    """Kiválasztott szerver törlése."""
    try:
        selection = listbox_servers.curselection()
        if not selection:
            messagebox.showerror("Hiba", "Válassz ki egy szervert a törléshez!")
            return
        
        # A törölni kívánt szerver indexének megszerzése
        server_index = selection[0]
        del servers[server_index]

        # A listbox frissítése
        listbox_servers.delete(server_index)

        # A szerverek újra mentése
        save_servers()

    except Exception as e:
        messagebox.showerror("Hiba", f"Probléma történt a szerver törlésekor: {str(e)}")

def connect_to_server():
    """Kiválasztott szerverhez csatlakozás."""
    try:
        if not mta_path:
            messagebox.showerror("Hiba", "Az MTA:SA elérési útját még nem választottad ki!")
            return

        selection = listbox_servers.curselection()
        if not selection:
            messagebox.showerror("Hiba", "Válassz ki egy szervert!")
            return
        
        server = servers[selection[0]]
        ip = server['ip']
        port = server['port']

        # A mtasa:// URL formátumot használjuk a csatlakozáshoz
        connection_url = f"mtasa://{ip}:{port}"

        # MTA:SA elindítása a megfelelő URL-lel
        subprocess.Popen([mta_path, connection_url])

        # Szerverek mentése
        save_servers()

        # Alkalmazás bezárása
        root.quit()
        root.destroy()

    except Exception as e:
        messagebox.showerror("Hiba", f"Probléma történt: {str(e)}")

# Alkalmazás ablak létrehozása
root = tk.Tk()
root.title("MTA:SA Szerver Kapcsoló")

# Szerver adatokat tartalmazó form
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

label_name = tk.Label(frame_input, text="Szerver neve:")
label_name.grid(row=0, column=0, padx=5, pady=5)
entry_name = tk.Entry(frame_input)
entry_name.grid(row=0, column=1, padx=5, pady=5)

label_ip = tk.Label(frame_input, text="IP cím:")
label_ip.grid(row=1, column=0, padx=5, pady=5)
entry_ip = tk.Entry(frame_input)
entry_ip.grid(row=1, column=1, padx=5, pady=5)

label_port = tk.Label(frame_input, text="Port:")
label_port.grid(row=2, column=0, padx=5, pady=5)
entry_port = tk.Entry(frame_input)
entry_port.grid(row=2, column=1, padx=5, pady=5)

button_add = tk.Button(frame_input, text="Szerver hozzáadása", command=add_server)
button_add.grid(row=3, column=0, columnspan=2, pady=10)

# Lista a szerverek kijelzésére
frame_list = tk.Frame(root)
frame_list.pack(pady=10)

label_servers = tk.Label(frame_list, text="Elérhető szerverek:")
label_servers.pack()

listbox_servers = tk.Listbox(frame_list, height=6, width=30)
listbox_servers.pack()

# Csatlakozás gomb
button_connect = tk.Button(root, text="Csatlakozás", command=connect_to_server)
button_connect.pack(pady=10)

# Törlés gomb
button_delete = tk.Button(root, text="Szerver törlése", command=delete_server)
button_delete.pack(pady=10)

# MTA:SA elérési út beállítása gomb
button_select_mta = tk.Button(root, text="MTA:SA elérési út kiválasztása", command=select_mta_path)
button_select_mta.pack(pady=10)

# Betöltjük az MTA:SA elérési utat és a szervereket indításkor
load_mta_path()
load_servers()

# Fő ciklus indítása
root.mainloop()
