import os
import sys
import numpy as np
import pyaudio
import time
import threading
from collections import deque
from PyQt5 import QtWidgets, QtCore, QtGui
import noisereduce as nr
import queue
import scipy.signal as signal

# Константы
CHUNK = 512  # Размер буфера для быстрого отклика
FORMAT = pyaudio.paInt16
RATE = 44100
SILENCE_THRESHOLD = 500   # Порог тишины
QUIET_THRESHOLD = 1500    # Порог тихой речи
MEDIUM_THRESHOLD = 3000   # Порог средней громкости
LOUD_THRESHOLD = 8000     # Порог громкой речи

# Константы для сглаживания
HISTORY_SIZE = 10         # Размер буфера истории громкости
MIN_STATE_DURATION = 0.1  # Минимальная продолжительность состояния в секундах

# Настройки шумоподавления
NOISE_REDUCTION_ENABLED = True   # Включено ли шумоподавление
NOISE_REDUCTION_STRENGTH = 0.5   # Уровень шумоподавления (0.0 - 1.0)
NOISE_STATIONARY = True          # Стационарный шум (true) или нестационарный (false)
NOISE_PROP_DECREASE = 0.95       # Коэффициент уменьшения шума (0.0 - 1.0)

# Глобальные переменные
audio_level = 0  # 0 - тишина, 1 - тихо, 2 - средне, 3 - громко
last_level_change = 0  # Время последнего изменения уровня
selected_mic_index = 0
is_running = True

# Создаем необходимые папки
os.makedirs('static', exist_ok=True)

