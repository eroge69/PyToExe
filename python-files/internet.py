import os
import random
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import webbrowser  # For opening websites in the default browser
from tkhtmlview import HTMLLabel  # Import the HTMLLabel widget from tkhtmlview

# Path to the shared text file
INSTANCES_FILE = "instances.txt"
WEBSITES_FOLDER = "websites"  # Folder to store website files
current_user = None  # Tracks the currently logged-in user

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
                    username, password, folder = line.split(',', 2)
                    if not username or not password or not folder:
                        raise ValueError("Empty username, password, or folder")
                    instances[username] = {"password": password, "folder": folder}
                except ValueError:
                    continue
    return instances

def save_instances(instances):
    """
    Saves the instances dictionary to the shared text file.
    """
    try:
        with open(INSTANCES_FILE, 'w') as file:
            for username, data in instances.items():
                file.write(f"{username},{data['password']},{data['folder']}\n")
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

def send_message_to_instance(message, target_username):
    """
    Sends a message to a specific instance by its username.
    """
    instances = load_instances()
    if target_username in instances:
        folder_path = instances[target_username]["folder"]
        binary_data = message_to_binary(message)
        save_binary_to_file(binary_data, folder_path)
        messagebox.showinfo("Success", f"Message sent to instance '{target_username}'.")
    else:
        messagebox.showerror("Error", f"No instance found with username '{target_username}'.")

def read_all_messages():
    """
    Reads all messages from all instance folders and decodes them into readable text.
    """
    instances = load_instances()
    messages = []
    for username, data in instances.items():
        folder = data["folder"]
        file_path = os.path.join(folder, "message.bin")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                binary_data = file.read()
                decoded_message = binary_to_message(binary_data)
                messages.append(f"Username: {username}, Message: {decoded_message}")
        else:
            messages.append(f"Username: {username}, No messages found.")
    messagebox.showinfo("Messages", "\n".join(messages) if messages else "No messages found.")

def read_my_messages():
    """
    Reads messages sent to the current instance and decodes them into readable text.
    """
    if not current_user:
        messagebox.showerror("Error", "You must be logged in to read your messages.")
        return

    instances = load_instances()
    folder = instances[current_user]["folder"]
    file_path = os.path.join(folder, "message.bin")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            binary_data = file.read()
            decoded_message = binary_to_message(binary_data)
            messagebox.showinfo("Messages", f"Message for '{current_user}': {decoded_message}")
    else:
        messagebox.showinfo("Messages", f"No messages found for '{current_user}'.")

def list_instances():
    """
    Lists all active instances.
    """
    instances = load_instances()
    if instances:
        instance_list = "\n".join([f"Username: {username}, Folder: {data['folder']}" for username, data in instances.items()])
        messagebox.showinfo("Instances", instance_list)
    else:
        messagebox.showinfo("Instances", "No active instances found.")

def send_message_gui():
    """
    GUI for sending a message to an instance.
    """
    if not current_user:
        messagebox.showerror("Error", "You must be logged in to send a message.")
        return

    target_username = simpledialog.askstring("Send Message", "Enter the target instance's username:")
    if target_username:
        message = simpledialog.askstring("Send Message", "Enter the message to send:")
        if message:
            send_message_to_instance(message, target_username)

