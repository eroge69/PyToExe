import random
import os
import time
import json

def vycisti_konzolu():
    os.system("cls" if os.name == "nt" else "clear")

def zobraz_licencne_podmienky():
    print("\n\033[93mLicenčné podmienky:\033[0m")
    print("Používaním tejto aplikácie súhlasíte s nasledujúcimi podmienkami:")
    print("1. Aplikácia je určená len na zábavu.")
    print("2. Autor nezodpovedá za žiadne škody spôsobené používaním aplikácie.")
    print("3. Akékoľvek neoprávnené používanie môže byť postihnuté.")
    print("\033[93m\nPokračovaním súhlasíte s týmito podmienkami.\033[0m\n")
    input("Stlačte Enter pre pokračovanie...")

def vyber_obtiznost():
    obtiznosti = {
        1: 35,  # Ľahká
        2: 150,  # Stredná
        3: 300,  # Ťažká
        4: 1000,   # Expert
        5: 8000, # Legendary
    }
    casove_limity = {
        1: 40,
        2: 70,
        3: 160,
        4: 220,  # Veľmi ľahká
        5: 380, # Veľmi ťažká
    }  # Časové limity pre jednotlivé úrovne
    while True:
        print("\nVyberte úroveň obtížnosti:")
        print("\033[92m1. Ľahká (1-35)\033[0m")  # Zelená
        print("\033[33m2. Stredná (1-150)\033[0m")  # Oranžová
        print("\033[91m3. Ťažká (1-300)\033[0m")  # Červená
        print("\033[95m4. Expert (1-1000)\033[0m")  # Fialová
        print("\033[96m5. Legendary (1-8000)\033[0m") # Svetlo modrá
        try:
            volba = input((
                 "\033[92m1\033[0m/\033[33m2\033[0m/\033[91m3\033[0m/\033[94m4\033[0m/\033[96m5\033[0m: "
            ))
            volba = int(volba)
            if volba in obtiznosti:
                return obtiznosti[volba], casove_limity[volba]  # Vráti aj časový limit
            else:
                print("Neplatná voľba. Skúste to znovu.")
        except ValueError:
            print("Prosím, zadajte platné číslo.")

def ziskat_ano_ne_vstup(prompt):
    while True:
        odpoved = input(prompt).strip().lower()
        if odpoved in ['a', 'n']:
            return odpoved
        print("Neplatný vstup. Zadajte 'A' pre áno alebo 'N' pre ne.")

def zobraz_statistiky(pocet_pokusov, pokusy, body):
    print("\n" + "=" * 50)
    print(f"\033[92m Vaše číslo je správne!!!\033[0m")  # Svetlo zelená
    print(f"\033[92m Podarilo se vám jej uhodnúť na {pocet_pokusov} pokusů\033[0m")
    print(f"\033[92m Vaše pokusy: {', '.join(map(str, pokusy))}\033[0m")
    print(f"\033[96m Získali ste {body} bodov.\033[0m")  # Zobraziť bodovanie
    print("=" * 50)

def ulozit_statistiky(pocet_pokusov, pokusy, username, body):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "timestamp": timestamp,
            "username": username,
            "pokusy": pocet_pokusov,
            "historie": pokusy,
            "body": body  # Uloženie bodov
        }
        dokumenty_adresar = os.path.expanduser('~\\Documents')
        if not os.path.exists(dokumenty_adresar):
            os.makedirs(dokumenty_adresar)
        soubor_cesta = os.path.join(dokumenty_adresar, "statistiky.json")
        if os.path.exists(soubor_cesta):
            try:
                with open(soubor_cesta, "r") as file:
                    stats = json.load(file)
            except json.JSONDecodeError:
                print("Soubor 'statistiky.json' je poškozen.")
                stats = []
        else:
            stats = []
        stats.append(data)
        with open(soubor_cesta, "w") as file:
            json.dump(stats, file, indent=4)
        print(f"\033[94mStatistiky boli uložené do súboru '{soubor_cesta}'.\033[0m")
    except Exception as e:
        print(f"Chyba pri ukladani statistik: {e}")

