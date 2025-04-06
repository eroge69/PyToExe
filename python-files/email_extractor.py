import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse
import time
import random

# Configuration
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
]
DELAY = 3  # Seconds between requests
MAX_RESULTS = 1000  # Limit for safety

class EmailExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": random.choice(USER_AGENTS)})

    def extract_from_url(self, url):
        """Extract emails from a single URL"""
        try:
            print(f"[+] Scanning: {url}")
            response = self.session.get(url, timeout=15)
            emails = set(re.findall(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", response.text, re.I))
            return list(emails)
        except Exception as e:
            print(f"[-] Error: {e}")
            return []

    def google_search(self, query, pages=1):
        """Extract emails from Google search results (B2B/B2C)"""
        emails = set()
        try:
            for page in range(pages):
                url = f"https://www.google.com/search?q={query}&start={page*10}"
                response = self.session.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                links = [a['href'] for a in soup.find_all('a', href=True) if 'http' in a['href']]
                
                for link in links:
                    domain = urlparse(link).netloc
                    if any(d in domain for d in ["linkedin.com", "facebook.com"]):  # Skip social media
                        continue
                    emails.update(self.extract_from_url(link))
                    time.sleep(DELAY)
        except Exception as e:
            print(f"[-] Google search failed: {e}")
        return list(emails)

    def save_results(self, emails, filename="emails.csv"):
        """Export to CSV"""
        df = pd.DataFrame(emails, columns=["Email"])
        df.to_csv(filename, index=False)
        print(f"[+] Saved {len(emails)} emails to {filename}")

if __name__ == "__main__":
    extractor = EmailExtractor()
    print("1. Extract from URL\n2. Search by Keyword (Google)")
    choice = input("Choose mode (1/2): ")

    if choice == "1":
        url = input("Enter URL: ")
        emails = extractor.extract_from_url(url)
    elif choice == "2":
        query = input("Enter keyword (e.g., 'B2B software companies'): ")
        emails = extractor.google_search(query)
    else:
        print("Invalid choice!")
        exit()

    if emails:
        extractor.save_results(emails)
    else:
        print("[-] No emails found.")