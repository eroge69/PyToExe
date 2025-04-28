#!/usr/bin/env python3

import socket
import subprocess
import sys
from plyer import notification
from plyer import platforms

ip = ""
port = ""

try:
    f = open("net.cfg", "r")
    ip, port = f.read().split(":")
    f.close() 
    socket.inet_aton(ip)
    port = int(port)
except ValueError:
    port = 10052
except:
    sys.exit()
    
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, int(port)))

try:
    while True:
        data, addr = sock.recvfrom(10240)
        data = data.decode("utf-8")
        t, m = data.split("@@@")
        subprocess.call([r"C:\ScriptToZabbix.exe"]
except (KeyboardInterrupt, SystemExit):
    sys.exit()


        
        
        

        
      
