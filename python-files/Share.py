import socket
import threading
import os  # Add import for clearing the console

# Server setup
def start_server():
    server_name = input("Enter the server's name: ")  # Ask for the server's name
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 72))  # Bind to all available interfaces on port 72
    server.listen(5)
    print("Server started. Waiting for connections...")

    # UDP broadcasting for server discovery
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", 72))

    def udp_broadcast():
        while True:
            data, addr = udp_socket.recvfrom(1024)
            if data.decode("utf-8") == "DISCOVER_SERVER":
                udp_socket.sendto(b"SERVER_HERE", addr)

    threading.Thread(target=udp_broadcast, daemon=True).start()

    clients = []

    def broadcast(message, sender_socket=None):
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    clients.remove(client)

    def handle_client(client_socket):
        try:
            # Ask for the client's name
            client_socket.send(b"Enter your name: ")
            client_name = client_socket.recv(1024).decode("utf-8").strip()
            print(f"{client_name} has joined the chat.")
            broadcast(f"{client_name} has joined the chat.".encode("utf-8"))

            while True:
                message = client_socket.recv(1024)
                if not message:
                    break
                print(f"{client_name}: {message.decode('utf-8')}")
                broadcast(f"{client_name}: {message.decode('utf-8')}".encode("utf-8"), client_socket)
        except:
            print(f"{client_name} has disconnected.")
            broadcast(f"{client_name} has left the chat.".encode("utf-8"))
            clients.remove(client_socket)

    def server_send_messages():
        print("You can start typing messages to broadcast to all clients.")
        while True:
            message = input()
            if message.lower() == "exit":
                print("Stopping server message broadcast.")
                break
            broadcast(f"{server_name}: {message}".encode("utf-8"))  # Include server name in messages

    threading.Thread(target=server_send_messages, daemon=True).start()

    while True:
        client_socket, addr = server.accept()
        print(f"New connection from {addr}")
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket,)).start()

# Client setup
def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Automatically discover the server
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.settimeout(5)
    udp_socket.sendto(b"DISCOVER_SERVER", ("<broadcast>", 72))
    print("Searching for server...")

    try:
        data, server_address = udp_socket.recvfrom(1024)
        if data.decode("utf-8") == "SERVER_HERE":
            server_ip = server_address[0]
            print(f"Server found at {server_ip}")
        else:
            print("Invalid response from server.")
            return
    except socket.timeout:
        print("Server not found. Defaulting to public server at 72.196.16.21.")
        server_ip = "72.196.16.21"  # Default to public server IP
    finally:
        udp_socket.close()

    client.connect((server_ip, 72))

    # Ask for the user's name
    name = input("Enter your name: ")
    client.send(name.encode("utf-8"))

    def receive_messages():
        while True:
            try:
                message = client.recv(1024).decode("utf-8")
                print(message)
            except:
                print("Disconnected from server.")
                break

    threading.Thread(target=receive_messages, daemon=True).start()

    print("Connected to the server. You can start typing messages.")
    while True:
        message = input()
        if message.lower() == "exit":
            break
        client.send(message.encode("utf-8"))

    client.close()

# Main function
if __name__ == "__main__":
    name = input("Enter your name: ")  # Ask for the user's name

    # Clear the console after entering the name
    os.system('cls' if os.name == 'nt' else 'clear')

    if name == "Emmet":
        print("You are the server.")
        start_server()
    else:
        print("You are a client. Connecting to the server at 72.196.16.21...")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(("72.196.16.21", 72))  # Connect to the default server
            client.send(name.encode("utf-8"))  # Send the user's name to the server

            def receive_messages():
                while True:
                    try:
                        message = client.recv(1024).decode("utf-8")
                        print(message)
                    except:
                        print("Disconnected from server.")
                        break
            threading.Thread(target=receive_messages, daemon=True).start()

            print("Connected to the server. You can start typing messages.")
            while True:
                message = input()
                if message.lower() == "exit":
                    break
                client.send(message.encode("utf-8"))

            client.close()
        except Exception as e:
            print(f"Failed to connect to the server: {e}")