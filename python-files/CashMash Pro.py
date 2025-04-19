import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
from datetime import datetime
import subprocess
import random
from playwright.sync_api import sync_playwright, TimeoutError
import winsound
import re
import sys
import traceback

# مسیر اصلی برنامه (نسبی)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SAVE_LOG_PATH = os.path.join(BASE_PATH, "SAVE LOG")
SAVE_TRUE_KEY_PATH = os.path.join(BASE_PATH, "SAVE TRUE KEY")
FAILD_KEY_PATH = os.path.join(BASE_PATH, "FAILD KEY")

# متغیرهای سراسری برای شمارش
total_keys_generated = 0
true_keys = 0
failed_keys = 0
auto_scan_enabled = True  # همیشه روشن
start_window = None
start_log = None
page = None
browser = None
playwright = None
running = False
canvas_frame_id = None

# تابع برای چک کردن وابستگی‌ها
def check_dependencies():
    missing = []
    try:
        import tkinter
    except ImportError:
        missing.append("tkinter (try: 'pip install tk')\n    Note: On Linux, you may need 'sudo apt-get install python3-tk'")
    
    try:
        from PIL import Image, ImageTk
    except ImportError:
        missing.append("Pillow (try: 'pip install Pillow')")
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        missing.append("playwright (try: 'pip install playwright' and then 'playwright install')")
    
    try:
        import winsound
    except ImportError:
        missing.append("winsound (Note: This is Windows-only. If on Linux/Mac, the program may still run but beeping won't work.)")
    
    if missing:
        error_message = "Missing dependencies:\n" + "\n".join(missing)
        messagebox.showerror("Dependency Error", error_message)
        sys.exit(1)

# تابع برای چک کردن فایل‌های مورد نیاز
def check_required_files():
    required_files = [
        ("KEY.txt", "Contains the list of words for generating phrases"),
        ("BgFile1.png", "Background image for the main window"),
        ("BGPAGE2.jpg", "Background image for the second window"),
        ("LOGO.png", "Logo image for the main window"),
        ("LOGO2.png", "Logo image for the second window"),
        ("start_icon.png", "Start button icon"),
        ("stop_icon.png", "Stop button icon"),
        ("CLICK MOUSE.bat", "Batch file for additional operations")
    ]
    missing = []
    for file_name, description in required_files:
        file_path = os.path.join(BASE_PATH, file_name)
        if not os.path.exists(file_path):
            missing.append(f"{file_name}: {description} (Path: {file_path})")
    
    if missing:
        error_message = "Missing required files:\n" + "\n".join(missing)
        messagebox.showerror("File Error", error_message)
        sys.exit(1)

