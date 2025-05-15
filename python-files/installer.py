import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import importlib.util
import threading

def check_python_installed():
    """Checks if Python 3 is installed."""
    try:
        subprocess.run([sys.executable, "-V"], check=True, capture_output=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def check_module_installed(module_name):
    """Checks if a specific Python module is installed."""
    return importlib.util.find_spec(module_name) is not None

def install_python():
    """Opens a message box guiding the user to install Python."""
    tk.messagebox.showinfo("Install Python", "Python 3 is required to run this installer.\nPlease download and install Python 3 from the official website (python.org).")

def install_modules():
    """Installs the specified Python modules using pip."""
    modules_to_install = [
        "requests",
        "Pillow",
        "cython",
        "aiohttp"
    ]
    progress_window = tk.Toplevel(root)
    progress_window.title("Installing Modules")
    progress_label = ttk.Label(progress_window, text="Installing required modules...")
    progress_label.pack(padx=20, pady=20)
    progressbar = ttk.Progressbar(progress_window, mode='indeterminate')
    progressbar.pack(padx=20, pady=10)
    progressbar.start()

    def run_pip_install():
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + modules_to_install)
            progressbar.stop()
            progress_label.config(text="All modules installed successfully!")
        except subprocess.CalledProcessError as e:
            progressbar.stop()
            progress_label.config(text=f"Error installing modules: {e}")
        except FileNotFoundError:
            progressbar.stop()
            progress_label.config(text="pip command not found. Ensure Python is correctly installed and pip is in your PATH.")
        finally:
            install_button.config(state=tk.DISABLED)
            close_button = ttk.Button(progress_window, text="Close", command=progress_window.destroy)
            close_button.pack(pady=10)

    threading.Thread(target=run_pip_install, daemon=True).start()

root = tk.Tk()
root.title("Python Installer")
root.geometry("300x150")

python_installed = check_python_installed()

if python_installed:
    python_label = ttk.Label(root, text="Python 3 is already installed.")
    python_label.pack(pady=10)

    modules_present = True
    missing_modules = []
    modules_to_check = {
        "requests": "requests",
        "Pillow": "PIL",
        "cython": "cython",
        "aiohttp": "aiohttp"
    }

    for display_name, import_name in modules_to_check.items():
        if not check_module_installed(import_name):
            modules_present = False
            missing_modules.append(display_name)

    if modules_present:
        modules_label = ttk.Label(root, text="Required modules are already installed.")
        modules_label.pack(pady=5)
        install_button = ttk.Button(root, text="Installed", state=tk.DISABLED)
        install_button.pack(pady=10)
    else:
        modules_label = ttk.Label(root, text=f"Missing modules: {', '.join(missing_modules)}")
        modules_label.pack(pady=5)
        install_button = ttk.Button(root, text="Install Modules", command=install_modules)
        install_button.pack(pady=10)

else:
    python_label = ttk.Label(root, text="Python 3 is not installed.")
    python_label.pack(pady=10)
    install_button = ttk.Button(root, text="Install Python", command=install_python)
    install_button.pack(pady=10)

root.mainloop()