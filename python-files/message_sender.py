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
                ip, folder = line.strip().split(',', 1)
                instances[ip] = folder
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
    instances = load_instances()
    fake_ip = generate_fake_ip()
    while fake_ip in instances:  # Ensure unique IP
        fake_ip = generate_fake_ip()
    folder_path = f"instance_{fake_ip.replace('.', '_')}"
    instances[fake_ip] = folder_path
    save_instances(instances)
    print(f"Instance started with IP address: {fake_ip}")
    return fake_ip

def read_all_messages():
    """
    Reads all messages from all instance folders.
    """
    instances = load_instances()
    print("\nMessages from all instances:")
    for ip, folder in instances.items():
        file_path = os.path.join(folder, "message.bin")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                binary_data = file.read()
                print(f"IP: {ip}, Message (binary): {binary_data}")
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