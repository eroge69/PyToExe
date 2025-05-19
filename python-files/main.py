import pygame
import random
import os

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 900, 700
FPS = 60
TIME_LIMIT = 15  # Время для режима "Временной вызов"

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Образовательный Квест")


# Загрузка изображений и звуков
def load_image(name):
    try:
        return pygame.image.load(os.path.join('sprites', name))
    except pygame.error as e:
        print(f"Ошибка: Не удалось загрузить изображение {name}. {e}")
        return None


def load_sound(name):
    try:
        return pygame.mixer.Sound(os.path.join('sounds', name))
    except pygame.error as e:
        print(f"Ошибка: Не удалось загрузить звук {name}. {e}")
        return None

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

path = resource_path(os.path.join('Folder', 'image.png'))
img = pygame.image.load(path)
path = resource_path(os.path.join('Folder', 'music.png'))
msc = pygame.music.load(path)
# Загрузить все необходимые ресурсы
background_image = load_image('background.png')
player_image = load_image('player.png')
correct_effect_image = load_image('correct.png')
wrong_effect_image = load_image('wrong.png')

correct_sound = load_sound('correct.wav')
wrong_sound = load_sound('wrong.wav')

# Проверка загруженных ресурсов
resources_loaded = all([
    background_image,
    player_image,
    correct_effect_image,
    wrong_effect_image,
    correct_sound,
    wrong_sound
])

if not resources_loaded:
    print("Недостаточно ресурсов для запуска игры.")
    pygame.quit()
    exit()

# Настройка шрифтов
font = pygame.font.Font(None, 36)


# Класс для игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5
        self.health = 3

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        self.rect.clamp_ip(screen.get_rect())


# Класс вопросов
class Question:
    def __init__(self, question, options, answer, fact=None):
        self.question = question
        self.options = options
        self.answer = answer
        self.fact = fact


questions = [
    Question("Что такое Земля?", ["Планета", "Звезда", "Спутник"], "Планета", "Земля — третья планета от Солнца."),
    Question("Кто разработал теорию относительности?", ["Ньютон", "Эйнштейн", "Кеплер"], "Эйнштейн", "Эйнштейн опубликовал теорию в 1905 году."),
    Question("Сколько континентов на Земле?", ["5", "6", "7"], "7", "Семь континентов: Азия, Африка, Северная Америка, Южная Америка, Антарктида, Европа и Австралия."),
    Question("Какой газ необходим для дыхания?", ["Кислород", "Азот", "Углекислый газ"], "Кислород", "Кислород составляет около 21% атмосферы."),
    Question("Сколько времени уходит на получение солнечного света до Земли?", ["8 минут", "30 минут", "24 часа"], "8 минут", "Свет от Солнца доходит до Земли за примерно 8 минут."),
    Question("Что является самой большой планетой в нашей солнечной системе?", ["Земля", "Юпитер", "Сатурн"], "Юпитер", "Юпитер — это газовый гигант с более чем 70 спутниками."),
    Question("На каком континенте находится пустыня Сахара?", ["Африка", "Азия", "Австралия"], "Африка", "Сахара — самая большая горячая пустыня в мире."),
    Question("Какой элемент имеет химический символ 'H'?", ["Гелий", "Водород", "Кислород"], "Водород", "Водород — самый легкий элемент в периодической таблице."),
    Question("Сколько материков на Земле?", ["6", "7", "8"], "7", "Семь материков: Азия, Африка, Северная Америка, Южная Америка, Антарктида, Европа и Австралия."),
    Question("Какой океан самый большой?", ["Атлантический", "Индийский", "Тихий"], "Тихий", "Тихий океан занимает около 63 миллионов квадратных миль."),
    Question("Какое животное является самым крупным на планете?", ["Синий кит", "Африканский слон", "Кашалот"], "Синий кит", "Синие киты могут достигать длины до 30 метров."),
    Question("Какой планет является самой близкой к Земле?", ["Венера", "Марс", "Меркурий"], "Венера", "Венера иногда называется 'сестрой Земли' из-за схожести размеров."),
    Question("Какой газ преобладает в атмосфере Земли?", ["Кислород", "Азот", "Углекислый газ"], "Азот", "Азот составляет около 78% от всей атмосферы."),
    Question("Что такое самый яркий объект на ночном небе?", ["Луна", "Солнце", "Звезда"], "Луна", "Луна — самый яркий объект, видимый с Земли в ночное время."),
    Question("Кто является автором картины 'Мона Лиза'?", ["Ван Гог", "Дали", "Да Винчи"], "Да Винчи", "Мона Лиза написана Леонардо да Винчи в начале 1500-х годов."),
    Question("Как называются три состояния материи?", ["Твердое, жидкое, газообразное", "Твердое, афинное, газообразное", "Жидкое, газообразное, плазма"], "Твердое, жидкое, газообразное", "Три состояния материи — это твердые тела, жидкости и газы."),
    Question("В каком году человек впервые высадился на Луну?", ["1969", "1971", "1965"], "1969", "Астронавты миссии Apollo 11 высадились на Луне в 1969 году."),
]


