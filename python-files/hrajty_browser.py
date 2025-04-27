import sys
import json
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtGui import QIcon, QKeySequence, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar,
    QAction, QMenu, QToolButton, QWidget, QVBoxLayout,
    QTabWidget, QDialog, QFormLayout, QDialogButtonBox,
    QListWidget, QCheckBox, QFileDialog, QTextEdit, QProgressBar, QPushButton, QLabel
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, QWebEngineDownloadItem, QWebEngineProfile, QWebEnginePage
)
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

SETTINGS_FILE = 'settings.json'
HISTORY_FILE = 'history.json'
BOOKMARKS_SYNC_FILE = 'bookmarks_sync.json'

# AdBlock interceptor
class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self, blocked_hosts=None):
        super().__init__()
        self.blocked_hosts = blocked_hosts or ['ads.', 'doubleclick.net', 'googlesyndication.com', 'adservice.']

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if any(h in url for h in self.blocked_hosts):
            info.block(True)

# Download manager dialog
class DownloadManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Stahování')
        self.resize(500, 300)
        layout = QVBoxLayout(self)
        self.list = QListWidget(self)
        layout.addWidget(self.list)
        self.download_items = {}

    def add_item(self, item):
        download_widget = QWidget(self)
        layout = QVBoxLayout(download_widget)
        
        # File name and progress bar
        filename = item.url().fileName()
        progress_bar = QProgressBar(self)
        progress_bar.setMaximum(100)
        
        layout.addWidget(QLabel(f"Stahování: {filename}"))
        layout.addWidget(progress_bar)

        # Pause / Continue button
        pause_button = QPushButton('Pauza', self)
        pause_button.clicked.connect(lambda: self.toggle_pause(item, progress_bar, pause_button))
        layout.addWidget(pause_button)

        # Open file / folder button
        open_button = QPushButton('Otevřít soubor', self)
        open_button.clicked.connect(lambda: self.open_file(item))
        layout.addWidget(open_button)

        # Add the download widget
        self.list.addItem(f"{filename}")
        self.list.setItemWidget(self.list.item(self.list.count() - 1), download_widget)
        
        # Save reference for progress updates
        self.download_items[item] = {
            'progress_bar': progress_bar,
            'pause_button': pause_button,
            'file': filename
        }

    def toggle_pause(self, item, progress_bar, pause_button):
        if item.state() == QWebEngineDownloadItem.DownloadActive:
            item.pause()
            pause_button.setText('Pokračovat')
        elif item.state() == QWebEngineDownloadItem.DownloadPaused:
            item.resume()
            pause_button.setText('Pauza')

    def open_file(self, item):
        # Open the folder containing the file
        path = item.path()
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def update_progress(self, item, bytes_received, bytes_total):
        progress_bar = self.download_items[item]['progress_bar']
        if bytes_total > 0:
            progress_bar.setValue(int((bytes_received / bytes_total) * 100))

    def handle_error(self, item):
        self.download_items[item]['pause_button'].setEnabled(False)
        self.download_items[item]['pause_button'].setText('Chyba')

# Reader mode dialog
class ReaderDialog(QDialog):
    def __init__(self, html, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Reader Mode')
        layout = QVBoxLayout(self)
        text = QTextEdit(self)
        text.setReadOnly(True)
        text.setHtml(html)
        layout.addWidget(text)

# Settings dialog
class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle('Nastavení')
        layout = QFormLayout(self)
        # Homepage
        self.home_input = QLineEdit(self)
        self.home_input.setText(settings.get('home_url', 'http://127.0.0.1:5000'))
        layout.addRow('Domovská stránka:', self.home_input)
        # Dark mode
        self.dark_checkbox = QCheckBox('Tmavý režim', self)
        self.dark_checkbox.setChecked(settings.get('dark_mode', False))
        layout.addRow(self.dark_checkbox)
        # Ad-block
        self.ad_checkbox = QCheckBox('Blokovat reklamy', self)
        self.ad_checkbox.setChecked(settings.get('adblock_enabled', True))
        layout.addRow(self.ad_checkbox)
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self):
        return {
            'home_url': self.home_input.text().strip(),
            'dark_mode': self.dark_checkbox.isChecked(),
            'adblock_enabled': self.ad_checkbox.isChecked()
        }

class HrajtyBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Hrajty 🚀')
        self.setWindowIcon(QIcon('icon.png'))
        self.setGeometry(100, 100, 1200, 800)

        # Load persisted data
        self.settings = self.load_json(SETTINGS_FILE) or {}
        self.home_url = QUrl(self.settings.get('home_url', 'http://127.0.0.1:5000'))
        self.dark_mode = self.settings.get('dark_mode', False)
        self.adblock_enabled = self.settings.get('adblock_enabled', True)
        self.history = self.load_json(HISTORY_FILE) or []

        # Apply dark mode
        self.apply_dark_mode(self.dark_mode)
        # Setup adblock interceptor
        profile = QWebEngineProfile.defaultProfile()
        profile.setUrlRequestInterceptor(AdBlocker() if self.adblock_enabled else None)

        # Toolbar
        nav = QToolBar('Navigace')
        self.addToolBar(nav)
        nav.addAction(QAction('←', self, shortcut=QKeySequence.Back, triggered=lambda: self.current_browser().back()))
        nav.addAction(QAction('→', self, shortcut=QKeySequence.Forward, triggered=lambda: self.current_browser().forward()))
        nav.addAction(QAction('🏠', self, triggered=lambda: self.current_browser().setUrl(self.home_url)))
        nav.addSeparator()
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)
        nav.addWidget(self.url_bar)
        nav.addAction(QAction('+', self, shortcut='Ctrl+T', triggered=self.add_new_tab))
        nav.addAction(QAction('⭐', self, triggered=self.add_bookmark))

        # Initialize bookmark menu
        self.bm_menu = QMenu(self)
        bm_btn = QToolButton(self)
        bm_btn.setText('Záložky ▼')
        bm_btn.setMenu(self.bm_menu)
        bm_btn.setPopupMode(QToolButton.InstantPopup)
        nav.addWidget(bm_btn)

        nav.addAction(QAction('📜', self, triggered=self.show_history))
        nav.addAction(QAction('🔍', self, shortcut='Ctrl+F', triggered=self.open_find))
        nav.addAction(QAction('📥', self, triggered=self.show_downloads))
        nav.addAction(QAction('🖼', self, triggered=self.screenshot))
        nav.addAction(QAction('📄PDF', self, triggered=self.open_pdf))
        nav.addAction(QAction('🔄', self, triggered=self.reader_mode))
        nav.addAction(QAction('⚙️', self, triggered=self.open_settings))
        nav.addAction(QAction('⛶', self, shortcut='F11', triggered=self.toggle_fullscreen))

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabs)
        central.setLayout(layout)
        self.setCentralWidget(central)

        # Download manager
        self.downloads = DownloadManager(self)

        # Open first tab
        self.add_new_tab()

    # Add toggle_fullscreen method
    def toggle_fullscreen(self):
        self.setWindowState(self.windowState() ^ Qt.WindowFullScreen)

    # Utility methods
    def load_json(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

    def save_json(self, path, data):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def apply_dark_mode(self, enable):
        pal = QPalette() if enable else QApplication.instance().style().standardPalette()
        if enable:
            pal.setColor(QPalette.Window, QColor(53, 53, 53))
            pal.setColor(QPalette.WindowText, QColor(255, 255, 255))
            pal.setColor(QPalette.Base, QColor(25, 25, 25))
            pal.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            pal.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
            pal.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
            pal.setColor(QPalette.Text, QColor(255, 255, 255))
            pal.setColor(QPalette.Button, QColor(53, 53, 53))
            pal.setColor(QPalette.ButtonText, QColor(255, 255, 255))
            pal.setColor(QPalette.BrightText, QColor(255, 0, 0))
            pal.setColor(QPalette.Link, QColor(42, 130, 218))
            pal.setColor(QPalette.Highlight, QColor(42, 130, 218))
            pal.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        QApplication.instance().setPalette(pal)

    def current_browser(self):
        return self.tabs.currentWidget()

    def current_tab_changed(self, index):
        self.url_bar.setText(self.current_browser().url().toString())

    def close_current_tab(self, index):
        self.tabs.removeTab(index)

    def add_new_tab(self):
        browser = QWebEngineView()
        browser.setUrl(self.home_url)
        self.tabs.addTab(browser, 'Nová karta')
        self.tabs.setCurrentWidget(browser)

    def load_url(self):
        url = self.url_bar.text().strip()
        self.current_browser().setUrl(QUrl(url))

    def add_bookmark(self):
        current_url = self.current_browser().url().toString()
        # Save bookmark logic here
        pass

    def show_history(self):
        # Show history dialog
        pass

    def open_find(self):
        # Implement search bar
        pass

    def show_downloads(self):
        self.downloads.exec_()

    def screenshot(self):
        # Implement screenshot capture
        pass

    def open_pdf(self):
        # Implement PDF viewer
        pass

    def reader_mode(self):
        html_content = self.current_browser().page().toHtml()
        self.reader_dialog = ReaderDialog(html_content, self)
        self.reader_dialog.exec_()

    def open_settings(self):
        dialog = SettingsDialog(self, self.settings)
        if dialog.exec_() == QDialog.Accepted:
            self.settings = dialog.get_values()
            self.save_json(SETTINGS_FILE, self.settings)
            self.apply_dark_mode(self.settings['dark_mode'])

# Main entry
if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = HrajtyBrowser()
    browser.show()
    sys.exit(app.exec_())
