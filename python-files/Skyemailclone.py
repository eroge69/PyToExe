import re
import requests
import csv
import os
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import socket
import dns.resolver
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import random
from datetime import datetime

class SkyEmailExtractorClone:
    def __init__(self, root):
        self.root = root
        self.root.title("Sky Email Extractor Clone")
        self.root.geometry("900x700")
        
        # Variables
        self.running = False
        self.emails_found = set()
        self.processed_urls = set()
        self.total_emails = 0
        self.start_time = None
        
        # GUI Setup
        self.setup_ui()
        
        # Session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def setup_ui(self):
        # Main Frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding="10")
        input_frame.pack(fill=tk.X, pady=5)
        
        # URL Input
        ttk.Label(input_frame, text="Website URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(input_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # Depth Level
        ttk.Label(input_frame, text="Crawl Depth:").grid(row=1, column=0, sticky=tk.W)
        self.depth_spinbox = ttk.Spinbox(input_frame, from_=1, to=5, width=5)
        self.depth_spinbox.grid(row=1, column=1, padx=5, sticky=tk.W)
        self.depth_spinbox.set(2)
        
        # Max Threads
        ttk.Label(input_frame, text="Max Threads:").grid(row=2, column=0, sticky=tk.W)
        self.threads_spinbox = ttk.Spinbox(input_frame, from_=1, to=50, width=5)
        self.threads_spinbox.grid(row=2, column=1, padx=5, sticky=tk.W)
        self.threads_spinbox.set(10)
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Extraction", command=self.start_extraction)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_extraction, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.export_button = ttk.Button(button_frame, text="Export Results", command=self.export_results)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # Results Frame
        results_frame = ttk.LabelFrame(main_frame, text="Extraction Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview for emails
        self.tree = ttk.Treeview(results_frame, columns=('Email', 'Source'), show='headings')
        self.tree.heading('Email', text='Email Address')
        self.tree.heading('Source', text='Source URL')
        self.tree.column('Email', width=300)
        self.tree.column('Source', width=400)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X)
        
    def start_extraction(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL")
            return
            
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.DISABLED)
        
        self.emails_found = set()
        self.processed_urls = set()
        self.total_emails = 0
        self.start_time = datetime.now()
        
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.status_var.set("Extraction started...")
        
        # Start extraction in a new thread
        threading.Thread(target=self.run_extraction, args=(url,), daemon=True).start()
        
    def stop_extraction(self):
        self.running = False
        self.status_var.set("Extraction stopped by user")
        
    def run_extraction(self, start_url):
        max_depth = int(self.depth_spinbox.get())
        max_threads = int(self.threads_spinbox.get())
        
        try:
            domain = urlparse(start_url).netloc
            self.crawl_site(start_url, domain, max_depth, max_threads)
            
            # After crawling, try pattern generation
            self.generate_pattern_emails(domain)
            
            # Verify emails
            self.verify_emails()
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
        finally:
            self.running = False
            self.root.after(0, self.on_extraction_complete)
            
    def crawl_site(self, url, domain, max_depth, max_threads, current_depth=1):
        if not self.running or current_depth > max_depth or url in self.processed_urls:
            return
            
        self.processed_urls.add(url)
        self.status_var.set(f"Processing: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                # Extract emails from this page
                emails = self.extract_emails_from_text(response.text)
                for email in emails:
                    if email not in self.emails_found:
                        self.emails_found.add(email)
                        self.total_emails += 1
                        self.root.after(0, self.add_email_to_tree, email, url)
                        
                # Find all links on the page
                soup = BeautifulSoup(response.text, 'html.parser')
                links = set()
                
                for link in soup.find_all('a', href=True):
                    href = link['href'].strip()
                    if href.startswith('mailto:'):
                        continue
                        
                    full_url = urljoin(url, href)
                    parsed = urlparse(full_url)
                    
                    # Only follow links from same domain
                    if parsed.netloc == domain and full_url not in self.processed_urls:
                        links.add(full_url)
                        
                # Process links with thread pool
                if links and current_depth < max_depth:
                    with ThreadPoolExecutor(max_workers=max_threads) as executor:
                        futures = []
                        for link in links:
                            futures.append(executor.submit(
                                self.crawl_site, 
                                link, 
                                domain, 
                                max_depth, 
                                max_threads, 
                                current_depth + 1
                            ))
                            
                        for future in futures:
                            future.result()
                            
        except Exception as e:
            pass
            
    def extract_emails_from_text(self, text):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return set(re.findall(email_pattern, text, re.IGNORECASE))
        
    def generate_pattern_emails(self, domain):
        common_patterns = [
            'info@{}',
            'contact@{}',
            'admin@{}',
            'support@{}',
            'sales@{}',
            'hello@{}',
            'webmaster@{}'
        ]
        
        for pattern in common_patterns:
            email = pattern.format(domain)
            if email not in self.emails_found:
                self.emails_found.add(email)
                self.total_emails += 1
                self.root.after(0, self.add_email_to_tree, email, "Pattern Generated")
                
    def verify_emails(self):
        self.status_var.set("Verifying emails...")
        
        for email in list(self.emails_found):
            if not self.running:
                break
                
            if self.verify_email(email):
                self.root.after(0, self.update_email_status, email, "Verified")
            else:
                self.root.after(0, self.update_email_status, email, "Unverified")
                
    def verify_email(self, email):
        domain = email.split('@')[-1]
        
        # Check MX records
        try:
            dns.resolver.resolve(domain, 'MX')
            return True
        except:
            return False
            
    def add_email_to_tree(self, email, source):
        self.tree.insert('', tk.END, values=(email, source))
        self.status_var.set(f"Found {self.total_emails} emails | Last: {email}")
        
    def update_email_status(self, email, status):
        for item in self.tree.get_children():
            if self.tree.item(item, 'values')[0] == email:
                self.tree.item(item, values=(email, status))
                break
                
    def on_extraction_complete(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.NORMAL)
        
        duration = datetime.now() - self.start_time
        self.status_var.set(
            f"Done! Found {self.total_emails} emails in {duration.total_seconds():.1f} seconds"
        )
        
    def export_results(self):
        if not self.emails_found:
            messagebox.showwarning("Warning", "No emails to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx"), ("All Files", "*.*")],
            title="Save Email List"
        )
        
        if not file_path:
            return
            
        try:
            data = []
            for item in self.tree.get_children():
                email, source = self.tree.item(item, 'values')
                data.append([email, source])
                
            df = pd.DataFrame(data, columns=['Email', 'Source'])
            
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
                
            messagebox.showinfo("Success", f"Exported {len(data)} emails to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SkyEmailExtractorClone(root)
    root.mainloop()