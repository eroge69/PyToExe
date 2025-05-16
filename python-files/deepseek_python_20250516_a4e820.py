def main():
    print("\n" + "="*60)
    print("SISTEMA DE SELECCIÓN DE TÉCNICA DE INYECCIÓN PARA PBB")
    print("="*60 + "\n")

    # Paso 1: Evaluar presión del yacimiento
    print("1. EVALUACIÓN DE PRESIÓN DEL YACIMIENTO")
    p_yac = float(input("Ingrese la presión del yacimiento (psi): "))
    
    if p_yac < 2000:
        print("\n>> Yacimiento de BAJA PRESIÓN (<2000 psi)")
        evaluar_baja_presion()
    elif 2000 <= p_yac <= 5000:
        print("\n>> Yacimiento de PRESIÓN MODERADA (2000-5000 psi)")
        evaluar_presion_moderada()
    else:
        print("\n>> Yacimiento de ALTA PRESIÓN (>5000 psi)")
        evaluar_alta_presion()

def evaluar_baja_presion():
    print("\n2. EVALUACIÓN DE CARACTERÍSTICAS DE LA FORMACIÓN (BAJA PRESIÓN)")
    consolidada = input("¿La formación es consolidada? (s/n): ").lower() == 's'
    
    if consolidada:
        print("\n>> Técnicas recomendadas:")
        print("- Gas Lift (Nitrógeno/Aire)")
        print("- Perforación con Aire")
    else:
        sensible_agua = input("¿La formación es sensible al agua? (s/n): ").lower() == 's'
        print("\n>> Técnicas recomendadas:")
        if sensible_agua:
            print("- Espuma Estabilizada")
            print("- Sistema Base Aceite")
        else:
            print("- Salmueras Livianas (KCl/CaCl₂)")
    
    validar_restricciones()

def evaluar_presion_moderada():
    print("\n2. EVALUACIÓN DE CARACTERÍSTICAS DE LA FORMACIÓN (PRESIÓN MODERADA)")
    permeabilidad = float(input("Ingrese la permeabilidad de la formación (mD): "))
    
    if permeabilidad > 100:
        print("\n>> Alta permeabilidad (>100 mD)")
        print("Técnicas recomendadas:")
        print("- Gas Lift con Nitrógeno")
        print("- Microburbujas en Lodo Base Agua")
    else:
        fracturada = input("¿La formación está fracturada? (s/n): ").lower() == 's'
        print("\n>> Técnicas recomendadas:")
        if fracturada:
            print("- Espuma de Alta Estabilidad")
        else:
            print("- Lodo Base Aceite con Densidad Controlada")
    
    validar_restricciones()

def evaluar_alta_presion():
    print("\n2. EVALUACIÓN DE CARACTERÍSTICAS DE LA FORMACIÓN (ALTA PRESIÓN)")
    profundidad = float(input("Ingrese la profundidad del pozo (m): "))
    
    if profundidad > 3000:
        print("\n>> Pozo PROFUNDO (>3000 m)")
        print("Técnicas recomendadas:")
        print("- Sistema Sintético (SBM) con Gas Asistido (Nitrógeno)")
        print("- Lodo Oil-Based con Gas")
    else:
        restricciones = input("¿Hay restricciones ambientales? (s/n): ").lower() == 's'
        print("\n>> Técnicas recomendadas:")
        if restricciones:
            print("- Salmuera Pesada (CaBr₂/ZnBr₂)")
        else:
            print("- Diesel/Gas Oil con Aditivos")
    
    validar_restricciones()

def validar_restricciones():
    print("\n3. VALIDACIÓN FINAL (FACTORES OPERATIVOS Y ECONÓMICOS)")
    
    print("\nDisponibilidad de equipos:")
    print("1. Compresores de gas")
    print("2. Generadores de espuma")
    print("3. Sistemas de inyección")
    equipos = input("¿Qué equipos están disponibles? (ingrese números separados por comas): ")
    
    print("\nConsideraciones económicas:")
    costo = input("Nivel de presupuesto (bajo/medio/alto): ").lower()
    
    print("\nRestricciones ambientales:")
    ambiental = input("¿Hay regulaciones ambientales estrictas? (s/n): ").lower() == 's'
    
    print("\n" + "="*60)
    print("RECOMENDACIÓN FINAL:")
    print("Considere las técnicas sugeridas anteriormente junto con:")
    print(f"- Equipos disponibles: {equipos}")
    print(f"- Presupuesto: {costo}")
    print(f"- Restricciones ambientales: {'Sí' if ambiental else 'No'}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()