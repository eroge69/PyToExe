
# Online Python - IDE, Editor, Compiler, Interpreter

def sum(a, b):
    return (a + b)

a = int(input('Enter 1st number: '))
b = int(input('Enter 2nd number: '))

print(f'Sum of {a} and {b} is {sum(a, b)}')
import csv
import os

# Bestandsnaam voor het opslaan van overdrachten
BESTAND = 'team_overdrachten.csv'

def controleer_bestand():
    # Als het bestand niet bestaat, maak het aan met koptekst
    if not os.path.exists(BESTAND):
        with open(BESTAND, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Van', 'Naar', 'Datum','Team','Omschrijving'])

def invoer_overdracht():
    van = input("Naam vertrekkende teamlid: ")
    naar = input("Naam binnenkomende teamlid: ")
    datum = input("Datum van overdracht (bijv. 2024-10-15): ")
    team = input("Team: ")
    omschrijving = input("Omschrijving (optioneel): ")

    # Voeg de overdracht toe aan het CSV-bestand
    with open(BESTAND, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([van, naar, datum, team, omschrijving])
    print("Overdracht succesvol toegevoegd.\n")

def overzicht_overdrachten():
    # Lees en toon alle overdrachten
    if not os.path.exists(BESTAND):
        print("Geen overdrachten gevonden.\n")
        return

    print("\nTeam Overdrachten:\n")
    with open(BESTAND, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(f"Van: {row['Van']} | Naar: {row['Naar']} | Datum: {row['Datum']} | Team: {row['Team']} | Omschrijving: {row['Omschrijving']}")
    print()

def main():
    controleer_bestand()
    while True:
        print("Kies een optie:")
        print("1. Voeg een overdracht toe")
        print("2. Bekijk alle overdrachten")
        print("3. Afsluiten")
        keuze = input("Voer je keuze in (1/2/3): ")

        if keuze == '1':
            invoer_overdracht()
        elif keuze == '2':
            overzicht_overdrachten()
        elif keuze == '3':
            print("Programma afgesloten.")
            break
        else:
            print("Ongeldige keuze, probeer opnieuw.\n")

if __name__ == "__main__":
    main()