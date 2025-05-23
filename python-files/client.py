import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(('localhost', 3030))
while True:
    text = input("введи текст")
    s.sendall(text.encode('utf-8'))

data = s.recv(1024)
s.close()