# تابع برای لاگ کردن ارورها به فایل
def log_error_to_file(error_message):
    error_log_path = os.path.join(BASE_PATH, "error_log.txt")
    with open(error_log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {error_message}\n")
    print(f"Error logged to {error_log_path}")

# خواندن کلمات از KEY.txt
def load_words():
    key_path = os.path.join(BASE_PATH, "KEY.txt")
    if os.path.exists(key_path):
        try:
            with open(key_path, "r", encoding="utf-8") as f:
                words = [line.strip() for line in f if line.strip()]
            if not words:
                messagebox.showwarning("Warning", "KEY.txt is empty! Program cannot proceed without words.")
                sys.exit(1)
            return words
        except Exception as e:
            log_error_to_file(f"Error reading KEY.txt: {e}")
            messagebox.showerror("Error", f"Error reading KEY.txt: {e}\nProgram cannot proceed.")
            sys.exit(1)
    else:
        messagebox.showerror("Error", f"KEY.txt not found at {key_path}\nProgram cannot proceed.")
        sys.exit(1)

# خواندن ترکیب‌های اشتباه از FAILD KEY
def load_failed_combinations():
    failed_combinations = set()
    if os.path.exists(FAILD_KEY_PATH):
        for filename in os.listdir(FAILD_KEY_PATH):
            filepath = os.path.join(FAILD_KEY_PATH, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    words = [line.split(": ")[1].strip() for line in f.readlines() if ": " in line]
                    if len(words) == 24:
                        failed_combinations.add(tuple(words))
            except Exception as e:
                log_error_to_file(f"Error reading failed combination {filepath}: {e}")
    return failed_combinations

# تابع برای باز کردن و آپدیت پنجره لاگ
def create_log_window(parent, height=8, width=80):
    log_frame = tk.Frame(parent, bg="#1a1a1a")
    log_frame.pack(pady=10)
    
    log_text = tk.Text(log_frame, height=height, width=width, bg="black", fg="white", font=("Consolas", 10))
    log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=log_text.yview)
    log_text.configure(yscrollcommand=log_scroll.set)
    
    log_scroll.pack(side="right", fill="y")
    log_text.pack(side="left", fill="both", expand=True)
    
    log_text.insert(tk.END, "Log started...\n")
    log_text.tag_configure("purple", foreground="purple")
    log_text.tag_configure("green", foreground="green")
    log_text.tag_configure("red", foreground="red")
    log_text.tag_configure("stats", foreground="white")
    log_text.tag_configure("highlight", foreground="yellow")  # برای موجودی غیر صفر
    return log_text

# تابع برای جدا کردن لاگ به پنجره جدید
def detach_log(log_widget):
    log_window = tk.Toplevel(root)
    log_window.title("CashMash Logs")
    log_window.geometry("800x600")
    log_window.configure(bg="black")
    
    new_log_text = tk.Text(log_window, bg="black", fg="white", font=("Consolas", 10))
    new_log_text.pack(expand=True, fill="both")
    new_log_text.insert(tk.END, log_widget.get("1.0", tk.END))
    
    log_widget.insert(tk.END, "Log detached to new window...\n")
    log_widget.see(tk.END)

# تابع برای ذخیره لاگ‌ها
def save_logs(log_widget, save_path=SAVE_LOG_PATH, custom_name=None):
    if not os.path.exists(save_path):
        try:
            os.makedirs(save_path)
        except Exception as e:
            log_error_to_file(f"Error creating directory {save_path}: {e}")
            return None, False
    
    now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    filename = custom_name if custom_name else f"CashMash_Log_{now}.txt"
    filepath = os.path.join(save_path, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(log_widget.get("1.0", tk.END))
        return filename, True
    except Exception as e:
        log_error_to_file(f"Error saving log to {filepath}: {e}")
        return None, False

# تابع برای ذخیره خودکار موقع بستن
def auto_save_logs(log_widget):
    filename, success = save_logs(log_widget, SAVE_LOG_PATH)
    if success:
        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Auto-saved main log as {filename}\n")
    else:
        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to auto-save main log!\n", "red")
    log_widget.see(tk.END)

# تابع برای اجرای CLICK MOUSE.bat
def run_click_mouse(log_widget):
    bat_path = os.path.join(BASE_PATH, "CLICK MOUSE.bat")
    if os.path.exists(bat_path):
        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Running CLICK MOUSE.bat...\n", "purple")
        log_widget.see(tk.END)
        try:
            process = subprocess.Popen(bat_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            if stdout:
                log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] CLICK MOUSE.bat output:\n{stdout}\n")
            if stderr:
                log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] CLICK MOUSE.bat errors:\n{stderr}\n", "red")
            
            log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] DONE !!\n")
        except Exception as e:
            log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error running CLICK MOUSE.bat: {e}\n", "red")
        log_widget.see(tk.END)
    else:
        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error: CLICK MOUSE.bat not found!\n", "red")
        log_widget.see(tk.END)

# تابع برای بستن برنامه
def on_closing():
    global running
    running = False
    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Exit\n")
    auto_save_logs(log_widget)
    try:
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
    except Exception as e:
        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error closing browser: {e}\n", "red")
    root.destroy()

# آپدیت لاگ اصلی با تعداد کلیدها
def update_main_log(log_widget):
    log_widget.delete("2.0", "3.0")
    log_widget.insert("2.0", f"Keys Generated: {total_keys_generated} | True Key = {true_keys} | Faild Key = {failed_keys}\n", "stats")
    log_widget.delete("3.0", "4.0")
    log_widget.insert("3.0", f"AUTO SCAN KEY 🔑 : {'On' if auto_scan_enabled else 'Off'}\n")

