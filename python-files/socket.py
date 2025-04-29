import socket
import time

print("---------------------")
print("1) scan host")
print("2) scan name_port")
print("3) scan number_port")
print("---------------------")
x = int(input( "( 1 - 2 -3 ) ? : "))
if x == 1:
    hostname = input("Enter the hostname : ")
    ip = socket.gethostbyname(hostname)
    print("---------------------")
    print( hostname + " ip = " + str(ip))
    q2 = input("want 2 exit ( y - n )")
    if q2 == "y":
        exit()
    elif q2 == "n":
        while True:
            time.sleep(1)

if x == 2:
    port_name = input("Enter the port name : ")
    port = socket.getservbyname(port_name)
    print("----------------------")
    print( port_name + " port number : " + str(port))
    q1 = input("want 2 exit ( y - n )")
    if q1 == "y":
        exit()
    elif q1 == "n":
        while True:
            time.sleep(1)
    exit() 
if x == 3:
    port_number = int(input("Enter the port number : "))
    service = socket.getservbyport(port_number)
    print("-----------------------")
    print( str(port_number) + " port name : " + service)
    q3 = input("want 2 exit ( y - n )")
    if q3 == "y":
        exit()
    elif q3 == "n":
        while True:
            time.sleep(1)
else:
    print("(:")
