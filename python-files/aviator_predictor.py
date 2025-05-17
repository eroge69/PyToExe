import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# Setup Chrome options
options = Options()
options.add_argument("--headless")  # Run in background
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Start browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://1wngpg.win/casino/game/aviator")

print("🔄 Loading Aviator game... Please wait 30 seconds...")
time.sleep(30)  # Wait for site to load

def fetch_last_numbers():
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    spans = soup.select("span.crash-point")
    numbers = [float(span.text.replace('x', '')) for span in spans if span.text.replace('x', '').replace('.', '', 1).isdigit()]
    return numbers[:20]

def predict_next(numbers):
    if len(numbers) < 2:
        return None
    avg = sum(numbers) / len(numbers)
    trend = numbers[-1] - numbers[-2]
    prediction = avg + (trend * 0.3)
    return round(prediction, 2)

while True:
    try:
        numbers = fetch_last_numbers()
        prediction = predict_next(numbers)

        now = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{now}] Last numbers: {numbers}")
        if prediction:
            print(f"⚠️ Predicted Next Number: {prediction}x")
        else:
            print("⚠️ Not enough data to predict.")

        time.sleep(30)

    except Exception as e:
        print(f"❌ Error: {e}")
        break

driver.quit()
