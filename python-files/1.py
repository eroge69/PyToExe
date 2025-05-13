import pygame
from PIL import Image, ImageDraw, ImageFont
import time
import jdatetime
import sys
import io
import base64
from embedded_font import FONT_DATA
import math
import random

# راه‌اندازی اولیه
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# رنگ‌ها
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)

# تنظیمات فونت
FONT_SIZE_TIME = int(HEIGHT * 0.3)
FONT_SIZE_DATE = int(HEIGHT * 0.08)

# بارگذاری فونت از حافظه
font_bytes = base64.b64decode(FONT_DATA)
font_stream_time = io.BytesIO(font_bytes)
font_stream_date = io.BytesIO(font_bytes)
font_time = ImageFont.truetype(font_stream_time, FONT_SIZE_TIME)
font_date = ImageFont.truetype(font_stream_date, FONT_SIZE_DATE)

# محاسبه اندازه‌ها
digit_bbox = font_time.getbbox("8")
DIGIT_WIDTH = digit_bbox[2] - digit_bbox[0]
DIGIT_HEIGHT = digit_bbox[3] - digit_bbox[1]
COLON_WIDTH = DIGIT_WIDTH // 2

# لیست انیمیشن‌ها
animations = []

def rainbow_color_by_time(cycle_duration=10.0):
    """تولید رنگ رنگین‌کمانی با افکت پالس"""
    t = time.time() % cycle_duration
    position = t / cycle_duration
    
    # افزودن پالس با تغییر دامنه
    pulse = 0.2 * math.sin(2 * math.pi * position * 2) + 1.0
    
    r = int(255 * (math.sin(2 * math.pi * position + 0) * 0.5 + 0.5) * pulse)
    g = int(255 * (math.sin(2 * math.pi * position + 2) * 0.5 + 0.5) * pulse)
    b = int(255 * (math.sin(2 * math.pi * position + 4) * 0.5 + 0.5) * pulse)
    
    return (
        min(255, max(0, r)),
        min(255, max(0, g)),
        min(255, max(0, b))
    )

# تعریف تم‌های مختلف
THEMES = {
    "classic": {
        "digit": lambda: WHITE,
        "colon": lambda: WHITE,
        "date": lambda: GRAY
    },
    "rainbow": {
        "digit": rainbow_color_by_time,
        "colon": rainbow_color_by_time,
        "date": rainbow_color_by_time
    },
    "warm": {
        "digit": lambda: (255, 150, 50),
        "colon": lambda: (255, 200, 100),
        "date": lambda: (200, 100, 50)
    }
}

current_theme = "classic"
theme_transition_progress = 0.0
theme_transition_speed = 0.05

def get_theme_color(color_type):
    """دریافت رنگ با در نظر گرفتن انتقال تدریجی بین تم‌ها"""
    if theme_transition_progress >= 1.0:
        return THEMES[current_theme][color_type]()
    
    prev_theme = "classic" if current_theme == "rainbow" else "rainbow"
    prev_color = THEMES[prev_theme][color_type]()
    current_color = THEMES[current_theme][color_type]()
    
    r = int(prev_color[0] * (1 - theme_transition_progress) + current_color[0] * theme_transition_progress)
    g = int(prev_color[1] * (1 - theme_transition_progress) + current_color[1] * theme_transition_progress)
    b = int(prev_color[2] * (1 - theme_transition_progress) + current_color[2] * theme_transition_progress)
    
    return (r, g, b)

