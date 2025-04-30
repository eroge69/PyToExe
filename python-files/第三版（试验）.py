# -*- coding: utf-8 -*-
import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTableView, QListWidget,
    QListWidgetItem, QComboBox, QStackedWidget, QStatusBar,
    QMenuBar, QSizePolicy, QSpacerItem, QAbstractItemView,
    QGroupBox, QFormLayout, QLineEdit, QSpinBox, QTextEdit, QMessageBox,
    QTabWidget, QHeaderView, QStyleOptionButton, QStyle
)
from PyQt6.QtGui import (
    QAction, QIcon, QPalette, QColor, QFont, QPainter, QStandardItemModel,
    QStandardItem, QActionGroup
)
from PyQt6.QtCore import (
    Qt, QAbstractTableModel, QModelIndex, QVariant, pyqtSignal, QThread,
    QSize, QObject
)

# --- Matplotlib Embedding ---
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# --- ML Libraries ---
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             r2_score, mean_absolute_error, mean_squared_error, roc_auc_score)
from scipy.stats import spearmanr
import lightgbm as lgb
import xgboost as xgb
import numpy as np
import traceback

# --- Constants ---
APP_NAME = "智能机器学习分析平台"
DEFAULT_THEME = "light"
VERSION = "0.2.3" # Incremented version after fix

# =============================================================================
# Helper Classes and Functions
# =============================================================================

class PandasModel(QAbstractTableModel):
    """A model to interface a Pandas DataFrame with QTableView."""
    def __init__(self, dataframe: pd.DataFrame = None, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._dataframe = dataframe if dataframe is not None else pd.DataFrame()

    def rowCount(self, parent=QModelIndex()) -> int:
        if not parent.isValid(): return len(self._dataframe)
        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        if not parent.isValid(): return len(self._dataframe.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount()):
            return QVariant()
        try: value = self._dataframe.iloc[index.row(), index.column()]
        except IndexError: return QVariant()

        if role == Qt.ItemDataRole.DisplayRole:
            if isinstance(value, (float, np.floating)):
                if pd.isna(value): return QVariant("NaN")
                if np.isinf(value): return QVariant("Inf")
                return QVariant(f"{value:.4f}")
            return QVariant(str(value))
        elif role == Qt.ItemDataRole.ToolTipRole: return QVariant(str(value))
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if isinstance(value, (int, float, np.number)): return QVariant(int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))
            else: return QVariant(int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))
        return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if 0 <= section < len(self._dataframe.columns): return QVariant(str(self._dataframe.columns[section]))
            if orientation == Qt.Orientation.Vertical: return QVariant(str(section + 1))
        return QVariant()

    def get_dataframe(self): return self._dataframe

    def update_dataframe(self, new_dataframe: pd.DataFrame = None):
        self.beginResetModel()
        self._dataframe = new_dataframe if new_dataframe is not None else pd.DataFrame()
        self.endResetModel()


