# -*- coding: utf-8 -*-
import sys
import os
import json
import platform
import time
import threading
import re
import configparser

# Проверка и импорт keyboard
try:
    import keyboard
except ImportError:
    print("="*60 + "\nОШИБКА: Библиотека 'keyboard' не найдена! Хоткей работать не будет.\nУстановите: pip install keyboard\n" + "="*60)
    keyboard = None

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QSplitter, QLabel, QStyle, QSizePolicy, QSpacerItem, QPushButton,
    QDialog, QDialogButtonBox, QMessageBox, QSizeGrip # Добавлен QSizeGrip
)
from PyQt6.QtGui import (
    QFont, QDrag, QPixmap, QPainter, QColor, QIcon, QFontMetrics, QScreen, QFontDatabase
)
from PyQt6.QtCore import (
    Qt, QMimeData, QUrl, QSize, QSettings, QByteArray, QPoint, QTimer,
    pyqtSignal, QObject, pyqtSlot, QRect
)

# --- Константы и Настройки ---
CONFIG_FILE = 'config.ini'
PLUGIN_ROOT_DIR = 'Plugins'
FAVORITES_FILE = 'favorites.json'
FONT_DIR = 'fonts'

TARGET_FONT_FAMILY = "Inter"
APP_FONT_SIZE = 12 # Значение по умолчанию, будет перезаписано из конфига
LOADED_FONT_REGULAR = None
LOADED_FONT_BOLD = None

APP_NAME = "PØP UP"
ORG_NAME = "CmdrUser"

SETTINGS_GEOMETRY_SIZE = "windowSize"
SETTINGS_SPLITTER_STATE = "splitterState"

CAT_ALL = "All Plugins"
CAT_FAVORITES = "⭐ Favorites"
CAT_GENERATORS = "Generators"
CAT_EFFECTS = "Effects"

plugin_data = {}
favorites_set = set()
main_window_ref = None
config = None
current_hotkey = 'f12'
default_width = 800 # Глобальные переменные для дефолтного размера
default_height = 600

# --- Класс для сигналов ---
class SignalEmitter(QObject):
    toggle_signal = pyqtSignal()
    hotkey_changed_signal = pyqtSignal(str)

signal_emitter = SignalEmitter()

# --- Функции для работы с КОНФИГОМ ---
def load_config():
    """Загружает конфигурацию из файла config.ini."""
    global config, current_hotkey, APP_FONT_SIZE, default_width, default_height
    config = configparser.ConfigParser(interpolation=None)
    defaults = {'Hotkey': 'f12', 'FontSize': '12', 'DefaultWidth': '800', 'DefaultHeight': '600'}
    config['General'] = defaults # Устанавливаем дефолты

    if not os.path.exists(CONFIG_FILE):
        print(f"Файл {CONFIG_FILE} не найден. Создаю с настройками по умолчанию.")
        save_config()
    else:
        try:
            config.read(CONFIG_FILE, encoding='utf-8')
            if 'General' not in config:
                print("Секция [General] отсутствует. Восстановление дефолтов.")
                config['General'] = defaults
                save_config()
            else:
                changed = False # Флаг, что конфиг был изменен
                for key, value in defaults.items():
                    if key not in config['General']:
                        print(f"! Ключ '{key}' отсутствует. Добавлен дефолт: '{value}'.")
                        config['General'][key] = value
                        changed = True
                if changed: save_config()
        except Exception as e:
            print(f"! Ошибка чтения {CONFIG_FILE}: {e}. Сброс на дефолт.")
            config['General'] = defaults # Сброс на дефолт при ошибке

    # Читаем значения
    current_hotkey = config.get('General', 'Hotkey', fallback='f12')
    try: APP_FONT_SIZE = config.getint('General', 'FontSize', fallback=12)
    except ValueError: print(f"! Неверное значение FontSize. Используется 12."); APP_FONT_SIZE = 12
    try: default_width = config.getint('General', 'DefaultWidth', fallback=800)
    except ValueError: print(f"! Неверное значение DefaultWidth. Используется 800."); default_width = 800
    try: default_height = config.getint('General', 'DefaultHeight', fallback=600)
    except ValueError: print(f"! Неверное значение DefaultHeight. Используется 600."); default_height = 600

    print(f"+ Конфиг загружен. Хоткей: {current_hotkey}, Шрифт: {APP_FONT_SIZE}pt, Деф. размер: {default_width}x{default_height}")

def save_config():
    global config;
    if config is None: return
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as cf: config.write(cf); print(f"+ Конфиг сохранен: {CONFIG_FILE}.")
    except Exception as e: print(f"! Ошибка сохранения конфига: {e}")

