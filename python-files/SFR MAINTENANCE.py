# SFR MAINTENANCE FORMATION vFinal - Interface Python
import tkinter as tk
from tkinter import messagebox
import os
import webbrowser
import subprocess
import datetime
import pathlib
from PIL import Image, ImageTk
import sys
import sys

def resource_path(relative_path):
    """Utilise ce chemin même quand l'app est compilée avec PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
def resource_path(relative_path):
    """Permet de charger les fichiers même quand l'appli est en .exe (PyInstaller)"""
    try:
        base_path = sys._MEIPASS  # PyInstaller crée ce dossier temporaire
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

APP_TITLE = "Intelcia ITS Maintenance V1"

# --- Fonctions Utilitaires ---
def open_file(path):
    try:
        os.startfile(path)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier ou dossier : {e}")

def open_url(url):
    webbrowser.open(url)

def open_mail():
    webbrowser.open("mailto:servicedesk@sfr.com")

def open_avaya():
    try:
        subprocess.Popen("AvayaAgent.exe")
    except:
        messagebox.showinfo("Avaya", "Avaya Agent non disponible.")

# --- Composants Réutilisables ---
def clear():
    for widget in content.winfo_children():
        widget.destroy()

import customtkinter as ctk
ctk.set_appearance_mode("light")
# ctk.set_default_color_theme("red")  # ❌ À enlever ou remplacer

def make_button(master, text, command):
    return ctk.CTkButton(master, text=text, command=command,
                         corner_radius=30,
                         fg_color="#003366",
                         hover_color="#002244",
                         text_color="white",
                         font=("Segoe UI", 11, "bold"),
                         height=40, width=180)

# --- Tooltip ---
class Tooltip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 60
        y = self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("Segoe UI", 9))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

# --- Pages ---

def show_home():
    clear()
    try:
        # Chemin vers banner/banner.png (relatif et compatible EXE)
        img_path = resource_path(os.path.join("banner", "banner.png"))
        img = Image.open(img_path)
        img = img.resize((950, 350))  # Redimension si nécessaire
        tk_img = ImageTk.PhotoImage(img)
        img_label = tk.Label(content, image=tk_img, bg="white")
        img_label.image = tk_img  # Garde référence pour éviter le garbage collector
        img_label.pack(pady=20)
    except Exception as e:
        tk.Label(content, text=f"Erreur chargement de l’image d’accueil : {e}", fg="red").pack()



def launch_all_tools():
    try:
        open_url("https://itsm.private.sfr.com")
        open_url("https://confluence.jmsp.prod")
        open_mail()
        open_avaya()

        boost_win = tk.Toplevel()
        boost_win.title("Go Boost activé !")
        boost_win.geometry("300x120")
        boost_win.configure(bg="#87CEEB")
        boost_win.resizable(False, False)

        tk.Label(boost_win, text="🚀 Tous les outils SFR ont été lancés !",
                 font=("Segoe UI", 11, "bold"), fg="white", bg="#87CEEB").pack(pady=20)
        tk.Button(boost_win, text="OK", command=boost_win.destroy).pack(pady=5)

        boost_win.attributes("-topmost", True)
        boost_win.after(5000, boost_win.destroy)

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir un ou plusieurs outils : {e}")

def show_tools():
    clear()
    tools = [
        ("ITSM", lambda: open_url("https://itsm.private.sfr.com")),
        ("Confluence", lambda: open_url("https://confluence.jmsp.prod")),
        ("Outlook", open_mail),
        ("Avaya Agent", open_avaya),
        ("🚀 Go Boost !", launch_all_tools)
    ]
    for label, cmd in tools:
        make_button(content, label, cmd).pack(pady=6)

def show_prestataires():
    clear()
    prestataires = [
        ("Umbrella", lambda: open_url("https://login.umbrella.com")),
        ("Contrat CISCO", lambda: open_url("https://ccrc.cisco.com/ccwr/")),
        ("Imperva", lambda: open_url("https://www.imperva.com")),
        ("Certes Networks", lambda: open_url("https://www.certesnetworks.com")),
        ("HPE Networking", lambda: open_url("https://www.hpe.com/fr/fr/networking.html"))
    ]
    for label, cmd in prestataires:
        make_button(content, label, cmd).pack(pady=6)

