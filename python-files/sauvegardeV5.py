import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
from datetime import date
import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import matplotlib.gridspec as gridspec
import re

#paramètres généraux
PORT_BLUETOOTH = "COM5"
BAUDRATE = 9600
conn = pymysql.connect(host="localhost", user="root", password="", database="kine_db")
cursor = conn.cursor()

#fonction pour charger les informations de patients
def charger_patients():
    cursor.execute("SELECT id_patient, nom, prenom, age, pathologie FROM patient")
    return cursor.fetchall()

#fonction pour
def rafraichir_table():
    for row in tree.get_children():
        tree.delete(row)
    for patient in charger_patients():
        if search_var.get().lower() in f"{patient[1]} {patient[2]}".lower():
            tree.insert('', 'end', iid=patient[0], values=patient[1:])
#ajout d'un patient dans la BDD
def ajouter_patient():
    nom = entry_nom.get()
    prenom = entry_prenom.get()
    age = entry_age.get()
    patho = entry_patho.get()
    if not nom or not prenom or not age or not patho:
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
        return
    try: #essai d'insertion dans BDD
        age = int(age)
        cursor.execute("INSERT INTO patient (nom, prenom, age, pathologie, date_debut) VALUES (%s, %s, %s, %s, %s)",
                       (nom, prenom, age, patho, date.today()))
        conn.commit()
        messagebox.showinfo("Succès", "Patient ajouté.")
        rafraichir_table()
        entry_nom.delete(0, tk.END)
        entry_prenom.delete(0, tk.END)
        entry_age.delete(0, tk.END)
        entry_patho.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Erreur", "L'âge doit être un nombre.")


def selection_patient():
    selected = tree.selection()
    return selected[0] if selected else None
   

def affiche_graphe(pitch_vals, roll_vals, time_data):
    #calculs moyennes et ecarts_types
    mean_pitch = np.mean(pitch_vals)
    mean_roll = np.mean(roll_vals)
    std_pitch=np.std(pitch_vals)
    std_roll=np.std(roll_vals)

    #ouvre une fenêtre
    graph_window = plt.figure(constrained_layout=True, figsize=(14, 8))
    mng = plt.get_current_fig_manager()
    try: #essai ouverture fenêtre
        mng.window.state('zoomed')
    except AttributeError:
        try:
            mng.window.showMaximized()
        except AttributeError:
            pass

   
    spec = gridspec.GridSpec(ncols=2, nrows=2, figure=graph_window)
    ax_pos = graph_window.add_subplot(spec[0, 0])  #en haut à gauche
    ax_pitch = graph_window.add_subplot(spec[0, 1]) # en haut à droite
    ax_roll = graph_window.add_subplot(spec[1, 1])  # en bas à droite
    ax_mean = graph_window.add_subplot(spec[1, 0])  # en bas à gauche

    # Position sur plateau
    ax_pos.set_xlim(-22, 22)
    ax_pos.set_ylim(-22, 22)
    ax_pos.set_aspect('equal') #aspect carré
    ax_pos.set_title("Position sur le Plateau")
    ax_pos.set_xlabel("Roll (°)")
    ax_pos.set_ylabel("Pitch (°)")
    ax_pos.axhline(0, color='black', linewidth=0.8)
    ax_pos.axvline(0, color='black', linewidth=0.8)
    cercle = plt.Circle((0, 0), 22, color='black', fill=False)
    ax_pos.add_patch(cercle)
    ax_pos.plot(roll_vals, pitch_vals, color='blue', linestyle='-', label="Trajectoire")
    ax_pos.legend()

    # Pitch
    ax_pitch.plot(time_data, pitch_vals, label="Pitch (°)", color='orange')
    ax_pitch.set_title("Pitch en fonction du Temps")
    ax_pitch.set_xlabel("Temps (s)")
    ax_pitch.set_ylabel("Pitch (°)")
    ax_pitch.grid(True)

    # Roll
    ax_roll.plot(time_data, roll_vals, label="Roll (°)", color='green')
    ax_roll.set_title("Roll en fonction du Temps")
    ax_roll.set_xlabel("Temps (s)")
    ax_roll.set_ylabel("Roll (°)")
    ax_roll.grid(True)

    # Moyenne et écart-type
    ax_mean.set_xlim(-22, 22)
    ax_mean.set_ylim(-22, 22)
    ax_mean.set_aspect('equal')
    ax_mean.axhline(0, color='black', linewidth=1)
    ax_mean.axvline(0, color='black', linewidth=1)
    ax_mean.set_xlabel("Roll (°)")
    ax_mean.set_ylabel("Pitch (°)")
    ax_mean.set_title("Moyenne et Écart-type")

    ax_mean.scatter(mean_roll, mean_pitch, color='green', marker='o', s=100, label="Point moyen")

    theta = np.linspace(0, 2 * np.pi, 100)
    x = mean_roll + (std_roll / 2) * np.sin(theta)
    y = mean_pitch + (std_pitch / 2) * np.cos(theta)
    ax_mean.fill(x, y, color='green', alpha=0.3, label="Ecart-type")

    plateau_radius = 22
    plateau_circle = plt.Circle((0, 0), plateau_radius, color='orange', alpha=0.5, fill=False, linewidth=2, label="Bord du Plateau")
    ax_mean.add_patch(plateau_circle)

    bord_detecte = False
    for i in range(len(roll_vals)):
        distance = np.sqrt(roll_vals[i] ** 2 + pitch_vals[i] ** 2)
        if distance > plateau_radius:
            if not bord_detecte:
                ax_mean.scatter(roll_vals[i], pitch_vals[i], color='red', marker='x', s=100, label="Bord touché")
                bord_detecte = True
            else:
                ax_mean.scatter(roll_vals[i], pitch_vals[i], color='red', marker='x', s=100)

    ax_mean.legend(loc='upper right', bbox_to_anchor=(1.8, 1.3))
    ax_mean.grid()

    plt.show()


