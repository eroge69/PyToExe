import time
import hashlib
import shutil
import os

# Chemin réseau partagé
FICHIER_PARTAGE = r"\\172.33.240.120\d\Echanges\Huseyin ORAL\copier coller pc a pc.txt"

# Copie locale
FICHIER_LOCAL = "copie_locale.txt"

def calculer_hash(chemin):
    """Retourne le hash md5 du contenu d'un fichier (ou None si le fichier n'existe pas)."""
    try:
        with open(chemin, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None

def copier(source, destination):
    try:
        shutil.copy2(source, destination)
        print(f"[OK] Copié : {source} => {destination}")
    except Exception as e:
        print(f"[ERREUR] Copie échouée : {e}")

def boucle_sync(intervalle=2):
    print("[DÉMARRÉ] Synchronisation sans watchdog, intervalle:", intervalle, "secondes")

    while True:
        hash_local = calculer_hash(FICHIER_LOCAL)
        hash_partage = calculer_hash(FICHIER_PARTAGE)

        if hash_local is None and hash_partage:
            # Première fois : récupère depuis le réseau
            print("[INFO] Aucune copie locale. Téléchargement du fichier partagé.")
            copier(FICHIER_PARTAGE, FICHIER_LOCAL)

        elif hash_local and hash_partage and hash_local != hash_partage:
            # Conflit : qui a changé ?
            mtime_local = os.path.getmtime(FICHIER_LOCAL)
            mtime_partage = os.path.getmtime(FICHIER_PARTAGE)

            if mtime_local > mtime_partage:
                print("[SYNC] Le fichier local est plus récent. Mise à jour du fichier réseau.")
                copier(FICHIER_LOCAL, FICHIER_PARTAGE)
            else:
                print("[SYNC] Le fichier réseau est plus récent. Mise à jour du fichier local.")
                copier(FICHIER_PARTAGE, FICHIER_LOCAL)

        time.sleep(intervalle)

if __name__ == "__main__":
    boucle_sync()
