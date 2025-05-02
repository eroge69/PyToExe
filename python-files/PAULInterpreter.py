import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import re
import random

class PAULInterpreter:
    def __init__(self, root):
        self.root = root
        self.root.title("PAUL Interpreter")
        self.root.configure(bg='black')
        
        # Configuration des styles
        self.syntax_tags = {
            'keyword': {'foreground': '#00A3E0'},
            'variable': {'foreground': '#6CBB3C'},
            'string': {'foreground': '#E3256B'},
            'number': {'foreground': '#FFD700'},
            'operator': {'foreground': '#FFFFFF'},
            'comment': {'foreground': '#888888'},
            'error': {'underline': True, 'foreground': 'red'}
        }
        
        # Zone d'entrée multi-lignes
        self.input_text = tk.Text(root, height=20, width=100, bg='black', fg='white', 
                                insertbackground='white', font=('Courier New', 12))
        self.input_text.pack(pady=5, padx=5, expand=True, fill='both')
        
        # Barre de menus
        self.create_menu()
        
        # Bouton Exécuter
        self.execute_btn = tk.Button(root, text="Exécuter", command=self.execute, 
                                   bg='gray', fg='white', width=20)
        self.execute_btn.pack(pady=2)
        
        # Console de sortie
        self.console = scrolledtext.ScrolledText(root, width=100, height=15, 
                                            bg='black', fg='white', font=('Courier New', 12))
        self.console.pack(pady=5, padx=5, expand=True, fill='both')
        
        # Variables globales
        self.variables = {}
        self.functions = {}
        self.error_count = 0
        self.current_file = None
        
        # Liaison des événements
        self.input_text.bind('<KeyRelease>', self.on_text_change)
        self.input_text.bind('<Control-s>', lambda e: self.save_file())
        
        # Appliquer la coloration initiale
        self.apply_syntax_highlighting()

    def create_menu(self):
        """Crée la barre de menus"""
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nouveau", command=self.new_file)
        file_menu.add_command(label="Ouvrir", command=self.open_file)
        file_menu.add_command(label="Enregistrer", command=self.save_file)
        file_menu.add_command(label="Enregistrer sous", command=lambda: self.save_file(save_as=True))
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        menubar.add_cascade(label="Fichier", menu=file_menu)
        self.root.config(menu=menubar)

    def apply_syntax_highlighting(self):
        """Applique la coloration syntaxique au texte"""
        # Supprime toutes les tags existantes
        for tag in self.syntax_tags:
            self.input_text.tag_remove(tag, "1.0", tk.END)
        
        # Définition des motifs de recherche
        patterns = {
            'keyword': r'\b(si|sino|alter|tenko|calm|pro|arb|rov|alarm|correct|zap|pong|mip)\b',
            'variable': r'\$[^$?]*\?',
            'string': r"(['«]).*?(['»])",
            'number': r'\b\d+\.?\d*\b',
            'operator': r'[\+\-\*/%=<>\&\|!]',
            'comment': r'#.*$'
        }
        
        # Applique les tags
        for tag, pattern in patterns.items():
            for match in re.finditer(pattern, self.input_text.get("1.0", tk.END), re.MULTILINE):
                start_idx = f"1.0 + {match.start()} chars"
                end_idx = f"1.0 + {match.end()} chars"
                self.input_text.tag_add(tag, start_idx, end_idx)
        
        # Configuration des tags
        for tag, style in self.syntax_tags.items():
            self.input_text.tag_config(tag, **style)
        
        # Planifie la prochaine mise à jour
        self.input_text.after(500, self.apply_syntax_highlighting)

    def on_text_change(self, event=None):
        """Gère les changements de texte"""
        self.remove_error_highlights()
        self.apply_syntax_highlighting()

    def remove_error_highlights(self):
        """Supprime les soulignements d'erreurs"""
        self.input_text.tag_remove('error', "1.0", tk.END)

    def highlight_error_line(self, line_number):
        """Souligne une ligne spécifique en rouge"""
        line_start = f"{line_number + 1}.0"
        line_end = f"{line_number + 1}.end"
        self.input_text.tag_add('error', line_start, line_end)

    def execute(self):
        """Exécute le code PAUL saisi"""
        code = self.input_text.get("1.0", tk.END).strip()
        if not code:
            return
            
        self.console.delete("1.0", tk.END)
        self.console.insert(tk.END, ">>> [Exécution du code]\n")
        
        lines = code.splitlines()
        error_occurred = False
        
        try:
            # Exécution du code
            error_occurred = self._parse_lines(lines)
            
            if not error_occurred:
                self.console.insert(tk.END, "✅ Exécution terminée avec succès\n")
            else:
                self.console.insert(tk.END, "❗ Erreurs détectées pendant l'exécution\n")
                
        except Exception as e:
            self._show_error(f"ERREUR CRITIQUE: {str(e)}")
        
        self.console.see(tk.END)

    def _parse_lines(self, lines):
        """Parse et exécute les lignes de code"""
        error_occurred = False
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            original_line = line
            line_number = i
            
            if not line:
                i += 1
                continue
                
            # Suppression des commentaires
            line = re.sub(r'#.*$', '', line).strip()
            
            try:
                # Déclaration de variable
                if re.match(r'^\$.+?\?.*$', line):
                    self._parse_variable(line, line_number)
                    
                # Affichage avec mip
                elif line.startswith('mip ') or re.search(r'\.mip$', line):
                    self._parse_mip(line)
                    
                # Conditions
                elif line.startswith('si '):
                    i += self._parse_condition(lines[i:])
                    
                # Boucle tenko (while)
                elif line.startswith('tenko '):
                    i += self._parse_loop(lines[i:])
                    
                # Boucle pro (for)
                elif line.startswith('pro '):
                    i += self._parse_for_loop(lines[i:])
                    
                # Gestion d'erreur
                elif line.startswith('alarm'):
                    i += self._parse_error_handling(lines[i:])
                    
                # Import de module
                elif line.startswith('pong '):
                    self._parse_import(line)
                    
                # Fonction arbre
                elif line.startswith('arb '):
                    i += self._parse_function(lines[i:])
                    
                # Opération mathématique simple
                elif re.match(r'^[\d+\s*[+\-*/%]\s*\d+.*$', line):
                    try:
                        result = eval(line)
                        self.console.insert(tk.END, f"{result}\n")
                    except Exception as e:
                        self._show_error(f"Calcul invalide: {str(e)}", line_number)
                        error_occurred = True
                        
                # Commande inconnue
                else:
                    if line:  # Si la ligne n'est pas vide après suppression du commentaire
                        self._show_error(f"Commande non reconnue: {original_line}", line_number)
                        error_occurred = True
                        
            except Exception as e:
                self._show_error(f"Erreur à la ligne {i+1}: {str(e)}", i)
                error_occurred = True
            
            i += 1
        
        return error_occurred

    def _show_error(self, message, line_number=None):
        """Affiche une erreur personnalisée et souligne la ligne"""
        self.error_count += 1
        self.console.insert(tk.END, f"❌ ERREUR #{self.error_count}: {message}\n", 'error')
        self.console.tag_configure('error', foreground='red')
        
        if line_number is not None:
            self.highlight_error_line(line_number)

    def _parse_variable(self, line, line_number):
        """Parse une déclaration de variable PAUL"""
        try:
            # Vérification des symboles $ et ?
            if not (line.startswith('$') and '?' in line):
                self._show_error("Erreur de syntaxe: Symboles $ ou ? manquants", line_number)
                return
                
            # Extraction du nom et de la valeur
            var_content = line[1:].split('?', 1)[0].strip()
            name_value = var_content.split('=', 1)
            
            if len(name_value) != 2:
                self._show_error("Erreur de syntaxe: Opérateur = manquant", line_number)
                return
                
            name = name_value[0].strip()
            value = name_value[1].strip()
            
            # Détection du type
            if re.match(r'^\d+$', value):
                self.variables[name] = {'type': 'NUM', 'value': int(value)}
            elif re.match(r'^\d+\.\d+$', value):
                self.variables[name] = {'type': 'VIRG', 'value': float(value)}
            elif value.upper() in ['VRAI', 'FAUX']:
                self.variables[name] = {'type': 'BOOL', 'value': value.upper() == 'VRAI'}
            elif re.match(r"^['«].*['»]$", value.strip()):
                # Nettoyage des guillemets/apostrophes
                cleaned_value = value[1:-1]
                self.variables[name] = {'type': 'CHAINE', 'value': cleaned_value}
            else:
                self._show_error(f"Type non reconnu pour la valeur: {value}", line_number)
                return
                
        except Exception as e:
            self._show_error(f"Erreur lors de la déclaration: {str(e)}", line_number)

    def _parse_mip(self, line):
        """Parse une commande d'affichage"""
        try:
            if '.mip' in line:
                # Méthode directe avec .mip
                var_name = line.split('.')[0].strip()
                if var_name in self.variables:
                    value = self.variables[var_name]['value']
                    self.console.insert(tk.END, f"{value}\n")
                else:
                    self._show_error(f"Variable non trouvée: {var_name}")
            else:
                # Méthode classique avec mip
                content = line[4:].strip()
                if content.startswith('$'):
                    # Déclaration et affichage direct
                    self._parse_variable(content, -1)
                    var_name = content.split('=', 1)[0].strip()[1:]
                    value = self.variables[var_name]['value']
                    self.console.insert(tk.END, f"{value}\n")
                elif content in self.variables:
                    value = self.variables[content]['value']
                    self.console.insert(tk.END, f"{value}\n")
                elif re.match(r"^['«].*['»]$", content):
                    self.console.insert(tk.END, f"{content[1:-1]}\n")
                else:
                    self._show_error(f"Impossible d'afficher: {content}")
        except Exception as e:
            self._show_error(f"Erreur d'affichage: {str(e)}")

    def _parse_condition(self, lines):
        """Parse une structure conditionnelle si/sino/alter"""
        try:
            count = 0
            current_line = lines[0]
            condition = current_line[3:].strip()
            
            # Évaluation de la condition
            result = self._evaluate_condition(condition)
            executed_block = False
            
            for i in range(1, len(lines)):
                line = lines[i].strip()
                count += 1
                
                if line == 'nf':
                    break
                    
                if line.startswith('sino:') or line.startswith('alter:'):
                    if not executed_block:
                        # Exécution du bloc sino/alter
                        if line.startswith('sino:'):
                            sub_lines = [l for l in lines[i+1:]]
                            self._parse_lines(sub_lines)
                            break
                        elif line.startswith('alter:'):
                            # Gestion de la condition supplémentaire
                            alter_cond = line[6:].strip()
                            if self._evaluate_condition(alter_cond):
                                sub_lines = [l for l in lines[i+1:]]
                                self._parse_lines(sub_lines)
                                break
                elif result and not executed_block:
                    # Exécution du bloc si
                    executed_block = True
                    sub_lines = [line]
                    self._parse_lines(sub_lines)
                    
            return count
        except Exception as e:
            self._show_error(f"Erreur de condition: {str(e)}")
            return 1

    def _parse_loop(self, lines):
        """Parse une boucle tenko (while)"""
        try:
            count = 0
            current_line = lines[0]
            condition = current_line[6:].strip()
            
            while self._evaluate_condition(condition):
                for i in range(1, len(lines)):
                    line = lines[i].strip()
                    count += 1
                    
                    if line == 'calm':
                        return count
                        
                    self._parse_lines([line])
                    
            return count
        except Exception as e:
            self._show_error(f"Erreur de boucle: {str(e)}")
            return 1

    def _parse_for_loop(self, lines):
        """Parse une boucle pro (for)"""
        try:
            count = 0
            current_line = lines[0]
            pattern = r'pro\s+(\w+)\s+ds\s+rang\s+(\d+)(?:\s+p(?:as)?\s+(\d+))?'
            match = re.match(pattern, current_line)
            
            if not match:
                self._show_error("Syntaxe de boucle 'pro' invalide")
                return 1
                
            var_name, end, step = match.groups()
            start = 1
            step = int(step) if step else 1
            end = int(end)
            
            for i in range(start, end + 1, step):
                self.variables[var_name] = {'type': 'NUM', 'value': i}
                for j in range(1, len(lines)):
                    line = lines[j].strip()
                    count += 1
                    
                    if line == 'calm':
                        return count
                        
                    self._parse_lines([line])
                    
            return count
        except Exception as e:
            self._show_error(f"Erreur de boucle 'pro': {str(e)}")
            return 1

    def _parse_error_handling(self, lines):
        """Parse une structure alarm/correct/zap"""
        try:
            count = 0
            in_error_block = False
            
            for i in range(len(lines)):
                line = lines[i].strip()
                count += 1
                
                if line == 'alarm':
                    in_error_block = True
                elif line.startswith('correct:') and in_error_block:
                    try:
                        # Exécution du bloc protégé
                        sub_lines = lines[1:i]
                        self._parse_lines(sub_lines)
                    except Exception as e:
                        # Gestion de l'erreur
                        self._show_error(f"Gestion d'erreur: {str(e)}")
                        error_lines = lines[i+1:]
                        if error_lines and error_lines[0].strip() != 'zap':
                            self._parse_lines(error_lines)
                    finally:
                        # Passage au bloc suivant
                        if 'zap' in lines:
                            zap_index = lines.index('zap', i)
                            count += (zap_index - i)
                            return count
                        return count
            return count
        except Exception as e:
            self._show_error(f"Erreur dans la gestion d'erreurs: {str(e)}")
            return 1

    def _parse_import(self, line):
        """Parse une commande d'importation"""
        try:
            module = line.split(' ', 1)[1].strip()
            # Implémentation simplifiée - dans un vrai cas, chargerait le module
            self.console.insert(tk.END, f"Module '{module}' importé\n")
        except Exception as e:
            self._show_error(f"Erreur d'import: {str(e)}")

    def _parse_function(self, lines):
        """Parse une déclaration de fonction"""
        try:
            count = 0
            current_line = lines[0]
            func_match = re.match(r'arb\s+(\w+)\s*$([^)]*)$', current_line)
            
            if not func_match:
                self._show_error("Syntaxe de fonction invalide")
                return 1
                
            func_name, params = func_match.groups()
            body = []
            
            for i in range(1, len(lines)):
                line = lines[i].strip()
                count += 1
                
                if line == '~':
                    break
                    
                body.append(line)
                
            self.functions[func_name] = {
                'params': [p.strip() for p in params.split(',')] if params else [],
                'body': body
            }
            
            return count
        except Exception as e:
            self._show_error(f"Erreur de fonction: {str(e)}")
            return 1

    def _evaluate_condition(self, condition):
        """Évalue une condition logique"""
        try:
            # Remplacement des opérateurs PAUL par des opérateurs Python
            condition = condition.replace('==', '==').replace('!=', '!=')
            condition = condition.replace('<', '<').replace('>', '>')
            condition = condition.replace('=<', '<=').replace('=>', '>=')
            condition = condition.replace('||', 'or').replace('&&', 'and').replace('!', 'not ')
            
            # Remplacement des noms de variables par leurs valeurs
            for var_name, var_info in self.variables.items():
                if var_name in condition:
                    value = var_info['value']
                    if isinstance(value, str):
                        condition = condition.replace(var_name, f"'{value}'")
                    else:
                        condition = condition.replace(var_name, str(value))
                        
            return eval(condition)
        except Exception as e:
            self._show_error(f"Erreur d'évaluation de condition: {str(e)}")
            return False

    # Fonctions de gestion de fichiers
    def new_file(self):
        """Crée un nouveau fichier"""
        if messagebox.askokcancel("Nouveau", "Voulez-vous créer un nouveau fichier ?"):
            self.input_text.delete("1.0", tk.END)
            self.current_file = None

    def open_file(self):
        """Ouvre un fichier existant"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Fichiers PAUL", "*.pol"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.input_text.delete("1.0", tk.END)
                    self.input_text.insert("1.0", file.read())
                self.current_file = file_path
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {str(e)}")

    def save_file(self, save_as=False):
        """Sauvegarde le fichier"""
        if not save_as and self.current_file:
            file_path = self.current_file
        else:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pol",
                filetypes=[("Fichiers PAUL", "*.pol"), ("Tous les fichiers", "*.*")]
            )
            if not file_path:
                return
            self.current_file = file_path
        
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.input_text.get("1.0", tk.END))
            messagebox.showinfo("Succès", "Fichier sauvegardé avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder le fichier : {str(e)}")

def main():
    root = tk.Tk()
    app = PAULInterpreter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
