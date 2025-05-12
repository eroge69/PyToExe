
import ctypes

ctypes.windll.user32.MessageBoxW(
    0,
    "Por favor cerrar y guardar todos los archivos.\nEn 5 minutos se realizará una copia de seguridad de los archivos.",
    "Aviso de Copia de Seguridad",
    0x30
)
