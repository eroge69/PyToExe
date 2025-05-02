import ctypes
from ctypes import wintypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    print("Translated: [INFO] Установлен режим DPI Awareness: System Aware (Mode 1)")
except AttributeError:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        print("Translated: [INFO] Установлен режим DPI Awareness через SetProcessDPIAware()")
    except AttributeError:
        print("Translated: [WARN] Установка DPI awareness не удалась.")

import time
import threading
import numpy as np
from PIL import Image, ImageGrab, ImageTk
import keyboard
import interception
import random
import math
import cv2
from sklearn.cluster import KMeans
import os, sys
import traceback

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

PREVIEW_WIDTH = 350
PREVIEW_HEIGHT = 250

try:
    _user32 = ctypes.WinDLL('user32', use_last_error=True)

    _GetWindowLongW = _user32.GetWindowLongW
    _GetWindowLongW.restype = wintypes.LONG
    _GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]

    _SetWindowLongW = _user32.SetWindowLongW
    _SetWindowLongW.restype = wintypes.LONG
    _SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LONG]

    _SetLayeredWindowAttributes = _user32.SetLayeredWindowAttributes
    _SetLayeredWindowAttributes.restype = wintypes.BOOL
    _SetLayeredWindowAttributes.argtypes = [wintypes.HWND, wintypes.COLORREF, wintypes.BYTE, wintypes.DWORD]

    _SetWindowPos = _user32.SetWindowPos
    _SetWindowPos.restype = wintypes.BOOL
    _SetWindowPos.argtypes = [
        wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int, wintypes.UINT
    ]
    HWND_TOPMOST = -1
    HWND_NOTOPMOST = -2
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOZORDER = 0x0004
    SWP_SHOWWINDOW = 0x0040
    SWP_NOACTIVATE = 0x0010

except Exception as e:
    print(f"Translated: [ERROR] Не удалось загрузить функции user32 через ctypes: {e}")

    _SetWindowPos = lambda *args: print("Translated: [ERROR] _SetWindowPos (ctypes) не загружена!") or 0
    _SetWindowLongW = lambda *args: print("Translated: [ERROR] _SetWindowLongW (ctypes) не загружена!") or 0
    _SetLayeredWindowAttributes = lambda *args: print("Translated: [ERROR] _SetLayeredWindowAttributes (ctypes) не загружена!") or 0