def show_formations():
    clear()
    base_path = os.path.join(os.path.dirname(__file__), "formations")
    jours = [
        ("Jour 1", os.path.join(base_path, "J1", "J1 - Formation INTELCIA.pptx")),
        ("Jour 2", os.path.join(base_path, "J2", "Portail esupport.pptx")),
    ]
    for jour, path in jours:
        make_button(content, jour, lambda p=path: open_file(p)).pack(pady=6)

def show_formations():
    clear()
    base_path = os.path.join(os.path.dirname(__file__), "formations")

    # --- Formations J1, J2 ---
    jours = [
        ("Jour 1", os.path.join(base_path, "J1", "J1 - Formation INTELCIA.pptx")),
        ("Jour 2", os.path.join(base_path, "J2", "Portail esupport.pptx")),
    ]
    for jour, path in jours:
        make_button(content, jour, lambda p=path: open_file(p)).pack(pady=6)

    # --- Section Création de compte ITSM ---
    tk.Label(content, text="Création de compte ITSM", font=("Segoe UI", 12, "bold"), bg="#f7f7f9").pack(pady=20)

    compte_path = os.path.join(base_path, "creation compte")
    fichiers = [
        ("Création Compte ITSM & Extract", "202201_SUP_ITSM-Procédure-Création d'un compte eSupport-v1.5.docx"),
        ("Fichier à remplir (client)", "Demande acces au portail_V2.xlsm")
    ]

    for label, filename in fichiers:
        full_path = os.path.join(compte_path, filename)
        btn = make_button(content, label, lambda p=full_path: open_file(p))
        btn.pack(pady=6)

        if "Fichier à remplir" in label:
            Tooltip(btn, "Ce fichier doit impérativement être complété par le client et retourné.\n"
                         "Il est obligatoire d’y indiquer le numéro de contrat AS pour assurer le bon rattachement.")
def afficher_images_avec_navigation(dossier_nom):
    clear()
    dossier_path = os.path.join(os.path.dirname(__file__), "formations2", dossier_nom)
    images = []
    for filename in sorted(os.listdir(dossier_path)):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            images.append(os.path.join(dossier_path, filename))

    if not images:
        tk.Label(content, text="Aucune image trouvée dans ce dossier.", fg="red").pack()
        return

    img_label = tk.Label(content, bg="white")
    img_label.pack(pady=10)

    index = [0]

    def show_image(i):
        try:
            img = Image.open(images[i])
            img = img.resize((800, 600))
            tk_img = ImageTk.PhotoImage(img)
            img_label.config(image=tk_img)
            img_label.image = tk_img
        except Exception as e:
            tk.Label(content, text=f"Erreur image : {e}", fg="red").pack()

    def prev_image():
        if index[0] > 0:
            index[0] -= 1
            show_image(index[0])

    def next_image():
        if index[0] < len(images) - 1:
            index[0] += 1
            show_image(index[0])

    show_image(index[0])

    btn_frame = tk.Frame(content, bg="white")
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="← Précédent", command=prev_image).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Suivant →", command=next_image).pack(side="left", padx=10)
    tk.Button(btn_frame, text="↩ Revenir", command=show_procedures).pack(side="left", padx=20)

