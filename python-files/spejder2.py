import os

name = input("Indtast navn: ")
email = input("Indtast email: ")
phone = input("Indtast telefonnummer: ")
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
save_path = os.path.join(desktop, "kontakt.txt")

with open(save_path, "a") as file:
    file.write(f"Navn: {name}\n")
    file.write(f"Email: {email}\n")
    file.write(f"Telefon: {phone}\n")
    file.write("---\n")

print("Kontaktoplysninger gemt i kontakt.txt")
