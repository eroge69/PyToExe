import os
import sqlite3
import time
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import sqlite3
import subprocess
import threading
from PIL import Image, ImageTk  # Nécessaire pour afficher les images
import shutil
from tkinter import filedialog
from PIL import ImageGrab
import pyperclip
from tkinter import messagebox

# Variables globales
database_name = 'images.db'
current_index = 0
images_list = []
destination_folder_path = ""

# Fonction pour créer la base de données et la table
def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            creation_date TEXT,
            modification_date TEXT,
            description TEXT,
            md5 TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_keywords (
            image_md5 TEXT NOT NULL,
            keyword_id INTEGER NOT NULL,
            FOREIGN KEY (image_md5) REFERENCES images (md5) ON DELETE CASCADE,
            FOREIGN KEY (keyword_id) REFERENCES keywords (id) ON DELETE CASCADE,
            PRIMARY KEY (image_md5, keyword_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS themes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            creation_date TEXT NOT NULL,
            description TEXT,
            owner TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_themes (
            image_md5 TEXT NOT NULL,
            theme_id INTEGER NOT NULL,
            FOREIGN KEY (image_md5) REFERENCES images (md5) ON DELETE CASCADE,
            FOREIGN KEY (theme_id) REFERENCES themes (id) ON DELETE CASCADE,
            PRIMARY KEY (image_md5, theme_id)
        )
    ''')
    conn.commit()
    conn.close()

# Fonction pour exécuter une requête SQLite dans un contexte sécurisé
def execute_query(db_name, query, params=(), fetch=False):
    """Exécute une requête SQLite avec gestion automatique de la connexion."""
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return None

def save_metadata():
    """Enregistre la description, les mots-clés et les thématiques dans la base de données."""
    global current_index, images_list
    if not images_list:
        return

    try:
        # Récupérer les données saisies
        description = description_text.get("1.0", tk.END).strip()  # Récupérer le texte du champ Text
        keywords = keywords_entry.get()
        themes = themes_entry.get()
        image_md5 = images_list[current_index]['md5']  # Utiliser le MD5 pour identifier l'image

        # Mettre à jour la base de données
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE images SET description = ? WHERE md5 = ?',
            (description, image_md5)
        )

        # Supprimer les anciens liens entre l'image et les mots-clés
        cursor.execute('DELETE FROM image_keywords WHERE image_md5 = ?', (image_md5,))

        # Gérer les mots-clés
        if keywords:
            # Ajouter les nouveaux mots-clés et créer les liens
            keyword_list = [keyword.strip() for keyword in keywords.split(',') if keyword.strip()]
            for keyword_keyword in keyword_list:
                keyword_data = {
                    'keyword': keyword_keyword
                }
                keyword_id = insert_or_update_keyword(conn, keyword_data)

                # Lier le mot-clé à l'image
                link_image_to_keyword(conn, image_md5, keyword_id)

        # Supprimer les anciens liens entre l'image et les mots-clés
        cursor.execute('DELETE FROM image_themes WHERE image_md5 = ?', (image_md5,))

        # Gérer les thématiques
        if themes:
            # Ajouter les nouvelles thématiques et créer les liens
            theme_list = [theme.strip() for theme in themes.split(',') if theme.strip()]
            for theme_title in theme_list:
                theme_data = {
                    'title': theme_title,
                    'creation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'description': '',
                    'owner': 'Utilisateur'
                }
                theme_id = insert_or_update_theme(conn, theme_data)

                link_image_to_theme(conn, image_md5, theme_id)

        conn.commit()
        conn.close()

        # Mettre à jour l'affichage des listes (toutes les thématiques et mots-clés)
        update_lists()

        progress_label.config(text="Méta-données enregistrées avec succès.")
    except Exception as e:
        progress_label.config(text=f"Erreur lors de l'enregistrement : {e}")

def start_indexing():
    """Lance l'indexation des images et met à jour la barre de progression."""
    # Ajouter une barre de progression
    progress_bar = ttk.Progressbar(right_frame, orient="horizontal", mode="determinate", length=300)
    progress_bar.pack(pady=5)
    progress_bar["value"] = 0  # Initialiser la barre de progression

    def run_script():
        try:
            # Afficher le message "mise à jour en cours"
            progress_label.config(text="Mise à jour en cours, veuillez patienter...")

            # Indexer les images dans le répertoire spécifié
            index_images_in_directory(directory_to_scan, db_name, progress_bar)

            # Charger les images
            load_images()

            # Mettre à jour les listes
            update_lists()

            progress_label.config(text="Indexation des images terminée avec succès.", font=("Arial", 8))
        except Exception as e:
            progress_label.config(text=f"Erreur : {e}")
        finally:
            # Réinitialiser le message et masquer la barre après un délai
            root.after(5000, lambda: progress_label.config(text=""))
            progress_bar.pack_forget()  # Masquer la barre de progression

    # Lancer le script dans un thread séparé pour ne pas bloquer l'UI
    threading.Thread(target=run_script, daemon=True).start()

# Fonction pour indexer les images du dossier
def index_images_in_directory(directory, db_name, progress_bar=None):
    """Indexe les images dans le répertoire spécifié et met à jour la barre de progression."""
    # Trouver tous les fichiers d'image dans le répertoire
    all_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp')):
                all_files.append(os.path.join(root, file))
    
    # Initialiser la barre de progression
    if progress_bar:
        progress_bar["maximum"] = len(all_files)  # Définir la valeur maximale
        progress_bar["value"] = 0  # Réinitialiser la barre

    # Parcourir les fichiers et les indexer
    for i, file_path in enumerate(all_files, start=1):
        metadata = get_image_metadata(file_path, directory)
        insert_or_update_image(db_name, metadata)
        
        # Mettre à jour la barre de progression
        if progress_bar:
            progress_bar["value"] = i
            progress_bar.update_idletasks()  # Forcer la mise à jour de l'interface utilisateur

    # Supprimer les fichiers qui ne sont plus présents
    delete_missing_images(db_name, directory)

# Fonction pour obtenir les métadonnées d'une image
def get_image_metadata(image_path, base_directory):
    relative_path = os.path.relpath(image_path, base_directory)
    file_info = os.stat(image_path)
    date_creation = datetime.fromtimestamp(file_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
    date_modification = datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    md5_hash = calculate_md5(image_path)
    return {
        'filename': os.path.basename(image_path),
        'file_path': relative_path,
        'creation_date': date_creation,
        'modification_date': date_modification,
        'description': '',
        'keywords': '',
        'md5': md5_hash
    }

# Fonction pour calculer le hash MD5 d'un fichier
def calculate_md5(file_path):
    """Calcule le hash MD5 d'un fichier."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Fonction pour ajouter ou mettre à jour une image dans la base de données
def insert_or_update_image(db_name, image_metadata):
    query_select = '''
        SELECT id, file_path, filename, creation_date, modification_date
        FROM images WHERE md5 = ?
    '''
    existing_image = execute_query(db_name, query_select, (image_metadata['md5'],), fetch=True)

    if existing_image:
        # Si l'image existe, vérifier si des métadonnées ont changé
        query_update = '''
            UPDATE images
            SET file_path = ?, filename = ?, creation_date = ?, modification_date = ?, description = ?
            WHERE md5 = ?
        '''
        execute_query(db_name, query_update, (
            image_metadata['file_path'],
            image_metadata['filename'],
            image_metadata['creation_date'],
            image_metadata['modification_date'],
            image_metadata['description'],
            image_metadata['md5']
        ))
    else:
        # Sinon, insérer une nouvelle entrée
        query_insert = '''
            INSERT INTO images (filename, file_path, creation_date, modification_date, description, md5)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        execute_query(db_name, query_insert, (
            image_metadata['filename'],
            image_metadata['file_path'],
            image_metadata['creation_date'],
            image_metadata['modification_date'],
            image_metadata['description'],
            image_metadata['md5']
        ))

# Fonction pour ajouter ou mettre à jour un mot-clé dans la base de données
def insert_or_update_keyword(conn, keyword_data):
    cursor = conn.cursor()

    # Vérifier si le mot-clé existe déjà
    cursor.execute('SELECT id FROM keywords WHERE keyword = ?', (keyword_data['keyword'],))
    existing_keyword = cursor.fetchone()

    if existing_keyword:
        keyword_id = existing_keyword[0]

    # Si le mot-clé n'existe pas, on insère un nouveau mot-clé
    else:
        cursor.execute('''
            INSERT INTO keywords (keyword)
            VALUES (?)
        ''', (keyword_data['keyword'],))
        keyword_id = cursor.lastrowid

    conn.commit()
    return keyword_id

# Fonction pour ajouter ou mettre à jour une thématique dans la base de données
def insert_or_update_theme(conn, theme_data):
    cursor = conn.cursor()

    # Vérifier si la thématique existe déjà
    cursor.execute('SELECT id FROM themes WHERE title = ?', (theme_data['title'],))
    existing_theme = cursor.fetchone()

    if existing_theme:
        # Si la thématique existe, on met à jour ses informations
        cursor.execute('''
            UPDATE themes
            SET creation_date = ?, description = ?, owner = ?
            WHERE id = ?
        ''', (
            theme_data['creation_date'],
            theme_data['description'],
            theme_data['owner'],
            existing_theme[0]
        ))
        theme_id = existing_theme[0]
    else:
        # Sinon, on insère une nouvelle thématique
        cursor.execute('''
            INSERT INTO themes (title, creation_date, description, owner)
            VALUES (?, ?, ?, ?)
        ''', (
            theme_data['title'],
            theme_data['creation_date'],
            theme_data['description'],
            theme_data['owner']
        ))
        theme_id = cursor.lastrowid

    conn.commit()
    return theme_id

# Fonction pour lier une image à une thématique
def link_image_to_theme(conn, image_md5, theme_id):
    """Lie une image à une thématique en utilisant le MD5 de l'image."""
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO image_themes (image_md5, theme_id) VALUES (?, ?)', (image_md5, theme_id))
    conn.commit()

# Fonction pour lier une image à un mot-clé
def link_image_to_keyword(conn, image_md5, keyword_id):
    """Lie une image à un mot-clé en utilisant le MD5 de l'image."""
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO image_keywords (image_md5, keyword_id) VALUES (?, ?)', (image_md5, keyword_id))
    conn.commit()

# Fonction pour supprimer les images absentes de la base de données
def delete_missing_images(db_name, directory):
    query_select = 'SELECT file_path FROM images'
    all_images = execute_query(db_name, query_select, fetch=True)

    valid_images = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp')):
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                valid_images.add(relative_path)

    for image in all_images:
        if image[0] not in valid_images:
            query_delete = 'DELETE FROM images WHERE file_path = ?'
            execute_query(db_name, query_delete, (image[0],))

    # Nettoyer les mots-clés orphelins
    clean_orphan_keywords(db_name)

    # Nettoyer les thèmes orphelins
    clean_orphan_themes(db_name)

# Fonction pour nettoyer les mots-clés orphelins
def clean_orphan_keywords(db_name):
    query_delete = '''
        DELETE FROM keywords
        WHERE id NOT IN (SELECT DISTINCT keyword_id FROM image_keywords)
    '''
    execute_query(db_name, query_delete)

# Fonction pour nettoyer les thèmes orphelins
def clean_orphan_themes(db_name):
    query_delete = '''
        DELETE FROM themes
        WHERE id NOT IN (SELECT DISTINCT theme_id FROM image_themes)
    '''
    execute_query(db_name, query_delete)

def update_lists(image_path=None):
    """Met à jour les listes des thèmes et des mots-clés dans la colonne droite uniquement lorsque nécessaire."""
    try:
        show_themes()
        show_keywords()
        show_images()
    except Exception as e:
        progress_label.config(text=f"Erreur lors de la mise à jour des listes : {e}")

def show_themes():
    """Réinitialise la liste des thématiques pour afficher toutes les thématiques disponibles."""
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute('SELECT title FROM themes ORDER BY title ASC')
        all_themes = [row[0] for row in cursor.fetchall()]
        themes_listbox.delete(0, tk.END)
        themes_listbox.insert(0, "Afficher toutes les images")
        for theme in all_themes:
            themes_listbox.insert(tk.END, theme)
    except Exception as e:
        progress_label.config(text=f"Erreur lors de l'affichage de toutes les thématiques : {e}")

def show_keywords():
    """Réinitialise la liste des mots-clés pour afficher tous les mots-clés disponibles."""
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute('SELECT keyword FROM keywords ORDER BY keyword ASC')
        all_keywords = [row[0] for row in cursor.fetchall()]
        keywords_listbox.delete(0, tk.END)
        # Ajouter une option pour afficher toutes les images et dont la valeur est None
        keywords_listbox.insert(0, "Afficher toutes les images")
        for keyword in all_keywords:
            keywords_listbox.insert(tk.END, keyword)
    except Exception as e:
        progress_label.config(text=f"Erreur lors de l'affichage de tous les mots-clés : {e}")

def load_images(theme=None, keyword=None):
    #####################################################################
    """Réinitialise la liste des images pour afficher toutes les images disponibles."""
    try:
        global images_list
        # Charger depuis la base de données
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()

        if theme!=None:
            print(f"Thème sélectionné : {theme}")
            # Charger les images liées à la thématique depuis la base de données
            cursor.execute('''
                SELECT i.file_path, i.md5 FROM images i
                JOIN image_themes it ON i.md5 = it.image_md5
                JOIN themes t ON t.id = it.theme_id
                WHERE t.title = ?
            ''', (theme,))
            images_list = [{'file_path': row[0], 'md5': row[1]} for row in cursor.fetchall()]
        elif keyword!=None:
            print(f"Mot-clé sélectionné : {keyword}")
            # Charger les images liées au mot-clé depuis la base de données
            cursor.execute('''
                SELECT i.file_path, i.md5 FROM images i
                JOIN image_keywords ik ON i.md5 = ik.image_md5
                JOIN keywords k ON k.id = ik.keyword_id
                WHERE k.keyword = ?
            ''', (keyword,))
            images_list = [{'file_path': row[0], 'md5': row[1]} for row in cursor.fetchall()]
        elif theme==None or keyword==None:
            print("Afficher toutes les images")
            # Charger toutes les images depuis la base de données
            cursor.execute('SELECT file_path, md5 FROM images')
            images_list = [{'file_path': row[0], 'md5': row[1]} for row in cursor.fetchall()]

        conn.close()
        print(f"# : {len(images_list)}")
        position_label.config(text=f"1/{len(images_list)}")  # Mettre à jour le compteur

    except Exception as e:
        progress_label.config(text=f"Erreur lors de l'affichage de toutes les images : {e}")

def show_images():
    """Réinitialise la liste des images pour afficher toutes les images disponibles."""
    try:
        # Effacer le contenu existant dans la Listbox
        image_listbox.delete(0, tk.END)

        # Ajouter toutes les images à la Listbox
        for image_data in images_list:
            image_name = image_data['file_path'].split('/')[-1]  # Extraire uniquement le nom du fichier
            image_listbox.insert(tk.END, image_name)

    except Exception as e:
        progress_label.config(text=f"Erreur lors de l'affichage de toutes les images : {e}")

def afficher_image_par_nom(event):
    """Affiche l'image sélectionnée dans la colonne centrale en fonction du nom de fichier cliqué."""
    global current_index, images_list
    try:
        # Récupérer l'index de l'élément sélectionné dans la Listbox
        selection = image_listbox.curselection()
        if not selection:
            return
        selected_index = selection[0]

        # Trouver le chemin complet de l'image correspondante
        image_name = image_listbox.get(selected_index)
        for index, image_data in enumerate(images_list):
            if image_data['file_path'].endswith(image_name):
                current_index = index
                show_image(current_index)
                break
    except Exception as e:
        progress_label.config(text=f"Erreur lors de l'affichage de l'image : {e}")

def show_image(index):
    """Affiche l'image à l'index donné et charge les métadonnées associées uniquement lorsque nécessaire."""
    global current_index, images_list
    if not images_list:
        image_label.config(text="Aucune image à afficher.", image="")
        description_text.delete("1.0", tk.END)
        keywords_entry.delete(0, tk.END)
        themes_entry.delete(0, tk.END)
        position_label.config(text="0/0")
        return

    try:
        # Charger l'image
        current_index = index
        image_path = images_list[index]['file_path']
        img = Image.open(image_path)
        img.thumbnail((400, 400), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo, text="", cursor="hand2")
        image_label.image = photo

        # Charger les métadonnées uniquement lorsque l'image est sélectionnée
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()

        # Charger la description
        cursor.execute('SELECT description FROM images WHERE file_path = ?', (image_path,))
        result = cursor.fetchone()
        description_text.delete("1.0", tk.END)
        description_text.insert("1.0", result[0] if result else "")

        # Charger les mots-clés associés
        cursor.execute('''
            SELECT k.keyword FROM keywords k
            JOIN image_keywords ik ON k.id = ik.keyword_id
            JOIN images i ON i.md5 = ik.image_md5
            WHERE i.file_path = ?
        ''', (image_path,))
        keywords = [row[0] for row in cursor.fetchall()]
        keywords_entry.delete(0, tk.END)
        keywords_entry.insert(0, ', '.join(keywords))

        # Charger les thématiques associées
        cursor.execute('''
            SELECT t.title FROM themes t
            JOIN image_themes it ON t.id = it.theme_id
            JOIN images i ON i.md5 = it.image_md5
            WHERE i.file_path = ?
        ''', (image_path,))
        themes = [row[0] for row in cursor.fetchall()]
        themes_entry.delete(0, tk.END)
        themes_entry.insert(0, ', '.join(themes))

        # Mettre à jour la position actuelle
        position_label.config(text=f"{index + 1}/{len(images_list)}")
    except Exception as e:
        image_label.config(text=f"Erreur lors du chargement de l'image : {e}", image="")

def next_image():
    """Affiche l'image suivante."""
    global current_index, images_list
    if images_list:
        current_index = (current_index + 1) % len(images_list)
        show_image(current_index)

def previous_image():
    """Affiche l'image précédente."""
    global current_index, images_list
    if images_list:
        current_index = (current_index - 1) % len(images_list)
        show_image(current_index)

def filter_images_by_theme(event):
    """Met à jour la liste des images en fonction de la thématique sélectionnée et affiche la première image."""
    try:
        # Récupérer la thématique sélectionnée
        selection = themes_listbox.curselection()
        if not selection:
            return
        selected_theme = themes_listbox.get(selection[0])

        if selected_theme=="Afficher toutes les images":
            selected_theme = None

        load_images(theme=selected_theme,keyword=None)
        show_images()
        show_image(0)

    except Exception as e:
        progress_label.config(text=f"Erreur lors du filtrage par thématique : {e}")

def filter_images_by_keyword(event):
    """Met à jour la liste des images en fonction du mot-clé sélectionné et affiche la première image."""
    try:
        # Récupérer le mot-clé sélectionné
        selection = keywords_listbox.curselection()
        if not selection:
            return
        selected_keyword = keywords_listbox.get(selection[0])

        if selected_keyword=="Afficher toutes les images":
            selected_keyword = None

        load_images(theme=None,keyword=selected_keyword)
        show_images()
        show_image(0)

    except Exception as e:
        progress_label.config(text=f"Erreur lors du filtrage par thématique : {e}")

def open_image(event):
    """Ouvre l'image affichée dans la visionneuse Windows par défaut."""
    global images_list, current_index
    if not images_list:
        return

    try:
        # Chemin de l'image actuellement affichée
        image_path = images_list[current_index]['file_path']

        # Si windows Ouvrir l'image avec l'application par défaut
        if os.name == 'nt':
            os.startfile(image_path)
        # Si linux
        if os.name == 'posix':
            # Utiliser xdg-open pour ouvrir l'image avec l'application par défaut
            import subprocess
            subprocess.Popen(['xdg-open', image_path])
    
    except Exception as e:
        progress_label.config(text=f"Erreur lors de l'ouverture de l'image : {e}")

def copy_images():
    """Copie toutes les images affichées dans la liste dans un dossier choisi par l'utilisateur."""
    global images_list, destination_folder_path
    if not images_list:
        copy_label.config(text="Aucune image à copier.")
        return

    # Ouvrir une boîte de dialogue pour sélectionner un dossier
    destination_folder = filedialog.askdirectory(title="Choisir un dossier de destination")
    if not destination_folder:
        copy_label.config(text="Copie annulée.")
        return

    try:
        # Afficher le message "copie en cours"
        copy_label.config(text="Copie en cours, veuillez patienter...")
        root.update_idletasks()  # Forcer la mise à jour de l'interface utilisateur

        # Copier chaque image dans le dossier sélectionné
        for image_data in images_list:
            shutil.copy(image_data['file_path'], destination_folder)

        # Stocker le chemin du répertoire de destination
        destination_folder_path = destination_folder

        # Mettre à jour le label avec le chemin cliquable
        copy_label.config(
            text=f"Images copiées dans :\n{destination_folder}",
            cursor="hand2"  # Changer le curseur pour indiquer un lien
        )
    except Exception as e:
        copy_label.config(text=f"Erreur lors de la sauvegarde : {e}")

def open_directory(event):
    """Ouvre le répertoire de destination dans l'explorateur Windows."""
    global destination_folder_path
    if destination_folder_path:
        # Ouvrir le répertoire
        destination_folder_path = destination_folder_path.replace("/", "\\")

        # Si windows
        if os.name == 'nt':
            os.startfile(destination_folder_path)

def create_context_menu(event):
    """Crée et affiche le menu contextuel lors d'un clic droit sur l'image."""
    global images_list, current_index
    if not images_list:
        return
    
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Copier l'image dans le presse-papier", command=copy_image_to_clipboard)
    context_menu.add_command(label="Copier le chemin dans le presse-papier", command=copy_image_path)
    context_menu.add_separator()
    context_menu.add_command(label="Supprimer l'image", command=delete_image)
    
    # Afficher le menu à la position du curseur
    context_menu.tk_popup(event.x_root, event.y_root)

def copy_image_to_clipboard():
    """Copie l'image actuellement affichée dans le presse-papier."""
    global images_list, current_index
    try:
        if not images_list:
            return

        image_path = images_list[current_index]['file_path']
        img = Image.open(image_path)

        # Conversion en RGB si nécessaire (pour les images PNG ou autres formats)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Copier l'image dans le presse-papier (Windows uniquement)
        if os.name == 'nt':
            from io import BytesIO
            import win32clipboard

            # Sauvegarder l'image dans un buffer en format BMP
            output = BytesIO()
            img.save(output, format='BMP')
            data = output.getvalue()[14:]  # Supprimer l'en-tête BMP
            output.close()

            # Copier dans le presse-papier
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()

        progress_label.config(text="Image copiée dans le presse-papier")
    except Exception as e:
        progress_label.config(text=f"Erreur lors de la copie de l'image : {e}")

def copy_image_path():
    """Copie le chemin de l'image dans le presse-papier."""
    global images_list, current_index
    if not images_list:
        return
        
    try:
        image_path = os.path.abspath(images_list[current_index]['file_path'])
        pyperclip.copy(image_path)
        progress_label.config(text="Chemin de l'image copié dans le presse-papier")
    except Exception as e:
        progress_label.config(text=f"Erreur lors de la copie du chemin : {e}")

def delete_image():
    """Supprime définitivement l'image après confirmation."""
    global images_list, current_index
    if not images_list:
        return
        
    try:
        image_path = images_list[current_index]['file_path']
        image_md5 = images_list[current_index]['md5']
        
        # Demander confirmation
        if not messagebox.askyesno("Confirmation", 
            "Voulez-vous vraiment supprimer définitivement cette image ?"):
            return
            
        # Supprimer le fichier
        os.remove(image_path)
        
        # Supprimer de la base de données
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM images WHERE md5 = ?', (image_md5,))
        conn.commit()
        conn.close()
        
        # Supprimer de la liste et mettre à jour l'affichage
        del images_list[current_index]
        if images_list:
            current_index = min(current_index, len(images_list) - 1)
            show_images()
            show_image(current_index)
        else:
            image_listbox.delete(0, tk.END)
            image_label.config(text="Aucune image à afficher.", image="")
            position_label.config(text="0/0")
            
        progress_label.config(text="Image supprimée avec succès")
    except Exception as e:
        progress_label.config(text=f"Erreur lors de la suppression : {e}")

# Lancement
if __name__ == '__main__':
    directory_to_scan = os.getcwd()  # Utiliser le dossier courant du script
    db_name = os.path.join(directory_to_scan, database_name)  # Enregistrer la base de données dans le dossier

    # Créer la base de données et la table si elles n'existent pas
    create_database(db_name)

# Création de la fenêtre principale
root = tk.Tk()
root.title("Visualiseur d'images")

# Configurer la taille de la fenêtre pour qu'elle occupe presque tout l'écran
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.9)  # 80% de la largeur de l'écran
window_height = int(screen_height * 0.9)  # 80% de la hauteur de l'écran
window_x = (screen_width - window_width) // 2  # Centrer horizontalement
window_y = (screen_height - window_height) // 2  # Centrer verticalement

root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

# Configuration des colonnes principales
root.grid_columnconfigure(0, weight=1, uniform="column")
root.grid_columnconfigure(1, weight=2, uniform="column")
root.grid_columnconfigure(2, weight=1, uniform="column")

# Configuration des lignes principales
root.grid_rowconfigure(0, weight=0)  # Ligne pour top_frame (hauteur adaptée au contenu)
root.grid_rowconfigure(1, weight=1)  # Ligne pour left_frame, center_frame, et right_frame

# Frame pour le bouton "Mise à jour" au-dessus de la colonne gauche
top_frame = tk.Frame(root)
top_frame.grid(row=0, column=0, sticky="nsew")

# Colonne gauche : Liste des noms des fichiers
left_frame = tk.Frame(root)
left_frame.grid(row=1, column=0, sticky="nsew")  # Déplacer la colonne gauche sous le bouton

# Titre pour la liste des images
images_title = tk.Label(left_frame, text="Liste des images", font=("Arial", 12, "bold"))
images_title.pack(pady=(5,0))

# Titre pour la liste des images
images_subtitle = tk.Label(left_frame, text="Selon la thématique ou le mot-clé sélectionné", font=("Arial", 8))
images_subtitle.pack(pady=(0,5))

# Listbox pour afficher les noms des fichiers
image_listbox = tk.Listbox(left_frame)
image_listbox.pack(side="left", fill="both", expand=True)

# Associer l'événement de sélection à la Listbox
image_listbox.bind("<<ListboxSelect>>", afficher_image_par_nom)

# Scrollbar pour la Listbox
left_scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=image_listbox.yview)
left_scrollbar.pack(side="right", fill="y")
image_listbox.config(yscrollcommand=left_scrollbar.set)

