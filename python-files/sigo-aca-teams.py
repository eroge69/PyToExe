import pyautogui
import time

# Coordenadas deseadas (por ejemplo: x = 500, y = 400)
x = 500
y = 400

while True:
    pyautogui.moveTo(x, y, duration=0.5)  # Mueve el cursor a (x, y)
    pyautogui.click()                     # Hace clic izquierdo
    time.sleep(240)                      # Espera 4 minutos (240 segundos)