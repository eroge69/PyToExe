import webview
import os
from tkinter import filedialog
from tkinter import Tk
import os
from dotenv import load_dotenv
from urllib.parse import urljoin

load_dotenv()

def create_window():
    window = webview.create_window(
        title='Anarholis Browser',
        url=os.getenv('UPLOAD_URL'),
        width=1280,
        height=720
    )

    # Инициализация Tkinter для диалоговых окон
    root = Tk()
    root.withdraw()

    # Обработчик для скачивания файлов
    def download_handler(download):
        file_path = filedialog.asksaveasfilename(
            initialdir=os.path.expanduser("~"),
            title="Сохранить файл",
            filetypes=[("Все файлы", "*.*")]
        )
        
        if file_path:
            download.destination = file_path
            download.start()

    # Настройка обработчика загрузок
    def setup_downloads():
        window.download_triggered = False  # Флаг для однократной инициализации
        window.evaluate_js("""
            // Перехватываем все клики по ссылкам
            document.addEventListener('click', function(e) {
                const target = e.target.closest('a');
                if (target && target.href) {
                    window.pywebview.api.handle_download(target.href);
                    e.preventDefault();
                }
            }, true);
            // Перехват программных запросов
            const originalFetch = window.fetch;
            window.fetch = async function(url, options) {
                if (url.includes('/file_download/')) {
                    window.pywebview.api.handle_file_download(url);
                    return new Response(null, {status: 200});
                }
                return originalFetch(url, options);
            };
        """)

    # API для обработки скачивания
    class Api:
        @staticmethod
        def handle_download(self, file_url):  # Исправленное имя метода
            try:
                if self.download_triggered:
                    return

                absolute_url = urljoin(self.base_url, file_url)
                
                if not absolute_url.startswith(f'{self.base_url}/file_download/'):
                    return

                self.download_triggered = True
                download = self.window.download(absolute_url)
                download.events.completed += self._reset_trigger
                download.start(self._download_handler)

            except Exception as e:
                print(f'Download error: {e}')
                self._reset_trigger()

        def _download_handler(self, download):
            try:
                file_name = download.url.split('/file_download/')[-1]
                file_path = filedialog.asksaveasfilename(
                    initialfile=file_name,
                    title="Сохранить файл",
                    filetypes=[("Все файлы", "*.*")]
                )

                if file_path:
                    download.destination = file_path
            except Exception as e:
                print(f'Save dialog error: {e}')
            finally:
                self._reset_trigger()

        def _reset_trigger(self, *args):
            self.download_triggered = False

    api = window._js_api

    # Добавляем кнопки навигации
    def add_navigation_buttons():
        js = """
        const toolbar = document.createElement('div');
        toolbar.style = `
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 999999;
            background: rgba(240,240,240,0.8);
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            gap: 10px;
        `;
        
        toolbar.innerHTML = `
            <button onclick="window.history.back()">← Назад</button>
            <button onclick="window.history.forward()">→ Вперед</button>
            <button onclick="window.location.reload()">⟳ Обновить</button>
        `;
        
        document.body.prepend(toolbar);
        """
        window.evaluate_js(js)

    # Подключаем обработчики
    window.events.loaded += lambda: (
        add_navigation_buttons(),
        setup_downloads()
    )

    webview.start(gui='edgechromium', http_server=True, debug=True, user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')

if __name__ == '__main__':
    create_window()