# Frame pour le bouton "Sauvegarder" en dessous de la colonne gauche
bottom_frame = tk.Frame(root)
bottom_frame.grid(row=2, column=0, sticky="nsew")

# Bouton "Sauvegarder"
copy_button = tk.Button(bottom_frame, text="Copier ces images dans un dossier", command=copy_images)
copy_button.pack(pady=15)

# Barre de progression (copy)
copy_label = tk.Label(bottom_frame, text="")
copy_label.pack(pady=(1, 5))

# Associer un clic gauche pour ouvrir le répertoire
copy_label.bind("<Button-1>", open_directory)

# Colonne centrale : Image et description
center_frame = tk.Frame(root)
center_frame.grid(row=0, column=1, sticky="nsew", rowspan=2)

# Boutons "Précédent" et "Suivant"
navigation_frame = tk.Frame(center_frame)
navigation_frame.pack(pady=10)

prev_button = tk.Button(navigation_frame, text="Image précédente", command=previous_image)
prev_button.pack(side=tk.LEFT, padx=5)

# Label pour afficher la position actuelle et le nombre total d'images
position_label = tk.Label(navigation_frame, text="0/0")
position_label.pack(side=tk.LEFT, padx=10)

next_button = tk.Button(navigation_frame, text="Image suivante", command=next_image)
next_button.pack(side=tk.RIGHT, padx=5)