def lancer_session(id_patient, duree):
    try:
        ser = serial.Serial(PORT_BLUETOOTH, BAUDRATE, timeout=1)
        print(f"Connexion à {PORT_BLUETOOTH}")
        ser.write(f"{duree:03}".encode())
        print(f"Durée {duree} sec envoyée")
    except serial.SerialException as e:
        messagebox.showerror("Erreur", str(e))
        return

    # --- Création de la fenêtre Tkinter pour l'affichage graphique ---
    fenetre_graphique = tk.Toplevel(root)
    fenetre_graphique.title("Position Temps Réel")
    canvas = tk.Canvas(fenetre_graphique, width=500, height=500, bg='white')
    canvas.pack()

    # Timer visuel pour le patient
    timer_label = tk.Label(fenetre_graphique, text="0.0 s", font=("Helvetica", 14))
    timer_label.pack(pady=5)
    start_time = time.time()

    center_x, center_y = 250, 250
    plateau_radius = 22 * 10  # facteur d'échelle : 10 pixels par degré

    # Cercle du plateau
    canvas.create_oval(center_x - plateau_radius, center_y - plateau_radius,
                       center_x + plateau_radius, center_y + plateau_radius,
                       outline="black", width=2)

    # Axes
    canvas.create_line(center_x, 0, center_x, 500, fill="gray", dash=(4, 2))
    canvas.create_line(0, center_y, 500, center_y, fill="gray", dash=(4, 2))

    # Point bleu initial
    point = canvas.create_oval(center_x, center_y, center_x + 8, center_y + 8, fill="blue")

    # --- Données pour stockage ---
    trames = []
    time_data, pitch_data, roll_data = [], [], []

    while True:
        try:
            ligne = ser.readline().decode('utf-8').strip()
        except UnicodeDecodeError:
            ligne = ser.readline().decode('latin-1', errors='ignore').strip()
        if ligne:
            print(ligne)

        # Mise à jour du timer
        elapsed = time.time() - start_time
        timer_label.config(text=f"{elapsed:.1f} s")

        if "<END>" in ligne or elapsed >= duree:
            print("Fin de session.")
            break

        match = re.search(r"(-?\d+\.\d{2}),(-?\d+\.\d{2})", ligne)
        if match:
            roll, pitch = map(float, match.groups())
            roll += 7.02
            pitch += 4.5

            trames.append((len(trames) + 1, pitch, roll))
            time_data.append(elapsed)
            pitch_data.append(pitch)
            roll_data.append(roll)

            # Met à jour la position du point bleu
            scale = 10
            x = center_x + roll * scale
            y = center_y - pitch * scale
            canvas.coords(point, x - 5, y - 5, x + 5, y + 5)

        # Rafraîchit l'affichage
        fenetre_graphique.update_idletasks()
        fenetre_graphique.update()

    ser.close()

    if not trames:
        messagebox.showerror("Erreur", "Aucune donnée reçue.")
        return

    # Traitement & sauvegarde
    pitch_vals = np.array([t[1] for t in trames])
    roll_vals = np.array([t[2] for t in trames])
    mean_pitch = np.mean(pitch_vals)
    mean_roll = np.mean(roll_vals)
    std_pitch = np.std(pitch_vals)
    std_roll = np.std(roll_vals)

    valeurs = (mean_pitch, mean_roll, std_pitch, std_roll, id_patient, date.today())
    cursor.execute("""INSERT INTO session (mean_pitch, mean_roll, std_pitch, std_roll, id_patient, date_session) 
                      VALUES (%s, %s, %s, %s, %s, %s)""", valeurs)
    cursor.execute("SELECT LAST_INSERT_ID()")
    id_session = cursor.fetchone()[0]

    for i in range(len(pitch_vals)):
        cursor.execute("INSERT INTO session_data (id_session, pitch, roll) VALUES (%s, %s, %s)",
                       (id_session, pitch_vals[i], roll_vals[i]))

    conn.commit()

    messagebox.showinfo("Succès", "Données enregistrées avec succès !")
    affiche_graphe(pitch_vals, roll_vals, time_data)
   
   


