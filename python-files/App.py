# -*- coding: utf-8 -*-
import sys
import math
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QToolBar, QStatusBar, QGraphicsView, QGraphicsScene,
    QGraphicsItem, QColorDialog, QInputDialog, QMessageBox, QMenu,
    QSizePolicy
)
from PyQt6.QtGui import (QPainter, QPen, QBrush, QColor, QPolygonF,
                         QPainterPath, QAction, QIcon, QTransform,
                         QActionGroup, QPainterPathStroker)

from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from shapely.geometry import Polygon, MultiPolygon, LineString, Point as ShapelyPoint
# Проверка установки библиотеки shapely, вывод сообщения при отсутствии
try:
    from shapely.ops import unary_union
except ImportError:
    messagebox.showerror("Ошибка импорта", "Библиотека 'shapely' не найдена.\nПожалуйста, установите её: pip install shapely")
    import sys
    sys.exit(1) # Выход, если shapely отсутствует
import pickle
import traceback # Для подробного вывода ошибок

# --- Вспомогательные функции и константы ---
DEFAULT_COLOR = Qt.GlobalColor.blue
SELECTED_COLOR = Qt.GlobalColor.red
HOVER_COLOR = Qt.GlobalColor.yellow # Цвет для подсветки при наведении (для ТМО)
DEFAULT_PEN_WIDTH = 2
PI = math.pi

def to_shapely_polygon(shape):
    """
    Преобразует объект Shape в шаплийский полигон.
    Возвращает объект shapely.geometry.Polygon или MultiPolygon,
    или None, если преобразование невозможно.
    """
    points = shape.get_points()
    if not points or len(points) < 3:
        return None

    coords = [(p.x(), p.y()) for p in points]
    
    # Замыкаем полигон, если он не замкнут
    if coords[0] != coords[-1]:
        coords.append(coords[0])

    try:
        poly = ShapelyPolygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)  # Исправляет невалидные полигоны
        return poly
    except Exception as e:
        print(f"[ERROR] Не удалось создать полигон из фигуры: {e}")
        return None

def degrees_to_radians(deg):
    """Конвертирует градусы в радианы."""
    return deg * PI / 180.0

def create_homogeneous_point(point: QPointF) -> np.ndarray:
    """Преобразует QPointF в однородные координаты [x, y, 1]."""
    return np.array([point.x(), point.y(), 1.0])

def point_from_homogeneous(h_point: np.ndarray) -> QPointF:
    """Преобразует однородные координаты обратно в QPointF."""
    if abs(h_point[2]) < 1e-9: # Избегаем деления на ноль
        # Обработка точки на бесконечности (здесь просто вернем что-то)
        # В реальной графике это требует более сложной логики
        return QPointF(h_point[0], h_point[1])
    return QPointF(h_point[0] / h_point[2], h_point[1] / h_point[2])

# --- Базовый класс для всех фигур ---
class Shape(QGraphicsItem):
    """Базовый класс для всех графических примитивов и сложных фигур."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._points = [] # Основные точки, определяющие фигуру
        self._color = QColor(DEFAULT_COLOR)



        self._pen = QPen(Qt.PenStyle.NoPen)  # ❌ без обводки 
        self._brush = QBrush(self._color)  # ✅ Заливка тем же цветом


        
        self._is_selected = False
        self._is_hovered_for_tmo = False # Флаг для выбора второго операнда ТМО

        # Включаем обработку наведения мыши
        self.setAcceptHoverEvents(True)
        # Делаем элемент выбираемым и перемещаемым стандартными средствами QGraphicsView
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True) # Базовое перемещение

    def get_points(self) -> list[QPointF]:
        """Возвращает копию списка точек фигуры."""
        return list(self._points) # Возвращаем копию, чтобы не изменить оригинал случайно

    def set_points(self, points: list[QPointF]):
        """Устанавливает точки фигуры и обновляет ее."""
        self.prepareGeometryChange() # Важно вызвать перед изменением геометрии
        self._points = points
        self.update() # Перерисовать элемент

    def get_color(self) -> QColor:
        """Возвращает цвет фигуры."""
        return self._color

    def set_color(self, color: QColor):
        """Устанавливает цвет фигуры."""
        if self._color != color:
            self._color = color
            self._pen.setColor(self._color)
            # Можно добавить и изменение цвета заливки, если нужно
            # self._brush.setColor(self._color)
            self.update()

    def get_center(self) -> QPointF:
        """Вычисляет геометрический центр фигуры (по bounding box)."""
        return self.boundingRect().center()

    def apply_transformation(self, matrix: np.ndarray):
        """
        Применяет матрицу преобразования (3x3) ко всем точкам фигуры.
        Использует однородные координаты.
        """
        new_points = []
        for point in self._points:
            h_point = create_homogeneous_point(point)
            transformed_h_point = matrix @ h_point # Матричное умножение
            new_points.append(point_from_homogeneous(transformed_h_point))

        self.prepareGeometryChange()
        self._points = new_points
        # Сброс стандартного QGraphicsItem трансформа, т.к. мы меняем точки напрямую
        self.setTransform(QTransform())
        self.update()
        # Сообщаем сцене об изменении для обновления bounding rect
        if self.scene():
            self.scene().update()


    # --- Переопределение методов QGraphicsItem ---

    def boundingRect(self) -> QRectF:
        """Возвращает ограничивающий прямоугольник (необходимо для QGraphicsItem)."""
        if not self._points:
            return QRectF()
        # Просто создаем прямоугольник, включающий все точки
        # Для кривых Безье нужно вычислять точнее
        poly = QPolygonF(self._points)
        return poly.boundingRect()


    def shape(self) -> QPainterPath:
        """Точная форма фигуры для взаимодействия с мышью — по заливке."""
        path = QPainterPath()
        if len(self._points) > 2:
            path.addPolygon(QPolygonF(self._points))  # ✅ Залитый полигон
        elif len(self._points) == 1:
            path.addEllipse(self._points[0], 5, 5)
        return path




    def paint(self, painter: QPainter, option, widget=None):
        """Рисует фигуру (необходимо для QGraphicsItem)."""
        current_pen = QPen(self._pen)
        if self.isSelected():
            current_pen.setColor(QColor(SELECTED_COLOR))
            current_pen.setStyle(Qt.PenStyle.DashLine)
        elif self._is_hovered_for_tmo:
             current_pen.setColor(QColor(HOVER_COLOR))
             current_pen.setWidth(DEFAULT_PEN_WIDTH + 1)

        painter.setPen(current_pen)
        painter.setBrush(self._brush) # Используем заданную кисть (может быть NoBrush)

        # Базовая отрисовка - полилиния. Переопределить в наследниках при необходимости.
        if len(self._points) > 1:
            painter.drawPolyline(QPolygonF(self._points))
            # Если это замкнутая фигура (например, многоугольник), можно замкнуть
            # Условие можно усложнить (например, проверять, является ли класс полигоном)
            if isinstance(self, (NStar, RegularCross, PolygonShape)):
                 if self._points[0] != self._points[-1]: # Если еще не замкнут
                     painter.drawLine(self._points[-1], self._points[0])

    def set_hovered_for_tmo(self, hover: bool):
        """Устанавливает флаг подсветки для ТМО."""
        if self._is_hovered_for_tmo != hover:
            self._is_hovered_for_tmo = hover
            self.update()

    # --- Обработка событий мыши ---
    def hoverEnterEvent(self, event):
        """Мышь вошла в область элемента."""
        # Здесь можно добавить визуальный эффект наведения, если нужно
        # print(f"Hover Enter: {self.__class__.__name__}")
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Мышь покинула область элемента."""
        # print(f"Hover Leave: {self.__class__.__name__}")
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        """Перехват изменений состояния элемента."""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            self._is_selected = bool(value)
            # print(f"{self.__class__.__name__} selected: {self._is_selected}")
            # Можно добавить доп. логику при выделении/снятии выделения
            self.update() # Обновить внешний вид
        return super().itemChange(change, value)

