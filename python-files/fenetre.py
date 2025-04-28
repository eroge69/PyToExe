import tkinter as tk
from tkinter import filedialog
import pandas as pd

# Variable globale pour stocker le chemin du fichier
chemin_fichier = ""

def choisir_fichier():
    global chemin_fichier
    # Filtre uniquement les fichiers Excel
    chemin_fichier = filedialog.askopenfilename(
        title="Sélectionner un fichier Excel",
        filetypes=[("Fichiers Excel", "*.xlsx *.xls")]
    )
    
    if chemin_fichier:
        print("Fichier Excel sélectionné :", chemin_fichier)
        label_resultat.config(text=f"Fichier Excel sélectionné :\n{chemin_fichier}")

        # Lecture du fichier Excel avec pandas
        try:
            df = pd.read_excel(chemin_fichier)
            print("\nContenu du fichier Excel (aperçu) :")
            print(df.head())  # Affiche les 5 premières lignes dans la console
        except Exception as e:
            print("Erreur lors de l'ouverture du fichier Excel :", e)
            label_resultat.config(text="Erreur lors de la lecture du fichier.")
    else:
        print("Aucun fichier sélectionné.")
        label_resultat.config(text="Aucun fichier sélectionné.")

# Création de la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Sélecteur de fichier Excel")
fenetre.geometry("500x200")

# Bouton de sélection
bouton = tk.Button(fenetre, text="Choisir un fichier Excel", command=choisir_fichier)
bouton.pack(pady=20)

# Zone de texte pour afficher le chemin
label_resultat = tk.Label(fenetre, text="", wraplength=480, justify="left")
label_resultat.pack(pady=10)

# Lancement de l'interface
fenetre.mainloop()
