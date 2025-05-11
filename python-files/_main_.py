import pygame
from copy import deepcopy
from random import choice, randrange

# Инициализация pygame и микшера для звуков
pygame.init()
pygame.mixer.init()

W, H = 10, 20
TILE = 45
GAME_RES = W * TILE, H * TILE
RES = 750, 940
FPS = 60
sc = pygame.display.set_mode(RES)
game_sc = pygame.Surface(GAME_RES)
clock = pygame.time.Clock()

# Загрузка звуков
try:
    pygame.mixer.music.load('tetris_music.mp3')  # Фоновая музыка
    rotate_sound = pygame.mixer.Sound('block-rotate.mp3')  # Звук поворота
    drop_sound = pygame.mixer.Sound('block.mp3')  # Звук ускоренного падения
    clear_sound = pygame.mixer.Sound('end.mp3')  # Звук очистки линии
    gameover_sound = pygame.mixer.Sound('08 Game Over.mp3')  # Звук окончания игры

    # Установка громкости звуков
    pygame.mixer.music.set_volume(0.5)
    rotate_sound.set_volume(0.3)
    drop_sound.set_volume(0.3)
    clear_sound.set_volume(0.5)
    gameover_sound.set_volume(0.7)

    # Воспроизведение фоновой музыки в цикле
    pygame.mixer.music.play(-1)
except:
    print("Не удалось загрузить звуковые файлы. Игра будет без звуков.")
    sound_enabled = False
else:
    sound_enabled = True

grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
field = [[0 for i in range(W)] for j in range(H)]

# Начальные значения
initial_anim_speed = 60
initial_anim_limit = 2000
anim_count, anim_speed, anim_limit = 0, initial_anim_speed, initial_anim_limit
level = 1
lines_cleared = 0  # Общее количество очищенных линий
paused = False  # Флаг паузы

# Загрузка изображений
try:
    bg = pygame.image.load('bg.jpg').convert()
    game_bg = pygame.image.load('bg2.jpg').convert()
except:
    bg = pygame.Surface(RES)
    bg.fill((0, 0, 0))
    game_bg = pygame.Surface(GAME_RES)
    game_bg.fill((0, 0, 0))

# Загрузка шрифтов
try:
    main_font = pygame.font.Font('font/font.ttf', 65)
    font = pygame.font.Font('font/font.ttf', 45)
    small_font = pygame.font.Font('font/font.ttf', 30)
except:
    main_font = pygame.font.SysFont('Arial', 65, bold=True)
    font = pygame.font.SysFont('Arial', 45, bold=True)
    small_font = pygame.font.SysFont('Arial', 30, bold=True)

title_tetris = main_font.render('TETRIS', True, pygame.Color('darkorange'))
title_score = font.render('score:', True, pygame.Color('green'))
title_record = font.render('record:', True, pygame.Color('purple'))
title_level = font.render('level:', True, pygame.Color('blue'))
pause_text = font.render('PAUSED', True, pygame.Color('white'))

get_color = lambda: (randrange(30, 256), randrange(30, 256), randrange(30, 256))

figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}


def check_borders():
    for i in range(4):
        if figure[i].x < 0 or figure[i].x > W - 1:
            return False
        elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
            return False
    return True


def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')
        return '0'


def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))


def update_level():
    global level, anim_speed, anim_limit, initial_anim_speed, initial_anim_limit

    # Уровень увеличивается каждые 10 очищенных линий
    new_level = lines_cleared // 10 + 1

    if new_level != level:
        level = new_level
        # Увеличиваем скорость (уменьшаем anim_limit и увеличиваем anim_speed)
        anim_speed = initial_anim_speed + (level * 5)
        anim_limit = max(100, initial_anim_limit - (level * 100))  # Не даем упасть ниже 100

        if sound_enabled:
            clear_sound.play()  # Звук при повышении уровня


while True:
    record = get_record()
    dx, rotate = 0, False
    sc.blit(bg, (0, 0))
    sc.blit(game_sc, (20, 20))
    game_sc.blit(game_bg, (0, 0))

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Пауза по клавише Пробел
                paused = not paused
                if sound_enabled:
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
            if paused:
                continue  # Если игра на паузе, пропускаем обработку других клавиш

            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
                if sound_enabled: drop_sound.play()
            elif event.key == pygame.K_UP:
                rotate = True
                if sound_enabled: rotate_sound.play()

    if paused:
        # Отображаем экран паузы
        sc.blit(pause_text, (RES[0] // 2 - pause_text.get_width() // 2, RES[1] // 2 - pause_text.get_height() // 2))
        pygame.display.flip()
        clock.tick(FPS)
        continue

    # delay for full lines
    for i in range(lines):
        pygame.time.wait(200)

    # move x
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
    if not check_borders():
        figure = deepcopy(figure_old)

    # move y
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
        if not check_borders():
            for i in range(4):
                field[figure_old[i].y][figure_old[i].x] = color
            figure, color = next_figure, next_color
            next_figure, next_color = deepcopy(choice(figures)), get_color()
            anim_limit = max(100, initial_anim_limit - (level * 100))  # Обновляем anim_limit с учетом уровня

    # rotate
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
        if not check_borders():
            figure = deepcopy(figure_old)

    # check lines
    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            anim_speed += 3
            lines += 1
            lines_cleared += 1
            if sound_enabled: clear_sound.play()

    # Обновляем уровень
    update_level()

    # compute score (с бонусом за уровень)
    score += scores[lines] * level

    # draw grid
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]

    # draw figure
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_sc, color, figure_rect)

    # draw field
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)

    # draw next figure
    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + 380
        figure_rect.y = next_figure[i].y * TILE + 185
        pygame.draw.rect(sc, next_color, figure_rect)

    # draw titles
    sc.blit(title_tetris, (485, -10))
    sc.blit(title_score, (535, 780))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (550, 840))
    sc.blit(title_record, (525, 650))
    sc.blit(font.render(record, True, pygame.Color('gold')), (550, 710))
    sc.blit(title_level, (535, 570))
    sc.blit(font.render(str(level), True, pygame.Color('white')), (550, 630))
    sc.blit(small_font.render(f"Lines: {lines_cleared}", True, pygame.Color('white')), (535, 500))

    # game over
    for i in range(W):
        if field[0][i]:
            if sound_enabled:
                pygame.mixer.music.stop()
                gameover_sound.play()
            set_record(record, score)
            field = [[0 for i in range(W)] for i in range(H)]
            anim_count, anim_speed, anim_limit = 0, initial_anim_speed, initial_anim_limit
            score, lines_cleared, level = 0, 0, 1
            for i_rect in grid:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (20, 20))
                pygame.display.flip()
                clock.tick(200)
            if sound_enabled:
                pygame.mixer.music.play(-1)

    pygame.display.flip()
    clock.tick(FPS)