# --- Классы конкретных фигур ---

class LineSegment(Shape):
    """Отрезок прямой (обязательный элемент)."""
    def __init__(self, p1: QPointF, p2: QPointF, parent=None):
        super().__init__(parent)
        self._points = [p1, p2]

    # boundingRect и paint наследуются от Shape, их достаточно

class BezierCurve(Shape):
    """
    Кривая Безье (BZ).
    Для простоты примера - кубическая кривая Безье (4 точки).
    """
    def __init__(self, p1: QPointF, p2: QPointF, p3: QPointF, p4: QPointF, parent=None):
        super().__init__(parent)
        # p1, p4 - конечные точки; p2, p3 - контрольные точки
        self._points = [p1, p2, p3, p4]
        self._num_segments = 30 # Количество отрезков для аппроксимации кривой

    def get_curve_points(self) -> list[QPointF]:
        """Генерирует точки на кривой для отрисовки."""
        if len(self._points) != 4: return []
        p1, p2, p3, p4 = self._points
        curve_points = []
        for i in range(self._num_segments + 1):
            t = i / self._num_segments
            x = (1-t)**3 * p1.x() + 3*(1-t)**2 * t * p2.x() + 3*(1-t) * t**2 * p3.x() + t**3 * p4.x()
            y = (1-t)**3 * p1.y() + 3*(1-t)**2 * t * p2.y() + 3*(1-t) * t**2 * p3.y() + t**3 * p4.y()
            curve_points.append(QPointF(x, y))
        return curve_points

    def boundingRect(self) -> QRectF:
        """Ограничивающий прямоугольник для кривой Безье."""
        # Точный расчет сложен, используем аппроксимацию
        if not self._points: return QRectF()
        poly = QPolygonF(self.get_curve_points())
        # Добавим контрольные точки, чтобы они тоже входили
        poly.append(self._points[1])
        poly.append(self._points[2])
        return poly.boundingRect().adjusted(-5, -5, 5, 5) # Небольшой запас



    def paint(self, painter: QPainter, option, widget=None):
        pen = QPen(QColor("black"))
        pen.setWidth(2)

        if self.isSelected():
            pen.setColor(QColor(SELECTED_COLOR))
            pen.setStyle(Qt.PenStyle.DashLine)
        elif self._is_hovered_for_tmo:
            pen.setColor(QColor(HOVER_COLOR))
            pen.setWidth(DEFAULT_PEN_WIDTH + 1)

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)  # Без заливки

        if len(self._points) == 4:
            path = QPainterPath(self._points[0])
            path.cubicTo(self._points[1], self._points[2], self._points[3])
            painter.drawPath(path)





    def shape(self) -> QPainterPath:
        """Точная форма кривой Безье."""
        path = QPainterPath()
        if len(self._points) == 4:
            path.moveTo(self._points[0])
            path.cubicTo(self._points[1], self._points[2], self._points[3])

        # Увеличиваем область для клика
        stroker = QPainterPathStroker()
        stroker.setWidth(DEFAULT_PEN_WIDTH + 6)
        stroked_path = stroker.createStroke(path)
        stroked_path.addPath(path) # Добавляем и саму кривую
        return stroked_path

class NStar(Shape):
    """Правильная n-конечная звезда (Zv)."""
    def __init__(self, center: QPointF, radius_point: QPointF, n: int, parent=None):
        super().__init__(parent)
        self.center = center
        self.radius_point = radius_point
        self.n = max(3, min(n, 20)) # Ограничение n от 3 до 20
        self._recalculate_points()

    def _recalculate_points(self):
        """Пересчитывает вершины звезды."""
        self.prepareGeometryChange()
        self._points = []
        xc, yc = self.center.x(), self.center.y()
        dx = self.radius_point.x() - xc
        dy = self.radius_point.y() - yc
        radius = math.sqrt(dx*dx + dy*dy)
        # Начальный угол определяется точкой radius_point
        start_angle = math.atan2(dy, dx) # В радианах

        if radius < 1 or self.n < 3: # Защита от некорректных данных
             self._points = [self.center] # Отобразим хотя бы центр
             return

        # Радиус внутреннего круга для звезды (можно настроить)
        inner_radius = radius * 0.5

        angle_step = 2 * PI / self.n

        for i in range(self.n):
            # Внешняя вершина
            outer_angle = start_angle + i * angle_step
            outer_x = xc + radius * math.cos(outer_angle)
            outer_y = yc + radius * math.sin(outer_angle)
            self._points.append(QPointF(outer_x, outer_y))

            # Внутренняя вершина
            inner_angle = start_angle + (i + 0.5) * angle_step
            inner_x = xc + inner_radius * math.cos(inner_angle)
            inner_y = yc + inner_radius * math.sin(inner_angle)
            self._points.append(QPointF(inner_x, inner_y))
        self.update()



    def paint(self, painter: QPainter, option, widget=None):
        brush_color = self._color

        # Меняем цвет заливки при выделении/подсветке
        if self.isSelected():
            brush_color = QColor(SELECTED_COLOR)
        elif self._is_hovered_for_tmo:
            brush_color = QColor(HOVER_COLOR)

        painter.setPen(Qt.PenStyle.NoPen)  # ❌ убираем контур
        painter.setBrush(QBrush(brush_color))  # ✅ заливаем нужным цветом

        if len(self._points) > 2:
            painter.drawPolygon(QPolygonF(self._points))  # ✅ рисуем полигон
        


