import random

Login = str(input("Podaj Login: "))
Pin = int(input("Podaj Pin: "))
PrawLogin = "Fajne"
PrawPin = 1646
Pensja = 1
konto = 1000
LVL = 0
czas = 0

if PrawLogin == Login and PrawPin == Pin:
    print("Zalogowano")
    while True:
        czas += 1
        print("\n--- MENU ---")
        print("1. Zarabiaj")
        print("2. Sprawdź stan konta")
        print("3. Wypłać")
        print("4. Kup Edukację")
        print("5. Sprawdź Level")
        print("6. Kup Bitcoin (LVL 30+) (100-10000 zł)")
        print("Storna 2. Przejdz na następną stronę")
        wybor = input("Wybierz opcję: ")

        if wybor == "1":
            zarobek = Pensja * (LVL * 10 if LVL > 0 else 1)
            konto += zarobek
            print(f"Dodano {zarobek} zł. Nowy stan konta: {konto} zł.")

        elif wybor == "2":
            print(f"Aktualny stan konta: {konto} zł.")

        elif wybor == "3":
            try:
                wyplata = int(input("Ile chcesz wypłacić? "))
                if wyplata > konto:
                    print("Nie masz tylu pieniędzy na koncie.")
                else:
                    konto -= wyplata
                    print(f"Wypłacono {wyplata} zł. Pozostało: {konto} zł.")
            except ValueError:
                print("Wprowadź poprawną liczbę.")

#KUPNO EDUKACJI
        elif wybor == "4":
            print("\n--- MENU EDUKACJI ---")
            print("1. Harvard (100000 zł)")
            print("2. Stanford (10000 zł)")
            print("3. Batory (1000 zł)")
            print("4. Zagle (100 zł)")
            print("5. Wyjdz")
            szkolenie = input("Wybierz opcję: ")

            if szkolenie == "5":
                print("Wyjście")
            elif szkolenie == "1" and konto >= 100000:
                konto -= 100000
                LVL += 15
                print(f"Kupiłeś Harvard. Masz teraz LVL: {LVL}. Pozostało: {konto} zł.")
            elif szkolenie == "2" and konto >= 10000:
                konto -= 10000
                LVL += 10
                print(f"Kupiłeś Stanford. Masz teraz LVL: {LVL}. Pozostało: {konto} zł.")
            elif szkolenie == "3" and konto >= 1000:
                konto -= 1000
                LVL += 5
                print(f"Kupiłeś Batory. Masz teraz LVL: {LVL}. Pozostało: {konto} zł.")
            elif szkolenie == "4" and konto >= 100:
                konto -= 100
                LVL += 1
                print(f"Kupiłeś Zagle. Masz teraz LVL: {LVL}. Pozostało: {konto} zł.")
            else:
                print("Nie masz wystarczająco pieniędzy lub wybrałeś złą opcję.")
#KONIEC




        elif wybor == "5":
            print(f"Aktualny Level: {LVL} Poziom")


#KUPNO BITCOIN
        elif wybor == "6" and LVL >= 30:
            cena_bitcoin = random.randint(100, 10000)
            bitcoin = random.randint(1, 60000)
            print(f"Cena Bitcoina: {cena_bitcoin} zł")
            print(f"Masz {konto} zł")

            if konto >= cena_bitcoin:
                decyzja = input("Chcesz kupić? (tak/nie): ").lower()
                if decyzja == "tak":
                    konto -= cena_bitcoin
                    print(f"Kupiłeś Bitcoina Możesz go sprzedać za: {bitcoin} zł.")
                    decyzja_sprzedaz = input("Sprzedać teraz? (tak/nie): ").lower()
                    if decyzja_sprzedaz == "tak":
                        konto += bitcoin
                        print(f"Sprzedano Nowy stan konta: {konto} zł.")
                    else:
                        print("Zatrzymano Bitcoina (nie sprzedano).")
                else:
                    print("Nie kupiłeś Bitcoina")
            else:
                print("Nie masz wystarczająco pieniędzy")
#KONIEC                
                
#STRONA 2               
        elif wybor == "Strona 2":
            print(" ")
            print("---STRONA 2/2---")
            print("7. Kody")
            print("8. Wyjdz")
            print("Powrót. Idzie do menu głównego")
            Wybor2 = input("Wybierz opcję: ").lower()
            if Wybor2 == "8":
                print("Wylogowano.")
                break
            elif Wybor2 == "7":
                print("Kody są od developera lub z losowych przyczyn.")
                print("Podaj Kod:")
                KodWpisany = input("Kod: ").lower()
                if KodWpisany == "IoG":
                    LVL += 0
                    konto += 10
                    print("Dano +15 LVL i 2012 zł")
                    print(f"Teraz masz {LVL} LVL, {konto} zł")
                    print("Tego kodu możesz używać ile chcesz")
                else:
                    print("Kod Nieprawidłowy")
            elif Wybor2 == "powrót":
                print("Powrócono")
        
        else:
            print("Nieprawidłowa opcja, spróbuj ponownie")
            
#KONIEC            
        
            
else:
    print("Nieprawidłowy login lub PIN.")
