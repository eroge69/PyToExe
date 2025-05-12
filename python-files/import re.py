import re

# Functie om software nummers in een BIN bestand te zoeken
def zoek_software_nummer(bin_bestand):
    try:
        with open(bin_bestand, 'rb') as bestand:
            data = bestand.read()

        # Reguliere expressie voor software nummers (standaard VAG patroon)
        patroon = re.compile(rb'\d{4,5}-\d{3}-\d{3}(-[A-Z])?')

        # Zoek software nummers
        software_nummers = patroon.findall(data)

        if software_nummers:
            print("Gevonden software nummers:")
            for nummer in software_nummers:
                print(nummer.decode('utf-8'))
        else:
            print("Geen software nummers gevonden.")

    except FileNotFoundError:
        print("Het BIN bestand is niet gevonden.")

# Voorbeeld van gebruik
if __name__ == '__main__':
    bin_pad = input("Geef het pad naar het BIN bestand op: ")
    zoek_software_nummer(bin_pad)