# تابع برای آپدیت بک‌گراند صفحه دوم
def update_background_second(event, canvas, window):
    width = window.winfo_width()
    height = window.winfo_height()
    
    try:
        bg_img = Image.open(os.path.join(BASE_PATH, "BGPAGE2.jpg"))
        bg_img = bg_img.resize((width // 2, height // 2), Image.Resampling.LANCZOS).resize((width, height), Image.Resampling.NEAREST)
        bg_photo = ImageTk.PhotoImage(bg_img)
        canvas.delete("bg")
        canvas.create_image(width // 2, height // 2, image=bg_photo, tags="bg")
        canvas.lower("bg")
        window.bg_photo = bg_photo
    except Exception as e:
        log_error_to_file(f"Error updating second window background: {e}")
    
    canvas.coords(canvas_frame_id, width // 2, 0)

# تابع برای تغییر حالت AUTO SCAN
def toggle_auto_scan(main_log_widget, indicator):
    global auto_scan_enabled
    auto_scan_enabled = not auto_scan_enabled
    indicator.delete("circle")
    indicator.create_oval(2, 2, 18, 18, fill="#00FF00" if auto_scan_enabled else "#FF3333", outline="#FFFFFF", tags="circle")
    update_main_log(main_log_widget)

# تابع برای پاک کردن FAILD KEY
def delete_failed_keys(main_log_widget, used_combinations):
    try:
        if os.path.exists(FAILD_KEY_PATH):
            for filename in os.listdir(FAILD_KEY_PATH):
                filepath = os.path.join(FAILD_KEY_PATH, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
            os.rmdir(FAILD_KEY_PATH)
            os.makedirs(FAILD_KEY_PATH)
        used_combinations.clear()
        main_log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] FAILD KEY folder cleared! 🗑️\n", "red")
        main_log_widget.see(tk.END)
    except PermissionError:
        main_log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error: Permission denied to clear FAILD KEY folder!\n", "red")
        main_log_widget.see(tk.END)
    except Exception as e:
        main_log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error clearing FAILD KEY folder: {e}\n", "red")
        main_log_widget.see(tk.END)

# تابع برای بازگشت به صفحه اصلی سایت (بهبودیافته)
def reset_to_main_page(log_widget):
    global page
    max_attempts = 3  # حداکثر تعداد تلاش برای ریست کردن صفحه
    retry_count = 0

    while retry_count < max_attempts:
        retry_count += 1
        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Reset to main page attempt {retry_count}/{max_attempts}\n", "purple")
        
        try:
            if page and not page.is_closed():
                # تلاش برای رفتن به صفحه اصلی
                page.goto("https://wallet.tonkeeper.com", timeout=30000)
                log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Navigated to main page: https://wallet.tonkeeper.com\n", "purple")
            else:
                log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Page closed, reopening browser...\n", "red")
                if not init_browser(log_widget):
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to reopen browser, stopping...\n", "red")
                    return False
                continue

            # تلاش برای پیدا کردن و کلیک دکمه "Get Started"
            for attempt in range(1, max_attempts + 1):
                try:
                    page.wait_for_selector("button:has-text('Get started')", timeout=10000)
                    page.click("button:has-text('Get started')")
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Clicked 'Get Started' button on attempt {attempt}\n", "purple")
                    break
                except TimeoutError:
                    if attempt < max_attempts:
                        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Get Started button not found on attempt {attempt}, retrying...\n", "red")
                        page.wait_for_timeout(2000)
                    else:
                        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Get Started button not found after {max_attempts} attempts, retrying reset...\n", "red")
                        continue
            
            # تلاش برای پیدا کردن و کلیک دکمه "Existing Wallet"
            for attempt in range(1, max_attempts + 1):
                try:
                    page.wait_for_selector("button:has-text('Existing Wallet')", timeout=10000)
                    page.click("button:has-text('Existing Wallet')")
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Clicked 'Existing Wallet' button on attempt {attempt}\n", "purple")
                    break
                except TimeoutError:
                    if attempt < max_attempts:
                        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Existing Wallet button not found on attempt {attempt}, retrying...\n", "red")
                        page.wait_for_timeout(2000)
                    else:
                        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Existing Wallet button not found after {max_attempts} attempts, retrying reset...\n", "red")
                        continue
            
            # چک کردن فرم 24 کلمه برای اطمینان از ریست موفق
            try:
                page.wait_for_selector("div[wordsnumber='24']", timeout=10000)
                log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Reset successful, 24-word form found\n", "purple")
                page.wait_for_timeout(500)
                return True  # ریست با موفقیت انجام شد
            except TimeoutError:
                log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 24-word form not found after reset, retrying...\n", "red")
                continue

        except Exception as e:
            log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error resetting to main page: {e}\n", "red")
            continue
    
    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to reset to main page after {max_attempts} attempts, stopping...\n", "red")
    return False

# تابع برای باز کردن مرورگر
def init_browser(log_widget):
    global page, browser, playwright
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://wallet.tonkeeper.com", timeout=30000)
        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Opened website: https://wallet.tonkeeper.com\n", "purple")
        
        try:
            page.wait_for_selector("button:has-text('Get started')", timeout=10000)
            page.click("button:has-text('Get started')")
            log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Clicked 'Get Started' button\n", "purple")
        except Exception as e:
            log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error clicking 'Get Started' button: {e}\n", "red")
            return False
        
        try:
            page.wait_for_selector("button:has-text('Existing Wallet')", timeout=10000)
            page.click("button:has-text('Existing Wallet')")
            log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Clicked 'Existing Wallet' button\n", "purple")
            page.wait_for_timeout(500)
        except Exception as e:
            log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error clicking 'Existing Wallet' button: {e}\n", "red")
            return False
        
        return True
    except Exception as e:
        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error initializing browser: {e}\n", "red")
        try:
            if browser:
                browser.close()
            if playwright:
                playwright.stop()
        except:
            pass
        return False

# تابع برای دکمه استارت صفحه اول
def start_action(log_widget):
    global running, total_keys_generated, start_window, start_log
    running = False  # هنوز شروع نمی‌کنیم
    words = load_words()
    used_combinations = load_failed_combinations() if auto_scan_enabled else set()
    
    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Start button clicked! 🟢\n", "purple")
    try:
        winsound.Beep(800, 300)  # بوق برای استارت
        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Played beep for Start\n", "purple")
    except Exception as e:
        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error playing beep for Start: {e}\n", "red")
    log_widget.insert(tk.END, f"Keys Generated: {total_keys_generated} | True Key = {true_keys} | Faild Key = {failed_keys}\n", "stats")
    log_widget.insert(tk.END, f"AUTO SCAN KEY 🔑 : {'On' if auto_scan_enabled else 'Off'}\n")
    
    # فقط صفحه دوم باز بشه
    create_second_window(words, used_combinations, log_widget)

# تابع برای ساخت صفحه دوم
def create_second_window(words, used_combinations, main_log_widget):
    global start_window, start_log, canvas_frame_id
    if start_window and start_window.winfo_exists():
        start_window.destroy()
    
    start_window = tk.Toplevel(root)
    start_window.title("Word Generator")
    start_window.geometry("1000x800")
    
    start_canvas = tk.Canvas(start_window, highlightthickness=0)
    start_canvas.pack(fill="both", expand=True)
    try:
        bg_img = Image.open(os.path.join(BASE_PATH, "BGPAGE2.jpg"))
        bg_img = bg_img.resize((500, 400), Image.Resampling.LANCZOS).resize((1000, 800), Image.Resampling.NEAREST)
        bg_photo = ImageTk.PhotoImage(bg_img)
        start_canvas.create_image(500, 400, image=bg_photo, tags="bg")
        start_canvas.lower("bg")
        start_window.bg_photo = bg_photo
    except FileNotFoundError:
        log_error_to_file(f"Could not find BGPAGE2.jpg at {os.path.join(BASE_PATH, 'BGPAGE2.jpg')}")
    except Exception as e:
        log_error_to_file(f"Error loading second window background: {e}")
    
    main_frame = tk.Frame(start_canvas, bg="#1a1a1a")
    canvas_frame_id = start_canvas.create_window((500, 0), window=main_frame, anchor="n")
    
    logo2_path = os.path.join(BASE_PATH, "LOGO2.png")
    try:
        logo2_img = Image.open(logo2_path)
        logo2_img = logo2_img.resize((100, 100), Image.Resampling.LANCZOS)
        logo2_photo = ImageTk.PhotoImage(logo2_img)
        logo2_label = tk.Label(main_frame, image=logo2_photo, bg="#1a1a1a", cursor="hand2")
        logo2_label.pack(pady=10)
        logo2_label.bind("<Button-1>", lambda e: update_used_combinations(used_combinations, start_log))
        main_frame.logo2_photo = logo2_photo
    except FileNotFoundError:
        log_error_to_file(f"Could not find LOGO2.png at {logo2_path}")
    
    fields_frame = tk.Frame(main_frame, bg="#1a1a1a")
    fields_frame.pack(pady=10)
    
    fields = []
    for i in range(24):
        label = tk.Label(fields_frame, text=f"{i+1}:", bg="#1a1a1a", fg="white")
        label.grid(row=i // 4, column=(i % 4) * 2, padx=5, pady=5)
        entry = tk.Entry(fields_frame, width=15)
        entry.grid(row=i // 4, column=(i % 4) * 2 + 1, padx=5, pady=5)
        fields.append(entry)
    
    continue_button = tk.Button(main_frame, text="continue", command=lambda: check_words(fields, start_log, words, used_combinations, main_log_widget, start_window), bg="#1a1a1a", fg="white")
    continue_button.pack(pady=10)
    
    start_log = create_log_window(main_frame, height=5, width=80)
    
    button_frame = tk.Frame(main_frame, bg="#1a1a1a")
    button_frame.pack(pady=10)
    
    save_button = tk.Button(button_frame, text="🚀 SAVE 🚀", command=lambda: save_logs(start_log), bg="#1a1a1a", fg="white", font=("Arial", 12))
    save_button.pack(side="left", padx=5)
    
    auto_scan_button = tk.Button(button_frame, text="AUTO SCAN KEY SAVED", bg="#333333", fg="white", font=("Arial", 12, "bold"), borderwidth=0, relief="flat", padx=10, pady=5, activebackground="#555555")
    auto_scan_button.pack(side="left", padx=5)
    auto_scan_button.bind("<Button-1>", lambda e: toggle_auto_scan(main_log_widget, indicator))
    
    indicator = tk.Canvas(button_frame, width=20, height=20, bg="#1a1a1a", highlightthickness=0)
    indicator.pack(side="left", padx=5)
    indicator.create_oval(2, 2, 18, 18, fill="#00FF00" if auto_scan_enabled else "#FF3333", outline="#FFFFFF", tags="circle")
    indicator.bind("<Button-1>", lambda e: toggle_auto_scan(main_log_widget, indicator))
    
    del_button = tk.Button(button_frame, text="DEL FAILD KEY", bg="#FF3333", fg="white", font=("Arial", 12, "bold"), borderwidth=0, relief="flat", padx=10, pady=5, activebackground="#FF5555")
    del_button.pack(side="left", padx=5)
    del_button.bind("<Button-1>", lambda e: delete_failed_keys(main_log_widget, used_combinations))
    
    # دکمه‌های ST و SP
    st_sp_frame = tk.Frame(main_frame, bg="#1a1a1a")
    st_sp_frame.pack(pady=5)
    
    st_button = tk.Button(st_sp_frame, text="ST", command=lambda: start_filling(fields, words, used_combinations, start_log, main_log_widget, start_window), bg="#00FF00", fg="black", font=("Arial", 12, "bold"), borderwidth=0, relief="flat", padx=10, pady=5)
    st_button.pack(side="left", padx=5)
    
    sp_button = tk.Button(st_sp_frame, text="SP", command=lambda: stop_filling(start_log), bg="#FF3333", fg="white", font=("Arial", 12, "bold"), borderwidth=0, relief="flat", padx=10, pady=5)
    sp_button.pack(side="left", padx=5)
    
    # دکمه TEST
    test_button = tk.Button(st_sp_frame, text="TEST", command=lambda: test_words(fields, start_log, words, used_combinations, main_log_widget, start_window), bg="#FFFF00", fg="black", font=("Arial", 12, "bold"), borderwidth=0, relief="flat", padx=10, pady=5)
    test_button.pack(side="left", padx=5)
    
    start_window.bind("<Configure>", lambda e: update_background_second(e, start_canvas, start_window))

# تابع برای شروع پر کردن کلمات
def start_filling(fields, words, used_combinations, start_log, main_log_widget, start_window):
    global running, page, browser, playwright
    running = True
    start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Started filling words\n", "purple")
    try:
        winsound.Beep(800, 300)  # بوق برای شروع
        start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Played beep for ST\n", "purple")
    except Exception as e:
        start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error playing beep for ST: {e}\n", "red")
    
    # باز کردن مرورگر
    if not page or page.is_closed():
        if not init_browser(start_log):
            start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to initialize browser\n", "red")
            running = False
            return
    
    def schedule_fill_words():
        global running
        max_retries = 3
        retry_count = 0

        while running and words and start_window.winfo_exists() and retry_count < max_retries:
            try:
                if not page or page.is_closed():
                    start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Page closed, reopening browser...\n", "red")
                    if not init_browser(start_log):
                        start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to reopen browser, stopping ST...\n", "red")
                        running = False
                        return
                
                fill_words(fields, words, used_combinations, start_log, main_log_widget, start_window)
                root.after(1000, schedule_fill_words)  # تأخیر 1 ثانیه برای جلوگیری از فشار به مرورگر
                return  # از تابع خارج می‌شیم تا حلقه بعدی
            except Exception as e:
                retry_count += 1
                start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error in ST loop (attempt {retry_count}/{max_retries}): {e}\n", "red")
                if retry_count < max_retries:
                    start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Retrying ST loop...\n", "purple")
                    if not reset_to_main_page(start_log):
                        start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to reset page, stopping ST...\n", "red")
                        running = False
                        return
                else:
                    start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Max retries reached in ST loop, stopping...\n", "red")
                    running = False
                    return
        
        if not running or not words or not start_window.winfo_exists():
            start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ST stopped: Page closed or window destroyed\n", "red")
            running = False
    
    root.after(100, schedule_fill_words)

# تابع برای توقف پر کردن کلمات
def stop_filling(start_log):
    global running
    running = False
    start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Stopped filling words\n", "purple")
    start_log.see(tk.END)

# تابع برای پر کردن کلمات
def fill_words(fields, words, used_combinations, start_log, main_log_widget, start_window):
    global total_keys_generated
    if auto_scan_enabled:
        used_combinations.update(load_failed_combinations())
    selected_words = random.sample(words, min(24, len(words)))
    combination = tuple(selected_words)
    if combination in used_combinations and auto_scan_enabled:
        return
    used_combinations.add(combination)
    total_keys_generated += 1
    update_main_log(main_log_widget)
    
    for i, entry in enumerate(fields):
        entry.delete(0, tk.END)
        if i < len(selected_words):
            entry.insert(0, selected_words[i])
    
    start_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Generated: ")
    for i, word in enumerate(selected_words, 1):
        start_log.insert(tk.END, f"{i}: {word}  ")
    start_log.insert(tk.END, "\n")
    start_log.see(tk.END)
    check_words(fields, start_log, words, used_combinations, main_log_widget, start_window, auto=True)

# تابع برای تست کلمات مشخص
def test_words(fields, log_widget, words, used_combinations, main_log_widget, start_window):
    global page
    if not page or page.is_closed():
        if not init_browser(log_widget):
            log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to initialize browser for TEST\n", "red")
            return
    
    # کلمات تست مشخص
    test_words_list = [
        "solution", "enough", "trophy", "trumpet", "spoil", "match", "alter", "quality",
        "trigger", "soccer", "shock", "exist", "cactus", "note", "bracket", "recall",
        "loan", "cable", "cool", "bag", "crumble", "warfare", "blush", "cricket"
    ]
    
    # پر کردن فیلدها با کلمات تست
    for i, entry in enumerate(fields):
        entry.delete(0, tk.END)
        if i < len(test_words_list):
            entry.insert(0, test_words_list[i])
    
    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Testing specified words: ")
    for i, word in enumerate(test_words_list, 1):
        log_widget.insert(tk.END, f"{i}: {word}  ")
    log_widget.insert(tk.END, "\n")
    log_widget.see(tk.END)
    
    check_words(fields, log_widget, words, used_combinations, main_log_widget, start_window, auto=False, test_mode=True)

# تابع برای آپدیت ترکیب‌های استفاده‌شده
def update_used_combinations(used_combinations, log_widget):
    failed_combinations = load_failed_combinations()
    used_combinations.update(failed_combinations)
    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Scanned FAILD KEY folder. Loaded {len(failed_combinations)} failed combinations.\n")
    log_widget.see(tk.END)

# تابع برای چک کردن کلمات (بهبودیافته)
def check_words(fields, log_widget, words, used_combinations, main_log_widget, window, auto=False, test_mode=False):
    global true_keys, failed_keys, page
    current_words = [entry.get().strip() for entry in fields]
    
    # چک کردن اینکه همه 24 فیلد پر شده باشن
    if len(current_words) != 24 or not all(current_words):
        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error: Not all 24 fields are filled, skipping...\n", "red")
        return
    
    is_correct = False
    max_test_attempts = 3 if test_mode else 1  # برای TEST تا 3 بار تلاش می‌کنیم
    
    for attempt in range(1, max_test_attempts + 1):
        if test_mode:
            log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] TEST attempt {attempt}/{max_test_attempts}\n", "purple")
        
        try:
            if not page or page.is_closed():
                log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Page closed, reopening browser...\n", "red")
                if not init_browser(log_widget):
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to reopen browser, stopping...\n", "red")
                    return
            
            log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Starting to sync words to website\n", "purple")
            
            # اطمینان از لود فرم 24 کلمه با تلاش اضافی
            max_form_attempts = 3
            for attempt_form in range(1, max_form_attempts + 1):
                try:
                    page.wait_for_selector("div[wordsnumber='24']", timeout=10000)
                    fields_elements = page.query_selector_all("div[wordsnumber='24'] input.sc-bHYtx.kdgTFO")
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(fields_elements)} input fields on attempt {attempt_form}\n", "purple")
                    if len(fields_elements) == 24:
                        break
                except TimeoutError:
                    if attempt_form < max_form_attempts:
                        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Form not found on attempt {attempt_form}, retrying...\n", "red")
                        page.wait_for_timeout(2000)
                    else:
                        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error: 24-word form not found after {max_form_attempts} attempts, resetting...\n", "red")
                        if not reset_to_main_page(log_widget):
                            log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to reset page, stopping...\n", "red")
                            return
            
            # پر کردن فرم وب‌سایت
            for i, field in enumerate(fields_elements):
                field.fill(current_words[i])
            
            # کلیک روی دکمه "Continue"
            page.click("button:has-text('Continue')")
            
            # چک کردن نتیجه
            try:
                page.wait_for_selector("text=Invalid recovery phrase", timeout=5000)
                log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Invalid recovery phrase detected\n", "red")
                failed_keys += 1
                update_main_log(main_log_widget)
                
                # ذخیره تو FAILD KEY
                if not os.path.exists(FAILD_KEY_PATH):
                    os.makedirs(FAILD_KEY_PATH)
                now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
                failed_filepath = os.path.join(FAILD_KEY_PATH, f"Failed_Key_{total_keys_generated}_{now}.txt")
                with open(failed_filepath, "w", encoding="utf-8") as f:
                    for i, word in enumerate(current_words, 1):
                        f.write(f"{i}: {word}\n")
                log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Saved to {failed_filepath}\n", "red")
                
                if not reset_to_main_page(log_widget):
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to reset page after invalid phrase\n", "red")
                    return
                
            except TimeoutError:
                # اگر پیام خطا ظاهر نشد، چک می‌کنیم که آیا صفحه "Choose Wallets" ظاهر شده
                try:
                    page.wait_for_selector("form.sc-jcUlRr.JIVwt", timeout=10000)
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Valid recovery phrase: Choose Wallets page detected\n", "green")
                    is_correct = True
                    true_keys += 1
                    update_main_log(main_log_widget)
                    
                    # شبیه‌سازی فشار دکمه SP
                    if auto:
                        stop_filling(log_widget)
                    
                    # استخراج اطلاعات کیف‌پول‌ها
                    wallet_elements = page.query_selector_all("div.sc-jHVeRl.kXDVak")
                    wallet_details = []
                    for elem in wallet_elements:
                        version = elem.query_selector("span.sc-jSguLX.egBbuV").inner_text()
                        address_balance = elem.query_selector("span.sc-kEjbdu.sc-dOFRUr.cCFujo.bsVYUI").inner_text()
                        wallet_details.append(f"{version}: {address_balance}")
                    
                    # ذخیره در SAVE TRUE KEY
                    if not os.path.exists(SAVE_TRUE_KEY_PATH):
                        os.makedirs(SAVE_TRUE_KEY_PATH)
                    now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
                    true_filepath = os.path.join(SAVE_TRUE_KEY_PATH, f"True_Key_{total_keys_generated}_{now}.txt")
                    with open(true_filepath, "w", encoding="utf-8") as f:
                        for i, word in enumerate(current_words, 1):
                            f.write(f"{i}: {word}\n")
                        f.write("\nWallet Details:\n")
                        for detail in wallet_details:
                            f.write(f"{detail}\n")
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Saved to {true_filepath} with wallet details\n", "green")
                    
                    try:
                        winsound.Beep(1000, 500)  # بوق برای موفقیت
                        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Played success beep\n", "green")
                    except Exception as e:
                        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error playing success beep: {e}\n", "red")
                    
                    # ادامه دادن به کار (راه‌اندازی مجدد پر کردن)
                    if auto:
                        global running
                        running = True
                        log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Resuming word filling after valid key\n", "purple")
                
                except TimeoutError:
                    # اگر صفحه "Choose Wallets" هم پیدا نشد، فرض می‌کنیم نامعتبر است
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Could not find Choose Wallets page, assuming invalid...\n", "red")
                    failed_keys += 1
                    update_main_log(main_log_widget)
                    if not os.path.exists(FAILD_KEY_PATH):
                        os.makedirs(FAILD_KEY_PATH)
                    now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
                    failed_filepath = os.path.join(FAILD_KEY_PATH, f"Failed_Key_{total_keys_generated}_{now}.txt")
                    with open(failed_filepath, "w", encoding="utf-8") as f:
                        for i, word in enumerate(current_words, 1):
                            f.write(f"{i}: {word}\n")
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Saved to {failed_filepath}\n", "red")
                
                if not reset_to_main_page(log_widget):
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to reset page after check\n", "red")
                    return
                
            break  # اگه به اینجا رسیدیم و خطایی نبود، از حلقه خارج می‌شیم
        
        except Exception as e:
            log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error during check (attempt {attempt}/{max_test_attempts}): {e}\n", "red")
            if attempt < max_test_attempts:
                log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Retrying check...\n", "purple")
                if not reset_to_main_page(log_widget):
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to reset page, stopping...\n", "red")
                    return
            else:
                log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Max retries reached, marking as failed...\n", "red")
                failed_keys += 1
                update_main_log(main_log_widget)
                if not os.path.exists(FAILD_KEY_PATH):
                    os.makedirs(FAILD_KEY_PATH)
                now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
                failed_filepath = os.path.join(FAILD_KEY_PATH, f"Failed_Key_{total_keys_generated}_{now}.txt")
                with open(failed_filepath, "w", encoding="utf-8") as f:
                    for i, word in enumerate(current_words, 1):
                        f.write(f"{i}: {word}\n")
                log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Saved to {failed_filepath}\n", "red")
                if not reset_to_main_page(log_widget):
                    log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Failed to reset page after max retries\n", "red")
                return
    
    log_widget.see(tk.END)

# تابع برای آپدیت بک‌گراند صفحه اصلی
def update_background(event, canvas, window):
    width = window.winfo_width()
    height = window.winfo_height()
    
    try:
        bg_img = Image.open(os.path.join(BASE_PATH, "BgFile1.png"))
        bg_img = bg_img.resize((width // 2, height // 2), Image.Resampling.LANCZOS).resize((width, height), Image.Resampling.NEAREST)
        bg_photo = ImageTk.PhotoImage(bg_img)
        canvas.delete("bg")
        canvas.create_image(width // 2, height // 2, image=bg_photo, tags="bg")
        canvas.lower("bg")
        window.bg_photo = bg_photo
    except Exception as e:
        log_error_to_file(f"Error updating main window background: {e}")

# تنظیمات اولیه و رابط کاربری اصلی
if __name__ == "__main__":
    # چک کردن وابستگی‌ها و فایل‌ها
    check_dependencies()
    check_required_files()
    
    # ساخت پنجره اصلی
    root = tk.Tk()
    root.title("CashMash Pro")
    root.geometry("1200x800")
    
    main_canvas = tk.Canvas(root, highlightthickness=0)
    main_canvas.pack(fill="both", expand=True)
    
    try:
        bg_img = Image.open(os.path.join(BASE_PATH, "BgFile1.png"))
        bg_img = bg_img.resize((600, 400), Image.Resampling.LANCZOS).resize((1200, 800), Image.Resampling.NEAREST)
        bg_photo = ImageTk.PhotoImage(bg_img)
        main_canvas.create_image(600, 400, image=bg_photo, tags="bg")
        main_canvas.lower("bg")
        root.bg_photo = bg_photo
    except FileNotFoundError:
        log_error_to_file(f"Could not find BgFile1.png at {os.path.join(BASE_PATH, 'BgFile1.png')}")
    
    main_frame = tk.Frame(main_canvas, bg="#1a1a1a")
    main_canvas.create_window((600, 400), window=main_frame, anchor="center")
    
    # لوگو
    logo_path = os.path.join(BASE_PATH, "LOGO.png")
    try:
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((150, 150), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(main_frame, image=logo_photo, bg="#1a1a1a")
        logo_label.pack(pady=20)
        main_frame.logo_photo = logo_photo
    except FileNotFoundError:
        log_error_to_file(f"Could not find LOGO.png at {logo_path}")
    
    # دکمه‌های Start و Stop
    button_frame = tk.Frame(main_frame, bg="#1a1a1a")
    button_frame.pack(pady=10)
    
    start_icon_path = os.path.join(BASE_PATH, "start_icon.png")
    stop_icon_path = os.path.join(BASE_PATH, "stop_icon.png")
    
    try:
        start_icon_img = Image.open(start_icon_path)
        start_icon_img = start_icon_img.resize((50, 50), Image.Resampling.LANCZOS)
        start_icon = ImageTk.PhotoImage(start_icon_img)
        start_button = tk.Button(button_frame, image=start_icon, command=lambda: start_action(log_widget), bg="#1a1a1a", borderwidth=0)
        start_button.pack(side="left", padx=10)
        button_frame.start_icon = start_icon
    except FileNotFoundError:
        log_error_to_file(f"Could not find start_icon.png at {start_icon_path}")
        start_button = tk.Button(button_frame, text="Start", command=lambda: start_action(log_widget), bg="#1a1a1a", fg="white")
        start_button.pack(side="left", padx=10)
    
    try:
        stop_icon_img = Image.open(stop_icon_path)
        stop_icon_img = stop_icon_img.resize((50, 50), Image.Resampling.LANCZOS)
        stop_icon = ImageTk.PhotoImage(stop_icon_img)
        stop_button = tk.Button(button_frame, image=stop_icon, command=lambda: stop_filling(log_widget), bg="#1a1a1a", borderwidth=0)
        stop_button.pack(side="left", padx=10)
        button_frame.stop_icon = stop_icon
    except FileNotFoundError:
        log_error_to_file(f"Could not find stop_icon.png at {stop_icon_path}")
        stop_button = tk.Button(button_frame, text="Stop", command=lambda: stop_filling(log_widget), bg="#1a1a1a", fg="white")
        stop_button.pack(side="left", padx=10)
    
    # لاگ اصلی
    log_widget = create_log_window(main_frame)
    
    # دکمه‌های اضافی
    extra_button_frame = tk.Frame(main_frame, bg="#1a1a1a")
    extra_button_frame.pack(pady=10)
    
    detach_button = tk.Button(extra_button_frame, text="DETACH LOG", command=lambda: detach_log(log_widget), bg="#1a1a1a", fg="white")
    detach_button.pack(side="left", padx=5)
    
    save_button = tk.Button(extra_button_frame, text="SAVE LOG", command=lambda: save_logs(log_widget), bg="#1a1a1a", fg="white")
    save_button.pack(side="left", padx=5)
    
    click_mouse_button = tk.Button(extra_button_frame, text="CLICK MOUSE", command=lambda: run_click_mouse(log_widget), bg="#1a1a1a", fg="white")
    click_mouse_button.pack(side="left", padx=5)
    
    # آپدیت بک‌گراند با تغییر اندازه
    root.bind("<Configure>", lambda e: update_background(e, main_canvas, root))
    
    # بستن برنامه
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # شروع برنامه
    root.mainloop()