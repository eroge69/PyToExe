import tkinter as tk
from tkinter import messagebox
import random
import string
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import imaplib
import email
import re
import zipfile
import io

class TikTokSignupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TikTok Signup Automation")
        self.root.geometry("400x600")

        # Initialize credentials
        self.credentials = self.load_credentials()
        self.email_credentials = self.load_email_credentials()
        self.current_email_index = 0  # Track current email index

        # Proxy settings
        self.proxy_host = "77.91.66.247"
        self.proxy_port = 30137  # Integer, not string
        self.proxy_user = "JsibMakRgg"
        self.proxy_pass = "fCtrtPT9OW"

        # GUI Elements
        tk.Label(root, text="Email (from mail.txt):").pack(pady=5)
        self.email_entry = tk.Entry(root, width=40)
        self.email_entry.pack(pady=5)
        if self.email_credentials:  # Load first email from mail.txt
            self.email_entry.insert(0, self.email_credentials[0]['email'])

        tk.Label(root, text="Generated Birthday:").pack(pady=5)
        self.birthday_label = tk.Label(root, text=self.get_birthday_text())
        self.birthday_label.pack(pady=5)

        tk.Label(root, text="Generated Password:").pack(pady=5)
        self.password_label = tk.Label(root, text=self.generate_password())  # Generate new password
        self.password_label.pack(pady=5)

        tk.Label(root, text="Generated Username:").pack(pady=5)
        self.username_label = tk.Label(root, text=self.generate_username())
        self.username_label.pack(pady=5)

        tk.Button(root, text="Start Signup", command=self.start_signup).pack(pady=20)
        tk.Button(root, text="Next Email", command=self.load_next_email).pack(pady=10)

    def generate_password(self):
        """Generate a password of 8-20 characters with letters, digits, and special characters."""
        length = random.randint(8, 20)
        special_chars = "!@#$%^&*()_+-=[]{}|;:'\",.<>/?`~"
        password = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
            random.choice(special_chars)
        ]
        all_chars = string.ascii_letters + string.digits + special_chars
        for _ in range(length - 4):
            password.append(random.choice(all_chars))
        random.shuffle(password)
        return ''.join(password)

    def generate_username(self):
        """Generate a random username of 2-24 characters."""
        prefixes = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Echo', 'Falcon', 'Ghost', 'Raven']
        suffixes = ['Storm', 'Blaze', 'Frost', 'Shadow', 'Warden', 'Mystic']
        mid_chars = ''.join(random.choices(string.ascii_lowercase, k=random.randint(2, 4)))
        username = (
            f"{random.choice(prefixes)}"
            f"{mid_chars}"
            f"{random.choice(suffixes) if random.random() > 0.5 else ''}"
            f"{random.randint(100, 99999)}"
        )[:24]
        return username

    def generate_random_user_agent(self):
        """Generate a random User-Agent string for desktop browsers and platforms."""
        browsers = [
            {
                'name': 'Chrome',
                'template': (
                    'Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/{chrome_version}.0.0.0 Safari/537.36'
                ),
                'versions': [range(90, 120)]
            },
            {
                'name': 'Firefox',
                'template': (
                    'Mozilla/5.0 ({platform}; rv:{firefox_version}.0) Gecko/20100101 '
                    'Firefox/{firefox_version}.0'
                ),
                'versions': [range(80, 115)]
            },
            {
                'name': 'Edge',
                'template': (
                    'Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/{chrome_version}.0.0.0 Safari/537.36 Edg/{edge_version}.0.0.0'
                ),
                'versions': [range(90, 120), range(90, 120)]  # Chrome and Edge version
            },
            {
                'name': 'Safari',
                'template': (
                    'Mozilla/5.0 ({platform}) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                    'Version/{safari_version} Safari/605.1.15'
                ),
                'versions': [range(14, 17)]
            }
        ]

        platforms = [
            'Windows NT 10.0; Win64; x64',
            'Windows NT 11.0; Win64; x64',
            'Macintosh; Intel Mac OS X 10_15_7',
            'Macintosh; Intel Mac OS X 11_2_3'
        ]

        # Select random browser and platform
        browser = random.choice(browsers)
        platform = random.choice(platforms)

        # Generate version numbers
        if browser['name'] == 'Chrome':
            chrome_version = random.choice(browser['versions'][0])
            user_agent = browser['template'].format(
                platform=platform,
                chrome_version=chrome_version
            )
        elif browser['name'] == 'Firefox':
            firefox_version = random.choice(browser['versions'][0])
            user_agent = browser['template'].format(
                platform=platform,
                firefox_version=firefox_version
            )
        elif browser['name'] == 'Edge':
            chrome_version = random.choice(browser['versions'][0])
            edge_version = random.choice(browser['versions'][1])
            user_agent = browser['template'].format(
                platform=platform,
                chrome_version=chrome_version,
                edge_version=edge_version
            )
        elif browser['name'] == 'Safari':
            safari_version = random.choice(browser['versions'][0])
            user_agent = browser['template'].format(
                platform=platform,
                safari_version=f'{safari_version}.0'
            )

        return user_agent

    def load_credentials(self):
        """Load or generate credentials (excluding password)."""
        if os.path.exists('credentials.txt'):
            with open('credentials.txt', 'r') as f:
                return json.load(f)
        else:
            credentials = {
                'month': random.choice(['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                                       'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']),
                'day': str(random.randint(1, 28)),
                'year': str(random.randint(1980, 2000)),
                'username': self.generate_username()
            }
            with open('credentials.txt', 'w') as f:
                json.dump(credentials, f)
            return credentials

    def load_email_credentials(self):
        """Load email credentials from mail.txt."""
        credentials = []
        try:
            with open('mail.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        email, password = line.split(':')
                        credentials.append({'email': email, 'password': password})
            return credentials
        except FileNotFoundError:
            messagebox.showerror("Error", "mail.txt not found in the script directory.")
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Error reading mail.txt: {str(e)}")
            return []

    def load_next_email(self):
        """Load the next email from mail.txt into the entry field."""
        if not self.email_credentials:
            messagebox.showerror("Error", "No emails available in mail.txt.")
            return
        self.current_email_index = (self.current_email_index + 1) % len(self.email_credentials)
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, self.email_credentials[self.current_email_index]['email'])

    def get_birthday_text(self):
        """Format birthday text."""
        return f"{self.credentials['month']} {self.credentials['day']}, {self.credentials['year']}"

    def fetch_verification_code(self, email_address, email_password):
        """Fetch verification code from email using IMAP."""
        try:
            mail = imaplib.IMAP4_SSL("imap.notletters.com", 993)
            mail.login(email_address, email_password)
            mail.select("inbox")
            _, data = mail.search(None, '(FROM "noreply@account.tiktok.com")')
            if not data[0]:
                print("No emails found from noreply@account.tiktok.com")
                return None
            email_id = data[0].split()[-1]
            _, data = mail.fetch(email_id, "(RFC822)")
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            for part in email_message.walk():
                if part.get_content_type() == "text/html":
                    body = part.get_payload(decode=True).decode()
                    match = re.search(r'\b\d{6}\b', body)
                    if match:
                        return match.group(0)
            print("No 6-digit code found in the email")
            return None
        except Exception as e:
            print(f"Error fetching email: {str(e)}")
            return None
        finally:
            try:
                mail.logout()
            except:
                pass

    def select_custom_dropdown(self, driver, wait, selector, value):
        """Select value from custom dropdown."""
        try:
            dropdown = wait.until(EC.element_to_be_clickable(selector))
            dropdown.click()
            option_selector = (By.XPATH, f'//div[@role="option" and contains(., "{value}")]')
            option = wait.until(EC.element_to_be_clickable(option_selector))
            option.click()
        except Exception as e:
            print(f"Error selecting {value}: {str(e)}")

    def create_proxy_extension(self):
        """Create a Chrome extension to handle proxy authentication using Manifest V3."""
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 3,
            "name": "Proxy Auth Extension",
            "permissions": [
                "proxy",
                "webRequest",
                "webRequestAuthProvider",
                "storage",
                "<all_urls>"
            ],
            "host_permissions": [
                "<all_urls>"
            ],
            "background": {
                "service_worker": "background.js"
            },
            "minimum_chrome_version": "88.0"
        }
        """

        background_js = f"""
        chrome.proxy.settings.set(
            {{
                value: {{
                    mode: "fixed_servers",
                    rules: {{
                        singleProxy: {{
                            scheme: "http",
                            host: "{self.proxy_host}",
                            port: {self.proxy_port}
                        }},
                        bypassList: ["localhost"]
                    }}
                }},
                scope: "regular"
            }},
            () => {{}}
        );

        chrome.webRequest.onAuthRequired.addListener(
            (details) => {{
                return {{
                    authCredentials: {{
                        username: "{self.proxy_user}",
                        password: "{self.proxy_pass}"
                    }}
                }};
            }},
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """

        # Create a temporary directory for the extension
        extension_dir = os.path.join(os.getcwd(), "proxy_auth_extension")
        if not os.path.exists(extension_dir):
            os.makedirs(extension_dir)

        # Write manifest.json
        with open(os.path.join(extension_dir, "manifest.json"), "w") as f:
            f.write(manifest_json)

        # Write background.js
        with open(os.path.join(extension_dir, "background.js"), "w") as f:
            f.write(background_js)

        # Create a zip file for the extension
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(os.path.join(extension_dir, "manifest.json"), "manifest.json")
            zip_file.write(os.path.join(extension_dir, "background.js"), "background.js")
        zip_buffer.seek(0)

        # Save the zip file
        zip_path = os.path.join(os.getcwd(), "proxy_auth_extension.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_buffer.getvalue())

        return zip_path

    def start_signup(self):
        """Initiate the signup process."""
        email_address = self.email_entry.get().strip()
        if not email_address:
            messagebox.showerror("Error", "Please enter an email address.")
            return

        # Find email password from mail.txt
        email_password = None
        for cred in self.email_credentials:
            if cred['email'] == email_address:
                email_password = cred['password']
                break
        if not email_password:
            messagebox.showerror("Error", f"Password for {email_address} not found in mail.txt.")
            return

        # Generate new credentials for this signup
        password = self.generate_password()
        self.credentials['username'] = self.generate_username()
        self.password_label.config(text=password)
        self.username_label.config(text=self.credentials['username'])
        with open('credentials.txt', 'w') as f:
            json.dump(self.credentials, f)

        # Setup Selenium with proxy and random User-Agent
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # Add random User-Agent
        user_agent = self.generate_random_user_agent()
        chrome_options.add_argument(f'user-agent={user_agent}')

        proxy_extension = self.create_proxy_extension()
        chrome_options.add_extension(proxy_extension)

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)

        try:
            driver.get("https://www.tiktok.com/signup/phone-or-email/email")

            # Select birthday
            self.select_custom_dropdown(
                driver, wait,
                (By.XPATH, '//div[contains(@class, "DivSelectLabel") and contains(., "Месяц")]'),
                self.credentials['month']
            )
            self.select_custom_dropdown(
                driver, wait,
                (By.XPATH, '//div[contains(@class, "DivSelectLabel") and contains(., "День")]'),
                self.credentials['day']
            )
            self.select_custom_dropdown(
                driver, wait,
                (By.XPATH, '//div[contains(@class, "DivSelectLabel") and contains(., "Год")]'),
                self.credentials['year']
            )

            # Input email
            email_input = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//input[@placeholder="Адрес эл. почты"]')
            ))
            email_input.send_keys(email_address)

            # Input password
            password_input = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//input[@placeholder="Пароль"]')
            ))
            password_input.send_keys(password)

            # Send code
            send_code_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-e2e="send-code-button"]')
            ))
            send_code_btn.click()

            # Fetch verification code
            max_attempts = 5
            attempt = 0
            final_code = None
            while attempt < max_attempts and not final_code:
                time.sleep(10)
                final_code = self.fetch_verification_code(email_address, email_password)
                attempt += 1

            if not final_code:
                messagebox.showerror("Error", "Failed to fetch verification code after multiple attempts.")
                return

            # Input verification code
            code_input = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//input[@placeholder="Введите 6-значный код"]')
            ))
            code_input.send_keys(final_code)

            # Submit form
            submit_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[type="submit"]')
            ))
            submit_btn.click()

            # Wait for potential redirect to username page
            time.sleep(5)

            # Check if on username page and input username
            if "create-username" in driver.current_url:
                username_input = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//input[@placeholder="Имя пользователя"]')
                ))
                username_input.send_keys(self.credentials['username'])

                # Submit username form
                try:
                    username_submit_btn = wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, 'button[type="submit"]')
                    ))
                    username_submit_btn.click()
                except Exception as e:
                    print(f"Error submitting username: {str(e)}")

            time.sleep(10)
            messagebox.showinfo("Success", "Signup process completed!")
            self.load_next_email()  # Automatically load next email after success

        except Exception as e:
            messagebox.showerror("Error", f"Signup failed: {str(e)}")
        finally:
            driver.quit()
            # Clean up proxy extension files
            try:
                os.remove(proxy_extension)
                extension_dir = os.path.join(os.getcwd(), "proxy_auth_extension")
                for file in os.listdir(extension_dir):
                    os.remove(os.path.join(extension_dir, file))
                os.rmdir(extension_dir)
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = TikTokSignupApp(root)
    root.mainloop()