# Zone pour afficher l'image
image_label = tk.Label(center_frame, text="Aucune image à afficher.")
image_label.pack(pady=10)

# Associer les événements de clic
image_label.bind("<Button-1>", open_image)
image_label.bind("<Button-3>", create_context_menu)  # Clic droit

# Zone pour la description
description_label = tk.Label(center_frame, text="Description pour cette image (détail, emplacement, licence, auteur·e, ...) :")
description_label.pack(pady=5)

# Remplacer Entry par Text pour permettre plusieurs lignes
description_text = tk.Text(center_frame, width=80, height=5, wrap="word")
description_text.pack(pady=5)

# Zone pour les mots-clés
keywords_label = tk.Label(center_frame, text="Mots-clés pour cette image (séparés par une virgule) :")
keywords_label.pack(pady=5)
keywords_entry = tk.Entry(center_frame, width=80)
keywords_entry.pack(pady=5)

# Zone pour les thématiques
themes_label = tk.Label(center_frame, text="Thématiques pour cette image (séparés par une virgule) :")
themes_label.pack(pady=5)
themes_entry = tk.Entry(center_frame, width=80)
themes_entry.pack(pady=5)

# Bouton "Enregistrer"
save_button = tk.Button(center_frame, text="Enregistrer la modification", command=save_metadata)
save_button.pack(pady=10)