def show_procedures():
    clear()

    make_button(content, "CHU Grenoble", lambda: open_file(os.path.join("formations", "Procédure CHU Grenoble.docx"))).pack(pady=6)
    make_button(content, "RMA Boulanger", lambda: open_url("https://confluence-jmsp.private.sfr.com/pages/viewpage.action?pageId=185185989")).pack(pady=6)
    make_button(content, "Ipanema", lambda: open_file("Intervention Ipanema.pptx")).pack(pady=6)
    make_button(content, "Procédures Certes Network", lambda: open_file(os.path.join("formations", "procédurecertes.docx"))).pack(pady=6)
    def afficher_image_unique(image_path):
        clear()
        try:
            img = Image.open(image_path)
            img = img.resize((800, 600))
            tk_img = ImageTk.PhotoImage(img)
            label = tk.Label(content, image=tk_img, bg="white")
            label.image = tk_img  # garde une référence
            label.pack(pady=20)
        except Exception as e:
            tk.Label(content, text=f"Erreur affichage image : {e}", fg="red").pack()

    make_button(content, "Traitement DIC", lambda: afficher_images_avec_navigation("Traitement DIC")).pack(pady=6)
    make_button(content, "Traitement Sunspring", lambda: afficher_images_avec_navigation("Traitement Sunspring")).pack(
        pady=6)
    make_button(content, "Garantie Constructeur",
                lambda: afficher_images_avec_navigation("Garantie Constructeur")).pack(pady=6)
    make_button(content, "Astreinte", lambda: afficher_images_avec_navigation("Astreinte")).pack(pady=6)
    make_button(content, "Procédure Richardson",
                lambda: afficher_images_avec_navigation("Procédure Richardson")).pack(pady=6)
   # Contrat LSI en texte affiché dans la fenêtre
    def show_contrat_lsi():
        clear()
        tk.Label(content, text="Procédure Contrat LSI", font=("Segoe UI", 14, "bold"), bg="#f7f7f9").pack(pady=10)
        text = """Cas 1: Demande Garantie constructeur/RMA client Top list ou top client.
  - Ouvrir le ticket et rajouter dans la note du ticket #Traitement en best effort
  - Dispatcher le ticket au support N2 en fonction de la techno
  - Faire un mail d'information aux ADV, GCM, IC du client pour leur notifier l'ouverture de l'incident du client.

Cas 2: Demande de Garantie constructeur/RMA client LSI (Location d'équipement SFR au client)
  - Ouvrir le ticket et préciser dans la note du ticket qu'il s'agit du client LSI
  - Pas la peine de passer par Cisco pour une garantie constructeur
  - Dispatcher le ticket directement au support N2 en fonction de la techno

Cas 3: Demande Garantie constructeur/RMA si client n'est ni LSI ni Top list ou top client → appliquer la procédure habituelle
  - Ouvrir le ticket même si SN hors contrat ou n'existe pas dans AX
  - Envoyer mail au ADV avec en copie IC (Ingénieur Commercial) pour vérification du SN
  - Si le SN est sous garantie chez Cisco, alors vous pouvez passer la garantie constructeur en ouvrant une tâche RMA à affecter à l'équipe logistique avec les informations nécessaires.
    PS: S'assurer que SFR est bien revendeur de cette borne

Cas 4: Dans le cas échéant de tout le cas précédemment cité à savoir SN non reconnu chez SFR ou Cisco et garantie constructeur Cisco expirée
  - Faire un mail au client avec le Template de mail standard qu'on envoie au client pour ce genre de cas

Si d'autres informations en complément, vous pouvez les rajouter. Merci.
"""
        txt = tk.Text(content, wrap="word", bg="white", font=("Segoe UI", 10))
        txt.insert("1.0", text)
        txt.config(state="disabled")
        txt.pack(expand=True, fill="both", padx=20, pady=10)
        tk.Button(content, text="↩ Revenir", command=show_procedures).pack(pady=10)

    make_button(content, "Contrats LSI", show_contrat_lsi).pack(pady=6)
def show_technologies():
    clear()
    base_path = os.path.join(os.path.dirname(__file__), "formations")
    fichiers = [
        ("Catégorisation Sécurité-Réseau-UC", os.path.join(base_path, "Catégorisation - Sécurité - Réseau - UC.xlsx")),
        ("Lien Confluence", "https://confluence.jmsp.prod/pages/viewpage.action?spaceKey=RCT&title=Fichier+Referentiel+Maintenance+ICT")
    ]
    for label, path in fichiers:
        if path.endswith(".xlsx"):
            make_button(content, label, lambda p=path: open_file(p)).pack(pady=6)
        else:
            make_button(content, label, lambda url=path: open_url(url)).pack(pady=6)

def show_appui():
    clear()
    fichiers = [
        ("TOPLIST", os.path.join("formations", "TOP List 2025.xlsx")),
        ("Lien ARIANE TOPLIST", r"\\ariane\ariane_001\Echanges\Clients_ROC\TOP LIST"),
        ("Stock SFR STOREP", r"\\ariane\ariane_001\Echanges\Clients_ROC\Documentation Ncc\Maintenance - Stock NANO5 Ipanema")
    ]

    for label, path in fichiers:
        make_button(content, label, lambda p=path: open_file(p)).pack(pady=6)
# --- Lancement Interface ---
root = tk.Tk()