class Worker(QThread):
    """ Generic worker thread for long-running tasks """
    finished = pyqtSignal(object)
    error = pyqtSignal(tuple)
    progress = pyqtSignal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func; self.args = args; self.kwargs = kwargs

    # --- FIX: Pass self.progress signal to the target function ---
    def run(self):
        try:
            # Don't emit 'Task started...' here, let the target function do it
            # Pass the progress signal object as the first argument to self.func
            result = self.func(self.progress, *self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            exc_type, exc_value, tb = sys.exc_info()
            tb_str = "".join(traceback.format_exception(exc_type, exc_value, tb))
            # Emit error *before* progress update for failure
            self.error.emit((exc_type, exc_value, tb_str))
            # Update progress *after* error signal if needed
            # self.progress.emit("任务失败.") # Optional: Can be emitted by main thread based on error signal
    # -----------------------------------------------------------


# =============================================================================
# Main Application Window
# =============================================================================

class MLClientApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME); self.setGeometry(100, 100, 1200, 750)
        self.dataframe = None; self.current_file_path = None
        self.feature_cols = []; self.target_col = None
        self.model = None; self.X_test_data = None; self.y_test_data = None
        self.predictions = None; self.model_type = None; self.trained_feature_names = None
        self.current_theme = DEFAULT_THEME
        self.central_widget = QWidget(); self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)
        self._create_menu_bar(); self._create_left_nav_bar(); self._create_main_panel(); self._create_status_bar()
        self.set_theme(self.current_theme)
        self.main_layout.addWidget(self.left_nav_widget, 1); self.main_layout.addWidget(self.main_stack, 5)
        self.main_stack.setCurrentIndex(0); self.update_nav_selection(0); self._update_ui_state()

    def set_theme(self, theme_name="light"):
        self.current_theme = theme_name; app = QApplication.instance()
        light_palette = QPalette(); dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53)) # ... (rest of dark palette definition)
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(120, 120, 120))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        disabled_text_color = QColor(127, 127, 127)
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_text_color)
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_text_color)

        if theme_name == "dark":
            app.setPalette(dark_palette)
            app.setStyleSheet("""
                QWidget { color: white; background-color: #353535; } QMainWindow, QDialog { background-color: #353535; }
                QMenuBar { background-color: #353535; color: white; } QMenuBar::item:selected { background-color: #5A5A5A; }
                QMenu { background-color: #353535; color: white; border: 1px solid #5A5A5A; } QMenu::item:selected { background-color: #4286d4; }
                QStatusBar { background-color: #353535; color: white; }
                QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox { background-color: #232323; color: white; border: 1px solid #5A5A5A; border-radius: 3px; padding: 3px; }
                QLineEdit:read-only, QTextEdit:read-only { background-color: #404040; }
                QPushButton { background-color: #5A5A5A; color: white; border: 1px solid #6A6A6A; padding: 5px 10px; border-radius: 3px; min-height: 25px; }
                QPushButton:hover { background-color: #6A6A6A; } QPushButton:pressed { background-color: #4A4A4A; }
                QPushButton:checked { background-color: #4286d4; border: 1px solid #3173ba; font-weight: bold; }
                QPushButton:disabled { background-color: #454545; color: #888888; border: 1px solid #555555; }
                QTableView { background-color: #232323; color: white; alternate-background-color: #2A2A2A; gridline-color: #4A4A4A; border: 1px solid #5A5A5A; selection-background-color: #4286d4; selection-color: black; }
                QHeaderView::section { background-color: #4A4A4A; color: white; padding: 4px; border: 1px solid #5A5A5A; }
                QListWidget { background-color: #232323; color: white; border: 1px solid #5A5A5A; } QListWidget::item:selected { background-color: #4286d4; color: black; }
                QGroupBox { color: white; border: 1px solid #5A5A5A; border-radius: 3px; margin-top: 10px; }
                QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; left: 10px; }
                QTabWidget::pane { border: 1px solid #5A5A5A; border-top: none; }
                QTabBar::tab { background-color: #4A4A4A; color: white; padding: 8px 15px; border: 1px solid #5A5A5A; border-bottom: none; border-top-left-radius: 3px; border-top-right-radius: 3px; }
                QTabBar::tab:selected { background-color: #353535; color: #4286d4; font-weight: bold; } QTabBar::tab:!selected:hover { background-color: #5A5A5A; }
                QWidget#LeftNavBar { background-color: #2A2A2A; }
                QWidget#LeftNavBar QPushButton { background-color: transparent; border: none; color: #CCCCCC; text-align: left; padding-left: 15px; border-radius: 5px; min-height: 40px; }
                QWidget#LeftNavBar QPushButton:checked { background-color: #4286d4; color: white; font-weight: bold; }
                QWidget#LeftNavBar QPushButton:hover:!checked { background-color: #4A4A4A; }
            """)
            icon_color = "white"; plt.style.use('dark_background')
        else: # Light Theme
            app.setPalette(light_palette)
            app.setStyleSheet("""
                QWidget#LeftNavBar { background-color: #f0f0f0; }
                QWidget#LeftNavBar QPushButton { background-color: transparent; border: none; color: #333333; text-align: left; padding-left: 15px; border-radius: 5px; min-height: 40px; }
                QWidget#LeftNavBar QPushButton:checked { background-color: #4a90e2; color: white; font-weight: bold; }
                QWidget#LeftNavBar QPushButton:hover:!checked { background-color: #e0e0e0; }
            """)
            icon_color = "black"; plt.style.use('default')

        font = QFont("Segoe UI", 9);
        if sys.platform == "darwin": font = QFont("San Francisco", 13)
        elif sys.platform.startswith("linux"): font = QFont("Noto Sans", 10)
        app.setFont(font)
        self._update_icons(icon_color); self.update()

    def _update_icons(self, color):
        style = QApplication.style()
        if hasattr(self, 'nav_buttons'):
             try: # Add try-except for robustness
                 self.nav_buttons["import"].setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon))
                 self.nav_buttons["preview"].setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
                 self.nav_buttons["config"].setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
                 self.nav_buttons["model"].setIcon(style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
                 self.nav_buttons["results"].setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
             except AttributeError: print("Warning: Could not load standard icons.")
        # Safely update action icons
        if hasattr(self, 'open_action') and self.open_action:
             try: self.open_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
             except AttributeError: pass
        if hasattr(self, 'exit_action') and self.exit_action:
             try: self.exit_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))
             except AttributeError: pass


    def _create_menu_bar(self): # (Code unchanged, assumed correct)
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("文件 (&F)")
        self.open_action = QAction("打开文件 (&O)...", self); self.open_action.triggered.connect(self.load_data_dialog)
        file_menu.addAction(self.open_action); file_menu.addSeparator()
        self.exit_action = QAction("退出 (&X)", self); self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        view_menu = menu_bar.addMenu("视图 (&V)")
        theme_menu = view_menu.addMenu("主题 (&T)")
        self.light_theme_action = QAction("浅色主题", self, checkable=True); self.light_theme_action.setChecked(self.current_theme == "light"); self.light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        self.dark_theme_action = QAction("深色主题", self, checkable=True); self.dark_theme_action.setChecked(self.current_theme == "dark"); self.dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_group = QActionGroup(self); theme_group.addAction(self.light_theme_action); theme_group.addAction(self.dark_theme_action); theme_group.setExclusive(True)
        theme_menu.addAction(self.light_theme_action); theme_menu.addAction(self.dark_theme_action)
        help_menu = menu_bar.addMenu("帮助 (&H)")
        about_action = QAction("关于 (&A)...", self); about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def _create_left_nav_bar(self): # (Code unchanged, assumed correct)
        self.left_nav_widget = QWidget(); self.left_nav_layout = QVBoxLayout(self.left_nav_widget)
        self.left_nav_layout.setContentsMargins(5, 10, 5, 10); self.left_nav_layout.setSpacing(8)
        self.left_nav_widget.setObjectName("LeftNavBar"); self.left_nav_widget.setFixedWidth(180)
        self.nav_buttons = {}
        nav_items = [("import", "数据导入"), ("preview", "数据预览"), ("config", "变量配置"), ("model", "模型配置"), ("results", "结果分析")]
        for i, (key, text) in enumerate(nav_items):
            button = QPushButton(f"  {text}"); button.setCheckable(True); button.setAutoExclusive(True)
            button.clicked.connect(lambda checked=False, index=i: self.switch_main_panel(index))
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.nav_buttons[key] = button; self.left_nav_layout.addWidget(button)
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding); self.left_nav_layout.addItem(spacer)

    def _create_main_panel(self): # (Code unchanged, assumed correct)
        self.main_stack = QStackedWidget(); self.main_stack.setContentsMargins(15, 15, 15, 15)
        self.page_welcome = self._create_welcome_page(); self.page_preview = self._create_preview_page()
        self.page_config = self._create_config_page(); self.page_model = self._create_model_page()
        self.page_results = self._create_results_page()
        self.main_stack.addWidget(self.page_welcome); self.main_stack.addWidget(self.page_preview)
        self.main_stack.addWidget(self.page_config); self.main_stack.addWidget(self.page_model); self.main_stack.addWidget(self.page_results)

    def _create_welcome_page(self): # (Code unchanged, assumed correct)
        page = QWidget(); layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label = QLabel(f"欢迎使用 {APP_NAME}"); font = welcome_label.font(); font.setPointSize(18); font.setBold(True); welcome_label.setFont(font); welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label = QLabel("请导入数据 (CSV/XLSX)."); instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter); instruction_label.setWordWrap(True)
        self.load_button_welcome = QPushButton(" 选择数据文件..."); self.load_button_welcome.clicked.connect(self.load_data_dialog)
        layout.addStretch(1); layout.addWidget(welcome_label); layout.addWidget(instruction_label); layout.addSpacing(20)
        layout.addWidget(self.load_button_welcome, 0, Qt.AlignmentFlag.AlignCenter); layout.addStretch(2); return page

    def _create_preview_page(self): # (Code unchanged, assumed correct)
        page = QWidget(); layout = QVBoxLayout(page)
        top_layout = QHBoxLayout(); self.preview_label = QLabel("数据预览: (未加载)"); font = self.preview_label.font(); font.setBold(True); self.preview_label.setFont(font)
        self.rows_cols_label = QLabel(""); top_layout.addWidget(self.preview_label); top_layout.addStretch(1); top_layout.addWidget(self.rows_cols_label); layout.addLayout(top_layout)
        self.preview_table = QTableView(); self.preview_table.setAlternatingRowColors(True); self.preview_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.preview_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); header = QHeaderView(Qt.Orientation.Horizontal); self.preview_table.setHorizontalHeader(header)
        header.setStretchLastSection(False); header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.preview_table.verticalHeader().setVisible(True); self.preview_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.preview_model = PandasModel(None); self.preview_table.setModel(self.preview_model); layout.addWidget(self.preview_table); return page

    def _create_config_page(self): # (Code unchanged, assumed correct)
        page = QWidget(); main_layout = QVBoxLayout(page)
        config_label = QLabel("变量配置"); font = config_label.font(); font.setBold(True); config_label.setFont(font); main_layout.addWidget(config_label)
        hbox = QHBoxLayout()
        vbox_avail = QVBoxLayout(); vbox_avail.addWidget(QLabel("可用列:")); self.avail_cols_list = QListWidget(); self.avail_cols_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection); vbox_avail.addWidget(self.avail_cols_list); hbox.addLayout(vbox_avail, 2)
        vbox_buttons = QVBoxLayout(); vbox_buttons.addStretch(1); self.add_feature_button = QPushButton(">>\n添加特征"); self.add_feature_button.clicked.connect(self.add_features)
        self.remove_feature_button = QPushButton("<<\n移除特征"); self.remove_feature_button.clicked.connect(self.remove_features)
        self.set_target_button = QPushButton(" > \n设为目标"); self.set_target_button.clicked.connect(self.set_target)
        self.clear_target_button = QPushButton(" < \n清除目标"); self.clear_target_button.clicked.connect(self.clear_target)
        vbox_buttons.addWidget(self.add_feature_button); vbox_buttons.addSpacing(10); vbox_buttons.addWidget(self.remove_feature_button); vbox_buttons.addSpacing(20)
        vbox_buttons.addWidget(self.set_target_button); vbox_buttons.addSpacing(10); vbox_buttons.addWidget(self.clear_target_button); vbox_buttons.addStretch(1); hbox.addLayout(vbox_buttons, 1)
        vbox_selected = QVBoxLayout(); vbox_selected.addWidget(QLabel("特征变量 (Features):")); self.feature_cols_list = QListWidget(); self.feature_cols_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection); vbox_selected.addWidget(self.feature_cols_list)
        vbox_selected.addSpacing(10); vbox_selected.addWidget(QLabel("目标变量 (Target):")); self.target_col_label = QLabel("<i>(未选择)</i>"); self.target_col_label.setFrameShape(QLabel.Shape.StyledPanel); self.target_col_label.setFrameShadow(QLabel.Shadow.Sunken)
        self.target_col_label.setMinimumHeight(25); self.target_col_label.setAlignment(Qt.AlignmentFlag.AlignCenter); vbox_selected.addWidget(self.target_col_label); hbox.addLayout(vbox_selected, 2)
        main_layout.addLayout(hbox); return page

    def _create_model_page(self): # (Code unchanged, assumed correct)
        page = QWidget(); layout = QVBoxLayout(page)
        model_select_label = QLabel("模型选择与配置"); font = model_select_label.font(); font.setBold(True); model_select_label.setFont(font); layout.addWidget(model_select_label)
        algo_layout = QHBoxLayout(); algo_layout.addWidget(QLabel("选择算法:")); self.algo_combo = QComboBox(); self.algo_combo.addItems(["随机森林", "神经网络(MLP)", "LightGBM", "XGBoost"]); algo_layout.addWidget(self.algo_combo, 1); layout.addLayout(algo_layout)
        self.param_group = QGroupBox("算法参数调整 (基础)"); self.param_layout = QFormLayout(self.param_group); self.param_n_estimators = QSpinBox(); self.param_n_estimators.setRange(10, 5000); self.param_n_estimators.setValue(100)
        self.param_layout.addRow("树/迭代次数:", self.param_n_estimators); self.param_max_depth = QSpinBox(); self.param_max_depth.setRange(-1, 100); self.param_max_depth.setValue(10); self.param_max_depth.setSpecialValueText("无限制 (-1)")
        self.param_layout.addRow("最大深度:", self.param_max_depth); layout.addWidget(self.param_group); layout.addStretch(1)
        self.train_button = QPushButton(" 开始训练模型"); self.train_button.clicked.connect(self.run_training); layout.addWidget(self.train_button); return page

    def _create_results_page(self): # (Code unchanged, assumed correct)
        page = QWidget(); layout = QVBoxLayout(page)
        results_label = QLabel("结果分析"); font = results_label.font(); font.setBold(True); results_label.setFont(font); layout.addWidget(results_label)
        self.results_tabs = QTabWidget()
        self.tab_predictions = QWidget(); pred_layout = QVBoxLayout(self.tab_predictions); pred_layout.addWidget(QLabel("预测结果预览 (测试集):")); self.predictions_table = QTableView()
        self.predictions_table.setAlternatingRowColors(True); self.predictions_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); header_pred = QHeaderView(Qt.Orientation.Horizontal); self.predictions_table.setHorizontalHeader(header_pred)
        header_pred.setSectionResizeMode(QHeaderView.ResizeMode.Interactive); self.prediction_model = PandasModel(None); self.predictions_table.setModel(self.prediction_model); pred_layout.addWidget(self.predictions_table); self.results_tabs.addTab(self.tab_predictions, "预测结果")
        self.tab_metrics = QWidget(); metrics_layout = QVBoxLayout(self.tab_metrics); metrics_layout.addWidget(QLabel("模型评估指标:")); self.metrics_display = QTextEdit(); self.metrics_display.setReadOnly(True); metrics_layout.addWidget(self.metrics_display); self.results_tabs.addTab(self.tab_metrics, "评估指标")
        self.tab_importance = QWidget(); importance_layout = QVBoxLayout(self.tab_importance); importance_layout.addWidget(QLabel("特征重要性:")); self.importance_figure = Figure(figsize=(5, 4), dpi=100)
        self.importance_canvas = FigureCanvas(self.importance_figure); importance_layout.addWidget(self.importance_canvas); self.results_tabs.addTab(self.tab_importance, "特征重要性")
        layout.addWidget(self.results_tabs); return page

    def _create_status_bar(self): self.status_bar = QStatusBar(); self.setStatusBar(self.status_bar); self.status_bar.showMessage("就绪.") # (Code unchanged)

    def switch_main_panel(self, index): # (Code unchanged, assumed correct)
        if not (0 <= index < self.main_stack.count()): return
        requires_data = index > 0
        if requires_data and self.dataframe is None:
            self.status_bar.showMessage("请先加载数据文件.", 3000); current_index = self.main_stack.currentIndex(); self.update_nav_selection(current_index); return
        self.main_stack.setCurrentIndex(index); self.update_nav_selection(index); self._update_ui_state()

    def update_nav_selection(self, index): # (Code unchanged, assumed correct)
        keys = list(self.nav_buttons.keys())
        if 0 <= index < len(keys):
            target_key = keys[index]
            for key, button in self.nav_buttons.items(): button.setChecked(key == target_key)

    def show_about_dialog(self): QMessageBox.about(self, "关于", f"<h2>{APP_NAME} v{VERSION}</h2><p>机器学习分析平台.</p>") # (Code unchanged)

    def _update_ui_state(self): # (Code unchanged, assumed correct)
        data_loaded = self.dataframe is not None; vars_configured = data_loaded and bool(self.feature_cols) and self.target_col is not None
        model_trained = self.model is not None; config_elements_exist = hasattr(self, 'add_feature_button')
        if config_elements_exist:
            self.add_feature_button.setEnabled(data_loaded); self.remove_feature_button.setEnabled(data_loaded)
            self.set_target_button.setEnabled(data_loaded); self.clear_target_button.setEnabled(data_loaded and self.target_col is not None)
        if hasattr(self, 'train_button'):
            is_training = self.train_button.text() == "正在训练..."; self.train_button.setEnabled(vars_configured and not is_training)
        if hasattr(self, 'rows_cols_label') and hasattr(self, 'preview_label'):
            if data_loaded:
                rows, cols = self.dataframe.shape; self.rows_cols_label.setText(f"{rows}x{cols}")
                fname = self.current_file_path.split('/')[-1] if self.current_file_path else "数据"; self.preview_label.setText(f"预览: {fname}")
            else: self.rows_cols_label.setText(""); self.preview_label.setText("预览: (未加载)")
        if not model_trained and hasattr(self, 'prediction_model'):
             self.prediction_model.update_dataframe(None);
             if hasattr(self, 'metrics_display'): self.metrics_display.clear()
             if hasattr(self, 'importance_figure'): self.importance_figure.clear()
             if hasattr(self, 'importance_canvas'): self.importance_canvas.draw()


    def load_data_dialog(self): # (Code unchanged, assumed correct)
        file_path, _ = QFileDialog.getOpenFileName(self, "选择数据文件", "", "数据 (*.csv *.xlsx)")
        if not file_path: return
        self.status_bar.showMessage(f"加载中: {file_path}..."); self.load_button_welcome.setEnabled(False); self.open_action.setEnabled(False)
        self.worker = Worker(self._load_data_thread, file_path); self.worker.finished.connect(self._on_data_loaded)
        self.worker.error.connect(self._on_load_error); self.worker.progress.connect(self.status_bar.showMessage)
        self.worker.finished.connect(self._reset_load_buttons_state); self.worker.error.connect(self._reset_load_buttons_state); self.worker.start()

    def _reset_load_buttons_state(self): self.load_button_welcome.setEnabled(True); self.open_action.setEnabled(True) # (Code unchanged)

    # --- FIX: Add progress_signal parameter and use it ---
    def _load_data_thread(self, progress_signal, file_path):
        progress_signal.emit(f"读取: {file_path.split('/')[-1]}...")
        try:
            if file_path.lower().endswith('.csv'): df = pd.read_csv(file_path)
            elif file_path.lower().endswith('.xlsx'): df = pd.read_excel(file_path)
            else: raise ValueError("不支持的文件格式.")
            if df.empty: raise ValueError("文件数据为空.")
            if not all(isinstance(c, str) for c in df.columns):
                 df.columns = df.columns.astype(str)
                 progress_signal.emit("警告: 列名转为字符串.") # Use progress_signal
            progress_signal.emit("文件读取完成.") # Use progress_signal
            return df, file_path
        except Exception as e:
            # No need to emit progress here, error signal handles it
            raise RuntimeError(f"加载文件失败: {e}")
    # ----------------------------------------------------

    def _on_data_loaded(self, result): # (Code unchanged, assumed correct)
        df, file_path = result; self.dataframe = df; self.current_file_path = file_path
        self.status_bar.showMessage(f"加载成功: {file_path.split('/')[-1]} ({len(df)}x{len(df.columns)})", 5000)
        self._reset_model_state(); self.preview_model.update_dataframe(self.dataframe)
        try: self.preview_table.resizeColumnsToContents()
        except Exception as e: print(f"Warn: resize failed: {e}")
        self.update_config_lists(); self._update_ui_state(); self.switch_main_panel(1)

    def _on_load_error(self, error_info): # (Code unchanged, assumed correct)
        exc_type, exc_value, tb_str = error_info; QMessageBox.critical(self, "加载错误", f"加载出错:\n{exc_value}\n\n详细:\n{tb_str}")
        self.status_bar.showMessage("加载失败.", 5000); self.dataframe = None; self.current_file_path = None
        self._reset_model_state(); self.preview_model.update_dataframe(None); self.update_config_lists(); self._update_ui_state(); self.switch_main_panel(0)

    def _reset_model_state(self): # (Code unchanged, assumed correct)
        self.feature_cols = []; self.target_col = None; self.model = None; self.X_test_data = None; self.y_test_data = None
        self.predictions = None; self.model_type = None; self.trained_feature_names = None
        if hasattr(self, 'prediction_model'): self.prediction_model.update_dataframe(None)
        if hasattr(self, 'metrics_display'): self.metrics_display.clear()
        if hasattr(self, 'importance_figure'): self.importance_figure.clear();
        if hasattr(self, 'importance_canvas'): self.importance_canvas.draw()

    def update_config_lists(self): # (Code unchanged, assumed correct)
        current_features = set(self.feature_cols); current_target = self.target_col
        self.avail_cols_list.clear(); self.feature_cols_list.clear()
        self.feature_cols = []; self.target_col = None; self.target_col_label.setText("<i>(未选择)</i>")
        if self.dataframe is not None:
            all_columns = self.dataframe.columns.tolist(); avail_cols_temp, features_temp = [], []
            for col in all_columns:
                if col == current_target: self.target_col = col; self.target_col_label.setText(f"<b>{col}</b>")
                elif col in current_features: features_temp.append(col)
                else: avail_cols_temp.append(col)
            self.avail_cols_list.addItems(avail_cols_temp); self.feature_cols_list.addItems(features_temp); self.feature_cols = features_temp

    def add_features(self): # (Code unchanged, assumed correct)
        selected = self.avail_cols_list.selectedItems(); items = [item.text() for item in selected]
        for name in items:
            found = self.avail_cols_list.findItems(name, Qt.MatchFlag.MatchExactly)
            if found: self.avail_cols_list.takeItem(self.avail_cols_list.row(found[0]))
            if name not in self.feature_cols: self.feature_cols_list.addItem(name); self.feature_cols.append(name)
        self._update_ui_state()

    def remove_features(self): # (Code unchanged, assumed correct)
        selected = self.feature_cols_list.selectedItems(); items = [item.text() for item in selected]
        for name in items:
            found = self.feature_cols_list.findItems(name, Qt.MatchFlag.MatchExactly)
            if found: self.feature_cols_list.takeItem(self.feature_cols_list.row(found[0]))
            if name in self.feature_cols: self.feature_cols.remove(name)
            if name != self.target_col and not self.avail_cols_list.findItems(name, Qt.MatchFlag.MatchExactly): self.avail_cols_list.addItem(name)
        self._update_ui_state()

    def set_target(self): # (Code unchanged, assumed correct)
        selected = self.avail_cols_list.selectedItems()
        if len(selected) != 1: QMessageBox.warning(self, "选择目标", "请选择一个目标变量。"); return
        item = selected[0]; new_target = item.text()
        if self.target_col and self.target_col != new_target and not self.avail_cols_list.findItems(self.target_col, Qt.MatchFlag.MatchExactly): self.avail_cols_list.addItem(self.target_col)
        self.target_col = new_target; self.target_col_label.setText(f"<b>{self.target_col}</b>")
        self.avail_cols_list.takeItem(self.avail_cols_list.row(item))
        found_feature = self.feature_cols_list.findItems(self.target_col, Qt.MatchFlag.MatchExactly)
        if found_feature: self.feature_cols_list.takeItem(self.feature_cols_list.row(found_feature[0]))
        if self.target_col in self.feature_cols: self.feature_cols.remove(self.target_col)
        self._update_ui_state()

    def clear_target(self): # (Code unchanged, assumed correct)
        if self.target_col:
            old = self.target_col; self.target_col = None; self.target_col_label.setText("<i>(未选择)</i>")
            if old not in self.feature_cols and not self.avail_cols_list.findItems(old, Qt.MatchFlag.MatchExactly): self.avail_cols_list.addItem(old)
            self._update_ui_state()

    def run_training(self): # (Code unchanged, assumed correct)
        if not self._validate_before_training(): return
        algo = self.algo_combo.currentText(); params = self._get_current_params()
        self.status_bar.showMessage(f"准备训练 {algo}..."); self.train_button.setEnabled(False); self.train_button.setText("正在训练...")
        df_copy=self.dataframe.copy(); feat_copy=self.feature_cols[:]; targ_copy=self.target_col
        self.train_worker = Worker(self._train_model_thread, df_copy, feat_copy, targ_copy, algo, params)
        self.train_worker.finished.connect(self._on_training_complete); self.train_worker.error.connect(self._on_training_error)
        self.train_worker.progress.connect(self.status_bar.showMessage); self.train_worker.finished.connect(self._reset_train_button_state)
        self.train_worker.error.connect(self._reset_train_button_state); self.train_worker.start()

    def _validate_before_training(self): # (Code unchanged, assumed correct)
        if self.dataframe is None: QMessageBox.warning(self, "错误", "请加载数据."); return False
        if not self.feature_cols: QMessageBox.warning(self, "错误", "请选择特征."); return False
        if not self.target_col: QMessageBox.warning(self, "错误", "请选择目标."); return False
        if self.target_col in self.feature_cols: QMessageBox.critical(self, "错误", "目标不能同时为特征."); return False
        return True

    def _get_current_params(self): return {'n_estimators': self.param_n_estimators.value(), 'max_depth': self.param_max_depth.value() if self.param_max_depth.value() != -1 else None} # (Code unchanged)

    def _reset_train_button_state(self): # (Code unchanged, assumed correct)
        vars_ok = self.dataframe is not None and bool(self.feature_cols) and self.target_col is not None
        self.train_button.setEnabled(vars_ok); self.train_button.setText(" 开始训练模型")

    # --- FIX: Add progress_signal parameter and use it throughout ---
    def _train_model_thread(self, progress_signal, df, features, target, algo_name, params):
        progress_signal.emit("数据预处理..."); X = df[features].copy(); y = df[target].copy()
        num_cols = X.select_dtypes(include=np.number).columns; cat_cols = X.select_dtypes(exclude=np.number).columns; msgs = []
        for col in num_cols:
            if X[col].isnull().any(): med = X[col].median(); X[col].fillna(med, inplace=True); msgs.append(f"'{col}':中位数({med:.2f})")
        for col in cat_cols:
            if X[col].isnull().any():
                if not X[col].empty: mode = X[col].mode()[0]; X[col].fillna(mode, inplace=True); msgs.append(f"'{col}':众数({mode})")
                else: X[col].fillna("missing", inplace=True); msgs.append(f"'{col}':填充 'missing'")
        if msgs: progress_signal.emit(f"填充缺失: {'; '.join(msgs)}") # Use progress_signal
        if y.isnull().any(): idx = y.isnull(); y=y[~idx]; X=X[~idx]; progress_signal.emit(f"警告:删{idx.sum()}行(目标缺失)."); # Use progress_signal
        if X.empty: raise ValueError("无有效数据行.")

        progress_signal.emit("推断类型..."); unique = y.nunique() # Use progress_signal
        if pd.api.types.is_numeric_dtype(y) and (pd.api.types.is_float_dtype(y) or unique > 20): p_type='regression'
        elif pd.api.types.is_object_dtype(y) or pd.api.types.is_categorical_dtype(y) or unique <= 20:
            p_type='classification'
            if not pd.api.types.is_numeric_dtype(y): y,_=pd.factorize(y); y=pd.Series(y,index=X.index); progress_signal.emit("目标转数值.") # Use progress_signal
        else: raise ValueError(f"无法确定目标类型 '{target}' ({y.dtype}, {unique} uniques).")
        progress_signal.emit(f"类型: {p_type}") # Use progress_signal

        progress_signal.emit("处理类别特征..."); init_cols = X.shape[1]; X=pd.get_dummies(X, drop_first=True, dummy_na=False); names=X.columns.tolist() # Use progress_signal
        new_cols = X.shape[1]-init_cols;
        if new_cols > 0: progress_signal.emit(f"One-Hot 完成 (增{new_cols}列)") # Use progress_signal

        progress_signal.emit("拆分数据..."); strat=y if p_type=='classification' else None # Use progress_signal
        try: X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42, stratify=strat)
        except ValueError: progress_signal.emit("警告:分层拆分失败."); X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42) # Use progress_signal

        progress_signal.emit(f"初始化: {algo_name}..."); model=None; n_est=params.get('n_estimators',100); m_dep=params.get('max_depth', None) # Use progress_signal
        t_params={'n_estimators':n_est,'max_depth':m_dep,'random_state':42,'n_jobs':-1}; l_params={'n_estimators':n_est,'max_depth':m_dep if m_dep else -1,'random_state':42,'n_jobs':-1}
        x_params={'n_estimators':n_est,'max_depth':m_dep,'random_state':42,'use_label_encoder':False,'n_jobs':-1}

        try:
            if algo_name.startswith("随机森林"): model=RandomForestClassifier(**t_params) if p_type=='classification' else RandomForestRegressor(**t_params)
            elif algo_name.startswith("神经网络"): m_params={'hidden_layer_sizes':(64,32),'max_iter':500,'random_state':42,'early_stopping':True,'n_iter_no_change':15}; model=MLPClassifier(**m_params) if p_type=='classification' else MLPRegressor(**m_params)
            elif algo_name.startswith("LightGBM"): model=lgb.LGBMClassifier(**l_params) if p_type=='classification' else lgb.LGBMRegressor(**l_params)
            elif algo_name.startswith("XGBoost"):
                if p_type=='classification': n_cls=y.nunique(); obj='binary:logistic' if n_cls<=2 else 'multi:softmax'; ev='logloss' if n_cls<=2 else 'mlogloss'; model=xgb.XGBClassifier(**x_params,objective=obj,eval_metric=ev);
                if n_cls > 2: model.set_params(num_class=n_cls)
                else: model=xgb.XGBRegressor(**x_params,objective='reg:squarederror',eval_metric='rmse')
            if model is None: raise ValueError("模型初始化失败.")

            progress_signal.emit(f"训练 {model.__class__.__name__}..."); model.fit(X_tr, y_tr); progress_signal.emit("训练完成.") # Use progress_signal

            progress_signal.emit("预测评估..."); y_pr=model.predict(X_te); y_proba=None # Use progress_signal
            if p_type=='classification' and hasattr(model,"predict_proba"):
                try: y_proba=model.predict_proba(X_te)
                except Exception as e: progress_signal.emit(f"Warn: proba failed - {e}") # Use progress_signal

            metrics={};
            if p_type=='classification': # (Metrics calculation unchanged)
                metrics['Accuracy']=accuracy_score(y_te,y_pr); n_cls=len(np.unique(y_te)); avg='binary' if n_cls<=2 else 'weighted'
                metrics['Precision']=precision_score(y_te,y_pr,average=avg,zero_division=0); metrics['Recall']=recall_score(y_te,y_pr,average=avg,zero_division=0); metrics['F1-Score']=f1_score(y_te,y_pr,average=avg,zero_division=0)
                if y_proba is not None:
                    try:
                        if n_cls==2: metrics['AUC']=roc_auc_score(y_te,y_proba[:,1])
                        elif n_cls>2: metrics['AUC(OvR)']=roc_auc_score(y_te,y_proba,multi_class='ovr',average='weighted')
                    except ValueError as e: metrics['AUC'] = f"N/A ({e})"
            else: metrics['R²']=r2_score(y_te,y_pr); metrics['MAE']=mean_absolute_error(y_te,y_pr); metrics['MSE']=mean_squared_error(y_te,y_pr); metrics['RMSE']=np.sqrt(metrics['MSE'])
            try: corr,_=spearmanr(y_te,y_pr); metrics['Spearman']=corr if not np.isnan(corr) else 'N/A'
            except: metrics['Spearman']='N/A'

            imp=None; # (Importance calculation unchanged)
            if hasattr(model,'feature_importances_'): imp=model.feature_importances_
            elif hasattr(model,'coef_') and model.coef_.ndim==1: imp=np.abs(model.coef_)
            progress_signal.emit("训练评估完成.") # Use progress_signal
            return {"model":model,"metrics":metrics,"feature_importance":imp,"feature_names":names,"X_test":X_te,"y_test":y_te,"y_pred":y_pr,"model_type":p_type}
        except Exception as e: print(f"Error in train thread:\n{traceback.format_exc()}"); raise RuntimeError(f"训练出错: {e}")
    # ----------------------------------------------------------

    def _on_training_complete(self, results): # (Code unchanged, assumed correct)
        if results is None: QMessageBox.warning(self,"结果","训练无结果."); return
        self.model=results["model"]; self.X_test_data=results["X_test"]; self.y_test_data=results["y_test"]
        self.predictions=results["y_pred"]; self.model_type=results["model_type"]; self.trained_feature_names=results["feature_names"]
        self.status_bar.showMessage("训练成功!", 5000)
        self.display_predictions(); self.display_metrics(results["metrics"]); self.display_feature_importance(results["feature_importance"], self.trained_feature_names)
        self.switch_main_panel(4); self._update_ui_state()

    def _on_training_error(self, error_info): # (Code unchanged, assumed correct)
        exc_type, exc_value, tb_str = error_info; error_dialog = QMessageBox(self); error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("训练失败"); error_dialog.setText(f"训练出错:\n<b>{exc_value}</b>"); error_dialog.setDetailedText(tb_str); error_dialog.exec()
        self.status_bar.showMessage("训练失败.", 5000); self.model = None; self._update_ui_state()

    def display_predictions(self): # (Code unchanged, assumed correct)
        if self.X_test_data is None or self.y_test_data is None or self.predictions is None: self.prediction_model.update_dataframe(None); return
        limit=min(200,len(self.X_test_data)); df=self.X_test_data.head(limit).copy(); actual=self.y_test_data[:limit]; pred=self.predictions[:limit]
        act_name=f"实际_{self.target_col}"; pred_name=f"预测_{self.target_col}"; df[act_name]=actual; df[pred_name]=pred
        cols_move=[act_name,pred_name]; other=[c for c in df.columns if c not in cols_move]; df=df[other+cols_move]
        self.prediction_model.update_dataframe(df);
        try: self.predictions_table.resizeColumnsToContents()
        except Exception as e: print(f"Warn: Resize pred failed: {e}")

    def display_metrics(self, metrics): # (Code unchanged, assumed correct)
        if not metrics: self.metrics_display.setText("无指标."); return
        name=self.model.__class__.__name__ if self.model else "N/A"; txt=f"模型:{name}\n类型:{self.model_type or 'N/A'}\n"
        txt+="="*40+"\n  评估指标\n"+"="*40+"\n"
        for k, v in metrics.items():
            if isinstance(v,(float,np.floating)): txt+=f"{k:<25}: {v:.4f}\n"
            else: txt+=f"{k:<25}: {str(v)}\n"
        txt+="="*40+"\n"; self.metrics_display.setText(txt)

    def display_feature_importance(self, importances, feature_names): # (Code unchanged, assumed correct)
        if not hasattr(self,'importance_figure') or not hasattr(self,'importance_canvas'): return
        self.importance_figure.clear(); ax=self.importance_figure.add_subplot(111)
        if importances is None or feature_names is None or len(importances)!=len(feature_names):
            ax.text(0.5,0.5,"重要性不可用",ha='center',va='center',transform=ax.transAxes,fontsize=10)
            ax.set_title("特征重要性"); ax.set_xlabel(""); ax.set_ylabel("")
        else:
            idx=np.argsort(importances)[::-1]; n_show=min(20,len(feature_names))
            feats=[feature_names[i] for i in idx[:n_show]]; imps=importances[idx[:n_show]]; y_pos=np.arange(len(feats))
            ax.barh(y_pos,imps,align='center'); ax.set_yticks(y_pos); ax.set_yticklabels(feats,fontsize=8)
            ax.invert_yaxis(); ax.set_xlabel('重要性'); ax.set_title(f'特征重要性 (Top {n_show})')
            try: self.importance_figure.tight_layout()
            except Exception as e: print(f"Warn: tight_layout fail: {e}")
        self.importance_canvas.draw()

# =============================================================================
# Application Entry Point
# =============================================================================
if __name__ == '__main__': # (Code unchanged)
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'): QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'): QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    window = MLClientApp()
    window.show()
    sys.exit(app.exec())