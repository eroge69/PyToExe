#!/usr/bin/env python3 """ PYDECOMPILATOR - Version 1.0.1 Créé par Benzo0dev

Outil professionnel pour décompiler des exécutables Python compilés avec PyInstaller. Le script installe automatiquement les dépendances nécessaires et télécharge pyinstxtractor.py, afin de pouvoir fonctionner sur un PC vierge dès l'installation de Python. """

import os import sys import subprocess import argparse import urllib.request import time from pathlib import Path

------------------- Installation automatique des dépendances -------------------

def install_package(package): """Installe un package via pip s'il n'est pas présent.""" try: print(f"[INFO] Installation du package '{package}'...") subprocess.check_call([sys.executable, "-m", "pip", "install", package]) except subprocess.CalledProcessError as e: print(f"[ERROR] Échec de l'installation du package {package}. Détails: {e}") sys.exit(1)

Importation des modules requis avec installation automatique

for package in ["colorama", "tabulate", "uncompyle6"]: try: import(package) except ImportError: install_package(package)

from colorama import init, Style from tabulate import tabulate

Initialisation de Colorama

init(autoreset=True)

------------------- Téléchargement automatique de pyinstxtractor.py -------------------

PYINSTXTRACTOR_URL = "https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py" PYINSTXTRACTOR_FILENAME = "pyinstxtractor.py"

def download_pyinstxtractor(): """Télécharge pyinstxtractor.py si absent.""" if not Path(PYINSTXTRACTOR_FILENAME).is_file(): print("[INFO] Téléchargement de pyinstxtractor.py...") try: urllib.request.urlretrieve(PYINSTXTRACTOR_URL, PYINSTXTRACTOR_FILENAME) print("[INFO] Téléchargement réussi.") except Exception as e: print(f"[ERROR] Échec du téléchargement: {e}") sys.exit(1) else: print("[INFO] pyinstxtractor.py déjà présent.")

download_pyinstxtractor()

------------------- Extraction et Décompilation -------------------

def extract_executable(exe_path, output_dir): """Extrait le contenu d'un exécutable PyInstaller.""" if not os.path.exists(exe_path): print(f"[ERROR] Le fichier {exe_path} n'existe pas.") sys.exit(1)

print(f"[INFO] Extraction de {exe_path} ...")
try:
    subprocess.run([sys.executable, PYINSTXTRACTOR_FILENAME, exe_path], check=True)
except subprocess.CalledProcessError:
    print("[ERROR] Échec de l'extraction avec pyinstxtractor.")
    sys.exit(1)

default_dir = exe_path + '_extracted'
if not os.path.exists(default_dir):
    print("[ERROR] Dossier extrait introuvable.")
    sys.exit(1)

os.rename(default_dir, output_dir)
print(f"[INFO] Extraction terminée dans: {output_dir}")
return output_dir

def decompile_pyc_files(extracted_dir, decompiled_dir): """Décompile les fichiers .pyc en .py.""" os.makedirs(decompiled_dir, exist_ok=True) decompiled_count = 0 for root, _, files in os.walk(extracted_dir): for file in files: if file.endswith('.pyc'): pyc_path = os.path.join(root, file) output_file = os.path.join(decompiled_dir, file.replace('.pyc', '.py')) print(f"[INFO] Décompilation de {pyc_path} -> {output_file}") try: with open(output_file, 'w', encoding='utf-8') as out_f: subprocess.run(['uncompyle6', '-o', '-', pyc_path], stdout=out_f, check=True) decompiled_count += 1 except subprocess.CalledProcessError: print(f"[ERROR] Échec de la décompilation de {pyc_path}") print(f"[INFO] {decompiled_count} fichier(s) décompilé(s) dans : {decompiled_dir}") return decompiled_count

------------------- Affichage du Résumé -------------------

def print_summary_table(exe_path, extract_dir, decompiled_dir, decompiled_count): """Affiche un tableau récapitulatif des opérations.""" headers = ["Étape", "Description", "Résultat"] data = [ ["Extraction", f"Exécutable: {exe_path}", f"Répertoire: {extract_dir}"], ["Décompilation", "Fichiers .pyc décompilés", f"{decompiled_count} fichier(s)"], ["Sortie", "Fichiers source", f"Répertoire: {decompiled_dir}"] ] print("\n[INFO] Résumé de l'opération:") print(tabulate(data, headers, tablefmt="grid"))

------------------- Main -------------------

def main(): parser = argparse.ArgumentParser( description="PYDECOMPILATOR - Outil pour décompiler des exécutables Python PyInstaller" ) parser.add_argument("exe", help="Chemin vers l'exécutable PyInstaller") parser.add_argument("--extract-dir", default="extracted", help="Répertoire de stockage des fichiers extraits") parser.add_argument("--decompiled-dir", default="decompiled", help="Répertoire de stockage des fichiers décompilés") args = parser.parse_args()

print("[INFO] Lancement du processus de décompilation...")
extracted_path = extract_executable(args.exe, args.extract_dir)
decompiled_count = decompile_pyc_files(extracted_path, args.decompiled_dir)
print_summary_table(args.exe, args.extract_dir, args.decompiled_dir, decompiled_count)
print("\n[INFO] Opération terminée. Merci d'utiliser PYDECOMPILATOR !\n")

if name == 'main': main()