# Класс эффектов для анимации
class Effect(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.lifetime = 30  # Количество кадров, на которое появится эффект

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


# Основной класс игры
class Game:
    def __init__(self):
        self.running = True
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.current_question = None
        self.score = 0
        self.show_question = False
        self.effects = pygame.sprite.Group()
        self.mode = "Normal"  # Режим игры
        self.time_remaining = TIME_LIMIT

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.show_question:
                    self.check_answer(event.key)

    def update(self):
        self.all_sprites.update()
        self.effects.update()

        if self.mode == "TimeTrial":
            if self.time_remaining > 0:
                self.time_remaining -= 1 / FPS  # Уменьшение времени оставшегося
            else:
                self.running = False  # Закончить игру при истечении времени

        if not self.current_question and len(questions) > 0:
            self.current_question = random.choice(questions)
            questions.remove(self.current_question)
            self.show_question = True

    def check_answer(self, key):
        answer_index = key - pygame.K_1
        if self.current_question and 0 <= answer_index < len(self.current_question.options):
            if self.current_question.options[answer_index] == self.current_question.answer:
                self.score += 1
                self.spawn_effect(correct_effect_image)
                correct_sound.play()
                self.show_fact()  # Показать интересный факт
            else:
                self.player.health -= 1
                self.spawn_effect(wrong_effect_image)
                wrong_sound.play()

            # Удаляем вопрос после ответа
            self.show_question = False
            self.current_question = None

            if self.player.health <= 0:
                self.running = False  # Игра окончена

    def spawn_effect(self, effect_image):
        if effect_image:  # Проверка, существует ли эффект
            effect_sprite = Effect(effect_image)
            self.effects.add(effect_sprite)

    def show_fact(self):
        if self.current_question.fact:
            fact_text = font.render(self.current_question.fact, True, BLACK)
            screen.blit(fact_text, (50, 400))
            pygame.display.flip()
            pygame.time.delay(3000)  # Показать факт на 3 секунды

    def draw(self):
        screen.fill(WHITE)  # Очистка экрана
        if background_image:  # Проверка наличия фона
            screen.blit(background_image, (0, 0))
        self.all_sprites.draw(screen)
        self.effects.draw(screen)

        if self.current_question and self.show_question:
            question_text = font.render(self.current_question.question, True, BLACK)
            screen.blit(question_text, (50, 50))
            for i, option in enumerate(self.current_question.options):
                option_text = font.render(f"{i + 1}. {option}", True, BLACK)
                screen.blit(option_text, (50, 100 + i * 40))

        # Отображение счета, здоровья и времени
        score_text = font.render(f"Очки: {self.score}", True, GREEN)
        health_text = font.render(f"Здоровье: {self.player.health}", True, RED)

        screen.blit(score_text, (50, HEIGHT - 150))
        screen.blit(health_text, (50, HEIGHT - 100))

        if self.mode == "TimeTrial":
            time_text = font.render(f"Время: {int(self.time_remaining)} сек", True, BLACK)
            screen.blit(time_text, (WIDTH - 200, 20))

        if self.player.health <= 0:
            self.draw_game_over()

        pygame.display.flip()

    def draw_game_over(self):
        game_over_text = font.render("Игра окончена! Попробуйте снова!", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

        restart_text = font.render("Нажмите 'R' для перезапуска", True, BLACK)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 40))

        # Обработка нажатия 'R' для перезапуска игры
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.__init__()  # Перезапуск игры

    # Экран меню
def show_menu():
        menu_running = True
        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            screen.fill(WHITE)
            title_text = font.render("Образовательный Квест", True, BLACK)
            normal_mode_text = font.render("Нажмите '1' для обычного режима", True, BLACK)
            time_trial_mode_text = font.render("Нажмите '2' для временного вызова", True, BLACK)
            exit_text = font.render("Нажмите 'ESC' для выхода", True, BLACK)

            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
            screen.blit(normal_mode_text, (WIDTH // 2 - normal_mode_text.get_width() // 2, 200))
            screen.blit(time_trial_mode_text, (WIDTH // 2 - time_trial_mode_text.get_width() // 2, 250))
            screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, 300))

            pygame.display.flip()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                game = Game()
                game.run()
            elif keys[pygame.K_2]:
                game = Game()
                game.mode = "TimeTrial"  # Установка режима
                game.run()
            elif keys[pygame.K_ESCAPE]:
                menu_running = False

# Запуск меню
if __name__ == "__main__":
    show_menu()
    pygame.quit()