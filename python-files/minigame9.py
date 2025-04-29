import pygame
import sys
import random
import math
import time

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Number Display Demo")

# Colors
BLACK = (30, 30, 30)
WHITE = (255, 255, 255)
RED = (160, 80, 80)
GREEN = (60, 180, 60)
BLUE = (60, 60, 100)
YELLOW = (185, 200, 90)
GRAY = (120, 120, 120)
HIGHLIGHT = (255, 220, 100)

# --- Number Display Setup ---
DISPLAY_COLS = 2
DISPLAY_ROWS = 2
DISPLAY_WIDTH = 80
DISPLAY_HEIGHT = 60
DISPLAY_MARGIN = 32
DISPLAY_TOP = 620  # Lowered to fit on screen

display_font = pygame.font.SysFont(None, 48)

def generate_display_row():
    return [f"{random.randint(1,9):02d}" for _ in range(DISPLAY_COLS)]

def get_display_rect(row, col):
    x = SCREEN_WIDTH//2 - (DISPLAY_WIDTH + DISPLAY_MARGIN) + \
        col * (DISPLAY_WIDTH + DISPLAY_MARGIN)
    y = DISPLAY_TOP + row * (DISPLAY_HEIGHT + DISPLAY_MARGIN)
    return pygame.Rect(x, y, DISPLAY_WIDTH, DISPLAY_HEIGHT)

def draw_number_displays(number_sets, selected_tiles, connection, drag_line):
    for row in range(DISPLAY_ROWS):
        for col in range(DISPLAY_COLS):
            rect = get_display_rect(row, col)
            if (row, col) in selected_tiles:
                pygame.draw.rect(screen, HIGHLIGHT, rect.inflate(8, 8), border_radius=12)
            pygame.draw.rect(screen, (50, 50, 50), rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, rect, 3, border_radius=8)
            num_text = display_font.render(number_sets[row][col], True, WHITE)
            text_rect = num_text.get_rect(center=rect.center)
            screen.blit(num_text, text_rect)
    if connection is not None:
        (r1, c1), (r2, c2) = connection
        rect1 = get_display_rect(r1, c1)
        rect2 = get_display_rect(r2, c2)
        pygame.draw.line(screen, YELLOW, rect1.center, rect2.center, 6)
    if drag_line is not None:
        start_pos, end_pos = drag_line
        pygame.draw.line(screen, YELLOW, start_pos, end_pos, 4)

# --- Enemy Ball Grid Setup ---
GRID_ROWS = 4
GRID_COLS = 4
BALL_RADIUS = 36
GRID_TOP = 70
GRID_LEFT = 140
GRID_CELL_SIZE = 110

ball_font = pygame.font.SysFont(None, 40)

