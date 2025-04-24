import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import math

# Stałe
TYPY_OPERACJI = ["Toczenie", "Wytaczanie", "Wiercenie", "Gwintowanie", "Toczenie gwintu", "Planowanie"]

# Główne okno
root = tk.Tk()
root.title("Kalkulator CNC")
root.geometry("600x800")

# Przechowywanie operacji
historia_operacji = []

etykiety = {}  # Mapowanie kluczy do etykiet
wszystkie_etykiety = []  # Lista wszystkich etykiet

# Funkcja do resetowania kolorów i podświetlania wymaganych

def podswietl_wymagane_pola(*args):
    for label in wszystkie_etykiety:
        label.config(background=root.cget("bg"))
    typ = combo_typ.get()
    wymagane = []

    if typ in ["Toczenie", "Wytaczanie"]:
        wymagane = [etykiety["d_start"], etykiety["d_koniec"], etykiety["ap"],
                    etykiety["dlugosc"], etykiety["posuw"], etykiety["vc"], etykiety["max_obroty"]]
    elif typ == "Wiercenie":
        wymagane = [etykiety["srednica_wiertla"], etykiety["vc"], etykiety["fn"],
                    etykiety["glebokosc_wiercenia"], etykiety["ilosc_otworow"]]
    elif typ == "Gwintowanie":
        wymagane = [etykiety["obroty"], etykiety["skok_gwintu"], etykiety["glebokosc_gwintu"], etykiety["ilosc_otworow"]]

    for label in wymagane:
        label.config(background="lightgreen")

# Funkcja pomocnicza do tworzenia pól

def label_entry(parent, text, row, klucz):
    label = ttk.Label(parent, text=text)
    label.grid(row=row, column=0, sticky="w", padx=10, pady=3)
    entry = ttk.Entry(parent)
    entry.grid(row=row, column=1, padx=10, pady=3)
    etykiety[klucz] = label
    wszystkie_etykiety.append(label)
    return entry

# Funkcja obliczająca czas operacji

def oblicz():
    typ = combo_typ.get()
    try:
        if typ in ["Toczenie", "Wytaczanie"]:
            d_start = float(entry_d_start.get())
            d_koniec = float(entry_d_koniec.get())
            ap = float(entry_ap.get())
            dlugosc = float(entry_dlugosc.get())
            posuw = float(entry_posuw.get())
            vc = float(entry_vc.get())
            max_rpm = float(entry_max_obroty.get())

            srednia_srednica = (d_start + d_koniec) / 2
            rpm = min((vc * 1000) / (math.pi * srednia_srednica), max_rpm)

            if typ == "Toczenie":
                glebokosc = abs(d_start - d_koniec) / 2
            else:  # Wytaczanie
                glebokosc = abs(d_koniec - d_start) / 2

            ilosc_przejazdow = math.ceil(glebokosc / ap)
            czas_operacji = (dlugosc / (rpm * posuw)) * ilosc_przejazdow
            droga_szybka = (dlugosc + 10) * ilosc_przejazdow
            czas_szybki = droga_szybka / 20000
            czas_operacji += czas_szybki

        elif typ == "Wiercenie":
            srednica = float(entry_srednica_wiertla.get())
            vc = float(entry_vc.get())
            fn = float(entry_fn.get())
            glebokosc = float(entry_glebokosc_wiercenia.get())
            ilosc = int(entry_ilosc_otworow.get())

            rpm = (vc * 1000) / (math.pi * srednica)
            czas_wiercenia = (glebokosc / (fn * rpm)) * ilosc
            czas_szybki = ((glebokosc + 10) / 20000) * ilosc
            czas_operacji = czas_wiercenia + czas_szybki

        elif typ == "Gwintowanie":
            obroty = float(entry_obroty.get())
            skok = float(entry_skok_gwintu.get())
            glebokosc = float(entry_glebokosc_gwintu.get())
            ilosc = int(entry_ilosc_otworow.get())

            czas_gwintowania = ((glebokosc * 2) / (skok * obroty)) + (5 / 60)
            czas_operacji = czas_gwintowania * ilosc

        else:
            messagebox.showinfo("Informacja", "Obliczenia dla wybranej operacji nie są jeszcze dostępne.")
            return

        minuty = int(czas_operacji)
        sekundy = int((czas_operacji - minuty) * 60)
        wynik = f"Czas operacji: {minuty} min {sekundy} s"
        label_wynik.config(text=wynik)

        historia_operacji.append((typ, czas_operacji))
        aktualizuj_liste()

    except ValueError:
        messagebox.showerror("Błąd", "Proszę poprawnie wypełnić wymagane pola.")

def aktualizuj_liste():
    listbox.delete(0, tk.END)
    suma = 0
    for i, (typ, czas) in enumerate(historia_operacji):
        minuty = int(czas)
        sekundy = int((czas - minuty) * 60)
        listbox.insert(tk.END, f"{i+1}. {typ}: {minuty} min {sekundy} s")
        suma += czas
    minuty = int(suma)
    sekundy = int((suma - minuty) * 60)
    label_suma.config(text=f"Łączny czas: {minuty} min {sekundy} s")

