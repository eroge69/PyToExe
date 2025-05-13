def monitor_diagnosis(ekrans_id, indikators_id, savienojums_id):
    ekrani = {
        1: "Darbojas normāli",
        2: "Melns ekrāns",
        3: "Zema izšķirtspēja",
        4: "Raustās vai mirgo",
        5: "No signal"
    }

    indikatori = {
        1: "Deg",
        2: "Mirgo",
        3: "Nedeg"
    }

    savienojumi = {
        1: "HDMI",
        2: "DisplayPort",
        3: "VGA",
        4: "DVI"
    }

    # Pārbaude vai ievadītie ID ir derīgi
    if ekrans_id not in ekrani or indikators_id not in indikatori or savienojums_id not in savienojumi:
        print("\n⚠️ Kļūda: Nepareizi ievadīts identifikators. Lūdzu mēģiniet vēlreiz ar derīgiem skaitļiem.")
        return

    ekrans = ekrani[ekrans_id]
    indikators = indikatori[indikators_id]
    savienojums = savienojumi[savienojums_id]

    secinajums = ""
    ieteikums = ""

    match (ekrans, indikators):
        case ("Melns ekrāns", "Nedeg"):
            secinajums = "Monitors nesaņem strāvu."
            ieteikums = "Pārbaudīt strāvas vadu un kontaktligzdu."
        case ("No signal", "Deg"):
            match savienojums:
                case "HDMI":
                    secinajums = "HDMI signāla problēma."
                    ieteikums = "Pārbaudīt HDMI kabeli un pieslēgvietu."
                case "VGA":
                    secinajums = "VGA signāla problēma."
                    ieteikums = "Pārbaudīt VGA kabeli un pieskrūvēt savienotāju."
                case _:
                    secinajums = "Nezināma signāla kļūda."
                    ieteikums = "Pārbaudīt video kabeli vai mainīt savienojuma veidu."
        case ("Raustās vai mirgo", _):
            secinajums = "Nestabila savienojuma problēma."
            ieteikums = "Nomainīt kabeli vai pārbaudīt kontaktus."
        case ("Zema izšķirtspēja", _):
            secinajums = "Nepareiza izšķirtspējas iestatīšana."
            ieteikums = "Pielāgot izšķirtspēju operētājsistēmas displeja iestatījumos."
        case ("Melns ekrāns", "Deg"):
            secinajums = "Iespējama iekšēja monitora kļūme."
            ieteikums = "Nodot ierīci diagnostikai vai remontam."
        case (_, "Mirgo"):
            secinajums = "Barošanas bloka problēma."
            ieteikums = "Pārbaudīt strāvas adapteri vai lietot citu barošanas avotu."
        case _:
            secinajums = "Nav pietiekamas informācijas."
            ieteikums = "Lūdzu pārbaudiet visus savienojumus un mēģiniet vēlreiz."

    print(f"\n🛠️ Secinājums: {secinajums}")
    print(f"✅ Ieteikums: {ieteikums}")


# -----------------------------
# Lietotāja ievade ar validāciju
def ievade_ar_skaitli(teksts, derigas_vertibas):
    while True:
        try:
            vertiba = int(input(teksts))
            if vertiba in derigas_vertibas:
                return vertiba
            else:
                print("⚠️ Lūdzu ievadiet derīgu skaitli.")
        except ValueError:
            print("⚠️ Lūdzu ievadiet skaitli, nevis tekstu.")

print("=== Monitora diagnostika ===")

print("\n1 - Darbojas normāli\n2 - Melns ekrāns\n3 - Zema izšķirtspēja\n4 - Raustās vai mirgo\n5 - No signal")
ekrans_id = ievade_ar_skaitli("Izvēlieties ekrāna stāvokli (1–5): ", range(1, 6))

print("\n1 - Deg\n2 - Mirgo\n3 - Nedeg")
indikators_id = ievade_ar_skaitli("Izvēlieties strāvas indikatora stāvokli (1–3): ", range(1, 4))

print("\n1 - HDMI\n2 - DisplayPort\n3 - VGA\n4 - DVI")
savienojums_id = ievade_ar_skaitli("Izvēlieties savienojuma veidu (1–4): ", range(1, 5))

monitor_diagnosis(ekrans_id, indikators_id, savienojums_id)


input("\nNospiediet Enter, lai aizvērtu programmu...")