# SPACE INVADERS

import tkinter as tk
from tkinter import messagebox
import random
import time
from abc import ABC, abstractmethod
import sys

class GameObject(ABC):
    """Classe abstraite de base pour tous les objets du jeu"""
    def __init__(self, canvas, x, y, width, height, color, speed):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.object = self.canvas.create_rectangle(
            x, y, x + width, y + height, fill=color
        )
        
    def move(self, dx, dy):
        """Déplace l'objet sur le canvas"""
        self.canvas.move(self.object, dx, dy)
        self.x += dx
        self.y += dy
        
    def collision(self, other):
        """Détecte la collision avec un autre objet"""
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)
    
    def delete(self):
        """Supprime l'objet du canvas"""
        self.canvas.delete(self.object)

class Joueur(GameObject):
    """Classe représentant le vaisseau du joueur"""
    def __init__(self, canvas):
        super().__init__(canvas, 400, 550, 40, 20, "blue", 8)
        self.vies = 3
        self.score = 0
        self.invincible = False
        self.invincible_timer = 0
        self.power_up_active = False
        self.power_up_timer = 0
        
    def tirer(self):
        """Crée un nouveau projectile"""
        if self.power_up_active:
            # Tir multiple si power-up actif
            return [
                Rocket(self.canvas, self.x + self.width/2 - 10, self.y),
                Rocket(self.canvas, self.x + self.width/2, self.y),
                Rocket(self.canvas, self.x + self.width/2 + 10, self.y)
            ]
        return [Rocket(self.canvas, self.x + self.width/2, self.y)]
    
    def hit(self):
        """Gère l'impact d'une bombe sur le joueur"""
        if not self.invincible:
            self.vies -= 1
            self.invincible = True
            self.invincible_timer = time.time()
            self.canvas.itemconfig(self.object, fill="gray")
    
    def update_invincibility(self):
        """Met à jour l'état d'invincibilité"""
        if self.invincible and time.time() - self.invincible_timer > 2:
            self.invincible = False
            self.canvas.itemconfig(self.object, fill="blue")
            
    def activate_power_up(self):
        """Active le power-up pour le joueur"""
        self.power_up_active = True
        self.power_up_timer = time.time()
        self.canvas.itemconfig(self.object, fill="gold")
        
    def update_power_up(self):
        """Met à jour l'état du power-up"""
        if self.power_up_active and time.time() - self.power_up_timer > 10:
            self.power_up_active = False
            self.canvas.itemconfig(self.object, fill="blue")

class Ennemi(GameObject):
    """Classe représentant les ennemis"""
    def __init__(self, canvas, x, y, niveau, type_ennemi="normal"):
        self.type = type_ennemi
        color = self._get_color()
        vitesse = self._get_speed(niveau)
        width, height = self._get_dimensions()
        super().__init__(canvas, x, y, width, height, color, vitesse)
        self.direction = 1
        self.points = self._get_points()
        self.last_shot = time.time()
        
    def _get_color(self):
        """Définit la couleur selon le type d'ennemi"""
        colors = {
            "normal": "red",
            "elite": "purple",
            "boss": "darkred"
        }
        return colors.get(self.type, "red")
    
    def _get_speed(self, niveau):
        """Calcule la vitesse selon le type et le niveau"""
        base_speed = 2 + niveau * 0.3
        speed_multiplier = {
            "normal": 1,
            "elite": 1.5,
            "boss": 0.7
        }
        return base_speed * speed_multiplier.get(self.type, 1)
    
    def _get_dimensions(self):
        """Définit les dimensions selon le type"""
        dimensions = {
            "normal": (30, 30),
            "elite": (40, 40),
            "boss": (60, 60)
        }
        return dimensions.get(self.type, (30, 30))
    
    def _get_points(self):
        """Définit les points selon le type"""
        points = {
            "normal": 100,
            "elite": 200,
            "boss": 500
        }
        return points.get(self.type, 100)
        
    def tirer(self):
        """Gère le tir des ennemis avec un délai minimum"""
        current_time = time.time()
        if current_time - self.last_shot < 1:  # Délai minimum entre les tirs
            return None
            
        probabilites = {
            "normal": 0.01,
            "elite": 0.02,
            "boss": 0.03
        }
        if random.random() < probabilites.get(self.type, 0.01):
            self.last_shot = current_time
            return Bombe(self.canvas, self.x + self.width/2, self.y + self.height)
        return None
