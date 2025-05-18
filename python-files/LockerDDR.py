import tkinter as tk
import winsound

# Jouer un son d'alerte (son système Windows)
winsound.MessageBeep()

# Création de la fenêtre
fenetre = tk.Tk()
fenetre.title("Système de sécurité")
fenetre.attributes("-fullscreen", True)
fenetre.configure(bg="darkred")

# Texte
message = tk.Label(fenetre, text="⚠️  Système bloqué !\nContactez l'administrateur.",
                   font=("Arial", 36, "bold"), fg="white", bg="darkred")
message.pack(expand=True)

# Bouton inactif
bouton = tk.Button(fenetre, text="Réparer", font=("Arial", 20), state="disabled")
bouton.pack(pady=50)

# Empêche la fermeture avec la croix
fenetre.protocol("WM_DELETE_WINDOW", lambda: None)

fenetre.mainloop()
