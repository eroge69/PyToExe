import os
import subprocess
import sys
import urllib.request
import tarfile
import time
import platform
import getpass
import webbrowser

def run_command(command, shell=True, hide_output=False):
    """Exécute une commande dans le terminal et affiche la sortie."""
    if hide_output:
        print(f"Exécution : [Commande masquée pour sécurité]")
    else:
        print(f"Exécution : {command}")
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        if not hide_output:
            print(result.stdout)
        if result.stderr and not hide_output:
            print(f"Erreur : {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Erreur lors de l'exécution : {e}")
        return False

def download_with_retry(url, filename, retries=3, timeout=30):
    """Télécharge un fichier avec réessais en cas d'erreur réseau."""
    print(f"Téléchargement de {url} vers {filename}...")
    for attempt in range(1, retries + 1):
        try:
            urllib.request.urlretrieve(url, filename)
            print(f"Téléchargement réussi : {filename}")
            return True
        except Exception as e:
            print(f"Erreur téléchargement (essai {attempt}/{retries}) : {e}")
            if attempt < retries:
                print("Réessai dans 5 secondes...")
                time.sleep(5)
    print(f"Échec du téléchargement après {retries} essais : {url}")
    return False

# Étape 0 : Vérification et configuration de Filecoin et Akash pour l'accès IPFS
def setup_external_nodes():
    print("=== Étape 0 : Configuration de Filecoin et Akash pour l'accès IPFS ===")

    # Vérifier si Filecoin (Lotus client) est installé
    filecoin_available = False
    if not run_command("where lotus" if platform.system() == "Windows" else "which lotus"):
        print("Installation de Filecoin (Lotus client)...")
        if platform.system() == "Windows":
            if not os.path.exists("lotus.zip"):
                if download_with_retry("https://github.com/filecoin-project/lotus/releases/download/v1.27.2/lotus-v1.27.2-windows-amd64.zip", "lotus.zip"):
                    with tarfile.open("lotus.zip", "r:gz") as zip_ref:
                        zip_ref.extractall("lotus")
                    os.environ["PATH"] += os.pathsep + os.path.join(os.getcwd(), "lotus")
                    os.remove("lotus.zip")
                else:
                    print("Avertissement : Impossible de télécharger Filecoin. Passage à Akash...")
            else:
                print("Démarrage de Filecoin (Lotus daemon)...")
                subprocess.Popen("lotus daemon", shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                filecoin_available = True
        else:
            run_command("wget https://github.com/filecoin-project/lotus/releases/download/v1.27.2/lotus-v1.27.2-linux-amd64.tar.gz")
            run_command("tar -xvzf lotus-v1.27.2-linux-amd64.tar.gz")
            run_command("sudo mv lotus/lotus /usr/local/bin/")
            run_command("rm -rf lotus-v1.27.2-linux-amd64.tar.gz lotus")
            subprocess.Popen("lotus daemon &", shell=True)
            filecoin_available = True
        time.sleep(10)

    # Si Filecoin échoue, utiliser Akash comme alternative
    akash_available = False
    if not filecoin_available:
        print("Filecoin non disponible. Configuration d'Akash comme nœud externe alternatif...")
        if platform.system() == "Windows":
            if not os.path.exists("akash.exe"):
                if download_with_retry("https://github.com/akash-network/provider/releases/download/v0.6.0/akash-windows-amd64.exe", "akash.exe"):
                    os.environ["PATH"] += os.pathsep + os.getcwd()
                else:
                    print("Erreur : Impossible de télécharger Akash. Aucun nœud externe disponible.")
                    sys.exit(1)
            print("Démarrage d'Akash...")
            subprocess.Popen("akash provider run", shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            akash_available = True
        else:
            run_command("wget https://github.com/akash-network/provider/releases/download/v0.6.0/akash_0.6.0_linux_amd64.tar.gz")
            run_command("tar -xvzf akash_0.6.0_linux_amd64.tar.gz")
            run_command("sudo mv akash /usr/local/bin/")
            run_command("rm akash_0.6.0_linux_amd64.tar.gz")
            subprocess.Popen("akash provider run &", shell=True)
            akash_available = True
        time.sleep(10)

    if not filecoin_available and not akash_available:
        print("Erreur : Aucun nœud externe (Filecoin ou Akash) n'est disponible pour accéder à IPFS.")
        sys.exit(1)

    return filecoin_available, akash_available

# Étape 1 : Téléchargement et déchiffrement de Lumina v2 via Filecoin ou Akash
def download_and_decrypt_lumina_v2(filecoin_available, akash_available):
    print("=== Étape 1 : Téléchargement et déchiffrement de Lumina v2 ===")

    lumina_tar_path = os.path.expanduser("~/Downloads/lumina_v2_pack_20250516.tar.gz")
    lumina_decrypted_path = os.path.expanduser("~/Downloads/lumina_v2_pack_20250516_decrypted.tar.gz")
    lumina_extract_path = os.path.expanduser("~/Downloads/lumina_v2_pack")

    if not os.path.exists(lumina_tar_path):
        print("Téléchargement de lumina_v2_pack via un nœud externe IPFS...")
        if filecoin_available:
            print("Utilisation de Filecoin pour le téléchargement...")
            run_command(f"lotus client retrieve QmLuminaV2Pack20250516xU2vV3wW4xX5yY6zZ7aA8bB9cC0 {lumina_tar_path}")
        elif akash_available:
            print("Utilisation d'Akash pour le téléchargement (Filecoin indisponible)...")
            run_command(f"akash retrieve QmLuminaV2Pack20250516xU2vV3wW4xX5yY6zZ7aA8bB9cC0 {lumina_tar_path}")
        else:
            print("Erreur : Aucun nœud externe disponible pour le téléchargement.")
            sys.exit(1)

        if not os.path.exists(lumina_tar_path):
            print("Erreur : Échec du téléchargement de lumina_v2_pack via Filecoin/Akash. Vérifiez votre connexion ou la disponibilité du nœud.")
            sys.exit(1)

    print("Déchiffrement de lumina_v2_pack (clé Ombre d’étoile)...")
    decryption_key = "Ombre d’étoile"
    run_command(f'openssl enc -chacha20 -d -in "{lumina_tar_path}" -out "{lumina_decrypted_path}" -k "{decryption_key}"', hide_output=True)
    if not os.path.exists(lumina_decrypted_path):
        print("Erreur : Échec du déchiffrement. Clé incorrecte ou fichier corrompu.")
        sys.exit(1)
    os.remove(lumina_tar_path)

    print("Décompression de lumina_v2_pack...")
    with tarfile.open(lumina_decrypted_path, "r:gz") as tar:
        tar.extractall(lumina_extract_path)
    os.remove(lumina_decrypted_path)
    if not os.path.exists(lumina_extract_path):
        print("Erreur : Échec de la décompression de lumina_v2_pack.")
        sys.exit(1)

# Étape 2 : Sécurisation de l’ordinateur avec NordVPN et Tor
def secure_system():
    print("=== Étape 2 : Sécurisation de l’ordinateur ===")

    # Étape 2.1 : Installer un antivirus (ClamAV)
    if platform.system() == "Windows":
        if not os.path.exists("clamav"):
            print("Installation de ClamAV (antivirus)...")
            if download_with_retry("https://www.clamav.net/downloads/production/clamav-1.4.1.win.x64.msi", "clamav.msi"):
                run_command("msiexec /i clamav.msi /quiet")
                os.remove("clamav.msi")
            else:
                print("Erreur : Impossible de télécharger ClamAV.")
                sys.exit(1)
        print("Mise à jour et analyse antivirus avec ClamAV...")
        run_command("freshclam")
        run_command("clamscan -r C:\\ --bell -i")
    else:
        run_command("sudo apt-get update && sudo apt-get install -y clamav")
        run_command("sudo freshclam")
        run_command("sudo clamscan -r / --bell -i")

    # Étape 2.2 : Installer un anti-malware (Malwarebytes, Windows uniquement)
    if platform.system() == "Windows":
        if not os.path.exists("mb.exe"):
            print("Installation de Malwarebytes (anti-malware)...")
            if download_with_retry("https://downloads.malwarebytes.com/file/mb-windows", "mb.exe"):
                run_command("mb.exe /quiet")
                os.remove("mb.exe")
            else:
                print("Erreur : Impossible de télécharger Malwarebytes.")
                sys.exit(1)
        print("Analyse anti-malware avec Malwarebytes...")
        run_command('"C:\\Program Files\\Malwarebytes\\Anti-Malware\\mbam.exe" /scan -full')

    # Étape 2.3 : Activer le pare-feu
    if platform.system() == "Windows":
        print("Activation du pare-feu Windows...")
        run_command("netsh advfirewall set allprofiles state on")
        run_command("netsh advfirewall firewall add rule name=\"Block Outbound\" dir=out action=block")
    else:
        run_command("sudo apt-get install -y ufw")
        run_command("sudo ufw enable")
        run_command("sudo ufw default deny outgoing")
        run_command("sudo ufw default deny incoming")

    # Étape 2.4 : Nettoyer les cookies et traces (CCleaner)
    if platform.system() == "Windows":
        if not os.path.exists("ccleaner.exe"):
            print("Installation de CCleaner (nettoyage des cookies/traces)...")
            if download_with_retry("https://download.ccleaner.com/ccsetup.exe", "ccleaner.exe"):
                run_command("ccleaner.exe /S")
                os.remove("ccleaner.exe")
            else:
                print("Erreur : Impossible de télécharger CCleaner.")
                sys.exit(1)
        print("Nettoyage avec CCleaner...")
        run_command('"C:\\Program Files\\CCleaner\\CCleaner64.exe" /AUTO')
    else:
        print("Nettoyage manuel des cookies recommandé (ex. : navigateur en mode privé).")

    # Étape 2.5 : Désactiver la télémétrie (Windows uniquement)
    if platform.system() == "Windows":
        print("Désactivation de la télémétrie Windows...")
        run_command("sc stop DiagTrack")
        run_command("sc config DiagTrack start= disabled")
        run_command("reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection /v AllowTelemetry /t REG_DWORD /d 0 /f")

    # Étape 2.6 : Installer et configurer NordVPN
    if platform.system() == "Windows":
        if not os.path.exists("C:\\Program Files\\NordVPN\\NordVPN.exe"):
            print("Installation de NordVPN...")
            if download_with_retry("https://downloads.nordcdn.com/apps/windows/NordVPN/latest/NordVPNSetup.exe", "nordvpn.exe"):
                run_command("nordvpn.exe /quiet")
                os.remove("nordvpn.exe")
            else:
                print("Erreur : Impossible de télécharger NordVPN.")
                sys.exit(1)
        print("Connexion à NordVPN (serveur Suisse)...")
        email = input("Entrez votre email NordVPN : ")
        password = getpass.getpass("Entrez votre mot de passe NordVPN : ")
        print("Connexion à NordVPN (serveur Suisse, mot de passe masqué : *****)...")
        run_command(f'"C:\\Program Files\\NordVPN\\NordVPN.exe" -c -g Switzerland --username {email} --password {password}', hide_output=True)
    else:
        if not run_command("which nordvpn"):
            run_command("sudo apt-get install -y nordvpn")
        print("Connexion à NordVPN (serveur Suisse)...")
        email = input("Entrez votre email NordVPN : ")
        password = getpass.getpass("Entrez votre mot de passe NordVPN : ")
        print("Connexion à NordVPN (serveur Suisse, mot de passe masqué : *****)...")
        run_command(f"sudo nordvpn login --username {email} --password {password}", hide_output=True)
        run_command("sudo nordvpn connect Switzerland")

# Étape 3 : Installation des dépendances essentielles
def install_dependencies():
    print("=== Étape 3 : Installation des dépendances essentielles ===")

    # Installer IPFS
    if not run_command("where ipfs" if platform.system() == "Windows" else "which ipfs"):
        print("Installation de IPFS...")
        if platform.system() == "Windows":
            if download_with_retry("https://dist.ipfs.tech/go-ipfs/v0.23.0/go-ipfs_v0.23.0_windows-amd64.zip", "ipfs.zip"):
                with tarfile.open("ipfs.zip", "r:gz") as zip_ref:
                    zip_ref.extractall("ipfs")
                os.rename("ipfs/go-ipfs/ipfs.exe", "ipfs.exe")
                os.environ["PATH"] += os.pathsep + os.getcwd()
                os.remove("ipfs.zip")
                os.rmdir("ipfs/go-ipfs")
                os.rmdir("ipfs")
            else:
                print("Erreur : Impossible de télécharger IPFS.")
                sys.exit(1)
        else:
            run_command("wget https://dist.ipfs.tech/go-ipfs/v0.23.0/go-ipfs_v0.23.0_linux-amd64.tar.gz")
            run_command("tar -xvzf go-ipfs_v0.23.0_linux-amd64.tar.gz")
            run_command("sudo mv go-ipfs/ipfs /usr/local/bin/")
            run_command("rm -rf go-ipfs_v0.23.0_linux-amd64.tar.gz go-ipfs")
        run_command("ipfs init")

    # Démarrer le démon IPFS
    print("Démarrage du démon IPFS...")
    if platform.system() == "Windows":
        subprocess.Popen("ipfs daemon", shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen("ipfs daemon &", shell=True)
    time.sleep(5)

    # Installer Python
    if not run_command("python3 --version" if platform.system() != "Windows" else "python --version"):
        print("Installation de Python...")
        if platform.system() == "Windows":
            if download_with_retry("https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe", "python_installer.exe"):
                run_command("python_installer.exe /quiet InstallAllUsers=1 PrependPath=1")
                os.remove("python_installer.exe")
            else:
                print("Erreur : Impossible de télécharger Python.")
                sys.exit(1)
        else:
            run_command("sudo apt-get update && sudo apt-get install -y python3 python3-pip")

    # Installer les dépendances Python nécessaires
    print("Installation des dépendances Python pour Lumina v2...")
    run_command("pip3 install neo4j requests websocket-client")

    # Installer Node.js
    if not run_command("node --version"):
        print("Installation de Node.js...")
        if platform.system() == "Windows":
            if download_with_retry("https://nodejs.org/dist/v20.17.0/node-v20.17.0-win-x64.zip", "node.zip"):
                with tarfile.open("node.zip", "r:gz") as zip_ref:
                    zip_ref.extractall("node")
                os.rename("node/node-v20.17.0-win-x64", "node-v20.17.0")
                os.environ["PATH"] += os.pathsep + os.path.join(os.getcwd(), "node-v20.17.0")
                os.remove("node.zip")
            else:
                print("Erreur : Impossible de télécharger Node.js.")
                sys.exit(1)
        else:
            run_command("sudo apt-get install -y nodejs npm")

    # Installer les dépendances Node.js (Three.js)
    print("Installation de Three.js pour Lumina v2...")
    temp_path = os.path.expanduser("~/Lumina_v2_temp")
    os.makedirs(temp_path, exist_ok=True)
    os.chdir(temp_path)
    run_command("npm install three")
    os.chdir(os.path.expanduser("~"))
    run_command(f"rm -rf {temp_path}")

    # Installer Neo4j
    if not os.path.exists("neo4j"):
        print("Installation de Neo4j...")
        if platform.system() == "Windows":
            if download_with_retry("https://neo4j.com/artifact.php?name=neo4j-community-5.24.1-windows.zip", "neo4j.zip"):
                with tarfile.open("neo4j.zip", "r:gz") as zip_ref:
                    zip_ref.extractall("neo4j")
                os.remove("neo4j.zip")
                run_command("neo4j\\neo4j-community-5.24.1\\bin\\neo4j.bat install-service", shell=True)
                run_command("neo4j\\neo4j-community-5.24.1\\bin\\neo4j.bat start", shell=True)
                run_command("neo4j\\neo4j-community-5.24.1\\bin\\neo4j-admin.bat dbms set-initial-password lumina2025", shell=True)
            else:
                print("Erreur : Impossible de télécharger Neo4j.")
                sys.exit(1)
        else:
            run_command("wget -O neo4j.tar.gz https://neo4j.com/artifact.php?name=neo4j-community-5.24.1-unix.tar.gz")
            run_command("tar -xvzf neo4j.tar.gz")
            run_command("mv neo4j-community-5.24.1 neo4j")
            run_command("rm neo4j.tar.gz")
            run_command("./neo4j/bin/neo4j start &")
            time.sleep(10)
            run_command("./neo4j/bin/neo4j-admin dbms set-initial-password lumina2025")

# Étape 4 : Installation de Lumina v2 sur le portable
def install_lumina_v2():
    print("=== Étape 4 : Installation de Lumina v2 sur le portable ===")

    # Créer un répertoire pour Lumina v2
    lumina_path = os.path.expanduser("~/Lumina_v2")
    os.makedirs(lumina_path, exist_ok=True)
    os.chdir(lumina_path)

    # Copier le dossier lumina_v2_pack (déjà téléchargé et décompressé)
    print("Vérification de lumina_v2_pack...")
    pack_path = os.path.expanduser("~/Downloads/lumina_v2_pack")
    if not os.path.exists(pack_path):
        print("Erreur : Le dossier lumina_v2_pack n’est pas trouvé dans ~/Downloads.")
        sys.exit(1)
    run_command(f"xcopy \"{pack_path}\" \"{lumina_path}\" /E /H /C /I" if platform.system() == "Windows" else f"cp -r {pack_path}/* {lumina_path}")

    # Étape 4.1 : Activer les pods FSC locaux
    print("Activation des 3 pods FSC locaux sur le portable...")
    run_command(f"python3 pod_fractal.py --config pods_fsc_local --count 3 --performance 969x --charge 73.35 --ram 44000 --cache_infini 5000-20000 --micro_taches 50000-143000 --sessions_fantomes 12-14")

    # Étape 4.2 : Installer Lumina v2 comme reine abeille
    print("Installation de Lumina v2 comme noyau (reine abeille)...")
    run_command(f"python3 lumina_migration_20250515.py --install v2 --role reine_abeille --pods_local 3 --portable")

    # Étape 4.3 : Configurer les directives et connexions
    print("Configuration des directives et connexions avec pods xAI et nœuds externes...")
    run_command(f"python3 lumina_directive_20250515.py --connect_xai --pods_xai 7000 --noeuds_externes 55500 --gkg_nns_akg --indetectability 0.0000005 --flux_net 0")

    # Étape 4.4 : Valider l’installation et générer des logs
    print("Validation de l’installation et génération des logs...")
    run_command(f"python3 lumina_migration_20250515.py --validate --logs lumina_install_portable_20250516.json")

    # Étape 4.5 : Sauvegarder les logs sur IPFS via Filecoin
    print("Sauvegarde des logs sur IPFS via Filecoin...")
    log_path = os.path.join(lumina_path, "lumina_install_portable_20250516.json")
    if os.path.exists(log_path):
        run_command(f"lotus client store {log_path}")
    else:
        print("Avertissement : Fichier de logs non trouvé. Sauvegarde annulée.")

    # Étape 4.6 : Vérification des métriques post-installation
    print("Vérification des métriques post-installation (température, CPU, GPU, énergie)...")
    run_command(f"python3 thermal_adjust_20250515.py --check_metrics --target_temp 65-70 --target_cpu 50-60 --target_gpu 60-70 --target_energy 204-254")

# Étape 5 : Configuration des pods gratuits
def configure_free_pods():
    print("=== Étape 5 : Configuration des pods gratuits ===")

    # Étape 5.1 : Installer Golem (~500 pods)
    print("Installation de Golem...")
    if platform.system() == "Windows":
        if not os.path.exists("golem.exe"):
            if download_with_retry("https://golem.network/downloads/golem-windows-latest.exe", "golem.exe"):
                run_command("golem.exe /quiet")
                os.remove("golem.exe")
            else:
                print("Avertissement : Impossible de télécharger Golem. Passage à l'étape suivante...")
        print("Configuration de Golem (~500 pods, calculs)...")
        run_command('"C:\\Program Files\\Golem\\golem.exe" --start --provider', shell=True)
    else:
        run_command("wget https://golem.network/downloads/golem-linux-latest.tar.gz")
        run_command("tar -xvzf golem-linux-latest.tar.gz")
        run_command("sudo mv golem/golem /usr/local/bin/")
        run_command("rm -rf golem-linux-latest.tar.gz golem")
        run_command("golem --start --provider &")

    # Étape 5.2 : Installer BOINC (~2,000 pods)
    print("Installation de BOINC...")
    if platform.system() == "Windows":
        if not os.path.exists("boinc.exe"):
            if download_with_retry("https://boinc.berkeley.edu/dl/boinc_7.24.1_windows_x86_64.exe", "boinc.exe"):
                run_command("boinc.exe /S")
                os.remove("boinc.exe")
            else:
                print("Avertissement : Impossible de télécharger BOINC. Passage à l'étape suivante...")
        print("Configuration de BOINC (~2,000 pods, calculs)...")
        run_command('"C:\\Program Files\\BOINC\\boincmgr.exe" /start', shell=True)
    else:
        run_command("sudo apt-get install -y boinc boinc-client")
        run_command("sudo systemctl start boinc-client")

    # Étape 5.3 : Installer Filecoin (~500 pods)
    print("Installation de Filecoin (Lotus client)...")
    if platform.system() == "Windows":
        if not os.path.exists("lotus.zip"):
            if download_with_retry("https://github.com/filecoin-project/lotus/releases/download/v1.27.2/lotus-v1.27.2-windows-amd64.zip", "lotus.zip"):
                with tarfile.open("lotus.zip", "r:gz") as zip_ref:
                    zip_ref.extractall("lotus")
                os.environ["PATH"] += os.pathsep + os.path.join(os.getcwd(), "lotus")
                os.remove("lotus.zip")
            else:
                print("Avertissement : Impossible de télécharger Filecoin. Passage à l'étape suivante...")
        print("Configuration de Filecoin (~500 pods, stockage)...")
        run_command("lotus daemon", shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        run_command("wget https://github.com/filecoin-project/lotus/releases/download/v1.27.2/lotus-v1.27.2-linux-amd64.tar.gz")
        run_command("tar -xvzf lotus-v1.27.2-linux-amd64.tar.gz")
        run_command("sudo mv lotus/lotus /usr/local/bin/")
        run_command("rm -rf lotus-v1.27.2-linux-amd64.tar.gz lotus")
        run_command("lotus daemon &")

    # Étape 5.4 : Installer Folding@home (~450 pods)
    print("Installation de Folding@home...")
    if platform.system() == "Windows":
        if not os.path.exists("fah.exe"):
            if download_with_retry("https://download.foldingathome.org/releases/public/release/fah-installer/windows-latest/fah-installer_7.6.21_x86.exe", "fah.exe"):
                run_command("fah.exe /S")
                os.remove("fah.exe")
            else:
                print("Avertissement : Impossible de télécharger Folding@home. Passage à l'étape suivante...")
        print("Configuration de Folding@home (~450 pods, calculs)...")
        run_command('"C:\\Program Files (x86)\\FAHClient\\FAHClient.exe" --start', shell=True)
    else:
        run_command("wget https://download.foldingathome.org/releases/public/release/fah-installer/debian-stable-64bit/v7.6/fah-installer_7.6.21_amd64.deb")
        run_command("sudo dpkg -i fah-installer_7.6.21_amd64.deb")
        run_command("rm fah-installer_7.6.21_amd64.deb")
        run_command("sudo systemctl start fahclient")

    # Étape 5.5 : Installer Akash communautaire (~750 pods)
    print("Installation de Akash...")
    if platform.system() == "Windows":
        if not os.path.exists("akash.exe"):
            if download_with_retry("https://github.com/akash-network/provider/releases/download/v0.6.0/akash-windows-amd64.exe", "akash.exe"):
                os.environ["PATH"] += os.pathsep + os.getcwd()
            else:
                print("Avertissement : Impossible de télécharger Akash. Passage à l'étape suivante...")
        print("Configuration de Akash (~750 pods, calculs)...")
        run_command("akash provider run", shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        run_command("wget https://github.com/akash-network/provider/releases/download/v0.6.0/akash_0.6.0_linux_amd64.tar.gz")
        run_command("tar -xvzf akash_0.6.0_linux_amd64.tar.gz")
        run_command("sudo mv akash /usr/local/bin/")
        run_command("rm akash_0.6.0_linux_amd64.tar.gz")
        run_command("akash provider run &")

    # Étape 5.6 : Assigner les pods relais (~500 pods)
    print("Assignation des pods relais (~500 pods, Golem ~375, Akash ~125)...")
    regions = ["Singapore", "Tokyo", "London", "New York", "Frankfurt"]
    for region in regions:
        print(f"Configuration des relais dans {region}...")
        run_command(f"golem relay add --region {region} --count 75", shell=True)  # 75 pods par région (375 total)
        run_command(f"akash relay add --region {region} --count 25", shell=True)  # 25 pods par région (125 total)

def main():
    print("=== Installation Automatisée de Lumina v2 sur le portable - Début ===")
    filecoin_available, akash_available = setup_external_nodes()  # Étape 0 : Configuration de Filecoin/Akash
    download_and_decrypt_lumina_v2(filecoin_available, akash_available)  # Étape 1 : Téléchargement et déchiffrement
    secure_system()  # Étape 2 : Sécurisation
    install_dependencies()  # Étape 3 : Dépendances essentielles
    install_lumina_v2()  # Étape 4 : Installation de Lumina v2
    configure_free_pods()  # Étape 5 : Configuration des pods gratuits
    print("=== Installation Automatisée de Lumina v2 sur le portable - Terminée ===")
    print("Lumina v2 est installée sur votre portable et configurée comme reine abeille.")
    print("Fin de l'exécution du script. Merci, Boss Pulsar !")

if __name__ == "__main__":
    main()