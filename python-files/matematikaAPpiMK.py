import random
import math
import matplotlib.pyplot as plt
import os


def monte_carlo_pi(num_points: int, ceo_krug: bool):
    inside_circle = 0
    x_inside = []
    y_inside = []
    x_outside = []
    y_outside = []

    for _ in range(num_points):
        if ceo_krug:
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
        else:
            x = random.uniform(0, 1)
            y = random.uniform(0, 1)

        if x**2 + y**2 <= 1:
            inside_circle += 1
            x_inside.append(x)
            y_inside.append(y)
        else:
            x_outside.append(x)
            y_outside.append(y)

    pi_approx = (4 * inside_circle) / num_points
    return pi_approx, x_inside, y_inside, x_outside, y_outside

def prikazi_grafiku(x_in, y_in, x_out, y_out, pi_approx, save_image, ceo_krug):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(x_in, y_in, color='blue', s=1, label='Unutar kruga')
    ax.scatter(x_out, y_out, color='red', s=1, label='Van kruga')

    krug = plt.Circle((0, 0), 1, color='black', fill=False, linewidth=1.2, linestyle='--')
    ax.add_patch(krug)
    if ceo_krug:
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
    else:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    ax.set_aspect('equal', adjustable='box')

    ax.set_title(f"Monte Karlo aproksimacija π\nπ ≈ {pi_approx}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    ax.grid(True)

    if save_image:
        filename = "monte_carlo_pi.png"
        plt.savefig(filename)
        print(f"Slika je sačuvana kao '{filename}' u direktorijumu: {os.getcwd()}")
    plt.show()

    # Objašnjenje nakon vizualizacije
    print("\n🔍 Objašnjenje metode:")
    if ceo_krug:
        print("Koristimo ceo krug unutar kvadrata [-1,1] x [-1,1].")
        print("Površina kvadrata je 4, površina kruga je π * r² = π.")
    else:
        print("Koristimo četvrtinu kruga unutar kvadrata [0,1] x [0,1].")
        print("Površina kvadrata je 1, površina četvrtine kruga je π/4.")
    print("Odnos tačaka unutar kruga prema ukupnom broju tačaka daje aproksimaciju π.")
    print("Formula: π ≈ 4 * (broj tačaka unutar kruga / ukupno tačaka)")

def main():
    print("Monte Karlo aproksimacija za broj PI")

    try:
        num_points = int(input("Unesite broj nasumičnih tačaka (npr. 1000): "))
        repetitions = int(input("Unesite broj ponavljanja simulacije: "))
    except ValueError:
        print("Unos mora biti ceo broj.")
        return

    if num_points <= 0 or repetitions <= 0:
        print("Uneti brojevi moraju biti pozitivni.")
        return

    ceo_krug = input("Da li želite da koristite ceo krug (umesto klasične četvrtine)? (da/ne): ").lower() == 'da'
    vizuelizacija = input("Da li želite grafički prikaz rezultata? (da/ne): ").lower() == 'da'
    sacuvaj_sliku = False
    if vizuelizacija:
        sacuvaj_sliku = input("Da li želite da sačuvate sliku? (da/ne): ").lower() == 'da'

    # Mini kviz
    print("\n🧠 Mini kviz! Kako mislite da će izgledati aproksimacija π?")
    print("A) Manje od 3.0\nB) Između 3.0 i 3.2\nC) Više od 3.2")
    odgovor = input("Vaš odgovor (A/B/C): ").strip().upper()

    pi_values = []
    for i in range(repetitions):
        pi_estimate, x_in, y_in, x_out, y_out = monte_carlo_pi(num_points, ceo_krug)
        pi_values.append(pi_estimate)
        print(f"Simulacija {i+1}: π ≈ {pi_estimate:.6f}")

        if vizuelizacija and i == repetitions - 1:
            prikazi_grafiku(x_in, y_in, x_out, y_out, pi_estimate, sacuvaj_sliku, ceo_krug)

    avg_pi = sum(pi_values) / repetitions
    greska = abs(math.pi - avg_pi)
    rel_greska = (greska / math.pi) * 100

    print(f"\nProsečna aproksimacija π: {avg_pi:.6f}")
    print(f"Stvarna vrednost π: {math.pi:.6f}")
    print(f"Apsolutna greška: {greska:.6f}")
    print(f"Relativna greška: {rel_greska:.4f}%")

    if greska < 0.01:
        print("✔️ Izvanredno! Vaša aproksimacija je veoma precizna.")
    elif greska < 0.05:
        print("👍 Dobar rezultat! Možete povećati broj tačaka za veću preciznost.")
    else:
        print("⚠️ Veća odstupanja – pokušajte sa više tačaka.")

    if (avg_pi < 3.0 and odgovor == 'A') or (3.0 <= avg_pi <= 3.2 and odgovor == 'B') or (avg_pi > 3.2 and odgovor == 'C'):
        print("🎉 Vaša pretpostavka je bila tačna!")
    else:
        print("❌ Vaša pretpostavka nije bila tačna, ali ste sada naučili više!")

    sacuvaj = input("Da li želite da sačuvate rezultate u fajl? (da/ne): ").lower() == 'da'
    if sacuvaj:
        with open("rezultat_pi.txt", "w") as f:
            f.write(f"Monte Karlo aproksimacija π\n")
            f.write(f"Korišćen metod: {'ceo krug' if ceo_krug else 'četvrtina kruga'}\n")
            f.write(f"Broj tačaka po simulaciji: {num_points}\n")
            f.write(f"Broj ponavljanja: {repetitions}\n")
            f.write(f"Prosečna aproksimacija π: {avg_pi}\n")
            f.write(f"Stvarna vrednost π: {math.pi}\n")
            f.write(f"Apsolutna greška: {greska}\n")
            f.write(f"Relativna greška: {rel_greska:.4f}%\n")
        print("Rezultati su sačuvani u 'rezultat_pi.txt'.")

if __name__ == "__main__":
    main()
