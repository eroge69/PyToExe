import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import piexif
import os
import random
from datetime import datetime, timedelta

# Configuración inicial
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class MetadataApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modificador de Metadatos iPhone 📸")
        self.geometry("600x600")
        self.lista_fotos = []

        # --- Entradas ---
        self.label_fecha = ctk.CTkLabel(self, text="Fecha (YYYY-MM-DD):")
        self.label_fecha.pack(pady=5)
        self.entry_fecha = ctk.CTkEntry(self)
        self.entry_fecha.pack(pady=5)

        self.label_ubicacion = ctk.CTkLabel(self, text="Ubicación (latitud,longitud):")
        self.label_ubicacion.pack(pady=5)
        self.entry_ubicacion = ctk.CTkEntry(self)
        self.entry_ubicacion.pack(pady=5)

        self.label_modelo = ctk.CTkLabel(self, text="Modelo de iPhone:")
        self.label_modelo.pack(pady=5)
        self.entry_modelo = ctk.CTkEntry(self)
        self.entry_modelo.pack(pady=5)

        self.label_ios = ctk.CTkLabel(self, text="Versión de iOS:")
        self.label_ios.pack(pady=5)
        self.entry_ios = ctk.CTkEntry(self)
        self.entry_ios.pack(pady=5)

        # --- Botones ---
        self.btn_subir = ctk.CTkButton(self, text="Seleccionar Fotos", command=self.seleccionar_fotos)
        self.btn_subir.pack(pady=20)

        self.btn_generar = ctk.CTkButton(self, text="Generar y Guardar", command=self.procesar_fotos)
        self.btn_generar.pack(pady=10)

        self.label_estado = ctk.CTkLabel(self, text="")
        self.label_estado.pack(pady=10)

    def seleccionar_fotos(self):
        archivos = filedialog.askopenfilenames(
            title="Selecciona tus fotos",
            filetypes=[("Imágenes JPG", "*.jpg *.jpeg")]
        )
        self.lista_fotos = list(archivos)
        self.label_estado.configure(text=f"{len(self.lista_fotos)} fotos seleccionadas.")

    def procesar_fotos(self):
        if not self.lista_fotos:
            self.label_estado.configure(text="⚠️ Primero selecciona fotos.")
            return

        fecha_base = self.entry_fecha.get()
        ubicacion = self.entry_ubicacion.get()
        modelo = self.entry_modelo.get()
        version_ios = self.entry_ios.get()

        latitud, longitud = [x.strip() for x in ubicacion.split(",")]

        # Crear carpeta en escritorio
        escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        carpeta_destino = os.path.join(escritorio, "Metadatos_iPhone_Modificados")
        os.makedirs(carpeta_destino, exist_ok=True)

        for foto in self.lista_fotos:
            imagen = Image.open(foto)

            if imagen.format != "JPEG":
                continue  # solo procesamos JPEG

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
            exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = self.convert_gps(float(latitud))
            exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = b'W'
            exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = self.convert_gps(float(longitud))

            # Guardar imagen
            exif_bytes = piexif.dump(exif_dict)
            nombre_random = f"{random.randint(100000,999999)}.jpg"
            ruta_final = os.path.join(carpeta_destino, nombre_random)
            imagen.save(ruta_final, "jpeg", exif=exif_bytes)

        self.label_estado.configure(text="✅ Fotos modificadas y guardadas en Escritorio.")

    def convert_gps(self, coord):
        grados = int(coord)
        minutos = int((coord - grados) * 60)
        segundos = int(((coord - grados) * 60 - minutos) * 60 * 100)
        return ((grados,1),(minutos,1),(segundos,100))

if __name__ == "__main__":
    app = MetadataApp()
    app.mainloop()