def ouvrir_session_popup():
    pid = selection_patient()
    if not pid:
        return

    popup = tk.Toplevel(root)
    popup.title("Lancer une session")
    tk.Label(popup, text="Durée de session (en secondes)").pack()
    durees = [30,90, 120, 150, 180]
    duree_strs=["30s", "1m30", "2m00", "2m30", "3m00"]
    duree_var = tk.StringVar()
    ttk.Combobox(popup, values=["30s","1m30", "2m00", "2m30", "3m00"], textvariable=duree_var).pack()

    def valider_session():
        val = duree_var.get()
        if val not in ["30s","1m30", "2m00", "2m30", "3m00"]:
            messagebox.showerror("Erreur", "Durée invalide.")
            return
        duree_session = durees[duree_strs.index(duree_var.get())]
        popup.destroy()
        lancer_session(pid, duree_session)

    ttk.Button(popup, text="Valider", command=valider_session).pack()



def afficher_historique():
    pid = selection_patient()
    if not pid:
        return

    cursor.execute("SELECT id_session, mean_pitch, mean_roll, std_pitch, std_roll, date_session FROM session WHERE id_patient = %s ORDER BY id_session DESC", (pid,))
    sessions = cursor.fetchall()

    histo = tk.Toplevel(root)
    histo.title("Historique des sessions")
    ttk.Label(histo, text="Historique du patient").pack()

    tree_hist=ttk.Treeview(histo, columns=('id', 'pitch', 'roll', 'std_pitch', 'std_roll', 'date_session'), show='headings')
    for col, text in zip(('id', 'pitch', 'roll', 'std_pitch', 'std_roll', 'date_session'),
                     ('ID Session', 'Pitch moyen', 'Roll moyen', 'Écart-type Pitch', 'Écart-type Roll', 'Date de session')):
        tree_hist.heading(col, text=text)
    for s in sessions:
        tree_hist.insert('', 'end', values=s)
    tree_hist.pack(fill='both', expand=True)

    def afficher_graphique_selection():
        selected = tree_hist.selection()
        if not selected:
            messagebox.showerror("Erreur", "Veuillez sélectionner une session.")
            return
        session_id = tree_hist.item(selected[0])['values'][0]

        cursor.execute("SELECT pitch, roll FROM session_data WHERE id_session = %s", (session_id,))
        data = cursor.fetchall()
        if not data:
            messagebox.showerror("Erreur", "Aucune donnée enregistrée pour cette session.")
            return

        pitch_vals = np.array([d[0] for d in data])
        roll_vals = np.array([d[1] for d in data])
        time_data = np.linspace(0, len(data)*0.1, len(data))  
        affiche_graphe(pitch_vals, roll_vals, time_data)

    btns = ttk.Frame(histo)
    btns.pack(pady=5)
    ttk.Button(btns, text="Graphiques", command=afficher_graphique_selection).grid(row=0, column=0, padx=10)
    ttk.Button(btns, text="Retour", command=histo.destroy).grid(row=0, column=1, padx=10)


# --- Interface principale ---
root = tk.Tk()
root.title("Suivi Kiné")
root.geometry("900x600")

notebook = ttk.Notebook(root)
frame_liste = ttk.Frame(notebook)
frame_ajout = ttk.Frame(notebook)
notebook.add(frame_liste, text="Liste des Patients")
notebook.add(frame_ajout, text="Ajouter un Patient")
notebook.pack(expand=True, fill='both')

# Barre de recherche
search_var = tk.StringVar()
search_var.trace("w", lambda *args: rafraichir_table())
tk.Label(frame_liste, text="Rechercher un patient :").pack()
tk.Entry(frame_liste, textvariable=search_var).pack(fill='x', padx=10)

# Tableau des patients
cols = ('Nom', 'Prénom', 'Âge', 'Pathologie')
tree = ttk.Treeview(frame_liste, columns=cols, show='headings')
for col in cols:
    tree.heading(col, text=col)
tree.pack(expand=True, fill='both', padx=10, pady=5)

# Boutons
btn_frame = ttk.Frame(frame_liste)
btn_frame.pack(pady=10)
btn_hist = ttk.Button(btn_frame, text="Historique", command=afficher_historique)
btn_session = ttk.Button(btn_frame, text="Lancer une Session", command=ouvrir_session_popup)
btn_hist.grid(row=0, column=0, padx=10)
btn_session.grid(row=0, column=1, padx=10)

# Onglet Ajouter un patient
tk.Label(frame_ajout, text="Nom :").pack()
entry_nom = tk.Entry(frame_ajout)
entry_nom.pack()
tk.Label(frame_ajout, text="Prénom :").pack()
entry_prenom = tk.Entry(frame_ajout)
entry_prenom.pack()
tk.Label(frame_ajout, text="Âge :").pack()
entry_age = tk.Entry(frame_ajout)
entry_age.pack()
tk.Label(frame_ajout, text="Pathologie :").pack()
entry_patho = tk.Entry(frame_ajout)
entry_patho.pack()
tk.Button(frame_ajout, text="Ajouter", command=ajouter_patient).pack(pady=10)

# Chargement initial
rafraichir_table()
root.mainloop()
cursor.close()
conn.close()
 