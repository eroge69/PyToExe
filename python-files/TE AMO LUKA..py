
import os
import time
import random
import sys

# Verifica si está en Windows para usar color
if os.name == 'nt':
    os.system('color 0D')  # Fondo negro, texto rosa (magenta claro)

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mensaje_inicio():
    limpiar_pantalla()
    print('''\n
"No fue un error de seguridad...
fue un acceso intencional,
para que sepas que me importas."\n''')
    time.sleep(3)

def mostrar_te_amo():
    chars = ["TE AMO"]
    while True:
        limpiar_pantalla()
        for _ in range(30):
            linea = ""
            for _ in range(80):
                if random.random() > 0.85:
                    linea += random.choice(chars)
                else:
                    linea += " "
            print(linea)
        time.sleep(0.1)

try:
    mensaje_inicio()
    mostrar_te_amo()
except KeyboardInterrupt:
    print("\nFin del mensaje.")
