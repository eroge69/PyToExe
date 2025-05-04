proben = 0.423
spritze = 0.999
verpackung = 0.12
umschlaege = 0.036

def berechne_mindestpreis():
    
    kosten = int(input("Parfum-Kosten : "))
    gesamt_ml = int(input("Flasche ml : "))
    probe_ml = int(input("Abfüllung ml: "))

    anzahl = gesamt_ml/probe_ml

    mindestpreis = ((kosten + spritze)/ anzahl)+ proben + verpackung + umschlaege
    preis = round(mindestpreis, 2)
    print("Mindestpreis : ", preis,"€")


def parfum_rechner():
    print("Willkommen zum Parfüm-Proben-Rechner!")

    while True:
        berechne_mindestpreis()

        nochmal = input("\Reset (ja/nein): ").strip().lower()
        if nochmal != "ja":
            print("\nDanke fürs Benutzen des Rechners. Viel Erfolg mit deinen Parfüm-Proben!")
            break

parfum_rechner()
