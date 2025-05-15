import tkinter as tk
from tkinter import messagebox
import sqlite3

# --- Gestion base SQLite ---

DB_NAME = "users.db"

def creer_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def creer_table_session():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session (
            id INTEGER PRIMARY KEY,
            username TEXT
        )
    ''')
    conn.commit()
    conn.close()

def inscrire_utilisateur(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # Nom déjà pris
    conn.close()
    return success

def verifier_connexion(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    utilisateur = cursor.fetchone()
    conn.close()
    return utilisateur is not None

def sauvegarder_session(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM session")  # on efface l'ancienne session
    cursor.execute("INSERT INTO session (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()

def recuperer_session():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM session LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def clear_session():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM session")
    conn.commit()
    conn.close()

# --- Variables globales ---

utilisateur = None  # utilisateur connecté
admins_autorises = {"Admin", "AdminAcc"}  # <-- Mets ici les noms autorisés pour l'admin

# --- Fonctions Admin ---

def clear_users():
    global utilisateur
    reponse = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer tous les utilisateurs ?")
    if reponse:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        conn.commit()
        conn.close()
        messagebox.showinfo("Succès", "Tous les utilisateurs ont été supprimés.")
        # Déconnexion forcée
        utilisateur = None
        clear_session()
        label_utilisateur.config(text="")
        bouton_deconnexion.pack_forget()
        bouton_connexion.pack(side="right", padx=5, pady=10)
        bouton_inscription.pack(side="right", padx=5, pady=10)
        aller_menu_principal()

def clear_user_by_name():
    global utilisateur
    nom_a_supprimer = entry_clear_user.get().strip()
    if not nom_a_supprimer or nom_a_supprimer == "Nom utilisateur à supprimer":
        messagebox.showwarning("Attention", "Veuillez saisir un nom d'utilisateur.")
        return

    if nom_a_supprimer == utilisateur:
        messagebox.showwarning("Attention", "Vous ne pouvez pas supprimer l'utilisateur actuellement connecté.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (nom_a_supprimer,))
    utilisateur_existe = cursor.fetchone()
    if utilisateur_existe:
        reponse = messagebox.askyesno("Confirmation", f"Supprimer l'utilisateur '{nom_a_supprimer}' ?")
        if reponse:
            cursor.execute("DELETE FROM users WHERE username = ?", (nom_a_supprimer,))
            conn.commit()
            messagebox.showinfo("Succès", f"Utilisateur '{nom_a_supprimer}' supprimé.")
            entry_clear_user.delete(0, tk.END)
    else:
        messagebox.showerror("Erreur", f"Aucun utilisateur nommé '{nom_a_supprimer}' trouvé.")
    conn.close()

# --- Navigation ---

def aller_menu_principal():
    fenetre.configure(bg="black")
    fenetre.title("Menu Application")
    barre_exterieure.configure(bg="black")
    barre_haute.configure(bg="white")
    cadre_gauche.configure(bg="white")
    label_admin.configure(bg="white", fg="black")
    bouton_connexion.configure(bg="white", fg="black")
    bouton_inscription.configure(bg="white", fg="black")
    label_admin.config(text="Admin Page")
    # Retirer les boutons admin s’ils sont présents
    try:
        bouton_clear_users.pack_forget()
        entry_clear_user.pack_forget()
        bouton_clear_user.pack_forget()
    except:
        pass
    if utilisateur:
        label_utilisateur.configure(text=f"Bienvenue, {utilisateur}", bg="white", fg="black")
    else:
        label_utilisateur.configure(text="", bg="white", fg="black")

def aller_admin():
    if utilisateur not in admins_autorises:
        messagebox.showerror("Accès refusé", "Vous n'êtes pas autorisé à accéder à la page Admin.")
        return

    fenetre.configure(bg="#333333")  # gris foncé
    fenetre.title("Admin Page")
    barre_exterieure.configure(bg="white")
    barre_haute.configure(bg="white")
    cadre_gauche.configure(bg="white")
    label_admin.configure(bg="white", fg="black")
    bouton_connexion.configure(bg="white", fg="black")
    bouton_inscription.configure(bg="white", fg="black")
    if utilisateur:
        label_utilisateur.configure(text=f"Bienvenue, {utilisateur}", bg="white", fg="black")

    global bouton_clear_users, entry_clear_user, bouton_clear_user

    try:
        bouton_clear_users.pack_forget()
        entry_clear_user.pack_forget()
        bouton_clear_user.pack_forget()
    except NameError:
        pass

    bouton_clear_users = tk.Button(barre_haute, text="Clear Users", command=clear_users, bg="#E53935", fg="white", cursor="hand2")
    bouton_clear_users.pack(side="left", padx=10, pady=10)

    entry_clear_user = tk.Entry(barre_haute)
    entry_clear_user.pack(side="left", padx=5, pady=10)
    entry_clear_user.insert(0, "Nom utilisateur à supprimer")
    entry_clear_user.config(fg="grey")

    def on_entry_click(event):
        if entry_clear_user.get() == "Nom utilisateur à supprimer":
            entry_clear_user.delete(0, "end")
            entry_clear_user.config(fg="black")

    def on_focusout(event):
        if entry_clear_user.get() == "":
            entry_clear_user.insert(0, "Nom utilisateur à supprimer")
            entry_clear_user.config(fg="grey")

    entry_clear_user.bind('<FocusIn>', on_entry_click)
    entry_clear_user.bind('<FocusOut>', on_focusout)

    bouton_clear_user = tk.Button(barre_haute, text="Clear User", command=clear_user_by_name, bg="#F4511E", fg="white", cursor="hand2")
    bouton_clear_user.pack(side="left", padx=5, pady=10)

# --- Connexion / Inscription ---

def connexion():
    def valider():
        global utilisateur
        nom = champ_nom.get()
        mdp = champ_mdp.get()

        if verifier_connexion(nom, mdp):
            utilisateur = nom
            sauvegarder_session(utilisateur)  # sauvegarde session ici
            label_utilisateur.config(text=f"Bienvenue, {utilisateur}")
            fenetre_connexion.destroy()
            bouton_deconnexion.pack(side="right", padx=5, pady=10)
            bouton_connexion.pack_forget()
            bouton_inscription.pack_forget()
        else:
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect")

    fenetre_connexion = tk.Toplevel(fenetre)
    fenetre_connexion.title("Connexion")
    fenetre_connexion.geometry("300x180")
    fenetre_connexion.configure(bg="white")

    tk.Label(fenetre_connexion, text="Nom d'utilisateur :", bg="white").pack(pady=5)
    champ_nom = tk.Entry(fenetre_connexion)
    champ_nom.pack()

    tk.Label(fenetre_connexion, text="Mot de passe :", bg="white").pack(pady=5)
    champ_mdp = tk.Entry(fenetre_connexion, show="*")
    champ_mdp.pack()

    tk.Button(fenetre_connexion, text="Se connecter", command=valider, bg="#4CAF50", fg="white").pack(pady=10)

def inscription():
    def valider():
        nom = champ_nom.get()
        mdp = champ_mdp.get()

        if inscrire_utilisateur(nom, mdp):
            messagebox.showinfo("Succès", "Inscription réussie !")
            fenetre_inscription.destroy()
        else:
            messagebox.showerror("Erreur", "Nom d'utilisateur déjà pris")

    fenetre_inscription = tk.Toplevel(fenetre)
    fenetre_inscription.title("Inscription")
    fenetre_inscription.geometry("300x200")
    fenetre_inscription.configure(bg="white")

    tk.Label(fenetre_inscription, text="Créer un nom d'utilisateur :", bg="white").pack(pady=5)
    champ_nom = tk.Entry(fenetre_inscription)
    champ_nom.pack()

    tk.Label(fenetre_inscription, text="Mot de passe :", bg="white").pack(pady=5)
    champ_mdp = tk.Entry(fenetre_inscription, show="*")
    champ_mdp.pack()

    tk.Button(fenetre_inscription, text="S'inscrire", command=valider, bg="#2196F3", fg="white").pack(pady=10)

def deconnexion():
    global utilisateur
    utilisateur = None
    clear_session()  # efface session ici
    label_utilisateur.config(text="")
    bouton_deconnexion.pack_forget()
    bouton_connexion.pack(side="right", padx=5, pady=10)
    bouton_inscription.pack(side="right", padx=5, pady=10)
    aller_menu_principal()

# --- Interface graphique ---

creer_table()
creer_table_session()

fenetre = tk.Tk()
fenetre.title("Menu Application")
fenetre.geometry("800x600")
fenetre.configure(bg="black")

# Barre extérieure (contour noir)
barre_exterieure = tk.Frame(fenetre, bg="black", height=54)
barre_exterieure.pack(side="top", fill="x")

# Bordure gauche blanche dans la barre
cadre_gauche = tk.Frame(barre_exterieure, bg="white", width=5, height=54)
cadre_gauche.pack(side="left", fill="y")

# Barre blanche en haut avec contour noir
barre_haute = tk.Frame(barre_exterieure, bg="white", height=54, bd=1, relief="solid")
barre_haute.pack(side="left", fill="x", expand=True)

# Label Admin Page cliquable
label_admin = tk.Label(barre_haute, text="Admin Page", bg="white", fg="black", cursor="hand2", font=("Arial", 14, "bold"))
label_admin.pack(side="left", padx=10)
label_admin.bind("<Button-1>", lambda e: aller_admin())

# Boutons Connexion / Inscription
bouton_connexion = tk.Button(barre_haute, text="Connexion", bg="white", fg="black", cursor="hand2", command=connexion)
bouton_connexion.pack(side="right", padx=5, pady=10)

bouton_inscription = tk.Button(barre_haute, text="Inscription", bg="white", fg="black", cursor="hand2", command=inscription)
bouton_inscription.pack(side="right", padx=5, pady=10)

# Label utilisateur en haut à droite
label_utilisateur = tk.Label(barre_haute, text="", bg="white", fg="black", font=("Arial", 12))
label_utilisateur.pack(side="right", padx=10)

# Bouton déconnexion (initialement caché)
bouton_deconnexion = tk.Button(barre_haute, text="Déconnexion", bg="white", fg="black", cursor="hand2", command=deconnexion)

# Chargement session au démarrage
utilisateur = recuperer_session()
if utilisateur:
    label_utilisateur.config(text=f"Bienvenue, {utilisateur}")
    bouton_deconnexion.pack(side="right", padx=5, pady=10)
    bouton_connexion.pack_forget()
    bouton_inscription.pack_forget()
else:
    utilisateur = None

aller_menu_principal()

fenetre.mainloop()
