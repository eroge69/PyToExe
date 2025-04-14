import pygame
import random
import time
from moviepy import VideoFileClip
import sys
import os
import math
import json

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("А это чей квас?!!")
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
SHADOW = (50, 50, 50, 100)

kvass_hints = {
    "светлый": [
        "Хочу что-то лёгкое и освежающее…",
        "Дай мне что-то светленькое!",
        "Люблю простой квас.",
        "Что-то ненавязчивое и светлое, пожалуйста.",
        "Светлый квас — мой идеал на жаркий день.",
        "Хочу что-то прохладное и несложное.",
        "Давай светлого, чтобы утолить жажду!",
        "Простой светлый — то, что нужно в жару.",
        "Люблю, когда квас светлый и легко пьётся.",
        "Светленькое, чтобы освежиться без лишнего.",
        "Что-то золотистое и искрящееся, как лето.",
        "Светлый, как утренний воздух.",
        "Хочу квас, который можно пить литрами.",
        "Что-то, что пьётся легко, как вода, но с вкусом.",
        "Лёгкий и прозрачный, чтобы насладиться днём.",
        "Светлый, чтобы не перегружать вкус.",
        "Хочу что-то, что спасает в жару.",
        "Простой и понятный, без лишних сложностей.",
        "Светлый, чтобы наслаждаться каждым глотком.",
        "Что-то, что подойдёт для долгого дня."],
    "тёмный": [
        "Мне бы что-то густое и насыщенное…",
        "Тёмный — мой выбор!",
        "Хочу крепкий и тёмный квас.",
        "Дай тёмного, чтобы почувствовать вкус.",
        "Люблю, когда квас глубокий и тёмный.",
        "Что-то тёмное и мощное — в самый раз!",
        "Тёмный квас — это моя слабость.",
        "Хочу густого тёмного с характером.",
        "Давай тёмненькое, чтобы ощутить полноту вкуса.",
        "Тёмный и насыщенный — вот мой стиль.",
        "Что-то с оттенками ржаного хлеба.",
        "Тёмный, как вечернее небо.",
        "Идеально для прохладного вечера.",
        "Хочу что-то, что согреет душу.",
        "Тёмный, чтобы насладиться каждым глотком.",
        "Что-то, что оставляет приятное послевкусие.",
        "Тёмный, чтобы почувствовать глубину вкуса.",
        "Хочу что-то, что напоминает о традициях.",
        "Тёмный, чтобы насладиться в одиночестве.",
        "Что-то, что подойдёт для уютного вечера."
    ],
    "медовый": [
        "Есть что-то с натуральной сладостью?",
        "Медовый — мой фаворит!",
        "Хочу сладенького кваса.",
        "Дай что-то с мёдом, чтобы побаловать себя.",
        "Люблю квас с медовым оттенком.",
        "Медовый квас — это сладкий кайф!",
        "Что-то мёдовое и мягкое, пожалуйста.",
        "Хочу сладости и кваса в одном стакане.",
        "Давай что-то мёдовое, чтобы почувствовать уют.",
        "Медовый — мой выбор для настроения.",
        "Как будто пьёшь жидкий мёд с газами.",
        "Сладкий, но не приторный.",
        "Напоминает о деревенском улье и цветах.",
        "Хочу что-то, что пахнет летом.",
        "Медовый, чтобы насладиться сладостью.",
        "Что-то, что подойдёт для тёплого дня.",
        "Медовый, чтобы почувствовать гармонию.",
        "Хочу что-то, что пьётся с удовольствием.",
        "Медовый, чтобы насладиться моментом.",
        "Что-то, что подойдёт для семейного застолья."
    ],
    "хлебный": [
        "Хочу что-то с ароматом свежего хлеба…",
        "Хлебный бы сейчас!",
        "Люблю настоящий хлебный вкус.",
        "Дай что-то сытное и хлебное.",
        "Хочу чего-то традиционного и хлебного.",
        "Хлебный квас — это мой комфорт.",
        "Люблю квас с лёгким хлебным послевкусием.",
        "Давай что-то хлебное, чтобы расслабиться.",
        "Что-то с ароматом ржаной корочки.",
        "Хлебный — идеально для обеда.",
        "Как будто пьёшь свежий хлебный настой.",
        "Простой и родной вкус.",
        "Напоминает о деревенских традициях.",
        "Хочу что-то, что пахнет домом.",
        "Хлебный, чтобы насладиться простотой.",
        "Что-то, что подойдёт к окрошке.",
        "Хлебный, чтобы почувствовать уют.",
        "Хочу что-то, что пьётся как традиция.",
        "Хлебный, чтобы насладиться ароматом.",
        "Что-то, что подойдёт для отдыха на даче."
    ],
    "ягодный": [
        "Дай что-то с ягодной свежестью!",
        "Ягодный — то, что надо!",
        "Люблю лёгкий ягодный вкус.",
        "Хочу ягодного с приятной кислинкой.",
        "Ягодный квас — это мой летний выбор!",
        "Давай что-то свежее и с ягодами.",
        "Люблю, когда квас пахнет лесом.",
        "Ягодный, чтобы освежиться!",
        "Что-то ягодное и прохладное, пожалуйста.",
        "Ягодный — идеально для яркого дня.",
        "Как будто пьёшь компот с газами.",
        "Лёгкая кислинка и ягодный аромат.",
        "Напоминает о летних прогулках и малине.",
        "Хочу что-то, что пахнет ягодами.",
        "Ягодный, чтобы насладиться свежестью.",
        "Что-то, что подойдёт для жаркого дня.",
        "Ягодный, чтобы почувствовать лёгкость.",
        "Хочу что-то, что пьётся с радостью.",
        "Ягодный, чтобы насладиться моментом.",
        "Что-то, что подойдёт для пикника."
    ],
    "травяной": [
        "Хочу что-то с ароматом трав…",
        "Травяной бы сейчас!",
        "Люблю квас с ноткой природы.",
        "Дай что-то травяное и свежее.",
        "Хочу чего-то с лёгким травяным оттенком.",
        "Травяной квас — это моя гармония.",
        "Люблю, когда квас пахнет лугом.",
        "Давай что-то травяное, чтобы расслабиться.",
        "Что-то с ароматом мяты или чабреца.",
        "Травяной — идеально для спокойствия.",
        "Как будто пьёшь настой с полей.",
        "Лёгкий и природный вкус.",
        "Напоминает о прогулках по лесу.",
        "Хочу что-то, что пахнет травами.",
        "Травяной, чтобы насладиться свежестью.",
        "Что-то, что подойдёт для отдыха.",
        "Травяной, чтобы почувствовать природу.",
        "Хочу что-то, что пьётся с умиротворением.",
        "Травяной, чтобы насладиться ароматом.",
        "Что-то, что подойдёт для вечера на веранде."
    ],
    "имбирный": [
        "Дай что-то освежающее и с огоньком!",
        "Имбирный — то, что надо!",
        "Люблю пряный вкус.",
        "Хочу имбирного с лёгкой остринкой.",
        "Имбирный квас — это мой драйв!",
        "Давай что-то свежее и с имбирным характером.",
        "Люблю, когда квас бодрит имбирём.",
        "Имбирный, чтобы встряхнуться!",
        "Что-то пряное и прохладное, пожалуйста.",
        "Имбирный — идеально для яркого вкуса.",
        "Как будто пьёшь пряный лимонад.",
        "Освежает и бодрит одновременно.",
        "Напоминает о зимних днях и тёплых напитках.",
        "Хочу что-то, что бодрит и освежает.",
        "Имбирный, чтобы почувствовать энергию.",
        "Что-то, что подойдёт для активного дня.",
        "Имбирный, чтобы насладиться пряностью.",
        "Хочу что-то, что пьётся с огоньком.",
        "Имбирный, чтобы насладиться вкусом.",
        "Что-то, что подойдёт для настроения."
    ],
    "окрошечный": [
        "Хочу что-то для летнего супа…",
        "Окрошечный бы сейчас!",
        "Люблю квас для окрошки.",
        "Дай что-то кислое и свежее.",
        "Хочу чего-то идеального для холодного супа.",
        "Окрошечный квас — это моя классика.",
        "Люблю квас с лёгкой кислинкой для еды.",
        "Давай что-то для окрошки на обед.",
        "Что-то с кислинкой и хлебным оттенком.",
        "Окрошечный — идеально для лета.",
        "Как будто создан для овощей и зелени.",
        "Лёгкий и кислый вкус.",
        "Напоминает о дачных обедах.",
        "Хочу что-то, что идеально для супа.",
        "Окрошечный, чтобы насладиться свежестью.",
        "Что-то, что подойдёт к обеду.",
        "Окрошечный, чтобы почувствовать лето.",
        "Хочу что-то, что пьётся с аппетитом.",
        "Окрошечный, чтобы насладиться моментом.",
        "Что-то, что подойдёт для семейного стола."
    ],
    "классический": [
        "Хочу классику в холодной банке!",
        "Классический — это всегда хорошо!",
        "Дай что-то лёгкое из банки.",
        "Люблю классический квас за простоту.",
        "Давай холодного классического на день.",
        "Классический квас — традиция, которая не подводит.",
        "Хочу лёгкого кваса, чтобы освежиться.",
        "Дай мне классический, чистый и холодный.",
        "Классический в банке — мой надёжный выбор.",
        "Что-то традиционное, вроде классического.",
        "Настоящий вкус кваса, как раньше.",
        "Просто и со вкусом.",
        "Идеально для жаркого дня и отдыха.",
        "Хочу что-то, что пьётся легко и непринуждённо.",
        "Классический, чтобы насладиться простотой.",
        "Что-то, что подойдёт для любого случая.",
        "Классический, чтобы почувствовать традиции.",
        "Хочу что-то, что пьётся с удовольствием.",
        "Классический, чтобы насладиться моментом.",
        "Что-то, что подойдёт для встреч с друзьями."
    ],
    "ржаной": [
        "Люблю насыщенный ржаной вкус!",
        "Ржаной в банке — мой выбор!",
        "Дай что-то ржаное, чтобы насладиться глубиной.",
        "Хочу чего-то с ароматом ржи.",
        "Ржаной квас — это мой надёжный друг!",
        "Люблю ржаной за его полноту.",
        "Давай что-то густое с хлебным послевкусием.",
        "Что-то ржаное, пожалуйста.",
        "Ржаной в банке — идеально для дня.",
        "Хочу ржаного кваса с характером.",
        "Как будто пьёшь ржаной хлеб в жидком виде.",
        "Густой и насыщенный вкус.",
        "Напоминает о деревенских традициях.",
        "Хочу что-то, что согреет душу.",
        "Ржаной, чтобы насладиться глубиной вкуса.",
        "Что-то, что подойдёт для обеда.",
        "Ржаной, чтобы почувствовать уют.",
        "Хочу что-то, что пьётся с наслаждением.",
        "Ржаной, чтобы насладиться моментом.",
        "Что-то, что подойдёт для отдыха."
    ],
    "мятный": [
        "Дай что-то свежее и ароматное!",
        "Мятный — это моё!",
        "Хочу кваса с мятной прохладой.",
        "Люблю мятный за его лёгкость.",
        "Давай мятный, чтобы освежиться!",
        "Мятный квас — мой выбор для свежести.",
        "Хочу чего-то с мятным ароматом.",
        "Дай мне мятный с приятной прохладой.",
        "Мятный в банке — это всегда праздник.",
        "Что-то мятное и лёгкое, пожалуйста.",
        "Как будто пьёшь летний ветер.",
        "Свежий и бодрящий вкус.",
        "Напоминает о прохладных утрах.",
        "Хочу что-то, что освежает и радует.",
        "Мятный, чтобы насладиться свежестью.",
        "Что-то, что подойдёт для жаркого дня.",
        "Мятный, чтобы почувствовать лёгкость.",
        "Хочу что-то, что пьётся с удовольствием.",
        "Мятный, чтобы насладиться моментом.",
        "Что-то, что подойдёт для отдыха."
    ],
    "Квас Тарас": [
        "Хочу что-то крепкое и традиционное из банки!",
        "Дай мне что-то с ярким вкусом.",
        "Люблю квас с насыщенным характером.",
        "Что-то мощное и хлебное, пожалуйста.",
        "Крепкий квас — мой выбор на день.",
        "Хочу чего-то, что чувствуется сразу.",
        "Давай что-то мощное из банки.",
        "Люблю, когда вкус бьёт по рецепторам.",
        "Крепкий и традиционный — то, что надо.",
        "Дай мне что-то с глубиной и силой.",
        "Настоящий вкус старинного рецепта.",
        "Сила традиций в каждой капле.",
        "Напоминает о ярмарках и праздниках.",
        "Хочу что-то, что бодрит и освежает.",
        "Квас Тарас, чтобы насладиться полнотой.",
        "Что-то, что подойдёт для яркого дня.",
        "Квас Тарас, чтобы почувствовать мощь.",
        "Хочу что-то, что пьётся с удовольствием.",
        "Квас Тарас, чтобы насладиться моментом.",
        "Что-то, что подойдёт для встреч."],
    "Никола": [
        "Хочу что-то мягкое, но с характером из банки.",
        "Дай мне что-то для спокойного дня.",
        "Люблю квас с лёгким, но ярким вкусом.",
        "Что-то сбалансированное и приятное, пожалуйста.",
        "Давай что-то для отдыха с друзьями.",
        "Хочу лёгкого, но запоминающегося кваса.",
        "Люблю, когда вкус мягкий и утончённый.",
        "Дай мне что-то из банки для настроения.",
        "Что-то классическое, но с изюминкой.",
        "Хочу квас, который пьётся легко и с удовольствием.",
        "Идеальный баланс вкуса и свежести.",
        "Мягкий, как летний день.",
        "Напоминает о душевных посиделках.",
        "Хочу что-то, что пьётся легко и непринуждённо.",
        "Никола, чтобы насладиться мягкостью.",
        "Что-то, что подойдёт для любого случая.",
        "Никола, чтобы почувствовать баланс.",
        "Хочу что-то, что пьётся с удовольствием.",
        "Никола, чтобы насладиться моментом.",
        "Что-то, что подойдёт для встреч."
    ],
    "Очаковский": [
        "Хочу что-то лёгкое и свежее из банки!",
        "Дай мне что-то для жаркого дня.",
        "Люблю квас с чистым и простым вкусом.",
        "Что-то освежающее и ненавязчивое, пожалуйста.",
        "Давай что-то, что утоляет жажду.",
        "Хочу лёгкого кваса с приятным послевкусием.",
        "Люблю, когда квас простой и понятный.",
        "Дай мне что-то холодное и свежее.",
        "Что-то из банки для лёгкого отдыха.",
        "Хочу что-то, что пьётся как вода, но с вкусом.",
        "Лёгкость и свежесть в каждом глотке.",
        "Просто, как деревенский квас.",
        "Напоминает о летнем отдыхе на даче.",
        "Хочу что-то, что освежает в жару.",
        "Очаковский, чтобы насладиться простотой.",
        "Что-то, что подойдёт для любого случая.",
        "Очаковский, чтобы почувствовать свежесть.",
        "Хочу что-то, что пьётся с удовольствием.",
        "Очаковский, чтобы насладиться моментом.",
        "Что-то, что подойдёт для встреч."
    ],
    "Лидский": [
        "Хочу что-то насыщенное и традиционное из банки!",
        "Дай мне что-то с глубоким вкусом.",
        "Люблю квас с богатым характером.",
        "Что-то хлебное и оригинальное, пожалуйста.",
        "Давай что-то, что выделяется среди других.",
        "Хочу кваса с ярким и смелым профилем.",
        "Люблю, когда вкус удивляет и радует.",
        "Дай мне что-то из банки с изюминкой.",
        "Что-то насыщенное и запоминающееся.",
        "Хочу квас, который оставляет впечатление.",
        "Настоящий вкус старых рецептов.",
        "Глубина и традиции в каждом глотке.",
        "Напоминает о старинных традициях.",
        "Хочу что-то, что бодрит и освежает.",
        "Лидский, чтобы насладиться полнотой.",
        "Что-то, что подойдёт для яркого дня.",
        "Лидский, чтобы почувствовать историю.",
        "Хочу что-то, что пьётся с удовольствием.",
        "Лидский, чтобы насладиться моментом.",
        "Что-то, что подойдёт для встреч."
    ],
    "Русский Дар": [
        "Хочу что-то мягкое и ароматное из банки!",
        "Дай мне что-то с лёгкими хлебными нотками.",
        "Люблю квас с утончённым вкусом.",
        "Что-то нежное и освежающее, пожалуйста.",
        "Давай что-то для любителей традиций из банки.",
        "Хочу кваса с тонким и приятным ароматом.",
        "Люблю, когда вкус мягкий и сложный.",
        "Дай мне что-то изысканное и лёгкое.",
        "Что-то с ноткой хлеба и свежести.",
        "Хочу квас, который радует душу.",
        "Русская классика с природным шармом.",
        "Изысканность и простота в одном глотке.",
        "Напоминает о деревенских просторах.",
        "Хочу что-то, что освежает и радует.",
        "Русский Дар, чтобы насладиться традицией.",
        "Что-то, что подойдёт для любого случая.",
        "Русский Дар, чтобы почувствовать тепло.",
        "Хочу что-то, что пьётся с удовольствием.",
        "Русский Дар, чтобы насладиться моментом.",
        "Что-то, что подойдёт для встреч."]
}



