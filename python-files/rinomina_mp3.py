
import os

# Inserisci qui il percorso della cartella con i file MP3
cartella = r"C:\Users\pc\Desktop\Music\pt 2"
prefisso = "SpotiDownloader.com - "

# Scorri tutti i file nella cartella
for nome_file in os.listdir(cartella):
    if nome_file.endswith(".mp3") and nome_file.startswith(prefisso):
        nuovo_nome = nome_file[len(prefisso):]
        percorso_vecchio = os.path.join(cartella, nome_file)
        percorso_nuovo = os.path.join(cartella, nuovo_nome)
        os.rename(percorso_vecchio, percorso_nuovo)

print("Rinominati tutti i file con successo.")