# --- Функция загрузки ШРИФТОВ ---
def load_application_fonts(font_dir=FONT_DIR):
    global LOADED_FONT_REGULAR, LOADED_FONT_BOLD, TARGET_FONT_FAMILY; loaded_families = {}; loaded_count = 0
    if not os.path.isdir(font_dir): print(f"! Папка шрифтов '{font_dir}' не найдена."); return False
    print(f"+ Загрузка шрифтов: {os.path.abspath(font_dir)}")
    for fn in os.listdir(font_dir):
        if fn.lower().endswith(('.ttf', '.otf')):
            path = os.path.join(font_dir, fn); id = QFontDatabase.addApplicationFont(path)
            if id != -1:
                families = QFontDatabase.applicationFontFamilies(id)
                if families:
                    family = families[0]; print(f"  + {fn} -> '{family}'"); loaded_count += 1; style = "Regular"
                    if re.search(r'[_-]bold', fn, re.I): style = "Bold"
                    elif re.search(r'[_-]medium', fn, re.I): style = "Medium"
                    elif re.search(r'[_-]regular', fn, re.I): style = "Regular"
                    if family not in loaded_families: loaded_families[family] = {}
                    loaded_families[family][style] = family
            else: print(f"  ! Ошибка загрузки: {fn}")
    if not loaded_families: print("! Шрифты не загружены."); return False
    print(f"+ Загр. файлов: {loaded_count}, Семейства: {list(loaded_families.keys())}")
    target = next((f for f in loaded_families if TARGET_FONT_FAMILY.lower() in f.lower()), list(loaded_families.keys())[0] if loaded_families else None)
    if not target: print("! Не найдено подходящих семейств шрифтов."); return False
    if TARGET_FONT_FAMILY.lower() not in target.lower(): print(f"! '{TARGET_FONT_FAMILY}' не найден, исп. '{target}'."); TARGET_FONT_FAMILY = target
    styles = loaded_families.get(target, {}); LOADED_FONT_REGULAR = styles.get("Regular", styles.get("Medium", target)); LOADED_FONT_BOLD = styles.get("Bold", None)
    print(f"+ Исп.: '{target}', Regular: '{LOADED_FONT_REGULAR}'" + (f", Bold: '{LOADED_FONT_BOLD}'" if LOADED_FONT_BOLD else ", Bold: не найден"))
    return True

# --- Функции данных ---
def load_favorites():
    global favorites_set;
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f: d=json.load(f); favorites_set = set(d) if isinstance(d, list) and all(isinstance(i,str) for i in d) else set()
        except Exception as e: print(f"! Ошибка {FAVORITES_FILE}: {e}"); favorites_set = set()
    else: favorites_set = set()
def save_favorites():
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f: json.dump(list(favorites_set), f, indent=4)
    except Exception as e: print(f"! Ошибка сохр. {FAVORITES_FILE}: {e}")
def scan_plugins():
    global plugin_data; plugin_data = {}; count = 0
    if not os.path.isdir(PLUGIN_ROOT_DIR): print(f"! Папка '{PLUGIN_ROOT_DIR}' не найдена."); return
    print(f"+ Сканирование: {os.path.abspath(PLUGIN_ROOT_DIR)}"); root_abs = os.path.abspath(PLUGIN_ROOT_DIR)
    for root, dirs, files in os.walk(root_abs, topdown=True):
        rel = os.path.relpath(root, root_abs);
        if rel == '.': continue
        parts = rel.split(os.sep)
        if len(parts) >= 1 and parts[0] in [CAT_GENERATORS, CAT_EFFECTS]:
            cat = parts[0]; sub_path = tuple(parts[1:])
            for f in files:
                if f.lower().endswith('.fst'):
                    name = os.path.splitext(f)[0]; path = os.path.join(root, f); fav = path in favorites_set
                    plugin_data[path] = {'name': name, 'path': path, 'category': cat, 'subcategory_path': sub_path, 'is_favorite': fav}; count += 1
        else: dirs[:] = []
    print(f"+ Найдено плагинов: {count}")