class Projectile(GameObject):
    """Classe abstraite de base pour tous les projectiles"""
    def __init__(self, canvas, x, y, width, height, color, speed):
        super().__init__(canvas, x, y, width, height, color, speed)
    
    @abstractmethod
    def update(self):
        """Méthode abstraite pour mettre à jour la position du projectile"""
        pass

class Rocket(Projectile):
    """Classe représentant les projectiles du joueur"""
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, 4, 10, "yellow", -10)
        
    def update(self):
        """Met à jour la position de la rocket et vérifie si elle sort de l'écran"""
        self.move(0, self.speed)
        return self.y < 0

class Bombe(Projectile):
    """Classe représentant les projectiles ennemis"""
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, 4, 10, "orange", 7)
        
    def update(self):
        """Met à jour la position de la bombe et vérifie si elle sort de l'écran"""
        self.move(0, self.speed)
        return self.y > 600

class ScoreBoard:
    """Classe gérant l'affichage du score et des informations de jeu"""
    def __init__(self, canvas):
        self.canvas = canvas
        self.score_text = canvas.create_text(
            50, 20, text="Score: 0", fill="white", anchor="w"
        )
        self.lives_text = canvas.create_text(
            50, 40, text="Vies: 3", fill="white", anchor="w"
        )
        self.level_text = canvas.create_text(
            50, 60, text="Niveau: 1", fill="white", anchor="w"
        )
        self.difficulty_text = canvas.create_text(
            50, 80, text="Difficulté: Normal", fill="white", anchor="w"
        )
    
    def update(self, score, vies, niveau, difficulty):
        """Met à jour l'affichage des informations"""
        self.canvas.itemconfig(self.score_text, text=f"Score: {score}")
        self.canvas.itemconfig(self.lives_text, text=f"Vies: {vies}")
        self.canvas.itemconfig(self.level_text, text=f"Niveau: {niveau}")
        self.canvas.itemconfig(self.difficulty_text, text=f"Difficulté: {difficulty.capitalize()}")

