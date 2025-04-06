import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from cryptography.fernet import Fernet
import socket
import threading
import os
import json
import uuid

# Functions for encryption and decryption
def generate_fernet_key():
    return Fernet.generate_key()

def load_settings():
    try:
        with open("settings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"save_directory": os.getcwd()}

def encrypt_message_fernet(key, message):
    cipher = Fernet(key)
    encrypted_message = cipher.encrypt(message.encode())
    return encrypted_message

def decrypt_message_fernet(key, encrypted_message):
    cipher = Fernet(key)
    decrypted_message = cipher.decrypt(encrypted_message).decode()
    return decrypted_message

def encrypt_file_fernet(key, file_path):
    cipher = Fernet(key)
    with open(file_path, 'rb') as file:
        file_data = file.read()
    encrypted_data = cipher.encrypt(file_data)
    return encrypted_data

def decrypt_file_fernet(key, encrypted_data, output_path):
    try:
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # Автоматическое определение типа файла
        try:
            # Попытка декодировать как текстовый файл
            decrypted_text = decrypted_data.decode('utf-8')
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(decrypted_text)
        except UnicodeDecodeError:
            # Если не текстовый файл - сохраняем как бинарный
            with open(output_path, 'wb') as file:
                file.write(decrypted_data)
        
        return decrypted_data
    except Exception as e:
        print(f"Ошибка при дешифровке: {e}")
        raise

# Networking functions
def start_server(app, host="0.0.0.0", port=12345):
    def server_thread():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(5)  # Поддержка до 5 подключений
        print(f"Сервер запущен на {host}:{port}")
        
        clients = {}  # Словарь для хранения подключенных клиентов
        
        while True:
            conn, addr = server_socket.accept()
            print(f"Подключение от {addr}")
            clients[addr] = conn
            threading.Thread(target=handle_client, args=(app, conn, addr, clients), daemon=True).start()

    def handle_client(app, conn, addr, clients):
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                # Дешифруем полученное сообщение
                decrypted_message = decrypt_message_fernet(app.key, data)
                app.root.after(0, update_chat, app, f"{addr[0]}:{addr[1]}: {decrypted_message}")
            except Exception as e:
                print(f"Ошибка с клиентом {addr}: {e}")
                break
        conn.close()
        del clients[addr]
        app.root.after(0, update_chat, app, f"{addr[0]}:{addr[1]} отключился")

    def update_chat(app, message):
        app.chat_text.insert(tk.END, message + "\n")
        app.chat_text.see(tk.END)

    threading.Thread(target=server_thread, daemon=True).start()

def send_message_to_server(host, port, encrypted_message):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        client_socket.sendall(encrypted_message)
        client_socket.close()
        print("Сообщение отправлено.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось отправить сообщение: {str(e)}")

def send_file_to_server(host, port, encrypted_file_data):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        client_socket.sendall(encrypted_file_data)
        client_socket.close()
        print("Файл отправлен.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось отправить файл: {str(e)}")

# GUI Application
class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Message Encryption & Decryption")
        self.root.geometry("500x600")
        
        self.key = generate_fernet_key()
        self.server_ip = "127.0.0.1"  # Default server IP
        self.server_port = 12345
        print(f"Сгенерированный ключ: {self.key.decode()}")

        # Setup dark theme
        self.root.configure(bg="#2e2e2e")
        self.root.tk_setPalette(background="#2e2e2e")
        
        # Tabs (Message Encryption, File Encryption, Chat, Settings)
        self.tab_control = ttk.Notebook(root)
        self.message_tab = tk.Frame(self.tab_control, bg="#2e2e2e")
        self.file_tab = tk.Frame(self.tab_control, bg="#2e2e2e")
        self.chat_tab = tk.Frame(self.tab_control, bg="#2e2e2e")
        self.settings_tab = tk.Frame(self.tab_control, bg="#2e2e2e")
        
        self.tab_control.add(self.message_tab, text="Message Encryption")
        self.tab_control.add(self.file_tab, text="File Encryption")
        self.tab_control.add(self.chat_tab, text="Chat")
        self.tab_control.add(self.settings_tab, text="Settings")
        self.tab_control.pack(expand=1, fill="both")

        # Message Encryption Section
        self.create_message_encryption_tab()

        # File Encryption Section
        self.create_file_encryption_tab()

        # Chat Section
        self.create_chat_tab()

        # Settings Section
        self.create_settings_tab()

        # Start server
        start_server(self)

    def save_settings(self):
        settings = {
            "server_ip": self.server_ip_entry.get(),
            "save_directory": self.save_directory_entry.get() or os.getcwd()
        }
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f)
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.server_ip = settings["server_ip"]
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {e}")

    def create_message_encryption_tab(self):
        tk.Label(self.message_tab, text="Encryption", font=("Arial", 14), bg="#2e2e2e", fg="white").pack(pady=10)

        tk.Label(self.message_tab, text="Enter your message:", bg="#2e2e2e", fg="white").pack()
        self.message_entry = tk.Entry(self.message_tab, width=50, bg="#555", fg="white", borderwidth=2, relief="solid")
        self.message_entry.pack(pady=5)

        tk.Button(self.message_tab, text="Encrypt", command=self.encrypt_message_gui, bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5).pack(pady=10)

        tk.Label(self.message_tab, text="Encrypted Message:", bg="#2e2e2e", fg="white").pack()
        self.encrypted_message = tk.Text(self.message_tab, height=4, width=50, bg="#555", fg="white", wrap="word", relief="solid")
        self.encrypted_message.pack(pady=5)

        tk.Button(self.message_tab, text="Send to Server", command=self.send_to_server_gui, bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5).pack(pady=10)

        # Decryption Section
        tk.Label(self.message_tab, text="Decryption", font=("Arial", 14), bg="#2e2e2e", fg="white").pack(pady=10)

        tk.Label(self.message_tab, text="Received encrypted message:", bg="#2e2e2e", fg="white").pack()
        self.decrypted_message_entry = tk.Text(self.message_tab, height=4, width=50, bg="#555", fg="white", wrap="word", relief="solid")
        self.decrypted_message_entry.pack(pady=5)

        tk.Button(self.message_tab, text="Decrypt", command=self.decrypt_message_gui, bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5).pack(pady=10)

        tk.Label(self.message_tab, text="Decrypted Message:", bg="#2e2e2e", fg="white").pack()
        self.decrypted_message = tk.Entry(self.message_tab, width=50, bg="#555", fg="white", borderwidth=2, relief="solid")
        self.decrypted_message.pack(pady=5)

    def create_file_encryption_tab(self):
        tk.Label(self.file_tab, text="Encrypt a File", font=("Arial", 14), bg="#2e2e2e", fg="white").pack(pady=10)

        tk.Button(self.file_tab, text="Choose File", command=self.choose_file_to_encrypt, bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5).pack(pady=10)

        self.file_path_label = tk.Label(self.file_tab, text="No file selected", bg="#2e2e2e", fg="white")
        self.file_path_label.pack(pady=5)

        tk.Button(self.file_tab, text="Encrypt and Send", command=self.encrypt_and_send_file, bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5).pack(pady=10)

        tk.Label(self.file_tab, text="Decrypt a File", font=("Arial", 14), bg="#2e2e2e", fg="white").pack(pady=10)

        tk.Button(self.file_tab, text="Choose Encrypted File", command=self.choose_file_to_decrypt, bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5).pack(pady=10)

        self.decrypted_file_label = tk.Label(self.file_tab, text="No file selected", bg="#2e2e2e", fg="white")
        self.decrypted_file_label.pack(pady=5)

        tk.Button(self.file_tab, text="Decrypt File", command=self.decrypt_file, bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5).pack(pady=10)

    def create_chat_tab(self):
        tk.Label(self.chat_tab, text="Chat", font=("Arial", 14), bg="#2e2e2e", fg="white").pack(pady=10)

        # Поле для ввода IP друга
        tk.Label(self.chat_tab, text="Friend's IP:", bg="#2e2e2e", fg="white").pack()
        self.friend_ip_entry = tk.Entry(self.chat_tab, width=20, bg="#555", fg="white", borderwidth=2, relief="solid")
        self.friend_ip_entry.pack(pady=5)

        # Кнопка подключения
        tk.Button(self.chat_tab, text="Connect", command=self.connect_to_friend, bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5).pack(pady=5)

        # История чата
        self.chat_text = tk.Text(self.chat_tab, height=10, width=50, bg="#555", fg="white", wrap="word", relief="solid")
        self.chat_text.pack(pady=5)

        # Поле ввода сообщения
        self.chat_entry = tk.Entry(self.chat_tab, width=50, bg="#555", fg="white", borderwidth=2, relief="solid")
        self.chat_entry.pack(pady=5)

        # Кнопка отправки
        tk.Button(self.chat_tab, text="Send", command=self.send_chat_message, bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5).pack(pady=5)

    def create_settings_tab(self):
        tk.Label(self.settings_tab, text="Settings", font=("Arial", 14), bg="#2e2e2e", fg="white").pack(pady=10)

        tk.Label(self.settings_tab, text="Enter server IP address:", bg="#2e2e2e", fg="white").pack()
        self.server_ip_entry = tk.Entry(self.settings_tab, width=50, bg="#555", fg="white", borderwidth=2, relief="solid")
        self.server_ip_entry.pack(pady=5)

        # Save Directory Settings
        tk.Label(self.settings_tab, text="Save Directory for Received Files:", bg="#2e2e2e", fg="white").pack()
    
        self.save_directory_frame = tk.Frame(self.settings_tab, bg="#2e2e2e")
        self.save_directory_frame.pack(pady=5)
    
        self.save_directory_entry = tk.Entry(self.save_directory_frame, width=40, bg="#555", fg="white", borderwidth=2, relief="solid")
        self.save_directory_entry.pack(side=tk.LEFT, padx=5)
    
        tk.Button(self.save_directory_frame, text="Browse", command=self.choose_save_directory, bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5).pack(side=tk.LEFT)

        # Save Button
        tk.Button(self.settings_tab, text="Save Settings", command=self.save_settings, bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5).pack(pady=10)

        # Load existing settings
        self.load_existing_settings()

    def load_existing_settings(self):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
            
            # Load server IP
            if "server_ip" in settings:
                self.server_ip_entry.delete(0, tk.END)
                self.server_ip_entry.insert(0, settings["server_ip"])
                self.server_ip = settings["server_ip"]

            # Load save directory
            save_directory = settings.get("save_directory", os.getcwd())
            self.save_directory_entry.delete(0, tk.END)
            self.save_directory_entry.insert(0, save_directory)

        except FileNotFoundError:
            # Set default values if settings file doesn't exist
            self.save_directory_entry.insert(0, os.getcwd())
            self.server_ip_entry.insert(0, "127.0.0.1")

    def choose_save_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_directory_entry.delete(0, tk.END)
            self.save_directory_entry.insert(0, directory)

    def encrypt_message_gui(self):
        message = self.message_entry.get()
        if not message:
            messagebox.showerror("Error", "Please enter a message to encrypt.")
            return
        encrypted = encrypt_message_fernet(self.key, message)
        self.encrypted_message.delete(1.0, tk.END)
        self.encrypted_message.insert(tk.END, encrypted.decode())

    def send_to_server_gui(self):
        host = self.server_ip
        encrypted_message = self.encrypted_message.get(1.0, tk.END).strip()
        if not host or not encrypted_message:
            messagebox.showerror("Error", "Please provide a valid server IP and encrypted message.")
            return
        send_message_to_server(host, self.server_port, encrypted_message.encode())

    def decrypt_message_gui(self):
        encrypted_message = self.decrypted_message_entry.get(1.0, tk.END).strip()
        if not encrypted_message:
            messagebox.showerror("Error", "Please enter an encrypted message to decrypt.")
            return
        try:
            decrypted_message = decrypt_message_fernet(self.key, encrypted_message.encode())
            self.decrypted_message.delete(0, tk.END)
            self.decrypted_message.insert(tk.END, decrypted_message)
        except Exception as e:
            try:
                output_path = "decrypted_received_file"
                with open("received_encrypted_file", 'rb') as file:
                    encrypted_data = file.read()
                decrypt_file_fernet(self.key, encrypted_data, output_path)
                messagebox.showinfo("Success", f"File decrypted and saved to {output_path}")
            except Exception as file_error:
                messagebox.showerror("Error", f"Decryption failed: {file_error}")

    def choose_file_to_encrypt(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path_label.config(text=file_path)

    def encrypt_and_send_file(self):
        file_path = self.file_path_label.cget("text")
        if not file_path:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите файл для шифрования.")
            return

        encrypted_data = encrypt_file_fernet(self.key, file_path)
        send_file_to_server(self.server_ip, self.server_port, encrypted_data)

    def choose_file_to_decrypt(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.decrypted_file_label.config(text=file_path)

    def decrypt_file(self):
        encrypted_file_path = self.decrypted_file_label.cget("text")
        if not encrypted_file_path:
            messagebox.showerror("Error", "Please select an encrypted file to decrypt.")
            return

        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                save_directory = settings.get("save_directory", os.getcwd())
        except FileNotFoundError:
            save_directory = os.getcwd()

        if not os.path.exists(save_directory):
            messagebox.showerror("Error", f"Save directory does not exist: {save_directory}")
            return

        unique_decrypted_filename = f"decrypted_file_{uuid.uuid4()}.txt"
        output_path = os.path.join(save_directory, unique_decrypted_filename)

        with open(encrypted_file_path, 'rb') as file:
            encrypted_data = file.read()

        try:
            decrypt_file_fernet(self.key, encrypted_data, output_path)
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    decrypted_content = f.read()
                    self.decrypted_message_entry.delete(1.0, tk.END)
                    self.decrypted_message_entry.insert(tk.END, decrypted_content)
            except UnicodeDecodeError:
                messagebox.showinfo("Success", f"File decrypted and saved to {output_path}")
        except Exception as e:
            messagebox.showerror("Decryption Error", str(e))

    def connect_to_friend(self):
        friend_ip = self.friend_ip_entry.get()
        if not friend_ip:
            messagebox.showerror("Error", "Please enter friend's IP.")
            return
        try:
            self.friend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.friend_socket.connect((friend_ip, self.server_port))
            messagebox.showinfo("Success", f"Connected to {friend_ip}")
            threading.Thread(target=self.receive_chat_messages, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")

    def receive_chat_messages(self):
        while True:
            try:
                data = self.friend_socket.recv(1024)
                if not data:
                    break
                decrypted_message = decrypt_message_fernet(self.key, data)
                self.chat_text.insert(tk.END, f"Friend: {decrypted_message}\n")
                self.chat_text.see(tk.END)
            except Exception as e:
                print(f"Ошибка получения сообщения: {e}")
                break

    def send_chat_message(self):
        message = self.chat_entry.get()
        if not message or not hasattr(self, 'friend_socket'):
            messagebox.showerror("Error", "Please connect to a friend and enter a message.")
            return
        encrypted_message = encrypt_message_fernet(self.key, message)
        self.friend_socket.sendall(encrypted_message)
        self.chat_text.insert(tk.END, f"You: {message}\n")
        self.chat_text.see(tk.END)
        self.chat_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = EncryptionApp(root)
    root.mainloop()