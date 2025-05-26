import sys
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QProgressBar, QCheckBox, QDoubleSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt, QProcess
from pathlib import Path
import json

class VideoAudioConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Audio Converter")
        self.setFixedSize(600, 480)
        self.setAcceptDrops(True)
        self.input_file = None
        self.process = None
        self.audio_streams = []
        self.subtitle_streams = []
        self.video_duration = 0
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Área para arrastrar y soltar
        self.drop_label = QLabel("Arrastra y suelta un archivo de video aquí", self)
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("border: 2px dashed gray; padding: 20px;")
        self.drop_label.setFixedHeight(100)
        layout.addWidget(self.drop_label)

        # Selección de pista de audio
        self.audio_track_layout = QHBoxLayout()
        self.audio_track_label = QLabel("Pista de audio:")
        self.audio_track_combo = QComboBox()
        self.audio_track_combo.addItem("Selecciona un archivo primero")
        self.audio_track_combo.setEnabled(False)
        self.audio_track_layout.addWidget(self.audio_track_label)
        self.audio_track_layout.addWidget(self.audio_track_combo)
        layout.addLayout(self.audio_track_layout)

        # Selección de contenedor (MKV predeterminado)
        container_layout = QHBoxLayout()
        container_label = QLabel("Contenedor de salida:")
        self.container_combo = QComboBox()
        self.container_combo.addItems(["mkv", "mp4", "avi"])
        self.container_combo.setCurrentText("mkv")
        self.container_combo.currentTextChanged.connect(self.update_codecs_based_on_container)
        container_layout.addWidget(container_label)
        container_layout.addWidget(self.container_combo)
        layout.addLayout(container_layout)

        # Selección de códec (se actualiza según contenedor)
        codec_layout = QHBoxLayout()
        codec_label = QLabel("Códec de audio:")
        self.codec_combo = QComboBox()
        self.update_codecs_based_on_container()  # Inicializa con codecs para MKV
        codec_layout.addWidget(codec_label)
        codec_layout.addWidget(self.codec_combo)
        layout.addLayout(codec_layout)

        # Selección de bitrate (128 kbps predeterminado)
        bitrate_layout = QHBoxLayout()
        bitrate_label = QLabel("Bitrate (kbps):")
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["64", "128", "160", "192", "224", "256", "320", "448", "512"])
        self.bitrate_combo.setCurrentText("128")
        bitrate_layout.addWidget(bitrate_label)
        bitrate_layout.addWidget(self.bitrate_combo)
        layout.addLayout(bitrate_layout)

        # Selección de canales (estéreo predeterminado)
        channels_layout = QHBoxLayout()
        channels_label = QLabel("Canales:")
        self.channels_combo = QComboBox()
        self.channels_combo.addItems(["1 (Mono)", "2 (Estéreo)", "4 (Cuadro)", "5.1", "6.1", "7.1"])
        self.channels_combo.setCurrentText("2 (Estéreo)")
        channels_layout.addWidget(channels_label)
        channels_layout.addWidget(self.channels_combo)
        layout.addLayout(channels_layout)

        # Aumentar volumen (en porcentaje)
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volumen (%):")
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0, 200)
        self.volume_spin.setValue(100)
        self.volume_spin.setSingleStep(1)
        self.volume_spin.setSuffix("%")
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_spin)
        layout.addLayout(volume_layout)

        # Normalización
        normalize_layout = QHBoxLayout()
        self.normalize_check = QCheckBox("Normalizar audio (loudnorm)")
        normalize_layout.addWidget(self.normalize_check)
        layout.addLayout(normalize_layout)

        # Botones de convertir y detener
        button_layout = QHBoxLayout()
        self.convert_button = QPushButton("Convertir audio", self)
        self.convert_button.setEnabled(False)
        self.convert_button.clicked.connect(self.start_conversion)
        self.stop_button = QPushButton("Detener", self)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_conversion)
        button_layout.addWidget(self.convert_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        # Barra de progreso
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

        # Estado
        self.status_label = QLabel("Esperando archivo...", self)
        self.status_label.setFixedHeight(20)
        layout.addWidget(self.status_label)

        layout.addStretch()

    def update_codecs_based_on_container(self):
        """Actualiza los codecs disponibles según el contenedor seleccionado"""
        container = self.container_combo.currentText()
        current_codec = self.codec_combo.currentText() if self.codec_combo.count() > 0 else ""
        
        self.codec_combo.clear()
        
        if container == "mkv":
            self.codec_combo.addItems(["aac", "mp3", "flac", "ogg", "wav"])
            recommended = "aac"
        elif container == "mp4":
            self.codec_combo.addItems(["aac", "mp3"])
            recommended = "aac"
        elif container == "avi":
            self.codec_combo.addItems(["mp3", "flac", "wav"])
            recommended = "mp3"
        
        # Restaurar el codec seleccionado anteriormente si sigue disponible
        if current_codec in [self.codec_combo.itemText(i) for i in range(self.codec_combo.count())]:
            self.codec_combo.setCurrentText(current_codec)
        else:
            self.codec_combo.setCurrentText(recommended)

    def show_codec_warning(self, container, codec):
        """Muestra advertencias sobre combinaciones no óptimas"""
        warnings = {
            ("mp4", "mp3"): "MP3 en MP4 no es la combinación óptima. Se recomienda usar AAC para mejor compatibilidad.",
            ("avi", "flac"): "FLAC en AVI puede tener problemas de compatibilidad con algunos reproductores.",
            ("avi", "wav"): "WAV en AVI producirá archivos muy grandes. Considera usar MP3 para mejor relación calidad/tamaño."
        }
        
        if (container, codec) in warnings:
            QMessageBox.warning(self, "Advertencia de compatibilidad", warnings[(container, codec)])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and os.path.isfile(files[0]):
            self.input_file = files[0]
            self.drop_label.setText(f"Archivo: {os.path.basename(self.input_file)}")
            self.convert_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.status_label.setText("Analizando pistas de audio y subtítulos...")
            self.progress_bar.setValue(0)

            if not os.access(self.input_file, os.R_OK):
                self.status_label.setText("Error: No se puede acceder al archivo.")
                self.audio_track_combo.clear()
                self.audio_track_combo.addItem("Error al cargar pistas")
                self.audio_track_combo.setEnabled(False)
                return

            self.probe_process = QProcess(self)
            self.probe_process.finished.connect(self.on_probe_finished)
            cmd = ["ffprobe", "-i", self.input_file, "-hide_banner", "-show_streams", "-show_format", "-print_format", "json"]
            self.probe_process.start(cmd[0], cmd[1:])

    def on_probe_finished(self):
        if self.probe_process.exitCode() == 0:
            output = self.probe_process.readAllStandardOutput().data().decode()
            try:
                probe_data = json.loads(output)
                self.audio_streams = [stream for stream in probe_data.get('streams', []) if stream['codec_type'] == 'audio']
                self.subtitle_streams = [stream for stream in probe_data.get('streams', []) if stream['codec_type'] == 'subtitle']
                self.video_duration = float(probe_data.get('format', {}).get('duration', 0))
                self.audio_track_combo.clear()
                
                if not self.audio_streams:
                    self.audio_track_combo.addItem("No se encontraron pistas de audio")
                    self.audio_track_combo.setEnabled(False)
                    self.convert_button.setEnabled(False)
                    self.status_label.setText("Error: El archivo no contiene pistas de audio.")
                else:
                    self.audio_track_combo.addItem("Todas las pistas")
                    for i in range(len(self.audio_streams)):
                        self.audio_track_combo.addItem(f"Pista {i + 1}")
                    self.audio_track_combo.setCurrentText("Todas las pistas")
                    self.audio_track_combo.setEnabled(True)
                    self.convert_button.setEnabled(True)
                    self.status_label.setText("Archivo cargado. Configura y presiona Convertir.")
            except json.JSONDecodeError:
                self.status_label.setText("Error: No se pudo parsear la información del archivo.")
                self.audio_track_combo.clear()
                self.audio_track_combo.addItem("Error al cargar pistas")
                self.audio_track_combo.setEnabled(False)
            except ValueError as e:
                self.status_label.setText(f"Error: Información inválida en el archivo ({str(e)}).")
                self.audio_track_combo.clear()
                self.audio_track_combo.addItem("Error al cargar pistas")
                self.audio_track_combo.setEnabled(False)
        else:
            error = self.probe_process.readAllStandardError().data().decode()
            self.status_label.setText(f"Error ffprobe: {error[:100].strip() or 'No se pudo analizar el archivo.'}...")
            self.audio_track_combo.clear()
            self.audio_track_combo.addItem("Error al cargar pistas")
            self.audio_track_combo.setEnabled(False)
        self.probe_process = None

    def start_conversion(self):
        if not self.input_file or not os.path.isfile(self.input_file):
            self.status_label.setText("Error: No se ha seleccionado un archivo válido.")
            return

        try:
            channels_map = {
                "1 (Mono)": 1, "2 (Estéreo)": 2, "4 (Cuadro)": 4,
                "5.1": 6, "6.1": 7, "7.1": 8
            }
            channels = channels_map[self.channels_combo.currentText()]
            codec = self.codec_combo.currentText()
            container = self.container_combo.currentText()
            bitrate = f"{self.bitrate_combo.currentText()}k"
            volume_percent = self.volume_spin.value()
            normalize = self.normalize_check.isChecked()
            audio_track = self.audio_track_combo.currentText()
        except (ValueError, KeyError):
            self.status_label.setText("Error: Configuración no válida.")
            return

        # Mostrar advertencia si la combinación no es óptima
        self.show_codec_warning(container, codec)

        output_file = str(Path(self.input_file).with_suffix(f".converted.{container}"))
        self.status_label.setText("Convirtiendo...")
        self.convert_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)

        try:
            # Configurar filtros de audio
            audio_filters = []
            if volume_percent != 100:
                audio_filters.append(f"volume={volume_percent/100}")
            if normalize:
                audio_filters.append("loudnorm")
            filter_str = ",".join(audio_filters) if audio_filters else None

            # Construir el comando ffmpeg
            cmd = ['ffmpeg', '-i', self.input_file, '-c:v', 'copy']
            
            # Mapear todos los streams
            cmd.extend(['-map', '0:v'])  # Video stream
            
            # Procesar pistas de audio
            if audio_track == "Todas las pistas":
                for i in range(len(self.audio_streams)):
                    cmd.extend([
                        f'-map', f'0:a:{i}',
                        f'-c:a:{i}', codec,
                        f'-b:a:{i}', bitrate,
                        f'-ac:{i}', str(channels)
                    ])
                    if filter_str:
                        cmd.extend([f'-af:{i}', filter_str])
            else:
                track_index = int(audio_track.split()[-1]) - 1
                for i in range(len(self.audio_streams)):
                    cmd.extend([f'-map', f'0:a:{i}'])
                    if i == track_index:
                        cmd.extend([
                            f'-c:a:{i}', codec,
                            f'-b:a:{i}', bitrate,
                            f'-ac:{i}', str(channels)
                        ])
                        if filter_str:
                            cmd.extend([f'-af:{i}', filter_str])
                    else:
                        cmd.extend([f'-c:a:{i}', 'copy'])

            # Añadir subtítulos si existen
            if self.subtitle_streams:
                cmd.extend(['-map', '0:s?', '-c:s', 'copy'])  # ? hace que sea opcional

            cmd.extend(['-y', output_file])  # -y para sobrescribir

            # Configurar el proceso
            self.process = QProcess(self)
            self.process.readyReadStandardError.connect(self.update_progress)
            self.process.finished.connect(self.conversion_finished)
            self.process.start(cmd[0], cmd[1:])

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.convert_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.progress_bar.setValue(0)

    def update_progress(self):
        if not self.process or not self.video_duration:
            return
        stderr = self.process.readAllStandardError().data().decode()
        time_match = re.search(r"time=(\d{2}):(\d{2}):(\d{2})\.\d{2}", stderr)
        if time_match:
            hours, minutes, seconds = map(int, time_match.groups())
            current_time = hours * 3600 + minutes * 60 + seconds
            progress = min(int((current_time / self.video_duration) * 100), 100)
            self.progress_bar.setValue(progress)

    def conversion_finished(self):
        if self.process and self.process.exitCode() == 0:
            self.status_label.setText(f"Conversión completada: {Path(self.input_file).with_suffix(f'.converted.{self.container_combo.currentText()}')}")
            self.progress_bar.setValue(100)
        else:
            self.status_label.setText("Error en la conversión. Verifica el archivo.")
            self.progress_bar.setValue(0)
        self.convert_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.process = None

    def stop_conversion(self):
        if self.process:
            self.process.terminate()
            self.process.waitForFinished(1000)
            if self.process.state() != QProcess.NotRunning:
                self.process.kill()
            self.status_label.setText("Conversión detenida.")
            self.progress_bar.setValue(0)
            self.convert_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.process = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoAudioConverter()
    window.show()
    sys.exit(app.exec_())