def gratulace(pocet_pokusov, body):
    if pocet_pokusov <= 3:
        body += 50
        print("\033[92mSkvělé! Uhádli jste číslo opravdu rychle!\033[0m")
    elif pocet_pokusov <= 7:
        body += 30
        print("\033[93mVýborně! Bylo to trochu ťažšie, ale zvládli jste to!\033[0m")
    else:
        body += 10
        print("\033[91mDobrá práca! I keď to trvalo déle, máte to za sebou!\033[0m")
    return body

def ziskej_cislo(prompt, min_hodnota, max_hodnota):
    while True:
        try:
            tip = int(input(prompt))
            if min_hodnota <= tip <= max_hodnota:
                return tip
            print(f"Číslo musí byť medzi {min_hodnota} a {max_hodnota}.")
        except ValueError:
            print("Prosím, zadajte platné číslo.")

def login_or_register():
    user_data_path = os.path.expanduser("~\\Documents\\user_data.json")
    if os.path.exists(user_data_path):
        with open(user_data_path, 'r') as f:
            users = json.load(f)
    else:
        users = {}

    while True:
        print("\n\033[96m1. Prihlásenie\033[0m")
        print("\033[93m2. Registrovať\033[0m")
        choice = input("Vyberte možnosť: ")
        
        if choice == "1":
            username = input("Zadajte meno: ")
            password = input("Zadajte heslo: ")
            if username in users and users[username] == password:
                print("\033[92mPrihlásenie úspešné!\033[0m")
                print(f"\033[96mVítame ťa v hre o hádanie čísel, {username}!\033[0m")
                return username
            else:
                print("\033[91mNesprávne meno alebo heslo!\033[0m")
        
        elif choice == "2":
            username = input("Zadajte nové meno: ")
            if username in users:
                print("\033[91mToto meno už existuje!\033[0m")
            else:
                password = input("Zadajte nové heslo: ")
                users[username] = password
                with open(user_data_path, 'w') as f:
                    json.dump(users, f, indent=4)
                zobraz_licencne_podmienky()
                print("\033[92mRegistrovanie úspešné!\033[0m")
                print(f"\033[96mVítame ťa v hre o hádanie čísel, {username}!\033[0m")
                return username
        else:
            print("\033[91mNeplatná voľba. Skúste to znova.\033[0m")

def hra_hadanie_cisiel():
    vycisti_konzolu()
    print("\033[96m" + "=" * 50)
    print("                Hra o hádaní čísel")
    print("=" * 50 + "\033[0m")

    username = login_or_register()

    horni_hranice, casovy_limit = vyber_obtiznost()
    nahodne_cislo = random.randint(1, horni_hranice)
    pocet_pokusov = 0
    pokusy = []
    body = 0  # Počiatočný počet bodov
    
    vycisti_konzolu()
    print(f"\033[95m\nNáhodné číslo bolo vygenerované medzi 1 a {horni_hranice}. Zadajte váš tip!\033[0m\n")  # Ružová
    start_time = time.time()

    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > casovy_limit:
            print("\033[91mČas vypršel! Neuhodli ste číslo v časovom limite.\033[0m")
            if ziskat_ano_ne_vstup("\033[93mChcete spustiť novú hru? (A/N): \033[0m") == 'a':
                hra_hadanie_cisiel()
                return
            else:
                return

        print(f"\033[93mČas: {casovy_limit - int(elapsed_time)} sekundy\033[0m")
        tip = ziskej_cislo("Zadejte číslo: ", 1, horni_hranice)
        pocet_pokusov += 1
        pokusy.append(tip)

        if tip > nahodne_cislo:
            print("\033[91mMéně!\033[0m")
        elif tip < nahodne_cislo:
            print("\033[94mVíce!\033[0m")
        else:
            # Odmeň bodmi
            body = gratulace(pocet_pokusov, body)
            zobraz_statistiky(pocet_pokusov, pokusy, body)
            ulozit_statistiky(pocet_pokusov, pokusy, username, body)
            if ziskat_ano_ne_vstup("\033[93mChcete spustiť novú hru? (A/N): \033[0m") == 'a':
                hra_hadanie_cisiel()
                return
            else:
                return

if __name__ == "__main__":
    hra_hadanie_cisiel()