def generate_enemy_grid():
    return [[random.randint(1,9) for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

def draw_arrow(surface, center, radius, direction_idx, color):
    angle = -math.pi/2 + direction_idx * (math.pi/4)
    tip = (center[0] + radius * math.cos(angle),
           center[1] + radius * math.sin(angle))
    left = (center[0] + radius * 0.5 * math.cos(angle + math.pi/1.5),
            center[1] + radius * 0.5 * math.sin(angle + math.pi/1.5))
    right = (center[0] + radius * 0.5 * math.cos(angle - math.pi/1.5),
             center[1] + radius * 0.5 * math.sin(angle - math.pi/1.5))
    pygame.draw.line(surface, color, center, tip, 8)
    pygame.draw.polygon(surface, color, [tip, left, right])

def draw_enemy_grid(enemy_grid, player_pos, arrow_dir):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            cx = GRID_LEFT + col * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            cy = GRID_TOP + row * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            if (row, col) == tuple(player_pos):
                pygame.draw.circle(screen, BLUE, (cx, cy), BALL_RADIUS + 4)
                pygame.draw.circle(screen, YELLOW, (cx, cy), BALL_RADIUS)
                draw_arrow(screen, (cx, cy), BALL_RADIUS-6, arrow_dir, BLACK)
            else:
                enemy_num = enemy_grid[row][col]
                if enemy_num > 0:
                    pygame.draw.circle(screen, GRAY, (cx, cy), BALL_RADIUS + 2)
                    pygame.draw.circle(screen, RED, (cx, cy), BALL_RADIUS)
                    num_text = ball_font.render(str(enemy_num), True, WHITE)
                    text_rect = num_text.get_rect(center=(cx, cy))
                    screen.blit(num_text, text_rect)

# --- D-pad Setup ---
DPAD_CENTER = (SCREEN_WIDTH - 650, SCREEN_HEIGHT - 20)
DPAD_RADIUS = 50

def draw_dpad(center, radius, cooldown_remaining):
    # Draw base
    pygame.draw.circle(screen, GRAY, center, radius)
    arrow_color = WHITE if cooldown_remaining == 0 else (100, 100, 100)
    arrow_size = 20
    # Up arrow
    up_pos = (center[0], center[1] - radius//2)
    pygame.draw.polygon(screen, arrow_color, [
        (up_pos[0] - arrow_size, up_pos[1] + arrow_size),
        (up_pos[0], up_pos[1] - arrow_size),
        (up_pos[0] + arrow_size, up_pos[1] + arrow_size)
    ])
    # Down arrow
    down_pos = (center[0], center[1] + radius//2)
    pygame.draw.polygon(screen, arrow_color, [
        (down_pos[0] - arrow_size, down_pos[1] - arrow_size),
        (down_pos[0], down_pos[1] + arrow_size),
        (down_pos[0] + arrow_size, down_pos[1] - arrow_size)
    ])
    # Left arrow
    left_pos = (center[0] - radius//2, center[1])
    pygame.draw.polygon(screen, arrow_color, [
        (left_pos[0] + arrow_size, left_pos[1] - arrow_size),
        (left_pos[0] - arrow_size, left_pos[1]),
        (left_pos[0] + arrow_size, left_pos[1] + arrow_size)
    ])
    # Right arrow
    right_pos = (center[0] + radius//2, center[1])
    pygame.draw.polygon(screen, arrow_color, [
        (right_pos[0] - arrow_size, right_pos[1] - arrow_size),
        (right_pos[0] + arrow_size, right_pos[1]),
        (right_pos[0] - arrow_size, right_pos[1] + arrow_size)
    ])
    # Cooldown overlay
    if cooldown_remaining > 0:
        overlay = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        overlay.fill((50, 50, 50, 180))
        screen.blit(overlay, (center[0]-radius, center[1]-radius))
        time_left = math.ceil(cooldown_remaining / 1000)
        text = display_font.render(str(time_left), True, WHITE)
        text_rect = text.get_rect(center=center)
        screen.blit(text, text_rect)

def clamp(val, minval, maxval):
    return max(minval, min(val, maxval))

def get_direction_index(from_tile, to_tile):
    dr = to_tile[0] - from_tile[0]
    dc = to_tile[1] - from_tile[1]
    dr = clamp(dr, -1, 1)
    dc = clamp(dc, -1, 1)
    dir_map = {
        (-1,  0): 0, (-1,  1): 1, (0,  1): 2, (1,  1): 3,
        (1,  0): 4, (1, -1): 5, (0, -1): 6, (-1, -1):7
    }
    return dir_map.get((dr, dc), 0)

def find_tile_under_mouse(mouse_pos):
    for row in range(DISPLAY_ROWS):
        for col in range(DISPLAY_COLS):
            rect = get_display_rect(row, col)
            if rect.collidepoint(mouse_pos):
                return (row, col)
    return None

def apply_gravity(enemy_grid, player_pos):
    """Make all enemy units fall down into empty spaces below them, but never into the player's position."""
    for col in range(GRID_COLS):
        for row in range(GRID_ROWS-2, -1, -1):  # Start from second-to-last row upwards
            if enemy_grid[row][col] != 0:
                curr_row = row
                while True:
                    next_row = curr_row + 1
                    # Stop if next row is off the grid
                    if next_row >= GRID_ROWS:
                        break
                    # Stop if next cell is occupied (by enemy or player)
                    if enemy_grid[next_row][col] != 0 or (next_row, col) == tuple(player_pos):
                        break
                    # Move unit down
                    enemy_grid[next_row][col] = enemy_grid[curr_row][col]
                    enemy_grid[curr_row][col] = 0
                    curr_row = next_row

def process_gravity_and_spawn(enemy_grid, player_pos):
    apply_gravity(enemy_grid, player_pos)
    # Generate new enemies in top row if empty
    for col in range(GRID_COLS):
        if enemy_grid[0][col] == 0:
            enemy_grid[0][col] = random.randint(1, 9)
    apply_gravity(enemy_grid, player_pos)

def main():
    running = True
    clock = pygame.time.Clock()
    FPS = 60

    # Number display setup
    number_sets = [generate_display_row(), generate_display_row()]
    selected_tiles = []
    connection = None
    product = None
    arrow_dir = 0
    processed_product = False
    score = 0

    # Drag state
    dragging = False
    drag_start_tile = None
    drag_start_pos = None
    drag_line = None

    # Enemy ball grid setup
    enemy_grid = generate_enemy_grid()
    player_pos = [random.randint(0, GRID_ROWS-1), random.randint(0, GRID_COLS-1)]

    # D-pad cooldown
    cooldown_duration = 3000  # 3 seconds
    last_move_time = 0
    
    # Game duration (35 seconds)
    game_duration = 35000  # 35 seconds in milliseconds
    start_time = pygame.time.get_ticks()

    while running:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time
        cooldown_remaining = max(0, cooldown_duration - (current_time - last_move_time))
        
        # Check if game time has expired
        if elapsed_time >= game_duration:
            running = False
            # Show final score for a few seconds before quitting
            screen.fill(BLACK)
            game_over_text = display_font.render("Game Over!", True, WHITE)
            score_text = display_font.render(f"Final Score: {score}", True, GREEN)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
            pygame.display.flip()
            pygame.time.delay(3000)  # Show for 3 seconds
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Mouse drag for number tiles
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                tile = find_tile_under_mouse(mouse_pos)
                if tile is not None:
                    dragging = True
                    drag_start_tile = tile
                    drag_start_pos = get_display_rect(*tile).center
                    drag_line = (drag_start_pos, mouse_pos)
                    selected_tiles = [tile]
                    connection = None
                    product = None
                    processed_product = False

            if event.type == pygame.MOUSEMOTION:
                if dragging and drag_start_pos is not None:
                    mouse_pos = pygame.mouse.get_pos()
                    drag_line = (drag_start_pos, mouse_pos)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging and drag_start_tile is not None:
                    mouse_pos = pygame.mouse.get_pos()
                    end_tile = find_tile_under_mouse(mouse_pos)
                    if end_tile is not None and end_tile != drag_start_tile:
                        selected_tiles = [drag_start_tile, end_tile]
                        connection = (drag_start_tile, end_tile)
                        n1 = int(number_sets[drag_start_tile[0]][drag_start_tile[1]])
                        n2 = int(number_sets[end_tile[0]][end_tile[1]])
                        product = n1 * n2
                        arrow_dir = get_direction_index(drag_start_tile, end_tile)
                        processed_product = False
                    else:
                        selected_tiles = []
                        connection = None
                        product = None
                        processed_product = False
                    dragging = False
                    drag_start_tile = None
                    drag_start_pos = None
                    drag_line = None

            # D-pad movement
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                dx = mouse_pos[0] - DPAD_CENTER[0]
                dy = mouse_pos[1] - DPAD_CENTER[1]
                distance_sq = dx**2 + dy**2

                if distance_sq <= DPAD_RADIUS**2:
                    if abs(dx) > abs(dy):
                        direction = 'right' if dx > 0 else 'left'
                    else:
                        direction = 'down' if dy > 0 else 'up'

                    if cooldown_remaining == 0:
                        new_row, new_col = player_pos
                        if direction == 'up':
                            new_row -= 1
                        elif direction == 'down':
                            new_row += 1
                        elif direction == 'left':
                            new_col -= 1
                        elif direction == 'right':
                            new_col += 1

                        if 0 <= new_row < GRID_ROWS and 0 <= new_col < GRID_COLS:
                            if enemy_grid[new_row][new_col] > 0:
                                score += 2
                                enemy_grid[new_row][new_col] = 0
                            player_pos = [new_row, new_col]
                            process_gravity_and_spawn(enemy_grid, player_pos)
                            last_move_time = current_time

        # Process product
        if product is not None and not processed_product:
            product_digits = list(str(product))
            direction_map = [
                (-1, 0), (-1, 1), (0, 1), (1, 1),
                (1, 0), (1, -1), (0, -1), (-1, -1)
            ]
            dr, dc = direction_map[arrow_dir]
            points = 0
            matched_cells = []
            for i in range(len(product_digits)):
                step = i + 1
                new_row = player_pos[0] + dr * step
                new_col = player_pos[1] + dc * step
                if 0 <= new_row < GRID_ROWS and 0 <= new_col < GRID_COLS:
                    enemy_num = enemy_grid[new_row][new_col]
                    if str(enemy_num) == product_digits[i]:
                        points += 10
                        matched_cells.append((new_row, new_col))
                    else:
                        break
                else:
                    break
            score += points
            # Destroy all matched cells in the chain
            for r, c in matched_cells:
                enemy_grid[r][c] = 0
            if matched_cells:
                process_gravity_and_spawn(enemy_grid, player_pos)
            processed_product = True

        # Drawing
        screen.fill(BLACK)
        draw_enemy_grid(enemy_grid, player_pos, arrow_dir)
        draw_number_displays(number_sets, selected_tiles, connection, drag_line)
        draw_dpad(DPAD_CENTER, DPAD_RADIUS, cooldown_remaining)

        # Show product and score
        if product is not None:
            prod_text = display_font.render(f"Product: {product}", True, GREEN)
            screen.blit(prod_text, (SCREEN_WIDTH//2 - prod_text.get_width()//2, DISPLAY_TOP + DISPLAY_ROWS*(DISPLAY_HEIGHT+DISPLAY_MARGIN) + 20))
        score_text = display_font.render(f"Score: {score}", True, GREEN)
        screen.blit(score_text, (SCREEN_WIDTH - 400, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()