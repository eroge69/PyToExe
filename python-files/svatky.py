import datetime


def zobraz_upozorneni_na_svatky():

    """

    Zobrazí upozornění na blížící se nebo dnešní státní svátky v ČR.

    """

    statni_svatky = {

        datetime.date(datetime.date.today().year, 1, 1): "Den obnovy samostatného českého státu",

        datetime.date(datetime.date.today().year, 3, 29): "Velký pátek",  # pohyblivý svátek

        datetime.date(datetime.date.today().year, 4, 1): "Velikonoční pondělí",  # pohyblivý svátek

        datetime.date(datetime.date.today().year, 5, 1): "Svátek práce",

        datetime.date(datetime.date.today().year, 5, 8): "Den vítězství",

        datetime.date(datetime.date.today().year, 7, 5): "Den slovanských věrozvěstů Cyrila a Metoděje",

        datetime.date(datetime.date.today().year, 7, 6): "Den upálení Mistra Jana Husa",

        datetime.date(datetime.date.today().year, 9, 28): "Den české státnosti",

        datetime.date(datetime.date.today().year, 10, 28): "Den vzniku samostatného československého státu",

        datetime.date(datetime.date.today().year, 11, 17): "Den boje za svobodu a demokracii",

        datetime.date(datetime.date.today().year, 12, 24): "Štědrý den",

        datetime.date(datetime.date.today().year, 12, 25): "1. svátek vánoční",

        datetime.date(datetime.date.today().year, 12, 26): "2. svátek vánoční"

    }


    dnes = datetime.date.today()

    zitra = dnes + datetime.timedelta(days=1)

    pozitri = dnes + datetime.timedelta(days=2)


    if dnes in statni_svatky:

        print(f"Dnes je státní svátek: {statni_svatky[dnes]}")


    if zitra in statni_svatky:

        print(f"Zítra ({zitra.strftime('%d.%m.%Y')}) je státní svátek: {statni_svatky[zitra]}")


    if pozitri in statni_svatky:

        print(f"Pozítří ({pozitri.strftime('%d.%m.%Y')}) je státní svátek: {statni_svatky[pozitri]}")


    for datum, nazev in statni_svatky.items():

        if datum > pozitri and (datum - dnes).days <= 7:

            print(f"Blíží se státní svátek ({datum.strftime('%d.%m.%Y')}): {nazev}")


if __name__ == "__main__":

    zobraz_upozorneni_na_svatky()