# Gestion licence
LICENSE_KEY = "SFR-MAINT-2025-UNIQUE-ITS"
INSTALL_DATE = datetime.datetime(2025, 4, 2)
VALIDITY_DAYS = 9
CONFIG_FILE = pathlib.Path.home() / ".sfr_license_valid"

def verify_license():
    if CONFIG_FILE.exists():
        return
    def validate():
        if entry.get() == LICENSE_KEY:
            today = datetime.datetime.now()
            days_elapsed = (today - INSTALL_DATE).days
            if days_elapsed > VALIDITY_DAYS:
                messagebox.showerror("Licence expirée", "Votre licence a expiré. Veuillez contacter le support.")
            else:
                CONFIG_FILE.touch()
                lic_win.destroy()
        else:
            messagebox.showerror("Clé invalide", "Veuillez entrer une licence valide.")
    lic_win = tk.Toplevel()
    lic_win.title("Activation Licence")
    lic_win.geometry("400x180")
    tk.Label(lic_win, text="Veuillez entrer votre clé de licence :", font=("Segoe UI", 10)).pack(pady=20)
    entry = tk.Entry(lic_win, width=40)
    entry.pack()
    tk.Button(lic_win, text="Valider", command=validate).pack(pady=10)
    lic_win.grab_set()

verify_license()

root.title(APP_TITLE)
root.geometry("1000x600")
root.configure(bg="#f0f1f5")

# Header
header = tk.Frame(root, bg="#ffffff")
header.pack(fill="x")

# Logo Intelcia à gauche
import sys

def resource_path(relative_path):
    """Récupère le chemin absolu du fichier, compatible .exe PyInstaller"""
    try:
        base_path = sys._MEIPASS  # quand packagé
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

##Fonction Réponse BOUTON Réponse AUTO
def open_reponse_auto():
    """Ouvre un document type pour réponse automatique (ex: .docx, .pdf, etc.)."""
    filepath = os.path.join("documents", "Reponse_Auto.docx")  # Chemin à adapter selon ton projet
    try:
        if sys.platform.startswith('darwin'):  # macOS
            subprocess.call(('open', filepath))
        elif os.name == 'nt':  # Windows
            os.startfile(filepath)
        elif os.name == 'posix':  # Linux
            subprocess.call(('xdg-open', filepath))
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")

# Chargement des images
intelcia_logo = Image.open(resource_path("logointelciaits.png")).resize((200, 100))
sfr_logo = Image.open(resource_path("Logo-SFR-Business.png")).resize((140, 70))
intelcia_img = ImageTk.PhotoImage(intelcia_logo)
intelcia_label = tk.Label(header, image=intelcia_img, bg="#ffffff")
intelcia_label.image = intelcia_img
intelcia_label.pack(side="left", padx=10, pady=5)


# Layout principal
content = tk.Frame(root, bg="#fdfdfd")
sidebar = tk.Frame(root, bg="#87CEEB", width=200)
sidebar.pack(fill="y", side="left")
content.pack(expand=True, fill="both", side="right")

# Navigation
# Message bas de menu
tk.Label(sidebar, text="Application Intelcia ITS Maintenance",
         font=("Segoe UI", 8), bg="#87CEEB", fg="white", justify="center").pack(side="bottom", pady=10)
make_button(sidebar, "Accueil", show_home).pack(pady=6, padx=10, fill="x")
make_button(sidebar, "Outils SFR", show_tools).pack(pady=6, padx=10, fill="x")
make_button(sidebar, "Formations", show_formations).pack(pady=6, padx=10, fill="x")
make_button(sidebar, "Procédures clients", show_procedures).pack(pady=6, padx=10, fill="x")
make_button(sidebar, "Technologies", show_technologies).pack(pady=6, padx=10, fill="x")
make_button(sidebar, "TOPLIST / Stock", show_appui).pack(pady=6, padx=10, fill="x")
make_button(sidebar, "Prestataires", show_prestataires).pack(pady=6, padx=10, fill="x")
make_button(sidebar, "Réponse Auto", open_reponse_auto).pack(pady=6, padx=10, fill="x")
make_button(sidebar, "Contact Développeur", lambda: open_url("mailto:arbimootez.trabelsi@intelcia.com")).pack(pady=6, padx=10, fill="x")

# Lancement page d'accueil
show_home()



root.mainloop()
