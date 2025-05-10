import os

reemplazos = {
    "BAÃ‘O DE LA MEZQUITA": "BANO DE LA MEZQUITA",
    "EX CONVENTO DE SAN FRANCISO. PARADOR DE TURISMO": "EX CONVENTO DE SAN FRANCISO PARADOR DE TURISMO",
    "SANTA MARÃA DE LA ALHAMBRA": "SANTA MARIA DE LA ALHAMBRA",
    "TENERÃA": "TENERIA",
    "TENERÃ‘A": "TENERIA",
    "SANTA MARÃA DE LA ALHAMBRA": "SANTA MARIA DE LA ALHAMBRA",
    "BAÃ‘O": "BANO",
    "Ã‘": "N",
    "Ã": "I",
    "Ã": "A",
    "Ã‰": "E",
    "Ã“": "O",
    "Ãš": "U",
}

for nombre in os.listdir():
    nombre_nuevo = nombre
    for viejo, nuevo in reemplazos.items():
        if viejo in nombre_nuevo:
            nombre_nuevo = nombre_nuevo.replace(viejo, nuevo)

    if nombre != nombre_nuevo:
        print(f'Renombrando: "{nombre}" -> "{nombre_nuevo}"')
        os.rename(nombre, nombre_nuevo)
