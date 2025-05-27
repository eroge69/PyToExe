import tkinter as tk

def on_close():
    print("Fermeture detected ! ")
    
    global running
    running = False
    #fenetre.destroy()
    
# Créer la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Ma fenêtre")
fenetre.configure(bg="black")  # Fond rouge
fenetre.resizable = False

# Ajouter un message dans la fenêtre
message = tk.Label(fenetre, text="you have been hacked!", bg="black", fg="green", font=("Platino", 16))
message.pack(padx=20, pady=20)

fenetre.protocol("WM_DELETE_WINDOW", on_close)

running = True
def boucle():
    if running:
        print("en boucle")
        fenetre.after(1000, boucle)

boucle()

# Lancer la boucle principale
fenetre.mainloop()

