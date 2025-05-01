
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def extract_emails_from_website(driver, url):
    emails = set()
    try:
        driver.get(url)
        time.sleep(5)
        page_text = driver.find_element("tag name", "body").text
        found_emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", page_text)
        emails.update(found_emails)
    except Exception as e:
        print(f"[ERROR] Could not process {url}: {e}")
    return emails

def scrape_emails_from_websites(websites):
    driver = setup_driver()
    results = []

    for site in websites:
        print(f"Scraping {site}...")
        emails = extract_emails_from_website(driver, site)
        if emails:
            print(f"  Found: {emails}")
        else:
            print("  No emails found.")
        for email in emails:
            results.append({"Website": site, "Email": email})

    driver.quit()
    return results

def save_to_excel(data, filename="emails.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"✅ Emails saved to {filename}")

if __name__ == "__main__":
    website_list = [
        "https://www.hntravel.com/",
        "http://www.sonomatravelservice.com/",
        "https://www.signaturetravelnetwork.com/",
        "http://calitravel.com/"
    ]

    email_data = scrape_emails_from_websites(website_list)
    save_to_excel(email_data)