class DifficultySelector:
    """Classe pour la sélection de la difficulté"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Sélection de la difficulté")
        self.window.geometry("300x200")
        self.window.transient(parent)  # Rend la fenêtre modale
        self.window.grab_set()  # Force le focus sur cette fenêtre
        
        self.selected_difficulty = None
        
        tk.Label(self.window, text="Choisissez la difficulté:",
                font=("Arial", 14)).pack(pady=10)
        
        for diff in ["Facile", "Normal", "Difficile"]:
            tk.Button(self.window, text=diff,
                     command=lambda d=diff.lower(): self.set_difficulty(d),
                     width=20, height=2).pack(pady=5)
    
    def set_difficulty(self, difficulty):
        """Définit la difficulté choisie et ferme la fenêtre"""
        self.selected_difficulty = difficulty
        self.window.destroy()

class Menu:
    """Classe gérant le menu principal du jeu"""
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root, bg="black")
        self.frame.pack(expand=True, fill="both")
        
        # Titre
        tk.Label(self.frame, text="SPACE INVADERS", font=("Arial", 24), 
                bg="black", fg="white").pack(pady=20)
        
        # Boutons
        styles = {"font": ("Arial", 12), "width": 20, "height": 2}
        tk.Button(self.frame, text="JOUER", command=self.start_game,
                 **styles).pack(pady=10)
        tk.Button(self.frame, text="RÈGLES", command=self.show_rules,
                 **styles).pack(pady=10)
        tk.Button(self.frame, text="QUITTER", command=self.quit_game,
                 **styles).pack(pady=10)
        
    def show_rules(self):
        """Affiche les règles du jeu"""
        rules = """
        RÈGLES DU JEU:
        
        - Utilisez les flèches GAUCHE/DROITE pour vous déplacer
        - ESPACE pour tirer
        - Évitez les bombes ennemies
        - Détruisez tous les envahisseurs
        
        TYPES D'ENNEMIS:
        - Rouge: Ennemi normal (100 pts)
        - Violet: Ennemi élite (200 pts)
        - Rouge foncé: Boss (500 pts)
        
        POWER-UPS:
        - Or: Tir multiple pendant 10 secondes
        """
        messagebox.showinfo("Règles", rules)
    
    def start_game(self):
        """Lance le processus de sélection de difficulté puis démarre le jeu"""
        difficulty_selector = DifficultySelector(self.root)
        self.root.wait_window(difficulty_selector.window)
        
        if difficulty_selector.selected_difficulty:
            self.frame.destroy()
            Game(self.root, difficulty_selector.selected_difficulty)
            
    def quit_game(self):
        """Ferme le jeu"""
        self.root.quit()
        self.root.destroy()
        sys.exit()
class Game:
    """Classe principale gérant le déroulement du jeu"""
    def __init__(self, root, difficulty):
        """Initialise une nouvelle partie"""
        self.root = root
        self.difficulty = difficulty
        self.setup_game_window()
        self.initialize_game_variables()
        self.create_game_objects()
        self.setup_controls()
        self.update()
        
    def setup_game_window(self):
        """Configure la fenêtre de jeu et les boutons"""
        # Frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both')
        
        # Frame pour les boutons
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(side='top', fill='x')
        
        # Boutons de contrôle avec style
        button_style = {'padx': 10, 'pady': 5, 'width': 15}
        
        tk.Button(self.button_frame, text="Rejouer",
                 command=self.restart_game,
                 **button_style).pack(side='left', padx=5)
                 
        tk.Button(self.button_frame, text="Menu Principal",
                 command=self.return_to_menu,
                 **button_style).pack(side='left', padx=5)
                 
        tk.Button(self.button_frame, text="Quitter",
                 command=self.quit_game,
                 **button_style).pack(side='right', padx=5)
        
        # Canvas de jeu
        self.canvas = tk.Canvas(self.main_frame, width=800, height=600,
                              bg="black")
        self.canvas.pack(expand=True, fill='both')
        
    def initialize_game_variables(self):
        """Initialise les variables du jeu"""
        self.niveau = 1
        self.game_active = True
        self.pause = False
        self.last_power_up = time.time()
        
        # Paramètres selon la difficulté
        self.difficulty_settings = {
            "facile": {
                "ennemis": 6,
                "elite_prob": 0.1,
                "boss_prob": 0.05,
                "power_up_freq": 15,
                "vitesse_base": 1
            },
            "normal": {
                "ennemis": 8,
                "elite_prob": 0.2,
                "boss_prob": 0.1,
                "power_up_freq": 25,
                "vitesse_base": 1.5
            },
            "difficile": {
                "ennemis": 12,
                "elite_prob": 0.3,
                "boss_prob": 0.15,
                "power_up_freq": 35,
                "vitesse_base": 2
            }
        }
        
    def create_game_objects(self):
        """Crée tous les objets du jeu"""
        self.joueur = Joueur(self.canvas)
        self.scoreboard = ScoreBoard(self.canvas)
        self.ennemis = []
        self.rockets = []
        self.bombes = []
        self.create_ennemis()
        
    def create_ennemis(self):
        """Crée les ennemis selon la difficulté et le niveau"""
        settings = self.difficulty_settings[self.difficulty]
        nb_ennemis = min(settings["ennemis"] + (self.niveau - 1) * 2, 40)  # Maximum 40 ennemis
        
        for i in range(nb_ennemis):
            x = 100 + (i % 10) * 60
            y = 50 + (i // 10) * 50
            
            # Détermination du type d'ennemi
            r = random.random()
            if r < settings["boss_prob"]:
                type_ennemi = "boss"
            elif r < settings["elite_prob"] + settings["boss_prob"]:
                type_ennemi = "elite"
            else:
                type_ennemi = "normal"
                
            self.ennemis.append(Ennemi(self.canvas, x, y, self.niveau,
                                     type_ennemi))
            
    def setup_controls(self):
        """Configure les contrôles du jeu"""
        self.root.bind("<Left>",
                      lambda e: self.move_player(-1) if not self.pause else None)
        self.root.bind("<Right>",
                      lambda e: self.move_player(1) if not self.pause else None)
        self.root.bind("<space>",
                      lambda e: self.player_shoot() if not self.pause else None)
        self.root.bind("<p>", lambda e: self.toggle_pause())
        self.root.bind("<Escape>", lambda e: self.return_to_menu())
        
    def move_player(self, direction):
        """Déplace le joueur en vérifiant les limites de l'écran"""
        new_x = self.joueur.x + (direction * self.joueur.speed)
        if 0 <= new_x <= 760:  # Limites de l'écran
            self.joueur.move(direction * self.joueur.speed, 0)
            
    def player_shoot(self):
        """Gère le tir du joueur"""
        new_rockets = self.joueur.tirer()
        self.rockets.extend(new_rockets)
        
    def toggle_pause(self):
        """Active/Désactive la pause"""
        self.pause = not self.pause
        if self.pause:
            self.canvas.create_text(400, 300, text="PAUSE",
                                  fill="white", font=("Arial", 30),
                                  tags="pause")
        else:
            self.canvas.delete("pause")
        
    def update(self):
        """Boucle principale du jeu"""
        if not self.game_active or self.pause:
            self.root.after(16, self.update)
            return
            
        self.joueur.update_invincibility()
        self.joueur.update_power_up()
        
        # Création possible d'un power-up
        self.check_power_up()
        
        if not self.ennemis:
            self.niveau += 1
            self.create_ennemis()
        
        self.update_ennemis()
        self.update_projectiles()
        self.check_collisions()
        self.scoreboard.update(self.joueur.score, self.joueur.vies,
                             self.niveau, self.difficulty)
        
        if self.joueur.vies > 0:
            self.root.after(16, self.update)
        else:
            self.game_over()
            
    def check_power_up(self):
        """Vérifie si un power-up doit apparaître"""
        current_time = time.time()
        if (current_time - self.last_power_up >
            self.difficulty_settings[self.difficulty]["power_up_freq"]):
            if random.random() < 0.1:  # 10% de chance
                self.last_power_up = current_time
                self.joueur.activate_power_up()
                
    def update_ennemis(self):
        """Met à jour la position des ennemis"""
        move_down = False
        for ennemi in self.ennemis:
            if ((ennemi.x + ennemi.width > 800 and ennemi.direction > 0) or
                (ennemi.x < 0 and ennemi.direction < 0)):
                move_down = True
                break
                
        if move_down:
            for ennemi in self.ennemis:
                ennemi.direction *= -1
                ennemi.move(0, 20)
        else:
            for ennemi in self.ennemis:
                ennemi.move(ennemi.speed * ennemi.direction, 0)
                
        for ennemi in self.ennemis:
            bombe = ennemi.tirer()
            if bombe:
                self.bombes.append(bombe)
                
    def update_projectiles(self):
        """Met à jour la position des projectiles"""
        for projectile in self.rockets[:]:
            if projectile.update():
                projectile.delete()
                self.rockets.remove(projectile)
                
        for projectile in self.bombes[:]:
            if projectile.update():
                projectile.delete()
                self.bombes.remove(projectile)
                
    def check_collisions(self):
        """Vérifie toutes les collisions"""
        # Collision rockets-ennemis
        for rocket in self.rockets[:]:
            for ennemi in self.ennemis[:]:
                if rocket.collision(ennemi):
                    rocket.delete()
                    ennemi.delete()
                    self.rockets.remove(rocket)
                    self.ennemis.remove(ennemi)
                    self.joueur.score += ennemi.points
                    break
                    
        # Collision bombes-joueur
        for bombe in self.bombes[:]:
            if bombe.collision(self.joueur):
                bombe.delete()
                self.bombes.remove(bombe)
                self.joueur.hit()
                
    def game_over(self):
        """Gère la fin de partie"""
        self.game_active = False
        self.canvas.create_text(
            400, 300,
            text=f"GAME OVER\nScore final: {self.joueur.score}\n"
                 f"Niveau atteint: {self.niveau}\n"
                 f"Appuyez sur 'Rejouer' pour recommencer",
            fill="white",
            font=("Arial", 30),
            justify="center"
        )
        
    def restart_game(self):
        """Redémarre le jeu"""
        self.canvas.delete("all")
        self.initialize_game_variables()
        self.create_game_objects()
        self.game_active = True
        self.update()
        
    def return_to_menu(self):
        """Retourne au menu principal"""
        self.main_frame.destroy()
        Menu(self.root)
        
    def quit_game(self):
        """Quitte le jeu"""
        self.root.quit()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Space Invaders")
    menu = Menu(root)
    root.mainloop()
    
