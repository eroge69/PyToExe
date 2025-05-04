import tkinter as tk
from tkinter import Toplevel, Scrollbar, Text, END

# Dane o produktach (tu wklej swój słownik "produkty")

produkty = {
        '7005836300': {'ilosc': '30 m', 'lokalizacja': 'A1'},
    '7001099400': {'ilosc': '13,6 m', 'lokalizacja': 'A2'},
    '7000146600': {'ilosc': '6 m', 'lokalizacja': 'A3'},
    '7001110400': {'ilosc': '156,6 m', 'lokalizacja': 'A4'},
    '7001108900': {'ilosc': '14 m', 'lokalizacja': 'A5'},
    '7001105700': {'ilosc': '1,8', 'lokalizacja': 'A6'},
    '7001123100': {'ilosc': '180 m', 'lokalizacja': 'A7 i A8'},
    '7001123200': {'ilosc': '33 m', 'lokalizacja': 'A9'},
    '7001098600': {'ilosc': '24 m', 'lokalizacja': 'A10'},
    '7008731300': {'ilosc': '3 m', 'lokalizacja': 'A11'},
    '7010456900': {'ilosc': '18 m', 'lokalizacja': 'A12'},
    '7005835100': {'ilosc': '100 m', 'lokalizacja': 'A13,A14,A15'},
    '7001122900': {'ilosc': '28,8 m', 'lokalizacja': 'A16'},
    '7001100900': {'ilosc': '8,5 m', 'lokalizacja': 'A17'},
    '7000145300': {'ilosc': '7m', 'lokalizacja': 'A18'},
    '7001105100': {'ilosc': '12 m', 'lokalizacja': 'A19'},
    '7001123700': {'ilosc': '12,5 m', 'lokalizacja': 'A20'},
    '7001102200': {'ilosc': '4,50 m', 'lokalizacja': 'A21'},
    '7000145800': {'ilosc': '79,8 m', 'lokalizacja': 'A31'},
    '7001107100': {'ilosc': '9 m', 'lokalizacja': 'A23'},
    '7001095500': {'ilosc': '22 m', 'lokalizacja': 'A24'},
    '7004770100': {'ilosc': '7,5 m', 'lokalizacja': 'A25'},
    '7001122600': {'ilosc': '4 m', 'lokalizacja': 'A26'},
    '7001081900': {'ilosc': '4 m', 'lokalizacja': 'A27'},
    '7004765700': {'ilosc': '2 m', 'lokalizacja': 'MIX'},
    '7005836200': {'ilosc': '30 m', 'lokalizacja': 'A29'},
    '7001099500': {'ilosc': '1,2 m', 'lokalizacja': 'A30'},
    '7005202000': {'ilosc': '11 m', 'lokalizacja': 'A32'},
    '7000000300': {'ilosc': '16,5 m', 'lokalizacja': 'A33'},
    '7000126200': {'ilosc': '1,90 m', 'lokalizacja': 'B2'},
    '7007369100': {'ilosc': '5 m', 'lokalizacja': 'A35'},
    '7000136500': {'ilosc': '106 m', 'lokalizacja': 'C8'},
    '7004768800': {'ilosc': '4 m', 'lokalizacja': 'A37'},
    '7005652500': {'ilosc': '2,7 m', 'lokalizacja': 'A38'},
    '7001095100': {'ilosc': '5 m', 'lokalizacja': 'B1'},
    '7001088200': {'ilosc': '7 m', 'lokalizacja': 'B3'},
    '7004771700': {'ilosc': '2,5 m', 'lokalizacja': 'B4'},
    '7000125000': {'ilosc': '18,2 m', 'lokalizacja': 'B5'},
    '7000134500': {'ilosc': '142,8 m', 'lokalizacja': 'B6 i B20'},
    '7004923300': {'ilosc': '15 m', 'lokalizacja': 'B7'},
    '7005823400': {'ilosc': '12,6 m', 'lokalizacja': 'C14'},
    '7000136800': {'ilosc': '2,50 m', 'lokalizacja': 'MIX'},
    '7011356400': {'ilosc': '15 m', 'lokalizacja': 'B10'},
    '7000458700': {'ilosc': '18 m', 'lokalizacja': 'B11'},
    '7004769500': {'ilosc': '331 m', 'lokalizacja': 'C2 i B12'},
    '7001299700': {'ilosc': '10 m', 'lokalizacja': 'C20'},
    '7004766000': {'ilosc': '397 m', 'lokalizacja': 'C7'},
    '7000121500': {'ilosc': '20 m', 'lokalizacja': 'B15'},
    '7004782400': {'ilosc': '197 m', 'lokalizacja': 'C11'},
    '7000129000': {'ilosc': '5 m', 'lokalizacja': 'B17'},
    '7000122300': {'ilosc': '102 m', 'lokalizacja': 'B18 i B19'},
    '7004783900': {'ilosc': '15 m', 'lokalizacja': 'B21'},
    '7001080500': {'ilosc': '151,3 m', 'lokalizacja': 'B22'},
    '7000124000': {'ilosc': '548 m', 'lokalizacja': 'C1'},
    '7000126300': {'ilosc': '10 m', 'lokalizacja': 'MIX'},
    '7004771500': {'ilosc': '50 m', 'lokalizacja': 'C4'},
    '7004767800': {'ilosc': '12 m', 'lokalizacja': 'C5'},
    '7004766100': {'ilosc': '48 m', 'lokalizacja': 'C9'},
    '7000127100': {'ilosc': '2,50 m', 'lokalizacja': 'C13'},
    '7001079900': {'ilosc': '21 m', 'lokalizacja': 'C15'},
    '7001082000': {'ilosc': '5 m', 'lokalizacja': 'C16'},
    '7000122200': {'ilosc': '79,8 m', 'lokalizacja': 'C17'},
    '7000127600': {'ilosc': '4 m', 'lokalizacja': 'C18'},
    '7001299100': {'ilosc': '23,8 m', 'lokalizacja': 'C19'},
    '7001293900': {'ilosc': '3,5 m', 'lokalizacja': 'C21'},
    '7000128400': {'ilosc': '4,10 m', 'lokalizacja': 'C22'},
    '7000000200': {'ilosc': '20 m', 'lokalizacja': 'MIX'},
    '7000121900': {'ilosc': '4 m', 'lokalizacja': 'MIX'},
    '7006547400': {'ilosc': '4 m', 'lokalizacja': 'MIX'},
    '7007368900': {'ilosc': '15 m', 'lokalizacja': 'MIX'},
    '7005836400': {'ilosc': '4 m', 'lokalizacja': 'MIX'},
    '7001101500': {'ilosc': '4m', 'lokalizacja': 'MIX'},
}

