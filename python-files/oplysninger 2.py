Email = input("skriv din Email ")
Nummer = input("skriv dit nummer ")
filepath = "C:\\Users\\birk0\\Desktop\\oplysninger.txt"

with open(filepath, "x") as f:
    f.write(f"Email: {Email}\n")
    f.write(f"Nummer: {Nummer}\n")