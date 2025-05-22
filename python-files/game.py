import pygame
import sys
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игродейс: Викторина + Морской бой")

# Цвета
WHITE = (255, 255, 255)
BLUE = (70, 130, 180)
RED = (220, 20, 60)
BLACK = (0, 0, 0)
GREEN = (50, 205, 50)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Шрифты
title_font = pygame.font.SysFont('arial', 48, bold=True)
font = pygame.font.SysFont('arial', 32)
small_font = pygame.font.SysFont('arial', 24)

# Состояния игры
MENU = 0
CATEGORIES = 1
QUESTION = 2
RESULT = 3
PLACEMENT = 4  # Новое состояние - расстановка кораблей
BATTLE = 5
state = MENU

# Игровые переменные
score = 0
shots_earned = 0
current_category = ""
current_question = {}
selected_answer = None
is_correct = False
current_ship_size = 4  # Начинаем с 4-палубного
ship_orientation = "horizontal"  # Ориентация корабля
player_ships = []  # Координаты кораблей игрока

# Категории и вопросы (сокращённый вариант)
categories = {
    "Великие океаны": [
        {"question": "Какой океан самый большой по площади?", "answers": ["Тихий", "Атлантический", "Индийский", "Северный Ледовитый"], "correct": 0, "points": 1},
        {"question": "Какой океан омывает Антарктиду?", "answers": ["Южный", "Тихий", "Атлантический", "Индийский"], "correct": 0, "points": 1},
        {"question": "Какой пролив разделяет Тихий и Северный Ледовитый океаны?", "answers": ["Берингов", "Гибралтарский", "Магелланов", "Дрейка"], "correct": 0, "points": 2},
        {"question": "Какое течение в Атлантике самое мощное?", "answers": ["Гольфстрим", "Куросио", "Перуанское", "Северо-Атлантическое"], "correct": 0, "points": 2}
    ],
    "Знаменитые моря": [
        {"question": "Какое море самое солёное?", "answers": ["Красное", "Мёртвое", "Средиземное", "Чёрное"], "correct": 0, "points": 1},
        {"question": "Какое море не имеет берегов?", "answers": ["Саргассово", "Карибское", "Балтийское", "Охотское"], "correct": 0, "points": 1},
        {"question": "Почему Чёрное море называется 'чёрным'?", "answers": ["Из-за сероводорода на глубине", "Из-за цвета воды", "Из-за чёрного песка", "Из-за древнего названия"], "correct": 0, "points": 2},
        {"question": "Какое море древние греки называли 'Понт Аксинский'?", "answers": ["Чёрное море", "Эгейское море", "Адриатическое море", "Ионическое море"], "correct": 0, "points": 2}
    ],
    "Легендарные корабли": [
        {"question": "Как назывался флагман Колумба?", "answers": ["Санта-Мария", "Нинья", "Пинта", "Виктория"], "correct": 0, "points": 1},
        {"question": "Какой корабль затонул в 1912 году, столкнувшись с айсбергом?", "answers": ["Титаник", "Лузитания", "Британик", "Олимпик"], "correct": 0, "points": 1},
        {"question": "Какой русский крейсер участвовал в Цусимском сражении?", "answers": ["Аврора", "Варяг", "Петропавловск", "Рюрик"], "correct": 0, "points": 2},
        {"question": "Как назывался первый в мире атомный ледокол?", "answers": ["Ленин", "Арктика", "Сибирь", "Ямал"], "correct": 0, "points": 2}
    ],
    "Морские чудовища": [
        {"question": "Как зовут гигантского кальмара из легенд?", "answers": ["Кракен", "Левиафан", "Сцилла", "Гидро"], "correct": 0, "points": 1},
        {"question": "Какая рыба считается самой опасной для человека?", "answers": ["Белая акула", "Рыба-меч", "Мурена", "Барракуда"], "correct": 0, "points": 1},
        {"question": "Какой глубины достигает голубой кит при нырянии?", "answers": ["До 500 м", "До 1000 м", "До 200 м", "До 1500 м"], "correct": 0, "points": 2},
        {"question": "Какое существо имеет самый большой мозг среди беспозвоночных?", "answers": ["Осьминог", "Кальмар", "Медуза", "Наутилус"], "correct": 0, "points": 2}
    ],
    "Навигация и открытия": [
        {"question": "Кто первым совершил кругосветное плавание?", "answers": ["Магеллан", "Кук", "Дрейк", "Колумб"], "correct": 0, "points": 1},
        {"question": "Какой прибор помогает определять стороны света?", "answers": ["Компас", "Секстант", "Астролябия", "Хронометр"], "correct": 0, "points": 1},
        {"question": "Кто открыл морской путь в Индию?", "answers": ["Васко да Гама", "Колумб", "Магеллан", "Кабрал"], "correct": 0, "points": 2},
        {"question": "Как назывались корабли Кука в его первом плавании?", "answers": ["Индевор", "Резольюшен", "Дискавери", "Бигль"], "correct": 0, "points": 2}
    ],
    "Пираты и корсары": [
        {"question": "Как звали самого известного пирата Карибского моря?", "answers": ["Чёрная Борода", "Генри Морган", "Калико Джек", "Бартоломью Робертс"], "correct": 0, "points": 1},
        {"question": "Что такое 'Весёлый Роджер'?", "answers": ["Пиратский флаг", "Пиратский кодекс", "Пиратский напиток", "Пиратский танец"], "correct": 0, "points": 1},
        {"question": "Какой пират стал губернатором Ямайки?", "answers": ["Генри Морган", "Фрэнсис Дрейк", "Эдвард Тич", "Джек Рэкхем"], "correct": 0, "points": 2},
        {"question": "Как назывался корабль капитана Кидда?", "answers": ["Приключение", "Месть королевы Анны", "Золотая лань", "Чёрная жемчужина"], "correct": 0, "points": 2}
    ],
    "Кораблекрушения": [
        {"question": "Где затонул 'Титаник'?", "answers": ["У берегов Ньюфаундленда", "У берегов Ирландии", "В Средиземном море", "В Северном море"], "correct": 0, "points": 1},
        {"question": "Как называется наука о затонувших кораблях?", "answers": ["Подводная археология", "Океанография", "Гидрография", "Наутиология"], "correct": 0, "points": 1},
        {"question": "Какое судно стало самым массовым кораблекрушением в истории?", "answers": ["Вильгельм Густлофф", "Титаник", "Лузитания", "Армения"], "correct": 0, "points": 2},
        {"question": "Какой корабль называли 'непотопляемым' до 'Титаника'?", "answers": ["Адмирал Нахимов", "Британик", "Олимпик", "Императрица Ирландии"], "correct": 0, "points": 2}
    ],
    "Подводный мир": [
        {"question": "Какое самое глубокое место в океане?", "answers": ["Марианская впадина", "Жёлоб Тонга", "Филиппинский жёлоб", "Кермадек"], "correct": 0, "points": 1},
        {"question": "Как называется симбиоз рыбки и анемона?", "answers": ["Рыба-клоун", "Рыба-попугай", "Рыба-бабочка", "Рыба-хирург"], "correct": 0, "points": 1},
        {"question": "Какие рыбы строят 'сады' на дне?", "answers": ["Рыбы-попугаи", "Рыбы-ангелы", "Рыбы-клоуны", "Рыбы-попугаи"], "correct": 0, "points": 2},
        {"question": "Какой организм является самым долгоживущим в океане?", "answers": ["Губка", "Коралл", "Актиния", "Медуза"], "correct": 0, "points": 2}
    ],
    "Морские сражения": [
        {"question": "Какое сражение называют 'морским Бородино'?", "answers": ["Цусимское", "Трафальгарское", "Ютландское", "Лепанто"], "correct": 0, "points": 1},
        {"question": "Кто победил в битве при Трафальгаре?", "answers": ["Нельсон", "Вильнёв", "Коллингвуд", "Гравина"], "correct": 0, "points": 1},
        {"question": "Как назывался фрегат, потопивший 'Мерримак'?", "answers": ["Монитор", "Вирджиния", "Кеокук", "Галена"], "correct": 0, "points": 2},
        {"question": "Какое сражение стало крупнейшим морским боем ВМВ?", "answers": ["Лейте", "Мидвей", "Гуадалканал", "Коралловое море"], "correct": 0, "points": 2}
    ],
    "Порты и гавани": [
        {"question": "Какой порт называют 'морскими воротами Европы'?", "answers": ["Роттердам", "Гамбург", "Антверпен", "Гавр"], "correct": 0, "points": 1},
        {"question": "Где находится порт Вальпараисо?", "answers": ["Чили", "Перу", "Аргентина", "Бразилия"], "correct": 0, "points": 1},
        {"question": "Какой азиатский порт был 'жемчужиной Британской империи'?", "answers": ["Гонконг", "Сингапур", "Шанхай", "Бомбей"], "correct": 0, "points": 2},
        {"question": "Какой русский порт не замерзает зимой?", "answers": ["Мурманск", "Архангельск", "Владивосток", "Санкт-Петербург"], "correct": 0, "points": 2}
    ],
    "Морская техника": [
        {"question": "Что измеряет эхолот?", "answers": ["Глубину", "Скорость", "Температуру воды", "Солёность"], "correct": 0, "points": 1},
        {"question": "Как называется подводный аппарат для исследований?", "answers": ["Батискаф", "Гидролокатор", "Сонар", "Эхолот"], "correct": 0, "points": 1},
        {"question": "Какой корабль может перевозить другие корабли?", "answers": ["Док-корабль", "Контейнеровоз", "Танкер", "Балкер"], "correct": 0, "points": 2},
        {"question": "Что такое 'FPSO' в морской добыче нефти?", "answers": ["Плавучая установка", "Подводный трубопровод", "Морская платформа", "Нефтеналивной танкер"], "correct": 0, "points": 2}
    ],
    "Морские традиции": [
        {"question": "Почему моряки носят тельняшку?", "answers": ["Хорошо видно за бортом", "Традиция", "Удобно", "Защита от холода"], "correct": 0, "points": 1},
        {"question": "Что значит флаг, поднятый вверх ногами?", "answers": ["SOS", "Победа", "Траур", "Вызов"], "correct": 0, "points": 1},
        {"question": "Почему на кораблях свистят в свисток?", "answers": ["Отдать честь", "Позвать на обед", "Сигнал тревоги", "Разгонять чаек"], "correct": 0, "points": 2},
        {"question": "Как называется церемония пересечения экватора?", "answers": ["Посвящение в моряки", "Крещение", "Инициация", "Обряд перехода"], "correct": 0, "points": 2}
    ],
    "Полярные экспедиции": [
        {"question": "Кто достиг Южного полюса первым?", "answers": ["Амундсен", "Скотт", "Шеклтон", "Нансен"], "correct": 0, "points": 1},
        {"question": "Как назывался корабль Шеклтона?", "answers": ["Эндьюранс", "Дискавери", "Фрам", "Терра Нова"], "correct": 0, "points": 1},
        {"question": "Кто открыл Антарктиду?", "answers": ["Беллинсгаузен и Лазарев", "Кук", "Росс", "Уилкс"], "correct": 0, "points": 2},
        {"question": "Какой корабль первым прошёл Севморпуть за одну навигацию?", "answers": ["Сибиряков", "Челюскин", "Литке", "Красин"], "correct": 0, "points": 2}
    ],
    "Каналы и проливы": [
        {"question": "Какой канал соединяет Средиземное и Красное моря?", "answers": ["Суэцкий", "Панамский", "Кильский", "Волго-Донской"], "correct": 0, "points": 1},
        {"question": "Какой пролив разделяет Европу и Африку?", "answers": ["Гибралтарский", "Босфор", "Дарданеллы", "Баб-эль-Мандебский"], "correct": 0, "points": 1},
        {"question": "Какой канал самый длинный в мире?", "answers": ["Великий китайский", "Суэцкий", "Панамский", "Беломорско-Балтийский"], "correct": 0, "points": 2},
        {"question": "Какой пролив называют 'кладбищем кораблей'?", "answers": ["Бермудский треугольник", "Магелланов пролив", "Пролив Дрейка", "Малаккский пролив"], "correct": 0, "points": 2}
    ],
    "Морская геология": [
        {"question": "Как называется подводная гора?", "answers": ["Гайот", "Атолл", "Риф", "Холм"], "correct": 0, "points": 1},
        {"question": "Где находится 'Чёрный курильщик'?", "answers": ["Срединно-Атлантический хребет", "Марианская впадина", "Курило-Камчатский жёлоб", "Восточно-Тихоокеанское поднятие"], "correct": 0, "points": 1},
        {"question": "Как образуются атоллы?", "answers": ["На месте вулканов", "Из кораллов", "Из песка", "Из известняка"], "correct": 0, "points": 2},
        {"question": "Что такое 'абиссальные равнины'?", "answers": ["Глубоководные равнины", "Подводные горы", "Коралловые рифы", "Морские террасы"], "correct": 0, "points": 2}
    ],
    "Морская метеорология": [
        {"question": "Что такое 'глаз бури'?", "answers": ["Центр урагана", "Верхушка волны", "Пена на воде", "Облако над морем"], "correct": 0, "points": 1},
        {"question": "Как называется волна высотой более 30 метров?", "answers": ["Блуждающая волна", "Цунами", "Штормовая волна", "Приливная волна"], "correct": 0, "points": 1},
        {"question": "Что измеряет шкала Бофорта?", "answers": ["Силу ветра", "Высоту волн", "Глубину моря", "Температуру воды"], "correct": 0, "points": 2},
        {"question": "Как образуется цунами?", "answers": ["При землетрясениях", "От ветра", "От приливов", "От подводных взрывов"], "correct": 0, "points": 2}
    ],
    "Морская биология": [
        {"question": "Какое животное самое большое в мире?", "answers": ["Синий кит", "Кашалот", "Гигантский кальмар", "Китовая акула"], "correct": 0, "points": 1},
        {"question": "Как рыбы-прилипалы прикрепляются к акулам?", "answers": ["Присоской", "Крючками", "Липучкой", "Магнитом"], "correct": 0, "points": 1},
        {"question": "Какие рыбы могут менять пол?", "answers": ["Рыбы-попугаи", "Рыбы-клоуны", "Рыбы-бабочки", "Рыбы-ангелы"], "correct": 0, "points": 2},
        {"question": "Как медузы размножаются?", "answers": ["Почкованием", "Икрой", "Живорождением", "Делением"], "correct": 0, "points": 2}
    ],
    "Морское право": [
        {"question": "Что такое 'территориальные воды'?", "answers": ["12 миль от берега", "3 мили от берега", "200 миль от берега", "Весь шельф"], "correct": 0, "points": 1},
        {"question": "Что разрешает 'право мирного прохода'?", "answers": ["Проход через территориальные воды", "Рыболовство", "Добычу полезных ископаемых", "Военные учения"], "correct": 0, "points": 1},
        {"question": "Что такое 'ИМО'?", "answers": ["Международная морская организация", "Институт морских исследований", "Морская страховая компания", "Судостроительный альянс"], "correct": 0, "points": 2},
        {"question": "Что регулирует СОЛАС?", "answers": ["Безопасность мореплавания", "Экологию океана", "Рыболовные квоты", "Морские границы"], "correct": 0, "points": 2}
    ],
    "Морская кухня": [
        {"question": "Почему моряки ели лимоны?", "answers": ["От цинги", "Для вкуса", "От тошноты", "От жажды"], "correct": 0, "points": 1},
        {"question": "Что такое 'гальюн'?", "answers": ["Туалет на корабле", "Камбуз", "Кубрик", "Трюм"], "correct": 0, "points": 1},
        {"question": "Как называется кухня на корабле?", "answers": ["Камбуз", "Гальюн", "Кубрик", "Каморка"], "correct": 0, "points": 2},
        {"question": "Почему ром ассоциируется с пиратами?", "answers": ["Дезинфекция воды", "Дешёвый напиток", "Традиция", "Маскировка запаха"], "correct": 0, "points": 2}
    ],
    "Морские суеверия": [
        {"question": "Почему нельзя свистеть на корабле?", "answers": ["Вызовет шторм", "Разозлит капитана", "Примает чаек", "Спутает ветер"], "correct": 0, "points": 1},
        {"question": "Какая женщина приносит удачу кораблю?", "answers": ["Фигура на носу", "Жена капитана", "Кок", "Юнга"], "correct": 0, "points": 1},
        {"question": "Почему нельзя называть кроликов на корабле?", "answers": ["Неудача", "Обидятся", "Примают шторм", "Вызовут пожар"], "correct": 0, "points": 2},
        {"question": "Какой цвет считается несчастливым для моряков?", "answers": ["Жёлтый", "Красный", "Синий", "Зелёный"], "correct": 0, "points": 2}
    ]
}


