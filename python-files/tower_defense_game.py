import pygame
import math
import random
from enum import Enum

pygame.init()

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 40
TOWER_MENU_WIDTH = 200
GAME_AREA_WIDTH = WIDTH - TOWER_MENU_WIDTH

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BROWN = (165, 42, 42)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Game")
clock = pygame.time.Clock()

path = [
    (0, 3 * GRID_SIZE),
    (5 * GRID_SIZE, 3 * GRID_SIZE),
    (5 * GRID_SIZE, 8 * GRID_SIZE),
    (10 * GRID_SIZE, 8 * GRID_SIZE),
    (10 * GRID_SIZE, 2 * GRID_SIZE),
    (14 * GRID_SIZE, 2 * GRID_SIZE)
]


class TowerType(Enum):
    ARCHER = 1
    MAGIC = 2
    CANNON = 3


class EnemyType(Enum):
    NORMAL = 1
    FAST = 2
    ARMORED = 3
    BOSS = 4


class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.level = 1
        self.target = None
        self.cooldown = 0

        if tower_type == TowerType.ARCHER:
            self.range = 3 * GRID_SIZE
            self.damage = 10
            self.fire_rate = 30
            self.cost = 50
            self.upgrade_cost = 30
            self.color = GREEN
        elif tower_type == TowerType.MAGIC:
            self.range = 2.5 * GRID_SIZE
            self.damage = 15
            self.fire_rate = 45
            self.cost = 100
            self.upgrade_cost = 60
            self.aoe_radius = 1 * GRID_SIZE
            self.color = BLUE
        elif tower_type == TowerType.CANNON:
            self.range = 4 * GRID_SIZE
            self.damage = 40
            self.fire_rate = 75
            self.cost = 150
            self.upgrade_cost = 90
            self.color = RED

    def upgrade(self):
        self.level += 1

        if self.tower_type == TowerType.ARCHER:
            self.damage += 5
            self.range += 0.5 * GRID_SIZE
            self.fire_rate -= 3
            self.upgrade_cost = int(self.upgrade_cost * 1.5)
        elif self.tower_type == TowerType.MAGIC:
            self.damage += 8
            self.range += 0.3 * GRID_SIZE
            self.aoe_radius += 0.2 * GRID_SIZE
            self.upgrade_cost = int(self.upgrade_cost * 1.5)
        elif self.tower_type == TowerType.CANNON:
            self.damage += 15
            self.range += 0.2 * GRID_SIZE
            self.fire_rate -= 5
            self.upgrade_cost = int(self.upgrade_cost * 1.5)

    def find_target(self, enemies):
        self.target = None
        closest_enemy = None
        min_distance = float('inf')

        for enemy in enemies:
            distance = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
            if distance <= self.range:
                if self.tower_type == TowerType.ARCHER:
                    if closest_enemy is None or enemy.speed > closest_enemy.speed:
                        closest_enemy = enemy
                        min_distance = distance
                elif self.tower_type == TowerType.MAGIC:
                    if closest_enemy is None or enemy.path_position > closest_enemy.path_position:
                        closest_enemy = enemy
                        min_distance = distance
                elif self.tower_type == TowerType.CANNON:
                    if closest_enemy is None or enemy.health > closest_enemy.health:
                        closest_enemy = enemy
                        min_distance = distance

        self.target = closest_enemy

    def attack(self, enemies):
        if self.cooldown <= 0 and self.target:
            if self.tower_type == TowerType.ARCHER:
                self.target.take_damage(self.damage)
                self.cooldown = self.fire_rate
            elif self.tower_type == TowerType.MAGIC:
                for enemy in enemies:
                    distance = math.sqrt((self.target.x - enemy.x) ** 2 + (self.target.y - enemy.y) ** 2)
                    if distance <= self.aoe_radius:
                        enemy.take_damage(self.damage)
                self.cooldown = self.fire_rate
            elif self.tower_type == TowerType.CANNON:
                self.target.take_damage(self.damage)
                self.cooldown = self.fire_rate
        else:
            self.cooldown -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), GRID_SIZE // 2)

        font = pygame.font.SysFont(None, 20)
        level_text = font.render(str(self.level), True, BLACK)
        level_rect = level_text.get_rect(center=(self.x, self.y))
        surface.blit(level_text, level_rect)

        if game.selected_tower == self:
            pygame.draw.circle(surface, self.color, (self.x, self.y), self.range, 1)

        if self.target and self.cooldown <= 5:
            pygame.draw.line(surface, YELLOW, (self.x, self.y), (self.target.x, self.target.y), 2)


