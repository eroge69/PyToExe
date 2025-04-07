import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from googlesearch import search
import concurrent.futures
import csv
import os
import time
from datetime import datetime
import argparse
import socket
import ssl
import whois
from urllib.robotparser import RobotFileParser

# Configure user-agent and timeout
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
TIMEOUT = 10
MAX_THREADS = 20

class EmailExtractor:
    def __init__(self):
        self.emails = set()
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.max_redirects = 5

    def is_valid_email(self, email):
        """Check if email is valid"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def can_fetch(self, url):
        """Check robots.txt permissions"""
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            rp = RobotFileParser()
            rp.set_url(f"{base_url}/robots.txt")
            rp.read()
            return rp.can_fetch(HEADERS['User-Agent'], url)
        except:
            return True  # Assume allowed if robots.txt can't be read

    def get_page_content(self, url):
        """Fetch page content with error handling"""
        try:
            if not self.can_fetch(url):
                print(f"[!] Skipping {url} due to robots.txt restrictions")
                return None
                
            response = self.session.get(url, timeout=TIMEOUT, allow_redirects=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                return None
                
            return response.text
        except (requests.RequestException, socket.timeout, ssl.SSLError) as e:
            print(f"[!] Error fetching {url}: {str(e)}")
            return None

    def extract_emails_from_text(self, text):
        """Extract emails from text content"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        found_emails = set(re.findall(email_pattern, text, re.IGNORECASE))
        return {email.lower() for email in found_emails if self.is_valid_email(email)}

    def extract_emails_from_url(self, url):
        """Extract emails from a single URL"""
        if url in self.visited_urls:
            return set()
            
        self.visited_urls.add(url)
        print(f"[*] Processing URL: {url}")
        
        content = self.get_page_content(url)
        if not content:
            return set()
            
        emails = self.extract_emails_from_text(content)
        
        # Also look for contact pages
        soup = BeautifulSoup(content, 'html.parser')
        contact_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if any(word in href for word in ['contact', 'about', 'connect', 'reach']):
                full_url = requests.compat.urljoin(url, link['href'])
                contact_links.append(full_url)
        
        # Process contact pages
        for contact_url in contact_links[:3]:  # Limit to 3 contact pages
            if contact_url not in self.visited_urls:
                contact_content = self.get_page_content(contact_url)
                if contact_content:
                    emails.update(self.extract_emails_from_text(contact_content))
        
        return emails

    def extract_emails_from_keyword(self, keyword, num_results=50):
        """Extract emails using keyword search"""
        print(f"[*] Searching for keyword: {keyword}")
        search_results = set()
        
        try:
            # Get Google search results
            for url in search(keyword, num_results=num_results, stop=num_results, pause=2):
                search_results.add(url)
        except Exception as e:
            print(f"[!] Google search error: {str(e)}")
            return set()
        
        # Process each search result
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_to_url = {executor.submit(self.extract_emails_from_url, url): url for url in search_results}
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    emails = future.result()
                    self.emails.update(emails)
                except Exception as e:
                    print(f"[!] Error processing URL: {str(e)}")
        
        return self.emails

    def save_to_csv(self, emails, filename):
        """Save emails to CSV file"""
        if not emails:
            print("[!] No emails to save")
            return
            
        os.makedirs('output', exist_ok=True)
        filepath = os.path.join('output', filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Email'])
            for email in sorted(emails):
                writer.writerow([email])
                
        print(f"[+] Saved {len(emails)} emails to {filepath}")

def main():
    print("""
    ███████╗███╗   ███╗ █████╗ ██╗██╗         ███████╗██╗  ██╗████████╗██████╗  █████╗  ██████╗████████╗ ██████╗ ██████╗ 
    ██╔════╝████╗ ████║██╔══██╗██║██║         ██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗
    █████╗  ██╔████╔██║███████║██║██║         █████╗   ╚███╔╝    ██║   ██████╔╝███████║██║        ██║   ██║   ██║██████╔╝
    ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║         ██╔══╝   ██╔██╗    ██║   ██╔══██╗██╔══██║██║        ██║   ██║   ██║██╔══██╗
    ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗    ███████╗██╔╝ ██╗   ██║   ██║  ██║██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║
    ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝    ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
    """)
    print("Powerful B2B & B2C Email Extractor")
    print("="*60)
    
    parser = argparse.ArgumentParser(description='Advanced Email Extractor Tool')
    parser.add_argument('-u', '--url', help='Single URL to extract emails from')
    parser.add_argument('-f', '--file', help='Text file containing list of URLs')
    parser.add_argument('-k', '--keyword', help='Keyword to search for emails')
    parser.add_argument('-o', '--output', help='Output CSV filename', default='emails.csv')
    parser.add_argument('-n', '--num-results', type=int, default=50, help='Number of search results for keyword (default: 50)')
    
    args = parser.parse_args()
    
    extractor = EmailExtractor()
    emails = set()
    
    start_time = time.time()
    
    if args.url:
        print(f"[*] Extracting emails from URL: {args.url}")
        emails.update(extractor.extract_emails_from_url(args.url))
    
    if args.file:
        print(f"[*] Extracting emails from file: {args.file}")
        try:
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
                
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                future_to_url = {executor.submit(extractor.extract_emails_from_url, url): url for url in urls}
                for future in concurrent.futures.as_completed(future_to_url):
                    try:
                        result = future.result()
                        emails.update(result)
                    except Exception as e:
                        print(f"[!] Error processing URL: {str(e)}")
        except Exception as e:
            print(f"[!] Error reading file: {str(e)}")
    
    if args.keyword:
        print(f"[*] Extracting emails using keyword: {args.keyword}")
        emails.update(extractor.extract_emails_from_keyword(args.keyword, args.num_results))
    
    if not args.url and not args.file and not args.keyword:
        print("[*] Interactive mode")
        print("\nChoose extraction method:")
        print("1. Extract from single URL")
        print("2. Extract from list of URLs (file)")
        print("3. Extract using keyword")
        print("4. Combine all methods")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            url = input("Enter URL: ").strip()
            emails.update(extractor.extract_emails_from_url(url))
        elif choice == '2':
            file_path = input("Enter file path: ").strip()
            try:
                with open(file_path, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
                    
                with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                    future_to_url = {executor.submit(extractor.extract_emails_from_url, url): url for url in urls}
                    for future in concurrent.futures.as_completed(future_to_url):
                        try:
                            result = future.result()
                            emails.update(result)
                        except Exception as e:
                            print(f"[!] Error processing URL: {str(e)}")
            except Exception as e:
                print(f"[!] Error reading file: {str(e)}")
        elif choice == '3':
            keyword = input("Enter keyword: ").strip()
            num_results = int(input("Number of search results (default 50): ") or 50)
            emails.update(extractor.extract_emails_from_keyword(keyword, num_results))
        elif choice == '4':
            url = input("Enter URL (optional, press Enter to skip): ").strip()
            if url:
                emails.update(extractor.extract_emails_from_url(url))
                
            file_path = input("Enter file path with URLs (optional, press Enter to skip): ").strip()
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        urls = [line.strip() for line in f if line.strip()]
                        
                    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                        future_to_url = {executor.submit(extractor.extract_emails_from_url, url): url for url in urls}
                        for future in concurrent.futures.as_completed(future_to_url):
                            try:
                                result = future.result()
                                emails.update(result)
                            except Exception as e:
                                print(f"[!] Error processing URL: {str(e)}")
                except Exception as e:
                    print(f"[!] Error reading file: {str(e)}")
            
            keyword = input("Enter keyword (optional, press Enter to skip): ").strip()
            if keyword:
                num_results = int(input("Number of search results (default 50): ") or 50)
                emails.update(extractor.extract_emails_from_keyword(keyword, num_results))
        else:
            print("[!] Invalid choice")
            return
    
    if emails:
        print(f"\n[+] Found {len(emails)} unique emails:")
        for i, email in enumerate(sorted(emails)):
            print(f"{i+1}. {email}")
        
        output_file = args.output if args.output else f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        extractor.save_to_csv(emails, output_file)
    else:
        print("[!] No emails found")
    
    print(f"\n[+] Execution time: {time.time() - start_time:.2f} seconds")

if __name__ == '__main__':
    main()