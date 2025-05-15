import os
import time
import threading
import sys
import json
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox)
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt

class WorkerSignals(QObject):
    """スレッド間通信用のシグナル定義"""
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

class FolderMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("大村自動起動アプリ")
        self.resize(800, 600)
        
        self.folder_path = ""
        self.interval = 10  # デフォルトの監視間隔を10秒に設定
        self.excel_file_path = ""
        
        self.monitoring_thread = None
        self.signals = WorkerSignals()
        self.signals.progress.connect(self.update_progress)
        self.signals.error.connect(self.show_error)
        
        self.create_widgets()
        self.load_settings()  # 起動時に設定を読み込む
        self.check_and_start_monitoring()

    def create_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # フォルダパス入力エリア
        folder_layout = QHBoxLayout()
        folder_label = QLabel("監視するフォルダ:")
        self.folder_path_input = QLineEdit()
        folder_button = QPushButton("フォルダ選択")
        folder_button.clicked.connect(self.select_folder)
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_path_input)
        folder_layout.addWidget(folder_button)
        main_layout.addLayout(folder_layout)
        
        # 監視間隔入力エリア
        interval_layout = QHBoxLayout()
        interval_label = QLabel("監視間隔 (秒):")
        self.interval_input = QLineEdit()
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_input)
        interval_layout.addStretch(1)
        main_layout.addLayout(interval_layout)
        
        # Excelファイル入力エリア
        excel_layout = QHBoxLayout()
        excel_label = QLabel("エクセルファイル:")
        self.excel_file_input = QLineEdit()
        excel_button = QPushButton("ファイル選択")
        excel_button.clicked.connect(self.select_excel_file)
        
        excel_layout.addWidget(excel_label)
        excel_layout.addWidget(self.excel_file_input)
        excel_layout.addWidget(excel_button)
        main_layout.addLayout(excel_layout)
        
        # 実行ボタン
        self.run_button = QPushButton("実行")
        self.run_button.clicked.connect(self.start_monitoring)
        main_layout.addWidget(self.run_button, alignment=Qt.AlignCenter)
        
        # 進捗表示テキストエリア
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        main_layout.addWidget(self.progress_text)

    def select_folder(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "監視するフォルダを選択")
        if folder_selected:
            self.folder_path_input.setText(folder_selected)
            self.folder_path = folder_selected
            xlsm_files = [f for f in os.listdir(folder_selected) if f.endswith('.xlsm')]
            if len(xlsm_files) == 1:
                excel_path = os.path.join(folder_selected, xlsm_files[0])
                self.excel_file_input.setText(excel_path)
                self.excel_file_path = excel_path

    def select_excel_file(self):
        file_selected, _ = QFileDialog.getOpenFileName(
            self, "エクセルファイルを選択", "", "Excel Files (*.xlsm)")
        if file_selected:
            self.excel_file_input.setText(file_selected)
            self.excel_file_path = file_selected
    
    def start_monitoring(self):
        folder = self.folder_path_input.text()
        try:
            interval = int(self.interval_input.text())
        except ValueError:
            QMessageBox.critical(self, "エラー", "監視間隔には数値を入力してください。")
            return
            
        excel_file = self.excel_file_input.text()
        
        if not folder or not interval or not excel_file:
            QMessageBox.critical(self, "エラー", "全てのフィールドを入力してください。")
            return
        
        if not os.path.isdir(folder):
            QMessageBox.critical(self, "エラー", f"フォルダが存在しません: {folder}")
            return

        if not os.path.isfile(excel_file):
            QMessageBox.critical(self, "エラー", f"エクセルファイルが存在しません: {excel_file}")
            return
        
        self.folder_path = folder
        self.interval = interval
        self.excel_file_path = excel_file
        
        self.run_button.setEnabled(False)
        self.folder_path_input.setEnabled(False)
        self.interval_input.setEnabled(False)
        self.excel_file_input.setEnabled(False)
        
        self.progress_text.clear()
        self.update_progress("監視を開始します...")
        self.save_settings()
        
        self.monitoring_thread = threading.Thread(
            target=self.monitor_folder, 
            args=(folder, interval, excel_file)
        )
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def monitor_folder(self, folder_path, interval, excel_file):
        while True:
            try:
                print_files = [f for f in os.listdir(folder_path) if f.startswith('print_')]
                saiho_files = [f for f in os.listdir(folder_path) if f.startswith('saiho_')]
                refresh_file = os.path.exists(os.path.join(folder_path, 'refresh'))
                file_found = bool(print_files or saiho_files or refresh_file)
                
                self.signals.progress.emit("Checking...")
                
                if file_found:
                    if not os.path.exists(excel_file):
                        xlsm_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsm')]
                        if len(xlsm_files) == 1:
                            excel_file = os.path.join(folder_path, xlsm_files[0])
                            self.excel_file_path = excel_file
                            self.save_settings()

                    self.signals.progress.emit(f"Files found: {print_files + saiho_files}. Opening Excel.")
                    self.open_excel_file(excel_file)
                    time.sleep(15)  # 15秒待つ
                    
                    # Excelファイルが開いている間は、監視を一時停止
                    while self.is_excel_open(excel_file):
                        self.signals.progress.emit("Excel is open, monitoring paused.")
                        time.sleep(2)
                    
                    self.signals.progress.emit("Excel closed, resuming monitoring.")
                else:
                    self.signals.progress.emit("No files found.")
                
                time.sleep(interval)
            except Exception as e:
                self.signals.error.emit(f"Error: {str(e)}")
                break

    @pyqtSlot(str)
    def update_progress(self, message):
        self.progress_text.append(message)
    
    @pyqtSlot(str)
    def show_error(self, message):
        QMessageBox.critical(self, "エラー", message)

    def open_excel_file(self, excel_file):
        try:
            if sys.platform == "win32":
                # Windowsでは絶対パスに変換してから開く（長いパス名対応）
                abs_path = os.path.abspath(excel_file)
                # ファイルが存在するか確認
                if not os.path.exists(abs_path):
                    self.signals.error.emit(f"エクセルファイルが見つかりません: {abs_path}")
                    return
                    
                try:
                    # Windowsでファイルを開く
                    os.startfile(abs_path)
                    self.signals.progress.emit(f"エクセルファイル '{excel_file}' を開きました。")
                except Exception as win_error:
                    # もし失敗したら、代替手段を試す
                    self.signals.progress.emit(f"標準方法での起動に失敗しました。代替方法を試みます。")
                    subprocess.Popen(['start', '', abs_path], shell=True)
                    self.signals.progress.emit(f"代替方法でエクセルファイル '{excel_file}' を開きました。")
                return
            elif sys.platform == "darwin":
                subprocess.run(["open", excel_file], check=True)
                self.signals.progress.emit(f"エクセルファイル '{excel_file}' を開きました。")
                return
            else:  # Linux and others
                subprocess.run(["xdg-open", excel_file], check=True)
                self.signals.progress.emit(f"エクセルファイル '{excel_file}' を開きました。")
                return

        except Exception as e:
            self.signals.error.emit(f"エクセルファイルを開く際にエラーが発生しました: {str(e)}")

    def is_excel_open(self, excel_file):
        # ファイルのディレクトリとファイル名を取得
        directory, filename = os.path.split(excel_file)
        # 対象ファイルの拡張子を除いた基本名を取得
        base_name, _ = os.path.splitext(filename)

        # ディレクトリ内の全ファイルをループ
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            # ファイルが隠しファイルかどうかをチェック
            if os.path.isfile(item_path) and item.startswith('~$') and base_name in item:
                return True

        return False

    def get_base_path(self):
        """
        アプリケーションが実行されているディレクトリのパスを返します。
        """
        # PyInstallerで一つのファイルにビルドされた場合、実行ファイルのディレクトリを参照
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        # スクリプトが直接Pythonで実行されている場合
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def save_settings(self):
        base_path = self.get_base_path()
        settings_path = os.path.join(base_path, 'settings.json')

        # 設定を保存する関数
        settings = {
            "folder_path": self.folder_path,
            "interval": self.interval,
            "excel_file_path": self.excel_file_path,
        }
        with open(settings_path, "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        # 設定を読み込む関数
        base_path = self.get_base_path()
        settings_path = os.path.join(base_path, 'settings.json')
        try:
            with open(settings_path, "r") as f:
                settings = json.load(f)
                folder_path = settings.get("folder_path", "")
                excel_file_path = settings.get("excel_file_path", "")
                if not os.path.isdir(folder_path):
                    folder_path = ""
                if not os.path.isfile(excel_file_path):
                    excel_file_path = ""
                    
                self.folder_path = folder_path
                self.folder_path_input.setText(folder_path)
                
                interval = settings.get("interval", 10)
                self.interval = interval
                self.interval_input.setText(str(interval))
                
                self.excel_file_path = excel_file_path
                self.excel_file_input.setText(excel_file_path)
        except FileNotFoundError:
            self.folder_path = ""
            self.interval = 10
            self.excel_file_path = ""
            self.interval_input.setText("10")

    def check_and_start_monitoring(self):
        if os.path.isdir(self.folder_path) and os.path.isfile(self.excel_file_path):
            self.start_monitoring()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FolderMonitorApp()
    window.show()
    sys.exit(app.exec_())
