import sys
import os
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit,
    QTabWidget, QWidget, QVBoxLayout, QTextEdit, QFileDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown


class NavegadorGeneralizado(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Nav Gen 1.0')
        self.setGeometry(100, 100, 1200, 800)

        self.historico = []  # Histórico geral
        self.ram_memoria = {}  # "RAM" para URLs por aba
        self.anonimo = {}  # Flags de aba anônima

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.fechar_aba)
        self.tabs.currentChanged.connect(self.atualizar_url_bar)
        self.setCentralWidget(self.tabs)

        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QAction('←', self)
        back_btn.triggered.connect(self.voltar)
        navbar.addAction(back_btn)

        forward_btn = QAction('→', self)
        forward_btn.triggered.connect(self.ir)
        navbar.addAction(forward_btn)

        reload_btn = QAction('⟳', self)
        reload_btn.triggered.connect(self.recarregar)
        navbar.addAction(reload_btn)

        new_tab_btn = QAction('+', self)
        new_tab_btn.triggered.connect(lambda _: self.nova_aba())
        navbar.addAction(new_tab_btn)

        anon_btn = QAction('Modo Anônimo', self)
        anon_btn.triggered.connect(self.nova_aba_anonima)
        navbar.addAction(anon_btn)

        open_file_btn = QAction('📂', self)
        open_file_btn.triggered.connect(self.abrir_arquivo)
        navbar.addAction(open_file_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navegar)
        navbar.addWidget(self.url_bar)

        self.nova_aba(url='https://google.com')

    def nova_aba(self, url='https://google.com'):
        browser = QWebEngineView()
        browser.setUrl(QUrl(url))
        browser.urlChanged.connect(lambda u, b=browser: self.url_mudou(u, b))
        index = self.tabs.addTab(browser, 'Nova Aba')
        self.tabs.setCurrentIndex(index)
        self.anonimo[index] = False  # Marca aba como não anônima
        self.ram_memoria[index] = [url]  # Começa com URL inicial
        return browser

    def nova_aba_anonima(self):
        browser = QWebEngineView()
        browser.setUrl(QUrl('https://duckduckgo.com'))
        browser.urlChanged.connect(lambda u, b=browser: self.url_mudou(u, b))
        index = self.tabs.addTab(browser, 'Anônimo')
        self.tabs.setCurrentIndex(index)
        self.anonimo[index] = True  # Marca como anônima
        self.ram_memoria[index] = []  # Sem salvar nada
        return browser

    def url_mudou(self, url, browser):
        i = self.tabs.indexOf(browser)
        if i == -1:
            return

        host = url.host() + (" (Anon)" if self.anonimo.get(i, False) else "")
        self.tabs.setTabText(i, host)
        if i == self.tabs.currentIndex():
            self.url_bar.setText(url.toString())
        
        if not self.anonimo.get(i, False):
            self.historico.append(url.toString())
            self.ram_memoria[i].append(url.toString())

    def atualizar_url_bar(self, i):
        if i == -1:
            return
        browser = self.tabs.widget(i)
        if browser:
            self.url_bar.setText(browser.url().toString())
            if not self.anonimo.get(i, False):
                print(f"[DEBUG] RAM da aba {i}:")
                for link in self.ram_memoria.get(i, []):
                    print(f"   > {link}")

    def navegar(self):
        url = self.url_bar.text()
        if not url.startswith('http'):
            url = 'http://' + url
        browser = self.tabs.currentWidget()
        if browser:
            browser.setUrl(QUrl(url))

    def voltar(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.back()

    def ir(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.forward()

    def recarregar(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.reload()

    def fechar_aba(self, i):
        if self.tabs.count() == 1:
            self.close()
        else:
            self.tabs.removeTab(i)
            self.ram_memoria.pop(i, None)
            self.anonimo.pop(i, None)

    def abrir_arquivo(self):
        caminho, _ = QFileDialog.getOpenFileName(self, 'Abrir arquivo', '', 'Arquivos (*.html *.htm *.md *.pdf *.txt)')
        if caminho:
            if caminho.endswith('.pdf'):
                self.abrir_pdf(caminho)
            elif caminho.endswith('.md'):
                self.abrir_markdown(caminho)
            else:
                browser = self.tabs.currentWidget()
                if browser:
                    browser.setUrl(QUrl.fromLocalFile(caminho))

    def abrir_pdf(self, caminho):
        if sys.platform == "win32":
            os.startfile(caminho)
        elif sys.platform == "darwin":
            os.system(f"open '{caminho}'")
        else:
            os.system(f"xdg-open '{caminho}'")

    def abrir_markdown(self, caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            md_text = f.read()

        html = markdown.markdown(md_text)

        janela_md = QWidget()
        janela_md.setWindowTitle(f'Markdown - {os.path.basename(caminho)}')
        janela_md.setGeometry(150, 150, 800, 600)

        layout = QVBoxLayout()
        editor = QTextEdit()
        editor.setReadOnly(True)
        editor.setHtml(html)
        layout.addWidget(editor)

        janela_md.setLayout(layout)
        janela_md.show()
        self.janela_md = janela_md


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1a001f;
        }

        QToolBar {
            background-color: #2c0033;
            spacing: 12px;
            padding: 6px;
            border-bottom: 2px solid #800040;
        }

        QToolButton {
            color: #ff4d6d;
            background: transparent;
            border: none;
            font-size: 20px;
            padding: 6px;
        }

        QToolButton:hover {
            color: #ff99aa;
            background-color: #4d0033;
            border-radius: 8px;
        }

        QLineEdit {
            background-color: #3d003d;
            color: #ffcce0;
            border: 1px solid #ff4d6d;
            border-radius: 10px;
            padding: 6px 12px;
            font-size: 16px;
            min-width: 300px;
        }

        QLineEdit:focus {
            border: 2px solid #ff6688;
            background-color: #4d004d;
        }
    """)
    navegador = NavegadorGeneralizado()
    navegador.show()
    sys.exit(app.exec_())
