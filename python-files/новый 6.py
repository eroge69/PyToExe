import netmiko
 
from netmiko import ConnectHandler
 
iosv_l2 = {
 
'device_type': 'eltex',
 
'ip': '172.21.99.182',
 
'username': 'divanets',
 
'password': 'Idcerog1978',
 
'secret': 'Idcerog1978',
 
}
 
net_connect =ConnectHandler(**iosv_l2)
 
net_connect.enable()
 
config_commands = ['interface gigabitethernet 0/29','shutdown','no shutdown','exit']
 
output = net_connect.send_config_set(config_commands)
 
print (output)
 
config_commands = ['exit']
 