def render_digit(digit):
    """رندر یک رقم با رنگ تم فعلی"""
    color = get_theme_color("digit")
    img = Image.new("RGBA", (DIGIT_WIDTH, DIGIT_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = font_time.getbbox(digit)
    x = (DIGIT_WIDTH - (bbox[2] - bbox[0])) // 2
    y = (DIGIT_HEIGHT - (bbox[3] - bbox[1])) // 2
    draw.text((x, y), digit, font=font_time, fill=color)
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)

def render_colon():
    """رندر دونقطه با رنگ تم فعلی"""
    color = get_theme_color("colon")
    img = Image.new("RGBA", (COLON_WIDTH, DIGIT_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = font_time.getbbox(":")
    x = (COLON_WIDTH - (bbox[2] - bbox[0])) // 2
    y = (DIGIT_HEIGHT - (bbox[3] - bbox[1])) // 2
    draw.text((x, y), ":", font=font_time, fill=color)
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)

def render_date(date_text):
    """رندر تاریخ با رنگ تم فعلی"""
    color = get_theme_color("date")
    img = Image.new("RGBA", (WIDTH, FONT_SIZE_DATE + 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = font_date.getbbox(date_text)
    x = (img.width - (bbox[2] - bbox[0])) // 2
    y = (img.height - (bbox[3] - bbox[1])) // 2
    draw.text((x, y), date_text, font=font_date, fill=color)
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)

def schedule_flip_animation(old_digit, new_digit, x_pos, y_pos, start_time):
    """زمان‌بندی انیمیشن تغییر رقم با افکت تصادفی"""
    animation_type = random.choice(["flip", "slide_down", "fade"])
    
    if animation_type == "flip":
        animations.append({
            "type": "flip",
            "old": render_digit(old_digit),
            "new": render_digit(new_digit),
            "x": x_pos,
            "y": y_pos,
            "start_time": start_time,
            "duration": 0.3,
        })
    elif animation_type == "slide_down":
        animations.append({
            "type": "slide_down",
            "old": render_digit(old_digit),
            "new": render_digit(new_digit),
            "x": x_pos,
            "y": y_pos,
            "start_time": start_time,
            "duration": 0.4,
        })
    elif animation_type == "fade":
        animations.append({
            "type": "fade",
            "old": render_digit(old_digit),
            "new": render_digit(new_digit),
            "x": x_pos,
            "y": y_pos,
            "start_time": start_time,
            "duration": 0.5,
        })

def update_animations(current_time_sec):
    """به‌روزرسانی و رندر انیمیشن‌های فعال"""
    still_running = []
    for anim in animations:
        elapsed = current_time_sec - anim["start_time"]
        if elapsed >= anim["duration"]:
            screen.blit(anim["new"], (anim["x"], anim["y"]))
            continue

        progress = elapsed / anim["duration"]
        
        if anim["type"] == "flip":
            old_height = int(DIGIT_HEIGHT * (1 - progress))
            new_height = DIGIT_HEIGHT - old_height

            screen.fill(BLACK, (anim["x"], anim["y"], DIGIT_WIDTH, DIGIT_HEIGHT))

            if old_height > 0:
                old_part = pygame.transform.scale(anim["old"], (DIGIT_WIDTH, old_height))
                screen.blit(old_part, (anim["x"], anim["y"]))

            if new_height > 0:
                new_part = pygame.transform.scale(anim["new"], (DIGIT_WIDTH, new_height))
                screen.blit(new_part, (anim["x"], anim["y"] + old_height))
        
        elif anim["type"] == "slide_down":
            offset = int(DIGIT_HEIGHT * progress)
            
            screen.fill(BLACK, (anim["x"], anim["y"], DIGIT_WIDTH, DIGIT_HEIGHT))
            screen.blit(anim["old"], (anim["x"], anim["y"] + offset))
            screen.blit(anim["new"], (anim["x"], anim["y"] + offset - DIGIT_HEIGHT))
        
        elif anim["type"] == "fade":
            alpha = int(255 * progress)
            
            old_surface = anim["old"].copy()
            old_surface.set_alpha(255 - alpha)
            
            new_surface = anim["new"].copy()
            new_surface.set_alpha(alpha)
            
            screen.fill(BLACK, (anim["x"], anim["y"], DIGIT_WIDTH, DIGIT_HEIGHT))
            screen.blit(old_surface, (anim["x"], anim["y"]))
            screen.blit(new_surface, (anim["x"], anim["y"]))

        still_running.append(anim)
    animations[:] = still_running

def draw_time(current_time, last_time):
    """رندر زمان با انیمیشن‌های تغییر رقم"""
    y_pos = (HEIGHT - DIGIT_HEIGHT) // 2
    total_width = 2*DIGIT_WIDTH + COLON_WIDTH + 2*DIGIT_WIDTH
    start_x = (WIDTH - total_width) // 2
    now_sec = time.time()

    for i in range(2):
        x_pos = start_x + i * DIGIT_WIDTH
        if last_time == "" or current_time[i] == last_time[i]:
            digit_img = render_digit(current_time[i])
            screen.blit(digit_img, (x_pos, y_pos))
        else:
            schedule_flip_animation(last_time[i], current_time[i], x_pos, y_pos, now_sec)

    colon = render_colon()
    colon_x = start_x + 2 * DIGIT_WIDTH
    screen.blit(colon, (colon_x, y_pos))

    for i in range(3, 5):
        x_pos = colon_x + COLON_WIDTH + (i - 3) * DIGIT_WIDTH
        if last_time == "" or current_time[i] == last_time[i]:
            digit_img = render_digit(current_time[i])
            screen.blit(digit_img, (x_pos, y_pos))
        else:
            schedule_flip_animation(last_time[i], current_time[i], x_pos, y_pos, now_sec)

# حالت اسکرین‌سیور: بستن با حرکت ماوس یا هر رویداد
last_time = ""
running = True
initial_mouse_pos = pygame.mouse.get_pos()

try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               event.type == pygame.KEYDOWN or \
               event.type == pygame.MOUSEBUTTONDOWN:
                running = False

        if pygame.mouse.get_pos() != initial_mouse_pos:
            running = False

        current_time = time.strftime("%H:%M")
        current_minute = int(time.strftime("%M"))
        
        # مدیریت تغییر تم
        target_theme = "rainbow" if current_minute % 5 == 0 else "classic"
        if target_theme != current_theme:
            current_theme = target_theme
            theme_transition_progress = 0.0
        
        if theme_transition_progress < 1.0:
            theme_transition_progress += theme_transition_speed
            theme_transition_progress = min(theme_transition_progress, 1.0)
        
        date_shamsi = jdatetime.date.today().strftime("%Y/%m/%d")

        screen.fill(BLACK)

        if current_time != last_time:
            draw_time(current_time, last_time)
            last_time = current_time
        else:
            draw_time(current_time, current_time)

        update_animations(time.time())

        date_surface = render_date(date_shamsi)
        screen.blit(date_surface, (0, HEIGHT - date_surface.get_height() - 20))

        pygame.display.flip()
        clock.tick(30)

except KeyboardInterrupt:
    pass
finally:
    pygame.quit()
    sys.exit()
