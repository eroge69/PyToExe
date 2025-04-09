import random
from collections import defaultdict
import json
import os

class Dobokocka:
    def __init__(self):
        self.oldalak = 6
        self.dobas_naplo = defaultdict(list)
        self.jatekos_neve = ""
        self.fajl_nev = "dobas_eredmenyek.json"
        self.betolt_fajlbol()
    
    def uj_jatekos(self):
        self.jatekos_neve = input("\nAdd meg az új játékos nevét: ").strip()
        if not self.jatekos_neve:
            self.jatekos_neve = "Ismeretlen"
        print(f"Üdvözöljük, {self.jatekos_neve}!")
    
    def beallit_jatekos_nevet(self):
        if not self.jatekos_neve:
            self.uj_jatekos()
    
    def rajzol_kockat(self, szam):
        kocka_rajz = [
            "┌───────┐",
            "│ │",
            "│ │",
            "│ │",
            "└───────┘"
        ]
        
        if szam == 1:
            kocka_rajz[2] = "│ ● │"
        elif szam == 2:
            kocka_rajz[1] = "│ ● │"
            kocka_rajz[3] = "│ ● │"
        elif szam == 3:
            kocka_rajz[1] = "│ ● │"
            kocka_rajz[2] = "│ ● │"
            kocka_rajz[3] = "│ ● │"
        elif szam == 4:
            kocka_rajz[1] = "│ ● ● │"
            kocka_rajz[3] = "│ ● ● │"
        elif szam == 5:
            kocka_rajz[1] = "│ ● ● │"
            kocka_rajz[2] = "│ ● │"
            kocka_rajz[3] = "│ ● ● │"
        elif szam == 6:
            kocka_rajz[1] = "│ ● ● │"
            kocka_rajz[2] = "│ ● ● │"
            kocka_rajz[3] = "│ ● ● │"
        
        print("\n".join(kocka_rajz))
        print(f"\nDobás eredménye: {szam}")
    
    def dob(self):
        self.beallit_jatekos_nevet()
        eredmeny = random.randint(1, self.oldalak)
        self.dobas_naplo[self.jatekos_neve].append(eredmeny)
        print(f"\n{self.jatekos_neve} dobása:")
        self.rajzol_kockat(eredmeny)
        self.mentes_fajlba()
        return eredmeny
    
    def statisztika(self):
        print("\nDobás statisztika:")
        if not self.dobas_naplo:
            print("Még nem történt dobás.")
            return
            
        max_név_hossz = max(len(nev) for nev in self.dobas_naplo.keys())
        
        for jatekos, dobasok in self.dobas_naplo.items():
            dobasszam = len(dobasok)
            utolso_dobas = dobasok[-1] if dobasok else "-"
            print(f"{jatekos.ljust(max_név_hossz)} : Összesen {dobasszam} dobás, utolsó: {utolso_dobas}")
    
    def reszletes_statisztika(self):
        print("\nRészletes dobás statisztika:")
        for jatekos, dobasok in self.dobas_naplo.items():
            print(f"\n{jatekos} dobásai:")
            szamlalo = defaultdict(int)
            for dob in dobasok:
                szamlalo[dob] += 1
            for szam in sorted(szamlalo.keys()):
                print(f"{szam}-es: {szamlalo[szam]} db")
            print(f"Összesen: {len(dobasok)} dobás")
    
    def eredmenyek_torlese(self):
        confirm = input("\nBiztosan törölni szeretnéd az összes eredményt? (i/n): ").lower()
        if confirm == 'i':
            self.dobas_naplo = defaultdict(list)
            self.jatekos_neve = ""
            try:
                os.remove(self.fajl_nev)
                print("Az összes eredmény törölve lett!")
            except FileNotFoundError:
                print("Nincsenek mentett eredmények a törléshez.")
            except Exception as e:
                print(f"Hiba történt a törlés közben: {e}")
        else:
            print("Törlés megszakítva.")
    
    def info(self):
        print("\n=== Információ ===")
        print("Ez egy dobókocka project amit Zero készített")
        print("Jelenlegi program verzió: v0.5")
        print("Valódi dobókocka szimulátor - csak pontok láthatóak")
        print("==================")
    
    def mentes_fajlba(self):
        try:
            with open(self.fajl_nev, 'w') as f:
                json.dump(self.dobas_naplo, f)
        except Exception as e:
            print(f"Hiba történt a mentés közben: {e}")
    
    def betolt_fajlbol(self):
        if os.path.exists(self.fajl_nev):
            try:
                with open(self.fajl_nev, 'r') as f:
                    data = json.load(f)
                    self.dobas_naplo = defaultdict(list, data)
            except Exception as e:
                print(f"Hiba történt a betöltés közben: {e}")

def main():
    print("Dobókocka szimulátor - Valódi kocka verzió")
    kocka = Dobokocka()
    
    while True:
        print("\nVálassz egy műveletet:")
        print("1 - Dobás (aktuális játékossal)")
        print("2 - Új játékos")
        print("3 - Összesített statisztika")
        print("4 - Részletes statisztika")
        print("5 - Eredmények törlése")
        print("6 - Információ")
        print("7 - Kilépés")
        
        try:
            valasztas = input("Választásod (1-7): ")
            
            if valasztas == "1":
                if not kocka.jatekos_neve:
                    print("\nNincs aktív játékos!")
                    kocka.uj_jatekos()
                else:
                    print(f"\nAktuális játékos: {kocka.jatekos_neve}")
                    kocka.dob()
            elif valasztas == "2":
                kocka.uj_jatekos()
            elif valasztas == "3":
                kocka.statisztika()
            elif valasztas == "4":
                kocka.reszletes_statisztika()
            elif valasztas == "5":
                kocka.eredmenyek_torlese()
            elif valasztas == "6":
                kocka.info()
            elif valasztas == "7":
                print("Kilépés...")
                kocka.mentes_fajlba()
                break
            else:
                print("Érvénytelen választás, próbáld újra!")
        except Exception as e:
            print(f"Váratlan hiba történt: {e}")
            continue

if __name__ == "__main__":
    main()