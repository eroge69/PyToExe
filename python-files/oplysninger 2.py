import os

Navn = input("skriv dit navn ")
Email = input("skriv din Email ")
Nummer = input("skriv dit nummer ")
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
filepath =  os.path.join(desktop, "oplysninger.txt")

with open(filepath, "a") as f:
    f.write(f"Navn: {Navn}\n")
    f.write(f"Email: {Email}\n")
    f.write(f"Nummer: {Nummer}\n")

    print(f"Oplysninger gemt på: {filepath}")