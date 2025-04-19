# -*- coding: utf-8 -*-
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from inference import get_model
from inference.core.exceptions import RoboflowAPINotAuthorizedError
import time

# Укажи Private API Key
API_KEY = "jnCXn6speF3WCN7X9KCU"  # Замени на свой Private API Key

try:
    # Загрузка модели
    model = get_model("emergency-vehicles-russia-gjfv1/4", api_key=API_KEY)
except RoboflowAPINotAuthorizedError as e:
    print("Ошибка: Неверный API-ключ. Проверь ключ и попробуй снова.")
    exit(1)
except Exception as e:
    print(f"Ошибка при загрузке модели: {e}")
    exit(1)

# Создаем корневое окно и скрываем его
root = tk.Tk()
root.withdraw()

# Открываем диалог выбора файла
video_path = filedialog.askopenfilename(
    title="Выберите видеофайл",
    filetypes=[
        ("Видео файлы", "*.mp4 *.avi *.mov"),
        ("Все файлы", "*.*")
    ]
)

if not video_path:
    print("Файл не выбран.")
    exit(1)

# Открытие видеофайла
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Ошибка: Не удалось открыть видео или камеру.")
    exit(1)

# Получаем FPS исходного видео
original_fps = cap.get(cv2.CAP_PROP_FPS)
frame_time = 1000 / original_fps  # Время на кадр в миллисекундах

print(f"FPS видео: {original_fps}")

# Добавляем глобальные переменные для отслеживания
last_emergency_detection = None
emergency_start_time = None
emergency_alert_shown = False
alert_start_time = None
DETECTION_THRESHOLD = 5.0  # Увеличиваем порог до 5 секунд
ALERT_DURATION = 2.0  # Длительность показа сообщения в секундах

def draw_prediction(frame, x, y, width, height, class_name, confidence):
    # Цвета в формате BGR
    box_color = (0, 140, 255)  # Оранжевый
    text_color = (255, 255, 255)  # Белый
    
    # Координаты прямоугольника
    x1 = x - width // 2
    y1 = y - height // 2
    x2 = x + width // 2
    y2 = y + height // 2
    
    # Толщина линий
    thickness = 2
    
    # Рисуем прямоугольник с закругленными углами
    cv2.line(frame, (x1, y1 + 10), (x1, y1), box_color, thickness)
    cv2.line(frame, (x1, y1), (x1 + 10, y1), box_color, thickness)
    
    cv2.line(frame, (x2 - 10, y1), (x2, y1), box_color, thickness)
    cv2.line(frame, (x2, y1), (x2, y1 + 10), box_color, thickness)
    
    cv2.line(frame, (x2, y2 - 10), (x2, y2), box_color, thickness)
    cv2.line(frame, (x2, y2), (x2 - 10, y2), box_color, thickness)
    
    cv2.line(frame, (x1 + 10, y2), (x1, y2), box_color, thickness)
    cv2.line(frame, (x1, y2), (x1, y2 - 10), box_color, thickness)
    
    # Подготовка текста
    text = f"{class_name} {confidence:.2f}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    
    # Получаем размеры текста
    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Создаем полупрозрачный фон для текста
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1 - text_height - 8), (x1 + text_width + 8, y1), box_color, -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    
    # Добавляем текст
    cv2.putText(frame, text, (x1 + 4, y1 - 5), font, font_scale, text_color, thickness)

def show_emergency_alert(frame):
    # Создаем полупрозрачный красный фон для предупреждения
    overlay = frame.copy()
    frame_height, frame_width = frame.shape[:2]
    
    # Параметры текста
    alert_text = u"ОБНАРУЖЕН АВТОМОБИЛЬ СПЕЦСЛУЖБ!"
    signal_text = u"ОЖИДАНИЕ СИГНАЛА ДЛЯ СВЕТОФОРА..."
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 1.2
    thickness = 2
    
    # Получаем размеры текста
    (text_width1, text_height1), _ = cv2.getTextSize(alert_text, font, font_scale, thickness)
    (text_width2, text_height2), _ = cv2.getTextSize(signal_text, font, font_scale, thickness)
    
    # Рисуем фон
    padding = 20
    total_height = text_height1 + text_height2 + 3 * padding
    
    cv2.rectangle(overlay, 
                 (0, 0),
                 (frame_width, total_height),
                 (0, 0, 200),  # Тёмно-красный цвет
                 -1)
    
    # Накладываем полупрозрачный фон
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Добавляем текст
    y_pos1 = padding + text_height1
    y_pos2 = 2 * padding + text_height1 + text_height2
    
    # Используем шрифт, который лучше поддерживает кириллицу
    cv2.putText(frame, alert_text,
                (frame_width // 2 - text_width1 // 2, y_pos1),
                font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
    
    cv2.putText(frame, signal_text,
                (frame_width // 2 - text_width2 // 2, y_pos2),
                font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

# Основной цикл обработки видео
start_time = time.time()
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    frame_count += 1
    
    try:
        # Применение модели к кадру
        results = model.infer(frame)
        
        emergency_detected = False
        
        # Обработка результатов
        for prediction in results:
            try:
                if hasattr(prediction, "predictions") and isinstance(prediction.predictions, list):
                    for nested_pred in prediction.predictions:
                        if all(hasattr(nested_pred, attr) for attr in ("x", "y", "width", "height", "class_name", "confidence")):
                            x = int(nested_pred.x)
                            y = int(nested_pred.y)
                            width = int(nested_pred.width)
                            height = int(nested_pred.height)
                            class_name = nested_pred.class_name
                            confidence = nested_pred.confidence
                            
                            if "ambulance" in class_name.lower() or "emergency" in class_name.lower():
                                emergency_detected = True
                            
                            draw_prediction(frame, x, y, width, height, class_name, confidence)
            except Exception as e:
                print(f"Ошибка при обработке предсказания: {e}")
                continue
        
        # Обработка обнаружения спецтранспорта
        current_time = time.time()
        
        if emergency_detected:
            if emergency_start_time is None:
                emergency_start_time = current_time
            elif not emergency_alert_shown and (current_time - emergency_start_time) >= DETECTION_THRESHOLD:
                emergency_alert_shown = True
                alert_start_time = current_time
        else:
            emergency_start_time = None
            
        if emergency_alert_shown:
            if alert_start_time is not None and (current_time - alert_start_time) <= ALERT_DURATION:
                show_emergency_alert(frame)
            else:
                emergency_alert_shown = False
                alert_start_time = None

        # Отображение кадра
        cv2.imshow("Video", frame)

        # Расчет задержки для поддержания правильного FPS
        elapsed_time = time.time() - start_time
        expected_frame_time = frame_count / original_fps
        
        # Ждем, если обработка идет быстрее, чем нужно
        wait_time = max(1, int(expected_frame_time - elapsed_time) * 1000)
        if cv2.waitKey(wait_time) & 0xFF == ord('q'):
            break
            
    except Exception as e:
        print(f"Ошибка при обработке кадра: {e}")
        break

# Освобождение ресурсов
cap.release()
cv2.destroyAllWindows()