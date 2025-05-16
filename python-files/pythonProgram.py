import random

def zgadnij_liczbe():
    liczba_do_zgadniecia = random.randint(1, 100)
    maks_proby = 15
    proby = 0
    print("Zgadnij liczb� od 1 do 100! Masz 15 pr�b.")

    while proby < maks_proby:
        try:
            zgadnij = int(input(f"Pr�ba {proby + 1}/{maks_proby}. Twoja liczba: "))
            proby += 1

            if zgadnij < 1 or zgadnij > 100:
                print("Liczba musi by� w zakresie 1-100.")
                continue

            if zgadnij < liczba_do_zgadniecia:
                print("Za ma�o!")
            elif zgadnij > liczba_do_zgadniecia:
                print("Za du�o!")
            else:
                print(f"Brawo! Zgad�e� liczb� {liczba_do_zgadniecia} w {proby} pr�bach.")
                return

        except ValueError:
            print("Wpisz poprawn� liczb�!")

    print(f"Przegra�e�! Prawid�owa liczba to {liczba_do_zgadniecia}.")

if __name__ == "__main__":
    while True:
        zgadnij_liczbe()
        jeszcze_raz = input("Chcesz zagra� jeszcze raz? (tak/nie): ").strip().lower()
        if jeszcze_raz != "tak":
            print("Dzi�ki za gr�! Do zobaczenia!")
            break