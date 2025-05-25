
import tkinter as tk

HASLO_POPRAWNE = "Arsii_unlock"

def pokaz_okno(index=1):
    okno = tk.Tk()
    okno.title(f"Okno nr {index}")
    okno.geometry("600x300")
    okno.configure(bg="black")
    okno.attributes("-topmost", True)

    # Blokuj zamykanie przez [X] oraz Alt+F4
    def blokuj_zamykanie():
        pass  # Nie rób nic — nie pozwól zamknąć
    okno.protocol("WM_DELETE_WINDOW", blokuj_zamykanie)
    okno.bind("<Alt-F4>", lambda e: "break")

    label = tk.Label(okno, text="Nie ten plik\n- Arsii", fg="red", bg="black", font=("Helvetica", 36, "bold"))
    label.pack(expand=True)

    haslo_label = tk.Label(okno, text="Podaj hasło:", font=("Arial", 14), bg="black", fg="white")
    haslo_label.pack()

    haslo_entry = tk.Entry(okno, show="*", font=("Arial", 14))
    haslo_entry.pack()

    blad_label = tk.Label(okno, text="", fg="red", bg="black")
    blad_label.pack()

    def sprawdz_haslo():
        if haslo_entry.get() == HASLO_POPRAWNE:
            okno.destroy()
        else:
            blad_label.config(text="Błędne hasło!")
            pokaz_okno(index + 1)

    potwierdz_btn = tk.Button(okno, text="OK", command=sprawdz_haslo, font=("Arial", 12))
    potwierdz_btn.pack()

    okno.mainloop()

pokaz_okno()
