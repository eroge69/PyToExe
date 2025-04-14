import cv2
import numpy as np
from collections import defaultdict, deque
from inference import get_model
import tkinter as tk
from tkinter import filedialog
import os
import time
import psutil
import gc
from math import sqrt
from datetime import datetime, timedelta

class TrafficAnalyzer:
    def __init__(self):
        self.model = None
        self.cap = None
        self.track_history = defaultdict(lambda: {
            'positions': deque(maxlen=30),
            'stopped_since': None,
            'last_detected': time.time(),
            'speed_history': deque(maxlen=5),
            'direction_history': deque(maxlen=3)
        })
        
        # Настройки производительности
        self.target_fps = 20
        self.frame_skip = 0
        self.last_cpu_check = time.time()
        self.cpu_check_interval = 5
        self.last_frame_time = time.time()
        self.fps = 0
        self.frame_counter = 0
        self.fps_update_interval = 1.0
        self.last_gc_run = time.time()
        
        # Параметры детекции
        self.STOPPED_SPEED_THRESHOLD = 0.3  # пикселей/кадр
        self.MIN_CONFIDENCE = 0.5
        
        # Параметры пробок
        self.JAM_VEHICLE_THRESHOLD = 5
        self.JAM_TIME_THRESHOLD = 30  # секунд
        self.JAM_AREA_RADIUS = 100  # пикселей
        
        # Параметры ДТП
        self.ACCIDENT_STOP_TIME = 60  # 1 минута в секундах (для теста)
        self.ACCIDENT_DISTANCE_THRESHOLD = 30
        self.ACCIDENT_AREA_RADIUS = 60
        self.accident_zones = []
        self.accident_cooldown = 300  # 5 минут
        
        # Настройки отображения
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.colors = {
            'vehicle': (0, 255, 0),
            'jam': (0, 215, 255),
            'accident': (0, 0, 255),
            'warning': (0, 165, 255),
            'info_bg': (20, 20, 20),
            'fps': (0, 255, 255)
        }

    def load_model(self):
        """Загружает модель детекции"""
        try:
            self.model = get_model("emergency-vehicles-russia-gjfv1/4", 
                                 api_key="jnCXn6speF3WCN7X9KCU")
            return True
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            return False

    def select_video(self):
        """Открывает диалог выбора видеофайла"""
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Выберите видеофайл",
            filetypes=[("Видео файлы", "*.mp4 *.avi *.mov *.mkv")]
        )
        root.destroy()
        return file_path

    def adjust_processing(self):
        """Регулирует нагрузку на CPU"""
        now = time.time()
        
        if now - self.last_cpu_check > self.cpu_check_interval:
            self.last_cpu_check = now
            cpu_percent = psutil.cpu_percent()
            
            if cpu_percent > 80:
                self.frame_skip = min(3, self.frame_skip + 1)
            elif cpu_percent < 60 and self.frame_skip > 0:
                self.frame_skip -= 1

    def _clean_old_tracks(self, max_age_seconds=30):
        """Очищает старые треки"""
        current_time = time.time()
        to_delete = [
            vid for vid, data in self.track_history.items()
            if (current_time - data['last_detected']) > max_age_seconds
        ]
        for vid in to_delete:
            del self.track_history[vid]

    def _update_fps(self):
        """Обновляет расчет FPS"""
        now = time.time()
        self.frame_counter += 1
        
        if now - self.last_frame_time >= self.fps_update_interval:
            self.fps = self.frame_counter / (now - self.last_frame_time)
            self.frame_counter = 0
            self.last_frame_time = now

    def _draw_vehicle_marker(self, frame, x, y, w, h, is_stopped=False):
        """Отрисовка маркера транспортного средства"""
        color = self.colors['accident'] if is_stopped else self.colors['vehicle']
        thickness = 2 if is_stopped else 1
        
        cv2.rectangle(frame, (x-w//2, y-h//2), (x+w//2, y+h//2), color, thickness)
        return frame

    def _process_detections(self, frame, results):
        """Обрабатывает результаты детекции"""
        current_time = time.time()
        
        for pred in results:
            if not hasattr(pred, "predictions"):
                continue
                
            for obj in pred.predictions:
                if not (hasattr(obj, "x") and hasattr(obj, "confidence")):
                    continue
                    
                if obj.confidence < self.MIN_CONFIDENCE:
                    continue
                
                x, y, w, h = int(obj.x), int(obj.y), int(obj.width), int(obj.height)
                vehicle_id = hash((x, y, obj.confidence))
                
                vehicle_data = self.track_history[vehicle_id]
                vehicle_data['positions'].append((x, y))
                vehicle_data['last_detected'] = current_time
                
                # Расчет скорости
                if len(vehicle_data['positions']) >= 2:
                    prev_pos = vehicle_data['positions'][-2]
                    curr_pos = vehicle_data['positions'][-1]
                    dx = curr_pos[0] - prev_pos[0]
                    dy = curr_pos[1] - prev_pos[1]
                    speed = sqrt(dx*dx + dy*dy)
                    vehicle_data['speed_history'].append(speed)
                    
                    # Проверка на остановку
                    avg_speed = np.mean(vehicle_data['speed_history']) if vehicle_data['speed_history'] else 0
                    if avg_speed < self.STOPPED_SPEED_THRESHOLD:
                        if vehicle_data['stopped_since'] is None:
                            vehicle_data['stopped_since'] = current_time
                    else:
                        vehicle_data['stopped_since'] = None
                
                # Отрисовка с учетом статуса остановки
                is_long_stop = vehicle_data['stopped_since'] is not None and \
                              (current_time - vehicle_data['stopped_since']) > self.ACCIDENT_STOP_TIME
                frame = self._draw_vehicle_marker(frame, x, y, w, h, is_long_stop)
        
        if self.frame_counter % 10 == 0:
            self._clean_old_tracks(30)
        
        return frame

    def _detect_jams(self, current_time):
        """Детектирует пробки на основе скопления транспортных средств"""
        active_vehicles = [
            data for data in self.track_history.values() 
            if current_time - data['last_detected'] < 2 and len(data['positions']) > 1
        ]
        
        if len(active_vehicles) < self.JAM_VEHICLE_THRESHOLD:
            return False
            
        # Простая проверка средней скорости
        avg_speed = np.mean([np.mean(data['speed_history']) for data in active_vehicles if data['speed_history']])
        return avg_speed < self.STOPPED_SPEED_THRESHOLD * 2

    def _detect_accidents(self, frame, current_time):
        """Детектирует ДТП по долгой остановке и близости машин"""
        stopped_vehicles = [
            (vid, data) for vid, data in self.track_history.items()
            if data['stopped_since'] is not None and 
               (current_time - data['stopped_since']) > self.ACCIDENT_STOP_TIME and
               len(data['positions']) > 1
        ]
        
        # Проверяем близость остановленных машин
        for i in range(len(stopped_vehicles)):
            for j in range(i+1, len(stopped_vehicles)):
                vid1, data1 = stopped_vehicles[i]
                vid2, data2 = stopped_vehicles[j]
                
                pos1 = data1['positions'][-1]
                pos2 = data2['positions'][-1]
                distance = sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)
                
                if distance < self.ACCIDENT_DISTANCE_THRESHOLD:
                    center = ((pos1[0]+pos2[0])//2, (pos1[1]+pos2[1])//2)
                    
                    # Проверяем, нет ли уже такой зоны ДТП
                    existing_zone = None
                    for zone in self.accident_zones:
                        zone_center = zone['center']
                        dist = sqrt((center[0]-zone_center[0])**2 + (center[1]-zone_center[1])**2)
                        if dist < self.ACCIDENT_AREA_RADIUS:
                            existing_zone = zone
                            break
                    
                    if existing_zone:
                        existing_zone['time'] = current_time
                    else:
                        self.accident_zones.append({
                            'center': center,
                            'time': current_time,
                            'vehicles': [vid1, vid2]
                        })
        
        # Удаляем старые зоны ДТП
        self.accident_zones = [
            zone for zone in self.accident_zones 
            if current_time - zone['time'] < self.accident_cooldown
        ]
        
        # Визуализация ДТП
        for zone in self.accident_zones:
            center = tuple(map(int, zone['center']))
            cv2.circle(frame, center, self.ACCIDENT_AREA_RADIUS, self.colors['accident'], 2)
            cv2.putText(frame, "ACCIDENT", (center[0]-40, center[1]-10), 
                       self.font, 0.7, self.colors['accident'], 2)

    def _draw_status(self, frame, jam_detected):
        """Отрисовывает статусную панель"""
        status_bar = np.zeros((40, frame.shape[1], 3), dtype=np.uint8)
        status_bar[:] = self.colors['info_bg']
        
        # Информация о FPS
        cv2.putText(status_bar, f"FPS: {self.fps:.1f}", (10, 25), 
                   self.font, 0.6, self.colors['fps'], 1)
        
        # Информация о пробке
        jam_text = "TRAFFIC JAM" if jam_detected else "CLEAR"
        jam_color = self.colors['jam'] if jam_detected else (100, 255, 100)
        cv2.putText(status_bar, jam_text, (frame.shape[1]//2 - 50, 25), 
                   self.font, 0.6, jam_color, 1)
        
        # Информация о ДТП
        accident_text = "ACCIDENT DETECTED" if self.accident_zones else "NO ACCIDENT"
        accident_color = self.colors['accident'] if self.accident_zones else (100, 255, 100)
        cv2.putText(status_bar, accident_text, (frame.shape[1] - 200, 25), 
                   self.font, 0.6, accident_color, 1)
        
        frame[0:40, 0:frame.shape[1]] = status_bar
        return frame

    def process_video(self, video_path):
        """Основной цикл обработки видео"""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print("Ошибка открытия видео")
            return
            
        # Сбрасываем состояние
        self.track_history.clear()
        self.accident_zones = []
        
        print(f"Обработка видео: {video_path}")
        print("Нажмите 'q' для выхода")
        
        try:
            while True:
                start_time = time.time()
                
                # Пропускаем кадры согласно настройке frame_skip
                for _ in range(self.frame_skip + 1):
                    ret, frame = self.cap.read()
                    if not ret:
                        break
                
                if not ret:
                    break
                    
                # Регулировка нагрузки
                self.adjust_processing()
                
                # Детекция объектов
                if self.frame_skip <= 1:
                    try:
                        results = self.model.infer(frame)
                        frame = self._process_detections(frame, results)
                        
                        # Детекция пробок
                        jam_detected = self._detect_jams(time.time())
                        
                        # Детекция ДТП
                        self._detect_accidents(frame, time.time())
                        
                        # Отрисовка статуса
                        frame = self._draw_status(frame, jam_detected)
                    except Exception as e:
                        print(f"Ошибка обработки: {e}")
                
                # Обновляем FPS
                self._update_fps()
                
                # Показ кадра
                cv2.imshow("Traffic Analyzer", frame)
                
                # Обработка клавиши выхода
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # Поддержание стабильного FPS
                processing_time = time.time() - start_time
                target_time = 1.0 / self.target_fps
                if processing_time < target_time:
                    time.sleep(max(0, target_time - processing_time))
                    
        finally:
            self.cap.release()
            cv2.destroyAllWindows()

def main():
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    os.environ['OMP_NUM_THREADS'] = '1'
    
    analyzer = TrafficAnalyzer()
    
    if not analyzer.load_model():
        return
        
    video_path = analyzer.select_video()
    if not video_path:
        print("Видео не выбрано")
        return
        
    analyzer.process_video(video_path)

if __name__ == "__main__":
    main()