def launch_message_sender():
    """
    Launches the Message Sender application.
    """
    def message_sender_main():
        """
        Main function for the Message Sender application.
        """
        def login_screen(root, buttons_frame):
            """
            Displays the login screen with options to log in or create a new user.
            """
            def login_user():
                """
                Handles user login.
                """
                global current_user
                username = simpledialog.askstring("Login", "Enter your username:")
                if not username:
                    return

                password = simpledialog.askstring("Login", "Enter your password:", show="*")
                if not password:
                    return

                instances = load_instances()
                if username in instances and instances[username]["password"] == password:
                    current_user = username
                    messagebox.showinfo("Login Successful", f"Welcome back, {username}!")
                    buttons_frame.pack(pady=10)  # Show the main menu buttons
                else:
                    messagebox.showerror("Error", "Invalid username or password.")

            def create_new_user():
                """
                Handles creating a new user.
                """
                instances = load_instances()
                username = simpledialog.askstring("Create New User", "Enter a username for the new user:")
                if not username:
                    return

                if username in instances:
                    messagebox.showerror("Error", f"A user with the username '{username}' already exists.")
                    return

                password = simpledialog.askstring("Create New User", "Enter a password for the new user:", show="*")
                if not password:
                    return

                folder_path = f"instance_{username}"
                os.makedirs(folder_path, exist_ok=True)
                instances[username] = {"password": password, "folder": folder_path}
                save_instances(instances)
                messagebox.showinfo("Success", f"User created with username: {username}")

            # Create a new window for the login screen
            login_window = tk.Toplevel(root)
            login_window.title("Login Screen")

            tk.Label(login_window, text="Login or Create a New User", font=("Arial", 14)).pack(pady=10)

            tk.Button(login_window, text="Login", command=login_user).pack(pady=5)
            tk.Button(login_window, text="Create New User", command=create_new_user).pack(pady=5)
            tk.Button(login_window, text="Close", command=login_window.destroy).pack(pady=5)

        # Message Sender GUI
        root = tk.Toplevel()
        root.title("Message Sender")

        tk.Label(root, text="Message Sender Application", font=("Arial", 16)).pack(pady=10)

        # Frame for the main menu buttons (hidden until login)
        buttons_frame = tk.Frame(root)
        tk.Button(buttons_frame, text="Send Message to Instance", command=lambda: send_message_gui()).pack(pady=5)
        tk.Button(buttons_frame, text="List All Instances", command=list_instances).pack(pady=5)
        tk.Button(buttons_frame, text="Read My Messages", command=read_my_messages).pack(pady=5)
        tk.Button(buttons_frame, text="Exit", command=root.destroy).pack(pady=5)

        # Initially hide the buttons frame
        buttons_frame.pack_forget()

        # Login button
        tk.Button(root, text="Login", command=lambda: login_screen(root, buttons_frame)).pack(pady=5)

        root.mainloop()

    message_sender_main()

def make_website():
    """
    Allows the user to create a website by entering HTML code and choosing a domain name.
    """
    # Ensure the websites folder exists
    os.makedirs(WEBSITES_FOLDER, exist_ok=True)

    # Prompt the user for a domain name
    domain = simpledialog.askstring("Make a Website", "Enter a domain name (e.g., example.com):")
    if not domain:
        return

    # Check if the domain already exists
    file_path = os.path.join(WEBSITES_FOLDER, f"{domain}.html")
    if os.path.exists(file_path):
        overwrite = messagebox.askyesno("Domain Exists", f"The domain '{domain}' already exists. Overwrite?")
        if not overwrite:
            return

    # Prompt the user for HTML code
    html_code = simpledialog.askstring("Make a Website", "Enter your HTML code:")
    if not html_code:
        return

    # Save the HTML code to a file
    with open(file_path, 'w') as file:
        file.write(html_code)

    messagebox.showinfo("Success", f"Website '{domain}' created successfully!")

def visit_website():
    """
    Allows the user to visit a website by entering its domain name and displays it rendered in a new window.
    """
    # Prompt the user for a domain name
    domain = simpledialog.askstring("Visit a Website", "Enter the domain name (e.g., example.com):")
    if not domain:
        return

    # Check if the domain exists
    file_path = os.path.join(WEBSITES_FOLDER, f"{domain}.html")
    if not os.path.exists(file_path):
        messagebox.showerror("Error", f"The website '{domain}' does not exist.")
        return

    # Read the HTML content
    with open(file_path, 'r') as file:
        html_content = file.read()

    # Create a new window to display the rendered HTML content
    website_window = tk.Toplevel()
    website_window.title(f"Website: {domain}")

    # Use HTMLLabel to render the HTML content
    html_label = HTMLLabel(website_window, html=html_content)
    html_label.pack(expand=True, fill="both")

def main_homepage():
    """
    Main homepage for the simulated internet.
    """
    root = tk.Tk()
    root.title("Internet Homepage")

    tk.Label(root, text="Welcome to the Internet", font=("Arial", 20)).pack(pady=20)

    # Button to launch the Message Sender application
    tk.Button(root, text="Launch Message Sender", command=launch_message_sender, width=30).pack(pady=10)

    # Button to make a website
    tk.Button(root, text="Make a Website", command=make_website, width=30).pack(pady=10)

    # Button to visit a website
    tk.Button(root, text="Visit a Website", command=visit_website, width=30).pack(pady=10)

    tk.Button(root, text="Exit", command=root.quit, width=30).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_homepage()