import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QToolBar, QAction, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kendi Tarayıcım")
        self.setGeometry(100, 100, 800, 600)
        
        # WebView (Tarayıcı Ekranı)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        
        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        # Toolbar (Geri, İleri, Yenile)
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        back_button = QAction("Geri", self)
        back_button.triggered.connect(self.browser.back)
        toolbar.addAction(back_button)
        
        forward_button = QAction("İleri", self)
        forward_button.triggered.connect(self.browser.forward)
        toolbar.addAction(forward_button)
        
        reload_button = QAction("Yenile", self)
        reload_button.triggered.connect(self.browser.reload)
        toolbar.addAction(reload_button)
        
        toolbar.addWidget(self.url_bar)
        
        # Sayfa yüklendiğinde URL'yi güncelle
        self.browser.urlChanged.connect(self.update_url)
        
        # Ana Layout
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))
    
    def update_url(self, q):
        self.url_bar.setText(q.toString())

app = QApplication(sys.argv)
browser = SimpleBrowser()
browser.show()
sys.exit(app.exec_())