class RegularCross(Shape):
    """Правильный крест (Kr)."""
    def __init__(self, center: QPointF, size: float, parent=None):
        super().__init__(parent)
        self.center = center
        self.size = max(1.0, size) # Минимальный размер
        self._recalculate_points()

    def _recalculate_points(self):
        """Пересчитывает вершины креста."""
        self.prepareGeometryChange()
        self._points = []
        cx, cy = self.center.x(), self.center.y()
        half_size = self.size / 2.0
        bar_width_ratio = 0.2 # Относительная ширина перекладин креста
        bar_half_width = half_size * bar_width_ratio

        # Вершины (по часовой стрелке, начиная с верхней части вертикальной перекладины)
        p = [
            QPointF(cx - bar_half_width, cy - half_size), # 0: Top-left of vertical bar
            QPointF(cx + bar_half_width, cy - half_size), # 1: Top-right of vertical bar
            QPointF(cx + bar_half_width, cy - bar_half_width), # 2: Right-top of horizontal bar
            QPointF(cx + half_size,      cy - bar_half_width), # 3: Right-end top
            QPointF(cx + half_size,      cy + bar_half_width), # 4: Right-end bottom
            QPointF(cx + bar_half_width, cy + bar_half_width), # 5: Right-bottom of horizontal bar
            QPointF(cx + bar_half_width, cy + half_size),      # 6: Bottom-right of vertical bar
            QPointF(cx - bar_half_width, cy + half_size),      # 7: Bottom-left of vertical bar
            QPointF(cx - bar_half_width, cy + bar_half_width), # 8: Left-bottom of horizontal bar
            QPointF(cx - half_size,      cy + bar_half_width), # 9: Left-end bottom
            QPointF(cx - half_size,      cy - bar_half_width), # 10: Left-end top
            QPointF(cx - bar_half_width, cy - bar_half_width), # 11: Left-top of horizontal bar
        ]
        self._points = p
        self.update()



    def paint(self, painter: QPainter, option, widget=None):
        brush_color = self._color

        # Меняем цвет заливки при выделении/подсветке
        if self.isSelected():
            brush_color = QColor(SELECTED_COLOR)
        elif self._is_hovered_for_tmo:
            brush_color = QColor(HOVER_COLOR)

        painter.setPen(Qt.PenStyle.NoPen)  # ❌ убираем контур
        painter.setBrush(QBrush(brush_color))  # ✅ заливаем нужным цветом

        if len(self._points) > 2:
            painter.drawPolygon(QPolygonF(self._points))  # ✅ рисуем полигон

        

    # Используем стандартный paint и shape для полигона

class PolygonShape(Shape):
    """Класс для представления произвольных многоугольников (FPg)
       и результатов ТМО."""


    def __init__(self, points: list[QPointF], parent=None):
        super().__init__(parent)
        
        if not points:
            self._points = []
            return

        # Убедимся, что полигон замкнут
        self._points = list(points)  # делаем копию списка

        if len(self._points) >= 1 and self._points[0] != self._points[-1]:
            self._points.append(QPointF(self._points[0]))  # замыкаем


    def paint(self, painter: QPainter, option, widget=None):
        brush_color = self._color

        if self.isSelected():
            brush_color = QColor(SELECTED_COLOR)
        elif self._is_hovered_for_tmo:
            brush_color = QColor(HOVER_COLOR)

        painter.setPen(Qt.PenStyle.NoPen)  # ❌ убираем контур
        painter.setBrush(QBrush(brush_color))  # ✅ заливаем цветом

        if len(self._points) > 2:
            painter.drawPolygon(QPolygonF(self._points))  # ✅ рисуем замкнутую фигуру



    def get_points(self) -> list[QPointF]:
        return self._points.copy()  # Возвращаем копию, чтобы не изменить случайно оригинал

        

    # paint, boundingRect, shape наследуются и подходят для полигонов

# --- Класс для выполнения преобразований ---
class Transformations:
    """Предоставляет методы для создания матриц преобразований."""

    @staticmethod
    def create_identity() -> np.ndarray:
        """Возвращает единичную матрицу 3x3."""
        return np.identity(3)

    @staticmethod
    def create_translate_matrix(dx: float, dy: float) -> np.ndarray:
        """Матрица переноса."""
        return np.array([
            [1.0, 0.0, dx],
            [0.0, 1.0, dy],
            [0.0, 0.0, 1.0]
        ])

    @staticmethod
    def create_scale_matrix(sx: float, sy: float, center: QPointF) -> np.ndarray:
        """Матрица масштабирования относительно центра."""
        cx, cy = center.x(), center.y()
        # Перенос в начало координат -> Масштаб -> Перенос обратно
        to_origin = Transformations.create_translate_matrix(-cx, -cy)
        scale = np.array([
            [sx,  0.0, 0.0],
            [0.0, sy,  0.0],
            [0.0, 0.0, 1.0]
        ])
        from_origin = Transformations.create_translate_matrix(cx, cy)
        return from_origin @ scale @ to_origin # Порядок важен!

    @staticmethod
    def create_rotate_matrix(angle_degrees: float, center: QPointF) -> np.ndarray:
        """Матрица поворота вокруг центра."""
        cx, cy = center.x(), center.y()
        angle_rad = degrees_to_radians(angle_degrees)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        # Перенос в начало координат -> Поворот -> Перенос обратно
        to_origin = Transformations.create_translate_matrix(-cx, -cy)
        rotate = np.array([
            [cos_a, -sin_a, 0.0],
            [sin_a, cos_a,  0.0],
            [0.0,   0.0,    1.0]
        ])
        from_origin = Transformations.create_translate_matrix(cx, cy)
        return from_origin @ rotate @ to_origin

    @staticmethod
    def create_reflect_vertical_matrix(x_line: float) -> np.ndarray:
        """Матрица зеркального отражения относительно вертикальной линии x = x_line (MV)."""
        # Перенос линии в ось Y -> Отражение -> Перенос обратно
        to_origin = Transformations.create_translate_matrix(-x_line, 0.0)
        reflect = np.array([
            [-1.0, 0.0, 0.0],
            [ 0.0, 1.0, 0.0],
            [ 0.0, 0.0, 1.0]
        ])
        from_origin = Transformations.create_translate_matrix(x_line, 0.0)
        return from_origin @ reflect @ to_origin

