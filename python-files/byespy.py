import os
import json
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from PIL import Image, ImageTk
import requests

# Define the target words to search for
target_words = ["https://", "PerformHttpRequest", "GetConvar", "os.execute", "txAdmin"]

# Whitelist of safe domains
whitelist_domains = [
    "docs.fivem.net",
    "discord.com",
    "discord.gg",
    "tebex.io",
    "discordapp.com",
    "cdn.discordapp.com",
    "media.tenor.com",
    "youtube.com",
    "steampowered.com",
    "raw.githubusercontent.com"
]

# Initialize the root folder variable
root_folder = "scripts"

# Initialize a list to store detected issues
detected_issues = []

# Discord webhook URL (replace with your actual webhook URL)
webhook_url = ""

def is_whitelisted(url):
    # Check if the domain or URL is in the whitelist
    for domain in whitelist_domains:
        if domain in url:
            return True
    return False

def extract_urls(line):
    # Regex pattern to match URLs
    url_pattern = re.compile(r'https?://[^\s\'"]+')
    return url_pattern.findall(line)

def scan_file_for_naughty_code(file_path):
    found_words = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        try:
            with open(file_path, "r", encoding="latin-1") as file:
                lines = file.readlines()
        except Exception as e:
            log_message(f"Failed to read {file_path}: {e}")
            return found_words

    for line_num, line in enumerate(lines, start=1):
        for word in target_words:
            if word in line:
                # Extract URLs and check if they are whitelisted
                urls = extract_urls(line)
                if urls:
                    for url in urls:
                        if not is_whitelisted(url):
                            found_words.append((line_num, line.strip(), word))
                            listbox.insert(tk.END, f"Found '{word}' in {file_path} on line {line_num}")
                else:
                    found_words.append((line_num, line.strip(), word))
                    listbox.insert(tk.END, f"Found '{word}' in {file_path} on line {line_num}")
    return found_words

def scan_folder(folder_path):
    global detected_issues
    detected_issues = []
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".lua") or file_name.endswith(".txt"):
                file_path = os.path.join(root, file_name)
                found_words = scan_file_for_naughty_code(file_path)
                if found_words:
                    detected_issues.append({
                        "file": file_path,
                        "issues": found_words
                    })

    # Send the results to the Discord webhook
    send_to_discord(detected_issues)

def show_details(event):
    selection = listbox.curselection()
    if selection:
        index = selection[0]
        selected_issue_index = 0
        for issue_index, issue in enumerate(detected_issues):
            if len(issue["issues"]) > index - selected_issue_index:
                details_textbox.delete(1.0, tk.END)
                # Display each issue (line of code) found in the file
                for line_num, line, word in issue["issues"]:
                    details_textbox.insert(tk.END, f"Line {line_num}: {line}\n\n")
                break
            selected_issue_index += len(issue["issues"])


def start_scan():
    listbox.delete(0, tk.END)
    details_textbox.delete(1.0, tk.END)
    if not root_folder:
        log_message("Please select a folder to scan.")
        return
    log_message(f"Starting scan in folder: {root_folder}...")
    scan_folder(root_folder)
    if not detected_issues:
        log_message("No naughty code found.")
    else:
        log_message("Scan completed. Select an item from the list to view details.")

def browse_folder():
    global root_folder
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        root_folder = folder_selected
        folder_label.config(text=f"Selected Folder: {root_folder}")
        log_message(f"Selected folder: {root_folder}")

def log_message(message):
    output_textbox.insert(tk.END, message + "\n")
    output_textbox.see(tk.END)