def get_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath("")
    return os.path.join(base_path, relative_path)

def grab_image(path, scale=None):
    try:
        img = pygame.image.load(get_path(path))
        if scale:
            return pygame.transform.scale(img, scale)
        return img
    except pygame.error:
        return pygame.Surface((50, 50))

def grab_sound(path):
    full_path = get_path(path)
    if not os.path.exists(full_path):
        return None
    try:
        sound = pygame.mixer.Sound(full_path)
        return sound
    except pygame.error:
        return None

pygame.display.set_icon(grab_image('config/data/ico.ico').convert_alpha())

bg_music = grab_sound("config/voises/background_music.wav")
if bg_music:
    bg_music.set_volume(0.2)

tap_sound = grab_sound("config/voises/pivo.wav")
sink_sound = grab_sound("config/voises/sink.wav")
fridge_open_sound = grab_sound("config/voises/open.wav")
fridge_working_sound = grab_sound("config/voises/working.wav")
fridge_close_sound = grab_sound("config/voises/close.wav")

menu_bg = grab_image('config/textures/bg/pause.png', (WIDTH, HEIGHT))

kvass_prices = {
    "светлый": 6,
    "тёмный": 8,
    "медовый": 10,
    "хлебный": 7,
    "ягодный": 9,
    "травяной": 8,
    "имбирный": 9,
    "окрошечный": 6,
    "классический": 5,
    "ржаной": 7,
    "мятный": 8,
    "Квас Тарас": 7,
    "Никола": 6,
    "Очаковский": 5,
    "Лидский": 7,
    "Русский Дар": 8
}

