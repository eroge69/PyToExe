
def generar_fixture(equipos):
    if len(equipos) % 2 != 0:
        equipos.append("Descansa")

    n = len(equipos)
    rondas = n - 1
    fixture = []

    for i in range(rondas):
        ronda = []
        for j in range(n // 2):
            local = equipos[j]
            visitante = equipos[n - 1 - j]
            if local != "Descansa" and visitante != "Descansa":
                ronda.append((local, visitante))
        fixture.append(ronda)
        equipos = [equipos[0]] + [equipos[-1]] + equipos[1:-1]

    return fixture

def main():
    print("=== Generador de Fixture Todos contra Todos ===")
    equipos = []
    while True:
        nombre = input("Ingresa el nombre del equipo (o presiona Enter para terminar): ")
        if nombre == "":
            break
        equipos.append(nombre)

    if len(equipos) < 2:
        print("Se necesitan al menos dos equipos.")
        return

    fixture = generar_fixture(equipos)

    print("\n=== Fixture Generado ===")
    for i, ronda in enumerate(fixture):
        print(f"\nRonda {i + 1}:")
        for local, visitante in ronda:
            print(f"  {local} vs {visitante}")

if __name__ == "__main__":
    main()
