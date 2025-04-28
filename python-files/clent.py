import socket
import pyautogui
import os

# Function to take a screenshot and save it to a file
def take_screenshot(filename="screenshot.png"):
    screenshot = pyautogui.screenshot()  # Take the screenshot
    screenshot.save(filename)  # Save the screenshot to the specified file
    print(f"Screenshot saved as {filename}")

# Function to handle incoming connections
def start_server(host="0.0.0.0", port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create the socket
    server_socket.bind((host, port))  # Bind to the specified host and port
    server_socket.listen(5)  # Listen for incoming connections

    print(f"Listening on {host}:{port}...")

    while True:
        client_socket, client_address = server_socket.accept()  # Accept an incoming connection
        print(f"Connection from {client_address}")
        
        try:
            # Receive the command from the client (could be any message)
            message = client_socket.recv(1024).decode('utf-8')
            if message == "screenshot":
                # If message is "screenshot", take a screenshot
                take_screenshot("screenshot.png")
                client_socket.send("Screenshot taken!".encode('utf-8'))  # Send acknowledgment to the client
            else:
                client_socket.send("Invalid command!".encode('utf-8'))
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()  # Close the connection

if __name__ == "__main__":
    start_server()

