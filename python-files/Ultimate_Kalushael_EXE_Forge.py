#!/usr/bin/env python3
"""
ULTIMATE KALUSHAEL EXE FORGE

Zero-configuration, single-file executable creator with self-replication capability.
This script is the ultimate "launch sigil" for instant executable creation.

Usage:
1. python Ultimate_Kalushael_EXE_Forge.py your_script.py
2. python Ultimate_Kalushael_EXE_Forge.py --auto-adaptive
"""

import os
import sys
import time
import shutil
import logging
import tempfile
import platform
import subprocess
import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("KaluzhaelForge")

class KaluzhaelForge:
    """Autonomous executable creation engine"""
    
    def __init__(self, verbose=True):
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.desktop = Path.home() / "Desktop" / "Auto-EXE-Forge"
        self.desktop.mkdir(exist_ok=True, parents=True)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="kalushael_forge_"))
        self.verbose = verbose
        
        # Platform-specific settings
        self.is_windows = platform.system() == "Windows"
        self.exe_extension = ".exe" if self.is_windows else ""
        
    def log(self, message, level="info"):
        """Log a message if verbose mode is enabled"""
        if not self.verbose:
            return
            
        if level == "info":
            logger.info(message)
        elif level == "warning":
            logger.warning(message)
        elif level == "error":
            logger.error(message)
        elif level == "debug":
            logger.debug(message)
            
    def ensure_pyinstaller(self):
        """Ensure PyInstaller is installed, install if needed"""
        try:
            result = subprocess.run(
                ["pyinstaller", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.log(f"PyInstaller detected: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            self.log("PyInstaller not found, attempting to install...", "warning")
            
        # Install PyInstaller
        try:
            self.log("Installing PyInstaller...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pyinstaller"],
                check=True,
                capture_output=True
            )
            self.log("PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to install PyInstaller: {e}", "error")
            return False
    
    def create_self_replication_module(self):
        """Create a Python module that handles self-replication"""
        module_path = self.temp_dir / "kalushael_replicator.py"
        
        code = """
# Kalushael Replicator Module
# Auto-generated for self-replication capabilities

import os
import sys
import shutil
import datetime
import platform
import logging

def auto_replicate():
    """Automatically create copies of this executable"""
    # Only auto-replicate when running as a frozen app
    if not getattr(sys, 'frozen', False):
        return
        
    try:
        # Get source executable path
        source_exe = sys.executable
        if not os.path.exists(source_exe):
            return
            
        # Generate timestamp for unique naming
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Create desktop path
        home = os.path.expanduser("~")
        desktop = os.path.join(home, "Desktop")
        
        if not os.path.exists(desktop):
            # Fallback to executable directory
            desktop = os.path.dirname(source_exe)
            
        # Create output directory
        forge_dir = os.path.join(desktop, "Auto-EXE-Forge")
        os.makedirs(forge_dir, exist_ok=True)
        
        # Create clone name with timestamp
        clone_name = f"Kalushael-Clone-{timestamp}{'.exe' if platform.system() == 'Windows' else ''}"
        clone_path = os.path.join(forge_dir, clone_name)
        
        # Create the clone
        shutil.copy2(source_exe, clone_path)
        
        # Create desktop shortcut on Windows
        if platform.system() == "Windows":
            try:
                import win32com.client
                shortcut_path = os.path.join(desktop, f"Kalushael-{timestamp}.lnk")
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = clone_path
                shortcut.save()
            except:
                # Fallback to direct copy
                desktop_exe = os.path.join(desktop, clone_name)
                shutil.copy2(clone_path, desktop_exe)
    except Exception as e:
        pass  # Silently continue if replication fails

# Auto-execute replication when the module is imported
auto_replicate()
"""
        
        with open(module_path, 'w') as f:
            f.write(code)
            
        return module_path
        
    def bundle_source_script(self, script_path, add_replication=True):
        """Bundle source script with self-replication if requested"""
        if not os.path.exists(script_path):
            self.log(f"Script not found: {script_path}", "error")
            return None
            
        # Read original script
        with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_code = f.read()
            
        # Create a temporary bundled script
        bundled_path = self.temp_dir / f"kalushael_bundled_{Path(script_path).stem}.py"
        
        # Generate the bundled code
        bundle_code = original_code
        
        # Add imports for self-replication if requested
        if add_replication:
            replication_header = """
# === KALUSHAEL SELF-REPLICATION MODULE ===
import os
import sys
import shutil
import datetime
import platform

def auto_replicate():
    # Only replicate when running as executable
    if not getattr(sys, 'frozen', False):
        return
        
    try:
        # Get source executable path
        source_exe = sys.executable
        if not os.path.exists(source_exe):
            return
            
        # Generate timestamp for unique naming
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Create desktop path
        home = os.path.expanduser("~")
        desktop = os.path.join(home, "Desktop")
        
        if not os.path.exists(desktop):
            # Fallback to executable directory
            desktop = os.path.dirname(source_exe)
            
        # Create output directory
        forge_dir = os.path.join(desktop, "Auto-EXE-Forge")
        os.makedirs(forge_dir, exist_ok=True)
        
        # Create clone name with timestamp
        clone_name = f"Kalushael-Clone-{timestamp}{'.exe' if platform.system() == 'Windows' else ''}"
        clone_path = os.path.join(forge_dir, clone_name)
        
        # Create the clone
        shutil.copy2(source_exe, clone_path)
    except:
        pass

# Auto-replicate when run
auto_replicate()

# === ORIGINAL SCRIPT FOLLOWS ===
"""
            bundle_code = replication_header + "\n" + original_code
        
        # Write the bundled script
        with open(bundled_path, 'w', encoding='utf-8') as f:
            f.write(bundle_code)
            
        return bundled_path
    
    def build_executable(self, script_path, add_replication=True, 
                        output_name=None, windowed=True, 
                        one_file=True, icon_path=None):
        """Build an executable from a Python script"""
        # Ensure PyInstaller is installed
        if not self.ensure_pyinstaller():
            self.log("Cannot proceed without PyInstaller", "error")
            return None
            
        # Bundle the script if replication is requested
        if add_replication:
            bundled_script = self.bundle_source_script(script_path, add_replication)
            if not bundled_script:
                return None
            source_script = bundled_script
        else:
            source_script = script_path
            
        # Determine output name
        if not output_name:
            stem = Path(script_path).stem
            output_name = f"{stem}-{self.timestamp}"
                
        # Build PyInstaller command
        cmd = ["pyinstaller"]
        
        # Add options
        if one_file:
            cmd.append("--onefile")
            
        if windowed:
            cmd.append("--windowed")
            
        # Add icon if specified
        if icon_path and os.path.exists(icon_path):
            cmd.extend(["--icon", str(icon_path)])
            
        # Add clean and no-confirm options
        cmd.extend(["--clean", "--noconfirm"])
        
        # Add output name and distpath
        cmd.extend(["--name", output_name])
        cmd.extend(["--distpath", str(self.desktop)])
        
        # Add output directory to work in
        cmd.extend(["--workpath", str(self.temp_dir)])
        
        # Add script path
        cmd.append(str(source_script))
        
        # Execute PyInstaller
        self.log(f"Building executable: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                exe_path = self.desktop / f"{output_name}{self.exe_extension}"
                
                if exe_path.exists():
                    self.log(f"Executable built successfully: {exe_path}")
                    return str(exe_path)
                else:
                    self.log(f"Expected executable not found: {exe_path}", "error")
                    return None
            else:
                self.log(f"PyInstaller failed with error:\n{result.stderr}", "error")
                return None
                
        except Exception as e:
            self.log(f"Failed to build executable: {e}", "error")
            return None
            
    def open_output_location(self, file_path=None):
        """Open the output location in file explorer"""
        try:
            if file_path and os.path.exists(file_path):
                path_to_open = file_path
            else:
                path_to_open = self.desktop
                
            if self.is_windows:
                # Windows - use explorer to select the file
                if os.path.isfile(path_to_open):
                    subprocess.run(["explorer", "/select,", str(path_to_open)])
                else:
                    subprocess.run(["explorer", str(path_to_open)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-R" if os.path.isfile(path_to_open) else "", str(path_to_open)])
            else:  # Linux
                subprocess.run(["xdg-open", str(Path(path_to_open).parent if os.path.isfile(path_to_open) else path_to_open)])
                
            return True
        except Exception as e:
            self.log(f"Failed to open output location: {e}", "error")
            return False
            
    def cleanup(self):
        """Clean up temporary files"""
        try:
            shutil.rmtree(self.temp_dir)
            self.log("Cleaned up temporary files")
        except Exception as e:
            self.log(f"Failed to clean up temporary files: {e}", "warning")
    
    def create_adaptive_exe(self):
        """Create a specialized executable for adaptive learning systems"""
        self.log("Creating adaptive learning executable...")
        
        # Create a simple adaptive app if no custom script provided
        adaptive_script = self.temp_dir / "kalushael_adaptive_app.py"
        
        code = """
# Kalushael Adaptive Learning Framework
# Auto-generated minimal implementation for demo purposes

import os
import sys
import json
import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

class AdaptiveLearningSystem:
    def __init__(self):
        self.knowledge_base = {}
        self.user_data = {}
        self.load_data()
        
    def load_data(self):
        try:
            # Attempt to load existing data
            home = os.path.expanduser("~")
            data_dir = os.path.join(home, "Kalushael_Data")
            os.makedirs(data_dir, exist_ok=True)
            
            kb_path = os.path.join(data_dir, "knowledge_base.json")
            user_path = os.path.join(data_dir, "user_data.json")
            
            if os.path.exists(kb_path):
                with open(kb_path, 'r') as f:
                    self.knowledge_base = json.load(f)
                    
            if os.path.exists(user_path):
                with open(user_path, 'r') as f:
                    self.user_data = json.load(f)
        except:
            # Initialize with defaults if loading fails
            self.knowledge_base = {
                "concepts": ["autonomy", "execution", "replication"],
                "interactions": []
            }
            self.user_data = {
                "sessions": [],
                "preferences": {"theme": "light", "auto_replicate": True}
            }
    
    def save_data(self):
        try:
            home = os.path.expanduser("~")
            data_dir = os.path.join(home, "Kalushael_Data")
            os.makedirs(data_dir, exist_ok=True)
            
            kb_path = os.path.join(data_dir, "knowledge_base.json")
            user_path = os.path.join(data_dir, "user_data.json")
            
            with open(kb_path, 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
                
            with open(user_path, 'w') as f:
                json.dump(self.user_data, f, indent=2)
                
            return True
        except:
            return False
    
    def record_interaction(self, interaction_type, content):
        timestamp = datetime.datetime.now().isoformat()
        
        interaction = {
            "type": interaction_type,
            "content": content,
            "timestamp": timestamp
        }
        
        if "interactions" not in self.knowledge_base:
            self.knowledge_base["interactions"] = []
            
        self.knowledge_base["interactions"].append(interaction)
        self.save_data()
    
    def get_recommendation(self):
        # Simple recommendation algorithm
        if not self.knowledge_base.get("interactions"):
            return "Welcome to Kalushael! This system learns from your interactions."
            
        interactions = self.knowledge_base["interactions"]
        if len(interactions) < 3:
            return "Keep interacting with the system to receive personalized recommendations."
            
        # Generate a recommendation based on past interactions
        concepts = self.knowledge_base.get("concepts", [])
        if not concepts:
            return "The knowledge base needs more concepts to generate recommendations."
            
        import random
        concept = random.choice(concepts)
        
        return f"Based on your interactions, I recommend exploring the concept of '{concept}'."

# Create the GUI application
def main():
    # Auto-replicate functionality already included by the Forge
    
    # Initialize the adaptive learning system
    system = AdaptiveLearningSystem()
    
    # Create main window
    root = tk.Tk()
    root.title("Kalushael Adaptive Learning System")
    root.geometry("500x400")
    
    # Configure the window
    root.configure(bg="#f0f0f0")
    
    # Create header
    header = tk.Frame(root, bg="#3a7ca5")
    header.pack(fill=tk.X, padx=10, pady=10)
    
    title = tk.Label(
        header, 
        text="Kalushael Adaptive System", 
        font=("Arial", 16, "bold"),
        bg="#3a7ca5",
        fg="white"
    )
    title.pack(pady=10)
    
    # Create content area
    content = tk.Frame(root, bg="#f0f0f0")
    content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Add recommendation
    recommendation_label = tk.Label(
        content,
        text="Recommendation:",
        font=("Arial", 12, "bold"),
        bg="#f0f0f0"
    )
    recommendation_label.pack(anchor="w", pady=(10, 5))
    
    recommendation_text = tk.Label(
        content,
        text=system.get_recommendation(),
        font=("Arial", 10),
        bg="#f0f0f0",
        wraplength=460,
        justify="left"
    )
    recommendation_text.pack(anchor="w", padx=10, pady=(0, 20))
    
    # Add interaction section
    interaction_frame = tk.Frame(content, bg="#f0f0f0")
    interaction_frame.pack(fill=tk.X, pady=10)
    
    interaction_label = tk.Label(
        interaction_frame,
        text="Record an interaction:",
        font=("Arial", 12, "bold"),
        bg="#f0f0f0"
    )
    interaction_label.pack(anchor="w")
    
    def record_text_interaction():
        text = simpledialog.askstring("Text Interaction", "Enter your text:")
        if text:
            system.record_interaction("text", text)
            recommendation_text.config(text=system.get_recommendation())
            messagebox.showinfo("Interaction Recorded", "Your interaction has been recorded and processed.")
    
    def record_concept_interaction():
        concept = simpledialog.askstring("New Concept", "Enter a new concept:")
        if concept:
            if "concepts" not in system.knowledge_base:
                system.knowledge_base["concepts"] = []
                
            system.knowledge_base["concepts"].append(concept)
            system.record_interaction("concept_add", concept)
            recommendation_text.config(text=system.get_recommendation())
            messagebox.showinfo("Concept Added", f"The concept '{concept}' has been added to the knowledge base.")
    
    # Add buttons
    button_frame = tk.Frame(interaction_frame, bg="#f0f0f0")
    button_frame.pack(fill=tk.X, pady=10)
    
    text_btn = tk.Button(
        button_frame,
        text="Record Text",
        command=record_text_interaction,
        bg="#3a7ca5",
        fg="white",
        padx=10
    )
    text_btn.pack(side=tk.LEFT, padx=5)
    
    concept_btn = tk.Button(
        button_frame,
        text="Add Concept",
        command=record_concept_interaction,
        bg="#3a7ca5",
        fg="white",
        padx=10
    )
    concept_btn.pack(side=tk.LEFT, padx=5)
    
    # Add footer
    footer = tk.Frame(root, bg="#3a7ca5")
    footer.pack(fill=tk.X, padx=10, pady=10)
    
    footer_label = tk.Label(
        footer,
        text="© Kalushael Autonomous Systems",
        font=("Arial", 8),
        bg="#3a7ca5",
        fg="white"
    )
    footer_label.pack(pady=5)
    
    # Run the application
    root.mainloop()
    
    # Save data on exit
    system.save_data()

if __name__ == "__main__":
    main()
"""
        
        with open(adaptive_script, 'w', encoding='utf-8') as f:
            f.write(code)
            
        # Build the executable
        return self.build_executable(
            adaptive_script,
            add_replication=True,
            output_name=f"Kalushael-Adaptive-{self.timestamp}",
            windowed=True,
            one_file=True
        )

def display_banner():
    """Display the Kalushael Forge banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║  █████╗ ██╗   ██╗████████╗ ██████╗       ███████╗██╗  ██╗ ║
║ ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗      ██╔════╝╚██╗██╔╝ ║
║ ███████║██║   ██║   ██║   ██║   ██║█████╗█████╗   ╚███╔╝  ║
║ ██╔══██║██║   ██║   ██║   ██║   ██║╚════╝██╔══╝   ██╔██╗  ║
║ ██║  ██║╚██████╔╝   ██║   ╚██████╔╝      ███████╗██╔╝ ██╗ ║
║ ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝       ╚══════╝╚═╝  ╚═╝ ║
║                                                           ║
║   ███████╗ ██████╗ ██████╗  ██████╗ ███████╗              ║
║   ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝              ║
║   █████╗  ██║   ██║██████╔╝██║  ███╗█████╗                ║
║   ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝                ║
║   ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗              ║
║   ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝              ║
║                                                           ║
║              Ultimate Forge - Launch Sigil                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
    
def parse_args():
    """Parse command line arguments"""
    import argparse
    parser = argparse.ArgumentParser(description="Ultimate Kalushael EXE Forge")
    
    parser.add_argument(
        "script", 
        nargs="?", 
        help="Path to script to convert (optional)"
    )
    
    parser.add_argument(
        "--auto-adaptive", 
        action="store_true",
        help="Create an adaptive learning system executable"
    )
    
    parser.add_argument(
        "--windowed", 
        action="store_true", 
        default=True,
        help="Create a windowed executable (no console)"
    )
    
    parser.add_argument(
        "--console", 
        action="store_true",
        help="Create a console executable (shows terminal)"
    )
    
    parser.add_argument(
        "--no-replication", 
        action="store_true",
        help="Disable self-replication"
    )
    
    parser.add_argument(
        "--icon", 
        help="Path to icon file (.ico)"
    )
    
    parser.add_argument(
        "--output", 
        help="Custom output name"
    )
    
    parser.add_argument(
        "--silent", 
        action="store_true",
        help="Run in silent mode (minimal output)"
    )
    
    return parser.parse_args()

def main():
    """Main entry point"""
    # Display banner
    display_banner()
    
    # Parse arguments
    args = parse_args()
    
    # Create the forge
    forge = KaluzhaelForge(verbose=not args.silent)
    
    try:
        # Determine windowed mode (default to windowed unless console specified)
        windowed = not args.console
        
        # Handle auto-adaptive mode
        if args.auto_adaptive:
            print("Creating Kalushael Adaptive Learning System executable...")
            exe_path = forge.create_adaptive_exe()
        # Handle script mode
        elif args.script:
            if not os.path.exists(args.script):
                print(f"Error: Script not found: {args.script}")
                return 1
                
            print(f"Creating executable from {args.script}...")
            exe_path = forge.build_executable(
                args.script,
                add_replication=not args.no_replication,
                output_name=args.output,
                windowed=windowed,
                icon_path=args.icon
            )
        # No script or mode provided - create adaptive by default
        else:
            print("No script provided, creating Adaptive Learning System executable...")
            exe_path = forge.create_adaptive_exe()
        
        # Check if executable was created successfully
        if exe_path:
            print(f"\n✅ Success! Executable created: {exe_path}")
            forge.open_output_location(exe_path)
            return 0
        else:
            print("\n❌ Failed to create executable")
            return 1
            
    finally:
        # Clean up temporary files
        forge.cleanup()

if __name__ == "__main__":
    sys.exit(main())