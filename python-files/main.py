import pygame
import math
import sys

pygame.init()
WIDTH, HEIGHT = 900, 600
CENTER = (600, 300)
RADIUS = 200

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
GRAY = (180, 180, 180)
RED = (255, 80, 80)
BLUE = (80, 140, 255)
GREEN = (100, 255, 100)
PURPLE = (180, 100, 255)
ORANGE = (255, 180, 80)

font = pygame.font.SysFont("Segoe UI", 18)
big_font = pygame.font.SysFont("Segoe UI", 22, bold=True)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Единичная окружность — шкала и стиль")

angle_rad = 0
input_active = None
input_fields = {
    "deg": {"rect": pygame.Rect(130, 30, 120, 30), "text": "", "label": "Угол (°):", "dirty": False},
    "rad": {"rect": pygame.Rect(130, 75, 120, 30), "text": "", "label": "Радианы:", "dirty": False},
}

def draw_text(text, pos, color=BLACK, size=font):
    label = size.render(text, True, color)
    screen.blit(label, pos)

def draw_inputs():
    for key, field in input_fields.items():
        draw_text(field["label"], (20, field["rect"].y + 5), color=BLACK)
        pygame.draw.rect(screen, WHITE, field["rect"], border_radius=5)
        pygame.draw.rect(screen, BLUE if input_active == key else GRAY, field["rect"], 2, border_radius=5)
        draw_text(field["text"], (field["rect"].x + 8, field["rect"].y + 6), color=BLACK)

def draw_values(angle_rad):
    sin_val = math.sin(angle_rad)
    cos_val = math.cos(angle_rad)
    tan_val = None if abs(cos_val) < 1e-6 else math.tan(angle_rad)
    cot_val = None if abs(sin_val) < 1e-6 else 1 / math.tan(angle_rad)

    values = [
        f"sin(α): {sin_val:.4f}",
        f"cos(α): {cos_val:.4f}",
        f"tan(α): {'∞' if tan_val is None else f'{tan_val:.4f}'}",
        f"cot(α): {'∞' if cot_val is None else f'{cot_val:.4f}'}"
    ]
    for i, line in enumerate(values):
        draw_text(line, (20, 130 + i * 30), color=BLACK)

def draw_angle_scale():
    for deg in range(0, 360, 30):
        rad = math.radians(deg)
        x = CENTER[0] + RADIUS * math.cos(rad)
        y = CENTER[1] - RADIUS * math.sin(rad)
        lx = CENTER[0] + (RADIUS + 15) * math.cos(rad)
        ly = CENTER[1] - (RADIUS + 15) * math.sin(rad)
        pygame.draw.line(screen, DARK_GRAY, (x, y), (lx, ly), 2)
        label = f"{deg}°"
        text = font.render(label, True, DARK_GRAY)
        text_rect = text.get_rect(center=(lx, ly))
        screen.blit(text, text_rect)

def draw_circle(angle_rad):
    # Axial lines at 0°, 90°, 180°, 270°
    pygame.draw.line(screen, GRAY, (CENTER[0] - RADIUS, CENTER[1]), (CENTER[0] + RADIUS, CENTER[1]), 1)
    pygame.draw.line(screen, GRAY, (CENTER[0], CENTER[1] - RADIUS), (CENTER[0], CENTER[1] + RADIUS), 1)
    pygame.draw.circle(screen, BLACK, CENTER, RADIUS, 2)
    # Axis lines already drawn above
    draw_angle_scale()

    sin_val = math.sin(angle_rad)
    cos_val = math.cos(angle_rad)
    x = CENTER[0] + RADIUS * cos_val
    y = CENTER[1] - RADIUS * sin_val

    pygame.draw.line(screen, RED, CENTER, (x, y), 3)
    pygame.draw.circle(screen, RED, (int(x), int(y)), 6)
    angle_deg = math.degrees(angle_rad) % 360
    draw_text(f"α = {angle_deg:.1f}°", ((CENTER[0] + x) / 2 + 10, (CENTER[1] + y) / 2), RED, big_font)

    pygame.draw.line(screen, BLUE, (CENTER[0], y), (x, y), 2)
    pygame.draw.line(screen, BLUE, (CENTER[0], y), (CENTER[0], CENTER[1]), 2)
    draw_text(f"sin={sin_val:.4f}", (CENTER[0] + 5, (y + CENTER[1]) / 2), BLUE)

    pygame.draw.line(screen, GREEN, (x, CENTER[1]), (CENTER[0], CENTER[1]), 2)
    pygame.draw.line(screen, GREEN, (x, y), (x, CENTER[1]), 2)
    draw_text(f"cos={cos_val:.4f}", ((CENTER[0] + x) / 2, CENTER[1] + 10), GREEN)

    if abs(cos_val) > 1e-6:
        tan_y = CENTER[1] - RADIUS * math.tan(angle_rad)
        tan_y = max(min(tan_y, CENTER[1] + RADIUS), CENTER[1] - RADIUS)
        pygame.draw.line(screen, PURPLE, (CENTER[0] + RADIUS - 10, CENTER[1]), (CENTER[0] + RADIUS - 10, tan_y), 2)
        draw_text(f"tan={math.tan(angle_rad):.4f}", (CENTER[0] + RADIUS, tan_y), PURPLE)

    if abs(sin_val) > 1e-6:
        cot_x = CENTER[0] + RADIUS / math.tan(angle_rad)
        cot_x = max(min(cot_x, CENTER[0] + RADIUS), CENTER[0] - RADIUS)
        pygame.draw.line(screen, ORANGE, (CENTER[0], CENTER[1] + RADIUS - 10), (cot_x, CENTER[1] + RADIUS - 10), 2)
        draw_text(f"cot={1 / math.tan(angle_rad):.4f}", (cot_x, CENTER[1] + RADIUS), ORANGE)

def update_angle_from_input():
    global angle_rad
    try:
        if input_active == "deg":
            val = float(input_fields["deg"]["text"])
            angle_rad = math.radians(val % 360)
        elif input_active == "rad":
            val = float(input_fields["rad"]["text"])
            angle_rad = val % (2 * math.pi)
    except:
        pass

def update_fields_from_angle():
    deg = math.degrees(angle_rad) % 360
    rad = angle_rad % (2 * math.pi)
    if not input_fields["deg"]["dirty"]:
        input_fields["deg"]["text"] = f"{deg:.2f}"
    if not input_fields["rad"]["dirty"]:
        input_fields["rad"]["text"] = f"{rad:.4f}"

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(LIGHT_GRAY)
    pygame.draw.rect(screen, WHITE, (0, 0, 280, HEIGHT))
    update_fields_from_angle()
    draw_inputs()
    draw_values(angle_rad)
    draw_circle(angle_rad)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for key, field in input_fields.items():
                if field["rect"].collidepoint(event.pos):
                    input_active = key
                    field["text"] = ""
                    field["dirty"] = True

        elif event.type == pygame.KEYDOWN and input_active:
            field = input_fields[input_active]
            if event.key == pygame.K_RETURN:
                update_angle_from_input()
                field["dirty"] = False
                input_active = None
            elif event.key == pygame.K_BACKSPACE:
                field["text"] = field["text"][:-1]
            else:
                if event.unicode.isdigit() or event.unicode in ".-":
                    field["text"] += event.unicode

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
