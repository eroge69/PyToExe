# app.py
import tkinter as tk
from tkinter import messagebox
import subprocess
import shutil
from pathlib import Path
import getpass
import logging
import os
import sys
import threading
import importlib.util
from flask import Flask, jsonify, render_template, request, redirect, url_for

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Try to import Windows-specific modules
winreg_available = importlib.util.find_spec("winreg") is not None
if winreg_available:
    import winreg
    logging.info("Successfully imported winreg module")
else:
    logging.warning("winreg module not available - will use mock functionality on non-Windows systems")

# -------------------------------
# Admin Privileges Functions
# -------------------------------
def is_admin():
    """Check if the script is running as an administrator."""
    try:
        return os.geteuid() == 0  # Unix-like systems check for admin privileges
    except AttributeError:
        try:
            if sys.platform.startswith('win'):
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            return False
        except:
            return False  # Assume not admin if we can't check

def run_as_admin():
    """Re-launch the script with administrator privileges if needed."""
    if not is_admin():
        try:
            if sys.version_info[0] == 3 and sys.platform.startswith('win'):
                import ctypes
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
                logging.info("Relaunching with administrator privileges")
                sys.exit(0)  # Exit after trying to relaunch
        except Exception as e:
            logging.error(f"Failed to elevate privileges: {e}")
            return False
    return True

