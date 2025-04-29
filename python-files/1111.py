import pyautogui
import time
from datetime import datetime

def click_at_specific_time(target_hour, target_minute, target_second, target_microsecond):
    # Бесконечный цикл для постоянной проверки времени
    while True:
        # Получаем текущее время с точностью до миллисекунд
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        current_second = now.second
        current_microsecond = now.microsecond
        
        # Проверяем, совпадает ли текущее время с целевым
        if (current_hour == target_hour and
            current_minute == target_minute and
            current_second == target_second and
            current_microsecond // 1000 == target_microsecond):
            pyautogui.click()  # Клик мышью
            print(f"Клик выполнен в {now.strftime('%H:%M:%S')}.{now.microsecond // 1000}")
            time.sleep(1)  # Ждем 1 секунду, чтобы избежать повторных кликов в пределах одной секунды
        else:
            # Проверяем каждую миллисекунду
            time.sleep(0.001)

# Пример: кликать каждый день в 15:30:10.123 (час:минута:секунда.миллисекунда)
target_hour = 15
target_minute = 30
target_second = 10
target_microsecond = 123  # 123 миллисекунды

click_at_specific_time(target_hour, target_minute, target_second, target_microsecond)