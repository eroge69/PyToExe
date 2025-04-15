import subprocess
import time
import pyautogui

# Configura il nome del dispositivo Miracast a cui vuoi connetterti
MIRACAST_DEVICE_NAME = "Xhadapter-9E8A0F"

def start_wireless_projection():
    try:
        print("Avvio della proiezione wireless...")

        # Apri il menu "Connetti" di Windows (Win + K)
        pyautogui.hotkey('win', 'k')
        time.sleep(2)  # Attendi che il menu si apra

        # Seleziona il dispositivo Miracast
        pyautogui.write(MIRACAST_DEVICE_NAME)  # Scrivi il nome del dispositivo
        time.sleep(1)
        pyautogui.hotkey('tab')
        pyautogui.press('enter')  # Premi Invio per selezionare il dispositivo

        print(f"Proiezione wireless avviata sul dispositivo: {MIRACAST_DEVICE_NAME}")
    except Exception as e:
        print(f"Errore durante l'avvio della proiezione wireless: {e}")

if __name__ == "__main__":
    # Avvia la proiezione wireless
    start_wireless_projection()

    # Mantieni aperta la finestra del terminale (solo su Windows)
    input("Premi Invio per uscire...")