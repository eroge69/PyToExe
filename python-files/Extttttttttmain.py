import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from googlesearch import search
import threading
import time
import json  # Added for better API response handling

class EmailExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Email Extractor v2.1")  # Version update
        self.root.geometry("650x450")  # Slightly larger window
        
        # GUI Elements
        self.setup_ui()
        
        # Initialize variables
        self.emails = []
        self.running = False
        self.stop_event = threading.Event()  # For proper thread stopping

    def setup_ui(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text="Source", padding=(10, 5))
        input_frame.pack(fill="x", padx=10, pady=5)
        
        self.source_var = tk.StringVar(value="url")
        ttk.Radiobutton(input_frame, text="From URL", variable=self.source_var, value="url").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(input_frame, text="Google Search", variable=self.source_var, value="google").grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(input_frame, text="Hunter.io API", variable=self.source_var, value="hunter").grid(row=2, column=0, sticky="w")
        
        self.input_entry = ttk.Entry(input_frame, width=55)
        self.input_entry.grid(row=0, column=1, rowspan=3, padx=5, sticky="ew")
        
        # Options Frame
        options_frame = ttk.LabelFrame(self.root, text="Options", padding=(10, 5))
        options_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(options_frame, text="Max Results:").grid(row=0, column=0, sticky="w")
        self.max_results = ttk.Spinbox(options_frame, from_=1, to=1000, width=8)
        self.max_results.set(50)
        self.max_results.grid(row=0, column=1, sticky="w")
        
        # Progress/Output
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        
        self.output_text = tk.Text(self.root, height=12, wrap="word")
        self.output_text.config(state="disabled")
        scrollbar = ttk.Scrollbar(self.root, command=self.output_text.yview)
        self.output_text['yscrollcommand'] = scrollbar.set
        self.output_text.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Action Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.extract_btn = ttk.Button(button_frame, text="Extract Emails", command=self.start_extraction)
        self.extract_btn.pack(side="left")
        
        self.save_btn = ttk.Button(button_frame, text="Save Results", command=self.save_results, state="disabled")
        self.save_btn.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Stop", command=self.stop_extraction).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_output).pack(side="right")
    
    def log(self, message):
        self.output_text.config(state="normal")
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.output_text.config(state="disabled")
    
    def clear_output(self):
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, "end")
        self.output_text.config(state="disabled")
        self.emails = []
        self.save_btn.config(state="disabled")
        self.progress["value"] = 0
    
    def stop_extraction(self):
        self.running = False
        self.stop_event.set()
        self.log("\nExtraction stopped by user")
        self.extract_btn.config(state="normal")
    
    def save_results(self):
        if not self.emails:
            messagebox.showwarning("Warning", "No emails to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Email Results"
        )
        
        if file_path:
            try:
                df = pd.DataFrame(self.emails, columns=["Email"])
                df.to_csv(file_path, index=False)
                self.log(f"\nSaved {len(self.emails)} emails to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
    
    def validate_url(self, url):
        """Check if URL has valid format"""
        return re.match(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', url)
    
    def extract_from_url(self, url):
        try:
            if not self.validate_url(url):
                self.log(f"Invalid URL format: {url}")
                return []
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
            
            self.log(f"\nConnecting to: {url}")
            response = requests.get(
                url, 
                headers=headers, 
                timeout=15,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Detect encoding properly
            if 'charset=' in response.headers.get('content-type', '').lower():
                response.encoding = response.apparent_encoding
            
            emails = re.findall(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", 
                response.text, 
                re.IGNORECASE
            )
            
            # Advanced filtering
            filtered = [
                e.lower() for e in emails 
                if not any(x in e for x in [
                    'noreply', 'mailer', 'notification', 
                    'support', 'hello', 'info', 'contact'
                ])
                and not re.match(r'^[\w._%+-]+@[\w.-]+\.(png|jpg|gif|svg)$', e)
            ]
            
            self.log(f"Found {len(filtered)} valid emails")
            return list(set(filtered))  # Remove duplicates
            
        except requests.RequestException as e:
            self.log(f"Connection error: {str(e)}")
            return []
        except Exception as e:
            self.log(f"Processing error: {str(e)}")
            return []
    
    def extract_from_google(self, query):
        try:
            results = []
            max_results = min(int(self.max_results.get()), 100)  # Limit to 100 for safety
            self.log(f"\nStarting Google search for: '{query}'")
            
            search_results = search(
                query, 
                num_results=max_results,
                lang="en",
                extra_params={"filter": "0"}  # Disable safe search
            )
            
            for i, url in enumerate(search_results):
                if not self.running or self.stop_event.is_set():
                    break
                    
                self.log(f"\n[{i+1}/{max_results}] Scanning: {url}")
                emails = self.extract_from_url(url)
                results.extend(emails)
                
                self.progress["value"] = ((i + 1) / max_results) * 100
                self.root.update()
                
                if emails:
                    self.log(f"→ Found {len(emails)} emails")
                
                time.sleep(2.5)  # Be polite to Google
            
            return list(set(results))  # Remove duplicates
            
        except Exception as e:
            self.log(f"\nSearch failed: {str(e)}")
            return []
    
    def extract_from_hunter(self, domain):
        try:
            API_KEY = "YOUR_HUNTER_API_KEY"  # REPLACE WITH YOUR KEY
            if API_KEY == "YOUR_HUNTER_API_KEY":
                messagebox.showwarning(
                    "API Key Required", 
                    "Please enter your Hunter.io API key in the code\n"
                    "Get one at: https://hunter.io/api-documentation"
                )
                return []
                
            url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={API_KEY}"
            self.log(f"\nQuerying Hunter.io API for: {domain}")
            
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            if data.get("errors"):
                self.log(f"API Error: {data['errors'][0]['details']}")
                return []
                
            emails = [e["value"] for e in data.get("data", {}).get("emails", [])]
            self.log(f"Hunter.io found {len(emails)} professional emails")
            return emails
            
        except requests.RequestException as e:
            self.log(f"\nAPI Connection Error: {str(e)}")
            return []
        except Exception as e:
            self.log(f"\nAPI Processing Error: {str(e)}")
            return []
    
    def start_extraction(self):
        if self.running:
            return
            
        self.clear_output()
        self.running = True
        self.stop_event.clear()
        self.extract_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.progress["value"] = 0
        
        source = self.source_var.get()
        input_text = self.input_entry.get().strip()
        
        if not input_text:
            messagebox.showwarning("Input Required", "Please enter a URL, search term, or domain")
            self.running = False
            self.extract_btn.config(state="normal")
            return
            
        # Run in thread to keep GUI responsive
        def extraction_thread():
            try:
                results = []
                
                if source == "url":
                    if not input_text.startswith(('http://', 'https://')):
                        input_text = f'https://{input_text}'
                    results = self.extract_from_url(input_text)
                elif source == "google":
                    results = self.extract_from_google(input_text)
                elif source == "hunter":
                    results = self.extract_from_hunter(input_text)
                
                self.emails = sorted(list(set(results)))  # Remove duplicates and sort
                
                if self.emails:
                    self.log(f"\nExtraction complete! Found {len(self.emails)} unique emails")
                    self.save_btn.config(state="normal")
                else:
                    self.log("\nNo valid emails found")
                
            except Exception as e:
                self.log(f"\nCritical error: {str(e)}")
            finally:
                self.running = False
                self.progress["value"] = 100
                self.extract_btn.config(state="normal")
                self.root.update()
        
        threading.Thread(target=extraction_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set UI theme
    try:
        root.tk.call('source', 'azure/azure.tcl')
        root.tk.call('set_theme', 'dark')
    except:
        pass  # Use default theme if custom theme fails
    
    app = EmailExtractorApp(root)
    
    # Center window
    root.eval('tk::PlaceWindow . center')
    
    root.mainloop()