# -------------------------------
# Windows Maintenance Functions
# -------------------------------
def stop_windows_update_service():
    """
    Attempts to stop the Windows Update service.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logging.debug("Attempting to stop Windows Update service...")
    try:
        if not sys.platform.startswith('win'):
            logging.warning("Not on Windows - simulating Windows Update service stop")
            return True
            
        result = subprocess.run("sc stop wuauserv", shell=True, check=True, capture_output=True)
        logging.info(f"Windows Update service stopped successfully. Output: {result.stdout.decode()}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to stop Windows Update service: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error stopping Windows Update service: {str(e)}")
        return False

def clean_temp_folders():
    """
    Cleans temporary files from various Windows system folders.
    
    Returns:
        int: Number of files/folders deleted
    """
    logging.debug("Starting to clean temporary folders...")
    username = getpass.getuser()
    
    # List of folders to clean
    if sys.platform.startswith('win'):
        folders = [
            Path("C:/Windows/Temp"),
            Path("C:/Windows/SoftwareDistribution"),
            Path("C:/Windows/Prefetch"),
            Path(f"C:/Users/{username}/AppData/Local/Temp")
        ]
    else:
        # For non-Windows systems, use temp directory for simulation
        folders = [
            Path("/tmp")
        ]
        logging.warning("Not on Windows - using alternative temp directories")

    deleted = 0
    
    for folder in folders:
        logging.debug(f"Cleaning folder: {folder}")
        if folder.exists():
            try:
                for item in folder.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                            deleted += 1
                            logging.debug(f"Deleted file: {item}")
                        elif item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                            deleted += 1
                            logging.debug(f"Deleted directory: {item}")
                    except PermissionError as e:
                        logging.warning(f"Permission denied for {item}: {str(e)}")
                    except FileNotFoundError as e:
                        logging.warning(f"File not found while deleting {item}: {str(e)}")
                    except Exception as e:
                        logging.warning(f"Error deleting {item}: {str(e)}")
            except PermissionError as e:
                logging.warning(f"Permission denied for folder {folder}: {str(e)}")
            except Exception as e:
                logging.warning(f"Error processing folder {folder}: {str(e)}")
        else:
            logging.warning(f"Folder {folder} does not exist")
    
    logging.info(f"Total items deleted: {deleted}")
    return deleted

def read_installed_apps():
    """
    Read installed applications from the registry on Windows.
    
    Returns:
        list: List of installed application names
    """
    logging.debug("Reading installed applications...")
    installed_apps = []
    
    if not winreg_available or not sys.platform.startswith('win'):
        logging.warning("Registry access not available - using mock data for installed apps")
        # Mock data for non-Windows systems or when winreg isn't available
        installed_apps = [
            "Microsoft Office",
            "Google Chrome",
            "Mozilla Firefox",
            "Adobe Acrobat Reader",
            "VLC Media Player",
            "Microsoft Edge",
            "Windows Defender",
            "Python 3.11",
            "Visual Studio Code"
        ]
        return installed_apps
    
    try:
        # Check both 32-bit and 64-bit registry keys
        reg_keys = [r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                   r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"]
        
        # Open registry keys
        for reg_key in reg_keys:
            try:
                reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(reg, reg_key)
                
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        
                        try:
                            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            installed_apps.append(display_name)
                        except (FileNotFoundError, OSError):
                            pass
                    except:
                        continue
            except Exception as e:
                logging.warning(f"Error opening registry key {reg_key}: {e}")
    except Exception as e:
        logging.error(f"Error reading installed apps: {e}")
    
    # Remove duplicates and sort
    installed_apps = sorted(list(set(installed_apps)))
    logging.info(f"Found {len(installed_apps)} installed applications")
    return installed_apps

def clear_app_cache():
    """
    Clear cache of commonly used applications.
    
    Returns:
        int: Number of items deleted
    """
    logging.debug("Clearing application caches...")
    username = getpass.getuser()
    
    # Define cache folders based on platform
    if sys.platform.startswith('win'):
        cache_folders = [
            Path(f"C:/Users/{username}/AppData/Local/Google/Chrome/User Data/Default/Cache"),
            Path(f"C:/Users/{username}/AppData/Local/Mozilla/Firefox/Profiles"),
            Path(f"C:/Users/{username}/AppData/Local/Microsoft/Edge/User Data/Default/Cache"),
            Path(f"C:/Users/{username}/AppData/Local/Temp")
        ]
    else:
        # For non-Windows systems, use typical cache locations
        home = os.path.expanduser("~")
        cache_folders = [
            Path(f"{home}/.cache/google-chrome"),
            Path(f"{home}/.cache/mozilla"),
            Path(f"{home}/.cache")
        ]
        logging.warning("Not on Windows - using alternative cache directories")
    
    deleted = 0
    
    for folder in cache_folders:
        logging.debug(f"Clearing cache folder: {folder}")
        if folder.exists():
            try:
                for item in folder.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                            deleted += 1
                            logging.debug(f"Deleted cache file: {item}")
                        elif item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                            deleted += 1
                            logging.debug(f"Deleted cache directory: {item}")
                    except PermissionError as e:
                        logging.warning(f"Permission denied for cache item {item}: {str(e)}")
                    except FileNotFoundError:
                        pass
                    except Exception as e:
                        logging.warning(f"Error clearing cache item {item}: {str(e)}")
            except PermissionError as e:
                logging.warning(f"Permission denied for cache folder {folder}: {str(e)}")
            except Exception as e:
                logging.warning(f"Error processing cache folder {folder}: {str(e)}")
        else:
            logging.debug(f"Cache folder {folder} does not exist")
    
    logging.info(f"Total cache items deleted: {deleted}")
    return deleted

# -------------------------------
# UI Setup
# -------------------------------
def create_ui():
    """Creates and runs the Tkinter GUI for Windows system maintenance"""
    # Check admin privileges first
    if not is_admin():
        admin_result = messagebox.askyesno("Administrator Privileges", 
                                            "This application requires administrator privileges to work properly.\n\n"
                                            "Would you like to restart with administrator privileges?")
        if admin_result:
            run_as_admin()
            return
        else:
            messagebox.showwarning("Limited Functionality", 
                                  "Some operations may fail without administrator privileges.")
    
    # UI elements that need to be accessed in functions
    global status_label, apps_listbox
    
    # Create Tkinter UI
    root = tk.Tk()
    root.title("Windows System Maintenance")
    root.geometry("650x500")
    root.config(bg="#2c3e50")  # Updated color scheme
    
    # Title
    tk.Label(root, text="🛠 Windows System Maintenance", fg="#ffffff",
             bg="#2c3e50", font=("Segoe UI", 16, "bold")).pack(pady=10)

    # Main Frame
    main_frame = tk.Frame(root, bg="#2c3e50")
    main_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Left panel (buttons)
    button_frame = tk.Frame(main_frame, bg="#34495e", bd=2, relief="groove")
    button_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    
    # Define buttons with their actions
    buttons = [
        {"text": "Stop Windows Update Service", "subtext": "Temporarily stops the Windows Update service", "emoji": "⛔", "action": "stop"},
        {"text": "Clean Temporary Files", "subtext": "Removes temporary files from system folders", "emoji": "🧹", "action": "clean"},
        {"text": "Clear App Cache", "subtext": "Clears cache of commonly used apps", "emoji": "🧼", "action": "cache"},
        {"text": "Read Installed Apps", "subtext": "Displays a list of installed applications", "emoji": "📦", "action": "apps"},
        {"text": "Complete Maintenance", "subtext": "Stops service, cleans temp files and cache", "emoji": "🛠️", "action": "all"}
    ]
    
    # Threading functionality
    def run_service_action(action_type):
        """Run actions in separate threads to avoid blocking the UI."""
        update_ui_status("⏳ Working... Please wait...", "lightblue")  # Show working message
        
        result = False
        message = ""
        deleted_count = 0
        apps_list = []
        
        if action_type == "stop":
            result = stop_windows_update_service()
            message = "Windows Update service stopped" if result else "Failed to stop Windows Update service"
        
        elif action_type == "clean":
            deleted_count = clean_temp_folders()
            result = deleted_count > 0
            message = f"Cleaned {deleted_count} temp files" if result else "No temporary files were cleaned"
        
        elif action_type == "cache":
            deleted_count = clear_app_cache()
            result = deleted_count > 0
            message = f"Cleared {deleted_count} cache items" if result else "No cache items were cleared"
        
        elif action_type == "apps":
            apps_list = read_installed_apps()
            result = len(apps_list) > 0
            message = f"Found {len(apps_list)} installed apps" if result else "Failed to read installed applications"
            
            # Update the listbox with the apps
            update_installed_apps_ui(apps_list)
        
        elif action_type == "all":
            update_status = stop_windows_update_service()
            temp_count = clean_temp_folders()
            cache_count = clear_app_cache()
            
            result = update_status and (temp_count > 0 or cache_count > 0)
            message = f"Service stopped, cleaned {temp_count + cache_count} items" if result else "Maintenance partially completed"
        
        # Update UI with results
        status_color = "lightgreen" if result else "red"
        update_ui_status(f"{'✅' if result else '❌'} {message}", status_color)
    
    def update_ui_status(message, color):
        """Update the status label after completing an action."""
        status_label.config(text=message, fg=color)
    
    def update_installed_apps_ui(apps_list):
        """Update the installed apps list in the UI."""
        apps_listbox.delete(0, tk.END)
        for app in sorted(apps_list):
            apps_listbox.insert(tk.END, app)
    
    def handle_action(action_type):
        """Handle button click actions by starting a new thread."""
        threading.Thread(target=run_service_action, args=(action_type,), daemon=True).start()
    
    # Create the buttons
    for btn in buttons:
        frame = tk.Frame(button_frame, bg="#34495e")
        frame.pack(fill="x", pady=5)
        button = tk.Button(frame, 
                  text=f"{btn['emoji']}  {btn['text']}", 
                  anchor="w", 
                  font=("Segoe UI", 11),
                  fg="#ffffff", 
                  bg="#1abc9c", 
                  relief="flat", 
                  padx=10,
                  activebackground="#16a085",
                  command=lambda action=btn["action"]: handle_action(action))
        button.pack(fill="x")
        
        tk.Label(frame, 
                text=btn["subtext"], 
                bg="#34495e", 
                fg="#a0a0a0",
                anchor="w", 
                font=("Segoe UI", 9)).pack(fill="x", padx=15)
    
    # Right panel (results and listbox)
    results_frame = tk.Frame(main_frame, bg="#34495e", bd=2, relief="groove")
    results_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
    
    # Status Label at the top of results frame
    status_label = tk.Label(results_frame, 
                           text="⚙️ Waiting for action...", 
                           font=("Segoe UI", 12), 
                           bg="#34495e", 
                           fg="#ffffff",
                           pady=10)
    status_label.pack(fill="x")
    
    # Label for the listbox
    tk.Label(results_frame, 
            text="Installed Applications:", 
            font=("Segoe UI", 11), 
            bg="#34495e", 
            fg="#ffffff",
            anchor="w",
            padx=10).pack(fill="x")
    
    # Create a frame for the listbox with a scrollbar
    listbox_frame = tk.Frame(results_frame, bg="#34495e")
    listbox_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Scrollbar
    scrollbar = tk.Scrollbar(listbox_frame)
    scrollbar.pack(side="right", fill="y")
    
    # Listbox for displaying installed apps
    apps_listbox = tk.Listbox(listbox_frame, 
                             height=10, 
                             font=("Segoe UI", 10), 
                             bg="#34495e", 
                             fg="#ffffff", 
                             selectmode=tk.SINGLE,
                             yscrollcommand=scrollbar.set)
    apps_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=apps_listbox.yview)
    
    # Add a refresh button specifically for the apps list
    refresh_button = tk.Button(results_frame,
                              text="Refresh Apps List",
                              font=("Segoe UI", 10),
                              bg="#1abc9c",
                              fg="#ffffff",
                              command=lambda: handle_action("apps"))
    refresh_button.pack(pady=10)

    logging.info("GUI application started")
    root.mainloop()

# -------------------------------
# Flask Routes
# -------------------------------
@app.route('/')
def index():
    """Render the landing page with instructions to launch the desktop app."""
    return render_template('index.html')

@app.route('/launch-app')
def launch_app():
    """Start the Tkinter GUI application in a separate thread."""
    # Start the Tkinter app in a new thread so it doesn't block the Flask server
    thread = threading.Thread(target=create_ui)
    thread.daemon = True  # This makes the thread exit when the main program exits
    thread.start()
    return redirect(url_for('index'))

@app.route('/api/stop-windows-update', methods=['POST'])
def api_stop_windows_update():
    """API endpoint to stop the Windows Update service."""
    try:
        success = stop_windows_update_service()
        if success:
            return jsonify({
                "status": "success",
                "message": "Windows Update service stopped successfully"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to stop Windows Update service"
            }), 500
    except Exception as e:
        logging.error(f"Error stopping Windows Update service: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/clean-temp', methods=['POST'])
def api_clean_temp():
    """API endpoint to clean temporary files from various Windows system folders."""
    try:
        deleted_count = clean_temp_folders()
        return jsonify({
            "status": "success",
            "files_deleted": deleted_count,
            "message": f"Successfully deleted {deleted_count} files/folders"
        })
    except Exception as e:
        logging.error(f"Error cleaning temporary files: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/clean-all', methods=['POST'])
def api_clean_all():
    """API endpoint to both stop Windows Update service and clean temporary files."""
    try:
        update_stopped = stop_windows_update_service()
        deleted_count = clean_temp_folders()
        cache_count = clear_app_cache()
        
        return jsonify({
            "status": "success",
            "windows_update_stopped": update_stopped,
            "files_deleted": deleted_count,
            "cache_cleared": cache_count,
            "message": f"Operation completed: Windows Update service {'stopped' if update_stopped else 'failed to stop'}, {deleted_count} temp files and {cache_count} cache items deleted"
        })
    except Exception as e:
        logging.error(f"Error in clean-all operation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/clear-cache', methods=['POST'])
def api_clear_cache():
    """API endpoint to clear application caches."""
    try:
        deleted_count = clear_app_cache()
        return jsonify({
            "status": "success",
            "items_deleted": deleted_count,
            "message": f"Successfully cleared {deleted_count} cache items"
        })
    except Exception as e:
        logging.error(f"Error clearing application cache: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/installed-apps', methods=['GET'])
def api_installed_apps():
    """API endpoint to get list of installed applications."""
    try:
        apps = read_installed_apps()
        return jsonify({
            "status": "success",
            "app_count": len(apps),
            "apps": apps,
            "message": f"Found {len(apps)} installed applications"
        })
    except Exception as e:
        logging.error(f"Error getting installed applications: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    # If run directly, launch the Tkinter GUI
    create_ui()