# --- Класс холста для рисования ---
class Canvas(QGraphicsScene):
    """Сцена для отображения и взаимодействия с фигурами."""
    # Сигнал, испускаемый при изменении состояния (для обновления статусбара и т.п.)
    status_changed = pyqtSignal(str)
    # Сигнал для обновления списка доступных действий (когда меняется выделение)
    selection_changed_signal = pyqtSignal()



    def _draw_temp_markers(self):
        """Рисует временные маркеры для создания объектов (например, кривой Безье, звезды, креста)."""
        # Удаляем старые маркеры
        for item in self.items():
            if hasattr(item, 'is_temp_marker'):
                self.removeItem(item)

        if not self.temp_points:
            return

        # Параметры стиля маркеров
        marker_radius = 5
        bg_color = Qt.GlobalColor.darkBlue
        fg_color = Qt.GlobalColor.white
        line_color = Qt.GlobalColor.blue
        font_size = 8

        for i, point in enumerate(self.temp_points):
            # Рисуем круглый маркер
            ellipse = self.addEllipse(
                point.x() - marker_radius,
                point.y() - marker_radius,
                2 * marker_radius,
                2 * marker_radius,
                QPen(line_color),
                QBrush(bg_color)
            )

            # Рисуем текст с номером точки
            text_item = self.addText(str(i + 1))
            text_font = text_item.font()
            text_font.setPointSize(font_size)
            text_font.setBold(True)
            text_item.setFont(text_font)
            text_item.setDefaultTextColor(fg_color)

            # Центрируем текст относительно точки
            text_rect = text_item.boundingRect()
            text_item.setPos(
                point.x() - text_rect.width() / 2,
                point.y() - text_rect.height() / 2
            )

            # Метим элементы как временные
            ellipse.is_temp_marker = True
            text_item.is_temp_marker = True

    

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tool = 'select' # 'select', 'draw_bz', 'draw_zv', 'draw_kr', 'tmo_intersect_1', 'tmo_symdiff_1'
        self.temp_points = [] # Временные точки для создания фигур
        self.first_tmo_operand = None # Первая фигура, выбранная для ТМО
        self.setBackgroundBrush(QBrush(Qt.GlobalColor.white))
        self.setSceneRect(0, 0, 800, 600) # Начальный размер сцены

        # Переопределяем обработку выделения
        self.selectionChanged.connect(self._handle_selection_change)

    def set_tool(self, tool_name: str):
        """Устанавливает текущий инструмент."""
        self.current_tool = tool_name
        self.status_changed.emit(f"Инструмент: {self.get_tool_description(tool_name)}")
        self.clear_tmo_selection() # Сбрасываем выбор ТМО при смене инструмента
        # Сбрасываем временные точки, если переключились с инструмента рисования
        if not tool_name.startswith('draw_'):
            self.temp_points = []


    def get_tool_description(self, tool_name):
        """Возвращает русское описание инструмента."""
        descriptions = {
            'select': "Выделение / Перемещение",
            'draw_bz': "Рисование кривой Безье (4 клика)",
            'draw_zv': "Рисование звезды (центр, точка радиуса, ввод N)",
            'draw_kr': "Рисование креста (центр, клик для размера)",
            'tmo_intersect_1': "ТМО: Пересечение (выберите 1-ю фигуру)",
            'tmo_intersect_2': "ТМО: Пересечение (выберите 2-ю фигуру)",
            'tmo_symdiff_1': "ТМО: Симм. разность (выберите 1-ю фигуру)",
            'tmo_symdiff_2': "ТМО: Симм. разность (выберите 2-ю фигуру)",
        }
        return descriptions.get(tool_name, "Неизвестный инструмент")

    def get_selected_item(self) -> Shape | None:
        """Возвращает единственный выделенный элемент или None."""
        selected = self.selectedItems()
        if len(selected) == 1 and isinstance(selected[0], Shape):
            return selected[0]
        return None

    def get_selected_items(self) -> list[Shape]:
        """Возвращает список выделенных элементов типа Shape."""
        return [item for item in self.selectedItems() if isinstance(item, Shape)]

    def clear_tmo_selection(self):
        """Сбрасывает выделение для ТМО."""
        if self.first_tmo_operand:
            self.first_tmo_operand.set_hovered_for_tmo(False)
            self.first_tmo_operand = None
        # Сбрасываем подсветку у всех остальных на всякий случай
        for item in self.items():
            if isinstance(item, Shape):
                item.set_hovered_for_tmo(False)

        # Обновляем статус, если были в режиме ТМО
        if self.current_tool.startswith('tmo_') and not self.current_tool.endswith('_1'):
            base_tool = self.current_tool.split('_')[1] # intersect или symdiff
            self.set_tool(f"tmo_{base_tool}_1")


    def _handle_selection_change(self):
        """Обработчик изменения выделения на сцене."""
        # Не вызываем, если мы в процессе выбора для ТМО
        if not self.current_tool.startswith('tmo_'):
             self.selection_changed_signal.emit()
             selected = self.get_selected_item()
             if selected:
                 self.status_changed.emit(f"Выбрана фигура: {selected.__class__.__name__}")
             elif not self.current_tool.startswith('draw_'): # Если не рисуем новую
                 self.set_tool('select') # Возвращаемся к выделению, если ничего не выбрано

    # --- Обработка событий мыши на сцене ---
    def mousePressEvent(self, event):
        """Обработка нажатия кнопки мыши."""
        pos = event.scenePos()
        item_at_pos = self.itemAt(pos, QTransform()) # Получаем элемент под курсором

        # --- Логика для инструментов рисования ---
        if self.current_tool == 'draw_bz':
            self.temp_points.append(pos)
            n_points = len(self.temp_points)
            self.status_changed.emit(f"Рисование Безье: Точка {n_points}/4")
            self._draw_temp_markers()
            if n_points == 4:
                shape = BezierCurve(*self.temp_points)
                self.addItem(shape)
                self.temp_points = []
                self._draw_temp_markers()  # Очистка
                self.set_tool('select')



        elif self.current_tool == 'draw_zv':
            self.temp_points.append(pos)
            n_points = len(self.temp_points)
            self._draw_temp_markers()

            if n_points == 1:
                self.status_changed.emit("Звезда: Укажите точку на радиусе")
            elif n_points == 2:
                center = self.temp_points[0]
                radius_point = self.temp_points[1]

                dialog = QInputDialog(self.parent().parent())
                dialog.setInputMode(QInputDialog.InputMode.IntInput)
                dialog.setIntMinimum(3)
                dialog.setIntMaximum(20)
                dialog.setIntValue(5)
                dialog.setWindowTitle("Количество вершин звезды")
                dialog.setLabelText("Введите N (от 3 до 20):")

                if dialog.exec() == QInputDialog.DialogCode.Accepted:
                    n = dialog.intValue()
                    shape = NStar(center, radius_point, n)
                    self.addItem(shape)

                # Сбрасываем
                self.temp_points = []
                self._draw_temp_markers()  # удаляет маркеры
                self.set_tool('select')





        elif self.current_tool == 'draw_kr':
            self.temp_points.append(pos)
            n_points = len(self.temp_points)
            self._draw_temp_markers()

            if n_points == 1:
                self.status_changed.emit("Крест: Кликните, чтобы определить размер")
            elif n_points == 2:
                center = self.temp_points[0]
                size_point = self.temp_points[1]
                size = math.sqrt((size_point.x() - center.x()) ** 2 +
                                 (size_point.y() - center.y()) ** 2) * 1.5  # масштабируем немного

                shape = RegularCross(center, size)
                self.addItem(shape)

                # Сбрасываем
                self.temp_points = []
                self._draw_temp_markers()
                self.set_tool('select')




                

        # --- Логика для инструментов ТМО ---
        elif self.current_tool in ['tmo_intersect_1', 'tmo_symdiff_1']:
            if isinstance(item_at_pos, Shape):
                 # Выбрали первый операнд
                 self.first_tmo_operand = item_at_pos
                 self.first_tmo_operand.set_hovered_for_tmo(True) # Подсветим его
                 if self.current_tool == 'tmo_intersect_1':
                     self.set_tool('tmo_intersect_2')
                 else:
                     self.set_tool('tmo_symdiff_2')
                 self.clearSelection() # Снимем общее выделение
                 event.accept() # Событие обработано здесь
                 return # Не передаем дальше
            else:
                 self.status_changed.emit("Ошибка ТМО: Кликните на фигуру")
                 self.clear_tmo_selection()

        elif self.current_tool in ['tmo_intersect_2', 'tmo_symdiff_2']:
            if isinstance(item_at_pos, Shape) and item_at_pos != self.first_tmo_operand:
                # Выбрали второй операнд
                second_operand = item_at_pos
                op_type = 'intersect' if self.current_tool == 'tmo_intersect_2' else 'symdiff'

                # --- Выполнение ТМО (ЗАГЛУШКИ) ---

                
                result_shapes = self.perform_tmo(self.first_tmo_operand, second_operand, op_type)

                if result_shapes:
                    for shape in result_shapes:
                        self.addItem(shape)
                    # Удаление операндов
                    self.removeItem(self.first_tmo_operand)
                    self.removeItem(second_operand)
                    self.status_changed.emit(f"ТМО '{op_type}' выполнено: создано {len(result_shapes)} новых фигур")
                else:
                    self.status_changed.emit(f"Ошибка ТМО '{op_type}': Не удалось выполнить операцию или результат пустой")

                self.clear_tmo_selection()
                self.set_tool('select') # Возвращаемся к выделению
                event.accept()
                return
            elif item_at_pos == self.first_tmo_operand:
                 self.status_changed.emit("Ошибка ТМО: Выберите ДРУГУЮ фигуру")
            else:
                 self.status_changed.emit("Ошибка ТМО: Кликните на фигуру")
                 # Не сбрасываем выбор первого операнда, даем шанс выбрать второй

        # --- Логика для инструмента выделения ---
        elif self.current_tool == 'select':
            # Если кликнули не по элементу, снимаем выделение со всех
            if not item_at_pos:
                self.clearSelection()
                self.selection_changed_signal.emit() # Обновить доступность действий
            # Стандартная обработка выбора/перемещения QGraphicsScene/QGraphicsItem
            super().mousePressEvent(event)



    def perform_tmo(self, shape1: Shape, shape2: Shape, operation: str) -> list[Shape] | None:
        

        def to_shapely_polygon(shape: Shape):
            # Преобразуем NStar и RegularCross во временный PolygonShape
            if isinstance(shape, (NStar, RegularCross)):
                points = shape.get_points()
                if points and points[0] != points[-1]:
                    points.append(points[0])  # замыкаем
                shape = PolygonShape(points)

            pts = [(p.x(), p.y()) for p in shape.get_points()]
            if len(pts) < 3:
                return None
            if pts[0] != pts[-1]:
                pts.append(pts[0])
            try:
                poly = ShapelyPolygon(pts)
                if not poly.is_valid:
                    poly = poly.buffer(0)
                return poly
            except Exception as e:
                print(f"[TMO] Ошибка создания полигона: {e}")
                return None

        poly1 = to_shapely_polygon(shape1)
        poly2 = to_shapely_polygon(shape2)

        if not poly1 or not poly2:
            print("[TMO] Невалидные полигоны")
            return None

        try:
            if operation == "symdiff":
                result_geom = poly1.symmetric_difference(poly2)
            elif operation == "intersect":
                result_geom = poly1.intersection(poly2)
            else:
                print(f"[TMO] Неизвестная операция: {operation}")
                return None
        except Exception as e:
            print(f"[TMO] Ошибка операции: {e}")
            return None

        if result_geom.is_empty:
            return None

        def extract_polygons(geom):
            from shapely import GeometryType

            if geom.is_empty:
                return []

            if geom.geom_type == 'MultiPolygon':
                return list(geom.geoms)
            elif geom.geom_type == 'Polygon':
                return [geom]
            elif geom.geom_type == 'GeometryCollection':
                # Выбираем только полигоны из коллекции
                return [g for g in geom.geoms if g.geom_type == 'Polygon']
            return []

        result_shapes = []
        for polygon in extract_polygons(result_geom):
            coords = list(polygon.exterior.coords)
            if len(coords) >= 3:
                qpoints = [QPointF(x, y) for x, y in coords]
                result_shapes.append(PolygonShape(qpoints))

        return result_shapes if result_shapes else None





        # --- ВАЖНО: Реализация ТМО ---
        # Это очень сложная часть. Для полигонов требуются алгоритмы клиппинга
        # (например, Сазерленда-Ходжмена для пересечения, Уайлера-Атертона для
        # объединения, разности, симметричной разности).
        # Для кривых Безье это еще сложнее.
        # Библиотека `shapely` может сильно помочь с полигонами.

        # Примерная логика с использованием Shapely (если бы она была интегрирована):
        # try:
        #     poly1 = shapely.geometry.Polygon([(p.x(), p.y()) for p in shape1.get_points()])
        #     poly2 = shapely.geometry.Polygon([(p.x(), p.y()) for p in shape2.get_points()])
        #
        #     result_poly = None
        #     if operation == 'intersect':
        #         result_poly = poly1.intersection(poly2)
        #     elif operation == 'symdiff': # symmetric_difference
        #         result_poly = poly1.symmetric_difference(poly2)
        #     # Добавить другие операции: union, difference
        #
        #     if result_poly and not result_poly.is_empty:
        #         # Преобразовать результат обратно в QPointF
        #         # Обработка MultiPolygon, если результат состоит из нескольких частей
        #         if isinstance(result_poly, shapely.geometry.Polygon):
        #              points = [QPointF(x, y) for x, y in result_poly.exterior.coords]
        #              return PolygonShape(points)
        #         # elif isinstance(result_poly, shapely.geometry.MultiPolygon):
        #         #     # TODO: Обработать случай с несколькими полигонами
        #         #     pass
        # except Exception as e:
        #     print(f"Ошибка при выполнении ТМО с Shapely: {e}")
        #     return None


        # Заглушка: возвращаем None, показывая, что операция не реализована
        QMessageBox.warning(self.parent().parent() if self.parent() else None,
                           "ТМО не реализовано",
                           f"Операция '{operation}' между полигонами/кривыми пока не поддерживается.")
        return None

    def mouseMoveEvent(self, event):
        """Обработка движения мыши."""
        pos = event.scenePos()
        self.status_changed.emit(f"X: {pos.x():.1f}, Y: {pos.y():.1f}")

        # Если мы в режиме выбора второго операнда ТМО, подсвечиваем фигуру под мышкой
        if self.current_tool in ['tmo_intersect_2', 'tmo_symdiff_2']:
             item_at_pos = self.itemAt(pos, QTransform())
             # Убираем подсветку со всех, кроме первого операнда
             for item in self.items():
                 if isinstance(item, Shape) and item != self.first_tmo_operand:
                     item.set_hovered_for_tmo(False)
             # Подсвечиваем текущую, если это Shape и не первый операнд
             if isinstance(item_at_pos, Shape) and item_at_pos != self.first_tmo_operand:
                 item_at_pos.set_hovered_for_tmo(True)

        super().mouseMoveEvent(event) # Стандартная обработка перемещения выделенных

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш."""
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected()
        elif event.key() == Qt.Key.Key_Escape:
             # Отмена текущего действия
             if self.current_tool.startswith('draw_') and self.temp_points:
                 self.temp_points = []
                 self.status_changed.emit("Рисование отменено.")
             elif self.current_tool.startswith('tmo_'):
                 self.clear_tmo_selection()
                 self.set_tool('select')
                 self.status_changed.emit("Выбор для ТМО отменен.")
             else:
                 self.clearSelection()
                 self.selection_changed_signal.emit()
        else:
            super().keyPressEvent(event) # Стандартная обработка

    # --- Функции действий ---
    def set_object_color(self):
        """Запросить цвет у пользователя и применить к выделенным."""
        selected = self.get_selected_items()
        if not selected:
            self.status_changed.emit("Нет выделенных фигур для смены цвета.")
            return

        # Берем цвет первого выделенного как начальный для диалога
        initial_color = selected[0].get_color()
        color = QColorDialog.getColor(initial_color, self.parent().parent() if self.parent() else None, "Выберите цвет")

        if color.isValid():
            for item in selected:
                item.set_color(color)
            self.status_changed.emit(f"Цвет {len(selected)} фигур изменен.")

    def delete_selected(self):
        """Удаляет выделенные фигуры."""
        selected = self.get_selected_items()
        if not selected:
            self.status_changed.emit("Нет выделенных фигур для удаления.")
            return

        reply = QMessageBox.question(self.parent().parent() if self.parent() else None, "Удаление",
                                     f"Удалить {len(selected)} выбранных фигур?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            count = 0
            for item in selected:
                self.removeItem(item)
                count += 1
            self.status_changed.emit(f"Удалено {count} фигур.")
            self.selection_changed_signal.emit() # Обновить доступность действий

    def transform_selected(self, transformation_type: str):
        """Применяет выбранное преобразование к выделенному объекту."""
        item = self.get_selected_item()
        if not item:
            self.status_changed.emit("Нет выделенной фигуры для преобразования.")
            return

        matrix = Transformations.create_identity()
        center = item.get_center() # Центр фигуры по умолчанию

        try:
            if transformation_type == 'translate':
                dx, ok1 = QInputDialog.getDouble(self.parent().parent(), "Перемещение", "Смещение по X:", 0.0, -10000, 10000, 1)
                if not ok1: return
                dy, ok2 = QInputDialog.getDouble(self.parent().parent(), "Перемещение", "Смещение по Y:", 0.0, -10000, 10000, 1)
                if not ok2: return
                matrix = Transformations.create_translate_matrix(dx, dy)

            elif transformation_type == 'rotate_center': # Rf - Поворот вокруг центра фигуры
                angle, ok = QInputDialog.getDouble(self.parent().parent(), "Поворот (Rf)", "Угол (градусы):", 0.0, -360, 360, 1)
                if not ok: return
                matrix = Transformations.create_rotate_matrix(angle, center)

            elif transformation_type == 'scale_y_center': # Syc - Масштаб Y отн. заданного центра
                sy, ok1 = QInputDialog.getDouble(self.parent().parent(), "Масштаб Y (Syc)", "Коэффициент по Y:", 1.0, 0.01, 100, 2)
                if not ok1: return
                cx, ok2 = QInputDialog.getDouble(self.parent().parent(), "Масштаб Y (Syc)", "Центр X:", center.x(), -10000, 10000, 1)
                if not ok2: return
                cy, ok3 = QInputDialog.getDouble(self.parent().parent(), "Масштаб Y (Syc)", "Центр Y:", center.y(), -10000, 10000, 1)
                if not ok3: return
                scale_center = QPointF(cx, cy)
                matrix = Transformations.create_scale_matrix(1.0, sy, scale_center) # Масштаб только по Y

            elif transformation_type == 'reflect_vertical': # MV - Отражение отн. верт. прямой
                x_line, ok = QInputDialog.getDouble(self.parent().parent(), "Отражение (MV)", "Координата X вертикальной линии:", center.x(), -10000, 10000, 1)
                if not ok: return
                matrix = Transformations.create_reflect_vertical_matrix(x_line)

            else:
                 self.status_changed.emit(f"Неизвестное преобразование: {transformation_type}")
                 return

            # Применяем матрицу
            item.apply_transformation(matrix)
            self.status_changed.emit(f"Преобразование '{transformation_type}' применено.")
            item.setSelected(False) # Сбрасываем выделение после трансформации
            item.setSelected(True)  # и снова выбираем, чтобы обновить BoundingBox и т.п.

        except ValueError:
            QMessageBox.warning(self.parent().parent(), "Ошибка ввода", "Неверный формат числа.")
        except Exception as e:
             QMessageBox.critical(self.parent().parent(), "Ошибка преобразования", f"Произошла ошибка: {e}")
             print(f"Ошибка преобразования: {e}") # Для отладки

# --- Класс главного окна приложения ---
class MainWindow(QMainWindow):
    """Главное окно редактора."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графический Редактор (Вариант 79)")
        self.setGeometry(100, 100, 1000, 700) # Положение и размер окна

        # --- Центральный виджет и сцена ---
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0,0,0,0) # Убираем отступы

        self.scene = Canvas(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing) # Включаем сглаживание
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag) # Выделение рамкой
        self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate) # Режим обновления

        layout.addWidget(self.view)

        # --- Панель инструментов ---
        self.toolbar = QToolBar("Инструменты")
        self.toolbar.setMovable(False) # Запрещаем перемещение
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        # --- Статус бар ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.scene.status_changed.connect(self.status_bar.showMessage)
        self.status_bar.showMessage("Редактор готов.")

        # --- Действия (Actions) ---
        self.create_actions()

        # --- Меню ---
        self.create_menus()

        # --- Заполнение панели инструментов ---
        self.populate_toolbar()

        # Соединяем сигнал изменения выделения с обновлением доступности действий
        self.scene.selection_changed_signal.connect(self.update_action_states)
        self.update_action_states() # Начальное состояние

    def create_actions(self):
        """Создает все действия для меню и панелей инструментов."""
        # Инструменты рисования
        self.action_select_tool = QAction(QIcon(), "Выделение", self) # TODO: Добавить иконки
        self.action_select_tool.setToolTip("Выбрать/Переместить фигуры (Esc для отмены)")
        self.action_select_tool.setCheckable(True)
        self.action_select_tool.triggered.connect(lambda: self.scene.set_tool('select'))

        self.action_draw_bz = QAction(QIcon(), "Кривая Безье (BZ)", self)
        self.action_draw_bz.setToolTip("Нарисовать кривую Безье (4 клика)")
        self.action_draw_bz.setCheckable(True)
        self.action_draw_bz.triggered.connect(lambda: self.scene.set_tool('draw_bz'))

        self.action_draw_zv = QAction(QIcon(), "Звезда (Zv)", self)
        self.action_draw_zv.setToolTip("Нарисовать правильную N-конечную звезду")
        self.action_draw_zv.setCheckable(True)
        self.action_draw_zv.triggered.connect(lambda: self.scene.set_tool('draw_zv'))

        self.action_draw_kr = QAction(QIcon(), "Крест (Kr)", self)
        self.action_draw_kr.setToolTip("Нарисовать правильный крест")
        self.action_draw_kr.setCheckable(True)
        self.action_draw_kr.triggered.connect(lambda: self.scene.set_tool('draw_kr'))

        # Группа для инструментов, чтобы только один был активен
        self.tool_action_group = QActionGroup(self)
        self.tool_action_group.addAction(self.action_select_tool)
        self.tool_action_group.addAction(self.action_draw_bz)
        self.tool_action_group.addAction(self.action_draw_zv)
        self.tool_action_group.addAction(self.action_draw_kr)
        self.action_select_tool.setChecked(True) # Выделение по умолчанию

        # Действия над объектами
        self.action_set_color = QAction(QIcon(), "Цвет...", self)
        self.action_set_color.setToolTip("Задать цвет для выделенных фигур")
        self.action_set_color.triggered.connect(self.scene.set_object_color)

        self.action_delete = QAction(QIcon(), "Удалить", self)
        self.action_delete.setToolTip("Удалить выделенные фигуры (Delete)")
        self.action_delete.setShortcut(Qt.Key.Key_Delete)
        self.action_delete.triggered.connect(self.scene.delete_selected)

        # Геометрические преобразования (для варианта 79)
        self.action_transform_translate = QAction("Перемещение...", self)
        self.action_transform_translate.triggered.connect(lambda: self.scene.transform_selected('translate'))

        self.action_transform_rotate_center = QAction("Поворот (Rf)...", self) # Rf
        self.action_transform_rotate_center.setToolTip("Поворот вокруг центра фигуры на заданный угол")
        self.action_transform_rotate_center.triggered.connect(lambda: self.scene.transform_selected('rotate_center'))

        self.action_transform_scale_y_center = QAction("Масштаб Y (Syc)...", self) # Syc
        self.action_transform_scale_y_center.setToolTip("Масштабирование по оси Y относительно заданного центра")
        self.action_transform_scale_y_center.triggered.connect(lambda: self.scene.transform_selected('scale_y_center'))

        self.action_transform_reflect_vertical = QAction("Отражение (MV)...", self) # MV
        self.action_transform_reflect_vertical.setToolTip("Зеркальное отражение относительно вертикальной прямой")
        self.action_transform_reflect_vertical.triggered.connect(lambda: self.scene.transform_selected('reflect_vertical'))

        # ТМО (для варианта 79)
        self.action_tmo_intersect = QAction("Пересечение ()", self)
        self.action_tmo_intersect.setToolTip("Выполнить пересечение двух фигур")
        self.action_tmo_intersect.triggered.connect(lambda: self.scene.set_tool('tmo_intersect_1'))

        self.action_tmo_symdiff = QAction("Симм. разность ()", self)
        self.action_tmo_symdiff.setToolTip("Выполнить симметричную разность двух фигур")
        self.action_tmo_symdiff.triggered.connect(lambda: self.scene.set_tool('tmo_symdiff_1'))

        # Общие действия
        self.action_exit = QAction("Выход", self)
        self.action_exit.setShortcut("Ctrl+Q")
        self.action_exit.triggered.connect(self.close)

        self.action_about = QAction("О программе", self)
        self.action_about.triggered.connect(self.show_about_dialog)

        # Действия, зависящие от выделения
        self.selection_dependent_actions = [
            self.action_set_color, self.action_delete,
            self.action_transform_translate, self.action_transform_rotate_center,
            self.action_transform_scale_y_center, self.action_transform_reflect_vertical
        ]
        # Действия ТМО зависят от наличия хотя бы двух фигур
        self.tmo_actions = [self.action_tmo_intersect, self.action_tmo_symdiff]


    def create_menus(self):
        """Создает меню программы."""
        menu_bar = self.menuBar()

        # Меню Файл
        file_menu = menu_bar.addMenu("Файл")
        # TODO: Добавить действия Открыть/Сохранить (требует сериализации фигур)
        file_menu.addAction(self.action_exit)

        # Меню Правка
        edit_menu = menu_bar.addMenu("Правка")
        edit_menu.addAction(self.action_delete)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_set_color)

        # Меню Фигуры (для создания)
        shapes_menu = menu_bar.addMenu("Фигуры")
        shapes_menu.addAction(self.action_draw_bz)
        shapes_menu.addAction(self.action_draw_zv)
        shapes_menu.addAction(self.action_draw_kr)
        # TODO: Добавить другие фигуры, если нужно (например, Отрезок)

        # Меню Преобразования
        transform_menu = menu_bar.addMenu("Преобразования")
        transform_menu.addAction(self.action_transform_translate)
        transform_menu.addSeparator()
        transform_menu.addAction(self.action_transform_rotate_center) # Rf
        transform_menu.addAction(self.action_transform_scale_y_center) # Syc
        transform_menu.addAction(self.action_transform_reflect_vertical) # MV
        # TODO: Добавить другие преобразования из варианта, если они есть

        # Меню ТМО
        tmo_menu = menu_bar.addMenu("ТМО")
        tmo_menu.addAction(self.action_tmo_intersect) # 
        tmo_menu.addAction(self.action_tmo_symdiff)   # 

        # Меню Справка
        help_menu = menu_bar.addMenu("Справка")
        help_menu.addAction(self.action_about)

    def populate_toolbar(self):
        """Заполняет панель инструментов действиями."""
        self.toolbar.addAction(self.action_select_tool)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_draw_bz)
        self.toolbar.addAction(self.action_draw_zv)
        self.toolbar.addAction(self.action_draw_kr)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_set_color)
        self.toolbar.addAction(self.action_delete)
        self.toolbar.addSeparator()
        # Можно добавить кнопки для часто используемых преобразований/ТМО
        self.toolbar.addAction(self.action_transform_rotate_center)
        self.toolbar.addAction(self.action_transform_reflect_vertical)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_tmo_intersect)
        self.toolbar.addAction(self.action_tmo_symdiff)


    def update_action_states(self):
        """Обновляет доступность действий в зависимости от выделения."""
        selected_items = self.scene.get_selected_items()
        has_selection = len(selected_items) > 0
        is_single_selection = len(selected_items) == 1
        can_perform_tmo = len(self.scene.items()) >= 2 # Проверяем общее кол-во фигур на сцене

        # Действия, требующие хотя бы одного выделенного элемента
        for action in self.selection_dependent_actions:
            action.setEnabled(has_selection)

        # Преобразования требуют ровно одного выделенного элемента
        # (Хотя можно было бы реализовать и для группы)
        self.action_transform_translate.setEnabled(is_single_selection)
        self.action_transform_rotate_center.setEnabled(is_single_selection)
        self.action_transform_scale_y_center.setEnabled(is_single_selection)
        self.action_transform_reflect_vertical.setEnabled(is_single_selection)

        # ТМО требуют наличия хотя бы двух фигур на сцене
        for action in self.tmo_actions:
            action.setEnabled(can_perform_tmo)

    def show_about_dialog(self):
        """Показывает диалоговое окно "О программе"."""
        QMessageBox.about(self, "О программе",
                          "<b>Графический Редактор v0.1</b><br><br>"
                          "Курсовая работа (Вариант 79)<br>"
                          "Реализованы фигуры: Безье (BZ), Звезда (Zv), Крест (Kr).<br>"
                          "Преобразования: Поворот (Rf), Масштаб Y (Syc), Отражение (MV), Перемещение.<br>"
                          "ТМО: Пересечение (), Симм. разность () - <i>заглушки</i>.<br><br>"
                          "Использует Python и PyQt6.")

    def closeEvent(self, event):
        """Обработка события закрытия окна."""
        # TODO: Добавить проверку несохраненных изменений, если будет функционал сохр.
        super().closeEvent(event)

# --- Запуск приложения ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