def splash_screen():
    if bg_music and pygame.mixer.get_busy():
        bg_music.stop()
    try:
        video_clip = VideoFileClip(get_path('config/textures/splash/splash.mp4'))
        start_time = time.time()
        splash_time = 6
        for frame in video_clip.iter_frames(fps=30):
            if time.time() - start_time > splash_time:
                break
            surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            screen.blit(pygame.transform.scale(surface, (WIDTH, HEIGHT)), (0, 0))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            clock.tick(30)
    except Exception:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 50)
        text = font.render("Загрузка...", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))
        pygame.display.flip()
        time.sleep(2)

font = pygame.font.Font(None, 50)

def start_menu():
    if bg_music and not pygame.mixer.get_busy():
        bg_music.play(-1)
    buttons = [
        {"text": "config/textures/buttons/play.png", "pos": (WIDTH // 2 - 150, HEIGHT // 2), "action": "play"},
        {"text": "config/textures/buttons/exit.png", "pos": (WIDTH // 2 - 150, HEIGHT // 2 + 100), "action": "quit"}
    ]
    loaded_buttons = []
    for button in buttons:
        btn_surface = grab_image(button['text'])
        btn_surface = btn_surface.convert_alpha()
        btn_surface = pygame.transform.scale(btn_surface, (300, 100))
        btn_rect = btn_surface.get_rect(topleft=button["pos"])
        loaded_buttons.append({"surface": btn_surface, "rect": btn_rect, "action": button["action"]})
    running = True
    while running:
        screen.blit(menu_bg, (0, 0))
        for button in loaded_buttons:
            screen.blit(button["surface"], button["rect"])
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for button in loaded_buttons:
                    if button["rect"].collidepoint(x, y):
                        if button["action"] == "play":
                            running = False
                            return
                        elif button["action"] == "quit":
                            running = False
                            pygame.quit()
                            sys.exit()
        clock.tick(FPS)

background = grab_image("config/textures/bg/main_bg.png")

character_textures = {
    "Василий": grab_image("config/textures/caracters/vasiliy.png", (300, 400)),
    "Коля": grab_image("config/textures/caracters/kolya.png", (300, 400)),
    "Оля": grab_image("config/textures/caracters/olya.png", (300, 400)),
    "Серёга": grab_image("config/textures/caracters/serega.png", (300, 400)),
    "Лена": grab_image("config/textures/caracters/lena.png", (300, 400)),
    "Женя": grab_image("config/textures/caracters/zhenya.png", (300, 400)),
    "Гоша": grab_image("config/textures/caracters/gosha.png", (300, 400)),
    "Катя": grab_image("config/textures/caracters/danua.png", (300, 400)),
    "Игорь": grab_image("config/textures/caracters/igor.png", (300, 400)),
    "Марина": grab_image("config/textures/caracters/misha.png", (300, 400))
}

character_sounds = {
    "Василий": grab_sound("config/voises/vasia.wav"),
    "Коля": grab_sound("config/voises/kolia.wav"),
    "Оля": grab_sound("config/voises/olua.wav"),
    "Серёга": grab_sound("config/voises/serega.wav"),
    "Лена": grab_sound("config/voises/lena.wav"),
    "Женя": grab_sound("config/voises/jenya.wav"),
    "Гоша": grab_sound("config/voises/gosha.wav"),
    "Катя": grab_sound("config/voises/danua.wav"),
    "Игорь": grab_sound("config/voises/igor.wav"),
    "Марина": grab_sound("config/voises/misha.wav")
}

tap_textures = {
    "светлый": grab_image("config/textures/kvass_taps/tap_light.png"),
    "тёмный": grab_image("config/textures/kvass_taps/tap_dark.png"),
    "медовый": grab_image("config/textures/kvass_taps/tap_honey.png"),
    "хлебный": grab_image("config/textures/kvass_taps/tap_bread.png"),
    "ягодный": grab_image("config/textures/kvass_taps/tap_berry.png"),
    "травяной": grab_image("config/textures/kvass_taps/tap_herbal.png"),
    "имбирный": grab_image("config/textures/kvass_taps/tap_ginger.png"),
    "окрошечный": grab_image("config/textures/kvass_taps/tap_okroshka.png")
}

kvass_textures = {
    "светлый": grab_image("config/textures/kvass/kvass.png", (62, 89)),
    "тёмный": grab_image("config/textures/kvass/kvass.png", (62, 89)),
    "медовый": grab_image("config/textures/kvass/kvass.png", (62, 89)),
    "хлебный": grab_image("config/textures/kvass/kvass.png", (62, 89)),
    "ягодный": grab_image("config/textures/kvass/kvass.png", (62, 89)),
    "травяной": grab_image("config/textures/kvass/kvass.png", (62, 89)),
    "имбирный": grab_image("config/textures/kvass/kvass.png", (62, 89)),
    "окрошечный": grab_image("config/textures/kvass/kvass.png", (62, 89))
}

kvass_taps = {
    "светлый": (20, 865),
    "тёмный": (150, 865),
    "медовый": (280, 865),
    "хлебный": (410, 865),
    "ягодный": (540, 865),
    "травяной": (670, 865),
    "имбирный": (800, 865),
    "окрошечный": (930, 865)
}

sink_texture = grab_image("config/textures/kvass_taps/sink.png")
sink_position = (830 + 200, 910)

fridge_closed = grab_image("config/textures/kvass_taps/fridge_closed.png")
fridge_open = grab_image("config/textures/kvass_taps/fridge_open.png")
fridge_position = (1500, 850)

phone_texture = grab_image("config/textures/kvass_taps/phone.png")
phone_position = (1320, 950)

can_textures = {
    "классический": grab_image("config/textures/kvass/can_classic.png", scale=(33, 59)),
    "ржаной": grab_image("config/textures/kvass/can_rye.png", scale=(33, 59)),
    "мятный": grab_image("config/textures/kvass/can_mint.png", scale=(33, 59)),
    "Квас Тарас": grab_image("config/textures/kvass/can_taras.png", scale=(33, 59)),
    "Никола": grab_image("config/textures/kvass/can_nikola.png", scale=(33, 59)),
    "Очаковский": grab_image("config/textures/kvass/can_ochakovsky.png", scale=(33, 59)),
    "Лидский": grab_image("config/textures/kvass/can_lidsky.png", scale=(33, 59)),
    "Русский Дар": grab_image("config/textures/kvass/can_russky_dar.png", scale=(33, 59))
}

fridge_positions = [
    (fridge_position[0] + 20, fridge_position[1] + 30),
    (fridge_position[0] + 70, fridge_position[1] + 30),
    (fridge_position[0] + 110, fridge_position[1] + 30),
    (fridge_position[0] + 160, fridge_position[1] + 30),
    (fridge_position[0] + 20, fridge_position[1] + 127),
    (fridge_position[0] + 70, fridge_position[1] + 127),
    (fridge_position[0] + 110, fridge_position[1] + 127),
    (fridge_position[0] + 160, fridge_position[1] + 127)
]

can_positions = {
    "классический": fridge_positions[0],
    "ржаной": fridge_positions[1],
    "мятный": fridge_positions[2],
    "Квас Тарас": fridge_positions[3],
    "Никола": fridge_positions[4],
    "Очаковский": fridge_positions[5],
    "Лидский": fridge_positions[6],
    "Русский Дар": fridge_positions[7]
}

kvass_types = ["светлый", "тёмный", "медовый", "хлебный", "ягодный", "травяной", "имбирный", "окрошечный"]
can_types = ["классический", "ржаной", "мятный", "Квас Тарас", "Никола", "Очаковский", "Лидский", "Русский Дар"]

characters = [
    {"name": "Василий"}, {"name": "Серёга"}, {"name": "Оля"}, {"name": "Коля"},
    {"name": "Лена"}, {"name": "Женя"}, {"name": "Гоша"}, {"name": "Катя"},
    {"name": "Игорь"}, {"name": "Марина"}
]

holding_mug = None
current_character = None
current_hint = None
current_beer = None
score = 0
spawn_timer = 0
SPAWN_INTERVAL = 180
character_x = WIDTH
character_state = "entering"
animation_time = 0
text_alpha = 0
last_character = None
tips = 0
money = 1000
beer_stock = {beer: 0 for beer in kvass_types + can_types}
owned_cans = []
fridge_hover = False
shop_open = False
selected_beer = None
slider_value = 0
scroll_offset = 0
scroll_velocity = 0
fridge_was_hovered = False

MAX_BEER_STOCK = 50
MAX_CAN_STOCK = 20

def setup_defaults():
    global money, beer_stock, owned_cans, tips
    money = 5000
    beer_stock = {beer: 10 for beer in kvass_types + can_types}
    owned_cans = []
    tips = 0

def save_game():
    data = {
        "money": money,
        "beer_stock": beer_stock,
        "owned_cans": owned_cans,
        "tips": tips
    }
    save_path = get_path("config/data/saves/save_data.json")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w") as f:
        json.dump(data, f)

def load_game():
    global money, beer_stock, owned_cans, tips
    save_path = get_path("config/data/saves/save_data.json")
    if os.path.exists(save_path):
        try:
            with open(save_path, "r") as f:
                data = json.load(f)
                money = data.get("money", 1000)
                beer_stock = data.get("beer_stock", {beer: 0 for beer in kvass_types + can_types})
                owned_cans = data.get("owned_cans", [])
                tips = data.get("tips", 0)
                for beer in kvass_types + can_types:
                    if beer not in beer_stock:
                        beer_stock[beer] = 0
        except (json.JSONDecodeError, IOError):
            setup_defaults()
            save_game()
    else:
        setup_defaults()
        save_game()

def pause_screen():
    paused = True
    buttons = [
        {"text": "config/textures/buttons/continue.png", "pos": (WIDTH // 2 - 150, HEIGHT // 2), "action": "resume"},
        {"text": "config/textures/buttons/tomenu.png", "pos": (WIDTH // 2 - 150, HEIGHT // 2 + 100), "action": "quit"}
    ]
    loaded_buttons = []
    for button in buttons:
        btn_surface = grab_image(button['text'])
        btn_surface = btn_surface.convert_alpha()
        btn_surface = pygame.transform.scale(btn_surface, (300, 100))
        btn_rect = btn_surface.get_rect(topleft=button["pos"])
        loaded_buttons.append({"surface": btn_surface, "rect": btn_rect, "action": button["action"]})
    while paused:
        screen.blit(menu_bg, (0, 0))
        for button in loaded_buttons:
            screen.blit(button["surface"], button["rect"])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for button in loaded_buttons:
                    if button["rect"].collidepoint(x, y):
                        if button["action"] == "resume":
                            paused = False
                        elif button["action"] == "quit":
                            save_game()
                            return True
        pygame.display.flip()
        clock.tick(FPS)
    return False

def draw_shop():
    global shop_open, selected_beer, slider_value, money, scroll_offset, scroll_velocity
    shop_rect = pygame.Rect(WIDTH // 4 - 50, HEIGHT // 4 - 250, WIDTH // 2 + 100, HEIGHT // 2 + 400)
    shadow_surface = pygame.Surface((shop_rect.width + 20, shop_rect.height + 20), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, SHADOW, shadow_surface.get_rect(), border_radius=20)
    screen.blit(shadow_surface, (shop_rect.x - 10, shop_rect.y - 10))
    gradient_surface = pygame.Surface((shop_rect.width, shop_rect.height), pygame.SRCALPHA)
    for y in range(shop_rect.height):
        alpha = 255 - (y / shop_rect.height) * 150
        pygame.draw.line(gradient_surface, (LIGHT_GRAY[0], LIGHT_GRAY[1], LIGHT_GRAY[2], alpha), (0, y), (shop_rect.width, y))
    screen.blit(gradient_surface, shop_rect.topleft)
    pygame.draw.rect(screen, GOLD, shop_rect, 3, border_radius=15)
    title_font = pygame.font.Font(None, 70)
    title = title_font.render("Магазин пива", True, GOLD)
    title_shadow = title_font.render("Магазин пива", True, DARK_GRAY)
    screen.blit(title_shadow, (shop_rect.x + shop_rect.width // 2 - title.get_width() // 2 + 2, shop_rect.y + 22))
    screen.blit(title, (shop_rect.x + shop_rect.width // 2 - title.get_width() // 2, shop_rect.y + 20))
    close_rect = pygame.Rect(shop_rect.right - 50, shop_rect.top + 10, 40, 40)
    close_hover = close_rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, (255, 80, 80) if close_hover else (220, 50, 50), close_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, close_rect, 2, border_radius=10)
    pygame.draw.line(screen, WHITE, (close_rect.x + 12, close_rect.y + 12), (close_rect.x + 28, close_rect.y + 28), 3)
    pygame.draw.line(screen, WHITE, (close_rect.x + 28, close_rect.y + 12), (close_rect.x + 12, close_rect.y + 28), 3)
    content_height = (len(kvass_types) + len(can_types)) * 50 + (150 if selected_beer else 0)
    scroll_bar_rect = pygame.Rect(shop_rect.right - 20, shop_rect.y + 80, 10, shop_rect.height - 130)
    scroll_thumb_height = max(50, (shop_rect.height - 130) * (shop_rect.height - 130) / content_height)
    max_scroll = max(0, content_height - (shop_rect.height - 130))
    scroll_offset = min(max(0, scroll_offset), max_scroll)
    y_offset = shop_rect.y + 80 - scroll_offset
    button_rects = []
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for beer in kvass_types + can_types:
        if y_offset + 50 < shop_rect.y + 80 or y_offset > shop_rect.bottom:
            y_offset += 50
            if selected_beer == beer:
                y_offset += 150
            continue
        price = kvass_prices[beer]
        stock = beer_stock.get(beer, 0) if beer in kvass_types else owned_cans.count(beer)
        text = f"{beer}: {price}$ (запас: {stock})"
        btn_surface = font.render(text, True, BLACK)
        btn_height = 50 if beer != selected_beer else 200
        btn_rect = pygame.Rect(shop_rect.x + 20, y_offset, shop_rect.width - 40, 50)
        full_rect = pygame.Rect(shop_rect.x + 20, y_offset, shop_rect.width - 40, btn_height)
        btn_hover = btn_rect.collidepoint(mouse_x, mouse_y)
        btn_color = WHITE if beer == selected_beer else (WHITE if not btn_hover else LIGHT_GRAY)
        pygame.draw.rect(screen, DARK_GRAY, full_rect.inflate(4, 4), border_radius=8)
        pygame.draw.rect(screen, btn_color, full_rect, 0, border_radius=8)
        screen.blit(btn_surface, (btn_rect.x + 10, btn_rect.y + (50 - btn_surface.get_height()) // 2))
        button_rects.append((beer, btn_rect))
        y_offset += 50
        if selected_beer == beer:
            current_stock = beer_stock.get(beer, 0) if beer in kvass_types else owned_cans.count(beer)
            max_stock = MAX_BEER_STOCK if beer in kvass_types else MAX_CAN_STOCK
            remaining_capacity = max_stock - current_stock
            max_purchase = MAX_CAN_STOCK if beer in can_types else float('inf')
            max_value = min(remaining_capacity, money // price, max_purchase)
            slider_rect = pygame.Rect(shop_rect.x + 40, y_offset + 40, 400, 20)
            pygame.draw.rect(screen, GRAY, slider_rect, border_radius=10)
            if max_value > 0:
                if beer in kvass_types:
                    slider_value = max(0, min(slider_value, max_value))
                    fill_width = (slider_value / max_value) * slider_rect.width
                else:
                    slider_value = int(max(0, min(slider_value, max_value)))
                    fill_width = (slider_value / max_value) * slider_rect.width
                pygame.draw.rect(screen, GOLD, (slider_rect.x, slider_rect.y, fill_width, 20), border_radius=10)
                slider_pos = slider_rect.x + fill_width
            else:
                slider_pos = slider_rect.x
            pygame.draw.circle(screen, WHITE, (int(slider_pos), slider_rect.centery), 12)
            pygame.draw.circle(screen, GOLD, (int(slider_pos), slider_rect.centery), 8)
            unit = 'л' if beer in kvass_types else 'шт'
            qty_text = font.render(f"Покупка: {slider_value}/{max_value} {unit}", True, BLACK)
            cost_text = font.render(f"Стоимость: {slider_value * price}$", True, BLACK)
            screen.blit(qty_text, (shop_rect.x + 40, y_offset + 70))
            screen.blit(cost_text, (shop_rect.x + 40, y_offset + 100))
            button_size = (40, 30)
            plus_1_rect = pygame.Rect(shop_rect.x + 500, y_offset + 45, *button_size)
            plus_5_rect = pygame.Rect(shop_rect.x + 500, y_offset + 80, *button_size)
            plus_10_rect = pygame.Rect(shop_rect.x + 500, y_offset + 115, *button_size)
            minus_1_rect = pygame.Rect(shop_rect.x + 550, y_offset + 45, *button_size)
            minus_5_rect = pygame.Rect(shop_rect.x + 550, y_offset + 80, *button_size)
            minus_10_rect = pygame.Rect(shop_rect.x + 550, y_offset + 115, *button_size)
            buttons = [
                (plus_1_rect, "+1", 1),
                (minus_1_rect, "-1", -1),
                (plus_5_rect, "+5", 5),
                (minus_5_rect, "-5", -5),
                (plus_10_rect, "+10", 10),
                (minus_10_rect, "-10", -10)
            ]
            for btn_rect, btn_text, value in buttons:
                hover = btn_rect.collidepoint(mouse_x, mouse_y)
                pygame.draw.rect(screen, GOLD if hover else LIGHT_GRAY, btn_rect, 0, border_radius=5)
                pygame.draw.rect(screen, DARK_GRAY, btn_rect, 2, border_radius=5)
                text_surface = font.render(btn_text, True, BLACK)
                screen.blit(text_surface, (
                    btn_rect.centerx - text_surface.get_width() // 2,
                    btn_rect.centery - text_surface.get_height() // 2))
                button_rects.append((btn_text, btn_rect))
            buy_rect = pygame.Rect(shop_rect.x + shop_rect.width - 150, y_offset + 20, 100, 40)
            buy_hover = buy_rect.collidepoint(mouse_x, mouse_y)
            pygame.draw.rect(screen, GOLD if buy_hover else LIGHT_GRAY, buy_rect, 0, border_radius=10)
            pygame.draw.rect(screen, DARK_GRAY, buy_rect, 2, border_radius=10)
            buy_text = font.render("Купить", True, BLACK)
            screen.blit(buy_text,
                        (buy_rect.centerx - buy_text.get_width() // 2, buy_rect.centery - buy_text.get_height() // 2))
            y_offset += 150
    if max_scroll > 0:
        scroll_thumb_y = shop_rect.y + 80 + (scroll_offset / max_scroll) * (
                shop_rect.height - 130 - scroll_thumb_height)
        pygame.draw.rect(screen, GRAY, scroll_bar_rect, border_radius=5)
        pygame.draw.rect(screen, GOLD, (scroll_bar_rect.x, scroll_thumb_y, 10, scroll_thumb_height), border_radius=5)
    scroll_offset += scroll_velocity
    scroll_offset = min(max(0, scroll_offset), max_scroll)
    scroll_velocity *= 0.9
    return close_rect, button_rects

def play_game():
    global holding_mug, current_character, current_hint, current_beer, score, spawn_timer, character_x, character_state, animation_time, text_alpha, last_character, tips, money, fridge_hover, shop_open, selected_beer, slider_value, scroll_offset, scroll_velocity, fridge_was_hovered
    load_game()
    if bg_music and not pygame.mixer.get_busy():
        bg_music.play(-1)
    running = True
    purchase_feedback = None
    feedback_timer = 0
    while running:
        screen.blit(background, (0, 0))
        for beer, pos in kvass_taps.items():
            tap_rect = tap_textures[beer].get_rect(topleft=pos)
            screen.blit(tap_textures[beer], pos)
        sink_rect = sink_texture.get_rect(topleft=sink_position)
        screen.blit(sink_texture, sink_position)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        fridge_rect = fridge_closed.get_rect(topleft=fridge_position)
        fridge_hover = fridge_rect.collidepoint(mouse_x, mouse_y)
        if fridge_hover and not fridge_was_hovered:
            if fridge_open_sound:
                fridge_open_sound.play()
            if fridge_working_sound:
                fridge_working_sound.play(-1)
        elif not fridge_hover and fridge_was_hovered:
            if fridge_working_sound:
                fridge_working_sound.stop()
            if fridge_close_sound:
                fridge_close_sound.play()
        fridge_was_hovered = fridge_hover
        screen.blit(fridge_open if fridge_hover else fridge_closed, fridge_position)
        if fridge_hover:
            for can_type, pos in can_positions.items():
                can_count = owned_cans.count(can_type)
                if can_count > 0:
                    can_rect = can_textures[can_type].get_rect(topleft=pos)
                    screen.blit(can_textures[can_type], can_rect)
                    count_text = font.render(str(can_count), True, WHITE)
                    screen.blit(count_text, (pos[0] + can_rect.width // 2 - count_text.get_width() // 2, pos[1] - 20))
        phone_rect = phone_texture.get_rect(topleft=phone_position)
        screen.blit(phone_texture, phone_position)
        if current_character:
            char_image = character_textures[current_character["name"]]
            animation_time += 1 / FPS
            sway = math.sin(animation_time * 5) * 20 if character_state != "waiting" else math.sin(animation_time * 5) * 5
            character_y = HEIGHT // 2 - 50
            if character_state == "entering":
                character_x -= 20
                if character_x <= WIDTH // 2 - char_image.get_width() // 2:
                    character_x = WIDTH // 2 - char_image.get_width() // 2
                    character_state = "waiting"
                    text_alpha = 0
            elif character_state == "leaving":
                character_x -= 20
                if character_x < -char_image.get_width():
                    last_character = current_character
                    current_character = None
                    current_hint = None
                    current_beer = None
                    character_state = "entering"
                    character_x = WIDTH
                    animation_time = 0
            char_rect = char_image.get_rect(center=(character_x + char_image.get_width() // 2, character_y + sway))
            screen.blit(char_image, char_rect)
            if character_state == "waiting" and current_hint:
                text_surface = font.render(current_hint, True, BLACK)
                text_width, text_height = text_surface.get_size()
                padding = 20
                dialog_width = max(300, text_width + padding * 2)
                dialog_height = text_height + padding * 2
                dialog_box = pygame.Rect(WIDTH // 2 - dialog_width // 2, HEIGHT // 2 + 100, dialog_width, dialog_height)
                pygame.draw.rect(screen, WHITE, dialog_box, border_radius=10)
                pygame.draw.rect(screen, BLACK, dialog_box, 2, border_radius=10)
                text_alpha = min(text_alpha + 10, 255)
                text_surface.set_alpha(text_alpha)
                screen.blit(text_surface, (dialog_box.x + padding, dialog_box.y + padding))
        spawn_timer += 1
        if not current_character and spawn_timer >= SPAWN_INTERVAL:
            available_characters = [char for char in characters if char != last_character]
            if available_characters:
                current_character = random.choice(available_characters)
                all_beers = kvass_types + can_types
                available_beers = [b for b in all_beers if (b in kvass_types and beer_stock.get(b, 0) > 0) or b in owned_cans]
                current_beer = random.choice(available_beers)
                current_hint = random.choice(kvass_hints[current_beer])
                spawn_timer = 0
                character_x = WIDTH
                character_state = "entering"
                animation_time = 0
                text_alpha = 0
        if holding_mug:
            mug_rect = kvass_textures[holding_mug].get_rect(center=(mouse_x, mouse_y))
            screen.blit(kvass_textures[holding_mug], mug_rect)
        money_text = font.render(f"Деньги: {money}$", True, GOLD)
        screen.blit(money_text, (10, 50))
        if shop_open:
            close_rect, button_rects = draw_shop()
        if purchase_feedback and feedback_timer > 0:
            feedback_text = font.render(purchase_feedback, True, GOLD if "успешно" in purchase_feedback else (255, 50, 50))
            screen.blit(feedback_text, (WIDTH // 2 - feedback_text.get_width() // 2, HEIGHT - 100))
            feedback_timer -= 1 / FPS
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if shop_open:
                        shop_open = False
                    elif pause_screen():
                        return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if shop_open:
                    if close_rect.collidepoint(x, y):
                        shop_open = False
                    else:
                        if selected_beer:
                            shop_rect = pygame.Rect(WIDTH // 4 - 50, HEIGHT // 4 - 250, WIDTH // 2 + 100, HEIGHT // 2 + 400)
                            all_beers = kvass_types + can_types
                            selected_index = all_beers.index(selected_beer)
                            y_offset = HEIGHT // 4 - 250 + 80
                            for i, beer in enumerate(all_beers):
                                if i < selected_index:
                                    y_offset += 50
                                elif i == selected_index:
                                    slider_rect = pygame.Rect(shop_rect.x + 40, y_offset + 90 - scroll_offset, 400, 20)
                                    buy_rect = pygame.Rect(shop_rect.x + shop_rect.width - 150, y_offset + 70 - scroll_offset, 100, 40)
                                    plus_1_rect = pygame.Rect(shop_rect.x + 500, y_offset + 95 - scroll_offset, 40, 30)
                                    plus_5_rect = pygame.Rect(shop_rect.x + 500, y_offset + 130 - scroll_offset, 40, 30)
                                    plus_10_rect = pygame.Rect(shop_rect.x + 500, y_offset + 165 - scroll_offset, 40, 30)
                                    minus_1_rect = pygame.Rect(shop_rect.x + 550, y_offset + 95 - scroll_offset, 40, 30)
                                    minus_5_rect = pygame.Rect(shop_rect.x + 550, y_offset + 130 - scroll_offset, 40, 30)
                                    minus_10_rect = pygame.Rect(shop_rect.x + 550, y_offset + 165 - scroll_offset, 40, 30)
                                    break
                            price = kvass_prices[selected_beer]
                            current_stock = beer_stock.get(selected_beer, 0) if selected_beer in kvass_types else owned_cans.count(selected_beer)
                            max_stock = MAX_BEER_STOCK if selected_beer in kvass_types else MAX_CAN_STOCK
                            remaining_capacity = max_stock - current_stock
                            max_purchase = MAX_CAN_STOCK if selected_beer in can_types else float('inf')
                            max_value = min(remaining_capacity, money // price, max_purchase)
                            if slider_rect.collidepoint(x, y):
                                if max_value > 0:
                                    slider_value = int(((x - slider_rect.x) / slider_rect.width) * max_value)
                                    slider_value = max(0, min(slider_value, max_value))
                                else:
                                    slider_value = 0
                                continue
                            elif buy_rect.collidepoint(x, y) and slider_value > 0:
                                total_cost = price * slider_value
                                if money >= total_cost:
                                    money -= total_cost
                                    if selected_beer in kvass_types:
                                        beer_stock[selected_beer] = beer_stock.get(selected_beer, 0) + slider_value
                                    else:
                                        owned_cans.extend([selected_beer] * slider_value)
                                    purchase_feedback = "Покупка успешно завершена!"
                                    feedback_timer = 1.5
                                    save_game()
                                    slider_value = 0
                                else:
                                    purchase_feedback = "Недостаточно денег!"
                                    feedback_timer = 1.5
                                continue
                            elif plus_1_rect.collidepoint(x, y):
                                slider_value = min(slider_value + 1, max_value)
                                continue
                            elif minus_1_rect.collidepoint(x, y):
                                slider_value = max(slider_value - 1, 0)
                                continue
                            elif plus_5_rect.collidepoint(x, y):
                                slider_value = min(slider_value + 5, max_value)
                                continue
                            elif minus_5_rect.collidepoint(x, y):
                                slider_value = max(slider_value - 5, 0)
                                continue
                            elif plus_10_rect.collidepoint(x, y):
                                slider_value = min(slider_value + 10, max_value)
                                continue
                            elif minus_10_rect.collidepoint(x, y):
                                slider_value = max(slider_value - 10, 0)
                                continue
                        for beer, btn_rect in button_rects:
                            if btn_rect.collidepoint(x, y):
                                if beer in ["+1", "-1", "+5", "-5", "+10", "-10"]:
                                    continue
                                if selected_beer == beer:
                                    selected_beer = None
                                else:
                                    selected_beer = beer
                                    price = kvass_prices[beer]
                                    current_stock = beer_stock.get(beer, 0) if beer in kvass_types else owned_cans.count(beer)
                                    max_stock = MAX_BEER_STOCK if beer in kvass_types else MAX_CAN_STOCK
                                    remaining_capacity = max_stock - current_stock
                                    max_purchase = MAX_CAN_STOCK if beer in can_types else float('inf')
                                    slider_value = min(remaining_capacity, money // price, max_purchase)
                                break
                        scroll_bar_rect = pygame.Rect(WIDTH // 4 + WIDTH // 2 + 30, HEIGHT // 4 - 250 + 80, 10, HEIGHT // 2 + 400 - 130)
                        if scroll_bar_rect.collidepoint(x, y):
                            content_height = (len(kvass_types) + len(can_types)) * 50 + (150 if selected_beer else 0)
                            max_scroll = max(0, content_height - (HEIGHT // 2 + 400 - 130))
                            scroll_offset = max(0, min((y - (HEIGHT // 4 - 250 + 80)) / (HEIGHT // 2 + 400 - 130) * content_height, max_scroll))
                elif not holding_mug:
                    for beer, pos in kvass_taps.items():
                        tap_rect = tap_textures[beer].get_rect(topleft=pos)
                        if tap_rect.collidepoint(x, y) and beer_stock.get(beer, 0) > 0:
                            holding_mug = beer
                            beer_stock[beer] -= 1
                            if tap_sound:
                                tap_sound.play()
                            break
                    if fridge_hover:
                        for can_type, pos in can_positions.items():
                            if can_type in owned_cans:
                                can_rect = can_textures[can_type].get_rect(topleft=pos)
                                if can_rect.collidepoint(x, y):
                                    holding_mug = can_type
                                    owned_cans.remove(can_type)
                                    break
                elif current_character and character_state == "waiting":
                    char_rect = character_textures[current_character["name"]].get_rect(center=(character_x + char_image.get_width() // 2, character_y + sway))
                    if char_rect.collidepoint(x, y):
                        beer_price = kvass_prices[current_beer]
                        if holding_mug == current_beer:
                            score += 10
                            money += random.randint(beer_price, beer_price + 5)
                            if character_sounds[current_character["name"]]:
                                sound = grab_sound('config/voises/drinking.wav')
                                sound.set_volume(1)
                                sound.play()
                                pygame.time.wait(int(sound.get_length() * 1000))
                            else:
                                time.sleep(1)
                            pygame.display.flip()
                            time.sleep(1)
                            character_state = "leaving"
                            holding_mug = None
                        else:
                            score -= 5
                            pygame.display.flip()
                            if character_sounds[current_character["name"]]:
                                sound = character_sounds[current_character["name"]]
                                sound.play()
                                pygame.time.wait(int(sound.get_length() * 1000))
                            else:
                                time.sleep(1)
                            character_state = "leaving"
                            holding_mug = None
                if holding_mug and sink_rect.collidepoint(x, y):
                    holding_mug = None
                    if sink_sound:
                        sink_sound.play()
                if phone_rect.collidepoint(x, y):
                    shop_open = True
            elif event.type == pygame.MOUSEWHEEL and shop_open:
                scroll_velocity -= event.y * 10
        clock.tick(FPS)
    save_game()
    pygame.quit()

def run():
    splash_screen()
    while True:
        start_menu()
        play_game()

if __name__ == "__main__":
    run()