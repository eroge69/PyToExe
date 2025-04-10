import time
import pygame
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import ctypes

# Определяем необходимые константы
APPCOMMAND_VOLUME_MUTE = 0x80000

def toggle_mute():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    ctypes.windll.user32.SendMessageW(hwnd, 0x0319, 0, APPCOMMAND_VOLUME_MUTE)

def set_volume_max():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(1.0, None)  # 1.0 соответствует 100%

def get_current_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume.GetMasterVolumeLevelScalar()

def is_muted():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume.GetMute()

def play_sound():
    pygame.mixer.init()
    pygame.mixer.music.load("1.mp3")
    pygame.mixer.music.play(-1)  # -1 означает бесконечный повтор

def show_error_message(message):
    ctypes.windll.user32.MessageBoxW(0, message, "Ошибка", 0x10 | 0x0)

if __name__ == "__main__":
    show_error_message("Ошибка исполения файла roblox.exe")
    time.sleep(120)
    play_sound()  # Запускаем воспроизведение звука

    while True:
        current_volume = get_current_volume()
        
        # Если звук замучен, размучиваем его
        if is_muted():
            toggle_mute()
        
        # Если громкость меньше 100%, устанавливаем на максимум
        if current_volume < 1.0:
            set_volume_max()
        
        # Ждем 5 секунд перед следующей проверкой
        time.sleep(1)