# Funkcja wyświetlająca dane na podstawie numeru produktu
def pokaz_dane():
    numer_produktu = entry_produkt.get().strip()
    if not numer_produktu:
        label_wynik.config(text="Wprowadź numer produktu.")
        return

    if numer_produktu in produkty:
        ilosc = produkty[numer_produktu]["ilosc"]
        lokalizacja = produkty[numer_produktu]["lokalizacja"]
        label_wynik.config(text=f"Numer Produktu: {numer_produktu}\nIlość: {ilosc}\nLokalizacja: {lokalizacja}")
    else:
        label_wynik.config(text="Produkt o podanym numerze nie istnieje")

# Funkcja do wyświetlania wszystkich produktów
def pokaz_wszystkie_produkty():
    nowe_okno = Toplevel(root)
    nowe_okno.title("Lista wszystkich produktów")

    text_area = Text(nowe_okno, wrap="word", font=("Arial", 12))
    scrollbar = Scrollbar(nowe_okno, command=text_area.yview)
    text_area.configure(yscrollcommand=scrollbar.set)

    text_area.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for nr, dane in produkty.items():
        text_area.insert(END, f"{nr} - Ilość: {dane['ilosc']}, Lokalizacja: {dane['lokalizacja']}\n")

# Tworzenie okna aplikacji
root = tk.Tk()
root.title("VOSS - Menu Produktów")
root.configure(bg="white")

# Logo
logo_label = tk.Label(root, text="VOSS", font=("Arial", 30, "bold"), fg="pink", bg="white")
logo_label.grid(row=0, column=0, columnspan=2, pady=10)

# Pole do wprowadzenia numeru produktu
label_produkt = tk.Label(root, text="Wprowadź numer produktu:", font=("Arial", 14), bg="white")
label_produkt.grid(row=1, column=0, padx=10, pady=5)

entry_produkt = tk.Entry(root, font=("Arial", 14))
entry_produkt.grid(row=1, column=1, padx=10, pady=5)

# Przycisk do wyświetlenia danych
button_sprawdz = tk.Button(root, text="Sprawdź dane", font=("Arial", 14), command=pokaz_dane)
button_sprawdz.grid(row=2, column=0, columnspan=2, pady=10)

# Przycisk do wyświetlenia wszystkich produktów
button_lista = tk.Button(root, text="Pokaż wszystkie produkty", font=("Arial", 12), command=pokaz_wszystkie_produkty)
button_lista.grid(row=3, column=0, columnspan=2, pady=5)

# Etykieta do wyświetlania wyników
label_wynik = tk.Label(root, text="", font=("Arial", 14), bg="white", justify="left")
label_wynik.grid(row=4, column=0, columnspan=2, pady=20)

# Uruchomienie aplikacji
root.mainloop()
