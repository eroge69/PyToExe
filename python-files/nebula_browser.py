import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QProgressBar
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon

class CustomBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nebula Browser ✨")
        self.setWindowIcon(QIcon("browser_icon.png"))  # Optional: your icon here

        self.setGeometry(100, 100, 1200, 800)

        self.browser = QWebEngineView()

        # --- Load Beautiful Custom Homepage ---
        self.load_custom_homepage()

        self.setCentralWidget(self.browser)

        # --- Navigation Bar ---
        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.load_custom_homepage)
        navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # --- Loading Progress Bar ---
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(200)
        navbar.addWidget(self.progress)
        self.progress.hide()

        # Connect signals
        self.browser.urlChanged.connect(self.update_url)
        self.browser.loadProgress.connect(self.update_progress)
        self.browser.loadStarted.connect(self.start_loading)
        self.browser.loadFinished.connect(self.end_loading)

        # Style progress bar
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: #222;
            }
            QProgressBar::chunk {
                background-color: #1e88e5;
                width: 20px;
            }
        """)

    def load_custom_homepage(self):
        self.browser.setHtml("""
        <html>
        <head>
            <title>Welcome to Nebula</title>
            <style>
                body {
                    background: linear-gradient(135deg, #1d1f27, #090a0f);
                    color: white;
                    font-family: 'Poppins', sans-serif;
                    text-align: center;
                    margin: 0;
                    padding: 0;
                    height: 100vh;
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                }

                h1 {
                    font-size: 3rem;
                    margin-bottom: 10px;
                    animation: fadeIn 2s ease;
                }

                p {
                    font-size: 1.2rem;
                    margin-bottom: 40px;
                    color: #aaa;
                    animation: fadeIn 3s ease;
                }

                input {
                    width: 400px;
                    padding: 15px;
                    border-radius: 30px;
                    border: none;
                    outline: none;
                    font-size: 18px;
                    background: #2c2f36;
                    color: white;
                    text-align: center;
                    box-shadow: 0 0 10px #1e88e5, 0 0 20px #1565c0;
                    transition: 0.3s ease;
                }

                input:focus {
                    box-shadow: 0 0 20px #64b5f6, 0 0 30px #1e88e5;
                }

                button {
                    margin-top: 20px;
                    padding: 12px 30px;
                    background-color: #1e88e5;
                    color: white;
                    font-size: 18px;
                    border: none;
                    border-radius: 30px;
                    cursor: pointer;
                    transition: background 0.3s ease;
                }

                button:hover {
                    background-color: #1565c0;
                }

                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(-20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            </style>
        </head>
        <body>
            <h1>Nebula Browser</h1>
            <p>Explore the universe of the web ✨</p>
            <form action="" id="searchForm">
                <input type="text" id="searchInput" placeholder="Search or enter URL...">
                <br>
                <button type="submit">Go</button>
            </form>

            <script>
                const form = document.getElementById('searchForm');
                form.addEventListener('submit', function(event) {
                    event.preventDefault();
                    const query = document.getElementById('searchInput').value;
                    if (query.startsWith('http')) {
                        window.location.href = query;
                    } else {
                        window.location.href = 'https://duckduckgo.com/?q=' + encodeURIComponent(query);
                    }
                });
            </script>
        </body>
        </html>
        """)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def start_loading(self):
        self.progress.show()

    def update_progress(self, progress):
        self.progress.setValue(progress)

    def end_loading(self):
        self.progress.hide()

# --- Launch App ---
app = QApplication(sys.argv)
app.setApplicationName("Nebula Browser")
window = CustomBrowser()
window.show()
sys.exit(app.exec_())