# Colonne droite : Thèmes et mots-clés
right_frame = tk.Frame(root)
right_frame.grid(row=0, column=2, sticky="nsew", rowspan=2)

# Haut : Liste des thèmes
themes_frame = tk.Frame(right_frame)
themes_frame.pack(fill="both", expand=True)

# Titre pour les thématiques
themes_title = tk.Label(themes_frame, text="Thématiques", font=("Arial", 12, "bold"))
themes_title.pack(pady=5)

themes_scrollbar = tk.Scrollbar(themes_frame, orient="vertical")
themes_scrollbar.pack(side="right", fill="y")

themes_listbox = tk.Listbox(themes_frame, yscrollcommand=themes_scrollbar.set)
themes_listbox.pack(fill="both", expand=True)
themes_scrollbar.config(command=themes_listbox.yview)

# Bas : Liste des mots-clés
keywords_frame = tk.Frame(right_frame)
keywords_frame.pack(fill="both", expand=True)

# Titre pour les mots-clés
keywords_title = tk.Label(keywords_frame, text="Mots-clés", font=("Arial", 12, "bold"))
keywords_title.pack(pady=5)

keywords_scrollbar = tk.Scrollbar(keywords_frame, orient="vertical")
keywords_scrollbar.pack(side="right", fill="y")

keywords_listbox = tk.Listbox(keywords_frame, yscrollcommand=keywords_scrollbar.set)
keywords_listbox.pack(fill="both", expand=True)
keywords_scrollbar.config(command=keywords_listbox.yview)

# Associer l'événement de sélection à la Listbox des thématiques
themes_listbox.bind("<<ListboxSelect>>", filter_images_by_theme)

# Associer les événements de sélection aux Listbox
keywords_listbox.bind("<<ListboxSelect>>", filter_images_by_keyword)

# Bouton "Mise à jour"
update_button = tk.Button(right_frame, text="Mise à jour de la bibliothèque", command=start_indexing)
update_button.pack(pady=5)

# Barre de progression (texte)
progress_label = tk.Label(right_frame, text="")
progress_label.pack(pady=1)

# Charger les images
load_images()

# Charger les listes au démarrage
update_lists()

# Charger les images au démarrage
if images_list:
    show_image(0)

# Charger les listes des mots-clés et thématiques uniquement lorsque l'utilisateur interagit
themes_listbox.bind("<Enter>", lambda event: update_lists())
keywords_listbox.bind("<Enter>", lambda event: update_lists())

# Lancement de l'application
root.mainloop()