def send_to_discord(issues):
    if not issues:
        return

    embeds = []

    for issue in issues:
        file_name = issue['file']
        description = ""
        for line_num, line, word in issue['issues']:
            description += f"**Line {line_num}**: `{line}`\n**Keyword**: `{word}`\n\n"
        
        embed = {
            "title": f"Backdoor Scan Alert - {os.path.basename(file_name)}",
            "description": description,
            "color": 16711680,  # Red color for the alert
            "fields": [
                {
                    "name": "File",
                    "value": file_name,
                    "inline": False
                }
            ],
            "footer": {
                "text": "5Mservers.com Free Code Scanner"
            }
        }

        embeds.append(embed)

    data = {
        "content": "**Backdoor Scan Results**",
        "embeds": embeds
    }

    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            log_message("Results sent to Discord successfully.")
        else:
            log_message(f"Failed to send results to Discord. HTTP Status Code: {response.status_code}")
    except Exception as e:
        log_message(f"Failed to send results to Discord: {e}")

def delete_bad_code():
    selection = listbox.curselection()
    if not selection:
        log_message("No item selected.")
        return

    index = selection[0]
    selected_issue_index = 0

    for issue_index, issue in enumerate(detected_issues):
        if len(issue["issues"]) > index - selected_issue_index:
            file_path = issue["file"]
            issues_to_delete = issue["issues"]

            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()

                # Remove or comment out the bad code
                for line_num, _, _ in issues_to_delete:
                    lines[line_num - 1] = f"-- BAD CODE REMOVED: {lines[line_num - 1]}"

                # Write the cleaned content back to the file
                with open(file_path, "w", encoding="utf-8") as file:
                    file.writelines(lines)

                log_message(f"Bad code removed from {file_path}")
            except Exception as e:
                log_message(f"Failed to remove bad code from {file_path}: {e}")

            break
        selected_issue_index += len(issue["issues"])

    # Refresh the listbox and details textbox after deletion
    start_scan()


# Create the main application window
root = tk.Tk()
root.title("5Mservers.com Free Code Scanner")
root.geometry("800x600")

# Load the background image
background_image = Image.open("clip.png")  # Replace with your image path
background_image = background_image.resize((800, 600), Image.Resampling.LANCZOS)

background_photo = ImageTk.PhotoImage(background_image)

# Create a canvas widget
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack(fill="both", expand=True)

# Set the background image on the canvas
canvas.create_image(0, 0, image=background_photo, anchor="nw")

# Create a styled label for the title
title_label = tk.Label(root, text="Code Scanner", font=("Courier", 24), fg="lime", bg="black")
title_label_window = canvas.create_window(400, 30, window=title_label)

# Create a folder selection label
folder_label = tk.Label(root, text=f"Selected Folder: {root_folder}", font=("Courier", 12), fg="lime", bg="black")
folder_label_window = canvas.create_window(400, 70, window=folder_label)

# Create a frame to hold the buttons
button_frame = tk.Frame(root, bg="black")
button_frame_window = canvas.create_window(400, 110, window=button_frame)

# Create the browse button to select the folder
browse_button = ttk.Button(button_frame, text="Browse Folder", command=browse_folder)
browse_button.pack(side=tk.LEFT, padx=5)
# Create the delete button to remove the detected bad code
delete_button = ttk.Button(button_frame, text="Delete Bad Code", command=delete_bad_code)
delete_button.pack(side=tk.LEFT, padx=5)

# Create the scan button
scan_button = ttk.Button(button_frame, text="Start Scan", command=start_scan)
scan_button.pack(side=tk.LEFT, padx=5)

# Create a listbox to display the scan results
listbox = tk.Listbox(root, font=("Courier", 12), fg="lime", bg="black", selectbackground="gray", activestyle="dotbox")
listbox_window = canvas.create_window(400, 300, window=listbox, width=750, height=200)
listbox.bind('<<ListboxSelect>>', show_details)

# Create a scrolled text widget for displaying details of the selected issue
details_textbox = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier", 12), fg="lime", bg="black", insertbackground="lime")
details_textbox_window = canvas.create_window(400, 480, window=details_textbox, width=750, height=100)

# Create a scrolled text widget for displaying log messages
output_textbox = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier", 10), fg="white", bg="black", insertbackground="white", height=4)
output_textbox_window = canvas.create_window(400, 550, window=output_textbox, width=750, height=50)

# Start the application
root.mainloop()
