import os
import stat
import sys
import ctypes
import subprocess
import platform
import time
import Pygame
from pygame.locals import *

# Проверка платформы
if platform.system() != "Windows":
    print("Эта программа работает только на Windows!")
    sys.exit(1)

# Проверка и импорт Windows-специфичных модулей
try:
    import win32api
    import win32file
    from win32con import FILE_SHARE_READ, FILE_SHARE_WRITE
    from win32file import GENERIC_READ, OPEN_EXISTING
except ImportError:
    print("Требуется модуль pywin32. Установите: pip install pywin32")
    sys.exit(1)

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Конфигурация интерфейса
WIDTH, HEIGHT = 800, 600
FPS = 60
BG_COLOR = (240, 240, 245)
PRIMARY_COLOR = (50, 120, 200)
SECONDARY_COLOR = (70, 140, 220)
ERROR_COLOR = (220, 80, 60)
SUCCESS_COLOR = (80, 180, 100)
TEXT_COLOR = (30, 30, 30)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DVD Cleaner Pro")
clock = pygame.time.Clock()

# Шрифты
try:
    font_large = pygame.font.SysFont('Arial', 42, bold=True)
    font_medium = pygame.font.SysFont('Arial', 28)
    font_small = pygame.font.SysFont('Arial', 18)
except:
    font_large = pygame.font.Font(None, 42)
    font_medium = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 18)

class Button:
    def __init__(self, x, y, w, h, text, radius=8):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.radius = radius
        self.hover = False
        self.clicked = False
        self.disabled = False
    
    def draw(self, surface):
        color = SECONDARY_COLOR if self.hover and not self.disabled else PRIMARY_COLOR
        if self.disabled:
            color = (180, 180, 180)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=self.radius)
        
        text_surf = font_medium.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(mouse_pos) and not self.disabled
        
        self.clicked = False
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.hover:
                self.clicked = True

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def find_dvd_drive():
    try:
        drives = [drive for drive in win32api.GetLogicalDriveStrings().split('\x00') if drive]
        for drive in drives:
            if win32file.GetDriveType(drive) == win32file.DRIVE_CDROM:
                return drive.rstrip('\\')
        return None
    except Exception as e:
        print(f"Ошибка поиска диска: {e}")
        return None

def clean_dvd(drive_path):
    try:
        drive_path = drive_path + '\\'
        if not os.path.exists(drive_path):
            return False, "DVD диск не найден"
        
        # Удаление файлов
        for root, dirs, files in os.walk(drive_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    os.chmod(file_path, stat.S_IWRITE)
                    os.remove(file_path)
                except Exception as e:
                    print(f"Ошибка удаления файла {file_path}: {e}")
            
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    os.rmdir(dir_path)
                except Exception as e:
                    print(f"Ошибка удаления папки {dir_path}: {e}")

        # Форматирование через PowerShell
        ps_command = (
            f"$disk = Get-WmiObject -Class Win32_Volume | Where-Object {{ $_.DriveLetter -eq '{drive_path[0]}' }}; "
            "if ($disk) { $disk.Format('UDF', $false, 4096, '', $true) }"
        )
        
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True, "DVD успешно очищен!"
        else:
            return False, f"Ошибка форматирования: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "Таймаут операции"
    except Exception as e:
        return False, f"Ошибка очистки: {str(e)}"

def draw_progress_bar(surface, x, y, width, height, progress):
    pygame.draw.rect(surface, (220, 220, 220), (x, y, width, height), border_radius=4)
    inner_width = max(0, int((width - 4) * progress))
    pygame.draw.rect(surface, PRIMARY_COLOR, (x+2, y+2, inner_width, height-4), border_radius=4)

def show_admin_warning():
    screen.fill(BG_COLOR)
    admin_text = font_large.render("Требуются права администратора!", True, ERROR_COLOR)
    hint_text = font_medium.render("Запустите программу от имени администратора", True, TEXT_COLOR)
    exit_text = font_small.render("Нажмите любую кнопку для выхода", True, TEXT_COLOR)
    
    screen.blit(admin_text, (WIDTH//2 - admin_text.get_width()//2, HEIGHT//2 - 60))
    screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT//2 + 10))
    screen.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, HEIGHT//2 + 60))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                waiting = False
    pygame.quit()
    sys.exit(1)

def main():
    if not is_admin():
        show_admin_warning()

    dvd_drive = find_dvd_drive()
    clean_button = Button(WIDTH//2 - 150, HEIGHT//2 + 100, 300, 60, "Очистить DVD")
    status_text = "Готов к работе" if dvd_drive else "Вставьте DVD-RW диск"
    status_color = SUCCESS_COLOR if dvd_drive else ERROR_COLOR
    progress = 0
    cleaning = False
    success = False

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                running = False
        
        screen.fill(BG_COLOR)
        
        # Заголовок
        title = font_large.render("DVD Cleaner Pro", True, PRIMARY_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Информация о диске
        current_drive = find_dvd_drive()  # Обновляем статус диска каждый кадр
        if current_drive:
            drive_text = font_medium.render(f"Найден DVD-диск: {current_drive}", True, SUCCESS_COLOR)
            clean_button.disabled = False
        else:
            drive_text = font_medium.render("DVD-диск не найден", True, ERROR_COLOR)
            clean_button.disabled = True
        
        screen.blit(drive_text, (WIDTH//2 - drive_text.get_width()//2, 180))
        
        # Статус
        status = font_medium.render(status_text, True, status_color)
        screen.blit(status, (WIDTH//2 - status.get_width()//2, 240))
        
        # Прогресс бар
        if cleaning:
            draw_progress_bar(screen, WIDTH//2 - 200, 300, 400, 30, progress)
            progress = min(progress + 0.01, 1.0)
            
            if progress >= 1.0:
                cleaning = False
                status_text = "Готово!" if success else "Ошибка!"
                status_color = SUCCESS_COLOR if success else ERROR_COLOR
        
        # Кнопка
        clean_button.update(events)
        clean_button.draw(screen)
        
        if clean_button.clicked and current_drive and not cleaning:
            cleaning = True
            progress = 0
            status_text = "Идет очистка..."
            status_color = TEXT_COLOR
            pygame.display.flip()
            
            success, message = clean_dvd(current_drive)
            status_text = message
            status_color = SUCCESS_COLOR if success else ERROR_COLOR
            dvd_drive = find_dvd_drive()  # Обновляем статус диска
        
        # Подсказка
        hint = font_small.render("Программа для очистки перезаписываемых DVD-дисков (DVD-RW/DVD+RW)", True, (150, 150, 150))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()