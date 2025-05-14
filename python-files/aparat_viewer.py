
import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time, random, requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

success_count = 0
fail_count = 0
running = False

def get_proxies():
    try:
        res = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=3000&country=all")
        return res.text.strip().split('\n')
    except:
        return []

def start_viewing(video_url, view_count, log_text):
    global success_count, fail_count, running
    success_count = 0
    fail_count = 0
    running = True
    proxies = get_proxies()
    log_text.insert(tk.END, f"تعداد پروکسی دریافت‌شده: {len(proxies)}\n")

    for i in range(view_count):
        if not running:
            break
        proxy = random.choice(proxies) if proxies else None
        Thread(target=watch_video, args=(video_url, proxy, i+1, log_text)).start()
        time.sleep(1)

def watch_video(url, proxy, idx, log_text):
    global success_count, fail_count
    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        if proxy:
            options.add_argument(f'--proxy-server=http://{proxy}')
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(15)
        driver.get(url)
        time.sleep(10)
        driver.quit()
        success_count += 1
        log_text.insert(tk.END, f"[{idx}] موفق\n")
    except Exception as e:
        fail_count += 1
        log_text.insert(tk.END, f"[{idx}] ناموفق\n")

def stop():
    global running
    running = False

def gui():
    root = tk.Tk()
    root.title("افزایش بازدید آپارات")
    root.geometry("400x450")

    tk.Label(root, text="لینک ویدیو:").pack()
    url_entry = tk.Entry(root, width=50)
    url_entry.pack()

    tk.Label(root, text="تعداد بازدید:").pack()
    count_entry = tk.Entry(root, width=10)
    count_entry.pack()

    log_text = tk.Text(root, height=15)
    log_text.pack()

    def start_btn():
        try:
            url = url_entry.get()
            count = int(count_entry.get())
            log_text.delete(1.0, tk.END)
            Thread(target=start_viewing, args=(url, count, log_text)).start()
        except:
            messagebox.showerror("خطا", "لطفاً ورودی‌ها را درست وارد کنید.")

    tk.Button(root, text="شروع", command=start_btn, bg="green", fg="white").pack(pady=5)
    tk.Button(root, text="توقف", command=stop, bg="red", fg="white").pack()

    root.mainloop()

if __name__ == "__main__":
    gui()
