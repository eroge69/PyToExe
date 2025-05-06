import os
import random
import time
import subprocess
from colorama import init, Fore

# Init colorama
init(autoreset=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(text, delay=0.03, color=Fore.WHITE):
    for char in text:
        print(color + char, end='', flush=True)
        time.sleep(delay)
    print()

def wait_enter():
    input(Fore.YELLOW + "\n[Enter] Continue...")

# 1. Device Access Simulator
def simulate_camera():
    clear()
    print(Fore.CYAN + "📷 Accessing live camera feed (simulated)...")
    time.sleep(1)
    print(Fore.YELLOW + "Streaming from: test_video.mp4")
    time.sleep(1)
    wait_enter()

def simulate_microphone():
    clear()
    print(Fore.CYAN + "🎤 Accessing microphone...")
    time.sleep(1)
    print(Fore.YELLOW + "Audio playing: test_audio.mp3")
    time.sleep(1)
    wait_enter()

# 2. Network Scanner
def network_scanner():
    clear()
    print(Fore.CYAN + "📡 Scanning network...")
    time.sleep(2)
    devices = ["192.168.0.1", "192.168.0.2", "192.168.0.3"]
    for device in devices:
        print(Fore.YELLOW + f"Found device: {device}")
    wait_enter()

# 3. DDOS Simulator
def ddos_simulator():
    clear()
    print(Fore.CYAN + "🌐 Starting DDOS Simulation...")
    time.sleep(2)
    print(Fore.RED + "WARNING: This is a simulation! This does not perform any real attack.")
    wait_enter()

# 4. File Manipulator
def file_manipulator():
    clear()
    print(Fore.CYAN + "💾 File Manipulator")
    time.sleep(1)
    print("1) View files\n2) Delete files\n3) Rename files\n0) Back")
    choice = input("Select option: ")
    if choice == "1":
        files = os.listdir()
        for file in files:
            print(file)
    elif choice == "2":
        file_name = input("Enter the filename to delete: ")
        if os.path.exists(file_name):
            os.remove(file_name)
            print(Fore.GREEN + f"{file_name} deleted.")
        else:
            print(Fore.RED + "File not found.")
    elif choice == "3":
        old_name = input("Enter the old filename: ")
        new_name = input("Enter the new filename: ")
        if os.path.exists(old_name):
            os.rename(old_name, new_name)
            print(Fore.GREEN + f"{old_name} renamed to {new_name}.")
        else:
            print(Fore.RED + "File not found.")
    wait_enter()

# 5. System Monitor
def system_monitor():
    clear()
    print(Fore.CYAN + "💻 System Monitor")
    time.sleep(1)
    print("System stats: CPU usage, RAM usage, disk usage")
    # Dummy stats for demonstration
    print(Fore.GREEN + "CPU: 20%\nRAM: 50%\nDisk: 40%")
    wait_enter()

# 6. Wireless Sniffer
def wireless_sniffer():
    clear()
    print(Fore.CYAN + "📡 Scanning for wireless networks...")
    time.sleep(2)
    networks = ["Network_1", "Network_2", "Network_3"]
    for net in networks:
        print(Fore.YELLOW + f"Found network: {net}")
    wait_enter()

# 7. Remote Control Simulator
def remote_control():
    clear()
    print(Fore.CYAN + "🖥️ Remote Control Simulation...")
    time.sleep(1)
    print(Fore.YELLOW + "Attempting to access remote machine...")
    time.sleep(2)
    print(Fore.GREEN + "Remote machine accessed.")
    wait_enter()

# 8. System Security Check
def system_security_check():
    clear()
    print(Fore.CYAN + "🔒 System Security Check")
    time.sleep(1)
    print(Fore.RED + "Security threat detected: Weak password.")
    wait_enter()

# 9. File Downloader Simulator
def file_downloader():
    clear()
    print(Fore.CYAN + "📥 Fake File Downloader...")
    time.sleep(2)
    print(Fore.YELLOW + "Downloading file: 'example.txt'...")
    time.sleep(3)
    print(Fore.GREEN + "Download complete.")
    wait_enter()

# 10. Test Modules (Placeholders)
def test_module():
    clear()
    print(Fore.CYAN + "This is a test module")
    wait_enter()

# 11. Device Access (Module 1)
def device_access():
    clear()
    print(Fore.CYAN + "📱 Device Access Menu:")
    print("1) 📷 Access Camera")
    print("2) 🎤 Access Microphone")
    print("0) Back")
    choice = input("Select option: ")
    if choice == "1":
        simulate_camera()
    elif choice == "2":
        simulate_microphone()
    elif choice == "0":
        return

# 12. Network Tools (Module 2)
def network_tools():
    clear()
    print(Fore.CYAN + "🌐 Network Tools Menu:")
    print("1) Network Scanner")
    print("2) DDOS Simulator")
    print("3) Wireless Sniffer")
    print("0) Back")
    choice = input("Select option: ")
    if choice == "1":
        network_scanner()
    elif choice == "2":
        ddos_simulator()
    elif choice == "3":
        wireless_sniffer()
    elif choice == "0":
        return

# 13. File Management (Module 3)
def file_management():
    clear()
    print(Fore.CYAN + "💾 File Management Menu:")
    print("1) File Manipulator")
    print("2) File Downloader")
    print("0) Back")
    choice = input("Select option: ")
    if choice == "1":
        file_manipulator()
    elif choice == "2":
        file_downloader()
    elif choice == "0":
        return

# 14. System Diagnostics (Module 4)
def system_diagnostics():
    clear()
    print(Fore.CYAN + "💻 System Diagnostics Menu:")
    print("1) System Monitor")
    print("2) Security Check")
    print("0) Back")
    choice = input("Select option: ")
    if choice == "1":
        system_monitor()
    elif choice == "2":
        system_security_check()
    elif choice == "0":
        return

# 15. Test Module (Module 5)
def test_module_5():
    clear()
    print(Fore.CYAN + "Test Module 5 Activated")
    wait_enter()

# 16. File Encryption/Decryption
def file_encryption():
    clear()
    print(Fore.CYAN + "🔐 File Encryption")
    file_name = input("Enter file name to encrypt: ")
    print(Fore.GREEN + f"Encrypting {file_name}...")
    time.sleep(2)
    print(Fore.YELLOW + "File encrypted successfully.")
    wait_enter()

def file_decryption():
    clear()
    print(Fore.CYAN + "🔓 File Decryption")
    file_name = input("Enter file name to decrypt: ")
    print(Fore.GREEN + f"Decrypting {file_name}...")
    time.sleep(2)
    print(Fore.YELLOW + "File decrypted successfully.")
    wait_enter()

# 17. Password Generator
def password_generator():
    clear()
    print(Fore.CYAN + "🔑 Password Generator")
    length = int(input("Enter password length: "))
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()"
    password = ''.join(random.choice(chars) for i in range(length))
    print(Fore.GREEN + f"Generated password: {password}")
    wait_enter()

# 18. Port Scanner
def port_scanner():
    clear()
    print(Fore.CYAN + "🛠️ Port Scanner")
    ip = input("Enter IP to scan: ")
    print(Fore.GREEN + f"Scanning ports for {ip}...")
    time.sleep(3)
    print(Fore.YELLOW + f"Open ports on {ip}: 80, 443, 8080")
    wait_enter()

# 19. IP Geolocation
def ip_geolocation():
    clear()
    print(Fore.CYAN + "🌍 IP Geolocation")
    ip = input("Enter IP to geolocate: ")
    print(Fore.GREEN + f"Geolocating IP {ip}...")
    time.sleep(2)
    print(Fore.YELLOW + f"Location: New York, USA")
    wait_enter()

# 20. Fake Virus Alert
def fake_virus_alert():
    clear()
    print(Fore.RED + "🚨 FAKE VIRUS ALERT 🚨")
    time.sleep(2)
    print(Fore.GREEN + "Your system is infected with a fake virus. Proceeding with simulation.")
    wait_enter()

# 21. System Information
def system_info():
    clear()
    print(Fore.CYAN + "💻 System Information")
    print(Fore.YELLOW + "OS: Windows 10\nCPU: Intel i7\nRAM: 16GB\nDisk: 500GB")
    wait_enter()

# 22. File System Mapping
def file_system_mapping():
    clear()
    print(Fore.CYAN + "🗂️ File System Mapping")
    time.sleep(1)
    print(Fore.YELLOW + "Mapping directories...")
    time.sleep(2)
    print(Fore.GREEN + "Mapped files and directories successfully.")
    wait_enter()

# 23. DNS Lookup
def dns_lookup():
    clear()
    print(Fore.CYAN + "🌐 DNS Lookup")
    domain = input("Enter domain for DNS lookup: ")
    print(Fore.GREEN + f"Looking up DNS for {domain}...")
    time.sleep(2)
    print(Fore.YELLOW + f"DNS info for {domain}: 192.168.1.1")
    wait_enter()

# 24. ARP Scan
def arp_scan():
    clear()
    print(Fore.CYAN + "🔍 ARP Scan")
    ip = input("Enter IP range for ARP scan (e.g., 192.168.1.1/24): ")
    print(Fore.GREEN + f"Scanning ARP for {ip}...")
    time.sleep(2)
    print(Fore.YELLOW + f"Found ARP entries: {ip}")
    wait_enter()

# 25. Firewall Tester
def firewall_tester():
    clear()
    print(Fore.CYAN + "🔥 Firewall Tester")
    ip = input("Enter IP to test firewall: ")
    print(Fore.GREEN + f"Testing firewall for {ip}...")
    time.sleep(3)
    print(Fore.YELLOW + f"Firewall is blocking: Port 80")
    wait_enter()

# 26. Network Protocol Analyzer
def protocol_analyzer():
    clear()
    print(Fore.CYAN + "📶 Network Protocol Analyzer")
    ip = input("Enter IP to analyze protocols: ")
    print(Fore.GREEN + f"Analyzing protocols for {ip}...")
    time.sleep(2)
    print(Fore.YELLOW + f"Protocols detected: TCP, UDP, HTTP")
    wait_enter()

# 27. Social Engineering Simulation
def social_engineering_simulation():
    clear()
    print(Fore.CYAN + "🎭 Social Engineering Simulation")
    time.sleep(1)
    print(Fore.GREEN + "Phishing attack simulation: Fake email sent to target.")
    wait_enter()

# 28. Webcam Hacking Simulator
def webcam_hacking_simulation():
    clear()
    print(Fore.CYAN + "📷 Webcam Hacking Simulator")
    time.sleep(2)
    print(Fore.GREEN + "Accessing webcam...")
    wait_enter()

# 29. Keylogger Simulation
def keylogger_simulation():
    clear()
    print(Fore.CYAN + "⌨️ Keylogger Simulation")
    time.sleep(1)
    print(Fore.GREEN + "Recording keystrokes...")
    wait_enter()

# 30. Proxy Server Simulator
def proxy_server_simulation():
    clear()
    print(Fore.CYAN + "🕵️‍♂️ Proxy Server Simulator")
    time.sleep(2)
    print(Fore.GREEN + "Setting up fake proxy server...")
    wait_enter()

# 31. Data Recovery Simulation
def data_recovery_simulation():
    clear()
    print(Fore.CYAN + "💾 Data Recovery Simulation")
    time.sleep(2)
    print(Fore.GREEN + "Recovering deleted files...")
    wait_enter()

# 32. USB Spoofing Simulation
def usb_spoofing_simulation():
    clear()
    print(Fore.CYAN + "🔌 USB Spoofing Simulation")
    time.sleep(1)
    print(Fore.GREEN + "Spoofing USB device...")
    wait_enter()

# 33. System Lockdown
def system_lockdown():
    clear()
    print(Fore.CYAN + "🔒 System Lockdown")
    time.sleep(1)
    print(Fore.GREEN + "Locking system...")
    wait_enter()

# 34. Network Traffic Analysis
def network_traffic_analysis():
    clear()
    print(Fore.CYAN + "📡 Network Traffic Analysis")
    time.sleep(2)
    print(Fore.GREEN + "Analyzing traffic...")
    wait_enter()

# 35. Vulnerability Scanner
def vulnerability_scanner():
    clear()
    print(Fore.CYAN + "🔍 Vulnerability Scanner")
    time.sleep(2)
    print(Fore.RED + "Vulnerabilities detected: SQL Injection, XSS")
    wait_enter()

# 36. System Backup
def system_backup():
    clear()
    print(Fore.CYAN + "💾 System Backup")
    time.sleep(2)
    print(Fore.GREEN + "System backup completed.")
    wait_enter()

# 37. Digital Footprint Analyzer
def digital_footprint_analyzer():
    clear()
    print(Fore.CYAN + "🌐 Digital Footprint Analyzer")
    time.sleep(2)
    print(Fore.GREEN + "Analyzing online footprint...")
    wait_enter()

# 38. Device Geolocation
def device_geolocation():
    clear()
    print(Fore.CYAN + "🌍 Device Geolocation")
    time.sleep(1)
    print(Fore.GREEN + "Geolocating device...")
    wait_enter()

# 39. Botnet Simulator
def botnet_simulator():
    clear()
    print(Fore.CYAN + "🤖 Botnet Simulator")
    time.sleep(1)
    print(Fore.RED + "Starting fake botnet simulation...")
    wait_enter()

# 40. Password Cracking Simulation
def password_cracking_simulation():
    clear()
    print(Fore.CYAN + "🔓 Password Cracking Simulation")
    time.sleep(2)
    print(Fore.RED + "Cracking password...")
    wait_enter()

# Main Menu
def main_menu():
    while True:
        clear()
        print(Fore.CYAN + "📚 PEGASUS TOOLKIT v3.0 - Main Menu")
        print("1) Device Access")
        print("2) Network Tools")
        print("3) File Management")
        print("4) System Diagnostics")
        print("5) Test Modules")
        print("6) System Information")
        print("0) Exit")
        choice = input("Select option: ")
        if choice == "1":
            device_access()
        elif choice == "2":
            network_tools()
        elif choice == "3":
            file_management()
        elif choice == "4":
            system_diagnostics()
        elif choice == "5":
            test_module_5()
        elif choice == "6":
            system_info()
        elif choice == "0":
            break

# Run the main menu
main_menu()
