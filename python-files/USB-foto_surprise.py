import webbrowser
import time
from datetime import datetime

# Il link dell'immagine che mi hai dato
url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTjAS7ArkAkpmZ66x8IOYED8_CcB7yUZQFPbg&s"

# Imposta l'orario per aprire l'immagine (formato 24 ore: HH:MM)
orario = "10:30"  # Cambia con l'orario che preferisci

# Funzione per controllare l'orario e aprire il sito
def controlla_orario():
    while True:
        # Ottieni l'orario attuale
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Verifica se l'orario corrente corrisponde a quello desiderato
        if current_time == orario:
            print("Orario trovato! Avvio dell'immagine...")
            
            # Apri il link dell'immagine nel browser
            webbrowser.open(url)
            
            break  # Esci dal ciclo dopo aver aperto il link
        
        time.sleep(10)  # Controlla ogni 10 secondi

# Esegui la funzione
controlla_orario()
