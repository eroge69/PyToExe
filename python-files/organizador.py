import os
import shutil

# 📁 Ruta de la carpeta que quieres organizar
# Ejemplo: r"C:\Users\TuUsuario\Downloads"
carpeta_objetivo = r"C:\Ruta\A\Tu\Carpeta"

# 📦 Categorías de archivos y sus extensiones
tipos_archivos = {
    "Imágenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Documentos": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv"],
    "Música": [".mp3", ".wav", ".ogg"],
    "Instaladores": [".exe", ".msi"],
    "Comprimidos": [".zip", ".rar", ".7z"],
    "Otros": []
}

def organizar_archivos(carpeta):
    for archivo in os.listdir(carpeta):
        ruta_archivo = os.path.join(carpeta, archivo)

        # Saltar si es una carpeta
        if os.path.isdir(ruta_archivo):
            continue

        # Obtener extensión
        _, extension = os.path.splitext(archivo)
        extension = extension.lower()

        # Buscar categoría
        categoria_encontrada = "Otros"
        for categoria, extensiones in tipos_archivos.items():
            if extension in extensiones:
                categoria_encontrada = categoria
                break

        # Crear carpeta destino si no existe
        carpeta_destino = os.path.join(carpeta, categoria_encontrada)
        os.makedirs(carpeta_destino, exist_ok=True)

        # Mover archivo
        shutil.move(ruta_archivo, os.path.join(carpeta_destino, archivo))
        print(f"🔄 Movido: {archivo} → {categoria_encontrada}/")

    print("\n✅ Organización completa.")

# Ejecutar función
organizar_archivos(carpeta_objetivo)