# email_extractor.py - FIXED FOR WINDOWS 10/11
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import sys

# Configuration
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36"
]
DELAY = 3  # Safer delay
TIMEOUT = 15

class EmailExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
        
    def extract_emails(self, text):
        return set(re.findall(
            r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", 
            text, re.IGNORECASE
        ))
    
    def get_website_text(self, url):
        try:
            resp = self.session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Error: {str(e)}")
            return ""
    
    def run(self):
        print("=== Email Extractor ===")
        print("1. Extract from URL\n2. Google Search")
        choice = input("Choose (1/2): ").strip()
        
        if choice == "1":
            url = input("Enter URL (include http://): ").strip()
            text = self.get_website_text(url)
            emails = self.extract_emails(text)
        elif choice == "2":
            query = input("Search term (e.g., 'B2B software'): ").strip()
            text = self.get_website_text(f"https://www.google.com/search?q={query}")
            emails = self.extract_emails(text)
        else:
            input("Invalid choice. Press Enter to exit...")
            return
            
        if emails:
            pd.DataFrame(sorted(emails), columns=["Email"]).to_csv("emails.csv", index=False)
            print(f"Saved {len(emails)} emails to emails.csv")
        else:
            print("No emails found")
        input("Press Enter to exit...")

if __name__ == "__main__":
    EmailExtractor().run()