def eksportuj_csv():
    if not historia_operacji:
        messagebox.showinfo("Informacja", "Brak operacji do eksportu.")
        return
    plik = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if plik:
        try:
            # Zapisujemy dane do pliku CSV
            with open(plik, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Numer operacji", "Typ operacji", "Czas (minuty:sekundy)"])  # Nagłówki
                suma_czasu = 0  # Zmienna do sumowania czasu

                for i, (typ, czas) in enumerate(historia_operacji):
                    minuty = int(czas)
                    sekundy = int((czas - minuty) * 60)
                    czas_str = f"{minuty} min {sekundy} s"
                    writer.writerow([i + 1, typ, czas_str])  # Zapisujemy numer operacji, nazwę i czas
                    suma_czasu += czas

                # Dodajemy podsumowanie
                minuty_suma = int(suma_czasu)
                sekundy_suma = int((suma_czasu - minuty_suma) * 60)
                writer.writerow(["", "", f"Całkowity czas: {minuty_suma} min {sekundy_suma} s"])

            messagebox.showinfo("Sukces", "Dane zapisane do pliku CSV.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać do pliku: {e}")
            

def wyczysc_historie():
    historia_operacji.clear()
    aktualizuj_liste()

def usun_operacje():
    zaznaczone = listbox.curselection()
    if zaznaczone:
        for i in reversed(zaznaczone):
            historia_operacji.pop(i)
        aktualizuj_liste()
    else:
        messagebox.showinfo("Informacja", "Wybierz operację do usunięcia.")

# GUI Layout
combo_typ = ttk.Combobox(root, values=TYPY_OPERACJI, state="readonly")
combo_typ.grid(row=0, column=1, padx=10, pady=5)
combo_typ.set(TYPY_OPERACJI[0])
combo_typ.bind("<<ComboboxSelected>>", podswietl_wymagane_pola)

label_typ = ttk.Label(root, text="Typ operacji:")
label_typ.grid(row=0, column=0, sticky="w", padx=10, pady=5)

entry_dlugosc = label_entry(root, "Długość (mm) - dla toczenia/wytaczania:", 1, "dlugosc")
entry_posuw = label_entry(root, "Posuw na obrót (mm):", 2, "posuw")
entry_vc = label_entry(root, "Prędkość skrawania Vc (m/min):", 3, "vc")
entry_max_obroty = label_entry(root, "Maksymalne obroty (obr/min):", 4, "max_obroty")
entry_srednica_wiertla = label_entry(root, "Średnica wiertła (mm):", 5, "srednica_wiertla")
entry_fn = label_entry(root, "Posuw na obrót (fn) (mm):", 6, "fn")
entry_glebokosc_wiercenia = label_entry(root, "Głębokość wiercenia (mm):", 7, "glebokosc_wiercenia")
entry_ilosc_otworow = label_entry(root, "Ilość otworów:", 8, "ilosc_otworow")
entry_d_start = label_entry(root, "Średnica startowa (mm):", 9, "d_start")
entry_d_koniec = label_entry(root, "Średnica końcowa (mm):", 10, "d_koniec")
entry_ap = label_entry(root, "Głębokość skrawania Ap (mm):", 11, "ap")
entry_obroty = label_entry(root, "Obroty (obr/min):", 12, "obroty")
entry_skok_gwintu = label_entry(root, "Skok gwintu (mm):", 13, "skok_gwintu")
entry_glebokosc_gwintu = label_entry(root, "Głębokość gwintu (mm):", 14, "glebokosc_gwintu")

btn_oblicz = ttk.Button(root, text="Dodaj operację", command=oblicz)
btn_oblicz.grid(row=15, column=0, columnspan=2, pady=10)

label_wynik = ttk.Label(root, text="")
label_wynik.grid(row=16, column=0, columnspan=2)

label_lista = ttk.Label(root, text="Historia operacji:")
label_lista.grid(row=17, column=0, columnspan=2)

listbox = tk.Listbox(root, width=50, selectmode=tk.MULTIPLE)
listbox.grid(row=18, column=0, columnspan=2, pady=5)

btn_usun = ttk.Button(root, text="Usuń wybrane", command=usun_operacje)
btn_usun.grid(row=19, column=0, pady=5)

label_suma = ttk.Label(root, text="Łączny czas: 0 min 0 s")
label_suma.grid(row=20, column=0, columnspan=2)

btn_eksportuj = ttk.Button(root, text="Eksportuj do CSV", command=eksportuj_csv)
btn_eksportuj.grid(row=21, column=0, columnspan=2, pady=10)

btn_wyczysc = ttk.Button(root, text="Wyczyść historię", command=wyczysc_historie)
btn_wyczysc.grid(row=22, column=0, columnspan=2)

root.mainloop()
