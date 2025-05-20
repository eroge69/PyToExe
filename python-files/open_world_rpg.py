import pygame
import sys
import random
import math

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
WORLD_SIZE = 100
PLAYER_SPEED = 2
PICKUP_RADIUS = 30
PICKUP_TIME_FRAMES = 60  # frames to hold ENTER (1 sec at 60 FPS)

# Colors
GRASS_GREEN = (80, 180, 80)
TREE_TRUNK = (99, 60, 30)
PLAYER_COLOR = (220, 40, 40)
INV_BG = (30, 30, 30)
INV_SLOT = (60, 60, 60)
INV_SLOT_BORDER = (100, 100, 100)
STICK_COLOR = (139, 69, 19)  # brown for sticks
ROCK_COLOR = (120, 120, 120)
ROCK_HIGHLIGHT = (160, 160, 160)
LOADING_BAR_BG = (50, 50, 50)
LOADING_BAR_FILL = (50, 220, 50)
HIGHLIGHT_COLOR = (200, 200, 50)

# Leaf shades
LEAF_COLORS = [
    (34, 139, 34),
    (50, 160, 50),
    (70, 180, 70),
    (40, 120, 40),
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Open World - Inventory & Crafting")

clock = pygame.time.Clock()

grass_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
grass_tile.fill(GRASS_GREEN)

player_x = WORLD_SIZE * TILE_SIZE // 2
player_y = WORLD_SIZE * TILE_SIZE // 2

def generate_tree_surface_and_colliders():
    surface = pygame.Surface((64, 88), pygame.SRCALPHA)
    for i in range(0, 64, 8):
        for j in range(0, 64, 8):
            color = random.choice(LEAF_COLORS)
            pygame.draw.rect(surface, color, (i, j, 8, 8))
    trunk_rect = pygame.Rect(26, 64, 12, 24)
    pygame.draw.rect(surface, TREE_TRUNK, trunk_rect)
    canopy_rect = pygame.Rect(0, 0, 64, 64)
    return surface, trunk_rect, canopy_rect

tree_data = []
for _ in range(300):
    tx = random.randint(0, WORLD_SIZE * TILE_SIZE)
    ty = random.randint(0, WORLD_SIZE * TILE_SIZE)
    surface, trunk_rect, canopy_rect = generate_tree_surface_and_colliders()
    world_trunk_rect = pygame.Rect(tx + trunk_rect.x, ty + trunk_rect.y, trunk_rect.width, trunk_rect.height)
    world_canopy_rect = pygame.Rect(tx + canopy_rect.x, ty + canopy_rect.y, canopy_rect.width, canopy_rect.height)
    tree_data.append({
        'x': tx,
        'y': ty,
        'surface': surface,
        'trunk_collider': world_trunk_rect,
        'canopy_collider': world_canopy_rect,
    })

# Generate sticks positions randomly
stick_count = 100
sticks = []
for _ in range(stick_count):
    sx = random.randint(0, WORLD_SIZE * TILE_SIZE)
    sy = random.randint(0, WORLD_SIZE * TILE_SIZE)
    sticks.append([sx, sy])

# Generate rocks positions randomly
rock_count = 80
rocks = []
for _ in range(rock_count):
    rx = random.randint(0, WORLD_SIZE * TILE_SIZE)
    ry = random.randint(0, WORLD_SIZE * TILE_SIZE)
    rocks.append([rx, ry])

inventory_open = False
inventory_slots = 20
slots_per_row = 5
slot_size = 40
inventory = [None] * inventory_slots  # None or dict {"name":..., "count":...}

# Crafting grid: 2x2 grid, 4 slots
crafting_grid = [None] * 4
crafting_result = None

font = pygame.font.SysFont("Arial", 18)

def draw_inventory_stick_icon(surface, x, y):
    pygame.draw.rect(surface, STICK_COLOR, (x, y + 4, 12, 4))
    pygame.draw.rect(surface, (160, 82, 45), (x + 2, y + 5, 2, 2))
    pygame.draw.rect(surface, (110, 55, 25), (x + 7, y + 5, 3, 2))

def draw_inventory_rock_icon(surface, x, y):
    pygame.draw.rect(surface, ROCK_COLOR, (x, y + 2, 12, 6))
    pygame.draw.rect(surface, ROCK_HIGHLIGHT, (x + 2, y + 4, 3, 2))
    pygame.draw.rect(surface, ROCK_HIGHLIGHT, (x + 7, y + 3, 2, 3))

def draw_inventory_axe_icon(surface, x, y):
    # Simple axe icon: brown handle + grey blade
    pygame.draw.rect(surface, (139, 69, 19), (x + 5, y + 8, 4, 10))  # handle
    pygame.draw.polygon(surface, (150, 150, 150), [(x + 4, y + 8), (x + 12, y + 6), (x + 12, y + 12)])  # blade

def add_item_to_inventory(name):
    for slot in range(inventory_slots):
        item = inventory[slot]
        if item and item["name"] == name and item["count"] < 32:
            item["count"] += 1
            return True
    for slot in range(inventory_slots):
        if inventory[slot] is None:
            inventory[slot] = {"name": name, "count": 1}
            return True
    return False  # inventory full

def remove_item_from_inventory(name, count):
    """Remove count items of given name from inventory, return True if success."""
    total_found = 0
    for item in inventory:
        if item and item["name"] == name:
            total_found += item["count"]
    if total_found < count:
        return False  # not enough items

    to_remove = count
    for slot in range(inventory_slots):
        item = inventory[slot]
        if item and item["name"] == name:
            if item["count"] > to_remove:
                item["count"] -= to_remove
                to_remove = 0
                break
            else:
                to_remove -= item["count"]
                inventory[slot] = None
            if to_remove <= 0:
                break
    return True

def check_crafting_recipe(grid):
    """
    Check crafting grid for recipes.
    grid: list of 4 slots (None or dict with "name","count")
    Returns crafted item name or None.
    
    Recipe example:
    2 sticks + 2 rocks anywhere = Axe
    """
    # Count items in grid
    counts = {"Stick": 0, "Rock": 0}
    for slot in grid:
        if slot:
            name = slot["name"]
            if name in counts:
                counts[name] += 1
            else:
                return None  # unknown item = no recipe

    # Recipe: Exactly 2 sticks and 2 rocks (total 4 items)
    if counts["Stick"] == 2 and counts["Rock"] == 2:
        return "Axe"
    return None

# Variables to track pickup progress
pickup_timer = 0
pickup_target = None  # ("Stick", index) or ("Rock", index)

# Variables for dragging item in inventory/crafting
dragging_item = None  # dict with "name", "count"
dragging_from = None  # ("inv", index) or ("craft", index)

running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                inventory_open = not inventory_open
                pickup_timer = 0
                pickup_target = None
                dragging_item = None
                dragging_from = None

        if event.type == pygame.MOUSEBUTTONDOWN and inventory_open:
            mx, my = pygame.mouse.get_pos()

            # Positions of main inventory slots
            inv_panel_width = slots_per_row * slot_size + 20
            inv_panel_height = ((inventory_slots + slots_per_row - 1) // slots_per_row) * slot_size + 40 + 100  # extra for crafting
            panel_x = WIDTH // 2 - inv_panel_width // 2
            panel_y = HEIGHT // 2 - inv_panel_height // 2

            # Check main inventory slots
            found_slot = False
            for i in range(inventory_slots):
                row = i // slots_per_row
                col = i % slots_per_row
                slot_x = panel_x + 10 + col * slot_size
                slot_y = panel_y + 10 + row * slot_size
                rect = pygame.Rect(slot_x, slot_y, slot_size - 4, slot_size - 4)
                if rect.collidepoint(mx, my):
                    found_slot = True
                    if event.button == 1:  # Left click (pick up whole stack or place)
                        if dragging_item is None and inventory[i] is not None:
                            # Pick up whole stack
                            dragging_item = inventory[i]
                            dragging_from = ("inv", i)
                            inventory[i] = None
                        elif dragging_item is not None:
                            # Place or swap items
                            if inventory[i] is None:
                                inventory[i] = dragging_item
                                dragging_item = None
                                dragging_from = None
                            else:
                                # Swap
                                inventory[i], dragging_item = dragging_item, inventory[i]
                                dragging_from = ("inv", i)
                    elif event.button == 3:  # Right click (pick up one item)
                        if inventory[i] is not None:
                            if dragging_item is None:
                                # Pick up one item from this slot
                                dragging_item = {"name": inventory[i]["name"], "count": 1}
                                dragging_from = ("inv", i)
                                inventory[i]["count"] -= 1
                                if inventory[i]["count"] <= 0:
                                    inventory[i] = None
                            else:
                                # If dragging same item, add one to dragging if possible (max stack 32)
                                if dragging_item["name"] == inventory[i]["name"] and dragging_item["count"] < 32:
                                    inventory[i]["count"] -= 1
                                    dragging_item["count"] += 1
                                    if inventory[i]["count"] <= 0:
                                        inventory[i] = None
                    break

            # Check crafting grid slots (2x2 grid under inventory)
            # Crafting grid located below inventory slots, 4 slots in 2x2
            craft_x = panel_x + 10
            craft_y = panel_y + ((inventory_slots + slots_per_row - 1) // slots_per_row) * slot_size + 20
            craft_slot_size = slot_size
            if not found_slot:
                for i in range(4):
                    row = i // 2
                    col = i % 2
                    slot_x = craft_x + col * craft_slot_size
                    slot_y = craft_y + row * craft_slot_size
                    rect = pygame.Rect(slot_x, slot_y, craft_slot_size - 4, craft_slot_size - 4)
                    if rect.collidepoint(mx, my):
                        if event.button == 1:  # Left click on crafting grid
                            if dragging_item is None and crafting_grid[i] is not None:
                                dragging_item = crafting_grid[i]
                                dragging_from = ("craft", i)
                                crafting_grid[i] = None
                            elif dragging_item is not None:
                                if crafting_grid[i] is None:
                                    crafting_grid[i] = dragging_item
                                    dragging_item = None
                                    dragging_from = None
                                else:
                                    crafting_grid[i], dragging_item = dragging_item, crafting_grid[i]
                                    dragging_from = ("craft", i)
                        elif event.button == 3:  # Right click on crafting grid
                            if crafting_grid[i] is not None:
                                if dragging_item is None:
                                    dragging_item = {"name": crafting_grid[i]["name"], "count": 1}
                                    dragging_from = ("craft", i)
                                    crafting_grid[i]["count"] -= 1
                                    if crafting_grid[i]["count"] <= 0:
                                        crafting_grid[i] = None
                                else:
                                    if dragging_item["name"] == crafting_grid[i]["name"] and dragging_item["count"] < 32:
                                        crafting_grid[i]["count"] -= 1
                                        dragging_item["count"] += 1
                                        if crafting_grid[i]["count"] <= 0:
                                            crafting_grid[i] = None
                        break

        if event.type == pygame.MOUSEBUTTONUP and inventory_open:
            # Drop dragged item into inventory or crafting grid if mouse over a slot
            if dragging_item is not None:
                mx, my = pygame.mouse.get_pos()
                inv_panel_width = slots_per_row * slot_size + 20
                inv_panel_height = ((inventory_slots + slots_per_row - 1) // slots_per_row) * slot_size + 40 + 100
                panel_x = WIDTH // 2 - inv_panel_width // 2
                panel_y = HEIGHT // 2 - inv_panel_height // 2

                placed = False

                # Check main inventory slots
                for i in range(inventory_slots):
                    row = i // slots_per_row
                    col = i % slots_per_row
                    slot_x = panel_x + 10 + col * slot_size
                    slot_y = panel_y + 10 + row * slot_size
                    rect = pygame.Rect(slot_x, slot_y, slot_size - 4, slot_size - 4)
                    if rect.collidepoint(mx, my):
                        # Try to place items in slot
                        if inventory[i] is None:
                            inventory[i] = dragging_item
                            dragging_item = None
                            dragging_from = None
                            placed = True
                            break
                        else:
                            # If same type, stack up to 32
                            if inventory[i]["name"] == dragging_item["name"]:
                                can_add = 32 - inventory[i]["count"]
                                to_add = min(can_add, dragging_item["count"])
                                if to_add > 0:
                                    inventory[i]["count"] += to_add
                                    dragging_item["count"] -= to_add
                                    if dragging_item["count"] <= 0:
                                        dragging_item = None
                                        dragging_from = None
                                        placed = True
                                    break
                            # Otherwise swap
                            else:
                                inventory[i], dragging_item = dragging_item, inventory[i]
                                dragging_from = ("inv", i)
                                placed = True
                                break

                # Check crafting grid slots if not placed
                if not placed:
                    craft_x = panel_x + 10
                    craft_y = panel_y + ((inventory_slots + slots_per_row - 1) // slots_per_row) * slot_size + 20
                    craft_slot_size = slot_size
                    for i in range(4):
                        row = i // 2
                        col = i % 2
                        slot_x = craft_x + col * craft_slot_size
                        slot_y = craft_y + row * craft_slot_size
                        rect = pygame.Rect(slot_x, slot_y, craft_slot_size - 4, craft_slot_size - 4)
                        if rect.collidepoint(mx, my):
                            if crafting_grid[i] is None:
                                crafting_grid[i] = dragging_item
                                dragging_item = None
                                dragging_from = None
                                placed = True
                                break
                            else:
                                if crafting_grid[i]["name"] == dragging_item["name"]:
                                    can_add = 32 - crafting_grid[i]["count"]
                                    to_add = min(can_add, dragging_item["count"])
                                    if to_add > 0:
                                        crafting_grid[i]["count"] += to_add
                                        dragging_item["count"] -= to_add
                                        if dragging_item["count"] <= 0:
                                            dragging_item = None
                                            dragging_from = None
                                        placed = True
                                    break
                                else:
                                    crafting_grid[i], dragging_item = dragging_item, crafting_grid[i]
                                    dragging_from = ("craft", i)
                                    placed = True
                                    break

                # If not placed, return dragged item to original slot
                if not placed:
                    if dragging_from is not None:
                        loc, idx = dragging_from
                        if loc == "inv":
                            if inventory[idx] is None:
                                inventory[idx] = dragging_item
                            else:
                                # Try stack if same type
                                if inventory[idx]["name"] == dragging_item["name"]:
                                    total = inventory[idx]["count"] + dragging_item["count"]
                                    if total <= 32:
                                        inventory[idx]["count"] = total
                                    else:
                                        inventory[idx]["count"] = 32
                                        dragging_item["count"] = total - 32
                                        # Drop remaining on ground?
                                        # For now discard extra
                                else:
                                    # Swap forcibly
                                    inventory[idx], dragging_item = dragging_item, inventory[idx]
                        elif loc == "craft":
                            if crafting_grid[idx] is None:
                                crafting_grid[idx] = dragging_item
                            else:
                                if crafting_grid[idx]["name"] == dragging_item["name"]:
                                    total = crafting_grid[idx]["count"] + dragging_item["count"]
                                    if total <= 32:
                                        crafting_grid[idx]["count"] = total
                                    else:
                                        crafting_grid[idx]["count"] = 32
                                        dragging_item["count"] = total - 32
                                        # Discard extra
                                else:
                                    crafting_grid[idx], dragging_item = dragging_item, crafting_grid[idx]
                    dragging_item = None
                    dragging_from = None

    # Movement keys for player
    keys = pygame.key.get_pressed()
    dx = 0
    dy = 0
    if keys[pygame.K_w]:
        dy -= PLAYER_SPEED
    if keys[pygame.K_s]:
        dy += PLAYER_SPEED
    if keys[pygame.K_a]:
        dx -= PLAYER_SPEED
    if keys[pygame.K_d]:
        dx += PLAYER_SPEED

    # Collision check with tree trunks
    new_x = player_x + dx
    new_y = player_y + dy
    player_rect = pygame.Rect(new_x, new_y, 20, 30)
    collision = False
    for tree in tree_data:
        if tree['trunk_collider'].colliderect(player_rect):
            collision = True
            break
    if not collision:
        player_x = new_x
        player_y = new_y

    # Pickup sticks
    if keys[pygame.K_RETURN]:
        if pickup_target is None:
            # Find stick or rock in pickup radius
            found = False
            for i, (sx, sy) in enumerate(sticks):
                dist = math.hypot(player_x - sx, player_y - sy)
                if dist < PICKUP_RADIUS:
                    pickup_target = ("Stick", i)
                    pickup_timer = 1
                    found = True
                    break
            if not found:
                for i, (rx, ry) in enumerate(rocks):
                    dist = math.hypot(player_x - rx, player_y - ry)
                    if dist < PICKUP_RADIUS:
                        pickup_target = ("Rock", i)
                        pickup_timer = 1
                        found = True
                        break
        else:
            pickup_timer += 1
            if pickup_timer > PICKUP_TIME_FRAMES:
                # Pick up item
                typ, idx = pickup_target
                if typ == "Stick":
                    if add_item_to_inventory("Stick"):
                        sticks.pop(idx)
                elif typ == "Rock":
                    if add_item_to_inventory("Rock"):
                        rocks.pop(idx)
                pickup_timer = 0
                pickup_target = None
    else:
        pickup_timer = 0
        pickup_target = None

    # Check crafting recipe
    crafting_result = check_crafting_recipe(crafting_grid)

    # Draw background world centered on player
    screen.fill((100, 150, 200))  # sky blue

    # Draw grass tiles around player
    start_tile_x = (player_x // TILE_SIZE) - (WIDTH // TILE_SIZE) // 2 - 2
    start_tile_y = (player_y // TILE_SIZE) - (HEIGHT // TILE_SIZE) // 2 - 2
    for i in range((WIDTH // TILE_SIZE) + 4):
        for j in range((HEIGHT // TILE_SIZE) + 4):
            gx = (start_tile_x + i) * TILE_SIZE
            gy = (start_tile_y + j) * TILE_SIZE
            screen_x = gx - player_x + WIDTH // 2
            screen_y = gy - player_y + HEIGHT // 2
            screen.blit(grass_tile, (screen_x, screen_y))

    # Draw sticks and rocks
    for sx, sy in sticks:
        screen_x = sx - player_x + WIDTH // 2
        screen_y = sy - player_y + HEIGHT // 2
        pygame.draw.rect(screen, STICK_COLOR, (screen_x, screen_y, 10, 4))
    for rx, ry in rocks:
        screen_x = rx - player_x + WIDTH // 2
        screen_y = ry - player_y + HEIGHT // 2
        pygame.draw.rect(screen, ROCK_COLOR, (screen_x, screen_y, 10, 6))

    # Draw trees
    for tree in tree_data:
        screen_x = tree['x'] - player_x + WIDTH // 2
        screen_y = tree['y'] - player_y + HEIGHT // 2
        # Draw canopy
        screen.blit(tree['surface'], (screen_x, screen_y))

    # Draw player
    player_rect_draw = pygame.Rect(WIDTH // 2 - 10, HEIGHT // 2 - 15, 20, 30)
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect_draw)

    # Draw inventory if open
    if inventory_open:
        inv_panel_width = slots_per_row * slot_size + 20
        inv_panel_height = ((inventory_slots + slots_per_row - 1) // slots_per_row) * slot_size + 40 + 100
        panel_x = WIDTH // 2 - inv_panel_width // 2
        panel_y = HEIGHT // 2 - inv_panel_height // 2
        pygame.draw.rect(screen, INV_BG, (panel_x, panel_y, inv_panel_width, inv_panel_height))

        # Draw inventory slots
        for i in range(inventory_slots):
            row = i // slots_per_row
            col = i % slots_per_row
            slot_x = panel_x + 10 + col * slot_size
            slot_y = panel_y + 10 + row * slot_size
            pygame.draw.rect(screen, INV_SLOT, (slot_x, slot_y, slot_size - 4, slot_size - 4))
            pygame.draw.rect(screen, INV_SLOT_BORDER, (slot_x, slot_y, slot_size - 4, slot_size - 4), 2)
            item = inventory[i]
            if item:
                # Draw item icon
                if item["name"] == "Stick":
                    draw_inventory_stick_icon(screen, slot_x + 8, slot_y + 8)
                elif item["name"] == "Rock":
                    draw_inventory_rock_icon(screen, slot_x + 8, slot_y + 8)
                elif item["name"] == "Axe":
                    draw_inventory_axe_icon(screen, slot_x + 8, slot_y + 8)
                # Draw count text
                count_text = font.render(str(item["count"]), True, (255, 255, 255))
                screen.blit(count_text, (slot_x + slot_size - 20, slot_y + slot_size - 22))

        # Draw crafting grid background and slots
        craft_x = panel_x + 10
        craft_y = panel_y + ((inventory_slots + slots_per_row - 1) // slots_per_row) * slot_size + 20
        pygame.draw.rect(screen, (50, 50, 50), (craft_x - 4, craft_y - 4, slot_size * 2 + 8, slot_size * 2 + 8))
        for i in range(4):
            row = i // 2
            col = i % 2
            slot_x = craft_x + col * slot_size
            slot_y = craft_y + row * slot_size
            pygame.draw.rect(screen, INV_SLOT, (slot_x, slot_y, slot_size - 4, slot_size - 4))
            pygame.draw.rect(screen, INV_SLOT_BORDER, (slot_x, slot_y, slot_size - 4, slot_size - 4), 2)
            item = crafting_grid[i]
            if item:
                if item["name"] == "Stick":
                    draw_inventory_stick_icon(screen, slot_x + 8, slot_y + 8)
                elif item["name"] == "Rock":
                    draw_inventory_rock_icon(screen, slot_x + 8, slot_y + 8)
                elif item["name"] == "Axe":
                    draw_inventory_axe_icon(screen, slot_x + 8, slot_y + 8)
                count_text = font.render(str(item["count"]), True, (255, 255, 255))
                screen.blit(count_text, (slot_x + slot_size - 20, slot_y + slot_size - 22))

        # Draw crafting result slot
        result_x = craft_x + slot_size * 2 + 20
        result_y = craft_y + slot_size // 2
        pygame.draw.rect(screen, (80, 80, 80), (result_x, result_y, slot_size, slot_size))
        pygame.draw.rect(screen, (180, 180, 180), (result_x, result_y, slot_size, slot_size), 2)
        if crafting_result:
            if crafting_result == "Axe":
                draw_inventory_axe_icon(screen, result_x + 8, result_y + 8)

        # Draw dragging item following mouse
        if dragging_item:
            mx, my = pygame.mouse.get_pos()
            icon_x = mx - slot_size // 2
            icon_y = my - slot_size // 2
            if dragging_item["name"] == "Stick":
                draw_inventory_stick_icon(screen, icon_x + 8, icon_y + 8)
            elif dragging_item["name"] == "Rock":
                draw_inventory_rock_icon(screen, icon_x + 8, icon_y + 8)
            elif dragging_item["name"] == "Axe":
                draw_inventory_axe_icon(screen, icon_x + 8, icon_y + 8)
            count_text = font.render(str(dragging_item["count"]), True, (255, 255, 255))
            screen.blit(count_text, (icon_x + slot_size - 20, icon_y + slot_size - 22))

    # Draw pickup loading bar if picking up stick or rock
    if pickup_target is not None and pickup_timer > 0:
        bar_width = 100
        bar_height = 10
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = HEIGHT // 2 + 50
        pygame.draw.rect(screen, LOADING_BAR_BG, (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * (pickup_timer / PICKUP_TIME_FRAMES))
        pygame.draw.rect(screen, LOADING_BAR_FILL, (bar_x, bar_y, fill_width, bar_height))

    pygame.display.flip()

pygame.quit()
sys.exit()