class Enemy:
    def __init__(self, enemy_type, wave):
        self.enemy_type = enemy_type
        self.path_position = 0
        self.x, self.y = path[0]
        self.progress = 0
        self.dead = False
        self.reached_end = False

        wave_multiplier = 1 + wave * 0.2

        if enemy_type == EnemyType.NORMAL:
            self.max_health = 50 * wave_multiplier
            self.speed = 0.02
            self.reward = 5
            self.color = GRAY
            self.size = GRID_SIZE // 2
        elif enemy_type == EnemyType.FAST:
            self.max_health = 30 * wave_multiplier
            self.speed = 0.04
            self.reward = 10
            self.color = BLUE
            self.size = GRID_SIZE // 3
        elif enemy_type == EnemyType.ARMORED:
            self.max_health = 100 * wave_multiplier
            self.speed = 0.01
            self.reward = 15
            self.color = BROWN
            self.size = GRID_SIZE // 2 + 5
        elif enemy_type == EnemyType.BOSS:
            self.max_health = 300 * wave_multiplier
            self.speed = 0.005
            self.reward = 50
            self.color = PURPLE
            self.size = GRID_SIZE // 2 + 10

        self.health = self.max_health

    def move(self):
        if self.path_position < len(path) - 1:
            start_x, start_y = path[self.path_position]
            end_x, end_y = path[self.path_position + 1]

            self.progress += self.speed

            if self.progress >= 1:
                self.path_position += 1
                self.progress = 0

                if self.path_position >= len(path) - 1:
                    self.reached_end = True
                    return

                start_x, start_y = path[self.path_position]
                end_x, end_y = path[self.path_position + 1]

            self.x = start_x + (end_x - start_x) * self.progress
            self.y = start_y + (end_y - start_y) * self.progress
        else:
            self.reached_end = True

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.dead = True

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

        health_bar_length = self.size * 2
        health_ratio = self.health / self.max_health
        health_bar_width = health_bar_length * health_ratio

        pygame.draw.rect(surface, RED, (int(self.x - health_bar_length // 2),
                                        int(self.y - self.size - 10),
                                        health_bar_length, 5))

        pygame.draw.rect(surface, GREEN, (int(self.x - health_bar_length // 2),
                                          int(self.y - self.size - 10),
                                          int(health_bar_width), 5))


class Game:
    def __init__(self):
        self.towers = []
        self.enemies = []
        self.lives = 10
        self.gold = 300
        self.wave = 0
        self.wave_in_progress = False
        self.enemies_spawned = 0
        self.enemies_to_spawn = 0
        self.spawn_delay = 0
        self.selected_tower = None
        self.selected_tower_type = None
        self.game_over = False
        self.wave_completed = False

    def start_wave(self):
        if not self.wave_in_progress and not self.game_over:
            self.wave += 1
            self.enemies_to_spawn = 5 + self.wave * 2
            self.enemies_spawned = 0
            self.wave_in_progress = True
            self.spawn_delay = 0
            self.wave_completed = False

    def spawn_enemy(self):
        if self.enemies_spawned < self.enemies_to_spawn:
            if self.spawn_delay <= 0:
                enemy_type_roll = random.random()

                if self.wave % 5 == 0 and random.random() < 0.2:
                    enemy_type = EnemyType.BOSS
                elif enemy_type_roll < 0.6:
                    enemy_type = EnemyType.NORMAL
                elif enemy_type_roll < 0.8:
                    enemy_type = EnemyType.FAST
                else:
                    enemy_type = EnemyType.ARMORED

                self.enemies.append(Enemy(enemy_type, self.wave))
                self.enemies_spawned += 1
                self.spawn_delay = 30
            else:
                self.spawn_delay -= 1

    def place_tower(self, x, y, tower_type):
        if x >= GAME_AREA_WIDTH:
            return False

        grid_x = (x // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
        grid_y = (y // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2

        for tower in self.towers:
            if tower.x == grid_x and tower.y == grid_y:
                return False

        for i in range(len(path) - 1):
            start_x, start_y = path[i]
            end_x, end_y = path[i + 1]

            if start_x == end_x:
                if abs(grid_x - start_x) < GRID_SIZE and min(start_y, end_y) - GRID_SIZE < grid_y < max(start_y,
                                                                                                        end_y) + GRID_SIZE:
                    return False
            else:
                if abs(grid_y - start_y) < GRID_SIZE and min(start_x, end_x) - GRID_SIZE < grid_x < max(start_x,
                                                                                                        end_x) + GRID_SIZE:
                    return False

        new_tower = Tower(grid_x, grid_y, tower_type)

        if self.gold >= new_tower.cost:
            self.gold -= new_tower.cost
            self.towers.append(new_tower)
            return True

        return False

    def upgrade_selected_tower(self):
        if self.selected_tower:
            if self.gold >= self.selected_tower.upgrade_cost:
                self.gold -= self.selected_tower.upgrade_cost
                self.selected_tower.upgrade()
                return True
        return False

    def sell_selected_tower(self):
        if self.selected_tower:
            refund = self.selected_tower.cost // 2
            for _ in range(1, self.selected_tower.level):
                refund += self.selected_tower.upgrade_cost // 2

            self.gold += refund
            self.towers.remove(self.selected_tower)
            self.selected_tower = None
            return True
        return False

    def select_tower(self, x, y):
        for tower in self.towers:
            distance = math.sqrt((tower.x - x) ** 2 + (tower.y - y) ** 2)
            if distance <= GRID_SIZE // 2:
                self.selected_tower = tower
                return True

        self.selected_tower = None
        return False

    def update(self):
        if self.game_over:
            return

        if self.wave_in_progress:
            self.spawn_enemy()

            if self.enemies_spawned >= self.enemies_to_spawn and not self.enemies:
                self.wave_in_progress = False
                self.wave_completed = True

        enemies_to_remove = []
        for enemy in self.enemies:
            enemy.move()

            if enemy.dead:
                self.gold += enemy.reward
                enemies_to_remove.append(enemy)
            elif enemy.reached_end:
                self.lives -= 1
                enemies_to_remove.append(enemy)
                if self.lives <= 0:
                    self.game_over = True

        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)

        for tower in self.towers:
            tower.find_target(self.enemies)
            tower.attack(self.enemies)

    def draw(self, surface):
        surface.fill(BLACK)

        for x in range(0, GAME_AREA_WIDTH, GRID_SIZE):
            for y in range(0, HEIGHT, GRID_SIZE):
                pygame.draw.rect(surface, LIGHT_GRAY, (x, y, GRID_SIZE, GRID_SIZE), 1)

        for i in range(len(path) - 1):
            start_x, start_y = path[i]
            end_x, end_y = path[i + 1]
            pygame.draw.line(surface, BROWN, (start_x, start_y), (end_x, end_y), GRID_SIZE // 2)

        pygame.draw.circle(surface, RED, path[-1], GRID_SIZE // 2)

        for tower in self.towers:
            tower.draw(surface)

        for enemy in self.enemies:
            enemy.draw(surface)

        self.draw_tower_menu(surface)

        self.draw_game_info(surface)

        if self.game_over:
            font = pygame.font.SysFont(None, 72)
            game_over_text = font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            surface.blit(game_over_text, game_over_rect)

            font = pygame.font.SysFont(None, 36)
            wave_text = font.render(f"Przetrwane fale: {self.wave}", True, WHITE)
            wave_rect = wave_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            surface.blit(wave_text, wave_rect)

        elif self.wave_completed:
            font = pygame.font.SysFont(None, 36)
            wave_text = font.render(f"Fala {self.wave} ukonczona!", True, GREEN)
            wave_rect = wave_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            surface.blit(wave_text, wave_rect)

            next_wave_text = font.render("Nacisnij SPACJE aby rozpoczac nastepna fale", True, WHITE)
            next_wave_rect = next_wave_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            surface.blit(next_wave_text, next_wave_rect)

    def draw_tower_menu(self, surface):
        pygame.draw.rect(surface, LIGHT_GRAY, (GAME_AREA_WIDTH, 0, TOWER_MENU_WIDTH, HEIGHT))
        pygame.draw.line(surface, BLACK, (GAME_AREA_WIDTH, 0), (GAME_AREA_WIDTH, HEIGHT), 2)

        font = pygame.font.SysFont(None, 28)
        title_text = font.render("MENU WIEZ", True, BLACK)
        title_rect = title_text.get_rect(center=(GAME_AREA_WIDTH + TOWER_MENU_WIDTH // 2, 30))
        surface.blit(title_text, title_rect)

        tower_options = [
            (TowerType.ARCHER, "Lucznik", GREEN, 50),
            (TowerType.MAGIC, "Mag", BLUE, 100),
            (TowerType.CANNON, "Dzialo", RED, 150)
        ]

        for i, (tower_type, name, color, cost) in enumerate(tower_options):
            button_y = 80 + i * 80
            button_rect = pygame.Rect(GAME_AREA_WIDTH + 20, button_y, TOWER_MENU_WIDTH - 40, 60)

            if self.selected_tower_type == tower_type:
                pygame.draw.rect(surface, YELLOW, button_rect, 3)
            else:
                pygame.draw.rect(surface, BLACK, button_rect, 1)

            pygame.draw.circle(surface, color, (GAME_AREA_WIDTH + 50, button_y + 30), 15)

            name_text = font.render(name, True, BLACK)
            name_rect = name_text.get_rect(midleft=(GAME_AREA_WIDTH + 75, button_y + 20))
            surface.blit(name_text, name_rect)

            cost_text = font.render(f"{cost} zlota", True, BLACK)
            cost_rect = cost_text.get_rect(midleft=(GAME_AREA_WIDTH + 75, button_y + 40))
            surface.blit(cost_text, cost_rect)

        if self.selected_tower:
            info_y = 330
            pygame.draw.line(surface, BLACK,
                             (GAME_AREA_WIDTH + 20, info_y),
                             (WIDTH - 20, info_y), 2)

            tower = self.selected_tower
            tower_types = {
                TowerType.ARCHER: "Lucznik",
                TowerType.MAGIC: "Mag",
                TowerType.CANNON: "Dzialo"
            }

            tower_info = [
                f"Typ: {tower_types[tower.tower_type]}",
                f"Poziom: {tower.level}",
                f"Obrazenia: {tower.damage}",
                f"Zasieg: {tower.range // GRID_SIZE} pol",
                f"Koszt ulepszenia: {tower.upgrade_cost}"
            ]

            for i, info in enumerate(tower_info):
                info_text = font.render(info, True, BLACK)
                info_rect = info_text.get_rect(topleft=(GAME_AREA_WIDTH + 30, info_y + 20 + i * 25))
                surface.blit(info_text, info_rect)

            upgrade_y = info_y + 160
            upgrade_rect = pygame.Rect(GAME_AREA_WIDTH + 20, upgrade_y, TOWER_MENU_WIDTH - 40, 40)
            pygame.draw.rect(surface, GREEN if self.gold >= tower.upgrade_cost else GRAY, upgrade_rect)

            upgrade_text = font.render("ULEPSZ", True, BLACK)
            upgrade_text_rect = upgrade_text.get_rect(center=(GAME_AREA_WIDTH + TOWER_MENU_WIDTH // 2, upgrade_y + 20))
            surface.blit(upgrade_text, upgrade_text_rect)

            sell_y = upgrade_y + 50
            sell_rect = pygame.Rect(GAME_AREA_WIDTH + 20, sell_y, TOWER_MENU_WIDTH - 40, 40)
            pygame.draw.rect(surface, RED, sell_rect)

            sell_text = font.render("SPRZEDAJ", True, BLACK)
            sell_text_rect = sell_text.get_rect(center=(GAME_AREA_WIDTH + TOWER_MENU_WIDTH // 2, sell_y + 20))
            surface.blit(sell_text, sell_text_rect)

    def draw_game_info(self, surface):
        font = pygame.font.SysFont(None, 30)

        lives_text = font.render(f"Zycia: {self.lives}", True, RED)
        surface.blit(lives_text, (10, 10))

        gold_text = font.render(f"Zloto: {self.gold}", True, YELLOW)
        surface.blit(gold_text, (10, 40))

        wave_text = font.render(f"Fala: {self.wave}", True, BROWN)
        surface.blit(wave_text, (10, 70))

        if not self.wave_in_progress and not self.game_over and not self.wave_completed:
            start_rect = pygame.Rect(10, HEIGHT - 50, 180, 40)
            pygame.draw.rect(surface, GREEN, start_rect)

            start_text = font.render("Rozpocznij fale", True, BLACK)
            start_text_rect = start_text.get_rect(center=(start_rect.centerx, start_rect.centery))
            surface.blit(start_text, start_text_rect)


def main():
    global game
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                if x > GAME_AREA_WIDTH:
                    for i, tower_type in enumerate([TowerType.ARCHER, TowerType.MAGIC, TowerType.CANNON]):
                        button_y = 80 + i * 80
                        button_rect = pygame.Rect(GAME_AREA_WIDTH + 20, button_y, TOWER_MENU_WIDTH - 40, 60)
                        if button_rect.collidepoint(x, y):
                            game.selected_tower_type = tower_type
                            game.selected_tower = None

                    if game.selected_tower:
                        upgrade_y = 330 + 160
                        upgrade_rect = pygame.Rect(GAME_AREA_WIDTH + 20, upgrade_y, TOWER_MENU_WIDTH - 40, 40)
                        if upgrade_rect.collidepoint(x, y):
                            game.upgrade_selected_tower()

                        sell_y = upgrade_y + 50
                        sell_rect = pygame.Rect(GAME_AREA_WIDTH + 20, sell_y, TOWER_MENU_WIDTH - 40, 40)
                        if sell_rect.collidepoint(x, y):
                            game.sell_selected_tower()

                else:
                    if not game.wave_in_progress and not game.game_over:
                        start_rect = pygame.Rect(10, HEIGHT - 50, 180, 40)
                        if start_rect.collidepoint(x, y):
                            game.start_wave()

                    elif game.selected_tower_type:
                        game.place_tower(x, y, game.selected_tower_type)
                    else:
                        game.select_tower(x, y)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game.wave_in_progress and not game.game_over:
                    game.start_wave()

        game.update()

        game.draw(screen)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()