# --- Виджет списка плагинов ---
class DraggablePluginListWidget(QListWidget):
    def __init__(self, mainWindow, parent=None):
        super().__init__(parent); self.mainWindow = mainWindow; self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection); self.setDropIndicatorShown(False); self.drag_active = False
    def startDrag(self, supportedActions):
        if self.drag_active: return
        self.drag_active = True; print("--- startDrag ---")
        try:
            items=self.selectedItems();
            if not items: print("No selection"); self.drag_active=False; return
            item=items[0]; path=item.data(Qt.ItemDataRole.UserRole); name=item.text().lstrip('★').strip()
            print(f"Drag: {name}, Path: {path}");
            if not path or not os.path.exists(path): print(f"! Bad path: '{path}'."); self.drag_active=False; return
            drag=QDrag(self); mime=QMimeData(); url=QUrl.fromLocalFile(path)
            if not url.isValid() or url.isEmpty(): print(f"! Bad QUrl: {path}"); self.drag_active=False; return
            mime.setUrls([url]); mime.setText(name); drag.setMimeData(mime); print("MIME OK.")
            try: # Pixmap
                font=self.font(); fm=QFontMetrics(font); tw=fm.horizontalAdvance(name); pw=max(100,tw+20); ph=max(25,fm.height()+10); pixmap=QPixmap(QSize(pw,ph));
                if pixmap.isNull(): raise ValueError("Pixmap Null"); pixmap.fill(Qt.GlobalColor.transparent); painter=QPainter(pixmap);
                if not painter.isActive(): raise ValueError("Painter inactive"); painter.setRenderHint(QPainter.RenderHint.Antialiasing); painter.setBrush(QColor(50,50,50,200)); painter.setPen(Qt.PenStyle.NoPen);
                painter.drawRoundedRect(pixmap.rect().adjusted(0,0,-1,-1),5,5); painter.setPen(Qt.GlobalColor.white); painter.setFont(font); tr=pixmap.rect().adjusted(10,5,-10,-5);
                painter.drawText(tr, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, name); painter.end(); drag.setPixmap(pixmap); drag.setHotSpot(QPoint(5,5)); print("Pixmap OK.")
            except Exception as e: print(f"! Pixmap Error: {e}.")
            if self.mainWindow: # Reset/Clear/Minimize
                if hasattr(self.mainWindow,'reset_view_to_all'): self.mainWindow.reset_view_to_all()
                if hasattr(self.mainWindow,'search_input'): print("Clearing search..."); self.mainWindow.search_input.clear()
                print("Minimizing..."); QTimer.singleShot(50, self.mainWindow.safe_show_minimized)
            print(f"Exec drag..."); result = drag.exec(Qt.DropAction.CopyAction); print(f"Drag done: {result}")
        except Exception as e: print(f"! CRITICAL DRAG ERROR: {e}")
        finally: self.drag_active = False; print("--- startDrag end ---")

# --- ОКНО НАСТРОЕК ---
class SettingsDialog(QDialog):
    def __init__(self, current_hotkey, parent=None):
        super().__init__(parent); self.setWindowTitle("Настройки"); self.setModal(True)
        layout = QVBoxLayout(self); layout.addWidget(QLabel("Горячая клавиша для показа/скрытия окна:"))
        self.hotkey_input = QLineEdit(current_hotkey); self.hotkey_input.setPlaceholderText("Например: f12, ctrl+alt+p"); layout.addWidget(self.hotkey_input)
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel); buttonBox.accepted.connect(self.accept); buttonBox.rejected.connect(self.reject)
        ok_button = buttonBox.button(QDialogButtonBox.StandardButton.Ok); cancel_button = buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
        if ok_button: ok_button.setObjectName("settingsOkButton")
        if cancel_button: cancel_button.setObjectName("settingsCancelButton")
        layout.addWidget(buttonBox)
    def getHotkey(self): return self.hotkey_input.text().strip().lower()

# --- ВИДЖЕТ ДЛЯ ФОНА БЕЗРАМОЧНОГО ОКНА ---
class RoundedBackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg_color = QColor("#1e1e1e"); painter.setBrush(bg_color); painter.setPen(Qt.PenStyle.NoPen)
        radius = 20.0 # Радиус скругления
        painter.drawRoundedRect(self.rect(), radius, radius)

