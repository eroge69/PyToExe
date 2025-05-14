import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QListWidget, QTabWidget, QLabel, QPushButton)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


class RoutingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Программа маршрутизации транспортных средств")
        self.setGeometry(100, 100, 1200, 800)
        
        self.initUI()
    
    def initUI(self):
        # Главный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Сплиттер для разделения карты и списков
        splitter = QSplitter()
        
        # Левая часть - Яндекс карта
        self.map_view = QWebEngineView()
        self.map_view.setHtml("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Яндекс Карта</title>
            <script src="https://api-maps.yandex.ru/2.1/?apikey=06e543de-35d6-4f8d-8899-46a6654c7b9d
&lang=ru_RU" type="text/javascript"></script>
            <style>
                html, body, #map {
                    width: 100%;
                    height: 100%;
                    padding: 0;
                    margin: 0;
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                ymaps.ready(init);
                function init() {
                    var map = new ymaps.Map("map", {
                        center: [55.751574, 37.573856],
                        zoom: 10
                    });
                    
                    // Пример маркеров (можно удалить)
                    var placemark1 = new ymaps.Placemark([55.751574, 37.573856], {
                        hintContent: 'Москва',
                        balloonContent: 'Столица России'
                    });
                    
                    map.geoObjects.add(placemark1);
                }
            </script>
        </body>
        </html>
        """)
        
        # Правая часть - табы с заказами и транспортом
        right_panel = QTabWidget()
        
        # Вкладка с нераспределенными заказами
        unassigned_tab = QWidget()
        unassigned_layout = QVBoxLayout(unassigned_tab)
        unassigned_layout.addWidget(QLabel("Нераспределенные заказы:"))
        self.unassigned_list = QListWidget()
        
        # Добавляем тестовые данные
        self.unassigned_list.addItems([
            "Заказ #1001: ул. Ленина, 10 → ул. Гагарина, 5",
            "Заказ #1002: пр. Мира, 15 → ул. Садовая, 3",
            "Заказ #1003: ул. Центральная, 1 → ул. Школьная, 7"
        ])
        
        unassigned_layout.addWidget(self.unassigned_list)
        assign_button = QPushButton("Назначить на транспорт")
        unassigned_layout.addWidget(assign_button)
        
        right_panel.addTab(unassigned_tab, "Нераспределенные")
        
        # Вкладка с заказами в маршруте
        in_route_tab = QWidget()
        in_route_layout = QVBoxLayout(in_route_tab)
        in_route_layout.addWidget(QLabel("Заказы в маршруте:"))
        self.in_route_list = QListWidget()
        
        # Добавляем тестовые данные
        self.in_route_list.addItems([
            "Транспорт #1: Заказ #1004 → Заказ #1005",
            "Транспорт #2: Заказ #1006"
        ])
        
        in_route_layout.addWidget(self.in_route_list)
        complete_button = QPushButton("Завершить маршрут")
        in_route_layout.addWidget(complete_button)
        
        right_panel.addTab(in_route_tab, "В маршруте")
        
        # Вкладка с транспортом
        vehicles_tab = QWidget()
        vehicles_layout = QVBoxLayout(vehicles_tab)
        vehicles_layout.addWidget(QLabel("Транспортные средства:"))
        self.vehicles_list = QListWidget()
        
        # Добавляем тестовые данные
        self.vehicles_list.addItems([
            "Грузовик #1 (ГАЗель) - Свободен",
            "Грузовик #2 (Камаз) - В маршруте",
            "Фургон #3 (Ford Transit) - Свободен"
        ])
        
        vehicles_layout.addWidget(self.vehicles_list)
        add_vehicle_button = QPushButton("Добавить транспорт")
        vehicles_layout.addWidget(add_vehicle_button)
        
        right_panel.addTab(vehicles_tab, "Транспорт")
        
        # Добавляем виджеты в сплиттер
        splitter.addWidget(self.map_view)
        splitter.addWidget(right_panel)
        splitter.setSizes([800, 400])
        
        main_layout.addWidget(splitter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoutingApp()
    window.show()
    sys.exit(app.exec_())