class OlegPainter:
    MODE_FLOOD_FILL = "flood_fill"
    MODE_LEGIT = "legit"
    MODE_SNAKE = "snake"
    DEFAULT_DRAWING_MODE = MODE_FLOOD_FILL
    DEFAULT_DRAW_DELAY = 0.001
    DEFAULT_K_CLUSTERS = 50
    DEFAULT_IMAGE_PATH = ""
    DEFAULT_BRUSH_SIZE = 2
    DEFAULT_REMOVE_BACKGROUND = False
    DEFAULT_BG_TOLERANCE = 25
    DEFAULT_ALPHA_THRESHOLD = 10
    DEFAULT_MODE = "color"
    DEFAULT_BW_DRAW_MODE = 'both'

    DRAW_DELAY = DEFAULT_DRAW_DELAY
    K_CLUSTERS = DEFAULT_K_CLUSTERS
    IMAGE_PATH = DEFAULT_IMAGE_PATH
    BRUSH_SIZE = DEFAULT_BRUSH_SIZE
    REMOVE_BACKGROUND = DEFAULT_REMOVE_BACKGROUND
    BG_TOLERANCE = DEFAULT_BG_TOLERANCE
    ALPHA_THRESHOLD = DEFAULT_ALPHA_THRESHOLD
    mode = DEFAULT_MODE
    bw_draw_mode = DEFAULT_BW_DRAW_MODE

    def __init__(self, status_callback=None, pixel_update_callback=None, preview_callback=None):
        self.draw_region = None
        self.raw_draw_region = None
        self.stop_flag = False
        self.drawing_enabled = False
        self.color_palette = []
        self.current_color_index = 0
        self.drawn_mask = None
        self.cluster_map = None
        self.image_rgb = None
        self.image_original_rgba = None
        self.background_mask = None
        self.has_transparency = False
        self.hex_input_coord = None
        self.is_waiting_for_hex_click = False
        self.drawing_mode = self.DEFAULT_DRAWING_MODE

        self.DRAW_DELAY = self.DEFAULT_DRAW_DELAY
        self.K_CLUSTERS = self.DEFAULT_K_CLUSTERS
        self.IMAGE_PATH = self.DEFAULT_IMAGE_PATH
        self.BRUSH_SIZE = self.DEFAULT_BRUSH_SIZE
        self.REMOVE_BACKGROUND = self.DEFAULT_REMOVE_BACKGROUND
        self.BG_TOLERANCE = self.DEFAULT_BG_TOLERANCE
        self.ALPHA_THRESHOLD = self.DEFAULT_ALPHA_THRESHOLD
        self.mode = self.DEFAULT_MODE
        self.bw_draw_mode = self.DEFAULT_BW_DRAW_MODE

        self.drawing_thread = None
        self.status_callback = status_callback
        self.pixel_update_callback = pixel_update_callback
        self.preview_callback = preview_callback
        self.mouse_listener = None

        self.dpi_scale_factor = 1.0

        try:
            SM_CXSCREEN = 0
            SM_CYSCREEN = 1
            self.primary_width = ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN)
            self.primary_height = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)
            if self.primary_width <= 0 or self.primary_height <= 0:
                raise ValueError("Translated: GetSystemMetrics вернул неверные размеры")
            self._log(f"Translated: Размеры основного монитора: {self.primary_width}x{self.primary_height}")
        except Exception as e:
            self._log(f"Translated: [WARN] Не удалось получить размеры основного монитора: {e}. Используем стандартные 1920x1080.", True)
            self.primary_width = 1920
            self.primary_height = 1080

        self._log("Translated: Координаты поля HEX не установлены. Нажмите F5 и кликните на поле.")

        self.neighbor_order = "36184527"
        self.neighbor_mapping = {'1':(-1,-1),'2':(-1,0),'3':(-1,1),'4':(0,-1),'5':(0,1),'6':(1,-1),'7':(1,0),'8':(1,1)}
        try:
            interception.auto_capture_devices(mouse=True, keyboard=False)
            self._log("Translated: Мышь успешно захвачена через Interception.")
        except Exception as e: self._log(f"Translated: Translated: Ошибка инициализации Interception: {e}. Проверьте драйвер и права.", True)

    def start_hex_coord_capture(self):
        "Translated: ""Начинает процесс ожидания клика мыши для установки координат поля HEX."""

        if self.is_waiting_for_hex_click:

            return
        if self.drawing_enabled:

            return

        self._log("Translated: Нажмите левой кнопкой мыши на поле ввода HEX (НА ОСНОВНОМ МОНИТОРЕ)...")
        self.status_callback("Translated: Ожидание клика ЛКМ для поля HEX (НА ОСНОВНОМ МОНИТОРЕ)...")
        self.is_waiting_for_hex_click = True

        def on_click(x, y, button, pressed):

            if pressed and button == mouse.Button.left and self.is_waiting_for_hex_click:
                if not hasattr(self, 'primary_width') or not hasattr(self, 'primary_height'):
                    self._log("Translated: [ERROR] Размеры основного монитора не определены! Не могу проверить клик.", True)
                    self.status_callback("Translated: Translated: Ошибка: Не определены размеры основного монитора.")
                    return

                if not (0 <= x < self.primary_width and 0 <= y < self.primary_height):
                    error_msg = "Translated: [WARN] Клик вне основного монитора! Пожалуйста, кликните на поле HEX на ОСНОВНОМ экране."
                    self._log(error_msg, True)
                    if self.status_callback:
                        self.status_callback(error_msg)
                    return

                self.hex_input_coord = (int(x), int(y))
                self.is_waiting_for_hex_click = False
                self._log(f"Translated: Координаты поля HEX установлены: {self.hex_input_coord}")

                if hasattr(self, 'hex_coord_set_callback') and self.hex_coord_set_callback:
                    self.hex_coord_set_callback(self.hex_input_coord)
                elif self.status_callback:
                    self.status_callback(f"Translated: Translated: Координаты HEX установлены: {self.hex_input_coord}")

                return False

        try:

            if self.mouse_listener and self.mouse_listener.is_alive():
                self.mouse_listener.stop()

            self.mouse_listener = mouse.Listener(on_click=on_click)
            self.mouse_listener.start()
            self._log("Translated: Прослушиватель мыши для HEX запущен.")
        except NameError:
            self._log("Translated: [ERROR] Библиотека pynput не импортирована должным образом!", True)
            self.status_callback("Translated: Критическая ошибка: pynput не найден.")
            self.is_waiting_for_hex_click = False
        except Exception as e:
            self._log(f"Translated: Translated: Ошибка запуска прослушивателя мыши: {e}", is_error=True)
            self.status_callback(f"Translated: Translated: Ошибка мыши: {e}")
            self.is_waiting_for_hex_click = False

    def _log(self, message, is_error=False):
        prefix = "[ERROR] " if is_error else "[INFO] "; full_message = prefix + str(message); print(full_message)
        if self.status_callback:
            try: self.status_callback(full_message)
            except Exception as e: print(f"[WARN] Status callback failed: {e}")

    def preprocess_image(self, img): return cv2.GaussianBlur(img, (5, 5), 0)

    def select_area(self):
        """
        ВЕРСИЯ, ИМИТИРУЮЩАЯ СТАРЫЙ КОД:
        Запускает процесс выбора области на ОСНОВНОМ мониторе.
        Сохраняет ФИЗИЧЕСКИЕ координаты из cv2.selectROI напрямую в self.draw_region.
        Не использует DPI масштабирование для координат рисования.
        Поле self.raw_draw_region НЕ используется.
        """
        if self.drawing_enabled:
            self._log("Translated: Нельзя выбрать область во время рисования.", True)
            self.status_callback("Translated: Translated: Ошибка: Рисование активно.")
            return

        if self.is_waiting_for_hex_click:
            self._log("Translated: Отмена ожидания клика для HEX поля из-за выбора области.")
            if hasattr(self, 'mouse_listener') and self.mouse_listener and self.mouse_listener.is_alive():
                try:
                    self.mouse_listener.stop()
                    self._log("Translated: Прослушиватель мыши для HEX остановлен.")
                except Exception as e_stop:
                    self._log(f"Translated: [WARN] Не удалось остановить mouse_listener: {e_stop}", True)
            self.is_waiting_for_hex_click = False
            self.status_callback("Translated: Выбор области отменил ожидание клика HEX.")

        self._log("Translated: Выбор области (ТОЛЬКО НА ОСНОВНОМ МОНИТОРЕ)...")
        self.status_callback("Translated: Запустите выбор области (Enter/C) - ТОЛЬКО НА ОСНОВНОМ МОНИТОРЕ")

        self.draw_region = None
        if hasattr(self, 'raw_draw_region'):
             self.raw_draw_region = None

        try:

            if not hasattr(self, 'primary_width') or not hasattr(self, 'primary_height') \
               or self.primary_width <= 0 or self.primary_height <= 0:
                error_msg = "Translated: [ERROR] Размеры основного монитора не определены или некорректны! Не могу выбрать область."
                self._log(error_msg, True)
                self.status_callback("Translated: Translated: Ошибка: Не определены размеры основного монитора.")
                return

            bbox_primary = (0, 0, self.primary_width, self.primary_height)
            try:
                 from PIL import ImageGrab
                 screenshot = ImageGrab.grab(bbox=bbox_primary, all_screens=False)
            except ImportError:
                 self._log("Translated: [ERROR] PIL (Pillow) не найден. Невозможно сделать скриншот.", True)
                 self.status_callback("Translated: Translated: Ошибка: Pillow не найден.")
                 return
            except Exception as grab_err:
                 self._log(f"Translated: [ERROR] Translated: Ошибка при захвате скриншота: {grab_err}", True)
                 self.status_callback(f"Translated: Translated: Ошибка скриншота: {grab_err}")
                 return

            img = np.array(screenshot)
            if img.shape[2] == 4: img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            else: img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            window_title = "Translated: Выберите область НА ОСНОВНОМ МОНИТОРЕ (Enter - подтвердить, C - отмена)"
            cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)

            try:
                cv2.setWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            except Exception as e_fs:
                self._log(f"Translated: [WARN] Не удалось установить полноэкранный режим: {e_fs}", True)
            try:
                 cv2.setWindowProperty(window_title, cv2.WND_PROP_TOPMOST, 1)
            except Exception as e_prop:
                 self._log(f"Translated: [WARN] Не удалось установить поверх всех: {e_prop}", True)

            roi = cv2.selectROI(window_title, img, showCrosshair=True, fromCenter=False)
            cv2.destroyWindow(window_title)

            x_roi, y_roi, w_roi, h_roi = roi

        except Exception as e:
            cv2.destroyAllWindows()
            self._log(f"Translated: Translated: Ошибка выбора области: {e}", True)
            traceback.print_exc()
            self.status_callback(f"Translated: Translated: Ошибка выбора: {e}")
            self.draw_region = None
            if self.preview_callback: self.preview_callback()
            return

        if w_roi > 0 and h_roi > 0:

            self.draw_region = tuple(map(int, roi))

            self._log(f"Translated: Область выбрана (физические коорд. сохранены в draw_region): {self.draw_region}")

            self.status_callback(f"Translated: Область (физ. пикс.): ({x_roi},{y_roi}) {w_roi}x{h_roi}")

            if self.IMAGE_PATH:
                self.prepare_image_and_palette()
            else:
                self._log("Translated: Translated: Изображение не выбрано. Область задана.")
                self.status_callback("Область выбрана (физ.). Translated: Выберите изображение.")
                if self.preview_callback:
                    self.preview_callback()
        else:

            self._log("Translated: Выбор области отменен пользователем.")
            self.status_callback("Translated: Выбор области отменен.")
            self.draw_region = None
            if self.preview_callback:
                self.preview_callback()

    def prepare_image_and_palette(self):
        """
        Подготавливает изображение: загружает, обрабатывает фон (альфа/угол, если включено),
        выполняет кластеризацию KMeans или бинаризацию, создает палитру и маски.
        """
        if self.drawing_enabled:
            self._log("Translated: Нельзя изменить параметры во время рисования.", True)
            return False

        if self.is_waiting_for_hex_click:
             self._log("Translated: Отмена ожидания клика для HEX поля из-за подготовки изображения.")
             if self.mouse_listener and self.mouse_listener.is_alive():
                 self.mouse_listener.stop()
             self.is_waiting_for_hex_click = False
             self.status_callback("Translated: Обработка изображения отменила ожидание клика HEX.")

        if self.draw_region is None:
            self._log("Translated: Область не выбрана.", True); self.status_callback("Translated: Translated: Ошибка: Translated: Область не выбрана."); return False
        if not self.IMAGE_PATH or not os.path.exists(self.IMAGE_PATH):
            self._log("Translated: Файл изображения не найден.", True); self.status_callback("Translated: Translated: Ошибка: Файл не найден.")
            self.image_rgb = None; self.cluster_map = None; self.drawn_mask = None; self.color_palette = []; self.image_original_rgba = None; self.background_mask = None; self.has_transparency = False
            if self.preview_callback: self.preview_callback()
            if self.pixel_update_callback: self.pixel_update_callback()

            return False

        self._log("Translated: Подготовка изображения и палитры (Альфа/Угол)..."); self.status_callback("Translated: Обработка изображения...")
        start_time = time.time(); success = False
        self.has_transparency = False

        try:
            if not isinstance(self.draw_region, (tuple, list)) or len(self.draw_region) != 4:
                raise ValueError(f"Translated: Некорректный формат draw_region: {self.draw_region}")
            x, y, w, h = self.draw_region
            if w <= 0 or h <= 0:
                raise ValueError(f"Translated: Некорректные размеры области: w={w}, h={h}")

            img_original = Image.open(self.IMAGE_PATH)
            img_rgba = img_original.convert("RGBA")
            self.image_original_rgba = img_rgba

            img_resized_rgba = img_rgba.resize((w, h), Image.LANCZOS)
            np_img_resized_rgba = np.array(img_resized_rgba)

            w_brush = max(1, w // self.BRUSH_SIZE)
            h_brush = max(1, h // self.BRUSH_SIZE)
            self._log(f"Translated: Размер карты кластеров: {w_brush}x{h_brush}")

            img_small_rgba = img_resized_rgba.resize((w_brush, h_brush), Image.LANCZOS)
            np_img_small_rgba = np.array(img_small_rgba)
            np_img_small_rgb = np_img_small_rgba[:, :, :3]
            alpha_channel = np_img_small_rgba[:, :, 3]

            self.background_mask = np.zeros((h_brush, w_brush), dtype=bool)
            background_color_rgb = None

            self.has_transparency = np.any(alpha_channel < 255 - self.ALPHA_THRESHOLD)

            if self.REMOVE_BACKGROUND:
                self._log(f"Translated: Удаление фона включено. Обнаружена прозрачность: {self.has_transparency}")
                if self.has_transparency:
                    self._log(f"Translated: Используем альфа-канал как маску фона (порог: {self.ALPHA_THRESHOLD}).")
                    self.background_mask = alpha_channel < self.ALPHA_THRESHOLD
                else:
                    self._log(f"Translated: Используем цвет верхнего левого пикселя как фон (допуск: {self.BG_TOLERANCE}).")
                    background_color_rgb = tuple(np_img_small_rgb[0, 0])
                    color_threshold = self.BG_TOLERANCE
                    color_diff = np.sqrt(np.sum((np_img_small_rgb.astype(float) - np.array(background_color_rgb).astype(float))**2, axis=2))
                    self.background_mask = color_diff < color_threshold
                    self._log(f"Translated: Цвет фона (верхний левый): {background_color_rgb}. Найдено {np.count_nonzero(self.background_mask)} пикселей фона.")
            else:
                self._log("Translated: Удаление фона выключено.")

            self.color_palette = []
            self.cluster_map = None
            self.image_rgb = np_img_small_rgb.copy()
            background_cluster_id = -1

            if self.mode == "bw":
                self._log("Translated: Режим Translated: Ч/Б.")
                img_gray = cv2.cvtColor(np_img_small_rgb, cv2.COLOR_RGB2GRAY)
                ret, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                self.cluster_map = (thresh == 0).astype(np.int8)
                self.cluster_map[self.background_mask] = background_cluster_id
                num_bg_pixels = np.count_nonzero(self.background_mask)
                if num_bg_pixels > 0: self._log(f"Translated: Применена маска фона к Translated: Ч/Б карте: {num_bg_pixels} пикс. помечены как фон (ID {background_cluster_id}).")

                count_black = np.count_nonzero(self.cluster_map == 1)
                count_white = np.count_nonzero(self.cluster_map == 0)
                self.color_palette = []
                if self.bw_draw_mode == 'both':
                    if count_black > 0: self.color_palette.append(("#000000", 1, count_black, (0, 0, 0)))
                    if count_white > 0: self.color_palette.append(("#FFFFFF", 0, count_white, (255, 255, 255)))
                elif self.bw_draw_mode == 'black_only':
                    if count_black > 0: self.color_palette.append(("#000000", 1, count_black, (0, 0, 0)))
                elif self.bw_draw_mode == 'white_only':
                    if count_white > 0: self.color_palette.append(("#FFFFFF", 0, count_white, (255, 255, 255)))

                self.image_rgb = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
                self.image_rgb[self.background_mask] = [128, 128, 128]

                if self.color_palette:
                   palette_colors = [p[0] for p in self.color_palette]
                   self._log(f"Translated: Палитра BW ({self.bw_draw_mode}) создана: {palette_colors}")
                else:
                   self._log(f"Translated: Палитра BW ({self.bw_draw_mode}) пуста.")

            else:

                 self._log("Режим Translated: Цветной.")
                 non_background_pixels_rgb = np_img_small_rgb[~self.background_mask]
                 if len(non_background_pixels_rgb) == 0:
                     self._log("Translated: Нет не-фоновых пикселей для кластеризации.")
                     self.color_palette = []; self.cluster_map = np.full((h_brush, w_brush), background_cluster_id, dtype=int); self.image_rgb.fill(128)
                 else:
                     self._log(f"Translated: Пикселей для кластеризации: {len(non_background_pixels_rgb)} (из {w_brush*h_brush})")
                     if non_background_pixels_rgb.ndim == 1:
                         if non_background_pixels_rgb.shape[0] == 3: non_background_pixels_rgb = non_background_pixels_rgb.reshape(1, 3)
                         else: raise ValueError("Translated: Некорректный массив пикселей после маскирования")
                     elif non_background_pixels_rgb.ndim != 2 or non_background_pixels_rgb.shape[1] != 3:
                         raise ValueError(f"Translated: Некорректная форма массива пикселей: {non_background_pixels_rgb.shape}")

                     unique_pixels = np.unique(non_background_pixels_rgb, axis=0)
                     k_actual = min(self.K_CLUSTERS, len(unique_pixels))
                     if k_actual < 1:
                         self._log("Translated: Нет уникальных не-фоновых пикселей для кластеризации."); self.color_palette = []; self.cluster_map = np.full((h_brush, w_brush), background_cluster_id, dtype=int); self.image_rgb.fill(128)
                     else:
                         self._log(f"Translated: Запуск KMeans с k={k_actual} на не-фоновых пикселях...")
                         kmeans = KMeans(n_clusters=k_actual, random_state=42, n_init='auto')
                         kmeans.fit(non_background_pixels_rgb.astype(float))
                         centers = kmeans.cluster_centers_.astype(int)

                         self._log("Translated: Предсказание кластеров для всей карты...")
                         all_pixels_reshaped = np_img_small_rgb.reshape(-1, 3)
                         all_pixels_reshaped = np.nan_to_num(all_pixels_reshaped.astype(float))
                         all_labels = kmeans.predict(all_pixels_reshaped)
                         self.cluster_map = all_labels.reshape(h_brush, w_brush)

                         self.cluster_map[self.background_mask] = background_cluster_id
                         num_bg_pixels = np.count_nonzero(self.background_mask)
                         if num_bg_pixels > 0: self._log(f"Translated: Применена маска фона к цветной карте: {num_bg_pixels} пикс. помечены как фон (ID {background_cluster_id}).")

                         foreground_labels = self.cluster_map[~self.background_mask].flatten()
                         if foreground_labels.size > 0: counts = np.bincount(foreground_labels, minlength=k_actual)
                         else: counts = np.zeros(k_actual, dtype=int)

                         temp_palette = []
                         for cluster_id in range(k_actual):
                             if counts[cluster_id] > 0:
                                 center_color = centers[cluster_id]
                                 center_color = np.clip(center_color, 0, 255)
                                 hex_color = "#{:02X}{:02X}{:02X}".format(center_color[0], center_color[1], center_color[2])
                                 temp_palette.append({"hex": hex_color, "id": cluster_id, "count": counts[cluster_id], "rgb": tuple(center_color)})

                         sorted_palette = sorted(temp_palette, key=lambda x: x["count"], reverse=True)
                         self.color_palette = [(p["hex"], p["id"], p["count"], p["rgb"]) for p in sorted_palette]

                         if not self.color_palette: self._log("Translated: Палитра пуста после фильтрации.")
                         else: self._log(f"Translated: Палитра создана ({len(self.color_palette)} цветов).")

                         self.image_rgb = np.zeros_like(np_img_small_rgb)
                         valid_clusters_mask = self.cluster_map != background_cluster_id
                         for cluster_id in range(k_actual):
                              mask_for_id = (self.cluster_map == cluster_id) & valid_clusters_mask
                              if cluster_id < len(centers):
                                   color_val = np.clip(centers[cluster_id], 0, 255)
                                   self.image_rgb[mask_for_id] = color_val
                              else: self.image_rgb[mask_for_id] = [255,0,255]
                         self.image_rgb[self.cluster_map == background_cluster_id] = [128, 128, 128]

            if self.cluster_map is not None:
                self.drawn_mask = (self.cluster_map == background_cluster_id)
                num_drawn_start = np.count_nonzero(self.drawn_mask)
                if num_drawn_start > 0: self._log(f"Translated: Инициализация drawn_mask: {num_drawn_start} пикс. фона помечены как 'уже нарисованные'.")
            else:
                self.drawn_mask = None

            self.current_color_index = 0
            success = True

        except Exception as e:
            self._log(f"Translated: Translated: Ошибка обработки изображения: {e}", True); traceback.print_exc()
            self.status_callback(f"Translated: Translated: Ошибка обработки: {e}")
            self.image_rgb = None; self.cluster_map = None; self.drawn_mask = None; self.color_palette = []; self.image_original_rgba = None; self.background_mask = None; self.has_transparency = False
            success = False
        finally:
            end_time = time.time()
            if success:
                self._log(f"PREP SUCCESS: Image='{self.IMAGE_PATH}', Region={self.draw_region}")
                log_prefix = "[PREP RESULT]"
                if self.cluster_map is not None:
                    self._log(f"{log_prefix} cluster_map ID={id(self.cluster_map)}, shape={self.cluster_map.shape}")
                else:
                    self._log(f"{log_prefix} cluster_map is None")

                if self.color_palette is not None:
                    self._log(
                        f"{log_prefix} color_palette ID={id(self.color_palette)}, length={len(self.color_palette)}")
                else:
                    self._log(f"{log_prefix} color_palette is None")

                if self.drawn_mask is not None:
                    self._log(f"{log_prefix} drawn_mask ID={id(self.drawn_mask)}, shape={self.drawn_mask.shape}")
                else:
                    self._log(f"{log_prefix} drawn_mask is None")
                self._log(f"Translated: Подготовка завершена за {end_time - start_time:.2f} сек."); self.status_callback("Translated: Изображение обработано.")
            else: self._log("Translated: Подготовка не удалась.")
            if self.preview_callback: self.preview_callback()
            if self.pixel_update_callback: self.pixel_update_callback()

        return success

    def pick_color(self, hex_color: str):

        if self.hex_input_coord is None:
            error_msg = "Translated: [ERROR] Координаты поля HEX не установлены! Нажмите F5 и кликните на поле."
            self._log(error_msg, True)

            self.status_callback("show_hex_error_popup:" + error_msg)
            self.stop_flag = True
            self.drawing_enabled = False
            return

        try:
            clean_hex = hex_color.lstrip('#')
            self._log(f"Translated: Выбор цвета: {clean_hex}")

            interception.move_to(self.hex_input_coord[0], self.hex_input_coord[1])
            time.sleep(0.05)
            interception.click(button='left')
            time.sleep(0.05)
            interception.click(button='left')

            time.sleep(0.15)

            keyboard.send("ctrl+a")

            time.sleep(0.1)

            keyboard.send("delete")
            time.sleep(0.05)

            keyboard.write(clean_hex)

            time.sleep(0.1)

            keyboard.send("enter")

            time.sleep(0.2)

        except Exception as e:
            self._log(f"Translated: Translated: Ошибка выбора цвета {hex_color}: {e}", True); self.stop_flag = True; self.drawing_enabled = False
            self.status_callback(f"Translated: Translated: Ошибка выбора цвета! Translated: Рисование остановлено.")

    def draw_line(self, x1, y1, x2, y2):
        "Translated: ""Перемещает мышь из (x1, y1) в (x2, y2) с обработкой ошибок interception."""
        while not self.drawing_enabled and not self.stop_flag:
            time.sleep(0.01)
        if self.stop_flag:
            return

        try:
            interception.move_to(x2, y2)
        except Exception as e:
             self._log(f"Translated: [WARN] Translated: Ошибка interception.move_to в draw_line ({x1},{y1} -> {x2},{y2}): {e}", True)

        if self.DRAW_DELAY > 0 and self.drawing_enabled and not self.stop_flag:
             time.sleep(self.DRAW_DELAY)

    def flood_fill_draw(self, mask, start_row, start_col, x0_unused, y0_unused):
        """
        ВЕРСИЯ, ИМИТИРУЮЩАЯ СТАРЫЙ КОД:
        Выполняет заливку, используя ФИЗИЧЕСКИЕ координаты из self.draw_region
        для вычисления позиций и передачи в interception.
        """
        if self.drawn_mask is None:
            self._log("Translated: [ERROR] flood_fill_draw (PhysCoords): Глобальная маска drawn_mask отсутствует!", True)
            self.status_callback("Translated: Translated: Ошибка: Маска рисования не найдена.")
            self.stop_flag = True
            return

        if self.draw_region is None or len(self.draw_region) != 4:
            self._log("Translated: [ERROR] flood_fill_draw (PhysCoords): Координаты области (draw_region) отсутствуют или некорректны!", True)
            self.status_callback("Translated: Translated: Ошибка: Координаты области не найдены для рисования.")
            self.stop_flag = True
            return

        try:
            x0_phys, y0_phys, w_phys, h_phys = map(int, self.draw_region)
            if w_phys <= 0 or h_phys <= 0: raise ValueError("Translated: Некорректные размеры в draw_region")
        except (TypeError, ValueError) as e:
            self._log(f"[ERROR] flood_fill_draw (PhysCoords): Translated: Ошибка в данных draw_region {self.draw_region}: {e}", True)
            self.status_callback(f"Translated: Translated: Ошибка данных области: {e}")
            self.stop_flag = True
            return

        brush = self.BRUSH_SIZE
        h_mask, w_mask = mask.shape

        if not (0 <= start_row < h_mask and 0 <= start_col < w_mask):
             self._log(f"Translated: [WARN] flood_fill_draw (PhysCoords): Начальная точка ({start_row}, {start_col}) вне маски {h_mask}x{w_mask}.", True)
             return
        if mask[start_row, start_col] != 255:
             self._log(f"Translated: [WARN] flood_fill_draw (PhysCoords): Начальная точка ({start_row}, {start_col}) не принадлежит целевой области (mask != 255).", True)
             return
        if self.drawn_mask[start_row, start_col]:
             return

        visited = np.zeros_like(mask, dtype=bool)
        stack = [(start_row, start_col)]
        visited[start_row, start_col] = True

        start_x_phys = x0_phys + start_col * brush + brush // 2
        start_y_phys = y0_phys + start_row * brush + brush // 2

        mouse_is_down = False
        resumed_just_now = False

        try:

            interception.move_to(start_x_phys, start_y_phys)
            time.sleep(0.01)

            if self.drawing_enabled:
                interception.mouse_down("left")
                time.sleep(0.01)
                mouse_is_down = True
                self.drawn_mask[start_row, start_col] = True
                if self.pixel_update_callback: self.pixel_update_callback()
            else:
                 self._log("Translated: [WARN] flood_fill_draw (PhysCoords): Попытка начать заливку во время паузы.", True)
                 return

        except Exception as e:
            self._log(f"Translated: [ERROR] flood_fill_draw (PhysCoords): Translated: Ошибка в начале (move/down на физ. {start_x_phys},{start_y_phys}): {e}", True)
            self.status_callback(f"Translated: Translated: Ошибка мыши при старте заливки!")
            if mouse_is_down:
                try: interception.mouse_up("left")
                except Exception as e_up: self._log(f"Translated: [WARN] Translated: Ошибка mouse_up при обработке ошибки начала: {e_up}", True)
            self.stop_flag = True
            return

        last_x_phys, last_y_phys = start_x_phys, start_y_phys
        jump_threshold_sq = (brush * 3) ** 2

        while stack and not self.stop_flag:

            paused_in_loop = False
            while not self.drawing_enabled and not self.stop_flag:
                if not paused_in_loop:
                    if mouse_is_down:
                        try:
                            interception.mouse_up("left")
                            mouse_is_down = False
                            self._log("Paused, mouse button released.")
                        except Exception as e:
                            self._log(f"Translated: [WARN] Translated: Ошибка mouse_up при паузе: {e}", True)
                    self._log("Drawing paused, waiting...")
                    self.status_callback("Translated: Translated: Пауза...")
                    paused_in_loop = True
                time.sleep(0.1)

            if self.stop_flag:
                self._log("Stop flag received while paused or before stack pop.")
                break

            row, col = stack.pop()

            if self.stop_flag:
                self._log(f"Translated: (PhysCoords) Заливка прервана флагом стоп после stack.pop для точки ({row}, {col}).")
                break

            if paused_in_loop and self.drawing_enabled:
                resumed_just_now = True
                self.status_callback("Translated: Рисование...")
                self._log("Resumed, mouse button should be UP.")

            next_x_phys = x0_phys + col * brush + brush // 2
            next_y_phys = y0_phys + row * brush + brush // 2

            if resumed_just_now:
                self._log(f"Repositioning mouse to last known phys pos ({last_x_phys}, {last_y_phys}) after pause.")
                try:
                    interception.move_to(last_x_phys, last_y_phys)
                    time.sleep(0.05)
                except Exception as e:
                    self._log(f"[ERROR] Translated: Ошибка при позиционировании после паузы (move to phys {last_x_phys},{last_y_phys}): {e}", True)
                    self.status_callback(f"Translated: Translated: Ошибка мыши при возобновлении!")
                    self.stop_flag = True; break
                resumed_just_now = False

            try:
                dist_sq = (next_x_phys - last_x_phys)**2 + (next_y_phys - last_y_phys)**2
                if dist_sq > jump_threshold_sq:
                    if mouse_is_down:
                        interception.mouse_up("left"); time.sleep(0.01)
                        mouse_is_down = False
                    interception.move_to(next_x_phys, next_y_phys); time.sleep(0.02)
                    if self.drawing_enabled:
                         interception.mouse_down("left"); time.sleep(0.01)
                         mouse_is_down = True
                    else: continue
                else:
                    if not mouse_is_down:
                        if self.drawing_enabled:
                            interception.move_to(last_x_phys, last_y_phys); time.sleep(0.01)
                            interception.mouse_down("left"); time.sleep(0.01)
                            mouse_is_down = True
                        else: continue
                    interception.move_to(next_x_phys, next_y_phys)
                    if self.DRAW_DELAY > 0: time.sleep(self.DRAW_DELAY)

                last_x_phys, last_y_phys = next_x_phys, next_y_phys
            except Exception as e:
                 self._log(f"Translated: [ERROR] (PhysCoords) Translated: Ошибка при перемещении/рисовании (физ. {last_x_phys},{last_y_phys} -> {next_x_phys},{next_y_phys}): {e}", True)
                 self.status_callback(f"Translated: Translated: Ошибка мыши при рисовании линии!")
                 if mouse_is_down:
                     try: interception.mouse_up("left"); mouse_is_down = False
                     except: pass
                 self.stop_flag = True; break

            for d in self.neighbor_order:

                 if self.stop_flag: break
                 dr, dc = self.neighbor_mapping[d]
                 nr, nc = row + dr, col + dc
                 if 0 <= nr < h_mask and 0 <= nc < w_mask:
                    if mask[nr, nc] == 255 and not visited[nr, nc]:
                        if not self.drawn_mask[nr, nc]:
                            visited[nr, nc] = True
                            stack.append((nr, nc))
                            self.drawn_mask[nr, nc] = True
                            if self.pixel_update_callback: self.pixel_update_callback()

            if self.stop_flag: break

        if mouse_is_down:

             try:
                interception.mouse_up("left")
                self._log("(PhysCoords) Mouse button released at the end of flood fill.")
             except Exception as e:
                self._log(f"Translated: [WARN] (PhysCoords) Translated: Ошибка mouse_up в конце flood_fill: {e}", True)

        if self.stop_flag:
             self._log(f"Translated: (PhysCoords) Заливка прервана флагом стоп во время обработки точки ({start_row}, {start_col}).")

    def legit_draw(self, mask_u8_copy, start_row, start_col):
        """
        Рисует область одного цвета, имитируя "Translated: человеческое" поведение.
        Версия 2: Исправлена структура try...finally.
        Основан на flood_fill_draw, но с плавными/неровными движениями
        и вариативной задержкой, без больших прыжков.
        """
        if self.drawn_mask is None or self.draw_region is None:
            self._log("Translated: [ERROR] LegitDraw: Отсутствует маска или область.", True)
            return

        self._log(f"Translated: [INFO] Начало 'легитного' рисования v2 от ({start_row}, {start_col}).")

        try:
            x0_phys, y0_phys, w_phys, h_phys = map(int, self.draw_region)
            if w_phys <= 0 or h_phys <= 0: raise ValueError("Translated: Некорректные размеры в draw_region")
        except (TypeError, ValueError, AttributeError) as e:
            self._log(f"Translated: [ERROR] LegitDraw: Translated: Ошибка в данных draw_region {getattr(self, 'draw_region', 'N/A')}: {e}", True)
            self.status_callback(f"Translated: Translated: Ошибка данных области: {e}")
            self.stop_flag = True
            return

        brush = self.BRUSH_SIZE
        h_mask, w_mask = mask_u8_copy.shape

        if not (0 <= start_row < h_mask and 0 <= start_col < w_mask):
             self._log(f"Translated: [WARN] LegitDraw: Начальная точка ({start_row}, {start_col}) вне маски {h_mask}x{w_mask}.", True)
             return
        if mask_u8_copy[start_row, start_col] != 255:
             self._log(f"Translated: [WARN] LegitDraw: Начальная точка ({start_row}, {start_col}) не принадлежит целевой области (mask != 255).", True)
             return
        try:
            if self.drawn_mask[start_row, start_col]:
                 self._log(f"Translated: [DEBUG] LegitDraw: Начальная точка ({start_row}, {start_col}) уже нарисована.")
                 return
        except IndexError:
             self._log(f"[WARN] LegitDraw: Start point ({start_row},{start_col}) out of drawn_mask bounds {self.drawn_mask.shape}")
             return

        visited = np.zeros_like(mask_u8_copy, dtype=bool)
        stack = [(start_row, start_col)]
        visited[start_row, start_col] = True

        start_x_phys = x0_phys + start_col * brush + brush // 2
        start_y_phys = y0_phys + start_row * brush + brush // 2

        mouse_is_down = False
        resumed_just_now = False
        last_x_phys, last_y_phys = start_x_phys, start_y_phys

        try:
            interception.move_to(start_x_phys, start_y_phys)
            if self.stop_flag: return
            time.sleep(0.05)

            if self.drawing_enabled:
                interception.mouse_down("left")
                mouse_is_down = True
                if 0 <= start_row < self.drawn_mask.shape[0] and 0 <= start_col < self.drawn_mask.shape[1]:
                     self.drawn_mask[start_row, start_col] = True
                     if self.pixel_update_callback: self.pixel_update_callback()
                time.sleep(0.02)
            else:
                 self._log("Translated: [WARN] LegitDraw: Попытка начать заливку во время паузы.")
                 return
        except Exception as e:
            self._log(f"Translated: [ERROR] LegitDraw: Translated: Ошибка в начале (move/down на {start_x_phys},{start_y_phys}): {e}", True)
            self.status_callback(f"Translated: Translated: Ошибка мыши при старте заливки!")

            self.stop_flag = True
            return

        try:
            while stack:

                if self.stop_flag:
                    self._log("Translated: LegitDraw: Обнаружен stop_flag в начале цикла stack.")
                    break
                paused_in_loop = False
                while not self.drawing_enabled and not self.stop_flag:
                    if not paused_in_loop:
                        if mouse_is_down:
                            try: interception.mouse_up("left"); mouse_is_down = False;
                            except Exception as eup: self._log(f"[WARN] Legit pause mouse_up error: {eup}")
                            self._log("Translated: Пауза в 'легитном' рисовании v2, ЛКМ отпущена.")
                        else: self._log("Translated: Пауза в 'легитном' рисовании v2...")
                        self.status_callback("Translated: Translated: Пауза...")
                        paused_in_loop = True
                    time.sleep(0.1)
                if self.stop_flag:
                    self._log("Translated: LegitDraw: Обнаружен stop_flag после паузы.")
                    break
                if paused_in_loop and self.drawing_enabled:
                    self._log("Translated: Возобновление 'легитного' рисования v2.")
                    self.status_callback("Translated: Рисование...")
                    resumed_just_now = True

                row, col = stack.pop()
                if self.stop_flag:
                    self._log(f"Translated: LegitDraw: Прервано флагом стоп после stack.pop для ({row}, {col}).")
                    break

                next_x_phys = x0_phys + col * brush + brush // 2
                next_y_phys = y0_phys + row * brush + brush // 2

                try:

                    if resumed_just_now:
                        self._log(f"Translated: LegitDraw: Перемещение в ({last_x_phys}, {last_y_phys}) после паузы.")
                        interception.move_to(last_x_phys, last_y_phys)
                        if self.stop_flag: break
                        time.sleep(0.05)
                        if not mouse_is_down:
                            interception.mouse_down("left")
                            mouse_is_down = True
                            if self.stop_flag: break
                            time.sleep(0.02)
                        resumed_just_now = False

                    dx = next_x_phys - last_x_phys
                    dy = next_y_phys - last_y_phys
                    dist = math.sqrt(dx*dx + dy*dy)
                    steps = 1
                    if dist > 0.1:
                        steps = max(2, min(8, int(dist / (brush * 0.5))))
                    base_step_delay = 0.001
                    delay_variation = base_step_delay * 0.5

                    if steps > 1:
                        for i in range(1, steps + 1):
                            if self.stop_flag: raise InterruptedError("Stop during legit move")
                            progress = i / steps
                            ix = last_x_phys + dx * progress
                            iy = last_y_phys + dy * progress
                            offset_scale = brush * 0.10
                            offset_x = random.uniform(-offset_scale, offset_scale)
                            offset_y = random.uniform(-offset_scale, offset_scale)
                            interception.move_to(int(ix + offset_x), int(iy + offset_y))
                            step_delay = base_step_delay + random.uniform(-delay_variation, delay_variation)
                            if step_delay > 0: time.sleep(step_delay)
                        if self.stop_flag: raise InterruptedError("Stop during legit move")
                        interception.move_to(next_x_phys, next_y_phys)
                        time.sleep(0.001)
                    elif dist > 0.1:
                        interception.move_to(next_x_phys, next_y_phys)
                        if self.stop_flag: raise InterruptedError("Stop during legit move")
                        time.sleep(base_step_delay)

                    last_x_phys, last_y_phys = next_x_phys, next_y_phys

                except InterruptedError:
                     break
                except Exception as move_err:
                     self._log(f"Translated: [ERROR] LegitDraw: Translated: Ошибка при имитации движения: {move_err}", True)
                     self.stop_flag = True
                     break

                if self.stop_flag: break

                for d in self.neighbor_order:
                    if self.stop_flag: break

                    dr, dc = self.neighbor_mapping[d]
                    nr, nc = row + dr, col + dc

                    if 0 <= nr < h_mask and 0 <= nc < w_mask:
                       if mask_u8_copy[nr, nc] == 255 and not visited[nr, nc]:
                           try:
                               if 0 <= nr < self.drawn_mask.shape[0] and 0 <= nc < self.drawn_mask.shape[1]:
                                   if not self.drawn_mask[nr, nc]:
                                       visited[nr, nc] = True
                                       stack.append((nr, nc))
                                       self.drawn_mask[nr, nc] = True
                                       if self.pixel_update_callback: self.pixel_update_callback()
                               else:
                                   self._log(f"[WARN] LegitDraw: Neighbor index ({nr},{nc}) out of drawn_mask bounds {self.drawn_mask.shape}")
                           except IndexError:
                                self._log(f"[WARN] LegitDraw: IndexError accessing drawn_mask at ({nr},{nc})")

                if self.stop_flag: break

        finally:
            self._log("LegitDraw: Entering finally block for cleanup.")
            if mouse_is_down:
                try:
                    interception.mouse_up("left")
                    self._log("Translated: LegitDraw: ЛКМ отпущена в блоке finally.")
                except Exception as e_fin:
                    self._log(f"[WARN] LegitDraw finally mouse_up error: {e_fin}")

        if self.stop_flag:
            self._log(f"Translated: LegitDraw: Рисование прервано флагом стоп от ({start_row}, {start_col}).")
        else:

            self._log(f"Translated: LegitDraw: Рисование завершено для области от ({start_row}, {start_col}).")

    def snake_fill_draw(self, cluster_id):
        """
        Рисует пиксели цвета cluster_id змейкой. Версия 10:
        Перемещает мышь ТОЛЬКО при рисовании. Пропускает (перепрыгивает)
        пустые/нецелевые области без движения мыши.
        Удерживает ЛКМ при рисовании смежных пикселей.
        """
        if self.draw_region is None or self.cluster_map is None or self.drawn_mask is None:
            self._log("Translated: [ERROR] SnakeFill v10: Отсутствует область, карта или маска.", True)
            return
        if self.stop_flag: return

        self._log(f"Translated: [INFO] Начало рисования 'змейкой v10' для ID {cluster_id}")
        x0_phys, y0_phys, w_phys, h_phys = self.draw_region
        brush = self.BRUSH_SIZE
        h_map, w_map = self.cluster_map.shape

        mouse_is_down = False

        try:

            for r in range(h_map):
                if self.stop_flag: break

                direction = 1 if r % 2 == 0 else -1
                col_indices = range(w_map) if direction == 1 else range(w_map - 1, -1, -1)

                for c in col_indices:

                    if self.stop_flag: break
                    paused_in_loop = False
                    while not self.drawing_enabled and not self.stop_flag:
                        if not paused_in_loop:
                            if mouse_is_down:
                                try: interception.mouse_up("left"); mouse_is_down = False
                                except Exception as eup: self._log(f"[WARN] Snake pause mouse_up error: {eup}")
                                self._log("Translated: Пауза в 'змейке v10', ЛКМ отпущена.")
                            else: self._log("Translated: Пауза в 'змейке v10'...")
                            self.status_callback("Translated: Translated: Пауза...")
                            paused_in_loop=True
                        time.sleep(0.1)
                    if self.stop_flag: break
                    if paused_in_loop and self.drawing_enabled:
                        self._log("Translated: Возобновление 'змейки v10'.")
                        self.status_callback("Translated: Рисование...")

                    try:
                         is_target = (self.cluster_map[r, c] == cluster_id) and \
                                     (not self.drawn_mask[r, c])
                    except IndexError:
                         is_target = False

                    if is_target:

                        target_x = x0_phys + c * brush + brush // 2
                        target_y = y0_phys + r * brush + brush // 2

                        if not mouse_is_down:

                            interception.move_to(target_x, target_y)
                            if self.stop_flag: break
                            time.sleep(0.01)
                            interception.mouse_down("left")
                            if self.stop_flag:
                                try: interception.mouse_up("left")
                                except Exception as e: pass; break
                            mouse_is_down = True

                            if self.DRAW_DELAY > 0: time.sleep(self.DRAW_DELAY)
                            if self.stop_flag:
                                try: interception.mouse_up("left")
                                except Exception as e: pass; break
                        else:

                            interception.move_to(target_x, target_y)
                            if self.stop_flag:
                                try: interception.mouse_up("left")
                                except Exception as e: pass; break

                        self.drawn_mask[r, c] = True
                        if self.pixel_update_callback: self.pixel_update_callback()

                    else:

                        if mouse_is_down:

                            try:
                                interception.mouse_up("left")
                                mouse_is_down = False

                                if self.DRAW_DELAY > 0: time.sleep(self.DRAW_DELAY)
                                if self.stop_flag: break
                                time.sleep(0.01)
                            except Exception as eup: self._log(f"[WARN] Snake v10 mouse_up (non-target) error: {eup}")

                            pass

                if mouse_is_down:
                    try:

                        interception.mouse_up("left")
                        mouse_is_down = False
                        self._log("Translated: [DEBUG] SnakeFill v10: ЛКМ отпущена в конце строки.")
                        time.sleep(0.01)
                    except Exception as eup_eol: self._log(f"[WARN] Snake v10 end_of_line mouse_up error: {eup_eol}")

                if self.stop_flag: break

        except Exception as e:
            self._log(f"Translated: [ERROR] Translated: Ошибка в цикле 'змейки v10': {e}", True)
            traceback.print_exc()
            self.stop_flag = True
        finally:

            if mouse_is_down:
                try: interception.mouse_up("left")
                except Exception as eup_final: self._log(f"[WARN] Snake v10 finally mouse_up error: {eup_final}")

        if self.stop_flag:
            self._log(f"Translated: [INFO] Рисование 'змейкой v10' прервано флагом стоп для ID {cluster_id}.")
        else:
            self._log(f"Translated: [INFO] Рисование 'змейкой v10' завершено для ID {cluster_id}.")

    def draw_image(self):
        """
        Переключает состояние рисования (Старт/Пауза/Возобновить).
        Добавлено принудительное self.stop_flag = False перед стартом нового потока.
        """

        if self.is_waiting_for_hex_click:
            self._log("Translated: Отмена ожидания клика для HEX поля из-за старта/паузы рисования.")
            if hasattr(self, 'mouse_listener') and self.mouse_listener and self.mouse_listener.is_alive():
                try:
                    self.mouse_listener.stop()
                except Exception as e_stop:
                    self._log(f"Translated: [WARN] Не удалось остановить mouse_listener: {e_stop}", True)
            self.is_waiting_for_hex_click = False

            self.status_callback("Translated: Нажмите F5 и кликните на поле HEX снова.")
            return False

        if self.drawing_enabled:
            self.drawing_enabled = False
            self._log("Translated: Пауза.")
            self.status_callback("Translated: Пауза.")

            return False

        else:

            if self.draw_region is None:
                self._log("Translated: Нельзя начать: Translated: Область не выбрана.", True)
                self.status_callback("Translated: Translated: Ошибка: Translated: Область не выбрана.")
                return False
            if not self.IMAGE_PATH:
                self._log("Нельзя начать: Translated: Изображение не выбрано.", True)
                self.status_callback("Translated: Ошибка: Translated: Изображение не выбрано.")
                return False
            if self.hex_input_coord is None:
                error_msg = "Translated: [ERROR] Координаты поля HEX не установлены! Нажмите F5 и кликните на поле."
                self._log(error_msg, True)
                self.status_callback("show_hex_error_popup:" + error_msg)
                return False
            if not self.color_palette or self.cluster_map is None:
                self._log("Translated: Нельзя начать: Палитра/карта не готовы (ошибка подготовки?).", True)
                self.status_callback("Translated: Translated: Ошибка: Данные изображения не готовы.")
                return False

            if self.current_color_index >= len(self.color_palette) and len(self.color_palette) > 0:
                self._log("Translated: Рисование уже завершено для этого изображения/палитры.", True)
                self.status_callback("Translated: Рисование завершено.")
                self.drawing_enabled = False
                return False

            self.drawing_enabled = True
            self.status_callback("Translated: Рисование...")

            if self.drawing_thread is not None and self.drawing_thread.is_alive():
                self._log("Translated: Возобновление.")

                return True

            else:
                self._log("Translated: Старт.")

                self.stop_flag = False
                self._log(f"Translated: Флаг stop_flag установлен в {self.stop_flag} перед запуском потока.")

                self.drawing_thread = threading.Thread(target=self.draw_colors_thread, daemon=True,
                                                       name="draw_colors_thread")
                self.drawing_thread.start()
                return True

    def draw_current_color(self):
        """
        Организует рисование всех областей текущего выбранного цвета,
        используя выбранный режим рисования (`self.drawing_mode`).
        """

        if self.draw_region is None or not self.color_palette or self.cluster_map is None or self.drawn_mask is None:
            self._log("Translated: [WARN] Пропуск draw_current_color: нет области/палитры/карты/маски.", True)
            return
        if self.current_color_index >= len(self.color_palette):

            self._log(
                f"Translated: [INFO] Пропуск draw_current_color: индекс {self.current_color_index} достиг конца палитры (длина {len(self.color_palette)}).")
            return
        if self.stop_flag:
            self._log("Translated: [INFO] Пропуск draw_current_color: установлен stop_flag.")
            return

        try:
            hex_color, cluster_id, pcount, _ = self.color_palette[self.current_color_index]
        except IndexError:
            self._log(
                f"Translated: [ERROR] draw_current_color: Translated: Ошибка индекса {self.current_color_index} при доступе к палитре (длина {len(self.color_palette)}).",
                True)
            self.stop_flag = True
            return
        except Exception as e:
            self._log(f"Translated: [ERROR] draw_current_color: Неожиданная ошибка при получении цвета из палитры: {e}", True)
            self.stop_flag = True
            return

        self._log(
            f"[DRAW {self.current_color_index + 1}/{len(self.color_palette)}] Цвет {hex_color} (ID:{cluster_id}, ~{pcount}px) Translated: Режим: {self.drawing_mode}...")
        self.status_callback(
            f"Translated: Рисуем {self.current_color_index + 1}/{len(self.color_palette)}: {hex_color} ({self.drawing_mode})")

        if self.stop_flag: return
        try:
            self.pick_color(hex_color)
        except Exception as e:
            self._log(f"Translated: [ERROR] Translated: Ошибка во время pick_color для {hex_color}: {e}", True)
            self.stop_flag = True

            self.status_callback(f"Translated: Translated: Ошибка выбора цвета {hex_color}! Translated: Рисование остановлено.")
            return

        if self.stop_flag:
            self._log(f"Translated: Остановка (stop_flag=True) после pick_color для {hex_color}.")
            return

        try:

            target_mask = (self.cluster_map == cluster_id) & (~self.drawn_mask)

            if not np.any(target_mask):
                self._log(f"Translated: Для цвета {hex_color} нет новых не нарисованных областей (маска пуста). Пропуск.")

                return
        except AttributeError as ae:
            self._log(
                f"Translated: [ERROR] Translated: Ошибка создания маски (AttributeError): Возможно, cluster_map или drawn_mask не инициализированы. {ae}",
                True)
            self.stop_flag = True
            return
        except Exception as mask_err:
            self._log(f"Translated: [ERROR] Translated: Ошибка создания маски для цвета {hex_color} (ID {cluster_id}): {mask_err}", True)
            traceback.print_exc()
            self.stop_flag = True
            return

        if self.stop_flag:
            self._log(f"Translated: Остановка (stop_flag=True) после создания маски для {hex_color}.")
            return

        self._log(f"Translated: Запуск режима '{self.drawing_mode}' для цвета {hex_color}...")
        try:
            if self.drawing_mode == self.MODE_FLOOD_FILL:

                mask_u8 = target_mask.astype(np.uint8) * 255
                if self.stop_flag: return

                try:
                    contours, _ = cv2.findContours(mask_u8.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                except Exception as contour_err:
                    self._log(f"Translated: [ERROR] Translated: Ошибка findContours (FloodFill) для цвета {hex_color}: {contour_err}", True)
                    self.stop_flag = True
                    return

                if self.stop_flag: return

                if not contours:
                    self._log(
                        f"Translated: Для цвета {hex_color} (FloodFill) нет контуров в маске (маска не пуста). Помечаем оставшиеся пиксели.")

                    try:
                        self.drawn_mask[target_mask] = True
                        if self.pixel_update_callback: self.pixel_update_callback()
                    except Exception as mark_err:
                        self._log(
                            f"Translated: [WARN] Не удалось пометить пиксели из target_mask как нарисованные при отсутствии контуров: {mark_err}",
                            True)
                    return

                self._log(f"Translated: Найдено {len(contours)} областей (FloodFill) для {hex_color}.")
                processed_contours = 0
                for i, cnt in enumerate(contours):

                    if self.stop_flag:
                        self._log(
                            f"Translated: Остановка (stop_flag) перед обработкой контура {i + 1}/{len(contours)} (FloodFill).")
                        break

                    paused_in_loop = False
                    while not self.drawing_enabled and not self.stop_flag:
                        if not paused_in_loop: self._log(
                            f"Translated: Пауза (FloodFill) контур {i + 1}/{len(contours)}..."); paused_in_loop = True
                        time.sleep(0.1)

                    if self.stop_flag:
                        self._log(f"Translated: Остановка (stop_flag) после паузы для контура {i + 1}/{len(contours)} (FloodFill).")
                        break
                    if paused_in_loop and self.drawing_enabled: self._log("Translated: Возобновление (FloodFill).")

                    if cnt is not None and len(cnt) > 0:
                        try:
                            sp = cnt[0][0]
                            start_col, start_row = int(sp[0]), int(sp[1])

                            if self.stop_flag: break

                            self.flood_fill_draw(mask_u8.copy(), start_row, start_col, 0, 0)

                            if self.stop_flag:
                                self._log(
                                    f"Translated: Остановка (stop_flag) после flood_fill_draw для контура {i + 1}/{len(contours)}.")
                                break
                            processed_contours += 1
                        except IndexError:
                            self._log(
                                f"Translated: [WARN] Не удалось получить стартовую точку из контура {i + 1}/{len(contours)} (FloodFill).")

                    else:
                        self._log(f"Translated:   Пропуск области {i + 1}/{len(contours)} (FloodFill): некорректный контур.")

                if not self.stop_flag:
                    self._log(f"Translated: Завершена обработка {hex_color} (FloodFill). Обработано {processed_contours} областей.")

            elif self.drawing_mode == self.MODE_LEGIT:

                mask_u8 = target_mask.astype(np.uint8) * 255

                if self.stop_flag: return

                try:

                    contours, _ = cv2.findContours(mask_u8.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                except Exception as contour_err:

                    self._log(f"Translated: [ERROR] Translated: Ошибка findContours (Legit) для цвета {hex_color}: {contour_err}", True)

                    self.stop_flag = True

                    return

                if self.stop_flag: return

                if not contours:

                    self._log(f"Translated: Для цвета {hex_color} (Legit) нет контуров в маске.")

                    try:

                        if np.any(target_mask):

                            self.drawn_mask[target_mask] = True

                            if self.pixel_update_callback: self.pixel_update_callback()

                    except Exception as mark_err:

                        self._log(f"Translated: [WARN] Не удалось пометить пиксели (Legit) при отсутствии контуров: {mark_err}",
                                  True)

                    return

                self._log(f"Translated: Найдено {len(contours)} областей (Legit) для {hex_color}.")

                processed_contours = 0

                for i, cnt in enumerate(contours):

                    if self.stop_flag:
                        self._log(f"Translated: Остановка (stop_flag) перед обработкой контура {i + 1}/{len(contours)} (Legit).")

                        break

                    paused_in_loop = False

                    while not self.drawing_enabled and not self.stop_flag:

                        if not paused_in_loop: self._log(
                            f"Translated: Пауза (Legit) контур {i + 1}/{len(contours)}..."); paused_in_loop = True

                        time.sleep(0.1)

                    if self.stop_flag:
                        self._log(f"Translated: Остановка (stop_flag) после паузы для контура {i + 1}/{len(contours)} (Legit).")

                        break

                    if paused_in_loop and self.drawing_enabled: self._log("Translated: Возобновление (Legit).")

                    if cnt is not None and len(cnt) > 0:

                        try:

                            sp = cnt[0][0]

                            start_col, start_row = int(sp[0]), int(sp[1])

                            if self.stop_flag: break

                            self.legit_draw(mask_u8.copy(), start_row, start_col)

                            if self.stop_flag:
                                self._log(
                                    f"Translated: Остановка (stop_flag) после legit_draw для контура {i + 1}/{len(contours)}.")

                                break

                            processed_contours += 1

                        except IndexError:

                            self._log(
                                f"Translated: [WARN] Не удалось получить стартовую точку из контура {i + 1}/{len(contours)} (Legit).")

                    else:

                        self._log(f"Translated:   Пропуск области {i + 1}/{len(contours)} (Legit): некорректный контур.")

                if not self.stop_flag:
                    self._log(f"Translated: Завершена обработка {hex_color} (Legit). Обработано {processed_contours} областей.")

            elif self.drawing_mode == self.MODE_SNAKE:

                self.snake_fill_draw(cluster_id)

            else:

                self._log(f"Translated: [ERROR] Неизвестный режим рисования: {self.drawing_mode}", True)
                self.status_callback(f"Translated: Translated: Ошибка: Неизвестный режим {self.drawing_mode}")
                self.stop_flag = True

        except Exception as e:

            self._log(f"Translated: [ERROR] Неожиданная ошибка в draw_current_color для {hex_color}: {e}", True)
            traceback.print_exc()
            self.status_callback(f"Translated: Критическая ошибка при рисовании цвета {hex_color}!")
            self.stop_flag = True

        if self.stop_flag:
            self._log(f"Translated: Остановка (stop_flag) подтверждена в конце draw_current_color для {hex_color}.")

    def draw_colors_thread(self):

        self._log("Translated: Поток рисования запущен.")
        log_prefix = "[DRAW THREAD SEES]"
        try:
            self._log(
                f"{log_prefix} Image='{getattr(self, 'IMAGE_PATH', 'N/A')}', Region={getattr(self, 'draw_region', 'N/A')}")
            _cm = getattr(self, 'cluster_map', None)
            _cp = getattr(self, 'color_palette', None)
            _dm = getattr(self, 'drawn_mask', None)

            if _cm is not None:
                self._log(f"{log_prefix} cluster_map ID={id(_cm)}, shape={_cm.shape}")
            else:
                self._log(f"{log_prefix} cluster_map is None")

            if _cp is not None:
                self._log(f"{log_prefix} color_palette ID={id(_cp)}, length={len(_cp)}")
            else:
                self._log(f"{log_prefix} color_palette is None")

            if _dm is not None:
                self._log(f"{log_prefix} drawn_mask ID={id(_dm)}, shape={_dm.shape}")
            else:
                self._log(f"{log_prefix} drawn_mask is None")
        except Exception as log_err:
            self._log(f"Translated: [ERROR] Translated: Ошибка при логировании в draw_colors_thread: {log_err}")

        while self.current_color_index < len(self.color_palette) and not self.stop_flag:
            while not self.drawing_enabled and not self.stop_flag: time.sleep(0.1)
            if self.stop_flag: self._log("Translated: Остановка потока по флагу."); break
            self.draw_current_color()
            if self.stop_flag: self._log("Translated: Остановка потока после цвета."); break
            self.current_color_index += 1
        if self.stop_flag: self._log("Translated: Поток остановлен."); self.status_callback("drawing_stopped")
        elif self.current_color_index >= len(self.color_palette):
             self._log("Translated: Поток завершен."); self.status_callback("drawing_complete"); self.drawing_enabled = False
        else: self._log("Translated: Поток завершился неожиданно.", True)

    def get_preview_image(self):
        """
        Возвращает изображение для превью с ПРОЗРАЧНЫМ фоном.
        В Translated: Ч/Б режиме отображает выбранные цвета (черный/белый/оба) на прозрачном фоне.
        В Цветном режиме отображает результат KMeans с прозрачным фоном.
        """
        if self.cluster_map is None:
            self._log("Translated: [WARN] get_preview_image: cluster_map is None, возвращаем None.", True)
            return None

        try:
            h, w = self.cluster_map.shape
            if h <= 0 or w <= 0:
                 self._log(f"Translated: [WARN] get_preview_image: cluster_map имеет неверные размеры {h}x{w}.", True)
                 return None

            preview_array = np.zeros((h, w, 4), dtype=np.uint8)

            if self.mode == 'bw':

                background_mask = (self.cluster_map == -1)

                if self.bw_draw_mode in ['both', 'black_only']:
                    black_mask = (self.cluster_map == 1) & (~background_mask)
                    preview_array[black_mask] = [0, 0, 0, 255]

                if self.bw_draw_mode in ['both', 'white_only']:
                    white_mask = (self.cluster_map == 0) & (~background_mask)
                    preview_array[white_mask] = [255, 255, 255, 255]

            elif self.mode == 'color':

                if self.image_rgb is not None and isinstance(self.image_rgb, np.ndarray) \
                   and self.image_rgb.shape[:2] == (h, w) and self.image_rgb.size > 0:

                    alpha_for_preview = np.full((h, w), 255, dtype=np.uint8)
                    background_mask = (self.cluster_map == -1)
                    alpha_for_preview[background_mask] = 0

                    preview_array[:, :, :3] = self.image_rgb

                    preview_array[:, :, 3] = alpha_for_preview

                else:

                    self._log("Translated: [WARN] get_preview_image (color mode): self.image_rgb не готов или некорректен, превью будет прозрачным.", True)

            else:
                 self._log(f"Translated: [WARN] get_preview_image: Неизвестный режим '{self.mode}', превью будет прозрачным.", True)

            return Image.fromarray(preview_array, mode='RGBA')

        except Exception as e:

            self._log(f"Translated: [ERROR] Translated: Ошибка создания превью (начальная): {e}", True)

            try:
                 if 'h' in locals() and 'w' in locals() and h > 0 and w > 0:
                     return Image.fromarray(np.zeros((h, w, 3), dtype=np.uint8), mode='RGB')
            except: pass
            return None

    def get_draw_region_aspect_ratio(self):
        if self.draw_region: x, y, w, h = self.draw_region; return w/h if h > 0 else None
        return None

    def get_progress_info(self):
        """
        Рассчитывает прогресс рисования на основе пикселей, которые *должны* быть нарисованы
        в соответствии с текущим режимом и настройками.

        Возвращает:
            tuple: (drawn_count, total_target_count)
                   drawn_count: Количество целевых пикселей, уже помеченных как нарисованные.
                   total_target_count: Общее количество пикселей, которые предполагается нарисовать.
        """
        if self.drawn_mask is None or self.cluster_map is None:

            return 0, 0

        target_mask = np.zeros_like(self.cluster_map, dtype=bool)

        if self.mode == 'color':

            target_mask = (self.cluster_map != -1)
        elif self.mode == 'bw':
            if self.bw_draw_mode == 'both':

                target_mask = (self.cluster_map != -1)
            elif self.bw_draw_mode == 'black_only':

                target_mask = (self.cluster_map == 1)
            elif self.bw_draw_mode == 'white_only':

                target_mask = (self.cluster_map == 0)

        total_target_count = np.count_nonzero(target_mask)

        if total_target_count == 0:

            if np.any(self.cluster_map != -1):

                return 0, 0
            else:

                return 1, 1

        drawn_target_count = np.count_nonzero(self.drawn_mask & target_mask)

        return drawn_target_count, total_target_count

    def stop_script(self):

        if hasattr(self, 'mouse_listener') and self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
            self._log("Translated: Прослушиватель мыши остановлен принудительно.")
        self.is_waiting_for_hex_click = False

        self.stop_flag = True; self.drawing_enabled = False; self._log("Translated: Получен сигнал стоп.")
    def register_hotkeys(self, new_drawing_callback, stop_callback):
        try: keyboard.add_hotkey('F1',self.select_area); keyboard.add_hotkey('F2',self.draw_image); keyboard.add_hotkey('F3',stop_callback); keyboard.add_hotkey('F4',new_drawing_callback); keyboard.add_hotkey('F5', self.start_hex_coord_capture); self._log("Translated: Горячие клавиши: F1(Обл), F2(Старт/Пауза), F3(Стоп), F4(Сброс), F5(HEX Поле)")
        except Exception as e: self._log(f"Hotkey error: {e}.", True)

    def reset_for_new_drawing(self):
        """
        Останавливает рисование и сбрасывает состояние для НОВОГО РИСУНКА.
        Сохраняет текущие настройки и HEX-координаты.
        Пытается дождаться завершения потока и сбрасывает состояние только при успехе.
        """
        self._log("Translated: Подготовка к новому рисунку...")
        original_thread = self.drawing_thread
        joined_successfully = False

        self.stop_flag = True
        self.drawing_enabled = False

        if original_thread is not None and original_thread.is_alive():

            time.sleep(0.05)
            if original_thread.is_alive():

                wait_time = 5.0
                self._log(f"Translated: Ожидание завершения потока {original_thread.name} (до {wait_time} сек)...")
                original_thread.join(wait_time)

                if original_thread.is_alive():

                    self._log(f"Translated: [ERROR] Поток {original_thread.name} не завершился за {wait_time} сек!")

                else:

                    self._log(f"Translated: Поток {original_thread.name} успешно завершен.")
                    joined_successfully = True
            else:

                self._log(f"Translated: Поток {original_thread.name} завершился быстро.")
                joined_successfully = True
        else:

            self._log("Translated: Предыдущий поток рисования не был активен.")
            joined_successfully = True

        self.drawing_thread = None

        if hasattr(self, 'mouse_listener') and self.mouse_listener and self.mouse_listener.is_alive():
            try:
                self.mouse_listener.stop()
                self._log("Translated: Прослушиватель мыши остановлен при сбросе.")
            except Exception as e:
                self._log(f"Translated: Translated: Ошибка остановки прослушивателя мыши при сбросе: {e}", True)
            self.mouse_listener = None
        self.is_waiting_for_hex_click = False

        if joined_successfully:
            self._log("Translated: Сброс состояния рисования после подтвержденной остановки потока.")
            self.color_palette = []
            self.current_color_index = 0
            self.drawn_mask = None
            self.cluster_map = None
            self.image_rgb = None
            self.IMAGE_PATH = self.DEFAULT_IMAGE_PATH
            self.draw_region = None
            self.image_original_rgba = None
            self.has_transparency = False
            self.background_mask = None

            self.stop_flag = False
            status_message = "Translated: Готово к выбору нового изображения и области."
        else:

            self._log("Translated: [WARN] Предыдущий поток рисования не завершился. Состояние не было сброшено для предотвращения ошибок. Рекомендуется перезапуск.")
            status_message = "Translated: [ERROR] Translated: Ошибка сброса: старый поток еще активен! Перезапустите программу."

        if self.status_callback:

            self.status_callback(status_message)

            if joined_successfully:
                self.status_callback("reset_progress")

        if self.preview_callback:
            self.preview_callback()

        if joined_successfully:
            self._log("Translated: Сброс для нового рисунка завершен успешно.")
        else:
            self._log("Translated: Сброс для нового рисунка завершен с ошибкой (поток не остановлен).")

    def reset_settings_to_default(self):
        """
        Сбрасывает ТОЛЬКО настройки рисования к значениям по умолчанию.
        Также очищает производные данные (палитру, карту), т.к. они устарели.
        Не влияет на текущий выбор файла/области или прогресс рисования (если идет).
        """
        self._log("Translated: Translated: Сброс настроек к значениям по умолчанию...")

        self.DRAW_DELAY = self.DEFAULT_DRAW_DELAY
        self.K_CLUSTERS = self.DEFAULT_K_CLUSTERS
        self.BRUSH_SIZE = self.DEFAULT_BRUSH_SIZE
        self.REMOVE_BACKGROUND = self.DEFAULT_REMOVE_BACKGROUND
        self.BG_TOLERANCE = self.DEFAULT_BG_TOLERANCE
        self.ALPHA_THRESHOLD = self.DEFAULT_ALPHA_THRESHOLD
        self.mode = self.DEFAULT_MODE
        self.bw_draw_mode = self.DEFAULT_BW_DRAW_MODE
        self.drawing_mode = self.DEFAULT_DRAWING_MODE

        if not self.drawing_enabled:
            self.color_palette = []

            self.drawn_mask = None
            self.cluster_map = None
            self.image_rgb = None
            self.has_transparency = False
            self.background_mask = None
            if self.preview_callback:
                self.preview_callback()
            if self.pixel_update_callback:
                self.pixel_update_callback()
            self._log("Translated: Производные данные (карта, палитра) очищены из-за смены настроек.")
        else:
            self._log("Translated: [WARN] Попытка сбросить настройки во время активного рисования!")
        self._log("Translated: Translated: Настройки сброшены.")

    def cleanup_before_exit(self):
        "Translated: ""Очищает ресурсы перед закрытием приложения."""
        self._log("Translated: Очистка OlegPainter перед выходом...");
        self.stop_flag=True;
        self.drawing_enabled=False

        if hasattr(self, 'mouse_listener') and self.mouse_listener and self.mouse_listener.is_alive():
            try:
                self.mouse_listener.stop()

                self._log("Translated: Прослушиватель мыши остановлен при выходе.")
            except Exception as e:
                self._log(f"Translated: Translated: Ошибка остановки прослушивателя мыши при выходе: {e}", True)
            finally:
                self.mouse_listener = None
        self.is_waiting_for_hex_click = False

        thread_to_join = self.drawing_thread
        if thread_to_join and thread_to_join.is_alive():
            self._log(f"Translated: Ожидание завершения потока {thread_to_join.name} при выходе (до 1.5 сек)...")
            thread_to_join.join(1.5)
            if thread_to_join.is_alive():

                 self._log(f"Translated: [WARN] Поток {thread_to_join.name} не завершился при выходе! Может остаться в фоне.", True)
        self.drawing_thread = None

        try:
             if 'keyboard' in sys.modules:
                  keyboard.remove_all_hotkeys()
                  self._log("Translated: Хоткеи сняты.")
             else:
                  self._log("Translated: Библиотека keyboard не была загружена, хоткеи не снимались.")
        except Exception as e:
             self._log(f"Translated: [ERROR] Translated: Ошибка снятия хоткеев: {e}\n{traceback.format_exc()}", True)

        try:

             cv2.destroyAllWindows()
             self._log("Translated: Окна OpenCV принудительно закрыты.")
        except Exception as e:
             self._log(f"Translated: [WARN] Translated: Ошибка при вызове cv2.destroyAllWindows(): {e}", True)

        self._log("Translated: Очистка OlegPainter завершена.")

class OlegPainterGUI(ctk.CTk):

    def __init__(self, painter: OlegPainter):
        super().__init__()
        self.painter = painter
        self.preview_image_ref = None
        self.stencil_window = None
        self.preview_update_job_id = None

        ctk.set_appearance_mode("dark")
        self.title("OlegPainter Pro 1.2")
        self.geometry("460x720+50+50")
        self.minsize(440, 785)
        self.resizable(True, True)

        try:
            icon_path = 'pro1.2.ico'
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'): base_path = sys._MEIPASS
            else: base_path = os.path.abspath(".")
            icon_full_path = os.path.join(base_path, icon_path)
            if os.path.exists(icon_full_path):
                 try: self.iconbitmap(icon_full_path)
                 except Exception as icon_err: print(f"[GUI WARN] Iconbitmap error: {icon_err}")
            else: print(f"[GUI WARN] Icon not found: {icon_full_path}")
        except Exception as e: print(f"[GUI WARN] Icon setup error: {e}")

        self.default_font = ("Segoe UI Black", 14)
        self.bold_font = ("Segoe UI Black", 14, "bold")
        self.pad_y = 5
        self.pad_x = 10
        widget_corner_radius = 16

        self.available_sections = ["Translated: Управление", "Translated: Настройки"]
        self.current_section_index = 0

        self.switcher_font = ctk.CTkFont(
            family="Segoe UI Black",
            size=16,
            )

        switcher_frame = ctk.CTkFrame(
            self,
            fg_color="#212121",
            corner_radius=widget_corner_radius,
            height=48,
            border_width=1,
            border_color="gray50"
            )

        switcher_frame.pack(side="top",
                            pady=self.pad_y,
                            anchor="n")
        switcher_frame.columnconfigure(1, weight=1)

        arrow_cfg = dict(width=28, height=28, font=("Segoe UI Black", 14), fg_color="transparent", border_width=0, text_color="#666666", hover_color="#333333", corner_radius=0)

        self.btn_prev = ctk.CTkButton(switcher_frame, text="❮",
                                      command=self.show_previous_section,
                                      **arrow_cfg)
        self.btn_prev.grid(row=0, column=0, padx=(6, 2), pady=4)

        self.btn_next = ctk.CTkButton(switcher_frame, text="❯",
                                      command=self.show_next_section,
                                      **arrow_cfg)
        self.btn_next.grid(row=0, column=2, padx=(2, 6), pady=4)

        self.lbl_section_name = ctk.CTkLabel(
            switcher_frame,
            text=self.available_sections[self.current_section_index],
            font=self.switcher_font,
            text_color="#FEFEFE")
        self.lbl_section_name.grid(row=0, column=1, sticky="nsew", pady=(4, 0))

        self.indicator_box = ctk.CTkFrame(switcher_frame, fg_color="transparent", height=4)
        self.indicator_box.grid(row=1, column=1, pady=(0, 2))

        bar_cfg = dict(width=24, height=4, corner_radius=2, fg_color="#505050")
        self.ind_left = ctk.CTkFrame(self.indicator_box, **bar_cfg)
        self.ind_right = ctk.CTkFrame(self.indicator_box, **bar_cfg)
        self.ind_left.pack(side="left", padx=4)
        self.ind_right.pack(side="left", padx=4)

        self.content_placeholder_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_placeholder_frame.pack(side="top", fill="both", expand=True, padx=self.pad_x, pady=0)

        self.control_content_frame = ctk.CTkFrame(self.content_placeholder_frame, fg_color="transparent")

        self.settings_content_frame = ctk.CTkFrame(self.content_placeholder_frame, fg_color="transparent", corner_radius=0)

        control_inner_pad_x = self.pad_x
        control_inner_pad_y = self.pad_y
        button_style = {"font": self.default_font, "corner_radius": widget_corner_radius}
        self.btn_select_image = ctk.CTkButton(self.control_content_frame, text="Translated: Выбрать изображение", command=self.select_image, **button_style)
        self.btn_select_image.pack(pady=control_inner_pad_y, padx=control_inner_pad_x, fill="x")
        self.btn_select_area = ctk.CTkButton(self.control_content_frame, text="Translated: Область (F1)", command=self.painter.select_area, **button_style)
        self.btn_select_area.pack(pady=control_inner_pad_y, padx=control_inner_pad_x, fill="x")
        self.btn_draw = ctk.CTkButton(self.control_content_frame, text="Translated: Старт/Пауза (F2)", command=self.toggle_drawing, **button_style)
        self.btn_draw.pack(pady=control_inner_pad_y, padx=control_inner_pad_x, fill="x")
        self.btn_new_drawing = ctk.CTkButton(self.control_content_frame, text="Translated: Translated: Новый рисунок (F4)", command=self.start_new_drawing_gui, **button_style)
        self.btn_new_drawing.pack(pady=control_inner_pad_y, padx=control_inner_pad_x, fill="x")
        self.btn_stop = ctk.CTkButton(self.control_content_frame, text="Translated: Стоп/Translated: Выход (F3)", command=self.stop_script, **button_style)
        self.btn_stop.pack(pady=control_inner_pad_y, padx=control_inner_pad_x, fill="x")
        self.btn_set_hex = ctk.CTkButton(self.control_content_frame, text="Translated: Задать HEX поле (F5)", command=self.painter.start_hex_coord_capture, **button_style)
        self.btn_set_hex.pack(pady=control_inner_pad_y, padx=control_inner_pad_x, fill="x")
        self.btn_toggle_stencil = ctk.CTkButton(self.control_content_frame, text="Translated: Включить трафарет",
                                                command=self.toggle_stencil, **button_style)
        self.btn_toggle_stencil.pack(pady=control_inner_pad_y, padx=control_inner_pad_x, fill="x")

        settings_inner_pad_x = self.pad_x
        settings_inner_pad_y = self.pad_y

        mode_frame = ctk.CTkFrame(self.settings_content_frame, fg_color="transparent")
        mode_frame.pack(fill="x", pady=settings_inner_pad_y, padx=settings_inner_pad_x)
        mode_frame.columnconfigure(0, weight=1); mode_frame.columnconfigure(1, weight=0)
        ctk.CTkLabel(mode_frame, text="Translated: Режим:", font=self.default_font, anchor='w').grid(row=0, column=0, sticky="w")
        self.mode_switch_var = tk.IntVar(value=1 if self.painter.mode == "color" else 0)
        self.mode_switch = ctk.CTkSwitch(mode_frame, text="Translated: Цветной", variable=self.mode_switch_var, onvalue=1, offvalue=0, command=self.toggle_mode_switch, font=self.default_font)
        self.mode_switch.grid(row=0, column=1, sticky="e")
        initial_mode_text = 'Translated: Цветной' if self.painter.mode == "color" else 'Translated: Ч/Б'
        self.mode_switch.configure(text=initial_mode_text)

        self.bw_options_frame = ctk.CTkFrame(self.settings_content_frame, fg_color="transparent")
        ctk.CTkLabel(self.bw_options_frame, text="Translated: Рисовать в Translated: Ч/Б:", font=self.default_font).pack(side="top", anchor="center", padx=0, pady=(0, 2))
        bw_radio_inner_frame = ctk.CTkFrame(self.bw_options_frame, fg_color="transparent")
        bw_radio_inner_frame.pack(fill="x", expand=True, anchor="center", pady=(0, self.pad_y / 2))
        self.bw_draw_mode_var = tk.StringVar(value=self.painter.bw_draw_mode)
        bw_mode_options = [("Translated: Оба", "Translated: both"), ("Черный", "Translated: black_only"), ("Белый", "white_only")]
        self.bw_mode_radios = []
        num_buttons = len(bw_mode_options); [bw_radio_inner_frame.columnconfigure(i, weight=1, uniform="bw_radio") for i in range(num_buttons)]
        INDICATOR_SIZE = 16
        radio_border_width = 2
        for i, (text, value) in enumerate(bw_mode_options):
            rb = ctk.CTkRadioButton(bw_radio_inner_frame, text=text, font=self.default_font, variable=self.bw_draw_mode_var, value=value, command=self.change_bw_draw_mode, radiobutton_width=INDICATOR_SIZE, radiobutton_height=INDICATOR_SIZE, border_width_checked=radio_border_width, border_width_unchecked=radio_border_width)
            rb.grid(row=0, column=i, padx=5, pady=2, sticky="")
            self.bw_mode_radios.append(rb)
        self.bw_options_frame.pack(fill="x", pady=(0, settings_inner_pad_y), padx=settings_inner_pad_x)

        drawing_mode_frame = ctk.CTkFrame(self.settings_content_frame, fg_color="transparent")

        drawing_mode_frame.pack(fill="x", pady=settings_inner_pad_y, padx=settings_inner_pad_x)

        ctk.CTkLabel(drawing_mode_frame, text="Translated: Режим рисования:", font=self.default_font).pack(side="left",
                                                                                               padx=(0, 10))

        drawing_mode_button_texts = ["Translated: Обычный", "Translated: Легит", "Translated: Змейка"]

        self._drawing_mode_map = {
            "Translated: Обычный": OlegPainter.MODE_FLOOD_FILL,
            "Translated: Легит": OlegPainter.MODE_LEGIT,
            "Translated: Змейка": OlegPainter.MODE_SNAKE
        }

        self._drawing_mode_rev_map = {v: k for k, v in self._drawing_mode_map.items()}

        self.drawing_mode_var = tk.StringVar()

        self.seg_button_draw_mode = ctk.CTkSegmentedButton(
            master=drawing_mode_frame,
            values=drawing_mode_button_texts,
            variable=self.drawing_mode_var,
            command=self.change_drawing_mode,
            font=self.default_font,
            height=30,
            corner_radius=widget_corner_radius
        )

        self.seg_button_draw_mode.pack(side="left", expand=True, fill="x")

        initial_button_text = self._drawing_mode_rev_map.get(
            self.painter.drawing_mode,
            "Translated: Обычный"
        )
        self.drawing_mode_var.set(initial_button_text)

        params_inner_frame = ctk.CTkFrame(self.settings_content_frame, fg_color="transparent")
        params_inner_frame.pack(fill="x", pady=0, padx=settings_inner_pad_x)
        self.slider_brush_size, self.brush_size_val_label = self.create_ctk_slider(params_inner_frame, "Translated: Кисть:", 1, 20, self.painter.BRUSH_SIZE, self.debounced_update_brush_size, is_int=True)
        self.slider_draw_delay, self.draw_delay_val_label = self.create_ctk_slider(params_inner_frame, "Translated: Задержка:", 0.0001, 0.05, self.painter.DRAW_DELAY, self.debounced_update_draw_delay, format_str="{:.4f}")
        self.slider_k_clusters, self.k_clusters_val_label = self.create_ctk_slider(params_inner_frame, "Translated: Цвета(K):", 5, 100, self.painter.K_CLUSTERS, self.debounced_update_k_clusters, is_int=True)
        self.slider_bg_tolerance, self.bg_tolerance_val_label = self.create_ctk_slider(params_inner_frame, "Translated: Допуск BG:", 0, 100, self.painter.BG_TOLERANCE, self.debounced_update_bg_tolerance, is_int=True)
        self.slider_alpha_threshold, self.alpha_threshold_val_label = self.create_ctk_slider(params_inner_frame, "Translated: Допуск Альфа:", 0, 254, self.painter.ALPHA_THRESHOLD, self.debounced_update_alpha_threshold, is_int=True)

        bg_remove_frame = ctk.CTkFrame(self.settings_content_frame, fg_color="transparent")
        bg_remove_frame.pack(fill="x", pady=settings_inner_pad_y, padx=settings_inner_pad_x)
        self.remove_bg_var = tk.BooleanVar(value=self.painter.REMOVE_BACKGROUND)
        self.chk_remove_bg = ctk.CTkCheckBox(
            bg_remove_frame,
            text="Translated: Удалять фон (по альфа/углу)",
            font=self.default_font,
            variable=self.remove_bg_var,
            command=self.toggle_remove_background,
            checkbox_width=INDICATOR_SIZE,
            checkbox_height=INDICATOR_SIZE,
            corner_radius=INDICATOR_SIZE // 2,
            border_width=2
            )
        self.chk_remove_bg.pack(side="left", pady=3)

        self.reset_settings_button = ctk.CTkButton(self.settings_content_frame, text="Translated: Сбросить настройки", command=self.reset_settings_gui, font=self.default_font, corner_radius=INDICATOR_SIZE//2)
        self.reset_settings_button.pack(pady=(settings_inner_pad_y * 2, settings_inner_pad_y), padx=settings_inner_pad_x, fill="x")

        self.image_path_label = ctk.CTkLabel(self, text="Translated: Изображение не выбрано", font=self.default_font, anchor="w")
        self.image_path_label.pack(side="top", pady=(self.pad_y, 0), padx=self.pad_x+10, fill="x")

        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.pack(side="top", fill="x", pady=(self.pad_y, 0), padx=self.pad_x+10)
        self.progress_label = ctk.CTkLabel(progress_frame, text="Translated: Прогресс: 0%", font=self.default_font, width=110, anchor="w")
        self.progress_label.pack(side="left")
        prog_bar_bg = ("gray70", "gray30"); prog_bar_fill = ("#4CAF50", "#66BB6A")
        self.progress_bar = ctk.CTkProgressBar(progress_frame, fg_color=prog_bar_bg, progress_color=prog_bar_fill)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.progress_bar.set(0)
        self.pixel_progress_label = ctk.CTkLabel(self, text="Translated: Пикселей: 0 / 0", font=self.default_font, anchor="w")
        self.pixel_progress_label.pack(side="top", pady=(self.pad_y, 0), padx=self.pad_x+10, fill="x")

        self.preview_container = ctk.CTkFrame(self, corner_radius=widget_corner_radius,border_width=1,border_color="gray50")
        self.preview_container.pack(side="top", pady=(self.pad_y, self.pad_y), padx=self.pad_x+10, anchor="n", fill="x",
                                    expand=False)

        self.preview_label = None
        self.preview_image_ref = None

        try:

            self.update_idletasks()

            tk_scale = self.tk.call('tk', 'scaling')
            print(f"[INFO] Tkinter 'tk scaling' reported factor: {tk_scale}")

            if isinstance(tk_scale, (int, float)) and tk_scale > 0:

                self.painter.dpi_scale_factor = float(tk_scale)
                print(f"Translated: [INFO] Установлен painter.dpi_scale_factor из Tkinter: {self.painter.dpi_scale_factor:.2f}")
            else:
                print(f"Translated: [WARN] Некорректный ответ от 'tk scaling' ({tk_scale}), используется painter's default (1.0).")

        except Exception as e:
            print(f"Translated: [WARN] Не удалось получить масштаб от Tkinter: {e}. Используется painter's default (1.0).")

        self.painter.status_callback = self.update_status
        self.painter.pixel_update_callback = self.schedule_progress_update
        self.painter.preview_callback = self.schedule_preview_update
        self.painter.hex_coord_set_callback = self.show_hex_coord_confirmation

        self._update_progress_display()
        self.update_gui_from_painter_state()
        self._update_preview_display()

        self.show_section(self.current_section_index)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.attributes('-topmost', True)

        self.settings_widgets_to_lock = [
             self.slider_brush_size, self.brush_size_val_label,
             self.slider_draw_delay, self.draw_delay_val_label,
             self.slider_k_clusters, self.k_clusters_val_label,
             self.slider_bg_tolerance, self.bg_tolerance_val_label,
             self.slider_alpha_threshold, self.alpha_threshold_val_label,
             self.btn_select_image, self.btn_select_area,
             self.btn_new_drawing,
             self.btn_set_hex,
             self.chk_remove_bg,
             self.reset_settings_button,
             self.mode_switch,
             self.seg_button_draw_mode,
         ] + self.bw_mode_radios
        self.status_label = ctk.CTkLabel(self, text="Translated: Готов.", font=self.default_font, anchor="w", height=28)
        self.status_label.pack(side="bottom", fill="x", padx=self.pad_x + 10, pady=(0, self.pad_y))

    def change_drawing_mode(self, selected_button_text):
        """
        Обработчик нажатия на кнопку выбора режима рисования (CTkSegmentedButton).
        Получает ТЕКСТ нажатой кнопки в аргументе selected_button_text.
        """

        new_mode_internal = self._drawing_mode_map.get(selected_button_text)

        if new_mode_internal and self.painter.drawing_mode != new_mode_internal:

            self.painter.drawing_mode = new_mode_internal

            self.update_status(f"Translated: Режим рисования изменен на: {selected_button_text}")
            self.painter._log(f"Drawing mode changed to: {new_mode_internal}")

    def _recreate_preview_label(self):
        "Translated: ""Уничтожает старый (если есть) и создает новый виджет превью."""

        if self.preview_label and self.preview_label.winfo_exists():
            try:
                self.preview_label.destroy()
            except Exception as e:
                print(f"[GUI WARN] Failed to destroy old preview label: {e}")

        self.preview_label = None
        self.preview_image_ref = None

        try:

            if not hasattr(self, 'preview_container') or not self.preview_container.winfo_exists():
                print("[GUI ERROR] Preview container does not exist, cannot recreate label.")
                return None

            self.preview_label = ctk.CTkLabel(self.preview_container, text="", width=PREVIEW_WIDTH,
                                              height=PREVIEW_HEIGHT, fg_color=("gray80", "gray20"))

            self.preview_label.pack(anchor="center", padx=1, pady=1)

            return self.preview_label
        except Exception as e:
            print(f"[GUI ERROR] Failed to recreate preview label: {e}")
            return None

    def toggle_stencil(self):
        """
        ВЕРСИЯ, ИМИТИРУЮЩАЯ СТАРЫЙ КОД:
        Включает или выключает окно трафарета, используя ФИЗИЧЕСКИЕ координаты
        из painter.draw_region для позиционирования через SetWindowPos.
        """

        if self.stencil_window and self.stencil_window.winfo_exists():

            try:
                self.stencil_window.destroy()
                print("Translated: [INFO] Окно трафарета закрыто.")
            except Exception as e:
                print(f"Translated: [WARN] Не удалось уничтожить окно трафарета: {e}")
            finally:
                self.stencil_window = None
                try:
                    self.btn_toggle_stencil.configure(text="Translated: Включить трафарет")
                    self.update_status("Translated: Трафарет выключен.")
                except Exception as e_cfg:
                     print(f"Translated: [WARN] Не удалось обновить кнопку/статус после закрытия трафарета: {e_cfg}")
            return

        else:

            physical_region_to_use = None
            if hasattr(self.painter, 'draw_region') and self.painter.draw_region:
                coords = self.painter.draw_region

                if isinstance(coords, (tuple, list)) and len(coords) == 4 \
                   and all(isinstance(n, (int, float)) for n in coords) \
                   and coords[2] > 0 and coords[3] > 0:
                    physical_region_to_use = tuple(int(c) for c in coords)
                else:
                    print(f"Translated: [WARN] toggle_stencil: Атрибут draw_region найден, но содержит некорректные данные: {coords}.")

            if physical_region_to_use is None:
                messagebox.showerror("Translated: Ошибка", "Translated: Сначала выберите область (F1)!", parent=self)
                return

            try:
                print(f"Translated: [INFO] toggle_stencil (PhysCoords): Создание трафарета с регионом {physical_region_to_use} из draw_region")
                initial_preview = self.painter.get_preview_image()

                self.stencil_window = StencilWindow(self,
                                                    physical_region=physical_region_to_use,
                                                    initial_pil_image=initial_preview,
                                                    alpha=150)

                self.btn_toggle_stencil.configure(text="Translated: Выключить трафарет")
                self.update_status("Translated: Трафарет вкл. (исп. физ. коорд.)")

            except Exception as e:

                print(f"Translated: [ERROR] Не удалось создать окно трафарета: {e}")
                traceback.print_exc()
                messagebox.showerror("Translated: Translated: Ошибка трафарета", f"Translated: Не удалось создать окно трафарета:\n{e}", parent=self)
                if self.stencil_window:
                    try: self.stencil_window.destroy()
                    except: pass
                self.stencil_window = None
                try: self.btn_toggle_stencil.configure(text="Translated: Включить трафарет")
                except Exception as e_cfg: print(f"Translated: [WARN] Не удалось сбросить кнопку трафарета: {e_cfg}")

    def _update_section_indicators(self):
        active = "#FFFFFF"
        inactive = "#505050"
        if self.current_section_index == 0:
            self.ind_left.configure(fg_color=active)
            self.ind_right.configure(fg_color=inactive)
        else:
            self.ind_left.configure(fg_color=inactive)
            self.ind_right.configure(fg_color=active)

    def show_section(self, index):
        "Translated: ""Показывает фрейм контента для секции с заданным индексом."""
        self.current_section_index = index
        section_name = self.available_sections[index]
        self.lbl_section_name.configure(text=section_name)

        self.control_content_frame.pack_forget()
        self.settings_content_frame.pack_forget()

        if index == 0:
            self.control_content_frame.pack(in_=self.content_placeholder_frame, fill="both", expand=True)
        elif index == 1:
            self.settings_content_frame.pack(in_=self.content_placeholder_frame, fill="both", expand=True)

        self._update_section_indicators()

    def show_previous_section(self):
        "Translated: ""Переключает на предыдущую секцию."""
        new_index = (self.current_section_index - 1) % len(self.available_sections)
        self.show_section(new_index)

    def show_next_section(self):
        "Translated: ""Переключает на следующую секцию."""
        new_index = (self.current_section_index + 1) % len(self.available_sections)
        self.show_section(new_index)

    def toggle_mode_switch(self):
        "Translated: ""Обрабатывает изменение состояния переключателя режима Color/BW."""

        new_mode = "color" if self.mode_switch_var.get() == 1 else "bw"

        if self.painter.mode != new_mode:
            self.painter.mode = new_mode

            mode_text = 'Translated: Цветной' if new_mode == "color" else 'Translated: Ч/Б'

            self.update_status(f"Translated: Translated: Режим: {mode_text}")
            self.painter._log(f"Mode changed to: {new_mode}")

            self.update_kmeans_slider_state()
            self.update_bw_options_state()

            self.mode_switch.configure(text=mode_text)

            self.trigger_prepare_image_if_needed()

    def toggle_remove_background(self):
        "Translated: ""Обрабатывает изменение состояния чекбокса 'Удалять фон'."""

        new_state = self.remove_bg_var.get()

        if self.painter.REMOVE_BACKGROUND != new_state:

            self.painter.REMOVE_BACKGROUND = new_state
            status_msg = f"Translated: Удаление фона: {'Включено' if new_state else 'Выключено'}"

            self.update_status(status_msg)
            self.painter._log(status_msg)

            self.update_tolerance_sliders_state(self.painter.has_transparency)

            self.trigger_prepare_image_if_needed()

    def debounced_update_brush_size(self, value):
        "Translated: ""Планирует обновление размера кисти после паузы."""

        self._pending_brush_size = int(value)

        if hasattr(self, '_brush_size_job'):
            try:
                self.after_cancel(self._brush_size_job)
            except ValueError:
                pass

        self._brush_size_job = self.after(400, self._apply_brush_size)

    def _apply_brush_size(self):
        "Translated: ""Применяет сохраненное значение размера кисти и перерисовывает, если нужно."""

        new_size = getattr(self, '_pending_brush_size', self.painter.BRUSH_SIZE)
        if self.painter.BRUSH_SIZE != new_size:
            self.painter.BRUSH_SIZE = new_size
            self.painter._log(f"Translated: Translated: Кисть: {new_size}")

            self.trigger_prepare_image_if_needed()

    def debounced_update_draw_delay(self, value):
        "Translated: ""Планирует обновление задержки рисования после паузы."""
        self._pending_draw_delay = float(value)
        if hasattr(self, '_draw_delay_job'):
            try:
                self.after_cancel(self._draw_delay_job)
            except ValueError:
                pass
        self._draw_delay_job = self.after(300, self._apply_draw_delay)

    def _apply_draw_delay(self):
        "Translated: ""Применяет сохраненное значение задержки рисования."""
        new_delay = getattr(self, '_pending_draw_delay', self.painter.DRAW_DELAY)
        new_delay = max(0.0, new_delay)
        if self.painter.DRAW_DELAY != new_delay:
            self.painter.DRAW_DELAY = new_delay
            self.painter._log(f"Translated: Translated: Задержка: {self.painter.DRAW_DELAY:.4f}")

    def debounced_update_k_clusters(self, value):
        "Translated: ""Планирует обновление количества кластеров (K) после паузы."""
        self._pending_k_clusters = int(value)
        if hasattr(self, '_k_clusters_job'):
            try:
                self.after_cancel(self._k_clusters_job)
            except ValueError:
                pass
        self._k_clusters_job = self.after(400, self._apply_k_clusters)

    def _apply_k_clusters(self):
        "Translated: ""Применяет сохраненное значение K и перерисовывает, если нужно."""
        new_k = getattr(self, '_pending_k_clusters', self.painter.K_CLUSTERS)
        if self.painter.K_CLUSTERS != new_k:
            self.painter.K_CLUSTERS = new_k
            self.painter._log(f"Translated: Translated: Цвета(K): {new_k}")
            self.trigger_prepare_image_if_needed()

    def debounced_update_bg_tolerance(self, value):
        "Translated: ""Планирует обновление допуска фона (BG Tolerance) после паузы."""
        self._pending_bg_tolerance = int(value)
        if hasattr(self, '_bg_tolerance_job'):
            try:
                self.after_cancel(self._bg_tolerance_job)
            except ValueError:
                pass
        self._bg_tolerance_job = self.after(400, self._apply_bg_tolerance)

    def _apply_bg_tolerance(self):
        "Translated: ""Применяет сохраненное значение допуска фона и перерисовывает, если нужно."""
        new_tolerance = getattr(self, '_pending_bg_tolerance', self.painter.BG_TOLERANCE)
        if self.painter.BG_TOLERANCE != new_tolerance:
            self.painter.BG_TOLERANCE = new_tolerance
            self.painter._log(f"Translated: Допуск фона (BG Tolerance): {new_tolerance}")
            self.trigger_prepare_image_if_needed()

    def debounced_update_alpha_threshold(self, value):
        "Translated: ""Планирует обновление допуска альфа-канала после паузы."""
        self._pending_alpha_threshold = int(value)
        if hasattr(self, '_alpha_threshold_job'):
            try:
                self.after_cancel(self._alpha_threshold_job)
            except ValueError:
                pass
        self._alpha_threshold_job = self.after(400, self._apply_alpha_threshold)

    def _apply_alpha_threshold(self):
        "Translated: ""Применяет сохраненное значение допуска альфа и перерисовывает, если нужно."""
        new_threshold = getattr(self, '_pending_alpha_threshold', self.painter.ALPHA_THRESHOLD)
        if self.painter.ALPHA_THRESHOLD != new_threshold:
            self.painter.ALPHA_THRESHOLD = new_threshold
            self.painter._log(f"Translated: Допуск альфа (Alpha Threshold): {new_threshold}")
            self.trigger_prepare_image_if_needed()

    def trigger_prepare_image_if_needed(self):
        """
        Проверяет, нужно ли пересоздавать палитру/карту, и запускает процесс,
        блокируя и разблокируя интерфейс.
        """

        if self.painter.draw_region and self.painter.IMAGE_PATH:
            self.update_status("Translated: Переподготовка изображения из-за смены настроек...")
            self._set_controls_state("disabled")
            self.update()
            try:

                success = self.painter.prepare_image_and_palette()
                if not success:
                    self.update_status("Translated: [ERROR] Translated: Ошибка переподготовки изображения!")
            except Exception as e:
                self.update_status(f"Translated: [ERROR] Исключение при переподготовке: {e}")
                traceback.print_exc()
            finally:

                self.after(50, self._set_controls_state, "normal")

    def change_bw_draw_mode(self):
        "Translated: ""Обрабатывает смену режима рисования для Translated: Ч/Б."""

        new_bw_mode = self.bw_draw_mode_var.get()

        if self.painter.bw_draw_mode != new_bw_mode:

            self.painter.bw_draw_mode = new_bw_mode

            mode_text = {"Translated: both": "Translated: Оба", "Translated: black_only": "Черный", "Translated: white_only": "Белый"}.get(new_bw_mode,
                                                                                                         new_bw_mode)

            self.update_status(f"Translated: Режим Translated: Ч/Б: {mode_text}")
            self.painter._log(f"BW draw mode changed to: {new_bw_mode}")

            if self.painter.mode == 'bw' and self.painter.draw_region and self.painter.IMAGE_PATH:
                self.update_status("Translated: Переподготовка изображения из-за смены опции Translated: Ч/Б...")

                self._set_controls_state("disabled")
                self.update()
                try:

                    success = self.painter.prepare_image_and_palette()
                    if not success:
                        self.update_status("Translated: [ERROR] Translated: Ошибка переподготовки изображения!")
                except Exception as e:
                    self.update_status(f"Translated: [ERROR] Исключение при переподготовке: {e}")
                    traceback.print_exc()
                finally:

                    self.after(50, self._set_controls_state, "normal")

    def on_closing(self):
        "Translated: ""Обработчик закрытия окна по нажатию на крестик."""
        if self.stencil_window and self.stencil_window.winfo_exists():
            self.stencil_window.destroy()
            self.stencil_window = None
        self.stop_script()

    def stop_script(self):
        """Обрабатывает нажатие кнопки 'Translated: Стоп/Translated: Выход (F3)'."""

        msg = "Translated: Остановить скрипт и выйти?"
        if hasattr(self.painter, 'is_waiting_for_hex_click') and self.painter.is_waiting_for_hex_click:
            msg = "Translated: Остановить скрипт, прервав ожидание клика HEX, и выйти?"
        elif self.painter.drawing_enabled or \
                (self.painter.drawing_thread and self.painter.drawing_thread.is_alive()):
            msg = "Translated: Остановить рисование и выйти?"

        if messagebox.askokcancel("Translated: Выход", msg, parent=self):

            self.update_status("Translated: Завершение работы...")
            try:

                self.painter.cleanup_before_exit()
            except Exception as e:
                print(f"Translated: [ERROR] Translated: Ошибка при вызове painter.cleanup_before_exit: {e}")
                traceback.print_exc()
            finally:

                self.destroy()

    def start_new_drawing_gui(self):
        """
        Обрабатывает запрос на новый рисунок из GUI.
        Закрывает трафарет, запрашивает подтверждение, вызывает сброс в painter
        и обновляет интерфейс.
        """
        if self.preview_update_job_id:
            try:
                self.after_cancel(self.preview_update_job_id)
            except ValueError:
                pass
            self.preview_update_job_id = None

        if self.stencil_window and self.stencil_window.winfo_exists():
            self.stencil_window.destroy()
            self.stencil_window = None

            if hasattr(self, 'btn_toggle_stencil'):
                 try:
                     self.btn_toggle_stencil.configure(text="Translated: Включить трафарет")
                 except Exception as e:
                     print(f"WARN: Failed to reset stencil button text: {e}")

        if messagebox.askyesno("Translated: Новый рисунок",
                               "Translated: Начать новый рисунок? Прогресс текущего будет потерян.",
                               parent=self):

            self.painter.reset_for_new_drawing()

            self.update_image_path_label_qt()
            self._update_progress_display()
            self.update_status("Готово к новому рисунку. Translated: Выберите изображение и область.")
            self.schedule_preview_update()

            self.after(10, self._set_controls_state, "normal")

    def reset_settings_gui(self):
        """
        Обработчик кнопки "Translated: Сбросить настройки".
        Вызывает сброс настроек в painter'е и обновляет виджеты GUI.
        """
        if messagebox.askyesno("Translated: Сброс настроек",
                               "Translated: Сбросить все настройки к значениям по умолчанию?",
                               parent=self):

            self.painter.reset_settings_to_default()

            self.update_gui_from_painter_state()

            self.update_status("Translated: Translated: Настройки сброшены к значениям по умолчанию.")

            self.schedule_preview_update()

    def toggle_drawing(self):
        "Translated: ""Обрабатывает нажатие кнопки Старт/Translated: Пауза."""

        self.painter.draw_image()

    def select_image(self):
        """Handles the 'Select Image' button click."""

        if self.painter.drawing_enabled:

            self.update_status("Translated: [WARN] Нельзя выбрать изображение во время рисования.")
            return

        if self.preview_update_job_id:
            try:
                self.after_cancel(self.preview_update_job_id)
            except ValueError:
                pass
            self.preview_update_job_id = None

        initial_dir = os.path.dirname(self.painter.IMAGE_PATH) if self.painter.IMAGE_PATH else os.path.expanduser("~")

        file_path = filedialog.askopenfilename(
            parent=self,
            title="Translated: Выберите изображение", initialdir=initial_dir,
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"), ("All Files", "*.*")]
        )

        if file_path:
            self.painter.IMAGE_PATH = file_path
            self.update_image_path_label_qt()

            self.update_status(f"Translated: Выбрано: {os.path.basename(file_path)}")
            self.painter._log(f"Selected image: {file_path}")

            if self.painter.draw_region:
                self.update_status("Translated: Подготовка изображения...")

                self._set_controls_state("disabled")
                self.update()
                try:

                    success = self.painter.prepare_image_and_palette()
                    if not success:
                        self.update_status("Translated: [ERROR] Translated: Ошибка подготовки изображения!")
                except Exception as e:
                    self.update_status(f"Translated: [ERROR] Исключение при подготовке: {e}")
                    traceback.print_exc()
                finally:

                    self.after(50, self._set_controls_state, "normal")
            else:

                self.schedule_preview_update()

    def show_hex_coord_confirmation(self, coords):
        """
        Безопасно планирует отображение сообщения об установке координат HEX.
        Вызывается из объекта painter как callback.
        """

        if self.winfo_exists():

            self.after(0, self._show_hex_coord_message, coords)

    def _show_hex_coord_message(self, coords):
        """
        Отображает messagebox с подтверждением (вызывается через self.after).
        """

        if self.winfo_exists():

            messagebox.showinfo("Translated: Координаты HEX",
                                f"Translated: Координаты поля HEX установлены: {coords}",
                                parent=self)

            self.update_status(f"Translated: Translated: Координаты HEX установлены: {coords}")

    def create_ctk_slider(self, parent, label_text, from_, to, initial_value, command, is_int=False, format_str=None):
        "Translated: ""Создает слайдер с метками, выровненными через grid."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=1, padx=0)

        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=0)

        label = ctk.CTkLabel(frame, text=label_text, font=self.default_font, width=70, anchor='w')
        label.grid(row=0, column=0, padx=(0, 5), sticky="w")

        value_label = ctk.CTkLabel(frame, text="", font=self.default_font, width=55, anchor='e')
        value_label.grid(row=0, column=2, padx=(5, 0), sticky="e")

        var = tk.DoubleVar(value=float(initial_value))
        if is_int:
            var = tk.IntVar(value=int(initial_value))

        def slider_changed(value):
            actual_value = int(round(float(value))) if is_int else float(value)
            fmt = "{:.0f}" if is_int else (format_str if format_str else "{:.4f}")
            try:
                 value_label.configure(text=fmt.format(actual_value))
            except Exception as e:
                 print(f"Label format error: {e}")
                 value_label.configure(text=str(round(actual_value, 4)))
            command(actual_value)

        track_color = ("gray75", "gray25")
        prog_color = ("#ffffff")
        btn_color = ("#ffffff")
        btn_hover_color = ("#a1a1a1")

        slider = ctk.CTkSlider(frame,
                               from_=from_,
                               to=to,
                               variable=var,
                               command=slider_changed,

                               fg_color=track_color,
                               progress_color=prog_color,
                               button_color=btn_color,
                               button_hover_color=btn_hover_color
                               )

        slider.grid(row=0, column=1, padx=5, sticky="ew")

        slider_changed(initial_value)

        def set_value(new_val):
             try:
                  slider.set(float(new_val))
                  slider_changed(float(new_val))
             except Exception as e: print(f"[GUI ERROR] Slider set error: {e}")
        slider.set_value = set_value

        return slider, value_label

    def _update_progress_display(self):
        "Translated: ""Обновляет прогресс-бар и текстовые метки прогресса."""

        drawn_count, total_count = self.painter.get_progress_info()

        if hasattr(self, 'pixel_progress_label') and self.pixel_progress_label:
            try:

                self.pixel_progress_label.configure(text=f"Translated: Пикселей: {drawn_count} / {total_count}")
            except Exception as e:
                print(f"Error updating pixel label: {e}")

        if total_count > 0:
            percentage = drawn_count / total_count
            percentage_text = int(percentage * 100)
            if hasattr(self, 'progress_bar') and self.progress_bar:
                try:
                    self.progress_bar.set(percentage)
                except Exception as e:
                    print(f"Error setting progress bar: {e}")
            if hasattr(self, 'progress_label') and self.progress_label:
                try:
                    self.progress_label.configure(text=f"Translated: Прогресс: {percentage_text}%")
                except Exception as e:
                    print(f"Error updating progress label: {e}")
        else:

            is_complete = (drawn_count == 1 and total_count == 1)
            progress_value = 1.0 if is_complete else 0.0
            progress_text = 100 if is_complete else 0

            if hasattr(self, 'progress_bar') and self.progress_bar:
                self.progress_bar.set(progress_value)
            if hasattr(self, 'progress_label') and self.progress_label:
                self.progress_label.configure(text=f"Translated: Прогресс: {progress_text}%")

            if hasattr(self, 'pixel_progress_label') and self.pixel_progress_label:
                self.pixel_progress_label.configure(
                    text=f"Translated: Пикселей: {drawn_count} / {total_count}" if is_complete else "Translated: Пикселей: 0 / 0")

    def _update_preview_display(self):
        "Translated: ""Обновляет превью, пересоздавая виджет Label при необходимости."""
        self.preview_update_job_id = None
        if not self.winfo_exists(): return

        pil_image = None
        try:
            pil_image = self.painter.get_preview_image()
        except Exception as e:
            print(f"[ERROR] Exception in painter.get_preview_image(): {e}")
            pil_image = None

        show_image = pil_image is not None

        label_to_configure = self.preview_label

        label_exists = label_to_configure and label_to_configure.winfo_exists()

        label_has_image = self.preview_image_ref is not None

        if not label_exists or (show_image != label_has_image):

            label_to_configure = self._recreate_preview_label()
            if not label_to_configure:
                print("[GUI ERROR] Cannot update preview, failed to get/recreate label.")
                return

        try:
            if show_image:

                img_w, img_h = pil_image.size
                if img_w <= 0 or img_h <= 0: raise ValueError("Invalid image dimensions")

                container_w = PREVIEW_WIDTH;
                container_h = PREVIEW_HEIGHT
                scale = min(container_w / img_w, container_h / img_h, 1.0)
                new_w = max(1, int(img_w * scale));
                new_h = max(1, int(img_h * scale))

                try:
                    resample_filter = Image.Resampling.LANCZOS
                except AttributeError:
                    resample_filter = Image.LANCZOS
                resized_pil_main = pil_image.resize((new_w, new_h), resample_filter)

                ctk_image_scaled = ctk.CTkImage(light_image=resized_pil_main, dark_image=resized_pil_main,
                                                size=(new_w, new_h))

                self.preview_image_ref = ctk_image_scaled
                label_to_configure.configure(image=self.preview_image_ref, text="")

            else:

                self.preview_image_ref = None
                label_to_configure.configure(image=None, text="Translated: Превью\n(Нет данных)",
                                             font=self.default_font)

        except Exception as e:

            print(f"Translated: [GUI ERROR] Translated: Ошибка при конфигурировании preview_label: {e}")
            self.preview_image_ref = None
            try:

                if label_to_configure and label_to_configure.winfo_exists():
                    label_to_configure.configure(image=None, text="Translated: Translated: Ошибка\nПревью", font=self.default_font)
            except Exception:
                pass

        if self.stencil_window and self.stencil_window.winfo_exists():
            try:
                self.stencil_window.update_image(pil_image)
            except Exception as e_stencil:
                print(f"Translated: [GUI ERROR] Translated: Ошибка обновления трафарета: {e_stencil}")

    def _set_controls_state(self, state: str):
        "Translated: ""Включает/выключает элементы управления CTk."""
        tk_state = "normal" if state == 'normal' else "disabled"
        widget_list = getattr(self, 'settings_widgets_to_lock', [])

        for widget in widget_list:
            if widget and isinstance(widget, (ctk.CTkButton, ctk.CTkSlider, ctk.CTkCheckBox, ctk.CTkRadioButton, ctk.CTkLabel)):
                try:
                    widget.configure(state=tk_state)
                except Exception as e:
                    print(f"[GUI WARN] Error setting state for {widget}: {e}")

        self.update_bw_options_state()

        self.update_tolerance_sliders_state(self.painter.has_transparency)

        self.update_kmeans_slider_state()

    def update_status(self, message):
        "Translated: ""Планирует обновление строки статуса."""

        if self.winfo_exists():
             self.after(0, self._update_status_safe, message)

    def _update_status_safe(self, message):
        "Translated: ""Обновляет строку статуса (выполняется в потоке GUI)."""
        display_message = ""
        text_color = "#ffffff"
        should_unlock_controls = False

        popup_prefix = "show_hex_error_popup:"
        if isinstance(message, str) and message.startswith(popup_prefix):

            full_error_message = message[len(popup_prefix):]

            display_message_status = full_error_message.strip().split('\n')[0]

            display_message_popup = full_error_message.strip()
            text_color = "#FF6B6B"

            try:

                messagebox.showerror("Translated: Translated: Ошибка координат HEX", display_message_popup, parent=self)
            except Exception as mb_error:
                 print(f"Translated: [GUI ERROR] Не удалось показать messagebox: {mb_error}")

            status_text = display_message_status
            if len(status_text) > 120: status_text = status_text[:117] + "..."
            if hasattr(self, 'status_label') and self.status_label:
               try:
                   self.status_label.configure(text=status_text, text_color=text_color)
               except Exception as e:
                    print(f"[GUI WARN] Error updating status label: {e}")

            return

        elif isinstance(message, str):

            if message.startswith("[ERROR]"):
                display_message=message[len("[ERROR] "):]
                text_color="#FF6B6B"

                if not self.painter.drawing_enabled: should_unlock_controls = True
            elif message.startswith("[WARN]"):
                display_message=message[len("[WARN] "):]
                text_color="#FFD166"
            elif message.startswith("[INFO]"):
                display_message=message[len("[INFO] "):]
                text_color="white"
            elif message == "reset_progress":
                self._update_progress_display()
                display_message="Translated: Состояние сброшено к начальному."
                should_unlock_controls = True
            elif message == "drawing_complete":
                display_message="Translated: Рисование завершено!"
                text_color="#90EE90"

                if self.winfo_exists():
                     messagebox.showinfo("Translated: Завершено", "Translated: Рисование завершено!", parent=self)
                self._update_progress_display()
                should_unlock_controls = True
            elif message == "drawing_stopped":
                display_message="Translated: Рисование остановлено."
                text_color="orange"
                should_unlock_controls = True
            elif message == "drawing_stopped_due_to_error":
                 display_message="Translated: Рисование остановлено из-за ошибки."
                 text_color = "#FF6B6B"
                 should_unlock_controls = True
            else:

                display_message = message
                text_color = "white"

            status_text = display_message.split('\n')[0]
            if len(status_text) > 120: status_text = status_text[:117] + "..."

            if hasattr(self, 'status_label') and self.status_label:
               try:
                   self.status_label.configure(text=status_text, text_color=text_color)
               except Exception as e:
                    print(f"[GUI WARN] Error updating status label: {e}")

            if should_unlock_controls:

                if not self.painter.drawing_enabled:
                    self.after(50, self._set_controls_state, "normal")
                else:

                    print("[GUI WARN] Status indicates unlock, but painter still drawing_enabled=True?")
        else:

            if hasattr(self, 'status_label') and self.status_label:
                try: self.status_label.configure(text=str(message), text_color="white")
                except Exception as e: print(f"[GUI WARN] Error updating status label: {e}")

    def schedule_progress_update(self):
        if self.winfo_exists():
            self.after(0, self._update_progress_display)

    def schedule_preview_update(self):
        "Translated: ""Планирует обновление превью, отменяя предыдущие задачи."""

        if self.preview_update_job_id:
            try:
                self.after_cancel(self.preview_update_job_id)

            except ValueError:
                pass
            self.preview_update_job_id = None

        if self.winfo_exists():

            self.preview_update_job_id = self.after(0, self._update_preview_display)

    def update_gui_from_painter_state(self):
        "Translated: ""Обновляет виджеты GUI на основе текущего состояния painter."""
        if not hasattr(self, 'painter'): return

        sliders = {
            self.slider_brush_size: self.painter.BRUSH_SIZE,
            self.slider_draw_delay: self.painter.DRAW_DELAY,
            self.slider_k_clusters: self.painter.K_CLUSTERS,
            self.slider_bg_tolerance: self.painter.BG_TOLERANCE,
            self.slider_alpha_threshold: self.painter.ALPHA_THRESHOLD,
        }
        for slider, value in sliders.items():
            if slider and hasattr(slider, 'set_value'):
                try: slider.set_value(value)
                except Exception as e: print(f"Error setting slider {slider}: {e}")

        if hasattr(self, 'mode_var'): self.mode_var.set(self.painter.mode)
        if hasattr(self, 'bw_draw_mode_var'): self.bw_draw_mode_var.set(self.painter.bw_draw_mode)
        if hasattr(self, 'remove_bg_var'): self.remove_bg_var.set(self.painter.REMOVE_BACKGROUND)

        self.update_kmeans_slider_state()
        self.update_tolerance_sliders_state(self.painter.has_transparency)
        self.update_bw_options_state()

        if hasattr(self, 'drawing_mode_var'):

            current_internal_mode = self.painter.drawing_mode

            button_text_to_select = self._drawing_mode_rev_map.get(current_internal_mode)

            if button_text_to_select:

                self.drawing_mode_var.set(button_text_to_select)
            else:

                default_text = self._drawing_mode_rev_map.get(OlegPainter.DEFAULT_DRAWING_MODE, "Translated: Обычный")
                self.drawing_mode_var.set(default_text)

        self.update_image_path_label_qt()

    def update_image_path_label_qt(self):
        "Translated: ""Обновляет метку пути к изображению (CTk)."""
        if hasattr(self, 'image_path_label') and self.image_path_label:
            if self.painter.IMAGE_PATH:

                 base_name = os.path.basename(self.painter.IMAGE_PATH)
                 display_text = f"Translated: Изобр.: {base_name}"
                 if len(display_text) > 50:
                     display_text = display_text[:20] + "..." + display_text[-27:]
                 self.image_path_label.configure(text=display_text)
            else:
                 self.image_path_label.configure(text="Translated: Изображение не выбрано")

    def update_kmeans_slider_state(self):
        "Translated: ""Обновляет состояние слайдера K-Means."""
        new_state = "normal" if self.painter.mode == "color" else "disabled"
        if hasattr(self, 'slider_k_clusters') and self.slider_k_clusters:
            self.slider_k_clusters.configure(state=new_state)
        if hasattr(self, 'k_clusters_val_label') and self.k_clusters_val_label:
            self.k_clusters_val_label.configure(state=new_state)

    def update_tolerance_sliders_state(self, has_transparency):
        "Translated: ""Обновляет состояние слайдеров допусков."""
        remove_bg_enabled = self.remove_bg_var.get()
        alpha_state = "disabled"
        color_state = "disabled"

        if remove_bg_enabled:
            if has_transparency: alpha_state = "normal"
            else: color_state = "normal"

        if hasattr(self, 'slider_alpha_threshold') and self.slider_alpha_threshold:
            self.slider_alpha_threshold.configure(state=alpha_state)
        if hasattr(self, 'alpha_threshold_val_label') and self.alpha_threshold_val_label:
            self.alpha_threshold_val_label.configure(state=alpha_state)

        if hasattr(self, 'slider_bg_tolerance') and self.slider_bg_tolerance:
            self.slider_bg_tolerance.configure(state=color_state)
        if hasattr(self, 'bg_tolerance_val_label') and self.bg_tolerance_val_label:
            self.bg_tolerance_val_label.configure(state=color_state)

    def update_bw_options_state(self):
        "Translated: ""Включает/выключает радиокнопки выбора Translated: Ч/Б."""
        new_state = "normal" if self.painter.mode == 'bw' else "disabled"

        if hasattr(self, 'bw_options_frame'):
             if new_state == "normal":
                 self.bw_options_frame.pack(fill="x", pady=(0, self.pad_y), padx=(self.pad_x + 20))
             else:
                 self.bw_options_frame.pack_forget()

class StencilWindow(ctk.CTkToplevel):
    """
    Класс для полупрозрачного окна-трафарета, повторяющего область рисования.
    Отображает превью и позволяет кликать "Translated: сквозь" себя.
    """
    def __init__(self, master, physical_region, initial_pil_image=None, alpha=150):

        super().__init__(master)
        self.physical_region = physical_region
        self.alpha = alpha
        self.image_label = None
        self.photo_image_ref = None
        self.hwnd = None

        x_phys, y_phys, w_phys, h_phys = self.physical_region
        if w_phys <= 0 or h_phys <= 0:
            print("[ERROR] StencilWindow (tk): Invalid physical_region dimensions.")
            self.after(1, self.destroy)
            return
        approx_w = w_phys
        approx_h = h_phys
        try:
             scale = master.painter.dpi_scale_factor
             if scale > 0:
                 approx_w = int(round(w_phys / scale))
                 approx_h = int(round(h_phys / scale))
        except: pass
        self.geometry(f"{approx_w}x{approx_h}+0+0")

        self.overrideredirect(True)

        self.image_label = tk.Label(self, borderwidth=0)
        self.image_label.pack(fill="both", expand=True)

        self.after(50, self._setup_window)

        if initial_pil_image:
            self.update_image(initial_pil_image)

    def _get_hwnd(self):
        "Translated: ""Находит правильный HWND для окна Toplevel."""
        if self.hwnd:
            return self.hwnd
        try:
            direct_hwnd = self.winfo_id()
            parent_hwnd = _user32.GetParent(direct_hwnd)
            hwnd_to_use = parent_hwnd if parent_hwnd else direct_hwnd
            if not hwnd_to_use:
                print("Translated: [ERROR] _get_hwnd: Не удалось получить HWND.")
                return None
            self.hwnd = hwnd_to_use
            print(f"Translated: [DEBUG] _get_hwnd: Используем HWND: {self.hwnd} (Direct: {direct_hwnd}, Parent: {parent_hwnd})")
            return self.hwnd
        except Exception as e:
            print(f"Translated: [ERROR] _get_hwnd: Translated: Ошибка при получении HWND: {e}")
            return None

    def _setup_window(self):
        "Translated: ""Применяет стили и позиционирует окно с использованием физических координат."""
        if not self.winfo_exists():
            print("Translated: [DEBUG] _setup_window: Окно уже не существует.")
            return

        hwnd = self._get_hwnd()
        if not hwnd:
            print("Translated: [ERROR] _setup_window: Не удалось получить HWND для применения стилей/позиции.")
            return

        x_phys, y_phys, w_phys, h_phys = self.physical_region

        try:
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x80000
            WS_EX_TRANSPARENT = 0x20
            LWA_COLORKEY = 0x1
            LWA_ALPHA = 0x2
            KEY_COLORREF = 0x00FF00FF

            original_ex_style = _GetWindowLongW(hwnd, GWL_EXSTYLE)
            new_ex_style = original_ex_style | WS_EX_LAYERED | WS_EX_TRANSPARENT

            if new_ex_style != original_ex_style:
                _SetWindowLongW(hwnd, GWL_EXSTYLE, new_ex_style)
                time.sleep(0.05)

            current_ex_style = _GetWindowLongW(hwnd, GWL_EXSTYLE)
            is_layered = (current_ex_style & WS_EX_LAYERED) != 0
            is_transparent = (current_ex_style & WS_EX_TRANSPARENT) != 0
            print(f"Translated: [DEBUG] _setup_window: Стили применены - Layered: {is_layered}, Transparent: {is_transparent}")
            if not is_layered or not is_transparent:
                print("Translated: [WARN] _setup_window: Не удалось установить необходимые стили WS_EX.")

                _SetWindowLongW(hwnd, GWL_EXSTYLE, new_ex_style)

        except Exception as e:
            print(f"Translated: [ERROR] _setup_window: Translated: Ошибка при установке стилей WS_EX: {e}")
            traceback.print_exc()
        try:
            dwFlags = LWA_COLORKEY | LWA_ALPHA
            alpha_byte = wintypes.BYTE(self.alpha)
            success_flag = _SetLayeredWindowAttributes(hwnd, KEY_COLORREF, alpha_byte, dwFlags)
            print(f"[DEBUG] _setup_window: SetLayeredWindowAttributes вернула: {success_flag} (0=Translated: Ошибка)")
            if success_flag == 0:
                error_code = ctypes.get_last_error()
                print(f"Translated: [ERROR] _setup_window: SetLayeredWindowAttributes вернула ошибку! Код: {error_code}")
        except Exception as e:
            print(f"Translated: [ERROR] _setup_window: Translated: Ошибка при вызове SetLayeredWindowAttributes: {e}")
            traceback.print_exc()
        try:
            print(
                f"Translated: [DEBUG] _setup_window: Вызов SetWindowPos для HWND {hwnd} с физ. коорд.: X={x_phys}, Y={y_phys}, W={w_phys}, H={h_phys}")
            flags = SWP_SHOWWINDOW | SWP_NOACTIVATE
            success_pos = _SetWindowPos(hwnd, HWND_TOPMOST, x_phys, y_phys, w_phys, h_phys, flags)
            print(f"[DEBUG] _setup_window: SetWindowPos вернула: {success_pos} (0=Translated: Ошибка)")
            if not success_pos:
                error_code = ctypes.get_last_error()
                print(f"Translated: [ERROR] _setup_window: SetWindowPos вернула ошибку! Код: {error_code}")

        except Exception as e:
            print(f"Translated: [ERROR] _setup_window: Исключение при вызове SetWindowPos: {e}")
            traceback.print_exc()

        print(f"Translated: [INFO] _setup_window: Настройка окна для HWND {hwnd} завершена.")

    def _apply_win_styles(self):
        "Translated: ""Применяет WS_EX_LAYERED, WS_EX_TRANSPARENT и SetLayeredWindowAttributes с LWA_COLORKEY | LWA_ALPHA."""
        if not self.winfo_exists():
            print("Translated: [DEBUG] _apply_win_styles (ReAdd TX): Окно уже не существует.")
            return

        try:
            direct_hwnd = self.winfo_id()
            parent_hwnd = _user32.GetParent(direct_hwnd)
            hwnd = parent_hwnd if parent_hwnd else direct_hwnd
            if not hwnd:
                 print("Translated: [ERROR] _apply_win_styles (ReAdd TX): Не удалось получить HWND.")
                 return
            print(f"Translated: [DEBUG] _apply_win_styles (ReAdd TX): Используем HWND: {hwnd} (Direct: {direct_hwnd}, Parent: {parent_hwnd})")

            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x80000
            WS_EX_TRANSPARENT = 0x20
            LWA_COLORKEY = 0x1
            LWA_ALPHA = 0x2
            KEY_COLORREF = 0x00FF00FF

            original_ex_style = _GetWindowLongW(hwnd, GWL_EXSTYLE)

            new_ex_style = original_ex_style | WS_EX_LAYERED | WS_EX_TRANSPARENT
            print(f"Translated: [DEBUG] _apply_win_styles (ReAdd TX): Целевой ExStyle: {new_ex_style:08X} (был {original_ex_style:08X})")

            if new_ex_style != original_ex_style:
                 _SetWindowLongW(hwnd, GWL_EXSTYLE, new_ex_style)
                 time.sleep(0.1)

                 current_ex_style = _GetWindowLongW(hwnd, GWL_EXSTYLE)
                 print(f"Translated: [DEBUG] _apply_win_styles (ReAdd TX): Текущий ExStyle: {current_ex_style:08X}")
                 is_layered_set = (current_ex_style & WS_EX_LAYERED) == WS_EX_LAYERED
                 is_transparent_set = (current_ex_style & WS_EX_TRANSPARENT) == WS_EX_TRANSPARENT
                 print(f"Translated: [DEBUG] _apply_win_styles (ReAdd TX): Флаг WS_EX_LAYERED установлен? -> {is_layered_set}")
                 print(f"Translated: [DEBUG] _apply_win_styles (ReAdd TX): Флаг WS_EX_TRANSPARENT установлен? -> {is_transparent_set}")

                 if not is_layered_set:
                      print("Translated: [ERROR] _apply_win_styles (ReAdd TX): НЕ УДАЛОСЬ установить флаг WS_EX_LAYERED!")
                 if not is_transparent_set:
                      print("Translated: [ERROR] _apply_win_styles (ReAdd TX): НЕ УДАЛОСЬ установить флаг WS_EX_TRANSPARENT!")
            else:
                 print(f"Translated: [DEBUG] _apply_win_styles (ReAdd TX): Стили WS_EX_LAYERED и WS_EX_TRANSPARENT уже установлены.")

            print(f"Translated: [DEBUG] _apply_win_styles (ReAdd TX): Попытка вызвать SetLayeredWindowAttributes с ColorKey={KEY_COLORREF:08X} и Alpha={self.alpha}...")
            dwFlags = LWA_COLORKEY | LWA_ALPHA
            alpha_byte = wintypes.BYTE(self.alpha)

            success_flag = _SetLayeredWindowAttributes(hwnd, KEY_COLORREF, alpha_byte, dwFlags)
            print(f"Translated: [DEBUG] _apply_win_styles (ReAdd TX): SetLayeredWindowAttributes вернула: {success_flag} (0=Translated: Ошибка, не 0=Успех)")

            if success_flag == 0:
                error_code = ctypes.get_last_error()
                print(f"Translated: [ERROR] _apply_win_styles (ReAdd TX): SetLayeredWindowAttributes ВЕРНУЛА ОШИБКУ (0)! Код ошибки Windows: {error_code}")

            print(f"Translated: [INFO] _apply_win_styles (ReAdd TX): Применение стилей к HWND {hwnd} завершено.")

        except NameError as ne:
             print(f"Translated: [ERROR] _apply_win_styles (ReAdd TX): NameError - возможно, ctypes функции не загружены: {ne}")
             traceback.print_exc()
        except Exception as e:
            print(f"Translated: [ERROR] _apply_win_styles (ReAdd TX): Исключение при применении стилей: {e}")
            traceback.print_exc()

    def update_image(self, pil_image_rgba):
        "Translated: ""Обновляет изображение, заменяя прозрачные пиксели на ключ-цвет."""
        if not self.winfo_exists() or self.image_label is None:
            return

        KEY_COLOR_RGB = (255, 0, 255)
        ALPHA_THRESHOLD = 10

        if pil_image_rgba is None or pil_image_rgba.mode != 'RGBA':

            self.image_label.configure(image='')
            self.photo_image_ref = None

            self.image_label.configure(bg='#FF00FF')
            return

        try:
            _x_phys, _y_phys, w_phys, h_phys = self.physical_region
            if w_phys <= 0 or h_phys <= 0:
                 self.image_label.configure(image='')
                 self.photo_image_ref = None
                 self.image_label.configure(bg='#FF00FF')
                 return

            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS
            resized_rgba = pil_image_rgba.resize((w_phys, h_phys), resample_filter)

            img_np_rgba = np.array(resized_rgba)

            img_np_rgb = img_np_rgba[:, :, :3].copy()

            alpha_channel = img_np_rgba[:, :, 3]

            transparent_mask = alpha_channel < ALPHA_THRESHOLD

            img_np_rgb[transparent_mask] = KEY_COLOR_RGB

            processed_pil_rgb = Image.fromarray(img_np_rgb, mode='RGB')

            self.photo_image_ref = ImageTk.PhotoImage(processed_pil_rgb)

            self.image_label.configure(image=self.photo_image_ref)

            self.image_label.configure(bg='#FF00FF')

        except Exception as e:
            print(f"[ERROR] Stencil (tk) update_image with color key failed: {e}")
            traceback.print_exc()

            self.image_label.configure(image='')
            self.photo_image_ref = None
            self.image_label.configure(bg='#FF00FF')

if __name__ == "__main__":

    try:
        from pynput import mouse
    except ImportError:
        print("Translated: [ERROR] Библиотека 'pynput' не найдена.")
        print("Translated: Пожалуйста, установите ее: pip install pynput")
        messagebox.showerror("Translated: Translated: Ошибка зависимости", "Translated: Необходима библиотека 'pynput'. Установите ее командой:\npip install pynput")
        sys.exit(1)

    except ImportError:
         print("Translated: [WARN] Библиотека 'keyboard' не найдена. Глобальные хоткеи F1-F5 работать не будут.")

    painter = OlegPainter()

    try:
        ctk.set_default_color_theme("my_theme.json")
        print("Translated: [INFO] Загружена тема: my_theme.json")
    except Exception as e:
        print(f"Translated: [WARN] Не удалось загрузить тему 'my_theme.json': {e}. Используется стандартная.")
        ctk.set_default_color_theme("blue")

    ctk.set_appearance_mode("dark")

    app = OlegPainterGUI(painter)

    try:
        if 'keyboard' in sys.modules:

             if hasattr(app, 'start_new_drawing_gui') and hasattr(app, 'stop_script'):
                 painter.register_hotkeys(app.start_new_drawing_gui, app.stop_script)
             else:
                 print("Translated: [WARN] Методы для хоткеев F4/F3 не найдены в GUI.")
        else:
              print("Translated: [INFO] Библиотека 'keyboard' не загружена, хоткеи F1-F5 не активны.")
    except Exception as e:
         print(f"Translated: [ERROR] Translated: Ошибка регистрации хоткеев: {e}")

    app.mainloop()
    print("GUI closed. Program terminated.")