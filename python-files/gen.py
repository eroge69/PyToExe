import random, string, time, requests
from camoufox.sync_api import Camoufox

# ====== Configuration ======
Config = {
    "webhook_url": "https://discord.com/api/webhooks/1376458929382359060/2D-uOGvb5CkUXWHXuGH5YiU1D4uIFoe2CXJOW13aMOwe0YS888xIQKBGf-p-s7LoYrqF"
}

# ====== Color Codes ======
class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

# ====== Load Data ======
with open("usernames.txt", encoding="utf-8") as f:
    usernames_list = [line.strip() for line in f.readlines()]
with open("name.txt", encoding="utf-8") as f:
    names_list = [line.strip() for line in f.readlines()]

# ====== Utilities ======
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_password(length=12):
    charset = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(charset, k=length))

def create_temp_email():
    alias = random_string()
    return f"{alias}@y.dldweb.info", alias

def generate_realistic_username():
    first = random.choice(usernames_list).lower()
    last = random.choice(names_list).lower()
    number = str(random.randint(10, 99))
    base = f"{first}{last}{number}"
    username = ''.join(filter(str.isalnum, base))[:10]
    while len(username) < 10:
        username += random.choice(string.digits)
    return username

def wait_for_selector(page, selector, timeout=10000):
    try:
        page.locator(selector).wait_for(timeout=timeout)
        return True
    except Exception:
        return False

def timestamp():
    return f"[{time.strftime('%H:%M:%S')}]"

def send_to_webhook(email, password, token_clean):
    webhook_url = Config["webhook_url"]
    payload = {"content": f"{email}:{password}:{token_clean}"}
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print(f"{Color.GREEN}[WEBHOOK]{Color.RESET} Sent successfully.")
        else:
            print(f"{Color.RED}[WEBHOOK] Failed. Status: {response.status_code}, Response: {response.text}{Color.RESET}")
    except Exception as e:
        print(f"{Color.RED}[WEBHOOK ERROR] {e}{Color.RESET}")

def fill_discord_form(page, email, username, password):
    print(f"{Color.YELLOW}[*] Navigating to Discord registration...{Color.RESET}")
    page.goto("https://discord.com/register", timeout=60000)
    time.sleep(5)

    if not wait_for_selector(page, "input[name='email']", timeout=15000):
        raise Exception("Registration form did not load properly.")

    page.fill("input[name='email']", email)
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)

    page.locator("#react-select-2-input").fill("May")
    page.keyboard.press("Enter")

    page.locator("#react-select-3-input").fill("15")
    page.keyboard.press("Enter")

    page.locator("#react-select-4-input").fill(str(random.randint(1995, 2005)))
    page.keyboard.press("Enter")

    def handle_response(response):
        if "auth/register" in response.url:
            if response.status == 429:
                retry_after = response.headers.get("retry-after")
                if retry_after:
                    wait_sec = float(retry_after)
                    print(f"{Color.RED}[RATE LIMIT]{Color.RESET} Waiting {wait_sec:.1f}s...")
                    for i in range(int(wait_sec), 0, -1):
                        print(f"[WAIT] {i} seconds remaining...", end='\r')
                        time.sleep(1)
                    print(" " * 60, end='\r')
                    try:
                        page.click("button[type='submit']")
                        print(f"{Color.YELLOW}[RETRY]{Color.RESET} Re-submitting after wait.")
                    except Exception as e:
                        print(f"{Color.RED}[RETRY ERROR] {e}{Color.RESET}")

    page.on("response", handle_response)
    page.click("button[type='submit']")
    print(f"{Color.CYAN}[FORM SUBMITTED]{Color.RESET} Solve CAPTCHA manually...")

def create_discord_account():
    email, yopmail_user = create_temp_email()
    username = generate_realistic_username()
    password = generate_password()

    try:
        with Camoufox(headless=False) as browser:
            page = browser.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

            try:
                fill_discord_form(page, email, username, password)
            except Exception as form_err:
                print(f"{Color.RED}[FORM ERROR] {form_err}{Color.RESET}")
                page.close()
                browser.close()
                return

            input(f"{Color.YELLOW}[STEP 1]{Color.RESET} Solve CAPTCHA then press ENTER...")

            page.goto("https://discord.com/channels/@me", timeout=30000)
            time.sleep(3)

            token = page.evaluate("() => window.localStorage.getItem('token')")
            if token and isinstance(token, str):
                token_clean = token.strip('"')

                print(f"{Color.GREEN}[SUCCESS]{Color.RESET} Account created.")
                send_to_webhook(email, password, token_clean)

                print(f"{Color.CYAN}[ACTION]{Color.RESET} Verify email at: {Color.YELLOW}{yopmail_user}@y.dldweb.info{Color.RESET}")
                page.goto(f"https://yopmail.com/en/?login={yopmail_user}", timeout=60000)
                input(f"{Color.YELLOW}[STEP 2]{Color.RESET} Verify email manually and press ENTER...")

                print(f"{timestamp()} {Color.CYAN}[INFO]{Color.RESET} Restarting in 5 seconds...")
                time.sleep(5)

                page.close()
                browser.close()

                cooldown = random.randint(30, 60)
                print(f"{timestamp()} {Color.YELLOW}[COOLDOWN]{Color.RESET} Waiting {cooldown} seconds...")
                time.sleep(cooldown)
            else:
                print(f"{Color.RED}[ERROR]{Color.RESET} Token not found. CAPTCHA or registration may have failed.")
                page.close()
                browser.close()

    except Exception as e:
        print(f"{Color.RED}[ERROR] {e}{Color.RESET}")

if __name__ == "__main__":
    while True:
        create_discord_account()
