
import os
import time
import difflib
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class UploadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("מעלה תמונות GIS")
        self.image_folder = ""
        self.csv_path = ""

        # ממשק גרפי
        tk.Button(root, text="בחר קובץ CSV", command=self.load_csv).pack(pady=5)
        tk.Button(root, text="בחר תיקיית תמונות", command=self.load_folder).pack(pady=5)
        tk.Button(root, text="התחל העלאה", command=self.run_upload).pack(pady=10)

        self.log = scrolledtext.ScrolledText(root, width=70, height=20)
        self.log.pack(padx=10, pady=10)

    def log_message(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.root.update()

    def load_csv(self):
        self.csv_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        self.log_message(f"📄 קובץ נטען: {self.csv_path}")

    def load_folder(self):
        self.image_folder = filedialog.askdirectory()
        self.log_message(f"📁 תיקייה נבחרה: {self.image_folder}")

    def find_image(self, street, number):
        target = f"{street}{number}".replace(" ", "").lower()
        files = os.listdir(self.image_folder)
        best_match = None
        highest_ratio = 0.0
        for file in files:
            name, ext = os.path.splitext(file)
            clean_name = name.replace(" ", "").lower()
            ratio = difflib.SequenceMatcher(None, target, clean_name).ratio()
            if ratio > 0.6 and ratio > highest_ratio:
                highest_ratio = ratio
                best_match = os.path.join(self.image_folder, file)
        return best_match

    def run_upload(self):
        if not self.csv_path or not self.image_folder:
            messagebox.showwarning("חסר מידע", "בחר קובץ CSV ותיקיית תמונות.")
            return

        try:
            df = pd.read_csv(self.csv_path, encoding='utf-8')
        except Exception as e:
            self.log_message(f"❌ שגיאה בקריאת הקובץ: {e}")
            return

        # פתיחת דפדפן
        options = Options()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(service=Service(), options=options)
        wait = WebDriverWait(driver, 20)
        driver.get("https://buildings.unlimited.net.il/gisibc/portal.aspx")

        for index, row in df.iterrows():
            uniq_id = str(row['Uniq_id'])
            street = str(row['שם רחוב'])
            number = str(row['בניין'])

            image_path = self.find_image(street, number)
            if not image_path:
                self.log_message(f"❌ לא נמצאה תמונה מתאימה עבור: {street} {number}")
                continue

            try:
                wait.until(EC.presence_of_element_located((By.ID, "txtaddressid"))).clear()
                driver.find_element(By.ID, "txtaddressid").send_keys(uniq_id)
                wait.until(EC.element_to_be_clickable((By.ID, "btnGetBuildings"))).click()
                wait.until(EC.element_to_be_clickable((By.ID, f"chk{uniq_id}"))).click()

                wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='קבלן מבצע']"))).click()
                wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='סיור בבניין']"))).click()
                wait.until(EC.presence_of_element_located((By.ID, "file_building"))).send_keys(image_path)
                wait.until(EC.element_to_be_clickable((By.ID, "jsSaveConnect"))).click()

                wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='פריסה']"))).click()
                wait.until(EC.presence_of_element_located((By.ID, "prisa6_file"))).send_keys(image_path)
                wait.until(EC.element_to_be_clickable((By.ID, "jsSaveConnect"))).click()

                wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "חזרה למסך חיפוש"))).click()
                self.log_message(f"✅ תמונה הועלתה בהצלחה עבור: {street} {number}")

            except Exception as e:
                self.log_message(f"⚠️ שגיאה בכתובת {street} {number}: {e}")
                continue

        driver.quit()
        self.log_message("🎉 סיום תהליך!")

if __name__ == "__main__":
    root = tk.Tk()
    app = UploadApp(root)
    root.mainloop()
