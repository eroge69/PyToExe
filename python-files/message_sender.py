import os
import random

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
                # Skip empty or malformed lines
                if not line or ',' not in line:
                    print(f"Warning: Skipping invalid line in '{INSTANCES_FILE}': {line}")
                    continue
                try:
                    ip, folder = line.split(',', 1)
                    if not ip or not folder:  # Ensure both IP and folder are non-empty
                        raise ValueError("Empty IP or folder")
                    instances[ip] = folder
                except ValueError as e:
                    print(f"Warning: Skipping malformed line in '{INSTANCES_FILE}': {line}. Error: {e}")
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
        print(f"Error: Permission denied when trying to write to '{INSTANCES_FILE}'.")
        print("Ensure the file is not open in another program and you have write permissions.")

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
    print(f"Binary data saved to {file_path}")

def send_message_to_instance(message, target_ip):
    """
    Sends a message to a specific instance by its fake IP address.
    """
    instances = load_instances()
    if target_ip in instances:
        folder_path = instances[target_ip]
        binary_data = message_to_binary(message)
        save_binary_to_file(binary_data, folder_path)
    else:
        print(f"Error: No instance found with IP address {target_ip}")

def start_instance():
    """
    Starts a new instance and assigns it a fake IP address.
    """
    try:
        instances = load_instances()
        fake_ip = generate_fake_ip()
        while fake_ip in instances:  # Ensure unique IP
            fake_ip = generate_fake_ip()
        folder_path = f"instance_{fake_ip.replace('.', '_')}"
        
        # Attempt to create the folder
        try:
            os.makedirs(folder_path, exist_ok=True)
        except OSError as e:
            print(f"Error: Failed to create folder '{folder_path}'. {e}")
            return
        
        instances[fake_ip] = folder_path
        
        # Attempt to save instances
        try:
            save_instances(instances)
        except Exception as e:
            print(f"Error: Failed to save instances to '{INSTANCES_FILE}'. {e}")
            return
        
        print(f"Instance started with IP address: {fake_ip}")
        return fake_ip
    except Exception as e:
        print(f"Unexpected error in start_instance: {e}")

def read_all_messages():
    """
    Reads all messages from all instance folders and decodes them into readable text.
    """
    instances = load_instances()
    print("\nMessages from all instances:")
    for ip, folder in instances.items():
        file_path = os.path.join(folder, "message.bin")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                binary_data = file.read()
                decoded_message = binary_to_message(binary_data)
                print(f"IP: {ip}, Message (decoded): {decoded_message}")
        else:
            print(f"IP: {ip}, No messages found.")

# Example usage
if __name__ == "__main__":
    # Ensure the shared text file exists
    if not os.path.exists(INSTANCES_FILE):
        save_instances({})

    while True:
        print("\nOptions:")
        print("1. Send a message to an instance")
        print("2. Start a new instance")
        print("3. List all instances")
        print("4. Read all messages")
        print("5. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            target_ip = input("Enter the target instance's IP address: ")
            message = input("Enter the message to send: ")
            send_message_to_instance(message, target_ip)
        elif choice == "2":
            start_instance()
        elif choice == "3":
            instances = load_instances()
            print("\nActive instances:")
            for ip, folder in instances.items():
                print(f"IP: {ip}, Folder: {folder}")
        elif choice == "4":
            read_all_messages()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")