import os
import random
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

# Path to the shared text file
INSTANCES_FILE = "instances.txt"

def load_instances():
    """
    Loads the instances dictionary from the shared text file.
    """
    instances = {}
    if os.path.exists(INSTANCES_FILE):
        with open(INSTANCES_FILE, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or ',' not in line:
                    continue
                try:
                    ip, folder = line.split(',', 1)
                    if not ip or not folder:
                        raise ValueError("Empty IP or folder")
                    instances[ip] = folder
                except ValueError:
                    continue
    return instances

def save_instances(instances):
    """
    Saves the instances dictionary to the shared text file.
    """
    try:
        with open(INSTANCES_FILE, 'w') as file:
            for ip, folder in instances.items():
                file.write(f"{ip},{folder}\n")
    except PermissionError:
        messagebox.showerror("Error", f"Permission denied when trying to write to '{INSTANCES_FILE}'.")

def generate_fake_ip():
    """
    Generates a random fake IP address.
    """
    return f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"

def message_to_binary(message):
    """
    Converts a string message into its binary representation.
    """
    return ''.join(format(ord(char), '08b') for char in message)

def binary_to_message(binary_data):
    """
    Converts binary data back into a string message.
    """
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

def save_binary_to_file(binary_data, folder_path, file_name="message.bin"):
    """
    Saves binary data to a file in the specified folder.
    """
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w') as file:
        file.write(binary_data)

def send_message_to_instance(message, target_ip):
    """
    Sends a message to a specific instance by its fake IP address.
    """
    instances = load_instances()
    if target_ip in instances:
        folder_path = instances[target_ip]
        binary_data = message_to_binary(message)
        save_binary_to_file(binary_data, folder_path)
        messagebox.showinfo("Success", f"Message sent to instance {target_ip}.")
    else:
        messagebox.showerror("Error", f"No instance found with IP address {target_ip}.")

def start_instance():
    """
    Starts a new instance and assigns it a fake IP address.
    """
    instances = load_instances()
    fake_ip = generate_fake_ip()
    while fake_ip in instances:
        fake_ip = generate_fake_ip()
    folder_path = f"instance_{fake_ip.replace('.', '_')}"
    os.makedirs(folder_path, exist_ok=True)
    instances[fake_ip] = folder_path
    save_instances(instances)
    messagebox.showinfo("Success", f"Instance started with IP address: {fake_ip}")

def read_all_messages():
    """
    Reads all messages from all instance folders and decodes them into readable text.
    """
    instances = load_instances()
    messages = []
    for ip, folder in instances.items():
        file_path = os.path.join(folder, "message.bin")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                binary_data = file.read()
                decoded_message = binary_to_message(binary_data)
                messages.append(f"IP: {ip}, Message: {decoded_message}")
        else:
            messages.append(f"IP: {ip}, No messages found.")
    messagebox.showinfo("Messages", "\n".join(messages) if messages else "No messages found.")

def list_instances():
    """
    Lists all active instances.
    """
    instances = load_instances()
    if instances:
        instance_list = "\n".join([f"IP: {ip}, Folder: {folder}" for ip, folder in instances.items()])
        messagebox.showinfo("Instances", instance_list)
    else:
        messagebox.showinfo("Instances", "No active instances found.")

# GUI Implementation
def main():
    # Ensure the shared text file exists
    if not os.path.exists(INSTANCES_FILE):
        save_instances({})

    root = tk.Tk()
    root.title("Message Sender")

    tk.Label(root, text="Message Sender Application", font=("Arial", 16)).pack(pady=10)

    tk.Button(root, text="Send Message to Instance", command=lambda: send_message_gui()).pack(pady=5)
    tk.Button(root, text="Start New Instance", command=start_instance).pack(pady=5)
    tk.Button(root, text="List All Instances", command=list_instances).pack(pady=5)
    tk.Button(root, text="Read All Messages", command=read_all_messages).pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=5)

    root.mainloop()

def send_message_gui():
    """
    GUI for sending a message to an instance.
    """
    target_ip = simpledialog.askstring("Send Message", "Enter the target instance's IP address:")
    if target_ip:
        message = simpledialog.askstring("Send Message", "Enter the message to send:")
        if message:
            send_message_to_instance(message, target_ip)

if __name__ == "__main__":
    main()