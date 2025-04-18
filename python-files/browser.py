import sys
import time
import threading
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit,
    QSpinBox, QLabel
)
from PyQt5.QtCore import Qt
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
import zipfile
import requests


class BrowserAutomation(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browser Automation with Proxy Support")
        self.setGeometry(100, 100, 600, 720)

        self.pause_flag = threading.Event()
        self.pause_flag.set()

        self.max_profiles = 4
        self.semaphore = threading.Semaphore(self.max_profiles)

        layout = QVBoxLayout()

        self.url_box = QTextEdit()
        self.url_box.setPlaceholderText("Enter URLs here (one per line)...")

        self.proxy_box = QTextEdit()
        self.proxy_box.setPlaceholderText("Enter proxies here (ip:port or ip:port:user:pass)...")

        self.views_label = QLabel("Views per URL:")
        self.views_spin = QSpinBox()
        self.views_spin.setMinimum(1)
        self.views_spin.setMaximum(1000)
        self.views_spin.setValue(1)

        self.xpath_label = QLabel("XPath to Click (Optional):")
        self.xpath_box = QTextEdit()
        self.xpath_box.setPlaceholderText("Enter XPath here (e.g. //a[1])")

        self.start_button = QPushButton("Start Automation")
        self.start_button.setStyleSheet("background-color: #1877F2; color: white; font-weight: bold;")
        self.start_button.clicked.connect(self.start_automation)

        self.pause_button = QPushButton("⏸ Pause")
        self.pause_button.clicked.connect(self.toggle_pause)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.proxy_count_label = QLabel("Proxies Entered: 0")

        layout.addWidget(QLabel("🗭 URLs:"))
        layout.addWidget(self.url_box)
        layout.addWidget(QLabel("🌐 Proxies:"))
        layout.addWidget(self.proxy_box)
        layout.addWidget(self.views_label)
        layout.addWidget(self.views_spin)
        layout.addWidget(self.xpath_label)
        layout.addWidget(self.xpath_box)
        layout.addWidget(self.start_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.proxy_count_label)
        layout.addWidget(QLabel("📜 Logs:"))
        layout.addWidget(self.log)

        self.setLayout(layout)

    def toggle_pause(self):
        if self.pause_flag.is_set():
            self.pause_flag.clear()
            self.pause_button.setText("▶️ Resume")
            self.log.append("⏸ Automation paused.")
        else:
            self.pause_flag.set()
            self.pause_button.setText("⏸ Pause")
            self.log.append("▶️ Automation resumed.")

    def validate_proxy(self, proxy):
        try:
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=5)
            return response.status_code == 200
        except:
            return False

    def start_automation(self):
        threading.Thread(target=self.run_automation, daemon=True).start()

    def run_automation(self):
        urls = [url.strip() for url in self.url_box.toPlainText().splitlines() if url.strip()]
        raw_proxies = [p.strip() for p in self.proxy_box.toPlainText().splitlines() if p.strip()]
        xpath_to_click = self.xpath_box.toPlainText().strip()

        if not urls or not raw_proxies:
            self.log.append("⚠️ URLs or Proxies missing.")
            return

        valid_proxies = []
        for proxy in raw_proxies:
            self.log.append(f"🔍 Validating proxy: {proxy}")
            if self.validate_proxy(proxy):
                valid_proxies.append(proxy)
                self.log.append(f"✅ Proxy valid: {proxy}")
            else:
                self.log.append(f"❌ Proxy invalid: {proxy}")

        if not valid_proxies:
            self.log.append("❌ No valid proxies found.")
            return

        self.proxy_count_label.setText(f"Proxies Entered: {len(valid_proxies)}")

        for i, proxy in enumerate(valid_proxies):
            while not self.pause_flag.is_set():
                time.sleep(1)
            url = urls[i % len(urls)]
            threading.Thread(target=self.launch_browser, args=(url, proxy, xpath_to_click), daemon=True).start()
            time.sleep(random.randint(5, 10))  # Delay between launching profiles

    def launch_browser(self, url, proxy, xpath_to_click):
        with self.semaphore:
            try:
                options = uc.ChromeOptions()
                width = random.randint(800, 1200)
                height = random.randint(600, 1000)
                options.add_argument(f"--window-size={width},{height}")
                options.add_argument("--no-first-run")
                options.add_argument("--disable-popup-blocking")
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...")

                if "@" in proxy or proxy.count(":") == 3:
                    ip, port, user, pwd = proxy.split(":")
                    proxy_str = f"{ip}:{port}"
                    options.add_argument(f"--proxy-server=http://{proxy_str}")
                    options.add_extension(self.create_proxy_auth_extension(ip, port, user, pwd))
                else:
                    options.add_argument(f"--proxy-server=http://{proxy}")

                driver = uc.Chrome(options=options)
                driver.execute_script("window.open('about:blank', '_blank');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(url)
                driver.switch_to.window(driver.window_handles[0])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                time.sleep(3)
                self.scroll_page(driver, down=True)
                self.scroll_page(driver, down=False)

                if xpath_to_click:
                    try:
                        link = driver.find_element(By.XPATH, xpath_to_click)
                        link.send_keys("\n")
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(random.randint(3, 5))
                        self.scroll_page(driver, down=True)
                        time.sleep(3)
                        self.scroll_page(driver, down=False)
                    except Exception as e:
                        self.log.append(f"XPath click error: {e}")

                time.sleep(random.randint(30, 50))
                driver.quit()
            except Exception as e:
                self.log.append(f"Browser error: {e}")

    def scroll_page(self, driver, down=True):
        try:
            scroll_pause = 1.5
            height = driver.execute_script("return document.body.scrollHeight")
            viewport = driver.execute_script("return window.innerHeight")
            step = viewport // 2
            y_positions = range(0, height, step) if down else range(height, 0, -step)

            for y in y_positions:
                driver.execute_script(f"window.scrollTo(0, {y});")
                time.sleep(scroll_pause)
        except Exception as e:
            self.log.append(f"Scroll error: {e}")

    def create_proxy_auth_extension(self, proxy_host, proxy_port, proxy_user, proxy_pass):
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy", "tabs", "unlimitedStorage", "storage", "<all_urls>", "webRequest", "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: parseInt({proxy_port})
                }},
                bypassList: ["localhost"]
            }}
        }};
        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        chrome.webRequest.onAuthRequired.addListener(
            function(details, callbackFn) {{
                callbackFn({{
                    authCredentials: {{username: "{proxy_user}", password: "{proxy_pass}"}}
                }});
            }},
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """

        plugin_file = f'proxy_auth_plugin_{proxy_host}_{proxy_port}.zip'
        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        return plugin_file


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserAutomation()
    window.show()
    sys.exit(app.exec_())