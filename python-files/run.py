import socket
import threading

LISTEN_PORT = 5555
HTTP_PORT = 80
TCP_PORT = 21119
BUFFER_SIZE = 4096

def forward(source, destination):
    try:
        while True:
            data = source.recv(BUFFER_SIZE)
            if not data:
                break
            destination.sendall(data)
    except:
        pass
    finally:
        source.close()
        destination.close()

def handle_client(client_socket):
    try:
        initial_data = client_socket.recv(8)
        header = initial_data.decode(errors='ignore').upper()

        if header.startswith(('GET', 'POST', 'HEAD', 'HTTP', 'OPTIONS')):
            forward_port = HTTP_PORT
        else:
            forward_port = TCP_PORT

        forward_socket = socket.create_connection(('127.0.0.1', forward_port))
        forward_socket.sendall(initial_data)

        threading.Thread(target=forward, args=(client_socket, forward_socket)).start()
        threading.Thread(target=forward, args=(forward_socket, client_socket)).start()

    except Exception as e:
        print(f"Lỗi: {e}")
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', LISTEN_PORT))
    server.listen(100)
    print(f"Multiplexer đang lắng nghe trên cổng {LISTEN_PORT}...")

    while True:
        client_sock, _ = server.accept()
        threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == "__main__":
    start_server()
