import sys
import pandas as pd
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QListWidget, QPushButton, QFileDialog, QTableWidget,
                             QTableWidgetItem, QAbstractItemView, QComboBox, QTextEdit,
                             QMessageBox, QDialog, QFormLayout, QSpinBox, QGroupBox, QDoubleSpinBox,
                             QRadioButton, QButtonGroup, QScrollArea, QProgressDialog,
                             QMenuBar, QMenu, QAction, QTabWidget, QSizePolicy) # 导入 QSizePolicy
from PyQt5.QtCore import Qt, QThread, pyqtSignal # 导入 QThread, pyqtSignal
from PyQt5.QtGui import QFont
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
import xgboost as xgb
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
from sklearn.model_selection import train_test_split
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import joblib
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.inspection import permutation_importance
import ast

class TrainingThread(QThread): # 使用 QThread 执行训练任务
    training_finished = pyqtSignal(str, object) # 信号，传递结果文本和模型
    training_error = pyqtSignal(str) # 信号，传递错误信息

    def __init__(self, parent, algorithm, algorithm_params, feature_scaling_method, X_train, X_test, y_train, y_test, features, targets):
        super().__init__(parent)
        self.algorithm = algorithm
        self.algorithm_params = algorithm_params
        self.feature_scaling_method = feature_scaling_method
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.features = features
        self.targets = targets
        self.model = None # 用于存储训练后的模型
        self.is_canceled = False

    def run(self):
        try:
            if self.algorithm == "支持向量回归 (SVR)":
                model = SVR(C=self.algorithm_params['C'], kernel=self.algorithm_params['kernel'], gamma=self.algorithm_params['gamma'])
            elif self.algorithm == "随机森林回归":
                model = RandomForestRegressor(n_estimators=self.algorithm_params['n_estimators'],
                                            max_depth=self.algorithm_params['max_depth'],
                                            random_state=42)
            elif self.algorithm == "K-近邻 (KNN)":
                model = KNeighborsRegressor(n_neighbors=self.algorithm_params['n_neighbors'],
                                            weights=self.algorithm_params['weights'],
                                            algorithm=self.algorithm_params['algorithm'])
            elif self.algorithm == "极限梯度提升 (XGBoost)":
                model = xgb.XGBRegressor(n_estimators=self.algorithm_params['n_estimators'],
                                         max_depth=self.algorithm_params['max_depth'],
                                         learning_rate=self.algorithm_params['learning_rate'],
                                         random_state=42)
            elif self.algorithm == "神经网络 (Neural Network)":
                model = MLPRegressor(hidden_layer_sizes=self.algorithm_params['hidden_layer_sizes'],
                                     activation=self.algorithm_params['activation'],
                                     solver=self.algorithm_params['solver'],
                                     alpha=self.algorithm_params['alpha'],
                                     max_iter=self.algorithm_params['max_iter'],
                                     random_state=42)
            else:
                raise ValueError("Unknown algorithm selected.")

            model.fit(self.X_train, self.y_train)
            predictions = model.predict(self.X_test)

            metrics = {
                "MAE": mean_absolute_error(self.y_test, predictions),
                "MSE": mean_squared_error(self.y_test, predictions),
                "RMSE": np.sqrt(mean_squared_error(self.y_test, predictions)),
                "R²": r2_score(self.y_test, predictions),
                "MAPE": mean_absolute_percentage_error(self.y_test, predictions)
            }

            text_results_parts = []
            for target in self.targets:
                text_results_parts.append(f"\n**目标变量: {target}**\n")
                for name, value in metrics.items():
                    text_results_parts.append(f"{name}: {value:.4f}\n")

            text_results = "".join(text_results_parts)
            end_time = datetime.datetime.now()
            time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
            text_results += f"\n训练完成时间: {time_str}\n"

            self.model = model # 保存训练好的模型
            self.training_finished.emit(text_results, model) # 发射完成信号，带结果和模型

        except Exception as e:
            error_msg = f"模型训练时发生错误：{str(e)}"
            self.training_error.emit(error_msg) # 发射错误信号

    def stop_training(self):
        self.is_canceled = True # 设置取消标志，可以在训练循环中检查 (目前代码中训练循环已在 sklearn 内部，这里主要用于外部取消信号)

class MLClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = None
        self.rf_params = {'n_estimators': 100, 'max_depth': None}
        self.svr_params = {'C': 1.0, 'kernel': 'rbf', 'gamma': 'scale'}
        self.knn_params = {'n_neighbors': 5, 'weights': 'uniform', 'algorithm': 'auto'}
        self.xgb_params = {'n_estimators': 100, 'max_depth': 3, 'learning_rate': 0.1}
        self.nn_params = {'hidden_layer_sizes': (100,), 'activation': 'relu', 'solver': 'adam', 'alpha': 0.0001, 'max_iter': 200}
        self.algorithm_params = {
            "支持向量回归 (SVR)": self.svr_params,
            "随机森林回归": self.rf_params,
            "K-近邻 (KNN)": self.knn_params,
            "极限梯度提升 (XGBoost)": self.xgb_params,
            "神经网络 (Neural Network)": self.nn_params,
        }
        self.missing_value_handling = 'mean'
        self.feature_scaling_method = None
        self.model = None
        self.feature_names = []
        self.target_names = []
        self.algorithm_name = ""
        self.current_algorithm = ""
        self.training_thread = None # 用于管理训练线程
        self.initUI()
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QListWidget { background-color: white; border: 1px solid #cccccc; }
            QTextEdit { background-color: white; border: 1px solid #cccccc; }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover { background-color: #006cbd; }
            QComboBox { background-color: white; border: 1px solid #cccccc; }
        """)

    def initUI(self):
        self.setWindowTitle('机器学习&纳米材料分析平台v2.0.1')
        self.setGeometry(100, 100, 1280, 800)

        self.initMenuBar()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)

        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(10, 10, 10, 10)

        # 文件操作区域
        file_btn = QPushButton('打开CSV文件', self)
        file_btn.clicked.connect(self.load_csv)
        file_btn.setToolTip("点击选择并加载CSV数据文件")
        control_layout.addWidget(file_btn)

        # 变量选择
        control_layout.addWidget(QLabel("特征变量（多选）："))
        self.feature_list = QListWidget()
        self.feature_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.feature_list.setToolTip("选择用于模型训练的特征变量 (可多选)")
        control_layout.addWidget(self.feature_list)
        feature_select_layout = QHBoxLayout()
        feature_select_all_btn = QPushButton('全选', self)
        feature_select_all_btn.clicked.connect(lambda: self.select_all_items(self.feature_list))
        feature_select_all_btn.setToolTip("选择所有特征变量")
        feature_select_layout.addWidget(feature_select_all_btn)
        feature_deselect_all_btn = QPushButton('取消全选', self)
        feature_deselect_all_btn.clicked.connect(lambda: self.deselect_all_items(self.feature_list))
        feature_deselect_all_btn.setToolTip("取消选择所有特征变量")
        feature_select_layout.addWidget(feature_deselect_all_btn)
        control_layout.addLayout(feature_select_layout)

        control_layout.addWidget(QLabel("目标变量（可多选）："))
        self.target_list = QListWidget()
        self.target_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.target_list.setToolTip("选择模型要预测的目标变量 (可多选)")
        control_layout.addWidget(self.target_list)
        target_select_layout = QHBoxLayout()
        target_select_all_btn = QPushButton('全选', self)
        target_select_all_btn.clicked.connect(lambda: self.select_all_items(self.target_list))
        target_select_all_btn.setToolTip("选择所有目标变量")
        target_select_layout.addWidget(target_select_all_btn)
        target_deselect_all_btn = QPushButton('取消全选', self)
        target_deselect_all_btn.clicked.connect(lambda: self.deselect_all_items(self.target_list))
        target_deselect_all_btn.setToolTip("取消选择所有目标变量")
        target_select_layout.addWidget(target_deselect_all_btn)
        control_layout.addLayout(target_select_layout)

        # 特征缩放选择
        control_layout.addWidget(QLabel("特征缩放："))
        self.scaling_combo = QComboBox()
        self.scaling_combo.addItems(["无", "标准化 (StandardScaler)", "最小-最大缩放 (MinMaxScaler)"])
        self.scaling_combo.setToolTip("选择特征缩放方法，用于预处理特征变量")
        control_layout.addWidget(self.scaling_combo)
        self.scaling_combo.currentIndexChanged.connect(self.update_feature_scaling_method)

        # 算法选择
        control_layout.addWidget(QLabel("选择算法："))
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["支持向量回归 (SVR)", "随机森林回归", "K-近邻 (KNN)", "极限梯度提升 (XGBoost)", "神经网络 (Neural Network)"])
        self.algorithm_combo.setToolTip("选择用于模型训练的机器学习算法")
        control_layout.addWidget(self.algorithm_combo)

        # 参数设置按钮
        self.params_btn = QPushButton('参数设置', self)
        self.params_btn.clicked.connect(self.open_generic_params_dialog)
        self.params_btn.setEnabled(False)
        self.params_btn.setToolTip("设置当前选择算法的参数")
        control_layout.addWidget(self.params_btn)

        # 训练按钮
        train_btn = QPushButton('开始训练', self)
        train_btn.clicked.connect(self.start_training_process) # 修改为 start_training_process
        train_btn.setToolTip("根据选择的特征变量、目标变量和算法开始模型训练")
        control_layout.addWidget(train_btn)
        self.train_btn = train_btn # 保存 train_btn 的引用

        # 结果展示
        control_layout.addWidget(QLabel("训练结果："))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # 结果框可以扩展
        self.result_text.setToolTip("显示模型训练的评估指标")
        control_layout.addWidget(self.result_text)

        data_panel = QWidget()
        data_layout = QVBoxLayout(data_panel)

        # 创建 QTabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # tab widget 可以扩展

        # 数据预览子页面
        self.table_tab = QWidget()
        self.table_tab_layout = QVBoxLayout(self.table_tab)
        table_area_label = QLabel("")
        self.table_tab_layout.addWidget(table_area_label)
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # table widget 可以扩展
        self.table.setToolTip("表格区域")
        self.table_tab_layout.addWidget(self.table)
        self.tab_widget.addTab(self.table_tab, "数据预览")

        # 图像展示子页面
        self.chart_tab = QWidget()
        self.chart_tab_layout = QVBoxLayout(self.chart_tab)
        chart_area_label = QLabel("")
        self.chart_tab_layout.addWidget(chart_area_label)
        self.chart_scroll_area = QScrollArea()
        self.chart_scroll_area.setWidgetResizable(True)
        self.chart_scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # scroll area 可以扩展
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setToolTip("图像区域")
        self.chart_scroll_area.setWidget(self.canvas)
        self.chart_tab_layout.addWidget(self.chart_scroll_area)

        self.chart_layout_vertical = QVBoxLayout()
        self.canvas_widget = QWidget()
        self.canvas_widget.setLayout(self.chart_layout_vertical)
        self.chart_scroll_area.setWidget(self.canvas_widget)

        self.tab_widget.addTab(self.chart_tab, "图像展示")

        data_layout.addWidget(self.tab_widget)

        main_layout.addWidget(control_panel, stretch=1)
        main_layout.addWidget(data_panel, stretch=3)

        self.statusBar().showMessage('就绪')
        self.algorithm_combo.currentIndexChanged.connect(self.update_algorithm_params_button)

    def initMenuBar(self):
        """初始化菜单栏，添加文件操作菜单"""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("文件")

        load_action = QAction("加载CSV文件", self)
        load_action.triggered.connect(self.load_csv)
        file_menu.addAction(load_action)

        save_model_action = QAction("保存模型", self)
        save_model_action.triggered.connect(self.save_model_dialog)
        save_model_action.setEnabled(False)
        self.save_model_action = save_model_action
        file_menu.addAction(save_model_action)

        load_model_action = QAction("加载模型", self)
        load_model_action.triggered.connect(self.load_model_dialog)
        file_menu.addAction(load_model_action)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "打开CSV文件", "", "CSV文件 (*.csv)")
        if path:
            self.statusBar().showMessage(f"加载文件: {path}...", 3000)
            try:
                self.df = pd.read_csv(path)
                if self.df.isnull().any().any():
                    missing_dialog = MissingValueDialog(self)
                    if missing_dialog.exec_() == QDialog.Accepted:
                        self.missing_value_handling = missing_dialog.get_selected_option()
                        if self.missing_value_handling == 'mean':
                            self.df.fillna(self.df.mean(numeric_only=True), inplace=True)
                        elif self.missing_value_handling == 'median':
                            self.df.fillna(self.df.median(numeric_only=True), inplace=True)
                        elif self.missing_value_handling == 'remove_rows':
                            self.df.dropna(inplace=True)

                self.update_table()
                self.update_lists()
                self.statusBar().showMessage(f"文件加载成功：{path}", 5000)
            except FileNotFoundError:
                QMessageBox.critical(self, "文件未找到", f"找不到文件：{path}")
                self.statusBar().showMessage("文件加载失败：文件未找到", 5000)
            except pd.errors.EmptyDataError:
                QMessageBox.warning(self, "文件内容为空", "CSV 文件内容为空，请选择包含数据的 CSV 文件。")
                self.statusBar().showMessage("文件加载失败：CSV 文件内容为空", 5000)
            except UnicodeDecodeError: # 添加 UnicodeDecodeError 处理
                QMessageBox.critical(self, "文件编码错误", "无法以UTF-8解码文件，请尝试其他CSV文件或检查文件编码。")
                self.statusBar().showMessage("文件加载失败：文件编码错误", 5000)
            except pd.errors.ParserError as e: # 更具体的 Pandas ParserError
                QMessageBox.critical(self, "CSV解析错误", f"CSV 文件解析错误：{str(e)}")
                self.statusBar().showMessage(f"文件加载失败：CSV解析错误", 5000)
            except Exception as e:
                QMessageBox.critical(self, "加载文件错误", f"加载 CSV 文件时发生未知错误：{str(e)}")
                self.statusBar().showMessage(f"文件加载错误：未知错误：{str(e)}", 5000)

    def update_feature_scaling_method(self, index):
        """更新特征缩放方法"""
        method_name = self.scaling_combo.itemText(index)
        if method_name == "标准化 (StandardScaler)":
            self.feature_scaling_method = StandardScaler()
        elif method_name == "最小-最大缩放 (MinMaxScaler)":
            self.feature_scaling_method = MinMaxScaler()
        else: # "无" 或其他情况
            self.feature_scaling_method = None

    def update_table(self):
        if self.df is not None:
            self.table.setRowCount(self.df.shape[0])
            self.table.setColumnCount(self.df.shape[1])
            self.table.setHorizontalHeaderLabels(self.df.columns)

            for row in range(self.df.shape[0]):
                for col in range(self.df.shape[1]):
                    item = QTableWidgetItem(str(self.df.iat[row, col]))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)
        else:
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.table.setHorizontalHeaderLabels([])

    def update_lists(self):
        self.feature_list.clear()
        self.target_list.clear()
        if self.df is not None and not self.df.empty:
            for col in self.df.columns:
                self.feature_list.addItem(col)
                self.target_list.addItem(col)
        else:
            pass

    def select_all_items(self, list_widget, single_select=False):
        if single_select:
             if list_widget.count() > 0:
                item = list_widget.item(0)
                item.setSelected(True)
                list_widget.setCurrentItem(item)
        else:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item.setSelected(True)

    def deselect_all_items(self, list_widget):
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setSelected(False)

    def update_algorithm_params_button(self, index):
        algorithm_name = self.algorithm_combo.itemText(index)
        self.current_algorithm = algorithm_name
        if algorithm_name == "随机森林回归":
            self.params_btn.setText("随机森林参数设置")
            self.params_btn.setEnabled(True)
            self.params_btn.clicked.disconnect()
            self.params_btn.clicked.connect(self.open_rf_params_dialog)
            self.params_btn.setToolTip("设置随机森林回归算法的参数")
        elif algorithm_name == "支持向量回归 (SVR)":
            self.params_btn.setText("SVR参数设置")
            self.params_btn.setEnabled(True)
            self.params_btn.clicked.disconnect()
            self.params_btn.clicked.connect(self.open_svr_params_dialog)
            self.params_btn.setToolTip("设置支持向量回归 (SVR) 算法的参数")
        elif algorithm_name == "K-近邻 (KNN)":
            self.params_btn.setText("KNN参数设置")
            self.params_btn.setEnabled(True)
            self.params_btn.clicked.disconnect()
            self.params_btn.clicked.connect(self.open_knn_params_dialog)
            self.params_btn.setToolTip("设置 K-近邻 (KNN) 算法的参数")
        elif algorithm_name == "极限梯度提升 (XGBoost)":
            self.params_btn.setText("XGBoost参数设置")
            self.params_btn.setEnabled(True)
            self.params_btn.clicked.disconnect()
            self.params_btn.clicked.connect(self.open_xgboost_params_dialog)
            self.params_btn.setToolTip("设置极限梯度提升 (XGBoost) 算法的参数")
        elif algorithm_name == "神经网络 (Neural Network)":
            self.params_btn.setText("神经网络参数设置")
            self.params_btn.setEnabled(True)
            self.params_btn.clicked.disconnect()
            self.params_btn.clicked.connect(self.open_nn_params_dialog)
            self.params_btn.setToolTip("设置神经网络 (Neural Network) 算法的参数")
        else:
            self.params_btn.setText("参数设置")
            self.params_btn.setEnabled(False)
            self.params_btn.clicked.disconnect()
            self.params_btn.clicked.connect(self.open_generic_params_dialog)
            self.params_btn.setToolTip("当前选择的算法没有可设置的参数")

    def open_rf_params_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("随机森林参数设置")
        form_layout = QFormLayout()

        self.n_estimators_spinbox = QSpinBox()
        self.n_estimators_spinbox.setRange(1, 1000)
        self.n_estimators_spinbox.setValue(self.rf_params['n_estimators'])
        form_layout.addRow("n_estimators (树的数量):", self.n_estimators_spinbox)

        self.max_depth_spinbox = QSpinBox()
        self.max_depth_spinbox.setRange(1, 100)
        self.max_depth_spinbox.setSpecialValueText("None")
        self.max_depth_spinbox.setToolTip("设置随机森林的最大深度，None 表示不限制深度")
        if self.rf_params['max_depth'] is None:
            self.max_depth_spinbox.setValue(0)
        else:
            self.max_depth_spinbox.setValue(self.rf_params['max_depth'])
        form_layout.addRow("max_depth (最大深度):", self.max_depth_spinbox)

        dialog_buttons = QHBoxLayout()
        ok_button = QPushButton("确定", dialog)
        ok_button.clicked.connect(lambda: self.set_rf_params(dialog))
        dialog_buttons.addWidget(ok_button)
        cancel_button = QPushButton("取消", dialog)
        cancel_button.clicked.connect(dialog.reject)
        dialog_buttons.addWidget(cancel_button)

        main_dialog_layout = QVBoxLayout()
        main_dialog_layout.addLayout(form_layout)
        main_dialog_layout.addLayout(dialog_buttons)
        dialog.setLayout(main_dialog_layout)
        dialog.exec_()

    def open_svr_params_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("支持向量回归 (SVR) 参数设置")
        form_layout = QFormLayout()

        self.svr_c_doublespinbox = QDoubleSpinBox()
        self.svr_c_doublespinbox.setRange(0.01, 1000.0)
        self.svr_c_doublespinbox.setSingleStep(0.1)
        self.svr_c_doublespinbox.setValue(self.svr_params['C'])
        form_layout.addRow("C (正则化参数):", self.svr_c_doublespinbox)
        self.svr_c_doublespinbox.setToolTip("C 值越大，正则化越弱") # 添加 Tooltip

        self.svr_kernel_combo = QComboBox()
        self.svr_kernel_combo.addItems(['linear', 'rbf', 'poly', 'sigmoid'])
        self.svr_kernel_combo.setCurrentText(self.svr_params['kernel'])
        form_layout.addRow("kernel (核函数类型):", self.svr_kernel_combo)
        self.svr_kernel_combo.setToolTip("选择 SVR 使用的核函数") # 添加 Tooltip

        self.svr_gamma_combo = QComboBox()
        self.svr_gamma_combo.addItems(['scale', 'auto', '数值'])
        self.svr_gamma_combo.setCurrentText(self.svr_params['gamma'])
        form_layout.addRow("gamma (核系数):", self.svr_gamma_combo)
        self.svr_gamma_combo.setToolTip("核函数系数，'scale'/'auto' 会自动计算") # 添加 Tooltip
        self.svr_gamma_spinbox = QDoubleSpinBox()
        self.svr_gamma_spinbox.setRange(0.0001, 10.0)
        self.svr_gamma_spinbox.setSingleStep(0.1)
        self.svr_gamma_spinbox.setValue(1.0)
        self.svr_gamma_spinbox.setVisible(self.svr_gamma_combo.currentText() == '数值')
        self.svr_gamma_combo.currentIndexChanged.connect(self.toggle_gamma_spinbox)
        form_layout.addRow("gamma 数值:", self.svr_gamma_spinbox)
        self.svr_gamma_spinbox.setToolTip("当 gamma 选择 '数值' 时，设置具体的数值") # 添加 Tooltip

        dialog_buttons = QHBoxLayout()
        ok_button = QPushButton("确定", dialog)
        ok_button.clicked.connect(lambda: self.set_svr_params(dialog))
        dialog_buttons.addWidget(ok_button)
        cancel_button = QPushButton("取消", dialog)
        cancel_button.clicked.connect(dialog.reject)
        dialog_buttons.addWidget(cancel_button)

        main_dialog_layout = QVBoxLayout()
        main_dialog_layout.addLayout(form_layout)
        main_dialog_layout.addLayout(dialog_buttons)
        dialog.setLayout(main_dialog_layout)
        dialog.exec_()

    def open_knn_params_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("K-近邻 (KNN) 参数设置")
        form_layout = QFormLayout()

        self.knn_n_neighbors_spinbox = QSpinBox()
        self.knn_n_neighbors_spinbox.setRange(1, 50)
        self.knn_n_neighbors_spinbox.setValue(self.knn_params['n_neighbors'])
        form_layout.addRow("n_neighbors (邻居数量):", self.knn_n_neighbors_spinbox)
        self.knn_n_neighbors_spinbox.setToolTip("KNN 算法中考虑的邻居数量") # 添加 Tooltip

        self.knn_weights_combo = QComboBox()
        self.knn_weights_combo.addItems(['uniform', 'distance'])
        self.knn_weights_combo.setCurrentText(self.knn_params['weights'])
        form_layout.addRow("weights (权重计算):", self.knn_weights_combo)
        self.knn_weights_combo.setToolTip("'uniform'：所有邻居权重相同，'distance'：权重与距离成反比") # 添加 Tooltip

        self.knn_algorithm_combo = QComboBox()
        self.knn_algorithm_combo.addItems(['auto', 'ball_tree', 'kd_tree', 'brute'])
        self.knn_algorithm_combo.setCurrentText(self.knn_params['algorithm'])
        form_layout.addRow("algorithm (搜索算法):", self.knn_algorithm_combo)
        self.knn_algorithm_combo.setToolTip("KNN 算法使用的搜索近邻算法") # 添加 Tooltip

        dialog_buttons = QHBoxLayout()
        ok_button = QPushButton("确定", dialog)
        ok_button.clicked.connect(lambda: self.set_knn_params(dialog))
        dialog_buttons.addWidget(ok_button)
        cancel_button = QPushButton("取消", dialog)
        cancel_button.clicked.connect(dialog.reject)
        dialog_buttons.addWidget(cancel_button)

        main_dialog_layout = QVBoxLayout()
        main_dialog_layout.addLayout(form_layout)
        main_dialog_layout.addLayout(dialog_buttons)
        dialog.setLayout(main_dialog_layout)
        dialog.exec_()

    def open_xgboost_params_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("极限梯度提升 (XGBoost) 参数设置")
        form_layout = QFormLayout()

        self.xgb_n_estimators_spinbox = QSpinBox()
        self.xgb_n_estimators_spinbox.setRange(10, 1000)
        self.xgb_n_estimators_spinbox.setValue(self.xgb_params['n_estimators'])
        form_layout.addRow("n_estimators (树的数量):", self.xgb_n_estimators_spinbox)
        self.xgb_n_estimators_spinbox.setToolTip("Boosting 过程中使用的树的数量") # 添加 Tooltip

        self.xgb_max_depth_spinbox = QSpinBox()
        self.xgb_max_depth_spinbox.setRange(1, 20)
        self.xgb_max_depth_spinbox.setValue(self.xgb_params['max_depth'])
        form_layout.addRow("max_depth (最大深度):", self.xgb_max_depth_spinbox)
        self.xgb_max_depth_spinbox.setToolTip("每棵树的最大深度，控制模型复杂度") # 添加 Tooltip

        self.xgb_learning_rate_doublespinbox = QDoubleSpinBox()
        self.xgb_learning_rate_doublespinbox.setRange(0.001, 1.0)
        self.xgb_learning_rate_doublespinbox.setSingleStep(0.01)
        self.xgb_learning_rate_doublespinbox.setValue(self.xgb_params['learning_rate'])
        form_layout.addRow("learning_rate (学习率):", self.xgb_learning_rate_doublespinbox)
        self.xgb_learning_rate_doublespinbox.setToolTip("控制每次 Boosting 迭代的步长，较小的值更保守") # 添加 Tooltip

        dialog_buttons = QHBoxLayout()
        ok_button = QPushButton("确定", dialog)
        ok_button.clicked.connect(lambda: self.set_xgb_params(dialog))
        dialog_buttons.addWidget(ok_button)
        cancel_button = QPushButton("取消", dialog)
        cancel_button.clicked.connect(dialog.reject)
        dialog_buttons.addWidget(cancel_button)

        main_dialog_layout = QVBoxLayout()
        main_dialog_layout.addLayout(form_layout)
        main_dialog_layout.addLayout(dialog_buttons)
        dialog.setLayout(main_dialog_layout)
        dialog.exec_()

    def open_nn_params_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("神经网络 (Neural Network) 参数设置")
        form_layout = QFormLayout()

        self.nn_hidden_layers_textedit = QTextEdit()
        self.nn_hidden_layers_textedit.setPlainText(str(self.nn_params['hidden_layer_sizes']))
        self.nn_hidden_layers_textedit.setToolTip("输入隐藏层大小，例如 (100,), (100, 50, 25)，使用逗号分隔") # 修改 Tooltip
        form_layout.addRow("hidden_layer_sizes (隐藏层大小):", self.nn_hidden_layers_textedit)

        self.nn_activation_combo = QComboBox()
        self.nn_activation_combo.addItems(['relu', 'logistic', 'tanh', 'identity'])
        self.nn_activation_combo.setCurrentText(self.nn_params['activation'])
        form_layout.addRow("activation (激活函数):", self.nn_activation_combo)
        self.nn_activation_combo.setToolTip("隐藏层使用的激活函数") # 添加 Tooltip

        self.nn_solver_combo = QComboBox()
        self.nn_solver_combo.addItems(['adam', 'lbfgs', 'sgd'])
        self.nn_solver_combo.setCurrentText(self.nn_params['solver'])
        form_layout.addRow("solver (优化器):", self.nn_solver_combo)
        self.nn_solver_combo.setToolTip("用于权重优化的求解器") # 添加 Tooltip

        self.nn_alpha_doublespinbox = QDoubleSpinBox()
        self.nn_alpha_doublespinbox.setRange(0.00001, 1.0)
        self.nn_alpha_doublespinbox.setSingleStep(0.0001)
        self.nn_alpha_doublespinbox.setValue(self.nn_params['alpha'])
        form_layout.addRow("alpha (L2 正则化系数):", self.nn_alpha_doublespinbox)
        self.nn_alpha_doublespinbox.setToolTip("L2 正则化项的参数，用于防止过拟合") # 添加 Tooltip

        self.nn_max_iter_spinbox = QSpinBox()
        self.nn_max_iter_spinbox.setRange(100, 1000)
        self.nn_max_iter_spinbox.setValue(self.nn_params['max_iter'])
        form_layout.addRow("max_iter (最大迭代次数):", self.nn_max_iter_spinbox)
        self.nn_max_iter_spinbox.setToolTip("求解器尝试收敛的最大迭代次数") # 添加 Tooltip

        dialog_buttons = QHBoxLayout()
        ok_button = QPushButton("确定", dialog)
        ok_button.clicked.connect(lambda: self.set_nn_params(dialog))
        dialog_buttons.addWidget(ok_button)
        cancel_button = QPushButton("取消", dialog)
        cancel_button.clicked.connect(dialog.reject)
        dialog_buttons.addWidget(cancel_button)

        main_dialog_layout = QVBoxLayout()
        main_dialog_layout.addLayout(form_layout)
        main_dialog_layout.addLayout(dialog_buttons)
        dialog.setLayout(main_dialog_layout)
        dialog.exec_()

    def open_generic_params_dialog(self):
        QMessageBox.information(self, "参数设置", f"当前选择的算法 ({self.current_algorithm}) 使用默认参数，或者暂无参数可设置。")

    def toggle_gamma_spinbox(self, index):
        """gamma ComboBox 切换时，控制数值 SpinBox 的显示"""
        if self.svr_gamma_combo.itemText(index) == '数值':
            self.svr_gamma_spinbox.setVisible(True)
        else:
            self.svr_gamma_spinbox.setVisible(False)

    def set_rf_params(self, dialog):
        self.rf_params['n_estimators'] = self.n_estimators_spinbox.value()
        max_depth_value = self.max_depth_spinbox.value()
        self.rf_params['max_depth'] = max_depth_value if max_depth_value == 0 else None
        dialog.accept()

    def set_svr_params(self, dialog):
        self.svr_params['C'] = self.svr_c_doublespinbox.value()
        self.svr_params['kernel'] = self.svr_kernel_combo.currentText()
        gamma_text = self.svr_gamma_combo.currentText()
        if gamma_text == '数值':
            self.svr_params['gamma'] = self.svr_gamma_spinbox.value()
        else:
            self.svr_params['gamma'] = gamma_text
        dialog.accept()

    def set_knn_params(self, dialog):
        self.knn_params['n_neighbors'] = self.knn_n_neighbors_spinbox.value()
        self.knn_params['weights'] = self.knn_weights_combo.currentText()
        self.knn_params['algorithm'] = self.knn_algorithm_combo.currentText()
        dialog.accept()

    def set_xgboost_params(self, dialog):
        self.xgb_params['n_estimators'] = self.xgb_n_estimators_spinbox.value()
        self.xgb_params['max_depth'] = self.xgb_max_depth_spinbox.value()
        self.xgb_params['learning_rate'] = self.xgb_learning_rate_doublespinbox.value()
        dialog.accept()

    def set_nn_params(self, dialog):
        hidden_layer_sizes_str = self.nn_hidden_layers_textedit.toPlainText()
        try:
            self.nn_params['hidden_layer_sizes'] = ast.literal_eval(hidden_layer_sizes_str)
            if not isinstance(self.nn_params['hidden_layer_sizes'], tuple):
                QMessageBox.warning(self, "参数错误", "隐藏层大小必须是元组形式，例如 (100,) 或 (100, 50).")
                return
        except (ValueError, SyntaxError):
            QMessageBox.warning(self, "参数错误", "隐藏层大小格式错误，请输入例如 (100,) 或 (100, 50, 25).")
            return

        self.nn_params['activation'] = self.nn_activation_combo.currentText()
        self.nn_params['solver'] = self.nn_solver_combo.currentText()
        self.nn_params['alpha'] = self.nn_alpha_doublespinbox.value()
        self.nn_params['max_iter'] = self.nn_max_iter_spinbox.value()
        dialog.accept()

    def start_training_process(self): # 新的开始训练方法
        if self.df is None:
            QMessageBox.warning(self, "数据未加载", "请先加载 CSV 数据文件。")
            self.statusBar().showMessage("请先加载数据文件", 5000)
            return

        features = [item.text() for item in self.feature_list.selectedItems()]
        targets = [item.text() for item in self.target_list.selectedItems()]

        if not features:
            QMessageBox.warning(self, "特征变量未选择", "请选择至少一个特征变量。")
            self.statusBar().showMessage("请选择至少一个特征变量", 5000)
            return
        if not targets:
            QMessageBox.warning(self, "目标变量未选择", "请选择至少一个目标变量。")
            self.statusBar().showMessage("请选择至少一个目标变量", 5000)
            return
        if set(features).intersection(targets): # 检查特征和目标变量是否重叠
            QMessageBox.warning(self, "变量选择错误", "特征变量和目标变量不能包含相同的列。")
            self.statusBar().showMessage("特征变量和目标变量选择错误", 5000)
            return

        self.feature_names = features
        self.target_names = targets
        self.algorithm_name = self.algorithm_combo.currentText()

        X = self.df[features].copy()

        # 数据类型检查 (提前进行)
        for col in features:
            if not pd.api.types.is_numeric_dtype(X[col]):
                QMessageBox.warning(self, "数据类型错误", f"特征变量 '{col}' 必须为数值类型。")
                self.statusBar().showMessage("特征变量必须为数值类型", 5000)
                return
        for target in targets:
            if target not in self.df.columns or not pd.api.types.is_numeric_dtype(self.df[target]):
                QMessageBox.warning(self, "数据类型错误", f"目标变量 '{target}' 必须为数值类型。")
                self.statusBar().showMessage("目标变量必须为数值类型", 5000)
                return

        # 应用特征缩放 (在线程外完成，因为 fit_transform 可能是快速的)
        if self.feature_scaling_method:
            self.statusBar().showMessage("正在进行特征缩放...", 3000)
            try:
                X = self.feature_scaling_method.fit_transform(X)
                X = pd.DataFrame(X, columns=features, index=self.df.index)
                self.statusBar().showMessage("特征缩放完成", 3000)
            except Exception as scale_err:
                QMessageBox.critical(self, "特征缩放错误", f"特征缩放失败：{str(scale_err)}")
                self.statusBar().showMessage("特征缩放错误", 5000)
                return

        Y = self.df[targets].copy() # 准备目标变量数据

        X_train, X_test, y_train_all, y_test_all = train_test_split(X, Y, test_size=0.2, random_state=42) # 一次性分割所有目标变量

        self.train_btn.setEnabled(False) # 训练开始时禁用训练按钮
        self.params_btn.setEnabled(False) # 禁用参数设置按钮
        self.save_model_action.setEnabled(False) # 禁用保存模型按钮
        self.statusBar().showMessage("模型训练中...", 0) # 状态栏显示 "模型训练中..."，持续显示直到完成

        self.progress_dialog = QProgressDialog("模型训练中...", "取消训练", 0, len(targets), self) # 进度条最大值设置为目标变量数量
        self.progress_dialog.setWindowTitle("模型训练")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setValue(0)
        self.progress_dialog.canceled.connect(self.cancel_training) # 连接取消信号
        self.progress_dialog.show()

        self.clear_chart_layout() # 清空之前的图表
        self.result_text.clear() # 清空结果文本框

        self.training_thread = TrainingThread( # 创建训练线程
            self,
            self.algorithm_name,
            self.algorithm_params[self.algorithm_name], # 传递算法参数
            self.feature_scaling_method,
            X_train, X_test, y_train_all, y_test_all[targets[0]], #  传递第一个目标变量的训练和测试集，因为 TrainingThread 目前只处理单个目标变量
            features, targets
        )
        self.training_thread.training_finished.connect(self.on_training_finished) # 连接完成信号
        self.training_thread.training_error.connect(self.on_training_error) # 连接错误信号
        self.training_thread.start() # 启动线程


    def cancel_training(self):
        if self.training_thread and self.training_thread.isRunning():
            self.training_thread.stop_training() # 调用线程的停止方法
            # self.training_thread.wait() # 等待线程结束 (可选，如果需要立即停止)
            self.statusBar().showMessage("模型训练已取消", 5000)
        if self.progress_dialog:
            self.progress_dialog.cancel() # 关闭进度条
            self.progress_dialog.close()

        self.train_btn.setEnabled(True) # 重新启用训练按钮
        self.params_btn.setEnabled(True) # 重新启用参数设置按钮
        self.save_model_action.setEnabled(False) # 保持禁用保存模型按钮 (因为训练被取消)

    def on_training_finished(self, text_results, model): # 训练完成槽函数
        self.progress_dialog.setValue(len(self.target_names)) # 进度条设置为满
        self.progress_dialog.close()
        self.show_results(text_results) # 显示结果文本
        self.statusBar().showMessage("模型训练完成并显示结果", 5000)
        self.save_model_action.setEnabled(True) # 训练完成后启用保存模型按钮
        self.model = model # 保存训练好的模型
        self.train_btn.setEnabled(True) # 重新启用训练按钮
        self.params_btn.setEnabled(True) # 重新启用参数设置按钮

        # 计算特征重要性并绘图 (在主线程中进行 UI 操作)
        importances = {}
        if hasattr(model, "feature_importances_"):
            importances = dict(zip(self.feature_names, model.feature_importances_))
        else:
            result = permutation_importance(model, self.training_thread.X_test, self.training_thread.y_test, n_repeats=10, random_state=42, n_jobs=-1)
            importances = dict(zip(self.feature_names, result.importances_mean))
        self.plot_importance(importances, self.target_names[0]) # 假设只处理第一个目标变量的特征重要性，需要根据实际需求调整

    def on_training_error(self, error_msg): # 训练错误槽函数
        self.progress_dialog.close()
        QMessageBox.critical(self, "训练模型错误", error_msg)
        self.statusBar().showMessage("模型训练出错", 5000)
        self.train_btn.setEnabled(True) # 重新启用训练按钮
        self.params_btn.setEnabled(True) # 重新启用参数设置按钮
        self.save_model_action.setEnabled(False) # 保持禁用保存模型按钮

    def show_results(self, text_results):
        """在结果文本框中显示训练结果"""
        self.result_text.setFont(QFont("Consolas", 10))
        self.result_text.setText(text_results)

    def plot_importance(self, importances, target):
        """绘制特征重要性条形图，调整字体大小至16号"""
        current_figure = Figure(figsize=(8, 4))
        canvas = FigureCanvas(current_figure)
        ax = current_figure.add_subplot(111)

        features = list(importances.keys())
        values = list(importances.values())

        ax.barh(features, values)
        ax.set_title(f"Feature Importance for {target}", fontsize=16)  # 设置标题字体大小为16号
        ax.set_xlabel("Score", fontsize=16)  # 设置横坐标标签字体大小为16号
        # ax.set_ylabel("Features", fontsize=16) # 如果需要设置纵坐标标签字体大小，取消注释并设置标签文本

        # 设置 y 轴刻度标签字体大小
        for label in ax.get_yticklabels():
            label.set_fontsize(14)

        # 设置 x 轴刻度标签字体大小
        for label in ax.get_xticklabels():
            label.set_fontsize(14)

        canvas.draw()
        self.chart_layout_vertical.addWidget(canvas)

    def clear_chart_layout(self):
        """清空图表布局中的所有旧图表"""
        for i in reversed(range(self.chart_layout_vertical.count())):
            widget_to_remove = self.chart_layout_vertical.itemAt(i).widget()
            self.chart_layout_vertical.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

    def save_model_dialog(self):
        """打开保存模型对话框"""
        if self.model is None:
            QMessageBox.warning(self, "模型未训练", "请先训练模型再保存。")
            return
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存模型", "", "模型文件 (*.model);;所有文件 (*)", options=options)
        if file_path:
            try:
                model_data = {
                    'model': self.model,
                    'feature_names': self.feature_names,
                    'target_names': self.target_names,
                    'algorithm_name': self.algorithm_name,
                    'scaling_method': self.feature_scaling_method
                }
                joblib.dump(model_data, file_path)
                self.statusBar().showMessage(f"模型已保存到: {file_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "保存模型失败", f"保存模型时发生错误：{str(e)}")
                self.statusBar().showMessage(f"模型保存失败：{str(e)}", 5000)

    def load_model_dialog(self):
        """打开加载模型对话框"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "加载模型", "", "模型文件 (*.model);;所有文件 (*)", options=options)
        if file_path:
            try:
                model_data = joblib.load(file_path)
                self.model = model_data['model']
                self.feature_names = model_data['feature_names']
                self.target_names = model_data['target_names']
                self.algorithm_name = model_data['algorithm_name']
                self.feature_scaling_method = model_data['scaling_method']

                algorithm_display_name = self.algorithm_name
                if self.algorithm_name == "SVR":
                    algorithm_display_name = "支持向量回归 (SVR)"
                elif self.algorithm_name == "K-近邻 (KNN)":
                    algorithm_display_name = "K-近邻 (KNN)"
                elif self.algorithm_name == "极限梯度提升 (XGBoost)":
                    algorithm_display_name = "极限梯度提升 (XGBoost)"
                elif self.algorithm_name == "神经网络 (Neural Network)":
                    algorithm_display_name = "神经网络 (Neural Network)"

                scaling_display_name = "无"
                if isinstance(self.feature_scaling_method, StandardScaler):
                    scaling_display_name = "标准化 (StandardScaler)"
                elif isinstance(self.feature_scaling_method, MinMaxScaler):
                    scaling_display_name = "最小-最大缩放 (MinMaxScaler)"

                model_info = f"已加载模型: {algorithm_display_name}, 特征缩放: {scaling_display_name}"
                self.statusBar().showMessage(model_info, 5000)
                QMessageBox.information(self, "模型加载成功", f"模型 '{file_path}' 加载成功。\n{model_info}")

                self.algorithm_combo.setCurrentText(algorithm_display_name)
                scaling_index = self.scaling_combo.findText(scaling_display_name)
                if scaling_index != -1:
                    self.scaling_combo.setCurrentIndex(scaling_index)
                else: # 如果加载的模型没有特征缩放，则设置为 "无"
                    no_scaling_index = self.scaling_combo.findText("无")
                    if no_scaling_index != -1:
                        self.scaling_combo.setCurrentIndex(no_scaling_index)


            except FileNotFoundError:
                QMessageBox.critical(self, "模型文件未找到", f"找不到模型文件：{file_path}")
                self.statusBar().showMessage("模型加载失败：文件未找到", 5000)
            except Exception as e:
                QMessageBox.critical(self, "加载模型错误", f"加载模型文件时发生错误：{str(e)}")
                self.statusBar().showMessage(f"模型加载错误：{str(e)}", 5000)

class MissingValueDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("缺失值处理")
        self.options_group = QButtonGroup(self)

        layout = QVBoxLayout(self)

        info_label = QLabel("检测到数据中存在缺失值，请选择处理方式：")
        layout.addWidget(info_label)

        options_group_box = QGroupBox("处理选项")
        options_layout = QVBoxLayout(options_group_box)

        mean_radio = QRadioButton("使用均值填充")
        mean_radio.setChecked(True)
        self.options_group.addButton(mean_radio)
        options_layout.addWidget(mean_radio)

        median_radio = QRadioButton("使用中位数填充")
        self.options_group.addButton(median_radio)
        options_layout.addWidget(median_radio)

        remove_rows_radio = QRadioButton("移除包含缺失值的行")
        self.options_group.addButton(remove_rows_radio)
        options_layout.addWidget(remove_rows_radio)

        options_group_box.setLayout(options_layout)
        layout.addWidget(options_group_box)

        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("确定", self)
        ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_button)
        cancel_button = QPushButton("取消", self)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def get_selected_option(self):
        selected_button = self.options_group.checkedButton()
        if selected_button:
            return {
                "使用均值填充": 'mean',
                "使用中位数填充": 'median',
                "移除包含缺失值的行": 'remove_rows'
            }.get(selected_button.text(), None)
        return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MLClient()
    window.show()
    sys.exit(app.exec_())