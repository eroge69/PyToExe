import os
import random
import piexif
from PIL import Image
from datetime import datetime, timedelta
from tkinter import filedialog, Tk

def pedir_datos_usuario():
    fecha = input("Introduce la fecha (YYYY-MM-DD): ").strip()
    ubicacion = input("Introduce la ubicación (latitud,longitud): ").strip()
    modelo = input("Introduce el modelo de iPhone: ").strip()
    version_ios = input("Introduce la versión de iOS: ").strip()
    return fecha, ubicacion, modelo, version_ios

def seleccionar_carpeta():
    root = Tk()
    root.withdraw()
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta con las fotos")
    return carpeta

def convertir_gps(coord):
    grados = int(coord)
    minutos = int((coord - grados) * 60)
    segundos = int(((coord - grados) * 60 - minutos) * 60 * 100)
    return ((grados,1),(minutos,1),(segundos,100))

def procesar_fotos(carpeta, fecha_base, ubicacion, modelo, version_ios):
    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    carpeta_destino = os.path.join(escritorio, "Metadatos_iPhone_Modificados")
    os.makedirs(carpeta_destino, exist_ok=True)

    latitud, longitud = [x.strip() for x in ubicacion.split(",")]

    fotos = [f for f in os.listdir(carpeta) if f.lower().endswith(('.jpg', '.jpeg'))]

    if not fotos:
        print("⚠️ No se encontraron fotos JPG o JPEG en la carpeta.")
        return

    for idx, foto in enumerate(fotos, 1):
        ruta_foto = os.path.join(carpeta, foto)
        imagen = Image.open(ruta_foto)

        if imagen.format != "JPEG":
            continue  # Solo procesamos JPEG

        exif_dict = piexif.load(imagen.info.get("exif", b""))

        # Generar hora aleatoria
        fecha_dt = datetime.strptime(fecha_base, "%Y-%m-%d")
        hora_random = timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        fecha_hora_final = fecha_dt + hora_random
        fecha_formateada = fecha_hora_final.strftime("%Y:%m:%d %H:%M:%S")

        # --- Editar EXIF ---
        exif_dict['0th'][piexif.ImageIFD.Make] = "Apple".encode()
        exif_dict['0th'][piexif.ImageIFD.Model] = modelo.encode()
        exif_dict['0th'][piexif.ImageIFD.Software] = f"{modelo} {version_ios}".encode()
        exif_dict['0th'][piexif.ImageIFD.Orientation] = random.choice([1, 6, 8])

        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = fecha_formateada.encode()
        exif_dict['Exif'][piexif.ExifIFD.LensMake] = "Apple".encode()
        exif_dict['Exif'][piexif.ExifIFD.LensModel] = modelo.encode()
        exif_dict['Exif'][piexif.ExifIFD.FNumber] = (int(random.uniform(16, 28)), 10)
        exif_dict['Exif'][piexif.ExifIFD.ExposureTime] = (1, random.choice([30, 60, 125, 250, 500, 1000]))
        exif_dict['Exif'][piexif.ExifIFD.ISOSpeedRatings] = random.choice([32, 64, 125, 250, 400, 800, 1600])

        exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = b'N'
        exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = convertir_gps(float(latitud))
        exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = b'W'
        exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = convertir_gps(float(longitud))

        # Guardar imagen
        exif_bytes = piexif.dump(exif_dict)
        nombre_random = f"{random.randint(100000,999999)}.jpg"
        ruta_final = os.path.join(carpeta_destino, nombre_random)
        imagen.save(ruta_final, "jpeg", exif=exif_bytes)

        print(f"[{idx}/{len(fotos)}] Foto {foto} procesada como {nombre_random}")

    print("\n✅ Todas las fotos fueron procesadas y guardadas en el Escritorio.")

if __name__ == "__main__":
    fecha_base, ubicacion, modelo, version_ios = pedir_datos_usuario()
    carpeta_fotos = seleccionar_carpeta()
    procesar_fotos(carpeta_fotos, fecha_base, ubicacion, modelo, version_ios)