# Класс для прозрачного окна VTuber
class VTuberWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # Создаем папку static, если она еще не существует
        os.makedirs('static', exist_ok=True)
        
        # Инициализация переменных
        self.audio_level = 0
        self.last_level_change = time.time()
        self.is_running = True
        self.selected_mic_index = 0
        self.hidden_mode = False
        
        # Очередь для буфера шума
        self.noise_profile_queue = queue.Queue()
        self.noise_profile = None
        self.calibrating_noise = False
        
        # Инициализация окна
        self.initUI()
        
        # Создание системного трея
        self.createTrayIcon()
        
        # Выбор микрофона и запуск анализатора звука
        self.selectMicrophone()
        self.startAudioAnalyzer()
    
    def initUI(self):
        # Настройка окна
        self.setWindowTitle('VTuber')
        self.setGeometry(100, 100, 400, 400)
        
        # Устанавливаем прозрачный фон
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        
        # Загружаем изображения
        self.loadImages()
        
        # Таймер для обновления изображения
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateImage)
        self.timer.start(50)  # 50 мс = 20 кадров в секунду
        
        self.show()
    
    def createTrayIcon(self):
        # Создаем иконку для системного трея
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        icon = QtGui.QIcon('static/silent.png')
        if not QtCore.QFile.exists('static/silent.png'):
            # Если иконка отсутствует, создаем заглушку
            pixmap = QtGui.QPixmap(64, 64)
            pixmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(pixmap)
            painter.setPen(QtGui.QPen(QtCore.Qt.white))
            painter.drawText(10, 32, "VTuber")
            painter.end()
            icon = QtGui.QIcon(pixmap)
        
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip('VTuber')
        
        # Создаем контекстное меню для трея
        self.tray_menu = QtWidgets.QMenu()
        
        # Действие для показа/скрытия окна
        self.showHideAction = QtWidgets.QAction("Скрыть с экрана", self)
        self.showHideAction.triggered.connect(self.toggleVisibility)
        self.tray_menu.addAction(self.showHideAction)
        
        # Действие для калибровки шумоподавления
        self.calibrateAction = QtWidgets.QAction("Калибровать шумоподавление", self)
        self.calibrateAction.triggered.connect(self.calibrateNoiseReduction)
        self.tray_menu.addAction(self.calibrateAction)
        
        # Действие для настроек
        self.settingsAction = QtWidgets.QAction("Настройки", self)
        self.settingsAction.triggered.connect(self.openSettings)
        self.tray_menu.addAction(self.settingsAction)
        
        # Действие для перезагрузки изображений
        self.reloadAction = QtWidgets.QAction("Перезагрузить изображения", self)
        self.reloadAction.triggered.connect(self.loadImages)
        self.tray_menu.addAction(self.reloadAction)
        
        # Действие для выхода
        self.exitAction = QtWidgets.QAction("Выход", self)
        self.exitAction.triggered.connect(self.closeApp)
        self.tray_menu.addAction(self.exitAction)
        
        # Устанавливаем меню для трея
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # Подключаем сигнал активации трея
        self.tray_icon.activated.connect(self.trayActivated)
        
        # Показываем иконку трея
        self.tray_icon.show()
    
    def calibrateNoiseReduction(self):
        """Калибровка профиля шума для шумоподавления"""
        if not NOISE_REDUCTION_ENABLED:
            QtWidgets.QMessageBox.information(self, "Информация", "Шумоподавление отключено в настройках")
            return
        
        # Показываем диалог для начала калибровки
        reply = QtWidgets.QMessageBox.information(self, "Калибровка шумоподавления",
                                               "Сейчас будет произведена калибровка шумоподавления.\n\n"
                                               "Пожалуйста, убедитесь, что в помещении присутствует только фоновый шум,\n"
                                               "и вы не говорите в микрофон в течение 3 секунд калибровки.\n\n"
                                               "Нажмите OK для начала калибровки.",
                                               QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        
        if reply == QtWidgets.QMessageBox.Ok:
            self.calibrating_noise = True
            # Очищаем очередь
            while not self.noise_profile_queue.empty():
                self.noise_profile_queue.get()
            
            # Запускаем таймер для информирования пользователя о завершении калибровки
            QtCore.QTimer.singleShot(3000, self.showCalibrationComplete)
    
    def showCalibrationComplete(self):
        """Показать сообщение о завершении калибровки"""
        self.calibrating_noise = False
        QtWidgets.QMessageBox.information(self, "Калибровка завершена", 
                                        "Калибровка шумоподавления успешно завершена!")
    
    def toggleVisibility(self):
        # Переключаем видимость окна и меняем текст действия
        if not self.hidden_mode:
            self.hide()
            self.hidden_mode = True
            self.showHideAction.setText("Показать на экране")
        else:
            self.show()
            self.hidden_mode = False
            self.showHideAction.setText("Скрыть с экрана")
    
    def trayActivated(self, reason):
        # При двойном клике на иконку в трее показываем окно
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            if self.hidden_mode:
                self.show()
                self.hidden_mode = False
                self.showHideAction.setText("Скрыть с экрана")
    
    def loadImages(self):
        # Загружаем изображения
        self.images = []
        image_files = ['silent.png', 'quiet.png', 'medium.png', 'loud.png']
        
        for img_file in image_files:
            path = os.path.join('static', img_file)
            if os.path.exists(path):
                self.images.append(QtGui.QPixmap(path))
            else:
                # Если изображение отсутствует, создаем заглушку с текстом
                pixmap = QtGui.QPixmap(400, 400)
                pixmap.fill(QtCore.Qt.transparent)
                painter = QtGui.QPainter(pixmap)
                painter.setPen(QtGui.QPen(QtCore.Qt.white))
                painter.drawText(150, 200, f"Изображение {img_file} отсутствует")
                painter.end()
                self.images.append(pixmap)
    
    def updateImage(self):
        # Вызывается по таймеру для обновления изображения
        self.update()
    
    def paintEvent(self, event):
        # Отрисовка текущего изображения
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Выбираем изображение в зависимости от уровня звука
        if 0 <= self.audio_level < len(self.images):
            pixmap = self.images[self.audio_level]
            
            # Масштабируем изображение по размеру окна
            scaled_pixmap = pixmap.scaled(self.width(), self.height(), 
                                          QtCore.Qt.KeepAspectRatio, 
                                          QtCore.Qt.SmoothTransformation)
            
            # Рассчитываем позицию для центрирования
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            
            # Рисуем изображение
            painter.drawPixmap(x, y, scaled_pixmap)
    
    def mousePressEvent(self, event):
        # Запоминаем позицию для перетаскивания окна
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        # Перетаскивание окна
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def contextMenuEvent(self, event):
        # Контекстное меню при правом клике
        menu = QtWidgets.QMenu(self)
        
        # Пункт меню "Скрыть с экрана"
        hideAction = menu.addAction("Скрыть с экрана")
        
        # Пункт меню "Калибровать шумоподавление"
        calibrateAction = menu.addAction("Калибровать шумоподавление")
        
        # Пункт меню "Настройки"
        settingsAction = menu.addAction("Настройки")
        
        # Пункт меню "Перезагрузить изображения"
        reloadAction = menu.addAction("Перезагрузить изображения")
        
        # Пункт меню "Выход"
        exitAction = menu.addAction("Выход")
        
        # Показываем меню и получаем выбранное действие
        action = menu.exec_(self.mapToGlobal(event.pos()))
        
        # Обрабатываем выбранное действие
        if action == settingsAction:
            self.openSettings()
        elif action == reloadAction:
            self.loadImages()
        elif action == exitAction:
            self.closeApp()
        elif action == hideAction:
            self.toggleVisibility()
        elif action == calibrateAction:
            self.calibrateNoiseReduction()
    
    def openSettings(self):
        # Открытие диалога настроек
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def selectMicrophone(self):
        # Получаем список доступных микрофонов
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        
        mic_list = []
        
        print("Доступные микрофоны:")
        for i in range(num_devices):
            device_info = p.get_device_info_by_index(i)
            if device_info.get('maxInputChannels') > 0:
                print(f"{i}: {device_info.get('name')}")
                mic_list.append((i, device_info.get('name')))
        
        p.terminate()
        
        if not mic_list:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Микрофоны не найдены!")
            sys.exit(1)
        
        # Простой диалог выбора микрофона
        items = [f"{idx}: {name}" for idx, name in mic_list]
        item, ok = QtWidgets.QInputDialog.getItem(self, "Выбор микрофона", 
                                                 "Выберите микрофон:", items, 0, False)
        
        if ok and item:
            # Извлекаем индекс микрофона из выбранного элемента
            selected_idx = int(item.split(':')[0])
            self.selected_mic_index = selected_idx
            print(f"Выбран микрофон: {item}")
        else:
            # Если пользователь отменил выбор, используем первый микрофон
            self.selected_mic_index = mic_list[0][0]
            print(f"Используется микрофон по умолчанию: {mic_list[0][1]}")
    
    def startAudioAnalyzer(self):
        # Запуск анализатора звука в отдельном потоке
        self.audio_thread = threading.Thread(target=self.audioAnalyzer)
        self.audio_thread.daemon = True
        self.audio_thread.start()
    
    def audioAnalyzer(self):
        # Функция анализа звука
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                       channels=1,
                       rate=RATE,
                       input=True,
                       input_device_index=self.selected_mic_index,
                       frames_per_buffer=CHUNK)
        
        # Буфер для хранения истории значений громкости
        volume_history = deque(maxlen=HISTORY_SIZE)
        
        # Буфер для сбора аудио для шумоподавления
        noise_frames = []
        
        # Для буферизации аудио для шумоподавления (оптимальный размер для noisereduce)
        buffer_size = int(RATE * 0.5)  # 500 мс буфер
        audio_buffer = np.zeros(buffer_size, dtype=np.int16)
        buffer_index = 0
        
        try:
            while self.is_running:
                try:
                    data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
                    
                    # Если производится калибровка шумоподавления
                    if self.calibrating_noise and NOISE_REDUCTION_ENABLED:
                        noise_frames.append(data)
                        # После накопления достаточного количества шума создаем профиль
                        if len(noise_frames) >= int(RATE * 3 / CHUNK):  # примерно 3 секунды аудио
                            noise_profile = np.concatenate(noise_frames)
                            self.noise_profile = noise_profile
                            noise_frames = []
                    
                    # Обработка шумоподавлением, если включено
                    if NOISE_REDUCTION_ENABLED and not self.calibrating_noise:
                        # Помещаем данные в буфер
                        if buffer_index + len(data) <= buffer_size:
                            audio_buffer[buffer_index:buffer_index + len(data)] = data
                            buffer_index += len(data)
                        
                        # Когда буфер заполнен, применяем шумоподавление
                        if buffer_index >= buffer_size:
                            # Применяем шумоподавление к буферу
                            if self.noise_profile is not None:
                                # Преобразуем аудио в float для noisereduce
                                audio_float = audio_buffer.astype(np.float32) / 32768.0
                                
                                # Применяем шумоподавление
                                denoised = nr.reduce_noise(
                                    y=audio_float,
                                    sr=RATE,
                                    stationary=NOISE_STATIONARY,
                                    prop_decrease=NOISE_PROP_DECREASE,
                                    n_std_thresh_stationary=NOISE_REDUCTION_STRENGTH,
                                    n_fft=512,
                                    win_length=512,
                                    hop_length=128
                                )
                                
                                # Преобразуем обратно в int16
                                data = (denoised[-CHUNK:] * 32768.0).astype(np.int16)
                            
                            # Сбрасываем буфер, оставляя последнюю половину
                            overlap = buffer_size // 2
                            audio_buffer[:overlap] = audio_buffer[buffer_size - overlap:]
                            audio_buffer[overlap:] = 0
                            buffer_index = overlap
                    
                    # Вычисляем громкость
                    current_volume = np.abs(data).mean()
                    
                    # Добавляем текущую громкость в историю
                    volume_history.append(current_volume)
                    
                    # Вычисляем среднюю громкость на основе истории
                    if len(volume_history) > 0:
                        avg_volume = sum(volume_history) / len(volume_history)
                    else:
                        avg_volume = current_volume
                    
                    # Определяем новый уровень на основе средней громкости
                    new_level = 0
                    if avg_volume < SILENCE_THRESHOLD:
                        new_level = 0  # Тишина
                    elif avg_volume < QUIET_THRESHOLD:
                        new_level = 1  # Тихо
                    elif avg_volume < MEDIUM_THRESHOLD:
                        new_level = 2  # Средне
                    else:
                        new_level = 3  # Громко
                    
                    # Проверяем, прошло ли достаточно времени с момента последнего изменения уровня
                    current_time = time.time()
                    time_since_last_change = current_time - self.last_level_change
                    
                    # Обновляем уровень, только если он изменился и прошло достаточно времени
                    # или если уровень повысился (более оперативная реакция на повышение громкости)
                    if new_level != self.audio_level and (time_since_last_change >= MIN_STATE_DURATION or new_level > self.audio_level):
                        self.audio_level = new_level
                        self.last_level_change = current_time
                    
                    # Небольшая задержка для снижения нагрузки на CPU
                    time.sleep(0.01)
                except Exception as e:
                    print(f"Ошибка при обработке аудио: {e}")
                    time.sleep(1)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
    
    def closeApp(self):
        # Завершение работы приложения
        self.is_running = False
        QtWidgets.QApplication.quit()
    
    def closeEvent(self, event):
        # Перехватываем событие закрытия окна
        reply = QtWidgets.QMessageBox.question(self, 'Подтверждение',
            "Вы уверены, что хотите выйти?", QtWidgets.QMessageBox.Yes |
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.closeApp()
            event.accept()
        else:
            event.ignore()

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Настройки')
        self.setMinimumWidth(300)
        
        layout = QtWidgets.QVBoxLayout()
        
        # Кнопка выбора микрофона
        self.micButton = QtWidgets.QPushButton("Выбрать микрофон", self)
        self.micButton.clicked.connect(self.parent.selectMicrophone)
        layout.addWidget(self.micButton)
        
        # Группа настроек громкости
        volumeGroup = QtWidgets.QGroupBox("Пороги громкости")
        volumeLayout = QtWidgets.QVBoxLayout()
        
        # Настройка порогов громкости - SILENCE
        volumeLayout.addWidget(QtWidgets.QLabel("Порог тишины:"))
        self.silenceSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.silenceSlider.setMinimum(100)
        self.silenceSlider.setMaximum(1000)
        self.silenceSlider.setValue(SILENCE_THRESHOLD)
        self.silenceSlider.valueChanged.connect(self.updateSilenceThreshold)
        volumeLayout.addWidget(self.silenceSlider)
        self.silenceLabel = QtWidgets.QLabel(f"Текущее значение: {SILENCE_THRESHOLD}")
        volumeLayout.addWidget(self.silenceLabel)
        
        # Настройка порогов громкости - QUIET
        volumeLayout.addWidget(QtWidgets.QLabel("Порог тихой речи:"))
        self.quietSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.quietSlider.setMinimum(500)
        self.quietSlider.setMaximum(3000)
        self.quietSlider.setValue(QUIET_THRESHOLD)
        self.quietSlider.valueChanged.connect(self.updateQuietThreshold)
        volumeLayout.addWidget(self.quietSlider)
        self.quietLabel = QtWidgets.QLabel(f"Текущее значение: {QUIET_THRESHOLD}")
        volumeLayout.addWidget(self.quietLabel)
        
        # Настройка порогов громкости - MEDIUM
        volumeLayout.addWidget(QtWidgets.QLabel("Порог средней громкости:"))
        self.mediumSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.mediumSlider.setMinimum(1500)
        self.mediumSlider.setMaximum(8000)
        self.mediumSlider.setValue(MEDIUM_THRESHOLD)
        self.mediumSlider.valueChanged.connect(self.updateMediumThreshold)
        volumeLayout.addWidget(self.mediumSlider)
        self.mediumLabel = QtWidgets.QLabel(f"Текущее значение: {MEDIUM_THRESHOLD}")
        volumeLayout.addWidget(self.mediumLabel)
        
        # Настройка порогов громкости - LOUD
        volumeLayout.addWidget(QtWidgets.QLabel("Порог громкой речи:"))
        self.loudSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.loudSlider.setMinimum(3000)
        self.loudSlider.setMaximum(15000)
        self.loudSlider.setValue(LOUD_THRESHOLD)
        self.loudSlider.valueChanged.connect(self.updateLoudThreshold)
        volumeLayout.addWidget(self.loudSlider)
        self.loudLabel = QtWidgets.QLabel(f"Текущее значение: {LOUD_THRESHOLD}")
        volumeLayout.addWidget(self.loudLabel)
        
        volumeGroup.setLayout(volumeLayout)
        layout.addWidget(volumeGroup)
        
        # Группа настроек шумоподавления
        noiseGroup = QtWidgets.QGroupBox("Шумоподавление")
        noiseLayout = QtWidgets.QVBoxLayout()
        
        # Включение/выключение шумоподавления
        self.noiseEnabledCheck = QtWidgets.QCheckBox("Включить шумоподавление")
        self.noiseEnabledCheck.setChecked(NOISE_REDUCTION_ENABLED)
        self.noiseEnabledCheck.stateChanged.connect(self.updateNoiseEnabled)
        noiseLayout.addWidget(self.noiseEnabledCheck)
        
        # Кнопка калибровки шумоподавления
        self.calibrateButton = QtWidgets.QPushButton("Калибровать шумоподавление", self)
        self.calibrateButton.clicked.connect(self.parent.calibrateNoiseReduction)
        noiseLayout.addWidget(self.calibrateButton)
        
        # Тип шумоподавления
        self.stationaryCheck = QtWidgets.QCheckBox("Стационарный шум (фоновый)")
        self.stationaryCheck.setChecked(NOISE_STATIONARY)
        self.stationaryCheck.stateChanged.connect(self.updateNoiseStationary)
        noiseLayout.addWidget(self.stationaryCheck)
        
        # Настройка силы шумоподавления
        noiseLayout.addWidget(QtWidgets.QLabel("Сила шумоподавления:"))
        self.noiseStrengthSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.noiseStrengthSlider.setMinimum(0)
        self.noiseStrengthSlider.setMaximum(100)
        self.noiseStrengthSlider.setValue(int(NOISE_REDUCTION_STRENGTH * 100))
        self.noiseStrengthSlider.valueChanged.connect(self.updateNoiseStrength)
        noiseLayout.addWidget(self.noiseStrengthSlider)
        self.noiseStrengthLabel = QtWidgets.QLabel(f"Текущее значение: {NOISE_REDUCTION_STRENGTH:.2f}")
        noiseLayout.addWidget(self.noiseStrengthLabel)
        
        # Настройка пропорции уменьшения шума
        noiseLayout.addWidget(QtWidgets.QLabel("Интенсивность уменьшения:"))
        self.noisePropSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.noisePropSlider.setMinimum(50)
        self.noisePropSlider.setMaximum(100)
        self.noisePropSlider.setValue(int(NOISE_PROP_DECREASE * 100))
        self.noisePropSlider.valueChanged.connect(self.updateNoiseProp)
        noiseLayout.addWidget(self.noisePropSlider)
        self.noisePropLabel = QtWidgets.QLabel(f"Текущее значение: {NOISE_PROP_DECREASE:.2f}")
        noiseLayout.addWidget(self.noisePropLabel)
        
        noiseGroup.setLayout(noiseLayout)
        layout.addWidget(noiseGroup)
        
        # Кнопки "Сохранить" и "Отмена"
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | 
                                             QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)
        
        self.setLayout(layout)
    
    def updateSilenceThreshold(self, value):
        global SILENCE_THRESHOLD
        SILENCE_THRESHOLD = value
        self.silenceLabel.setText(f"Текущее значение: {value}")
    
    def updateQuietThreshold(self, value):
        global QUIET_THRESHOLD
        QUIET_THRESHOLD = value
        self.quietLabel.setText(f"Текущее значение: {value}")
    
    def updateMediumThreshold(self, value):
        global MEDIUM_THRESHOLD
        MEDIUM_THRESHOLD = value
        self.mediumLabel.setText(f"Текущее значение: {value}")
    
    def updateLoudThreshold(self, value):
        global LOUD_THRESHOLD
        LOUD_THRESHOLD = value
        self.loudLabel.setText(f"Текущее значение: {value}")
    
    def updateNoiseEnabled(self, state):
        global NOISE_REDUCTION_ENABLED
        NOISE_REDUCTION_ENABLED = state == QtCore.Qt.Checked
        
        # Активируем/деактивируем контролы шумоподавления
        self.calibrateButton.setEnabled(NOISE_REDUCTION_ENABLED)
        self.stationaryCheck.setEnabled(NOISE_REDUCTION_ENABLED)
        self.noiseStrengthSlider.setEnabled(NOISE_REDUCTION_ENABLED)
        self.noisePropSlider.setEnabled(NOISE_REDUCTION_ENABLED)
    
    def updateNoiseStationary(self, state):
        global NOISE_STATIONARY
        NOISE_STATIONARY = state == QtCore.Qt.Checked
    
    def updateNoiseStrength(self, value):
        global NOISE_REDUCTION_STRENGTH
        NOISE_REDUCTION_STRENGTH = value / 100.0
        self.noiseStrengthLabel.setText(f"Текущее значение: {NOISE_REDUCTION_STRENGTH:.2f}")
    
    def updateNoiseProp(self, value):
        global NOISE_PROP_DECREASE
        NOISE_PROP_DECREASE = value / 100.0
        self.noisePropLabel.setText(f"Текущее значение: {NOISE_PROP_DECREASE:.2f}")

def main():
    # Создание и запуск приложения
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Не завершать при закрытии последнего окна
    window = VTuberWindow()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 