# --- Главное окно ---
class MainWindow(QMainWindow):
    toggle_visibility_signal = pyqtSignal()

    def __init__(self):
        super().__init__(); global main_window_ref; main_window_ref = self
        self.setWindowTitle(f"{APP_NAME}"); self._set_app_icon()

        # <<< ВКЛЮЧАЕМ РЕЖИМ БЕЗ РАМКИ >>>
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        print("!!! Режим без рамки !!!")

        self.old_pos = None # Для перетаскивания

        self.setup_ui(); self.populate_categories(); self.connect_signals(); self.load_settings_and_center()
        if not self.category_tree.currentItem():
            item=self.category_tree.topLevelItem(0);
            if item:self.category_tree.setCurrentItem(item)
        self.update_plugin_list(); signal_emitter.toggle_signal.connect(self._handle_toggle_request)
        signal_emitter.hotkey_changed_signal.connect(self._update_hotkey_registration)

    def _set_app_icon(self):
        path='app_icon.png';
        if os.path.exists(path): self.setWindowIcon(QIcon(path)); print(f"+ Иконка: {path}")
        else: print(f"! Иконка не найдена: {path}"); icon=self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon); self.setWindowIcon(icon)

    def setup_ui(self):
        # Используем кастомный виджет для фона и скругления
        central_widget = RoundedBackgroundWidget()
        self.setCentralWidget(central_widget)

        # Главный layout теперь у central_widget
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10); main_layout.setSpacing(5)

        top_bar = QHBoxLayout(); top_bar.setSpacing(5)
        self.search_input = QLineEdit(); self.search_input.setPlaceholderText("Search plugins...")
        fm = QFontMetrics(self.font()); h = int(fm.height() * 1.8); self.search_input.setFixedHeight(max(30, h))
        self.search_input.setClearButtonEnabled(True); top_bar.addWidget(self.search_input, 1)

        self.settings_button = QPushButton() # Без текста
        settings_icon_path = 'settings_icon.png'
        if os.path.exists(settings_icon_path):
            settings_icon = QIcon(settings_icon_path); self.settings_button.setIcon(settings_icon)
            icon_size = int(h * 0.65); self.settings_button.setIconSize(QSize(icon_size, icon_size))
        else: self.settings_button.setText("⚙️"); print(f"! Нет иконки: {settings_icon_path}")
        self.settings_button.setFixedSize(h, h); self.settings_button.setToolTip("Настройки"); self.settings_button.setObjectName("settingsButton")
        top_bar.addWidget(self.settings_button); main_layout.addLayout(top_bar)

        self.splitter = QSplitter(Qt.Orientation.Horizontal); main_layout.addWidget(self.splitter, 1)
        sw = QWidget(); sl = QVBoxLayout(sw); sl.setContentsMargins(0, 0, 0, 0)
        self.category_tree = QTreeWidget(); self.category_tree.setHeaderHidden(True); self.category_tree.setIndentation(15) # Отступ для стрелок
        # Убираем явный стиль для дерева, чтобы QSS применялся
        # self.category_tree.setStyleSheet("QTreeWidget { border-right: 1px solid #333; }")
        sl.addWidget(self.category_tree); self.splitter.addWidget(sw)
        maw = QWidget(); mal = QVBoxLayout(maw); mal.setContentsMargins(0, 0, 0, 0)
        self.plugin_list = DraggablePluginListWidget(self); mal.addWidget(self.plugin_list); self.splitter.addWidget(maw)

        # # --- Нижняя панель с QSizeGrip ---
        # bottom_layout = QHBoxLayout()
        # bottom_layout.setContentsMargins(0,0,0,0)
        # bottom_layout.addStretch(1) # Растягиваем пустое место слева
        # # Добавляем QSizeGrip к central_widget
        # self.size_grip = QSizeGrip(central_widget)
        # # Стиль можно задать в QSS для QSizeGrip, если стандартный не нравится
        # # self.size_grip.setStyleSheet("QSizeGrip { background-color: red; }") # Пример
        # bottom_layout.addWidget(self.size_grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        # main_layout.addLayout(bottom_layout) # Добавляем нижний layout в главный

    # <<< ОБНОВЛЕНА populate_categories - еще раз исправляем рекурсию >>>
    def populate_categories(self):
        self.category_tree.clear()
        bf = QFont(self.font())
        if LOADED_FONT_BOLD: bf.setFamily(LOADED_FONT_BOLD); bf.setWeight(QFont.Weight.Bold)
        else: bf.setWeight(QFont.Weight.Bold)

        all_item=QTreeWidgetItem(self.category_tree, [CAT_ALL]); all_item.setData(0,Qt.ItemDataRole.UserRole,{"type":"all","path":tuple()}); all_item.setFont(0,bf);
        fav_item=QTreeWidgetItem(self.category_tree, [CAT_FAVORITES]); fav_item.setData(0,Qt.ItemDataRole.UserRole,{"type":"favorites","path":tuple()}); fav_item.setFont(0,bf);

        folder_paths = {}
        for p_data in plugin_data.values():
            cat = p_data['category']; sub_path = p_data['subcategory_path']
            current = (cat,);
            if current not in folder_paths: folder_paths[current] = set()
            for i, part in enumerate(sub_path):
                parent = current; current = (cat,) + sub_path[:i+1]
                if current not in folder_paths: folder_paths[current] = set()
                if parent in folder_paths: folder_paths[parent].add(part)

        sorted_paths = sorted(list(folder_paths.keys()), key=lambda x: (len(x), x))
        created_items = {} # {path_tuple: QTreeWidgetItem}

        # --- ИСПРАВЛЕННАЯ РЕКУРСИВНАЯ ФУНКЦИЯ ---
        def add_tree_items(path_tuple):
            if path_tuple in created_items: return created_items[path_tuple]

            name = path_tuple[-1] # Имя текущего элемента

            # Определяем родителя и другие атрибуты
            if len(path_tuple) == 1: # Корневая категория
                parent_widget = self.category_tree
                item_type = "category"
                font = bf
            else: # Подкатегория
                parent_path = path_tuple[:-1]
                # <<< ПРОВЕРКА СУЩЕСТВОВАНИЯ РОДИТЕЛЯ ПЕРЕД ИСПОЛЬЗОВАНИЕМ >>>
                if parent_path not in created_items:
                    print(f"!!! ОШИБКА populate_categories: Родитель {parent_path} не найден для {path_tuple}!")
                    # Пытаемся создать родителя рекурсивно, если его нет (на всякий случай)
                    parent_widget = add_tree_items(parent_path)
                    if not parent_widget: # Если и родителя создать не удалось
                         return None # Прерываем создание этого элемента
                else:
                     parent_widget = created_items[parent_path] # Берем из кеша, если есть

                # Теперь можно безопасно определять тип и шрифт
                item_type = "subcategory"
                font = self.font()

            # Создаем элемент, только если родитель существует
            if parent_widget:
                 item = QTreeWidgetItem(parent_widget, [name])
                 item.setData(0, Qt.ItemDataRole.UserRole, {"type": item_type, "path": path_tuple})
                 item.setFont(0, font)
                 created_items[path_tuple] = item # Добавляем в кэш

                 # Раскрываем корневые категории
                 if item_type == "category":
                     item.setExpanded(True)

                 # Рекурсивно добавляем дочерние папки
                 children_names = folder_paths.get(path_tuple, set())
                 for child_name in sorted(list(children_names)):
                     add_tree_items(path_tuple + (child_name,)) # Рекурсивный вызов

                 return item
            else:
                 # Если родителя так и не нашли/создали, возвращаем None
                 return None
        # --- КОНЕЦ РЕКУРСИВНОЙ ФУНКЦИИ ---

        # Запускаем построение дерева для всех путей
        for path_t in sorted_paths:
            add_tree_items(path_t) # Вызов рекурсивной функции

    def connect_signals(self):
        self.category_tree.currentItemChanged.connect(self.update_plugin_list)
        self.search_input.textChanged.connect(self.update_plugin_list)
        self.plugin_list.itemDoubleClicked.connect(self.toggle_favorite)
        # self.category_tree.itemClicked.connect(self._return_focus_to_search) # Заменяем эту строку
        self.plugin_list.itemClicked.connect(self._return_focus_to_search)
        self.settings_button.clicked.connect(self._open_settings_window)

        # <<< НОВЫЕ ПОДКЛЮЧЕНИЯ ДЛЯ ДЕРЕВА >>>
        # Используем itemPressed для немедленной реакции
        self.category_tree.itemPressed.connect(self._handle_tree_item_pressed)

    @pyqtSlot()
    def _open_settings_window(self):
        global current_hotkey, config; dialog = SettingsDialog(current_hotkey, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new = dialog.getHotkey();
            if new and new != current_hotkey:
                print(f"Новый хоткей: {new}"); old = current_hotkey;
                if config: config['General']['Hotkey'] = new; save_config(); current_hotkey = new; signal_emitter.hotkey_changed_signal.emit(old)
                else: QMessageBox.warning(self, "Ошибка", "Конфиг не обновлен.")
            elif not new: QMessageBox.warning(self, "Ошибка", "Хоткей не может быть пустым.")

    @pyqtSlot(str)
    def _update_hotkey_registration(self, old_hotkey):
        print(f"Перерегистрация: {old_hotkey} -> {current_hotkey}"); stop_hotkey_listener(); time.sleep(0.1); start_hotkey_listener()

    @pyqtSlot()
    def _return_focus_to_search(self):
        if hasattr(self, 'search_input'): QTimer.singleShot(0, self.search_input.setFocus)

    @pyqtSlot(QTreeWidgetItem, int)  # Сигнал itemPressed передает элемент и колонку
    def _handle_tree_item_pressed(self, item, column):
        """Обрабатывает нажатие на элемент дерева: раскрывает/схлопывает и возвращает фокус."""
        if item:  # Проверяем, что элемент существует
            # Переключаем состояние expanded (раскрыт/схлопнут)
            item.setExpanded(not item.isExpanded())

            # Возвращаем фокус в поиск (как и при itemClicked)
            self._return_focus_to_search()

    def update_plugin_list(self):
        item = self.category_tree.currentItem(); data = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        term = self.search_input.text().lower().strip(); self.plugin_list.clear();
        if not data: return
        filtered = []; cat_type = data.get("type"); sel_path = tuple(data.get("path", []))
        for path, p_data in plugin_data.items():
            if term and term not in p_data['name'].lower(): continue
            match = False; p_path = (p_data['category'],) + p_data['subcategory_path']
            if cat_type == "all": match = True
            elif cat_type == "favorites": match = p_data['is_favorite']
            elif cat_type == "category" or cat_type == "subcategory":
                if len(p_path) >= len(sel_path) and p_path[:len(sel_path)] == sel_path: match = True
            if match: filtered.append(p_data)
        filtered.sort(key=lambda p: p['name'].lower())
        for p in filtered:
            d_name = f"★ {p['name']}" if p['is_favorite'] else f"   {p['name']}"
            l_item = QListWidgetItem(d_name); l_item.setData(Qt.ItemDataRole.UserRole, p['path']); l_item.setToolTip(f"{'/'.join(p_path)}\n{p['path']}")
            self.plugin_list.addItem(l_item)

    def reset_view_to_all(self):
        tree = self.category_tree
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i);
            if item and item.text(0) == CAT_ALL:tree.setCurrentItem(item); print("Сброс на 'All Plugins'"); break

    def toggle_favorite(self):
        items = self.plugin_list.selectedItems();
        if not items: return
        item = items[0]; path = item.data(Qt.ItemDataRole.UserRole)
        if path and path in plugin_data:
            p = plugin_data[path]; status = not p['is_favorite']; p['is_favorite'] = status
            if status: favorites_set.add(path)
            else: favorites_set.discard(path)
            print(f"{'Добавлено' if status else 'Удалено'} из избранного: {p['name']}")
            save_favorites(); d_name = f"★ {p['name']}" if status else f"   {p['name']}"; item.setText(d_name)
            cur_item = self.category_tree.currentItem()
            if cur_item and cur_item.data(0, Qt.ItemDataRole.UserRole).get("type") == "favorites": self.update_plugin_list()
        else: print("Ошибка toggle_favorite.")

    def save_settings(self):
        settings = QSettings(ORG_NAME, APP_NAME)
        # <<< УБИРАЕМ СОХРАНЕНИЕ РАЗМЕРА ОКНА >>>
        # settings.setValue(SETTINGS_GEOMETRY_SIZE, self.size())
        settings.setValue(SETTINGS_SPLITTER_STATE, self.splitter.saveState())
        print("Настройки сохранены (только сплиттер).")

    def load_settings_and_center(self):
        # <<< Используем ГЛОБАЛЬНЫЕ переменные для дефолтного размера, ЗАГРУЖЕННЫЕ ИЗ КОНФИГА >>>
        global default_width, default_height
        settings = QSettings(ORG_NAME, APP_NAME)

        # <<< ВСЕГДА УСТАНАВЛИВАЕМ РАЗМЕР ИЗ КОНФИГА (через глобальные переменные) >>>
        self.resize(default_width, default_height)
        print(f"Размер окна установлен из конфига/умолчания: {default_width}x{default_height}")

        # Центрируем окно
        self.center_on_screen()

        # Загружаем состояние сплиттера (остается без изменений)
        state = settings.value(SETTINGS_SPLITTER_STATE)
        if isinstance(state, QByteArray):
            if not self.splitter.restoreState(state): print("! Не восст. сплиттер."); self.splitter.setSizes([200, 600])
            else: print("+ Сплиттер загружен.")
        else: self.splitter.setSizes([200, 600]); print("+ Сплиттер по умолч.")
    def center_on_screen(self):
        try:
            screen = self.screen();
            if not screen: screen = QApplication.primaryScreen()
            if screen: center = screen.availableGeometry().center(); fg = self.frameGeometry(); fg.moveCenter(center); self.move(fg.topLeft()); print("Окно отцентрировано.")
            else: print("! Нет экрана для центрирования.")
        except Exception as e: print(f"! Ошибка центрирования: {e}")

    def closeEvent(self, event): print("Закрытие..."); self.save_settings(); stop_hotkey_listener(); super().closeEvent(event)

    # <<< ДОБАВЛЕНЫ МЕТОДЫ ДЛЯ ПЕРЕТАСКИВАНИЯ БЕЗРАМОЧНОГО ОКНА >>>
    def mousePressEvent(self, event):
        if self.windowFlags() & Qt.WindowType.FramelessWindowHint and event.button() == Qt.MouseButton.LeftButton:
             # Проверяем, не кликнули ли на QSizeGrip
             if hasattr(self, 'size_grip') and self.size_grip.geometry().contains(event.pos()):
                 self.old_pos = None # Не начинаем перетаскивание окна, если клик на грипе
                 print("Mouse Press on SizeGrip")
             else:
                 self.old_pos = event.globalPosition().toPoint()
                 print(f"Mouse Press - Old Pos: {self.old_pos}")
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.windowFlags() & Qt.WindowType.FramelessWindowHint and event.buttons() == Qt.MouseButton.LeftButton and self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.old_pos is not None: # Сбрасываем, только если перетаскивали
                print("Mouse Release - Reset Drag Pos")
                self.old_pos = None
        super().mouseReleaseEvent(event)
    # <<< КОНЕЦ МЕТОДОВ ПЕРЕТАСКИВАНИЯ >>>


    @pyqtSlot()
    def _handle_toggle_request(self):
        print("Обработка toggle...");
        if self.isVisible() and not self.isMinimized(): self.safe_show_minimized()
        else: self.safe_show_normal()

    def safe_show_normal(self):
        print("safe_show_normal...");
        if self.isHidden(): self.show()
        self.setWindowState( (self.windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive ); self.raise_(); self.activateWindow()
        print("Окно активно."); self._return_focus_to_search()

    def safe_show_minimized(self): print("safe_show_minimized..."); self.showMinimized(); print("Окно свернуто.")

# --- Хоткей ---
hotkey_listener_thread = None; stop_event = threading.Event()
def hotkey_callback(): print(f"Хоткей '{current_hotkey}' нажат."); signal_emitter.toggle_signal.emit()
def listen_for_hotkey():
    global current_hotkey;
    if not keyboard: return
    try: keyboard.add_hotkey(current_hotkey, hotkey_callback, trigger_on_release=False); print(f"[{threading.current_thread().name}] Хоткей '{current_hotkey}' ОК."); stop_event.wait(); print(f"[{threading.current_thread().name}] Стоп.")
    except ValueError as ve: print(f"[{threading.current_thread().name}] Ошибка рег. хоткея '{current_hotkey}': {ve}")
    except Exception as e: print(f"[{threading.current_thread().name}] Ошибка потока хоткея: {e}.")
    finally:
        print(f"[{threading.current_thread().name}] Удаление хоткея '{current_hotkey}'...");
        try:
            if keyboard: keyboard.remove_hotkey(current_hotkey)
        except Exception: pass; print(f"[{threading.current_thread().name}] Поток хоткея завершен.")
def start_hotkey_listener():
    global hotkey_listener_thread;
    if keyboard and hotkey_listener_thread is None: stop_event.clear(); hotkey_listener_thread = threading.Thread(target=listen_for_hotkey, name="HotkeyListener", daemon=True); hotkey_listener_thread.start(); print("Поток хоткея запущен.")
def stop_hotkey_listener():
    global hotkey_listener_thread, current_hotkey;
    if hotkey_listener_thread and hotkey_listener_thread.is_alive(): print(f"Стоп хоткея '{current_hotkey}'..."); stop_event.set(); hotkey_listener_thread = None; print("Сигнал стоп.")
    elif keyboard:
        try: keyboard.remove_hotkey(current_hotkey)
        except Exception: pass

# --- Стили ---
# --- Стили ---
def load_stylesheet():
    font_family = LOADED_FONT_REGULAR if LOADED_FONT_REGULAR else TARGET_FONT_FAMILY
    radius = max(8, int(APP_FONT_SIZE * 1.2))
    clear_btn = "QLineEdit::clear-button { background-color:#555; border-radius:7px; border:1px solid #666; margin-right:4px; } QLineEdit::clear-button:hover { background-color:#666; } QLineEdit::clear-button:pressed { background-color:#444; }"
    dialog_btns = "QDialogButtonBox QPushButton#settingsOkButton { background-color:#007acc; color:white; border-radius:4px; padding:5px 15px; min-width:60px; } QDialogButtonBox QPushButton#settingsOkButton:hover { background-color:#005a9e; } QDialogButtonBox QPushButton#settingsCancelButton { background-color:#555; color:white; border-radius:4px; padding:5px 15px; min-width:60px; } QDialogButtonBox QPushButton#settingsCancelButton:hover { background-color:#666; }"
    settings_btn = f"QPushButton#settingsButton {{ background-color:transparent; border:none; border-radius: 10px; padding: 2px; /* Небольшой паддинг для иконки */ }} QPushButton#settingsButton:hover {{ background-color:#555; }} QPushButton#settingsButton:pressed {{ background-color:#444; }}"
    tree_style = f"QTreeWidget {{ background-color:#2a2d2e; border:none; margin: 0px 10px 0px 0px; padding:5px 5px; outline:0; border-right:1px solid #333; border-radius: 20px}} QTreeWidget::item {{ padding: 8px 10px 8px 10px; /* Уменьшил левый паддинг */ border-radius:20px; margin:0px; font-style:normal !important; border-left: 3px solid transparent; }} QTreeWidget::item:selected {{ background-color:#3a3d41; color:#ffffff; border-left:none; border-radius: 10px}} QTreeWidget::item:!selected:hover {{ background-color:#333; border-radius: 10px}} QTreeView::branch {{ background-color:transparent;}} /* Стандартные стрелки должны рисоваться теперь */ "

    return f""" QWidget {{ color:#d4d4d4; border:none; font-family:"{font_family}"; font-size:{APP_FONT_SIZE}pt; }} QMainWindow {{ background-color:transparent; border:none; }} QSplitter::handle {{ background-color: transparent; border: none; border-radius: 20px; width:5px; margin:0px 0; }} QSplitter::handle:hover {{ background-color:#555; }} QLineEdit {{ background-color:#3c3c3c; border:1px solid #555; padding:5px 10px; color:#d4d4d4; border-radius:{radius}px; font-style:normal !important; }} QLineEdit:focus {{ border:1px solid #007acc; }} {clear_btn} {tree_style} {settings_btn} {dialog_btns} QListWidget {{ background-color:#1e1e1e; border:none; padding:0px; outline:0; }} QListWidget::item {{ padding:8px 12px; border-bottom:1px solid #333; border-radius:10px; margin:1px 3px; font-style:normal !important; }} QListWidget::item:last-child {{ border-bottom:none; }} QListWidget::item:selected {{ background-color:#6f6f6f; color:#ffffff; border-bottom-color:#094771; border-radius }} QListWidget::item:!selected:hover {{ background-color:#3a3d41; }} QScrollBar:vertical {{ border:none; background: transparent; width:10px; margin:0px; }} QScrollBar::handle:vertical {{ background:#555; min-height:30px; border-radius:5px; }} QScrollBar::handle:vertical:hover {{ background:#666; }} QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ border:none; background:none; height:0px; }} QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{ background:none; }} QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background:none; }} QScrollBar:horizontal {{ border:none; background:#252526; height:10px; margin:0px; }} QScrollBar::handle:horizontal {{ background:#555; min-width:30px; border-radius:5px; }} QScrollBar::handle:horizontal:hover {{ background:#666; }} QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ border:none; background:none; width:0px; }} QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {{ background:none; }} QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background:none; }} """


# --- Запуск ---
if __name__ == "__main__":
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'): QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'): QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv); app.setOrganizationName(ORG_NAME); app.setApplicationName(APP_NAME)
    load_config(); fonts_loaded = load_application_fonts()
    font_family = LOADED_FONT_REGULAR if fonts_loaded and LOADED_FONT_REGULAR else TARGET_FONT_FAMILY
    app_font = QFont(font_family, APP_FONT_SIZE); app_font.setStyle(QFont.Style.StyleNormal); app_font.setItalic(False); app.setFont(app_font)
    actual_font = app.font(); print(f"Шрифт: {actual_font.family()}, {actual_font.pointSize()}pt, Курсив: {actual_font.italic()}");
    if actual_font.italic(): print("!!! КУРСИВ !!!");
    if not actual_font.family().lower().startswith(TARGET_FONT_FAMILY.lower()): print(f"!!! {TARGET_FONT_FAMILY} НЕ ПРИМЕНЕН !!!")
    app.setStyleSheet(load_stylesheet()); load_favorites(); scan_plugins(); window = MainWindow(); window.show(); start_hotkey_listener();
    exit_code = app.exec(); print(f"Выход: {exit_code}"); stop_hotkey_listener(); sys.exit(exit_code)