# Параметры морского боя
GRID_SIZE = 10
CELL_SIZE = 30
SHIPS = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]  # Размеры кораблей
player_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
enemy_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
enemy_ships = []
player_shots = []
enemy_shots = []
game_over = False
battle_message = ""

# Кнопки
class Button:
    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=RED):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# Создаём кнопки
start_button = Button(WIDTH//2 - 100, HEIGHT//2, 200, 50, "СТАРТ")
next_button = Button(WIDTH//2 - 100, HEIGHT - 100, 200, 50, "ДАЛЕЕ")
back_button = Button(50, HEIGHT - 100, 150, 50, "НАЗАД")
battle_button = Button(WIDTH//2 - 100, HEIGHT - 150, 200, 50, "В БОЙ!")
rotate_button = Button(WIDTH - 200, HEIGHT - 100, 150, 50, "ПОВЕРНУТЬ")
done_button = Button(WIDTH - 200, HEIGHT - 100, 150, 50, "ГОТОВО")

# Функции для морского боя
def place_ships(grid):
    ships = []
    for size in SHIPS:
        placed = False
        while not placed:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            orientation = random.choice(["horizontal", "vertical"])
            
            if can_place_ship(grid, x, y, size, orientation):
                ship_coords = []
                for i in range(size):
                    if orientation == "horizontal":
                        grid[y][x + i] = 1
                        ship_coords.append((x + i, y))
                    else:
                        grid[y + i][x] = 1
                        ship_coords.append((x, y + i))
                ships.append(ship_coords)
                placed = True
    return ships

def can_place_ship(grid, x, y, size, orientation):
    if orientation == "horizontal":
        if x + size > GRID_SIZE:
            return False
        for i in range(max(0, x - 1), min(GRID_SIZE, x + size + 1)):
            for j in range(max(0, y - 1), min(GRID_SIZE, y + 2)):
                if grid[j][i] == 1:
                    return False
    else:
        if y + size > GRID_SIZE:
            return False
        for i in range(max(0, x - 1), min(GRID_SIZE, x + 2)):
            for j in range(max(0, y - 1), min(GRID_SIZE, y + size + 1)):
                if grid[j][i] == 1:
                    return False
    return True

def check_hit(grid, x, y):
    return grid[y][x] == 1

def check_sunk(grid, ships, x, y):
    for ship in ships:
        if (x, y) in ship:
            for coord in ship:
                if grid[coord[1]][coord[0]] != 2:  # 2 - попадание
                    return False
            return True
    return False

def draw_grid(surface, grid, offset_x, offset_y, hide_ships=False):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, WHITE, rect, 1)
            
            if grid[y][x] == 2:  # Попадание
                pygame.draw.rect(surface, RED, rect)
            elif grid[y][x] == 3:  # Промах
                pygame.draw.circle(surface, WHITE, rect.center, CELL_SIZE // 3)
            elif not hide_ships and grid[y][x] == 1:  # Корабль
                pygame.draw.rect(surface, BLUE, rect)

def draw_ship_preview(surface, x, y, size, orientation, offset_x, offset_y, valid):
    color = GREEN if valid else RED
    for i in range(size):
        if orientation == "horizontal":
            rect = pygame.Rect(offset_x + (x + i) * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        else:
            rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + (y + i) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 2)

# Инициализация морского боя
enemy_ships = place_ships(enemy_grid)

# Основной игровой цикл
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Обработка кнопок
        if state == MENU:
            start_button.check_hover(mouse_pos)
            if start_button.is_clicked(mouse_pos, event):
                state = CATEGORIES
        
        elif state == CATEGORIES:
            back_button.check_hover(mouse_pos)
            battle_button.check_hover(mouse_pos)
            
            if back_button.is_clicked(mouse_pos, event):
                state = MENU
            elif battle_button.is_clicked(mouse_pos, event) and shots_earned > 0:
                state = PLACEMENT  # Переходим к расстановке кораблей
            
            # Проверка клика по категориям
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, category in enumerate(categories.keys()):
                    row = i // 5
                    col = i % 5
                    cat_rect = pygame.Rect(100 + col * 180, 150 + row * 120, 160, 100)
                    if cat_rect.collidepoint(event.pos):
                        current_category = category
                        current_question = random.choice(categories[category])
                        state = QUESTION
        
        elif state == QUESTION:
            next_button.check_hover(mouse_pos)
            
            # Выбор ответа
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(4):
                    answer_rect = pygame.Rect(WIDTH//2 - 200, 250 + i*70, 400, 60)
                    if answer_rect.collidepoint(event.pos):
                        selected_answer = i
                        is_correct = (selected_answer == current_question["correct"])
                        if is_correct:
                            score += current_question["points"]
                            shots_earned += 1
                        state = RESULT
        
        elif state == RESULT:
            if next_button.is_clicked(mouse_pos, event):
                state = CATEGORIES
                selected_answer = None
        
        elif state == PLACEMENT:
            rotate_button.check_hover(mouse_pos)
            done_button.check_hover(mouse_pos)
            
            if rotate_button.is_clicked(mouse_pos, event):
                ship_orientation = "vertical" if ship_orientation == "horizontal" else "horizontal"
            
            if done_button.is_clicked(mouse_pos, event) and current_ship_size == 0:
                state = BATTLE
            if back_button.is_clicked(mouse_pos, event):
                state = MENU
            
            # Размещение кораблей
            if event.type == pygame.MOUSEBUTTONDOWN and current_ship_size > 0:
                grid_x = (mouse_pos[0] - (WIDTH//2 + 50)) // CELL_SIZE
                grid_y = (mouse_pos[1] - 150) // CELL_SIZE
                
                if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                    if can_place_ship(player_grid, grid_x, grid_y, current_ship_size, ship_orientation):
                        # Размещаем корабль
                        ship_coords = []
                        for i in range(current_ship_size):
                            if ship_orientation == "horizontal":
                                player_grid[grid_y][grid_x + i] = 1
                                ship_coords.append((grid_x + i, grid_y))
                            else:
                                player_grid[grid_y + i][grid_x] = 1
                                ship_coords.append((grid_x, grid_y + i))
                        player_ships.append(ship_coords)
                        
                        # Переходим к следующему кораблю
                        SHIPS.remove(current_ship_size)
                        if SHIPS:
                            current_ship_size = SHIPS[0] if SHIPS[0] != current_ship_size else SHIPS[1] if len(SHIPS) > 1 else SHIPS[0]
                        else:
                            current_ship_size = 0
        
        elif state == BATTLE:
            if event.type == pygame.MOUSEBUTTONDOWN and shots_earned > 0:
                grid_x = (mouse_pos[0] - 50) // CELL_SIZE
                grid_y = (mouse_pos[1] - 150) // CELL_SIZE
                
                if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE and (grid_x, grid_y) not in player_shots:
                    player_shots.append((grid_x, grid_y))
                    shots_earned -= 1
                    
                    if check_hit(enemy_grid, grid_x, grid_y):
                        enemy_grid[grid_y][grid_x] = 2
                        if check_sunk(enemy_grid, enemy_ships, grid_x, grid_y):
                            battle_message = "Вы потопили корабль!"
                        else:
                            battle_message = "Попадание!"
                    else:
                        enemy_grid[grid_y][grid_x] = 3
                        battle_message = "Промах!"
                if back_button.is_clicked(mouse_pos, event):
                    state = MENU
                    
                    # Ход компьютера
                    if not game_over:
                        x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                        while (x, y) in enemy_shots:
                            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                        
                        enemy_shots.append((x, y))
                        if check_hit(player_grid, x, y):
                            player_grid[y][x] = 2
                        else:
                            player_grid[y][x] = 3
    
    # Отрисовка
    screen.fill(BLACK)
    
    # Меню
    if state == MENU:
        title = title_font.render("ИГРОДЕЙС: Викторина + Морской бой", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        
        subtitle = font.render("Ответь на вопросы, чтобы получить выстрелы!", True, WHITE)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 300))
        
        start_button.draw(screen)
    
    # Выбор категории
    elif state == CATEGORIES:
        title = title_font.render("ВЫБЕРИТЕ КАТЕГОРИЮ", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Отрисовка категорий (5x4)
        for i, category in enumerate(categories.keys()):
            row = i // 5
            col = i % 5
            
            color = BLUE if i % 2 == 0 else GREEN
            cat_rect = pygame.Rect(100 + col * 180, 150 + row * 120, 160, 100)
            pygame.draw.rect(screen, color, cat_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, cat_rect, 2, border_radius=10)
            
            if len(category) > 12:
                parts = [category[:12], category[12:]]
                for p, part in enumerate(parts):
                    text = small_font.render(part, True, WHITE)
                    screen.blit(text, (cat_rect.centerx - text.get_width()//2, 
                                    cat_rect.centery - 10 + p*20))
            else:
                text = small_font.render(category, True, WHITE)
                screen.blit(text, (cat_rect.centerx - text.get_width()//2, 
                                cat_rect.centery - 10))
        
        back_button.draw(screen)
        battle_button.draw(screen)
        
        shots_text = font.render(f"Выстрелы: {shots_earned}", True, YELLOW)
        screen.blit(shots_text, (WIDTH - 200, HEIGHT - 100))
    
    # Вопрос
    elif state == QUESTION:
        cat_text = font.render(f"Категория: {current_category}", True, WHITE)
        screen.blit(cat_text, (50, 50))
        
        question_text = font.render(current_question["question"], True, WHITE)
        screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 150))
        
        for i, answer in enumerate(current_question["answers"]):
            color = BLUE
            if selected_answer is not None and i == selected_answer:
                color = RED if not is_correct else GREEN
            
            answer_rect = pygame.Rect(WIDTH//2 - 200, 250 + i*70, 400, 60)
            pygame.draw.rect(screen, color, answer_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, answer_rect, 2, border_radius=10)
            
            answer_text = font.render(answer, True, WHITE)
            screen.blit(answer_text, (answer_rect.centerx - answer_text.get_width()//2,
                                    answer_rect.centery - answer_text.get_height()//2))
    
    # Результат ответа
    elif state == RESULT:
        result_text = font.render("Правильно!" if is_correct else "Неправильно!", 
                                True, GREEN if is_correct else RED)
        screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 200))
        
        points_text = font.render(f"+{current_question['points']} очков" if is_correct else "+0 очков", 
                                True, WHITE)
        screen.blit(points_text, (WIDTH//2 - points_text.get_width()//2, 250))
        
        correct_text = font.render(f"Правильный ответ: {current_question['answers'][current_question['correct']]}", 
                                 True, WHITE)
        screen.blit(correct_text, (WIDTH//2 - correct_text.get_width()//2, 300))
        
        next_button.draw(screen)
    
    # Расстановка кораблей
    elif state == PLACEMENT:
        title = title_font.render("РАССТАНОВКА КОРАБЛЕЙ", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Поле игрока
        player_label = font.render("Ваше поле", True, GREEN)
        screen.blit(player_label, (WIDTH//2 + 50, 120))
        draw_grid(screen, player_grid, WIDTH//2 + 50, 150)
        
        # Инструкция
        if current_ship_size > 0:
            instruction = font.render(f"Разместите {current_ship_size}-палубный корабль", True, YELLOW)
            screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT - 200))
            
            # Превью корабля
            grid_x = (mouse_pos[0] - (WIDTH//2 + 50)) // CELL_SIZE
            grid_y = (mouse_pos[1] - 150) // CELL_SIZE
            
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                valid = can_place_ship(player_grid, grid_x, grid_y, current_ship_size, ship_orientation)
                draw_ship_preview(screen, grid_x, grid_y, current_ship_size, ship_orientation, WIDTH//2 + 50, 150, valid)
            
            rotate_button.draw(screen)
        else:
            instruction = font.render("Все корабли размещены!", True, GREEN)
            screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT - 200))
            done_button.draw(screen)
        
        # Статус
        status_text = font.render(f"Осталось кораблей: {len(SHIPS)}", True, WHITE)
        screen.blit(status_text, (50, HEIGHT - 100))
    
    # Морской бой
    elif state == BATTLE:
        title = title_font.render("МОРСКОЙ БОЙ", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Поле противника
        enemy_label = font.render("Противник", True, RED)
        screen.blit(enemy_label, (50, 120))
        draw_grid(screen, enemy_grid, 50, 150, True)
        
        # Поле игрока
        player_label = font.render("Ваш флот", True, GREEN)
        screen.blit(player_label, (WIDTH//2 + 50, 120))
        draw_grid(screen, player_grid, WIDTH//2 + 50, 150)
        
        # Статус
        status_text = font.render(f"Выстрелов осталось: {shots_earned}", True, YELLOW)
        screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, HEIGHT - 200))
        
        if battle_message:
            message_text = font.render(battle_message, True, WHITE)
            screen.blit(message_text, (WIDTH//2 - message_text.get_width()//2, HEIGHT - 250))
        
        back_button.draw(screen)
    
    # Отображение счёта
    score_text = font.render(f"Очки: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH - 150, 30))
    
    pygame.display.flip()
    clock = pygame.time.Clock()
    clock.tick(60)

pygame.quit()
sys.exit()