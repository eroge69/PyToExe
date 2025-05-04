import random

def play_lemonade_stand_final_v4():
    money = 10.00
    lemons = 0
    day_of_week = 1
    day_number = 1
    total_profit = 0
    lemons_per_drink = 1
    base_lemon_price = 0.50

    daily_stats = []

    def get_weather():
        return random.choice(["Slnečno", "Mierne", "Zamračené", "Daždivo"])

    def get_weather_effect(weather):
        if weather == "Slnečno":
            return 1.2
        elif weather == "Mierne":
            return 1.0
        elif weather == "Zamračené":
            return 0.8
        elif weather == "Daždivo":
            return 0.5
        return 1.0

    def calculate_sales(weather, price, event_multiplier=1):
        weather_effect = get_weather_effect(weather)
        base_sales_factor = 20
        price_effect = (price - 0.5) * 6
        sales = max(0, int((base_sales_factor * weather_effect - price_effect) * event_multiplier))
        return sales

    def get_lemon_price():
        price_change = random.uniform(-0.15, 0.15)
        return max(0.10, base_lemon_price + price_change)

    def get_random_event():
        events = [
            {"name": "Obecný festival!", "effect": "Predaj limonády sa zdvojnásobuje!", "multiplier": 2},
            {"name": "Deň detí!", "effect": "Veľa smädných zákazníkov!", "multiplier": 1.6},
            {"name": "Miestne trhy.", "effect": "Viac ľudí v okolí.", "multiplier": 1.4},
            {"name": "Nič zvláštne.", "effect": "", "multiplier": 1},
            {"name": "Horúčava!", "effect": "Ešte väčší smäd!", "multiplier": 1.3},
            {"name": "Chladný vietor.", "effect": "Ľudia sa radšej zahrievajú inak.", "multiplier": 0.7},
            {"name": "Prach na cestách.", "effect": "Menej prechádzajúcich.", "multiplier": 0.8},
            {"name": "Sviatok v susednej dedine.", "effect": "Menej domácich zákazníkov.", "multiplier": 0.6}
        ]
        return random.choice(events)

    print("Vitajte v Žitavanoch!")
    print("Rozhodli ste sa stráviť prázdniny (júl a august) predajom osviežujúcej domácej limonády.")
    print("Vaším cieľom je zarobiť čo najviac peňazí počas týchto letných mesiacov!")
    print("Pamätajte, počasie a udalosti v obci ovplyvnia váš predaj.")
    print("Na 1 dávku limonády potrebujete 1 citrón.")
    print("Veľa šťastia!\n")

    weather_today = get_weather()
    weather_tomorrow = get_weather()
    lemon_price = get_lemon_price()

    while money >= 0 and day_number <= 62:
        print(f"\n--- Deň {day_number} ({day_of_week}. deň v týždni) ---")
        print(f"Peniaze: {money:.2f} €")
        print(f"Zásoba citrónov: {lemons}")
        print(f"Počasie na dnes: {weather_today}")
        if day_number < 62:
            print(f"Predpoveď počasia na zajtra: {weather_tomorrow}")
        print(f"Aktuálna cena citrónov: {lemon_price:.2f} €/kus")

        event = get_random_event()
        if event["multiplier"] != 1:
            print(f"\n--- Udalosť dňa: {event['name']} ---")
            print(event["effect"])

        daily_revenue = 0
        daily_cost = 0
        lemons_bought = 0
        drinks_sold = 0

        try:
            buy_lemons_str = input("Koľko citrónov chcete nakúpiť? ('koniec' pre ukončenie) ")
            if buy_lemons_str.lower() == "koniec":
                break
            buy_lemons = int(buy_lemons_str)
            if buy_lemons < 0:
                print("Počet citrónov nemôže byť záporný.")
                continue
            lemon_cost = buy_lemons * lemon_price
            if money >= lemon_cost:
                money -= lemon_cost
                lemons += buy_lemons
                daily_cost += lemon_cost
                lemons_bought = buy_lemons
                print(f"Nakúpili ste {buy_lemons} citrónov za {lemon_cost:.2f} €.")
            elif buy_lemons > 0:
                print("Nemáte dosť peňazí na nákup toľkých citrónov.")

            sell_price = float(input("Za akú cenu budete predávať limonádu? (€/dávka) "))
            if sell_price <= 0:
                print("Cena musí byť vyššia ako 0.")
                continue

            sales = calculate_sales(weather_today, sell_price, event["multiplier"])
            actual_sales = min(sales, lemons // lemons_per_drink)
            daily_revenue = actual_sales * sell_price
            money += daily_revenue
            lemons -= actual_sales * lemons_per_drink
            daily_profit = daily_revenue - daily_cost
            total_profit += daily_profit
            drinks_sold = actual_sales

            daily_stats.append({"day": day_number, "profit": daily_profit, "sales": actual_sales})

            print(f"\n--- Koniec dňa {day_number} ---")
            print(f"Počasie: {weather_today}")
            print(f"Predali ste {actual_sales} dávok limonády za {sell_price:.2f} €/dávka.")
            print(f"Príjmy za deň: +{daily_revenue:.2f} €")
            print(f"Náklady za deň: -{daily_cost:.2f} €")
            print(f"Zisk/strata za deň: {daily_profit:.2f} €")
            print(f"Aktuálne peniaze: {money:.2f} €")
            print(f"Zásoba citrónov: {lemons}")

            if day_of_week % 7 == 0:
                tax = total_profit * 0.15
                tax_amount = total_profit * 0.15
                money -= tax_amount
                print(f"\n--- Koniec týždňa ---")
                print(f"Celkový zisk za týždeň: {total_profit:.2f} €")
                print(f"Daň (15%): -{tax_amount:.2f} €")
                print(f"Aktuálne peniaze po zdanení: {money:.2f} €")
                total_profit = 0

            weather_today = weather_tomorrow
            weather_tomorrow = get_weather()
            lemon_price = get_lemon_price()
            day_of_week = (day_of_week % 7) + 1
            day_number += 1

        except ValueError:
            print("Neplatný vstup. Zadajte číslo.")
        except KeyboardInterrupt:
            print("\nKoniec hry.")
            break

    print("\n--- Koniec prázdnin! ---")
    if money >= 0:
        print(f"Celkovo ste zarobili {money:.2f} € počas vašich prázdnin.")
    else:
        print(f"Bohužiaľ, vaše podnikanie skončilo so stratou. Mali ste {money:.2f} €.")

    if daily_stats:
        best_day_profit = max(daily_stats, key=lambda x: x['profit'])
        worst_day_profit = min(daily_stats, key=lambda x: x['profit'])
        best_day_sales = max(daily_stats, key=lambda x: x['sales'])

        print("\n--- Štatistiky prázdnin ---")
        print(f"Najväčší zárobok za jeden deň: Deň {best_day_profit['day']} - {best_day_profit['profit']:.2f} €")
        print(f"Najväčšia strata za jeden deň: Deň {worst_day_profit['day']} - {worst_day_profit['profit']:.2f} €")
        print(f"Najviac predaných limonád za jeden deň: Deň {best_day_sales['day']} - {best_day_sales['sales']} dávok")
    else:
        print("Počas prázdnin ste nepredali žiadnu limonádu.")

    print("\nĎakujem, že ste si zahrali Žitavanskú Limonádu!")

if __name__ == "__main__":
    play_lemonade_stand_final_v4()