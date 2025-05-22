import os
import time
import zipfile
import comtypes.client  # Requiere Windows + PowerPoint instalado

# Archivos y carpetas
ARCHIVO_NOMBRES = "nombres.txt"
PPTX_PLANTILLA = "plantilla.pptx"
CARPETA_SALIDA = "certificados_generados"
ZIP_SALIDA = "certificados.zip"

# Crear carpeta de salida si no existe
os.makedirs(CARPETA_SALIDA, exist_ok=True)

# Leer nombres desde el archivo .txt
with open(ARCHIVO_NOMBRES, "r", encoding="utf-8") as f:
    nombres = [line.strip() for line in f if line.strip()]

# Inicializar PowerPoint (COM)
powerpoint = comtypes.client.CreateObject("PowerPoint.Application")
powerpoint.Visible = 1

def generar_certificado(nombre, index):
    ppt = powerpoint.Presentations.Open(os.path.abspath(PPTX_PLANTILLA), WithWindow=False)
    slide = ppt.Slides(1)

    encontrado = False

    for shape in slide.Shapes:
        try:
            if shape.HasTextFrame and shape.TextFrame.HasText == -1:
                for paragraph in shape.TextFrame.TextRange.Paragraphs():
                    original = paragraph.Text
                    if "participante" in original.lower():
                        nuevo = original.lower().replace("participante", nombre)
                        paragraph.Text = nuevo
                        print(f"→ Reemplazando '{original.strip()}' por '{nuevo.strip()}'")
                        encontrado = True
        except Exception as e:
            print(f"[⚠️ Error procesando shape]: {e}")

    if not encontrado:
        print(f"[⚠️ Advertencia]: No se encontró 'participante' para {nombre}")

    output_path = os.path.abspath(os.path.join(CARPETA_SALIDA, f"certificado_{index+1}_{nombre}.pdf"))
    ppt.SaveAs(output_path, FileFormat=32)  # Guardar como PDF
    ppt.Close()
    time.sleep(0.5)

# Generar certificados
for i, nombre in enumerate(nombres):
    print(f"\n📄 Generando certificado para: {nombre}")
    generar_certificado(nombre, i)

# Comprimir en ZIP
with zipfile.ZipFile(ZIP_SALIDA, "w") as zipf:
    for filename in os.listdir(CARPETA_SALIDA):
        filepath = os.path.join(CARPETA_SALIDA, filename)
        zipf.write(filepath, arcname=filename)

print(f"\n✅ Todos los certificados fueron generados correctamente.")
print(f"🗂 ZIP disponible: {ZIP_SALIDA}")

# Cerrar PowerPoint
powerpoint.Quit()
