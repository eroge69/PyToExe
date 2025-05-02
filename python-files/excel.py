import pandas as pd
import math
import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading

class ExcelSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Splitter Avancé")
        self.root.geometry("900x900")
        self.root.resizable(True, True)

        # Variables
        self.input_file_path = tk.StringVar()
        self.output_folder_path = tk.StringVar()
        self.rows_per_file = tk.IntVar(value=500)
        self.file_prefix = tk.StringVar(value="Template")
        self.split_mode = tk.StringVar(value="rows")
        self.selected_column = tk.StringVar()

        # Données
        self.data = None
        self.columns = []

        documents_path = os.path.join(Path.home(), "Documents", "ExcelSplitter")
        self.output_folder_path.set(documents_path)

        self.create_widgets()
        self.root.focus_force()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=5)
        style.configure("TLabelframe", padding=10)
        style.configure("TRadiobutton", padding=5)

        style.configure("Accent.TButton", background="#4e73df", foreground="white")

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_canvas = tk.Canvas(main_frame)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=main_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        main_canvas.configure(yscrollcommand=scrollbar.set)
        main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

        content_frame = ttk.Frame(main_canvas)
        main_canvas.create_window((0, 0), window=content_frame, anchor="nw", width=880)

        input_frame = ttk.LabelFrame(content_frame, text="Fichier Excel à diviser")
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(input_frame, text="Fichier:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        input_buttons_frame = ttk.Frame(input_frame)
        input_buttons_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        input_buttons_frame.columnconfigure(0, weight=1)

        ttk.Entry(input_buttons_frame, textvariable=self.input_file_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(input_buttons_frame, text="Parcourir...", command=self.browse_input_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(input_buttons_frame, text="Charger", command=self.load_file).pack(side=tk.LEFT)

        self.split_mode_frame = ttk.LabelFrame(content_frame, text="Mode de division")
        self.split_mode_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Radiobutton(self.split_mode_frame, text="Division par nombre de lignes", variable=self.split_mode,
                        value="rows", command=self.update_ui_for_mode).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(self.split_mode_frame, text="Division par valeurs de colonne", variable=self.split_mode,
                        value="column", command=self.update_ui_for_mode).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        self.rows_config_frame = ttk.LabelFrame(content_frame, text="Configuration (division par lignes)")
        self.rows_config_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(self.rows_config_frame, text="Nombre de lignes par fichier:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(self.rows_config_frame, from_=1, to=10000, textvariable=self.rows_per_file, width=10).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.column_config_frame = ttk.LabelFrame(content_frame, text="Configuration (division par colonne)")
        ttk.Label(self.column_config_frame, text="Sélectionnez la colonne:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.column_combobox = ttk.Combobox(self.column_config_frame, textvariable=self.selected_column, state="readonly", width=30)
        self.column_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        preview_frame = ttk.LabelFrame(self.column_config_frame, text="Aperçu des valeurs distinctes")
        preview_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

        columns = ("valeur", "nombre")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=8)
        self.preview_tree.heading("valeur", text="Valeur distincte")
        self.preview_tree.heading("nombre", text="Nombre d'occurrences")
        self.preview_tree.column("valeur", width=450)
        self.preview_tree.column("nombre", width=200, anchor=tk.CENTER)

        preview_scroll = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scroll.set)
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        prefix_frame = ttk.LabelFrame(content_frame, text="Paramètres communs")
        prefix_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(prefix_frame, text="Préfixe des fichiers:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(prefix_frame, textvariable=self.file_prefix, width=20).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        output_frame = ttk.LabelFrame(content_frame, text="Dossier de sortie")
        output_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(output_frame, text="Dossier:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        output_buttons_frame = ttk.Frame(output_frame)
        output_buttons_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        output_buttons_frame.columnconfigure(0, weight=1)

        ttk.Entry(output_buttons_frame, textvariable=self.output_folder_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_buttons_frame, text="Parcourir...", command=self.browse_output_folder).pack(side=tk.LEFT)

        progress_frame = ttk.Frame(content_frame)
        progress_frame.pack(fill=tk.X, padx=5, pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)

        status_frame = ttk.Frame(content_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        self.status_var = tk.StringVar(value="Prêt. Veuillez charger un fichier Excel.")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5)

        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        self.split_button = ttk.Button(button_frame, text="Diviser le fichier Excel", command=self.split_excel, state=tk.DISABLED)
        self.split_button.pack(side=tk.RIGHT, padx=5)

        self.update_ui_for_mode()

    def update_ui_for_mode(self):
        """Met à jour l'interface selon le mode de division sélectionné"""
        if self.split_mode.get() == "rows":
            if hasattr(self, 'column_config_frame'):
                self.column_config_frame.pack_forget()
            self.rows_config_frame.pack(fill=tk.X, padx=5, pady=5, after=self.split_mode_frame)
        else:
            self.rows_config_frame.pack_forget()
            self.column_config_frame.pack(fill=tk.X, padx=5, pady=5, after=self.split_mode_frame)
    
    def browse_input_file(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier Excel d'entrée"""
        filetypes = [("Fichiers Excel", "*.xlsx *.xls"), ("Tous les fichiers", "*.*")]
        filename = filedialog.askopenfilename(filetypes=filetypes, title="Sélectionner un fichier Excel")
        if filename:
            self.input_file_path.set(filename)
            self.root.focus_force()
    
    def browse_output_folder(self):
        """Ouvre une boîte de dialogue pour sélectionner le dossier de sortie"""
        folder = filedialog.askdirectory(title="Sélectionner un dossier de sortie")
        if folder:
            self.output_folder_path.set(folder)
            self.root.focus_force()
    
    def load_file(self):
        """Charge le fichier Excel et extrait les colonnes"""
        if not self.input_file_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier Excel d'entrée.")
            self.root.focus_force()
            return
        
        try:
            self.update_status("Chargement du fichier Excel...")
            self.progress_var.set(0)
            self.root.update_idletasks()
            
            # Désactiver les boutons pendant le chargement
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget['state'] = tk.DISABLED
            
            # Charger le fichier
            self.data = pd.read_excel(self.input_file_path.get())
            self.columns = list(self.data.columns)
            
            # Mettre à jour l'interface
            self.column_combobox['values'] = self.columns
            if self.columns:
                self.column_combobox.current(0)
                self.update_column_preview()
            
            self.split_button['state'] = tk.NORMAL
            self.split_button.focus_set()
            
            num_rows = len(self.data)
            num_cols = len(self.columns)
            self.update_status(f"Fichier chargé : {num_rows} lignes, {num_cols} colonnes")
            
            self.column_combobox.bind("<<ComboboxSelected>>", lambda e: self.update_column_preview())
            
            # Réactiver les boutons
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget['state'] = tk.NORMAL
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le fichier : {str(e)}")
            self.update_status(f"Erreur : {str(e)}")
            self.root.focus_force()
    
    def update_column_preview(self):
        """Met à jour l'aperçu des valeurs distinctes pour la colonne sélectionnée"""
        if self.data is None or not self.selected_column.get():
            return
            
        try:
            # Effacer le tableau d'aperçu
            self.preview_tree.delete(*self.preview_tree.get_children())
            
            # Obtenir les valeurs distinctes (limitée à 50 pour la performance)
            col_name = self.selected_column.get()
            value_counts = self.data[col_name].value_counts().reset_index().head(50)
            value_counts.columns = ['value', 'count']
            
            # Ajouter les valeurs au tableau
            for _, row in value_counts.iterrows():
                self.preview_tree.insert("", tk.END, values=(row['value'], row['count']))
            
            # Ajouter une note si la liste est tronquée
            total_unique = self.data[col_name].nunique()
            if total_unique > 50:
                self.preview_tree.insert("", tk.END, values=(f"... (liste tronquée à 50 valeurs sur {total_unique}) ...", ""))
            
            self.update_status(f"Colonne '{col_name}' - {total_unique} valeurs uniques (affichage limité)")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse de la colonne : {str(e)}")
            self.update_status(f"Erreur : {str(e)}")
            self.root.focus_force()
    
    def update_status(self, message):
        """Met à jour le message de statut"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def split_by_rows(self, output_folder, date_aujourdhui):
        """Divise le fichier par nombre de lignes"""
        try:
            count = len(self.data)
            rows_per_file = self.rows_per_file.get()
            no_of_files = math.ceil(count/rows_per_file)
            
            self.update_status(f"Divisant {count} lignes en {no_of_files} fichiers...")
            self.progress_var.set(0)
            
            for x in range(no_of_files):
                start_row = x * rows_per_file
                end_row = min((x + 1) * rows_per_file, count)
                
                new_data = self.data.iloc[start_row:end_row]
                output_file = os.path.join(
                    output_folder, 
                    f"{self.file_prefix.get()}_{date_aujourdhui}_{x}.xlsx"
                )
                
                new_data.to_excel(output_file, index=False)
                
                progress = (x + 1) / no_of_files * 100
                self.progress_var.set(progress)
                self.update_status(f"Création du fichier {x+1}/{no_of_files} : {os.path.basename(output_file)}")
                self.root.update_idletasks()
            
            return no_of_files
        
        except Exception as e:
            raise Exception(f"Erreur lors de la division par lignes : {str(e)}")
    
    def split_by_column(self, output_folder, date_aujourdhui):
        """Divise le fichier par valeurs de colonne"""
        try:
            col_name = self.selected_column.get()
            unique_values = self.data[col_name].unique()
            no_of_files = len(unique_values)
            
            self.update_status(f"Divisant selon les {no_of_files} valeurs de la colonne '{col_name}'...")
            self.progress_var.set(0)
            
            for i, value in enumerate(unique_values):
                filtered_data = self.data[self.data[col_name] == value]
                
                safe_value = str(value).replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_") \
                             .replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
                if len(safe_value) > 50:
                    safe_value = safe_value[:50]
                
                output_file = os.path.join(
                    output_folder, 
                    f"{self.file_prefix.get()}_{date_aujourdhui}_{safe_value}.xlsx"
                )
                
                filtered_data.to_excel(output_file, index=False)
                
                progress = (i + 1) / no_of_files * 100
                self.progress_var.set(progress)
                self.update_status(f"Création du fichier {i+1}/{no_of_files} : {os.path.basename(output_file)}")
                self.root.update_idletasks()
            
            return no_of_files
        
        except Exception as e:
            raise Exception(f"Erreur lors de la division par colonne : {str(e)}")
    
    def split_excel_thread(self):
        """Fonction exécutée dans un thread séparé pour diviser le fichier Excel"""
        try:
            # Désactiver les widgets pendant le traitement
            self.split_button['state'] = tk.DISABLED
            for widget in self.root.winfo_children():
                if isinstance(widget, (ttk.Button, ttk.Entry, ttk.Combobox)):
                    widget['state'] = tk.DISABLED
            
            # Vérification des entrées
            if not self.input_file_path.get():
                messagebox.showerror("Erreur", "Veuillez sélectionner un fichier Excel d'entrée.")
                return
            
            if self.data is None:
                messagebox.showerror("Erreur", "Veuillez d'abord charger le fichier.")
                return
            
            if self.split_mode.get() == "column" and not self.selected_column.get():
                messagebox.showerror("Erreur", "Veuillez sélectionner une colonne pour la division.")
                return
            
            # Création du dossier de sortie
            output_folder = self.output_folder_path.get()
            os.makedirs(output_folder, exist_ok=True)
            
            date_aujourdhui = datetime.datetime.now().strftime("%Y%m%d")
            
            if self.split_mode.get() == "rows":
                no_of_files = self.split_by_rows(output_folder, date_aujourdhui)
                mode_str = "par nombre de lignes"
            else:
                no_of_files = self.split_by_column(output_folder, date_aujourdhui)
                mode_str = f"par valeurs de la colonne '{self.selected_column.get()}'"
            
            self.update_status(f"Terminé ! {no_of_files} fichiers créés dans {output_folder}")
            messagebox.showinfo("Succès", f"Division {mode_str} terminée !\n{no_of_files} fichiers ont été créés dans le dossier :\n{output_folder}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
            self.update_status(f"Erreur : {str(e)}")
        
        finally:
            # Réactiver les widgets
            self.split_button['state'] = tk.NORMAL
            for widget in self.root.winfo_children():
                if isinstance(widget, (ttk.Button, ttk.Entry, ttk.Combobox)):
                    widget['state'] = tk.NORMAL
            self.root.focus_force()
    
    def split_excel(self):
        """Lance la division du fichier Excel dans un thread séparé"""
        threading.Thread(target=self.split_excel_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelSplitterApp(root)
    root.mainloop()
