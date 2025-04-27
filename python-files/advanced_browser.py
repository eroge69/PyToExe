import sys
from PyQt5.QtCore import QUrl, QSettings, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLineEdit, QToolBar, 
                             QAction, QWidget, QTabWidget, QMenu, QMessageBox, QShortcut)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineDownloadItem
from PyQt5.QtGui import QKeySequence

class AdvancedBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gelişmiş Tarayıcı")
        self.setGeometry(100, 100, 1024, 768)
        
        # Ayarlar (Favoriler ve Geçmiş için)
        self.settings = QSettings("MyBrowser", "AdvancedBrowser")
        self.favorites = self.settings.value("favorites", [])
        self.history = self.settings.value("history", [])
        
        # Sekme Yapısı
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.setCentralWidget(self.tabs)
        
        # Toolbar (Araç Çubuğu)
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Butonlar ve Kısayollar
        back_btn = QAction("◀ Geri", self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        toolbar.addAction(back_btn)
        
        forward_btn = QAction("İleri ▶", self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        toolbar.addAction(forward_btn)
        
        reload_btn = QAction("🔄 Yenile", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        toolbar.addAction(reload_btn)
        
        home_btn = QAction("🏠 Ana Sayfa", self)
        home_btn.triggered.connect(self.navigate_home)
        toolbar.addAction(home_btn)
        
        # Adres Çubuğu
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        # Yeni Sekme Butonu
        new_tab_btn = QAction("➕ Yeni Sekme", self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        toolbar.addAction(new_tab_btn)
        
        # Favori Ekle Butonu
        fav_btn = QAction("⭐ Favori Ekle", self)
        fav_btn.triggered.connect(self.add_to_favorites)
        toolbar.addAction(fav_btn)
        
        # Kısayollar
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.add_new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(lambda: self.current_browser().reload())
        
        # İlk Sekmeyi Aç
        self.add_new_tab(QUrl("https://www.google.com"))
        
        # İndirme Yöneticisi
        self.downloads = []
    
    def current_browser(self):
        return self.tabs.currentWidget()
    
    def add_new_tab(self, url=None):
        if url is None:
            url = QUrl("https://www.google.com")
        
        browser = QWebEngineView()
        browser.setUrl(url)
        browser.urlChanged.connect(self.update_url_bar)
        
        index = self.tabs.addTab(browser, "Yeni Sekme")
        self.tabs.setCurrentIndex(index)
        
        # Sekme başlığını güncelle
        browser.loadFinished.connect(lambda _, i=index, b=browser: 
                                    self.tabs.setTabText(i, b.page().title()[:15]))
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()
    
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.current_browser().setUrl(QUrl(url))
    
    def navigate_home(self):
        self.current_browser().setUrl(QUrl("https://www.google.com"))
    
    def update_url_bar(self, q=None):
        if q:
            self.url_bar.setText(q.toString())
            self.add_to_history(q.toString())
        else:
            self.url_bar.setText(self.current_browser().url().toString())
    
    def add_to_history(self, url):
        if url not in self.history:
            self.history.append(url)
            self.settings.setValue("history", self.history)
    
    def add_to_favorites(self):
        url = self.current_browser().url().toString()
        title = self.current_browser().page().title()
        
        if url not in self.favorites:
            self.favorites.append({"title": title, "url": url})
            self.settings.setValue("favorites", self.favorites)
            QMessageBox.information(self, "Favori Eklendi", f"'{title}' favorilere eklendi!")
    
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        
        new_tab_action = context_menu.addAction("Yeni Sekme Aç")
        new_tab_action.triggered.connect(self.add_new_tab)
        
        view_history = context_menu.addAction("Geçmişi Göster")
        view_history.triggered.connect(self.show_history)
        
        view_favorites = context_menu.addAction("Favorileri Göster")
        view_favorites.triggered.connect(self.show_favorites)
        
        context_menu.exec_(event.globalPos())
    
    def show_history(self):
        history_msg = "\n".join(self.history[-10:]) if self.history else "Geçmiş boş."
        QMessageBox.information(self, "Geçmiş", history_msg)
    
    def show_favorites(self):
        if not self.favorites:
            QMessageBox.information(self, "Favoriler", "Henüz favori eklenmedi.")
            return
        
        fav_menu = QMenu(self)
        for fav in self.favorites:
            action = fav_menu.addAction(fav["title"])
            action.triggered.connect(lambda _, url=fav["url"]: self.current_browser().setUrl(QUrl(url)))
        
        fav_menu.exec_(self.mapToGlobal(self.url_bar.pos()))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = AdvancedBrowser()
    browser.show()
    sys.exit(app.exec_())