import tkinter as tk  # Uvoz GUI biblioteke

# Kreiramo glavni prozor
prozor = tk.Tk()
prozor.title("Moj prvi prozor")
prozor.geometry("300x200")  # širina x visina

# Funkcija koja se poziva kad se klikne dugme
def prikazi_poruku():
    labela.config(text="Zdravo, svete!")

# Tekst koji će se prikazati
labela = tk.Label(prozor, text="Klikni dugme ispod:")
labela.pack(pady=10)

# Dugme koje poziva funkciju
dugme = tk.Button(prozor, text="Klikni me", command=prikazi_poruku)
dugme.pack(pady=10)

# Pokreće aplikaciju
prozor.mainloop()