
import os
import re
import sys
import pdfplumber

def extraer_creditos_de_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            texto = ""
            for pagina in pdf.pages:
                texto += pagina.extract_text() or ""
            coincidencias = re.findall(r"(\d+[\.,]?\d*)\s+créditos", texto, re.IGNORECASE)
            if coincidencias:
                creditos_str = coincidencias[0].replace(",", ".")
                return float(creditos_str)
    except Exception as e:
        print(f"Error al procesar {pdf_path}: {e}")
    return 0.0

def main():
    carpeta = os.path.dirname(os.path.abspath(__file__))
    archivos_pdf = [f for f in os.listdir(carpeta) if f.lower().endswith(".pdf")]

    total_creditos = 0.0
    print("Analizando certificados PDF en la carpeta actual...\n")

    for archivo in archivos_pdf:
        ruta_pdf = os.path.join(carpeta, archivo)
        creditos = extraer_creditos_de_pdf(ruta_pdf)
        if creditos > 0:
            print(f"{archivo}: {creditos} créditos")
        else:
            print(f"{archivo}: No se encontraron créditos")
        total_creditos += creditos

    print("\nResumen:")
    print(f"Total acumulado: {total_creditos:.1f} créditos")
    print(f"Créditos restantes para llegar a 50: {max(0, 50 - total_creditos):.1f} créditos")

if __name__ == "__main__":
    main()
