import socket
import threading
import customtkinter as ctk

SERVER_IP = input("Enter server IP (e.g. 10.0.0.59): ")
PORT = int(input("Enter the port (e.g. 55555): "))

client = None
username = None
user_listbox = None

def setup_gui():
    root = ctk.CTk()
    root.title(f"Chat - {username}")
    root.attributes("-topmost", True)

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    # Message display area
    message_display = ctk.CTkTextbox(root, width=400, height=300, state='disabled', wrap="word", fg_color="#2e3b34", text_color="white")
    message_display.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

    # Users list area
    global user_listbox
    user_listbox = ctk.CTkTextbox(root, width=150, height=300, state='disabled', fg_color="#1e2b27", text_color="lightgreen")
    user_listbox.grid(row=0, column=1, padx=5, pady=10, sticky="n")

    # Message entry
    message_entry = ctk.CTkEntry(root, width=380, fg_color="#2e3b34", text_color="white", border_color="green")
    message_entry.grid(row=2, column=0, padx=10, pady=5)

    def send_message():
        try:
            message = message_entry.get()
            if message:
                full_message = f"{message}"
                client.sendall(full_message.encode('utf-8'))
                message_display.configure(state='normal')
                message_display.insert('end', f"You: {message}\n")
                message_display.configure(state='disabled')
                message_entry.delete(0, 'end')
        except Exception as e:
            print(f"Error sending message: {e}")

    send_button = ctk.CTkButton(root, text="Send", command=send_message, fg_color="green", hover_color="#3e8e41")
    send_button.grid(row=2, column=1, padx=5, pady=5)

    return root, message_display, message_entry

def update_user_list(usernames):
    global user_listbox
    user_listbox.configure(state='normal')
    user_listbox.delete("0.0", "end")
    for name in usernames:
        user_listbox.insert("end", f"- {name}\n")
    user_listbox.configure(state='disabled')

def receive_messages(client, message_display):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith("__users__:"):
                user_list = message.replace("__users__:", "").split(",")
                update_user_list(user_list)
            else:
                message_display.configure(state='normal')
                message_display.insert('end', f"{message}\n")
                message_display.configure(state='disabled')
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def main():
    global client, username
    username = input("Enter your name: ")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((SERVER_IP, PORT))
        print("[+] Connected to the server.")
    except Exception as e:
        print(f"Error connecting to the server: {e}")
        return

    try:
        client.sendall(username.encode('utf-8'))
    except Exception as e:
        print(f"Error sending username: {e}")
        return

    root, message_display, message_entry = setup_gui()
    threading.Thread(target=receive_messages, args=(client, message_display), daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()
