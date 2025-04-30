# -*- coding: utf-8 -*-
import sys
import pandas as pd
import numpy as np
import traceback
import joblib # For model saving/loading
import io # Moved import to top - Used for DataFrame.info redirection
import datetime # For default save filenames

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFileDialog, QTableView, QListWidget, QSplitter,
    QListWidgetItem, QComboBox, QStackedWidget, QStatusBar, QDialog,
    QMenuBar, QSizePolicy, QSpacerItem, QAbstractItemView, QCheckBox,
    QGroupBox, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit,
    QMessageBox, QTabWidget, QHeaderView, QStyleOptionButton, QStyle,
    QProgressDialog, QScrollArea
)
from PyQt6.QtGui import (
    QAction, QIcon, QPalette, QColor, QFont, QPainter, QStandardItemModel,
    QStandardItem, QActionGroup
)
from PyQt6.QtCore import (
    Qt, QAbstractTableModel, QModelIndex, QVariant, pyqtSignal, QThread,
    QSize, QObject, QTimer
)

# --- Icon Library ---
try:
    import qtawesome as qta
    QTA_LOADED = True
except ImportError:
    print("Warning: qtawesome not found. Falling back to standard icons. "
          "Install with: pip install qtawesome")
    QTA_LOADED = False

# --- Matplotlib Embedding ---
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
# from matplotlib.cm import get_cmap # get_cmap is deprecated, use plt.get_cmap

# --- ML Libraries ---
from sklearn.model_selection import train_test_split, cross_val_score # Added cross_val_score (though not fully implemented in training yet)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             r2_score, mean_absolute_error, mean_squared_error, roc_auc_score)
                             # Removed confusion_matrix, roc_curve
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, OrdinalEncoder # Added preprocessors
from sklearn.impute import SimpleImputer # Added imputer
from sklearn.compose import ColumnTransformer # For applying different transforms (conceptually useful)
from sklearn.pipeline import Pipeline # For structured preprocessing (conceptually useful)
from scipy.stats import spearmanr
# Optional: Only import if installed and used
try: import lightgbm as lgb
except ImportError: lgb = None; print("Warning: lightgbm not installed.")
try: import xgboost as xgb
except ImportError: xgb = None; print("Warning: xgboost not installed.")

# --- Constants ---
APP_NAME = "智能机器学习分析平台"
DEFAULT_THEME = "light"
VERSION = "0.3.2" # Incremented version (removed plots)
MAX_PREVIEW_ROWS = 500 # Limit rows shown in preview tables

# =============================================================================
# Helper Classes and Functions
# =============================================================================

class PandasModel(QAbstractTableModel):
    """ A model to interface a Pandas DataFrame with QTableView. """
    def __init__(self, dataframe: pd.DataFrame = None, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._dataframe = dataframe if dataframe is not None else pd.DataFrame()

    def rowCount(self, parent=QModelIndex()) -> int:
        if not parent.isValid(): return min(MAX_PREVIEW_ROWS, len(self._dataframe)) # Limit rows for performance
        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        if not parent.isValid(): return len(self._dataframe.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount()):
            return QVariant()
        try:
            value = self._dataframe.iloc[index.row(), index.column()]
        except IndexError:
             print(f"Warning: IndexError accessing data at {index.row()}, {index.column()}")
             return QVariant()

        if role == Qt.ItemDataRole.DisplayRole:
            if pd.isna(value): return QVariant("NaN")
            if isinstance(value, (float, np.floating)):
                if np.isinf(value): return QVariant("Inf")
                return QVariant(f"{value:.4f}")
            return QVariant(str(value))
        elif role == Qt.ItemDataRole.ToolTipRole:
            return QVariant(str(value))
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if isinstance(value, (int, float, np.number)) and not pd.isna(value):
                 return QVariant(int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))
            else:
                 return QVariant(int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))
        return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if 0 <= section < len(self._dataframe.columns): return QVariant(str(self._dataframe.columns[section]))
            if orientation == Qt.Orientation.Vertical:
                if self._dataframe.index.name:
                     if 0 <= section < self.rowCount(): return QVariant(str(self._dataframe.index[section]))
                return QVariant(str(section + 1))
        return QVariant()

    def get_dataframe(self): return self._dataframe

    def update_dataframe(self, new_dataframe: pd.DataFrame = None):
        self.beginResetModel()
        self._dataframe = new_dataframe if new_dataframe is not None else pd.DataFrame()
        self.endResetModel()
        if not self._dataframe.empty:
            print(f"PandasModel updated. Displaying {self.rowCount()} of {len(self._dataframe)} rows.")


class Worker(QThread):
    """ Generic worker thread for long-running tasks with progress dialog support """
    finished = pyqtSignal(object)
    error = pyqtSignal(tuple)
    progress = pyqtSignal(int) # Emit percentage progress
    status_update = pyqtSignal(str) # Emit text status updates

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func; self.args = args; self.kwargs = kwargs
        self._is_running = True

    def run(self):
        try:
            result = self.func(self.progress, self.status_update, *self.args, **self.kwargs)
            if self._is_running:
                self.finished.emit(result)
        except Exception as e:
            if self._is_running:
                exc_type, exc_value, tb = sys.exc_info()
                tb_str = "".join(traceback.format_exception(exc_type, exc_value, tb))
                self.error.emit((exc_type, exc_value, tb_str))

    def stop(self):
        self._is_running = False
        self.status_update.emit("操作已取消...")


def get_icon(name, fallback_name=None, color=None, color_disabled=None):
    """ Helper to get qtawesome icon or fallback """
    if QTA_LOADED:
        try:
            options = {}
            if color: options['color'] = color
            if color_disabled: options['color_disabled'] = color_disabled
            return qta.icon(name, **options)
        except Exception as e:
            print(f"Warning: qtawesome icon '{name}' failed: {e}")
    if fallback_name:
        try:
            style = QApplication.style()
            pixmap_enum = getattr(QStyle.StandardPixmap, fallback_name, None)
            if pixmap_enum:
                return style.standardIcon(pixmap_enum)
        except Exception:
            pass
    return QIcon()

# =============================================================================
# Main Application Window
# =============================================================================

class MLClientApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}"); self.setGeometry(50, 50, 1400, 850)
        # Data & State
        self.dataframe = None
        self.processed_dataframe = None
        self.preprocessor = None
        self.current_file_path = None; self.feature_cols = []; self.target_col = None
        self.model = None;
        self.X_test_data_processed = None; self.y_test_data = None
        self.predictions = None; self.model_type = None; self.trained_feature_names = None
        self.current_theme = DEFAULT_THEME; self.progress_dialog = None
        self.theme_icon_color = 'gray'; self.theme_icon_color_disabled = 'darkGray'

        # UI Setup
        self.central_widget = QWidget(); self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)
        self._create_menu_bar(); self._create_left_nav_bar(); self._create_main_panel(); self._create_status_bar()
        self.set_theme(self.current_theme)
        self.main_layout.addWidget(self.left_nav_widget, 1); self.main_layout.addWidget(self.main_stack, 5)
        self.main_stack.setCurrentIndex(0); self.update_nav_selection(0); self._update_ui_state()

    # --- Theme and Style ---
    def set_theme(self, theme_name="light"):
        self.current_theme = theme_name; app = QApplication.instance()
        light_palette = QPalette(); dark_palette = QPalette()
        # Define dark palette
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
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

        # Base Font
        font = QFont("Segoe UI", 10);
        if sys.platform == "darwin": font = QFont("San Francisco", 14)
        elif sys.platform.startswith("linux"): font = QFont("Noto Sans", 11)
        app.setFont(font)

        if theme_name == "dark":
            app.setPalette(dark_palette)
            self.theme_icon_color = "#e0e0e0"; self.theme_icon_color_disabled = "#888888"
            plt.style.use('dark_background')
            # More detailed dark QSS
            app.setStyleSheet("""
                QMainWindow { background-color: #353535; }
                QDialog { background-color: #353535; }
                QWidget { color: #e0e0e0; background-color: #353535; border: none;} /* Base for most widgets */
                QScrollArea { background-color: transparent; border: none; } /* Make scroll area background transparent */
                QMenuBar { background-color: #2a2a2a; color: #e0e0e0; border-bottom: 1px solid #4a4a4a;}
                QMenuBar::item { padding: 4px 10px; background-color: transparent; }
                QMenuBar::item:selected { background-color: #5A5A5A; }
                QMenu { background-color: #3c3c3c; color: #e0e0e0; border: 1px solid #5A5A5A; padding: 4px;}
                QMenu::item { padding: 5px 25px; }
                QMenu::item:selected { background-color: #4a90e2; color: white; } /* Use highlight color */
                QMenu::separator { height: 1px; background-color: #5A5A5A; margin: 4px 0;}
                QStatusBar { background-color: #2a2a2a; color: #cccccc; border-top: 1px solid #4a4a4a;}
                QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                    background-color: #232323; color: #e0e0e0; border: 1px solid #5A5A5A;
                    border-radius: 4px; padding: 5px; /* Increased padding */
                }
                QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                    border: 1px solid #4a90e2; /* Highlight border on focus */
                }
                QLineEdit:read-only, QTextEdit:read-only { background-color: #404040; color: #bbbbbb;}
                QPushButton {
                    background-color: #4a4a4a; color: #e0e0e0; border: 1px solid #5a5a5a;
                    padding: 6px 12px; border-radius: 4px; min-height: 28px;
                }
                QPushButton:hover { background-color: #5a5a5a; border-color: #6a6a6a;}
                QPushButton:pressed { background-color: #3a3a3a; }
                QPushButton:checked { background-color: #4a90e2; border-color: #3173ba; color: white; font-weight: bold; }
                QPushButton:disabled { background-color: #404040; color: #888888; border-color: #505050; }
                QTableView {
                    background-color: #2c2c2c; color: #e0e0e0; alternate-background-color: #353535;
                    gridline-color: #4a4a4a; border: 1px solid #4a4a4a;
                    selection-background-color: #4a90e2; selection-color: white;
                }
                QHeaderView::section {
                    background-color: #4a4a4a; color: #e0e0e0; padding: 5px; border: 1px solid #5a5a5a; border-bottom: 2px solid #6a6a6a;
                }
                QListWidget { background-color: #2c2c2c; color: #e0e0e0; border: 1px solid #4a4a4a; }
                QListWidget::item { padding: 4px; }
                QListWidget::item:selected { background-color: #4a90e2; color: white; }
                QGroupBox {
                    color: #e0e0e0; border: 1px solid #4a4a4a; border-radius: 4px; margin-top: 15px; padding: 10px 5px 5px 5px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; left: 10px; color: #cccccc;
                }
                QTabWidget::pane { border: 1px solid #4a4a4a; border-top: none; background-color: #353535;}
                QTabBar::tab {
                    background-color: #4a4a4a; color: #cccccc; padding: 8px 20px; margin-right: 1px;
                    border: 1px solid #4a4a4a; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px;
                }
                QTabBar::tab:selected { background-color: #353535; color: #4a90e2; font-weight: bold; border-color: #4a4a4a; }
                QTabBar::tab:!selected:hover { background-color: #5a5a5a; color: white; }
                QSplitter::handle { background-color: #4a4a4a; height: 1px; width: 1px;}
                QSplitter::handle:horizontal { width: 1px; }
                QSplitter::handle:vertical { height: 1px; }
                QCheckBox { spacing: 5px; } QCheckBox::indicator { width: 15px; height: 15px; }
                QCheckBox::indicator:unchecked { border: 1px solid #5A5A5A; background-color: #232323; border-radius: 3px;}
                QCheckBox::indicator:checked { background-color: #4a90e2; border: 1px solid #3173ba; border-radius: 3px; image: none; } /* Add checkmark image if desired */
                /* Custom Nav Bar Dark */
                QWidget#LeftNavBar { background-color: #2a2a2a; border-right: 1px solid #4a4a4a;}
                QWidget#LeftNavBar QPushButton {
                    background-color: transparent; border: none; color: #cccccc; text-align: left;
                    padding: 8px 0px 8px 20px; border-radius: 4px; margin: 2px 5px; /* Add margin */
                }
                QWidget#LeftNavBar QPushButton:checked { background-color: #4a90e2; color: white; font-weight: bold; }
                QWidget#LeftNavBar QPushButton:hover:!checked { background-color: #3a3a3a; color: white; }
            """)
        else: # Light Theme
            app.setPalette(light_palette)
            self.theme_icon_color = "#333333"; self.theme_icon_color_disabled = "#aaaaaa"
            plt.style.use('default')
            # More detailed light QSS
            app.setStyleSheet("""
                QMainWindow { background-color: #ffffff; }
                QDialog { background-color: #ffffff; }
                QWidget { background-color: #ffffff; border: none;}
                QScrollArea { background-color: transparent; border: none; }
                QMenuBar { background-color: #f0f0f0; color: #333333; border-bottom: 1px solid #cccccc;}
                QMenuBar::item { padding: 4px 10px; background-color: transparent; }
                QMenuBar::item:selected { background-color: #dddddd; }
                QMenu { background-color: #ffffff; color: #333333; border: 1px solid #cccccc; padding: 4px;}
                QMenu::item { padding: 5px 25px; }
                QMenu::item:selected { background-color: #4a90e2; color: white; }
                QMenu::separator { height: 1px; background-color: #cccccc; margin: 4px 0;}
                QStatusBar { background-color: #f0f0f0; color: #555555; border-top: 1px solid #cccccc;}
                QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                    background-color: #ffffff; color: #333333; border: 1px solid #cccccc;
                    border-radius: 4px; padding: 5px;
                }
                QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                    border: 1px solid #4a90e2;
                }
                QLineEdit:read-only, QTextEdit:read-only { background-color: #f5f5f5; color: #777777;}
                QPushButton {
                    background-color: #f0f0f0; color: #333333; border: 1px solid #cccccc;
                    padding: 6px 12px; border-radius: 4px; min-height: 28px;
                }
                QPushButton:hover { background-color: #e0e0e0; border-color: #bbbbbb;}
                QPushButton:pressed { background-color: #d0d0d0; }
                QPushButton:checked { background-color: #4a90e2; border-color: #3173ba; color: white; font-weight: bold; }
                QPushButton:disabled { background-color: #e8e8e8; color: #aaaaaa; border-color: #d8d8d8; }
                QTableView {
                    background-color: #ffffff; color: #333333; alternate-background-color: #f8f8f8;
                    gridline-color: #e0e0e0; border: 1px solid #cccccc;
                    selection-background-color: #4a90e2; selection-color: white;
                }
                QHeaderView::section {
                    background-color: #f0f0f0; color: #333333; padding: 5px; border: 1px solid #cccccc; border-bottom: 2px solid #bbbbbb;
                }
                QListWidget { background-color: #ffffff; color: #333333; border: 1px solid #cccccc; }
                QListWidget::item { padding: 4px; }
                QListWidget::item:selected { background-color: #4a90e2; color: white; }
                QGroupBox {
                    color: #333333; border: 1px solid #cccccc; border-radius: 4px; margin-top: 15px; padding: 10px 5px 5px 5px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; left: 10px; color: #555555;
                }
                QTabWidget::pane { border: 1px solid #cccccc; border-top: none; background-color: #ffffff;}
                QTabBar::tab {
                    background-color: #f0f0f0; color: #555555; padding: 8px 20px; margin-right: 1px;
                    border: 1px solid #cccccc; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px;
                }
                QTabBar::tab:selected { background-color: #ffffff; color: #4a90e2; font-weight: bold; border-color: #cccccc; }
                QTabBar::tab:!selected:hover { background-color: #e0e0e0; color: #333333; }
                QSplitter::handle { background-color: #cccccc; height: 1px; width: 1px;}
                QSplitter::handle:horizontal { width: 1px; }
                QSplitter::handle:vertical { height: 1px; }
                QCheckBox { spacing: 5px; } QCheckBox::indicator { width: 15px; height: 15px; }
                QCheckBox::indicator:unchecked { border: 1px solid #cccccc; background-color: #ffffff; border-radius: 3px;}
                QCheckBox::indicator:checked { background-color: #4a90e2; border: 1px solid #3173ba; border-radius: 3px; /* Add checkmark image here */}
                /* Custom Nav Bar Light */
                QWidget#LeftNavBar { background-color: #e8e8e8; border-right: 1px solid #cccccc;}
                QWidget#LeftNavBar QPushButton {
                    background-color: transparent; border: none; color: #333333; text-align: left;
                    padding: 8px 0px 8px 20px; border-radius: 4px; margin: 2px 5px;
                }
                QWidget#LeftNavBar QPushButton:checked { background-color: #4a90e2; color: white; font-weight: bold; }
                QWidget#LeftNavBar QPushButton:hover:!checked { background-color: #d8d8d8; color: #111111; }
            """)

        self._update_icons()
        self.update()

    def _get_themed_icon(self, name, fallback_name):
         """ Gets icon with current theme colors """
         return get_icon(name, fallback_name, color=self.theme_icon_color, color_disabled=self.theme_icon_color_disabled)

    def _update_icons(self):
        """ Update icons using qtawesome with theme colors """
        # --- Menu Actions ---
        if hasattr(self, 'open_action'): self.open_action.setIcon(self._get_themed_icon('fa5s.folder-open', 'SP_DialogOpenButton'))
        if hasattr(self, 'save_model_action'): self.save_model_action.setIcon(self._get_themed_icon('fa5s.save', 'SP_DialogSaveButton'))
        if hasattr(self, 'load_model_action'): self.load_model_action.setIcon(self._get_themed_icon('fa5s.folder', 'SP_DialogOpenButton'))
        if hasattr(self, 'exit_action'): self.exit_action.setIcon(self._get_themed_icon('fa5s.times-circle', 'SP_DialogCloseButton'))

        # --- Nav Buttons ---
        if hasattr(self, 'nav_buttons'):
            self.nav_buttons["import"].setIcon(self._get_themed_icon('fa5s.file-import', 'SP_FileIcon'))
            self.nav_buttons["preview"].setIcon(self._get_themed_icon('fa5s.table', 'SP_FileDialogDetailedView'))
            self.nav_buttons["preprocess"].setIcon(self._get_themed_icon('fa5s.cogs', 'SP_ComputerIcon'))
            self.nav_buttons["config"].setIcon(self._get_themed_icon('fa5s.sliders-h', 'SP_FileDialogContentsView'))
            self.nav_buttons["model"].setIcon(self._get_themed_icon('fa5s.brain', 'SP_ComputerIcon'))
            self.nav_buttons["results"].setIcon(self._get_themed_icon('fa5s.chart-bar', 'SP_MediaPlay')) # Keep chart icon for general results

        # --- Buttons (Examples) ---
        if hasattr(self, 'load_button_welcome'): self.load_button_welcome.setIcon(self._get_themed_icon('fa5s.folder-open', 'SP_DialogOpenButton'))
        if hasattr(self, 'apply_preprocess_button'): self.apply_preprocess_button.setIcon(self._get_themed_icon('fa5s.play', 'SP_DialogApplyButton'))
        if hasattr(self, 'train_button'): self.train_button.setIcon(self._get_themed_icon('fa5s.play-circle', 'SP_MediaPlay'))


    # --- UI Creation Methods ---
    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        # File Menu
        file_menu = menu_bar.addMenu("文件 (&F)")
        self.open_action = QAction("打开文件 (&O)...", self)
        self.open_action.triggered.connect(self.load_data_dialog)
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        self.exit_action = QAction("退出 (&X)", self)
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        # Model Menu
        model_menu = menu_bar.addMenu("模型 (&M)")
        self.save_model_action = QAction("保存模型 (&S)...", self)
        self.save_model_action.triggered.connect(self.save_model_dialog)
        model_menu.addAction(self.save_model_action)
        self.load_model_action = QAction("加载模型 (&L)...", self)
        self.load_model_action.triggered.connect(self.load_model_dialog)
        model_menu.addAction(self.load_model_action)
        # View Menu (Theme selection)
        view_menu = menu_bar.addMenu("视图 (&V)")
        theme_menu = view_menu.addMenu("主题 (&T)")
        self.light_theme_action = QAction("浅色", self, checkable=True)
        self.light_theme_action.setChecked(self.current_theme == "light")
        self.light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        self.dark_theme_action = QAction("深色", self, checkable=True)
        self.dark_theme_action.setChecked(self.current_theme == "dark")
        self.dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_group = QActionGroup(self)
        theme_group.addAction(self.light_theme_action)
        theme_group.addAction(self.dark_theme_action)
        theme_group.setExclusive(True)
        theme_menu.addAction(self.light_theme_action)
        theme_menu.addAction(self.dark_theme_action)
        # Help Menu
        help_menu = menu_bar.addMenu("帮助 (&H)")
        about_action = QAction("关于 (&A)...", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        # Initial state for model menu items
        self.save_model_action.setEnabled(False)
        self.load_model_action.setEnabled(True)

    def _create_left_nav_bar(self):
        self.left_nav_widget = QWidget()
        self.left_nav_layout = QVBoxLayout(self.left_nav_widget)
        self.left_nav_layout.setContentsMargins(5, 10, 5, 10)
        self.left_nav_layout.setSpacing(6)
        self.left_nav_widget.setObjectName("LeftNavBar")
        self.left_nav_widget.setFixedWidth(200)
        self.nav_buttons = {}
        nav_items = [("import", "数据导入"), ("preview", "数据预览"), ("preprocess", "数据预处理"),
                     ("config", "变量配置"), ("model", "模型配置"), ("results", "结果分析")]
        for i, (key, text) in enumerate(nav_items):
            button = QPushButton(f"  {text}")
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.clicked.connect(lambda checked=False, index=i: self.switch_main_panel(index))
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            button.setFixedHeight(42)
            self.nav_buttons[key] = button
            self.left_nav_layout.addWidget(button)
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.left_nav_layout.addItem(spacer)

    def _create_main_panel(self):
        self.main_stack = QStackedWidget()
        self.main_stack.setContentsMargins(15, 15, 15, 15)
        # Create Pages
        self.page_welcome = self._create_welcome_page()
        self.page_preview = self._create_preview_page()
        self.page_preprocess = self._create_preprocess_page()
        self.page_config = self._create_config_page()
        self.page_model = self._create_model_page()
        self.page_results = self._create_results_page() # Updated results page creation
        # Add Pages in order
        self.main_stack.addWidget(self.page_welcome)   # 0
        self.main_stack.addWidget(self.page_preview)  # 1
        self.main_stack.addWidget(self.page_preprocess)# 2
        self.main_stack.addWidget(self.page_config)   # 3
        self.main_stack.addWidget(self.page_model)    # 4
        self.main_stack.addWidget(self.page_results)  # 5

    def _create_welcome_page(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label = QLabel();
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label = QLabel(f"{APP_NAME}"); font = welcome_label.font(); font.setPointSize(24); font.setBold(True); welcome_label.setFont(font); welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label = QLabel("开始您的机器学习之旅。\n请通过菜单或下方按钮导入数据 (CSV/XLSX)。"); instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter); instruction_label.setWordWrap(True)
        self.load_button_welcome = QPushButton(" 选择数据文件..."); self.load_button_welcome.clicked.connect(self.load_data_dialog); self.load_button_welcome.setMinimumWidth(180)
        layout.addStretch(1); layout.addWidget(icon_label); layout.addSpacing(15); layout.addWidget(welcome_label); layout.addWidget(instruction_label); layout.addSpacing(30)
        layout.addWidget(self.load_button_welcome, 0, Qt.AlignmentFlag.AlignCenter); layout.addStretch(2);
        # Set initial icon
        icon = self._get_themed_icon('fa5s.rocket', 'SP_ComputerIcon')
        if not icon.isNull(): icon_label.setPixmap(icon.pixmap(QSize(64, 64)))
        return page

    def _create_preview_page(self):
        page = QWidget(); layout = QVBoxLayout(page)
        top_layout = QHBoxLayout(); self.preview_label = QLabel("数据预览: (未加载)"); font = self.preview_label.font(); font.setBold(True); self.preview_label.setFont(font)
        self.rows_cols_label = QLabel(""); top_layout.addWidget(self.preview_label); top_layout.addStretch(1); top_layout.addWidget(self.rows_cols_label); layout.addLayout(top_layout)
        self.preview_table = QTableView(); self.preview_table.setAlternatingRowColors(True); self.preview_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.preview_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); header = self.preview_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive); self.preview_table.verticalHeader().setVisible(True); self.preview_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.preview_model = PandasModel(None); self.preview_table.setModel(self.preview_model); layout.addWidget(self.preview_table); return page

    def _create_preprocess_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.addWidget(QLabel("<h2>数据预处理</h2>"))

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Side: Data Info and Column Selection
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("<b>数据信息概览:</b>"))
        self.data_info_display = QTextEdit()
        self.data_info_display.setReadOnly(True)
        self.data_info_display.setFontFamily("monospace")
        self.data_info_display.setFixedHeight(200)
        left_layout.addWidget(self.data_info_display)

        left_layout.addWidget(QLabel("<b>选择要处理的列:</b> (按住Ctrl/Shift多选)"))
        self.preprocess_col_list = QListWidget()
        self.preprocess_col_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        left_layout.addWidget(self.preprocess_col_list)
        splitter.addWidget(left_widget)

        # Right Side: Preprocessing Steps (Scrollable)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # --- Imputation ---
        impute_group = QGroupBox("缺失值处理")
        impute_form = QFormLayout(impute_group)
        self.impute_strategy_combo = QComboBox()
        self.impute_strategy_combo.addItems(["不处理", "均值 (Mean)", "中位数 (Median)", "众数 (Most Frequent)", "常量 (Constant)"])
        self.impute_constant_value = QLineEdit("0")
        self.impute_constant_value.setEnabled(False)
        self.impute_strategy_combo.currentTextChanged.connect(lambda text: self.impute_constant_value.setEnabled(text == "常量 (Constant)"))
        impute_form.addRow("填充策略:", self.impute_strategy_combo)
        impute_form.addRow("常量值:", self.impute_constant_value)
        right_layout.addWidget(impute_group)

        # --- Scaling ---
        scale_group = QGroupBox("特征缩放 (数值列)")
        scale_form = QFormLayout(scale_group)
        self.scale_strategy_combo = QComboBox()
        self.scale_strategy_combo.addItems(["不处理", "标准化 (StandardScaler)", "归一化 (MinMaxScaler)"])
        scale_form.addRow("缩放方法:", self.scale_strategy_combo)
        right_layout.addWidget(scale_group)

        # --- Encoding ---
        encode_group = QGroupBox("类别特征编码")
        encode_form = QFormLayout(encode_group)
        self.encode_strategy_combo = QComboBox()
        self.encode_strategy_combo.addItems(["不处理", "独热编码 (One-Hot)", "序号编码 (Ordinal)"])
        encode_form.addRow("编码方法:", self.encode_strategy_combo)
        right_layout.addWidget(encode_group)

        right_layout.addStretch(1)
        scroll_area.setWidget(right_widget)
        splitter.addWidget(scroll_area)

        main_layout.addWidget(splitter)

        # Action Button
        self.apply_preprocess_button = QPushButton(" 应用预处理步骤")
        self.apply_preprocess_button.clicked.connect(self.run_preprocessing)
        main_layout.addWidget(self.apply_preprocess_button, 0, Qt.AlignmentFlag.AlignRight)

        splitter.setSizes([350, 450])
        return page


    def _create_config_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        config_label = QLabel("<h2>变量配置</h2>")
        config_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        main_layout.addWidget(config_label)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Available Columns ---
        vbox_avail = QWidget(); layout_avail = QVBoxLayout(vbox_avail)
        layout_avail.addWidget(QLabel("<b>可用列:</b>")); self.avail_cols_list = QListWidget(); self.avail_cols_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection); layout_avail.addWidget(self.avail_cols_list)
        splitter.addWidget(vbox_avail)

        # --- Buttons ---
        vbox_buttons = QWidget(); layout_buttons = QVBoxLayout(vbox_buttons); layout_buttons.addStretch(1)
        self.add_feature_button = QPushButton(">>\n添加特征"); self.add_feature_button.setToolTip("将选中的可用列添加为特征变量"); self.add_feature_button.clicked.connect(self.add_features)
        self.remove_feature_button = QPushButton("<<\n移除特征"); self.remove_feature_button.setToolTip("将选中的特征变量移回可用列"); self.remove_feature_button.clicked.connect(self.remove_features)
        self.set_target_button = QPushButton(" > \n设为目标"); self.set_target_button.setToolTip("将选中的可用列设为目标变量"); self.set_target_button.clicked.connect(self.set_target)
        self.clear_target_button = QPushButton(" < \n清除目标"); self.clear_target_button.setToolTip("清除当前目标变量"); self.clear_target_button.clicked.connect(self.clear_target)
        layout_buttons.addWidget(self.add_feature_button); layout_buttons.addSpacing(10); layout_buttons.addWidget(self.remove_feature_button); layout_buttons.addSpacing(20)
        layout_buttons.addWidget(self.set_target_button); layout_buttons.addSpacing(10); layout_buttons.addWidget(self.clear_target_button); layout_buttons.addStretch(1)
        vbox_buttons.setFixedWidth(120)
        splitter.addWidget(vbox_buttons)

        # --- Selected Columns ---
        vbox_selected = QWidget(); layout_selected = QVBoxLayout(vbox_selected)
        layout_selected.addWidget(QLabel("<b>特征变量 (Features):</b>")); self.feature_cols_list = QListWidget(); self.feature_cols_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection); layout_selected.addWidget(self.feature_cols_list)
        layout_selected.addSpacing(10); layout_selected.addWidget(QLabel("<b>目标变量 (Target):</b>")); self.target_col_label = QLabel("<i>(未选择)</i>"); self.target_col_label.setFrameShape(QLabel.Shape.StyledPanel); self.target_col_label.setFrameShadow(QLabel.Shadow.Sunken)
        self.target_col_label.setMinimumHeight(30); self.target_col_label.setAlignment(Qt.AlignmentFlag.AlignCenter); layout_selected.addWidget(self.target_col_label)
        splitter.addWidget(vbox_selected)

        main_layout.addWidget(splitter)
        splitter.setSizes([350, 120, 350])
        return page


    def _create_model_page(self):
        page = QWidget(); layout = QVBoxLayout(page)
        layout.addWidget(QLabel("<h2>模型选择与配置</h2>"))

        # Algorithm Selection
        algo_layout = QHBoxLayout(); algo_layout.addWidget(QLabel("选择算法:"))
        self.algo_combo = QComboBox()
        algo_items = ["随机森林", "神经网络(MLP)"]
        if lgb: algo_items.append("LightGBM")
        if xgb: algo_items.append("XGBoost")
        self.algo_combo.addItems(algo_items)
        algo_layout.addWidget(self.algo_combo, 1); layout.addLayout(algo_layout)

        # --- Dynamic Parameter Area ---
        self.param_stack = QStackedWidget()
        self.param_widgets = {
            "随机森林": self._create_rf_params(),
            "神经网络(MLP)": self._create_mlp_params(),
        }
        if lgb: self.param_widgets["LightGBM"] = self._create_lgbm_params()
        if xgb: self.param_widgets["XGBoost"] = self._create_xgb_params()

        for widget in self.param_widgets.values(): self.param_stack.addWidget(widget)
        self.algo_combo.currentTextChanged.connect(self.switch_param_widget)
        layout.addWidget(self.param_stack)

        # --- Cross-Validation Option ---
        cv_group = QGroupBox("交叉验证设置 (可选)")
        cv_layout = QHBoxLayout(cv_group)
        self.cv_checkbox = QCheckBox("使用交叉验证")
        self.cv_folds_spinbox = QSpinBox()
        self.cv_folds_spinbox.setRange(2, 20); self.cv_folds_spinbox.setValue(5); self.cv_folds_spinbox.setEnabled(False)
        self.cv_checkbox.toggled.connect(self.cv_folds_spinbox.setEnabled)
        cv_layout.addWidget(self.cv_checkbox); cv_layout.addWidget(QLabel("折数 (K):")); cv_layout.addWidget(self.cv_folds_spinbox); cv_layout.addStretch()
        layout.addWidget(cv_group)

        layout.addStretch(1)
        # Train Button
        self.train_button = QPushButton(" 开始训练模型")
        self.train_button.clicked.connect(self.run_training); layout.addWidget(self.train_button)
        self.switch_param_widget(self.algo_combo.currentText())
        return page

    # --- Parameter Widget Creation Methods ---
    def _create_rf_params(self):
        widget = QWidget(); layout = QFormLayout(widget); widget.setObjectName("param_rf")
        n_est = QSpinBox(); n_est.setRange(10, 5000); n_est.setValue(100); layout.addRow("树的数量 (n_estimators):", n_est)
        max_d = QSpinBox(); max_d.setRange(-1, 100); max_d.setValue(-1); max_d.setSpecialValueText("无限制 (-1)"); layout.addRow("最大深度 (max_depth):", max_d)
        min_s_split = QSpinBox(); min_s_split.setRange(2, 100); min_s_split.setValue(2); layout.addRow("最小分裂样本数 (min_samples_split):", min_s_split)
        min_s_leaf = QSpinBox(); min_s_leaf.setRange(1, 100); min_s_leaf.setValue(1); layout.addRow("最小叶子样本数 (min_samples_leaf):", min_s_leaf)
        criterion_c = QComboBox(); criterion_c.addItems(["gini", "entropy", "log_loss"]); layout.addRow("分类标准 (criterion):", criterion_c)
        criterion_r = QComboBox(); criterion_r.addItems(["squared_error", "absolute_error", "friedman_mse", "poisson"]); layout.addRow("回归标准 (criterion):", criterion_r)
        widget.setProperty("get_params", lambda model_type: {
            'n_estimators': n_est.value(), 'max_depth': max_d.value() if max_d.value()!=-1 else None,
            'min_samples_split': min_s_split.value(), 'min_samples_leaf': min_s_leaf.value(),
            'criterion': criterion_c.currentText() if model_type == 'classification' else criterion_r.currentText()
        })
        return widget

    def _create_mlp_params(self):
        widget = QWidget(); layout = QFormLayout(widget); widget.setObjectName("param_mlp")
        hidden_layers = QLineEdit("64, 32"); layout.addRow("隐藏层大小 (例: 64, 32):", hidden_layers)
        activation = QComboBox(); activation.addItems(["relu", "tanh", "logistic", "identity"]); activation.setCurrentText("relu"); layout.addRow("激活函数 (activation):", activation)
        solver = QComboBox(); solver.addItems(["adam", "sgd", "lbfgs"]); solver.setCurrentText("adam"); layout.addRow("优化器 (solver):", solver)
        alpha = QDoubleSpinBox(); alpha.setDecimals(5); alpha.setRange(0.0, 1.0); alpha.setSingleStep(0.0001); alpha.setValue(0.0001); layout.addRow("L2正则化 (alpha):", alpha)
        max_iter = QSpinBox(); max_iter.setRange(50, 2000); max_iter.setValue(500); layout.addRow("最大迭代次数 (max_iter):", max_iter)
        widget.setProperty("get_params", lambda model_type: {
            'hidden_layer_sizes': tuple(map(int, hidden_layers.text().replace(' ','').split(','))) if hidden_layers.text() else (100,),
            'activation': activation.currentText(), 'solver': solver.currentText(), 'alpha': alpha.value(), 'max_iter': max_iter.value()
        })
        return widget

    def _create_lgbm_params(self):
        widget = QWidget(); layout = QFormLayout(widget); widget.setObjectName("param_lgbm")
        n_est = QSpinBox(); n_est.setRange(10, 5000); n_est.setValue(100); layout.addRow("迭代次数 (n_estimators):", n_est)
        lr = QDoubleSpinBox(); lr.setDecimals(4); lr.setRange(0.0001, 1.0); lr.setSingleStep(0.01); lr.setValue(0.1); layout.addRow("学习率 (learning_rate):", lr)
        max_d = QSpinBox(); max_d.setRange(-1, 100); max_d.setValue(-1); max_d.setSpecialValueText("无限制 (-1)"); layout.addRow("最大深度 (max_depth):", max_d)
        num_leaves = QSpinBox(); num_leaves.setRange(2, 1000); num_leaves.setValue(31); layout.addRow("叶子节点数 (num_leaves):", num_leaves)
        widget.setProperty("get_params", lambda model_type: {
            'n_estimators': n_est.value(), 'learning_rate': lr.value(),
            'max_depth': max_d.value() if max_d.value()!=-1 else -1, 'num_leaves': num_leaves.value()
        })
        return widget

    def _create_xgb_params(self):
        widget = QWidget(); layout = QFormLayout(widget); widget.setObjectName("param_xgb")
        n_est = QSpinBox(); n_est.setRange(10, 5000); n_est.setValue(100); layout.addRow("迭代次数 (n_estimators):", n_est)
        lr = QDoubleSpinBox(); lr.setDecimals(4); lr.setRange(0.0001, 1.0); lr.setSingleStep(0.01); lr.setValue(0.1); layout.addRow("学习率 (eta / learning_rate):", lr)
        max_d = QSpinBox(); max_d.setRange(0, 100); max_d.setValue(6); layout.addRow("最大深度 (max_depth):", max_d)
        subsample = QDoubleSpinBox(); subsample.setRange(0.1, 1.0); subsample.setSingleStep(0.1); subsample.setValue(1.0); layout.addRow("样本采样比 (subsample):", subsample)
        colsample = QDoubleSpinBox(); colsample.setRange(0.1, 1.0); colsample.setSingleStep(0.1); colsample.setValue(1.0); layout.addRow("特征采样比 (colsample_bytree):", colsample)
        widget.setProperty("get_params", lambda model_type: {
            'n_estimators': n_est.value(), 'learning_rate': lr.value(), 'eta': lr.value(),
            'max_depth': max_d.value(), 'subsample': subsample.value(), 'colsample_bytree': colsample.value()
        })
        return widget

    def switch_param_widget(self, algo_name):
        """ Show the parameter widget for the selected algorithm """
        if algo_name in self.param_widgets:
            widget_to_show = self.param_widgets[algo_name]
            self.param_stack.setCurrentWidget(widget_to_show)
        else:
            pass # Silently ignore if widget doesn't exist (shouldn't happen)

    def _create_results_page(self): # Simplified Results Page
        page = QWidget(); layout = QVBoxLayout(page); layout.addWidget(QLabel("<h2>结果分析</h2>"))
        self.results_tabs = QTabWidget()

        # Tab 1: Predictions
        self.tab_predictions = QWidget(); pred_layout = QVBoxLayout(self.tab_predictions); pred_layout.addWidget(QLabel("预测结果预览 (测试集部分样本):")); self.predictions_table = QTableView()
        self.predictions_table.setAlternatingRowColors(True); self.predictions_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); header_pred = self.predictions_table.horizontalHeader()
        header_pred.setSectionResizeMode(QHeaderView.ResizeMode.Interactive); self.prediction_model = PandasModel(None); self.predictions_table.setModel(self.prediction_model); pred_layout.addWidget(self.predictions_table); self.results_tabs.addTab(self.tab_predictions, "预测结果")

        # Tab 2: Evaluation Metrics
        self.tab_metrics = QWidget(); metrics_layout = QVBoxLayout(self.tab_metrics); metrics_layout.addWidget(QLabel("模型评估指标:")); self.metrics_display = QTextEdit(); self.metrics_display.setReadOnly(True); self.metrics_display.setFontFamily("monospace"); metrics_layout.addWidget(self.metrics_display); self.results_tabs.addTab(self.tab_metrics, "评估指标")

        # Tab 3: Feature Importance
        self.tab_importance = QWidget(); importance_layout = QVBoxLayout(self.tab_importance); importance_layout.addWidget(QLabel("特征重要性:"))
        self.importance_figure = Figure(figsize=(7, 5), dpi=100) # Adjusted size
        self.importance_canvas = FigureCanvas(self.importance_figure); importance_layout.addWidget(self.importance_canvas); self.results_tabs.addTab(self.tab_importance, "特征重要性")

        # REMOVED: Confusion Matrix Tab
        # REMOVED: ROC Curve Tab

        layout.addWidget(self.results_tabs)
        return page


    def _create_status_bar(self): self.status_bar = QStatusBar(); self.setStatusBar(self.status_bar); self.status_bar.showMessage("就绪.")

    # --- UI Interaction ---
    def switch_main_panel(self, index):
        if not (0 <= index < self.main_stack.count()): return
        current_data = self.processed_dataframe if self.processed_dataframe is not None else self.dataframe
        can_proceed = True
        required_step = ""
        if index >= 1 and self.dataframe is None:
            can_proceed = False; required_step = "加载数据"
        elif index == 2 and self.dataframe is None:
             can_proceed = False; required_step = "加载数据"
        elif index >= 3 and current_data is None:
            can_proceed = False; required_step = "加载或预处理数据"
        elif index >= 4 and (not self.feature_cols or not self.target_col):
             can_proceed = False; required_step = "配置变量"
        elif index == 5 and self.model is None:
             can_proceed = False; required_step = "训练模型"

        if not can_proceed:
            self.status_bar.showMessage(f"请先完成步骤: {required_step}", 3000)
            current_ui_index = self.main_stack.currentIndex()
            self.update_nav_selection(current_ui_index)
            return

        self.main_stack.setCurrentIndex(index)
        self.update_nav_selection(index)
        self._update_ui_state()

        # Special actions when switching TO a specific page
        if index == 1: # Preview page
            df_to_show = self.processed_dataframe if self.processed_dataframe is not None else self.dataframe
            self.preview_model.update_dataframe(df_to_show)
            if df_to_show is not None:
                 try: self.preview_table.resizeColumnsToContents()
                 except Exception as e: print(f"Warn: resize failed: {e}")
        elif index == 2: # Preprocess page
            self.update_preprocess_info()
        elif index == 3: # Config page
            self.update_config_lists()

    def update_nav_selection(self, index):
        keys = list(self.nav_buttons.keys())
        if 0 <= index < len(keys):
            target_key = keys[index]
            for key, button in self.nav_buttons.items():
                button.blockSignals(True)
                button.setChecked(key == target_key)
                button.blockSignals(False)

    def show_about_dialog(self): QMessageBox.about(self, "关于", f"<h2>{APP_NAME} v{VERSION}</h2><p>一个基于 PyQt6 和 scikit-learn 的机器学习分析平台。</p><p><b>作者:</b> [您的名字/组织]</p><p><b>依赖库:</b> PyQt6, Pandas, NumPy, Scikit-learn, Matplotlib, Joblib, qtawesome (可选), LightGBM (可选), XGBoost (可选)</p>")

    def _update_ui_state(self):
        """ Updates the enabled/disabled state of UI elements based on application state. """
        data_loaded = self.dataframe is not None
        data_available_for_config = self.processed_dataframe if self.processed_dataframe is not None else self.dataframe
        data_ready = data_available_for_config is not None
        vars_configured = data_ready and bool(self.feature_cols) and self.target_col is not None
        model_trained = self.model is not None

        # Menu Items
        self.save_model_action.setEnabled(model_trained)
        self.load_model_action.setEnabled(True)

        # Nav Buttons
        self.nav_buttons["preview"].setEnabled(data_loaded)
        self.nav_buttons["preprocess"].setEnabled(data_loaded)
        self.nav_buttons["config"].setEnabled(data_ready)
        self.nav_buttons["model"].setEnabled(vars_configured)
        self.nav_buttons["results"].setEnabled(model_trained)

        # Preprocess Page
        if hasattr(self, 'apply_preprocess_button'):
            is_processing = hasattr(self, 'preprocess_worker') and self.preprocess_worker and self.preprocess_worker.isRunning()
            self.apply_preprocess_button.setEnabled(data_loaded and not is_processing)

        # Config Page
        config_elements_exist = hasattr(self, 'add_feature_button')
        if config_elements_exist:
            self.add_feature_button.setEnabled(data_ready)
            self.remove_feature_button.setEnabled(data_ready)
            self.set_target_button.setEnabled(data_ready)
            self.clear_target_button.setEnabled(data_ready and self.target_col is not None)

        # Model Page
        if hasattr(self, 'train_button'):
            is_training = hasattr(self, 'train_worker') and self.train_worker and self.train_worker.isRunning()
            self.train_button.setEnabled(vars_configured and not is_training)
            self.train_button.setText("正在训练..." if is_training else " 开始训练模型")

        # Preview Page Labels
        if hasattr(self, 'rows_cols_label') and hasattr(self, 'preview_label'):
            df_to_show = self.processed_dataframe if self.processed_dataframe is not None else self.dataframe
            if df_to_show is not None:
                rows, cols = df_to_show.shape
                limit_msg = f" (显示前 {MAX_PREVIEW_ROWS} 行)" if rows > MAX_PREVIEW_ROWS else ""
                self.rows_cols_label.setText(f"{rows} 行 x {cols} 列{limit_msg}")
                fname = self.current_file_path.split('/')[-1] if self.current_file_path else "数据"
                status = " (已处理)" if self.processed_dataframe is not None else ""
                self.preview_label.setText(f"预览: {fname}{status}")
            else:
                self.rows_cols_label.setText("")
                self.preview_label.setText("预览: (未加载)")

        # Results Page Tabs - REMOVED CM/ROC logic
        # if hasattr(self, 'results_tabs'):
            # No specific tab enabling needed beyond general model_trained state for results nav button


    # --- Progress Dialog Handling ---
    def _start_progress(self, title, max_val=100, worker=None):
        """ Shows a modal progress dialog linked to a worker's signals """
        if self.progress_dialog is None:
            self.progress_dialog = QProgressDialog(title, "取消", 0, max_val, self)
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_dialog.setAutoReset(True)
            self.progress_dialog.setAutoClose(True)
            self.progress_dialog.setValue(0)

            if worker:
                worker.progress.connect(self.progress_dialog.setValue)
                worker.status_update.connect(self.progress_dialog.setLabelText)
                self.progress_dialog.canceled.connect(worker.stop)
                worker.finished.connect(self._finish_progress)
                worker.error.connect(self._finish_progress)
            else:
                print("Warning: Progress dialog started without a worker to connect to.")

            self.progress_dialog.show()
        else:
            self.progress_dialog.setWindowTitle(title)
            self.progress_dialog.setRange(0, max_val)
            self.progress_dialog.setValue(0)

    def _finish_progress(self):
        """ Closes the progress dialog if it exists. """
        if self.progress_dialog is not None:
            self.progress_dialog.close()
            self.progress_dialog = None


    # --- Data Loading ---
    def load_data_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择数据文件", "", "数据 (*.csv *.xlsx *.xls)")
        if not file_path: return
        self.status_bar.showMessage(f"开始加载: {file_path.split('/')[-1]}...")
        self.load_button_welcome.setEnabled(False); self.open_action.setEnabled(False)

        self.load_worker = Worker(self._load_data_thread, file_path)
        self.load_worker.finished.connect(self._on_data_loaded)
        self.load_worker.error.connect(self._on_load_error)
        self.load_worker.finished.connect(self._reset_load_buttons_state)
        self.load_worker.error.connect(self._reset_load_buttons_state)

        self._start_progress(f"加载文件: {file_path.split('/')[-1]}", worker=self.load_worker)
        self.load_worker.start()

    def _reset_load_buttons_state(self):
        """ Re-enables data loading buttons. """
        self.load_button_welcome.setEnabled(True)
        self.open_action.setEnabled(True)

    def _load_data_thread(self, progress_signal, status_signal, file_path):
        status_signal.emit(f"读取: {file_path.split('/')[-1]}...")
        progress_signal.emit(10)
        try:
            ext = file_path.lower().split('.')[-1]
            if ext == 'csv':
                read_func = pd.read_csv
            elif ext in ['xlsx', 'xls']:
                read_func = pd.read_excel
            else:
                raise ValueError(f"不支持的文件类型: {ext}")

            df = read_func(file_path)
            progress_signal.emit(70)

            if df.empty: raise ValueError("文件数据为空.")

            df.columns = df.columns.astype(str)
            if df.columns.duplicated().any():
                status_signal.emit("警告: 检测到重复列名，已自动重命名。")
                # This pandas internal function usage might be brittle across versions.
                # A safer approach might be a custom renaming loop if this causes issues.
                try:
                    # Attempt to use pandas internal function if available
                    from pandas.io.parsers.base_parser import maybe_convert_usecols_to_str
                    df.columns = maybe_convert_usecols_to_str(df.columns, {})
                except (ImportError, AttributeError):
                    # Fallback manual renaming
                    cols = pd.Series(df.columns)
                    for dup in cols[cols.duplicated()].unique():
                        cols[cols[cols == dup].index.values.tolist()] = [dup + '.' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
                    df.columns = cols
                    status_signal.emit("警告: 使用备用方法重命名重复列。")


            progress_signal.emit(90)
            status_signal.emit("文件读取完成.")
            progress_signal.emit(100)
            return df, file_path
        except Exception as e:
            if "No such file or directory" in str(e):
                 raise FileNotFoundError(f"找不到文件: {file_path}")
            elif "requires 'openpyxl'" in str(e):
                 raise ImportError("需要 'openpyxl' 库来读取 XLSX 文件. 请安装: pip install openpyxl")
            elif "requires 'xlrd'" in str(e):
                 raise ImportError("需要 'xlrd' 库来读取旧版 XLS 文件. 请安装: pip install xlrd")
            else:
                 raise RuntimeError(f"加载失败: {e}")

    def _on_data_loaded(self, result):
        df, file_path = result
        self.dataframe = df
        self.processed_dataframe = None
        self.preprocessor = None
        self.current_file_path = file_path
        self.status_bar.showMessage(f"加载成功: {file_path.split('/')[-1]} ({len(df)}x{len(df.columns)})", 5000)

        self._reset_model_state_full()

        self.preview_model.update_dataframe(self.dataframe)
        try: self.preview_table.resizeColumnsToContents()
        except Exception as e: print(f"Warn: resize columns failed: {e}")

        self._update_ui_state()
        self.switch_main_panel(1)

    def _on_load_error(self, error_info):
        exc_type, exc_value, tb_str = error_info
        QMessageBox.critical(self, "加载错误", f"加载文件时出错:\n{exc_value}\n\n详细信息:\n{tb_str}")
        self.status_bar.showMessage("加载失败.", 5000)
        self.dataframe = None
        self.processed_dataframe = None
        self.preprocessor = None
        self.current_file_path = None

        self._reset_model_state_full()
        self.preview_model.update_dataframe(None)
        self.update_preprocess_info()
        self.update_config_lists()
        self._update_ui_state()
        self.switch_main_panel(0)

    def _reset_model_state_full(self):
        """ Resets model, preprocessing info, and variable selections. """
        self._reset_model_state()
        self.feature_cols = []
        self.target_col = None
        self.preprocessor = None
        self.processed_dataframe = None

        if hasattr(self, 'avail_cols_list'): self.avail_cols_list.clear()
        if hasattr(self, 'feature_cols_list'): self.feature_cols_list.clear()
        if hasattr(self, 'target_col_label'): self.target_col_label.setText("<i>(未选择)</i>")
        if hasattr(self, 'preprocess_col_list'): self.preprocess_col_list.clear()
        if hasattr(self, 'data_info_display'): self.data_info_display.clear()

    def _reset_model_state(self):
        """ Resets only variables related to trained model and results displays. """
        self.model = None
        self.X_test_data_processed = None
        self.y_test_data = None
        self.predictions = None
        self.model_type = None
        self.trained_feature_names = None

        if hasattr(self, 'prediction_model'): self.prediction_model.update_dataframe(None)
        if hasattr(self, 'metrics_display'): self.metrics_display.clear()

        # Clear plot figures (Only Importance plot remains)
        for fig_name in ['importance_figure']: # Removed 'cm_figure', 'roc_figure'
             if hasattr(self, fig_name):
                 fig = getattr(self, fig_name)
                 fig.clear()
                 canvas_name = fig_name.replace('figure', 'canvas')
                 if hasattr(self, canvas_name):
                     canvas = getattr(self, canvas_name)
                     try:
                         canvas.draw_idle()
                     except Exception as e:
                         print(f"Warning: Error redrawing canvas {canvas_name}: {e}")

        if hasattr(self, 'save_model_action'): self.save_model_action.setEnabled(False)


    # --- Preprocessing ---
    def update_preprocess_info(self):
        """ Updates the data info display and column list on the preprocess page. """
        if self.dataframe is None:
            if hasattr(self, 'data_info_display'): self.data_info_display.setText("请先加载数据。")
            if hasattr(self, 'preprocess_col_list'): self.preprocess_col_list.clear()
            return

        if not hasattr(self, 'data_info_display') or not hasattr(self, 'preprocess_col_list'):
            print("Warning: Preprocessing UI elements not ready.")
            return

        info_str_io = io.StringIO()
        self.dataframe.info(buf=info_str_io)
        info_str = "<b>基本信息:</b>\n" + info_str_io.getvalue() + "\n\n"

        missing = self.dataframe.isnull().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            missing_percent = (missing / len(self.dataframe)) * 100
            missing_df = pd.DataFrame({'缺失数量': missing, '缺失比例 (%)': missing_percent.round(2)})
            if missing_df.index.name == 'index': missing_df.index.name = '列名' # Avoid confusion
            info_str += "<b>缺失值统计 (仅显示含缺失列):</b>\n" + missing_df.to_string() + "\n"
        else:
            info_str += "<b>无缺失值。</b>\n"

        self.data_info_display.setText(info_str)

        self.preprocess_col_list.clear()
        self.preprocess_col_list.addItems(self.dataframe.columns.astype(str))

    def run_preprocessing(self):
        """ Starts the preprocessing worker thread. """
        if self.dataframe is None: QMessageBox.warning(self, "错误", "请先加载数据。"); return

        selected_items = self.preprocess_col_list.selectedItems()
        selected_cols = [item.text() for item in selected_items]

        if not selected_cols:
             reply = QMessageBox.question(self, "选择列", "未选择任何列进行处理。\n是否要对 *所有* 列应用所选操作（如果适用）？",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                          QMessageBox.StandardButton.No)
             if reply == QMessageBox.StandardButton.No: return
             selected_cols = self.dataframe.columns.tolist()

        impute_strat = self.impute_strategy_combo.currentText()
        impute_const = self.impute_constant_value.text() if impute_strat == "常量 (Constant)" else None
        scale_strat = self.scale_strategy_combo.currentText()
        encode_strat = self.encode_strategy_combo.currentText()

        if impute_strat == "常量 (Constant)" and not impute_const:
             QMessageBox.warning(self, "输入错误", "选择常量填充策略时，请输入一个常量值。")
             return

        params = {
            'selected_cols': selected_cols,
            'impute_strategy': impute_strat, 'impute_constant': impute_const,
            'scale_strategy': scale_strat, 'encode_strategy': encode_strat
        }

        self.status_bar.showMessage("开始预处理...");
        self._update_ui_state()

        self.preprocess_worker = Worker(self._preprocess_data_thread, self.dataframe.copy(), params)
        self.preprocess_worker.finished.connect(self._on_preprocessing_complete)
        self.preprocess_worker.error.connect(self._on_preprocessing_error)
        self.preprocess_worker.finished.connect(self._update_ui_state)
        self.preprocess_worker.error.connect(self._update_ui_state)

        self._start_progress("正在应用预处理...", worker=self.preprocess_worker)
        self.preprocess_worker.start()

    def _preprocess_data_thread(self, progress_signal, status_signal, df, params):
        """ Worker function to apply preprocessing steps directly to the DataFrame. """
        status_signal.emit("准备预处理...")
        progress_signal.emit(5)

        selected_cols = params['selected_cols']
        numeric_features_selected = df[selected_cols].select_dtypes(include=np.number).columns.tolist()
        categorical_features_selected = df[selected_cols].select_dtypes(exclude=np.number).columns.tolist()

        df_processed = df # Modify the copy directly

        # --- 1. Imputation ---
        impute_strat_map = { "均值 (Mean)": 'mean', "中位数 (Median)": 'median',
                             "众数 (Most Frequent)": 'most_frequent', "常量 (Constant)": 'constant'}
        impute_key = params['impute_strategy']

        if impute_key in impute_strat_map:
            strategy = impute_strat_map[impute_key]
            fill_val_param = params['impute_constant']
            status_signal.emit(f"应用填充: {impute_key}")

            # Apply to selected numeric cols
            if numeric_features_selected:
                num_fill_value = None
                if strategy == 'constant':
                    try: num_fill_value = float(fill_val_param)
                    except (ValueError, TypeError):
                        status_signal.emit(f"警告: 无法将常量 '{fill_val_param}' 转为数值，数值列跳过常量填充。")
                        num_imputer = SimpleImputer(strategy='mean') # Fallback to mean? Or raise error?
                        df_processed[numeric_features_selected] = num_imputer.fit_transform(df_processed[numeric_features_selected])
                    else:
                        num_imputer = SimpleImputer(strategy=strategy, fill_value=num_fill_value)
                        df_processed[numeric_features_selected] = num_imputer.fit_transform(df_processed[numeric_features_selected])
                else:
                     num_imputer = SimpleImputer(strategy=strategy)
                     df_processed[numeric_features_selected] = num_imputer.fit_transform(df_processed[numeric_features_selected])

            # Apply to selected categorical cols
            if categorical_features_selected:
                 cat_strategy = 'most_frequent' if strategy != 'constant' else 'constant'
                 cat_fill_value = fill_val_param if strategy == 'constant' else 'missing'
                 cat_imputer = SimpleImputer(strategy=cat_strategy, fill_value=cat_fill_value)
                 df_processed[categorical_features_selected] = cat_imputer.fit_transform(df_processed[categorical_features_selected])

        progress_signal.emit(35)

        # --- 2. Scaling ---
        scale_key = params['scale_strategy']
        scaler = None
        if scale_key == "标准化 (StandardScaler)": scaler = StandardScaler()
        elif scale_key == "归一化 (MinMaxScaler)": scaler = MinMaxScaler()

        if scaler and numeric_features_selected:
            status_signal.emit(f"应用缩放: {scale_key} 到数值列")
            df_processed[numeric_features_selected] = scaler.fit_transform(df_processed[numeric_features_selected])
        progress_signal.emit(65)

        # --- 3. Encoding ---
        encode_key = params['encode_strategy']
        current_categorical_selected = df_processed[selected_cols].select_dtypes(exclude=np.number).columns.tolist()

        if not current_categorical_selected:
            if encode_key != "不处理": status_signal.emit("编码步骤跳过：选择中无类别列")
        elif encode_key == "独热编码 (One-Hot)":
             status_signal.emit(f"应用编码: {encode_key} 到类别列")
             encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
             try:
                encoded_data = encoder.fit_transform(df_processed[current_categorical_selected])
                new_col_names = encoder.get_feature_names_out(current_categorical_selected)
                encoded_df = pd.DataFrame(encoded_data, index=df_processed.index, columns=new_col_names)

                df_processed = df_processed.drop(columns=current_categorical_selected)
                df_processed = pd.concat([df_processed, encoded_df], axis=1)
             except Exception as e:
                 status_signal.emit(f"错误: OneHot 编码失败 - {e}")
                 raise

        elif encode_key == "序号编码 (Ordinal)":
             status_signal.emit(f"应用编码: {encode_key} 到类别列")
             encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
             try:
                df_processed[current_categorical_selected] = encoder.fit_transform(df_processed[current_categorical_selected])
             except Exception as e:
                 status_signal.emit(f"错误: Ordinal 编码失败 - {e}")
                 raise

        progress_signal.emit(95)
        status_signal.emit("预处理完成.")
        progress_signal.emit(100)
        return df_processed

    def _on_preprocessing_complete(self, result_df):
        self.processed_dataframe = result_df
        self.status_bar.showMessage("预处理步骤已应用.", 5000)

        self.preview_model.update_dataframe(self.processed_dataframe)
        try: self.preview_table.resizeColumnsToContents()
        except Exception as e: print(f"Warn: resize preview failed after preprocess: {e}")

        self._reset_model_state()
        self.feature_cols = []
        self.target_col = None
        if hasattr(self, 'feature_cols_list'): self.feature_cols_list.clear()
        if hasattr(self, 'target_col_label'): self.target_col_label.setText("<i>(未选择)</i>")

        self.update_config_lists()
        self._update_ui_state()
        self.switch_main_panel(3)

    def _on_preprocessing_error(self, error_info):
        exc_type, exc_value, tb_str = error_info
        QMessageBox.critical(self, "预处理错误", f"应用预处理时出错:\n{exc_value}\n\n详细信息:\n{tb_str}")
        self.status_bar.showMessage("预处理失败.", 5000)


    # --- Variable Configuration ---
    def update_config_lists(self):
        """Populates the available columns list based on the current data."""
        current_features = set(self.feature_cols)
        current_target = self.target_col

        if hasattr(self, 'avail_cols_list'): self.avail_cols_list.clear()
        if hasattr(self, 'feature_cols_list'): self.feature_cols_list.clear()

        df_to_use = self.processed_dataframe if self.processed_dataframe is not None else self.dataframe

        self.feature_cols = [] # Reset internal list
        if df_to_use is None or current_target not in df_to_use.columns:
             self.target_col = None
             if hasattr(self, 'target_col_label'): self.target_col_label.setText("<i>(未选择)</i>")
        elif hasattr(self, 'target_col_label'):
             self.target_col_label.setText(f"<b>{current_target}</b>")

        if df_to_use is not None:
            all_columns = df_to_use.columns.tolist()
            avail_cols_temp = []
            features_temp = []

            for col in all_columns:
                col_str = str(col)
                if col_str == self.target_col:
                    continue
                elif col_str in current_features:
                    features_temp.append(col_str)
                else:
                    avail_cols_temp.append(col_str)

            if hasattr(self, 'avail_cols_list'): self.avail_cols_list.addItems(avail_cols_temp)
            if hasattr(self, 'feature_cols_list'): self.feature_cols_list.addItems(features_temp)
            self.feature_cols = features_temp # Update internal list

        self._update_ui_state()


    # --- Config Button Actions ---
    def add_features(self):
        selected = self.avail_cols_list.selectedItems()
        if not selected: return
        items_to_move = [item.text() for item in selected]
        for name in items_to_move:
            found = self.avail_cols_list.findItems(name, Qt.MatchFlag.MatchExactly)
            if found: self.avail_cols_list.takeItem(self.avail_cols_list.row(found[0]))
            if name not in self.feature_cols:
                if hasattr(self, 'feature_cols_list'): self.feature_cols_list.addItem(name)
                self.feature_cols.append(name)
        self._update_ui_state()

    def remove_features(self):
        selected = self.feature_cols_list.selectedItems()
        if not selected: return
        items_to_move = [item.text() for item in selected]
        for name in items_to_move:
            found = self.feature_cols_list.findItems(name, Qt.MatchFlag.MatchExactly)
            if found: self.feature_cols_list.takeItem(self.feature_cols_list.row(found[0]))
            if name in self.feature_cols: self.feature_cols.remove(name)
            if name != self.target_col and hasattr(self, 'avail_cols_list') and not self.avail_cols_list.findItems(name, Qt.MatchFlag.MatchExactly):
                 self.avail_cols_list.addItem(name)
        self._update_ui_state()

    def set_target(self):
        selected = self.avail_cols_list.selectedItems()
        if len(selected) != 1:
             QMessageBox.warning(self, "选择目标", "请从可用列中选择 *一个* 目标变量。")
             return
        item = selected[0]
        new_target = item.text()

        if self.target_col and self.target_col != new_target:
            if self.target_col not in self.feature_cols and hasattr(self, 'avail_cols_list') and not self.avail_cols_list.findItems(self.target_col, Qt.MatchFlag.MatchExactly):
                self.avail_cols_list.addItem(self.target_col)

        self.target_col = new_target
        if hasattr(self, 'target_col_label'): self.target_col_label.setText(f"<b>{self.target_col}</b>")

        self.avail_cols_list.takeItem(self.avail_cols_list.row(item))

        if self.target_col in self.feature_cols:
            if hasattr(self, 'feature_cols_list'):
                found_feature = self.feature_cols_list.findItems(self.target_col, Qt.MatchFlag.MatchExactly)
                if found_feature: self.feature_cols_list.takeItem(self.feature_cols_list.row(found_feature[0]))
            self.feature_cols.remove(self.target_col)

        self._update_ui_state()

    def clear_target(self):
        if self.target_col:
            old_target = self.target_col
            self.target_col = None
            if hasattr(self, 'target_col_label'): self.target_col_label.setText("<i>(未选择)</i>")

            if old_target not in self.feature_cols and hasattr(self, 'avail_cols_list') and not self.avail_cols_list.findItems(old_target, Qt.MatchFlag.MatchExactly):
                 self.avail_cols_list.addItem(old_target)

            self._update_ui_state()

    # --- Model Training ---
    def run_training(self):
        if not self._validate_before_training(): return

        algo_name = self.algo_combo.currentText()
        df_for_training = self.processed_dataframe if self.processed_dataframe is not None else self.dataframe
        y_series = df_for_training[self.target_col]
        temp_model_type = self._infer_problem_type(y_series)
        if temp_model_type is None: return

        params = self._get_current_params(algo_name, temp_model_type)
        if params is None: return

        use_cv = self.cv_checkbox.isChecked()
        cv_folds = self.cv_folds_spinbox.value() if use_cv else 5 # Use 5 as default for CV if checked

        self.status_bar.showMessage(f"准备训练 {algo_name}...");
        self._update_ui_state()

        self.train_worker = Worker(self._train_model_thread, df_for_training.copy(), self.feature_cols[:], self.target_col, algo_name, params, use_cv, cv_folds)
        self.train_worker.finished.connect(self._on_training_complete)
        self.train_worker.error.connect(self._on_training_error)
        self.train_worker.finished.connect(self._update_ui_state)
        self.train_worker.error.connect(self._update_ui_state)

        self._start_progress(f"正在训练 {algo_name}...", worker=self.train_worker)
        self.train_worker.start()

    def _validate_before_training(self):
        df_to_use = self.processed_dataframe if self.processed_dataframe is not None else self.dataframe
        if df_to_use is None: QMessageBox.warning(self, "验证错误", "数据不可用，请先加载或预处理数据。"); return False
        if not self.feature_cols: QMessageBox.warning(self, "验证错误", "请在“变量配置”页面选择至少一个特征变量。"); return False
        if not self.target_col: QMessageBox.warning(self, "验证错误", "请在“变量配置”页面选择一个目标变量。"); return False

        missing_feats = [f for f in self.feature_cols if f not in df_to_use.columns]
        if missing_feats:
            QMessageBox.critical(self, "验证错误", f"选择的部分特征列在当前数据中不存在 (可能在预处理后被移除或重命名):\n{', '.join(missing_feats)}"); return False
        if self.target_col not in df_to_use.columns:
            QMessageBox.critical(self, "验证错误", f"选择的目标列 '{self.target_col}' 在当前数据中不存在。"); return False
        if self.target_col in self.feature_cols:
            QMessageBox.critical(self, "验证错误", f"目标列 '{self.target_col}' 不能同时是特征列。"); return False

        X_check = df_to_use[self.feature_cols]
        y_check = df_to_use[self.target_col]
        if X_check.isnull().values.any():
             reply = QMessageBox.warning(self, "数据警告", "特征列中检测到缺失值 (NaN)。\n建议在“数据预处理”页面处理缺失值。\n是否继续训练 (模型可能会失败或表现不佳)?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
             if reply == QMessageBox.StandardButton.No: return False
        if y_check.isnull().values.any():
             QMessageBox.critical(self, "数据错误", "目标列中检测到缺失值 (NaN)。\n请处理或移除包含缺失目标的行后重试。")
             return False
        if np.isinf(X_check.select_dtypes(include=np.number)).values.any() or \
           np.isinf(y_check if pd.api.types.is_numeric_dtype(y_check) else 0).values.any():
             reply = QMessageBox.warning(self, "数据警告", "特征或目标列中检测到无穷大 (inf) 值。\n这可能导致训练错误。\n是否继续?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
             if reply == QMessageBox.StandardButton.No: return False

        return True

    def _infer_problem_type(self, y_series):
        """Infers problem type (classification/regression) based on target column."""
        try:
            if pd.api.types.is_float_dtype(y_series):
                return 'regression'
            if pd.api.types.is_integer_dtype(y_series) and y_series.nunique() > 20:
                return 'regression'
            if pd.api.types.is_object_dtype(y_series) or \
               pd.api.types.is_categorical_dtype(y_series) or \
               pd.api.types.is_bool_dtype(y_series):
                 if y_series.dropna().empty:
                      raise ValueError("目标列只包含缺失值.")
                 return 'classification'
            if pd.api.types.is_integer_dtype(y_series) and y_series.nunique() <= 20:
                if y_series.nunique() <= 2:
                     print("Inferred binary classification.")
                else:
                     print(f"Inferred multi-class classification ({y_series.nunique()} classes).")
                return 'classification'
            raise ValueError(f"无法自动确定目标列 '{y_series.name}' 的问题类型 (dtype: {y_series.dtype}, unique: {y_series.nunique()}).")
        except Exception as e:
            QMessageBox.critical(self, "类型推断错误", f"无法确定目标变量类型: {e}")
            return None


    def _get_current_params(self, algo_name, model_type):
        """ Retrieves parameters from the currently active parameter widget. """
        if algo_name in self.param_widgets:
            param_widget = self.param_widgets[algo_name]
            prop_func = param_widget.property("get_params")
            if callable(prop_func):
                try:
                    params = prop_func(model_type)
                    print(f"Retrieved params for {algo_name} ({model_type}): {params}")
                    return params
                except Exception as e:
                    error_msg = f"无法获取 '{algo_name}' 的参数: {e}\n\n检查输入格式 (例如 隐藏层大小)。\n\n详细错误:\n{traceback.format_exc()}"
                    QMessageBox.critical(self, "参数错误", error_msg)
                    return None
            else:
                 QMessageBox.warning(self, "参数错误", f"'{algo_name}' 的参数配置界面缺少 'get_params' 方法。")
                 return None
        else:
            QMessageBox.warning(self, "参数错误", f"未找到 '{algo_name}' 的参数配置界面。")
            return None


    def _train_model_thread(self, progress_signal, status_signal, df, features, target, algo_name, params, use_cv, cv_folds):
        """ Trains the model (single split or placeholder CV) and evaluates. """
        status_signal.emit("准备数据..."); progress_signal.emit(5)
        X = df[features]
        y = df[target]

        status_signal.emit("推断问题类型...");
        problem_type = self._infer_problem_type(y)
        if problem_type is None: raise ValueError("无法确定问题类型.")
        status_signal.emit(f"问题类型: {problem_type}")

        y_original = y.copy()
        label_mapping = None
        if problem_type == 'classification' and not pd.api.types.is_numeric_dtype(y):
            status_signal.emit("目标列进行数值编码...")
            y, label_mapping = pd.factorize(y)
            y = pd.Series(y, index=X.index)
            print("标签映射:", dict(enumerate(label_mapping)))
        progress_signal.emit(10)

        X_train, X_test, y_train, y_test = None, None, None, None
        cv_scores = None

        if use_cv:
            status_signal.emit(f"准备 {cv_folds}-折交叉验证...")
            status_signal.emit(f"注意: 交叉验证评估逻辑未完全实现，将执行标准训练/测试评估。")
            # Fall through to standard split...

        if X_train is None:
             status_signal.emit("拆分训练/测试数据...")
             stratify_param = y if problem_type == 'classification' and y.nunique() > 1 else None
             try:
                 X_train, X_test, y_train, y_test = train_test_split(
                     X, y, test_size=0.25, random_state=42, stratify=stratify_param
                 )
             except ValueError as e:
                 status_signal.emit(f"警告: 分层拆分失败 ({e})，使用非分层拆分。")
                 X_train, X_test, y_train, y_test = train_test_split(
                     X, y, test_size=0.25, random_state=42
                 )
        progress_signal.emit(15)

        model = self._instantiate_model(algo_name, problem_type, params, status_signal)
        if model is None: raise ValueError("模型初始化失败.")
        progress_signal.emit(20)

        status_signal.emit(f"训练 {model.__class__.__name__}...")
        try:
             model.fit(X_train, y_train)
        except Exception as fit_error:
             status_signal.emit(f"错误: 模型训练失败 - {fit_error}")
             raise RuntimeError(f"模型训练失败: {fit_error}") from fit_error

        progress_signal.emit(80)
        status_signal.emit("训练完成.")

        status_signal.emit("在测试集上预测与评估...")
        y_pred = model.predict(X_test)
        y_pred_proba = None
        if problem_type == 'classification' and hasattr(model, "predict_proba"):
            try:
                y_pred_proba = model.predict_proba(X_test)
            except Exception as e:
                status_signal.emit(f"警告: 获取预测概率失败 - {e}")
        progress_signal.emit(85)

        metrics = self._calculate_metrics(y_test, y_pred, y_pred_proba, problem_type, status_signal)
        progress_signal.emit(90)

        importance, importance_names = self._get_feature_importance(model, X.columns)
        progress_signal.emit(95)

        status_signal.emit("处理完成.")
        progress_signal.emit(100)

        return {"model": model,
                "metrics": metrics,
                "feature_importance": importance,
                "feature_names": importance_names,
                "X_test_processed": X_test,
                "y_test": y_test,
                "y_pred": y_pred,
                "y_pred_proba": y_pred_proba,
                "model_type": problem_type,
                "label_mapping": label_mapping
                }

    def _instantiate_model(self, algo_name, problem_type, params, status_signal):
        """ Helper to instantiate the correct model based on name and type """
        status_signal.emit(f"初始化模型: {algo_name}...")
        model = None
        base_params = {'random_state': 42}

        try:
            if algo_name == "随机森林":
                 model_params = {**base_params, **params, 'n_jobs': -1}
                 model = RandomForestClassifier(**model_params) if problem_type == 'classification' else RandomForestRegressor(**model_params)
            elif algo_name == "神经网络(MLP)":
                 mlp_params = {k: v for k, v in params.items() if k in ['hidden_layer_sizes', 'activation', 'solver', 'alpha', 'max_iter']}
                 model_params = {**base_params, **mlp_params, 'early_stopping': True, 'n_iter_no_change': 10}
                 model = MLPClassifier(**model_params) if problem_type == 'classification' else MLPRegressor(**model_params)
            elif algo_name == "LightGBM" and lgb:
                 lgbm_params = {k: v for k, v in params.items() if k in ['n_estimators', 'learning_rate', 'max_depth', 'num_leaves']}
                 model_params = {**base_params, **lgbm_params, 'n_jobs': -1}
                 model = lgb.LGBMClassifier(**model_params) if problem_type == 'classification' else lgb.LGBMRegressor(**model_params)
            elif algo_name == "XGBoost" and xgb:
                 xgb_params = {k: v for k, v in params.items() if k in ['n_estimators', 'learning_rate', 'eta', 'max_depth', 'subsample', 'colsample_bytree']}
                 model_params = {**base_params, **xgb_params, 'use_label_encoder': False, 'eval_metric': 'logloss' if problem_type=='classification' else 'rmse'}

                 if problem_type == 'classification':
                      objective = 'binary:logistic'
                      model = xgb.XGBClassifier(**model_params, objective=objective)
                 else:
                      objective = 'reg:squarederror'
                      model = xgb.XGBRegressor(**model_params, objective=objective)
            else:
                 raise ValueError(f"未知或不支持的算法: {algo_name}")

            status_signal.emit(f"{model.__class__.__name__} 已初始化.")
            return model

        except Exception as e:
             status_signal.emit(f"错误: 初始化模型失败 - {e}")
             print(f"Model instantiation error:\n{traceback.format_exc()}")
             return None

    def _calculate_metrics(self, y_true, y_pred, y_pred_proba, problem_type, status_signal):
        """ Calculates evaluation metrics based on problem type. """
        metrics = {}
        try:
            if problem_type == 'classification':
                metrics['Accuracy'] = accuracy_score(y_true, y_pred)
                n_classes = pd.Series(y_true).nunique() # Use pandas nunique on Series
                avg_strat = 'binary' if n_classes <= 2 else 'weighted'
                metrics['Precision'] = precision_score(y_true, y_pred, average=avg_strat, zero_division=0)
                metrics['Recall'] = recall_score(y_true, y_pred, average=avg_strat, zero_division=0)
                metrics['F1-Score'] = f1_score(y_true, y_pred, average=avg_strat, zero_division=0)

                if y_pred_proba is not None:
                    try:
                        if n_classes == 2:
                            if y_pred_proba.ndim == 2 and y_pred_proba.shape[1] >= 2:
                                metrics['AUC'] = roc_auc_score(y_true, y_pred_proba[:, 1])
                            else: metrics['AUC'] = 'N/A (Proba shape)'
                        elif n_classes > 2:
                             # Check if y_true has labels for all classes in y_pred_proba for OvR
                             present_classes = np.unique(y_true)
                             if len(present_classes) < n_classes:
                                 metrics['AUC (OvR)'] = f'N/A ({len(present_classes)}/{n_classes} cls present)'
                             elif y_pred_proba.ndim == 2 and y_pred_proba.shape[1] == n_classes:
                                metrics['AUC (OvR)'] = roc_auc_score(y_true, y_pred_proba, multi_class='ovr', average='weighted', labels=np.arange(n_classes))
                             else: metrics['AUC (OvR)'] = 'N/A (Proba shape)'
                    except ValueError as auc_error:
                         metrics['AUC'] = f"N/A ({auc_error})"
                         status_signal.emit(f"警告: 计算 AUC 失败 - {auc_error}")
                else:
                    metrics['AUC'] = 'N/A (No probabilities)'

            else: # Regression
                metrics['R²'] = r2_score(y_true, y_pred)
                metrics['MAE'] = mean_absolute_error(y_true, y_pred)
                metrics['MSE'] = mean_squared_error(y_true, y_pred)
                metrics['RMSE'] = np.sqrt(metrics['MSE'])

            try:
                corr, p_value = spearmanr(y_true, y_pred)
                metrics['Spearman Rho'] = corr if not np.isnan(corr) else 'N/A'
            except ValueError:
                 metrics['Spearman Rho'] = 'N/A (Calc error)'

        except Exception as e:
            status_signal.emit(f"错误: 计算指标失败 - {e}")
            print(f"Metrics calculation error:\n{traceback.format_exc()}")
        return metrics


    def _get_feature_importance(self, model, feature_names):
        """ Extracts feature importance if available from the model. """
        importances = None
        names = list(feature_names)

        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            if model.coef_.ndim == 1:
                 importances = np.abs(model.coef_)
            elif model.coef_.ndim == 2:
                 importances = np.mean(np.abs(model.coef_), axis=0)

        if importances is not None and len(importances) == len(names):
            return importances, names
        else:
            if importances is not None:
                 print(f"Warning: Feature importance length ({len(importances)}) mismatch with feature names ({len(names)}).")
            return None, names


    def _on_training_complete(self, results):
        if results is None: QMessageBox.warning(self,"训练结果","训练未返回有效结果。"); return

        self.model = results["model"]
        self.X_test_data_processed = results["X_test_processed"]
        self.y_test_data = results["y_test"]
        self.predictions = results["y_pred"]
        self.model_type = results["model_type"]
        self.trained_feature_names = results["feature_names"]
        y_pred_proba = results.get("y_pred_proba") # Still needed for AUC metric
        label_mapping = results.get("label_mapping")

        self.status_bar.showMessage("训练成功!", 5000)

        # Display results (Plots are removed)
        self.display_predictions(label_mapping)
        self.display_metrics(results["metrics"])
        self.display_feature_importance(results["feature_importance"], self.trained_feature_names)

        # No CM/ROC plots to display or clear

        self.switch_main_panel(5)
        self._update_ui_state()

    def _on_training_error(self, error_info):
        exc_type, exc_value, tb_str = error_info
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("训练失败")
        layout = QVBoxLayout(error_dialog)
        label = QLabel(f"训练过程中发生错误:\n<b>{exc_value}</b>")
        label.setWordWrap(True)
        layout.addWidget(label)
        tb_edit = QTextEdit()
        tb_edit.setPlainText(tb_str)
        tb_edit.setReadOnly(True)
        tb_edit.setMinimumSize(600, 200)
        layout.addWidget(QLabel("详细错误信息:"))
        layout.addWidget(tb_edit)
        button_box = QPushButton("关闭")
        button_box.clicked.connect(error_dialog.accept)
        layout.addWidget(button_box)
        error_dialog.exec()

        self.status_bar.showMessage("训练失败.", 5000)
        self._reset_model_state()
        self._update_ui_state()

    # --- Results Display ---
    def display_predictions(self, label_mapping=None):
        """ Displays predictions vs actuals, potentially decoding labels. """
        if self.X_test_data_processed is None or self.y_test_data is None or self.predictions is None:
            if hasattr(self, 'prediction_model'): self.prediction_model.update_dataframe(None)
            return

        limit = min(MAX_PREVIEW_ROWS, len(self.X_test_data_processed))
        df_display = self.X_test_data_processed.head(limit).copy()

        actual_encoded = self.y_test_data[:limit]
        pred_encoded = self.predictions[:limit]

        actual_display = actual_encoded
        pred_display = pred_encoded

        if self.model_type == 'classification' and label_mapping is not None:
            try:
                 # Create Series before mapping for correct index alignment
                 actual_display = pd.Series(actual_encoded, index=df_display.index).map(dict(enumerate(label_mapping))).fillna("未知")
                 pred_display = pd.Series(pred_encoded, index=df_display.index).map(dict(enumerate(label_mapping))).fillna("未知")
            except Exception as e:
                 print(f"Warning: Could not decode labels using mapping - {e}")

        actual_col_name = f"实际_{self.target_col}"
        pred_col_name = f"预测_{self.target_col}"
        df_display[actual_col_name] = actual_display
        df_display[pred_col_name] = pred_display

        cols_to_move = [actual_col_name, pred_col_name]
        other_cols = [c for c in df_display.columns if c not in cols_to_move]
        df_display = df_display[other_cols + cols_to_move]

        if hasattr(self, 'prediction_model'):
            self.prediction_model.update_dataframe(df_display)
            if hasattr(self, 'predictions_table'):
                 try: self.predictions_table.resizeColumnsToContents()
                 except Exception as e: print(f"Warn: Resize prediction table failed: {e}")

    def display_metrics(self, metrics):
        if not hasattr(self, 'metrics_display'): return
        if not metrics: self.metrics_display.setText("无可用评估指标。"); return

        model_name = self.model.__class__.__name__ if self.model else "N/A"
        problem_type_str = self.model_type or 'N/A'

        txt = f"模型: {model_name}\n类型: {problem_type_str}\n"
        txt += "="*40 + "\n  评估指标 (测试集)\n" + "="*40 + "\n"
        for key, value in metrics.items():
            try:
                if isinstance(value, (float, np.floating)):
                    txt += f"{key:<25}: {value:.4f}\n"
                else:
                    txt += f"{key:<25}: {str(value)}\n"
            except Exception as format_exc:
                 txt += f"{key:<25}: Error ({format_exc})\n"
        txt += "="*40 + "\n"
        self.metrics_display.setText(txt)

    def display_feature_importance(self, importances, feature_names):
        if not hasattr(self,'importance_figure') or not hasattr(self,'importance_canvas'): return
        self.importance_figure.clear()
        ax = self.importance_figure.add_subplot(111)

        valid_importance = importances is not None and feature_names is not None and len(importances) == len(feature_names)

        if not valid_importance:
            ax.text(0.5, 0.5, "特征重要性不可用\n(模型不支持或计算错误)",
                    ha='center', va='center', transform=ax.transAxes, fontsize=10, wrap=True)
            ax.set_title("特征重要性")
            ax.set_xlabel("")
            ax.set_ylabel("")
        else:
            try:
                 importance_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
                 importance_df = importance_df.sort_values('importance', ascending=False)
                 n_show = min(20, len(importance_df))
                 df_show = importance_df.head(n_show)

                 y_pos = np.arange(len(df_show))
                 ax.barh(y_pos, df_show['importance'], align='center')
                 ax.set_yticks(y_pos)
                 ax.set_yticklabels(df_show['feature'], fontsize=8)
                 ax.invert_yaxis()
                 ax.set_xlabel('重要性值')
                 ax.set_title(f'特征重要性 (Top {n_show})')
                 self.importance_figure.tight_layout()
            except Exception as e:
                 ax.text(0.5, 0.5, f"绘制重要性时出错:\n{e}",
                         ha='center', va='center', transform=ax.transAxes, fontsize=9, color='red', wrap=True)
                 print(f"Error plotting importance: {e}\n{traceback.format_exc()}")

        self.importance_canvas.draw_idle()

    # REMOVED: display_confusion_matrix method
    # REMOVED: display_roc_curve method

    # --- Model Persistence ---
    def save_model_dialog(self):
        if self.model is None: QMessageBox.warning(self,"保存失败","无已训练模型可保存。"); return

        algo_name = self.model.__class__.__name__
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        suggested_filename = f"{algo_name}_{timestamp}.joblib"

        filePath, _ = QFileDialog.getSaveFileName(self, "保存模型文件", suggested_filename, "Joblib 模型文件 (*.joblib);;All Files (*)")
        if filePath:
            if not filePath.lower().endswith('.joblib'): filePath += '.joblib'

            data_to_save = {
                'model': self.model,
                'trained_feature_names': self.trained_feature_names,
                'target_name': self.target_col,
                'model_type': self.model_type,
                'app_version': VERSION,
                # 'preprocessor': self.preprocessor # Still missing
            }
            print("--- Saving Model ---")
            print(f"Model: {self.model.__class__.__name__}")
            print(f"Features: {self.trained_feature_names}")
            print(f"Target: {self.target_col}")
            print(f"Type: {self.model_type}")
            print("--------------------")

            try:
                joblib.dump(data_to_save, filePath, compress=3)
                self.status_bar.showMessage(f"模型已保存至: {filePath}", 5000)
                QMessageBox.information(self, "保存成功", f"模型及相关信息已保存到:\n{filePath}\n\n"
                                        "<b>重要提示:</b> 当前版本未保存预处理步骤。加载此模型后，需确保新数据经过完全相同的预处理。")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存模型时发生错误: {e}\n\n详细信息:\n{traceback.format_exc()}")

    def load_model_dialog(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "加载模型文件", "", "Joblib 模型文件 (*.joblib);;All Files (*)")
        if filePath:
            try:
                loaded_data = joblib.load(filePath)

                if not isinstance(loaded_data, dict) or 'model' not in loaded_data or 'trained_feature_names' not in loaded_data:
                     QMessageBox.warning(self,"加载失败","文件格式无效或缺少必要的模型信息 (模型、特征名)。")
                     return

                loaded_version = loaded_data.get('app_version', '未知')
                if loaded_version != VERSION:
                     QMessageBox.warning(self, "版本不匹配", f"模型由不同版本的应用 ({loaded_version}) 保存。\n加载可能成功，但行为可能不完全一致。")

                if 'preprocessor' not in loaded_data:
                     QMessageBox.warning(self, "预处理警告", "加载的模型文件不包含预处理步骤信息。\n请确保当前使用的数据已经过与训练时 *完全相同* 的预处理，否则预测结果将不可靠。")

                self._reset_model_state_full()

                self.model = loaded_data['model']
                self.trained_feature_names = loaded_data.get('trained_feature_names')
                loaded_target = loaded_data.get('target_name')
                self.model_type = loaded_data.get('model_type')

                print("--- Loading Model ---")
                print(f"Model: {self.model.__class__.__name__}")
                print(f"Expected Features: {self.trained_feature_names}")
                print(f"Original Target: {loaded_target}")
                print(f"Type: {self.model_type}")
                print("---------------------")

                self.status_bar.showMessage(f"模型已从 {filePath} 加载.", 5000)

                if self.dataframe is not None:
                    if loaded_target and loaded_target in self.dataframe.columns:
                         self.target_col = loaded_target
                    if self.trained_feature_names:
                         self.feature_cols = [f for f in self.trained_feature_names if f in self.dataframe.columns]
                         missing_loaded_feats = [f for f in self.trained_feature_names if f not in self.dataframe.columns]
                         if missing_loaded_feats:
                             QMessageBox.warning(self, "特征缺失", f"当前加载的数据缺少模型训练时使用的部分特征:\n{', '.join(missing_loaded_feats)}\n请确保数据包含所有必需列或重新加载/预处理数据。")
                    self.update_config_lists()
                else:
                     self.target_col = loaded_target
                     self.feature_cols = self.trained_feature_names if self.trained_feature_names else []
                     QMessageBox.information(self, "模型已加载", f"模型 {self.model.__class__.__name__} 已加载。\n请加载或准备与训练时兼容的数据（特征: {len(self.feature_cols)} 列, 目标: '{self.target_col}'）并进行必要的预处理。")

                self._update_ui_state()

            except FileNotFoundError:
                 QMessageBox.critical(self, "加载失败", f"找不到文件: {filePath}")
            except joblib.externals.loky.process_executor.TerminatedWorkerError:
                 QMessageBox.critical(self, "加载失败", "加载模型时发生 Joblib Worker 错误。\n可能是由于 Python 版本或库版本不兼容。\n请确保加载环境与保存环境相似。")
            except Exception as e:
                QMessageBox.critical(self, "加载失败", f"加载模型时发生未知错误: {e}\n\n详细信息:\n{traceback.format_exc()}")
                self._reset_model_state_full()
                self._update_ui_state()


# =============================================================================
# Entry Point
# =============================================================================
if __name__ == '__main__':
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
         QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
         QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    # import os
    # os.environ['QT_QPA_PLATFORM'] = 'xcb'

    app = QApplication(sys.argv)
    window = MLClientApp()
    window.show()
    sys.exit(app.exec())