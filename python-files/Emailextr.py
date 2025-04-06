# email_extractor_win.py - TESTED ON WINDOWS 10/11
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse
import time
import random
import sys

# Configuration
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36"
]
DELAY = 5  # Safer delay for Windows
TIMEOUT = 20  # Longer timeout for slow sites

class EmailExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
        
    def extract_emails(self, text):
        """Improved email regex for Windows"""
        return set(re.findall(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            text, re.IGNORECASE
        ))
    
    def get_website_text(self, url):
        """Safe webpage fetcher"""
        try:
            resp = self.session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""
    
    def google_search(self, query, pages=1):
        """Bypass simple bot detection"""
        results = set()
        for page in range(pages):
            try:
                url = f"https://www.google.com/search?q={query}&start={page*10}"
                html = self.get_website_text(url)
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract links safely
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('/url?q='):
                        real_url = href.split('&')[0][7:]
                        if any(x in real_url for x in ['google.com', 'facebook.com', 'linkedin.com']):
                            continue
                        print(f"Scanning: {real_url}")
                        text = self.get_website_text(real_url)
                        results.update(self.extract_emails(text))
                        time.sleep(DELAY)
            except Exception as e:
                print(f"Search error: {str(e)}")
        return results
    
    def run(self):
        print("1. Extract from URL\n2. Search by Keyword")
        choice = input("Choose (1/2): ").strip()
        
        if choice == "1":
            url = input("Enter URL (include http://): ").strip()
            text = self.get_website_text(url)
            emails = self.extract_emails(text)
        elif choice == "2":
            query = input("Enter search term: ").strip()
            emails = self.google_search(query)
        else:
            print("Invalid choice")
            return
            
        if emails:
            df = pd.DataFrame(sorted(emails), columns=["Email"])
            df.to_csv("extracted_emails.csv", index=False)
            print(f"Saved {len(emails)} emails to extracted_emails.csv")
        else:
            print("No emails found")

if __name__ == "__main__":
    EmailExtractor().run()