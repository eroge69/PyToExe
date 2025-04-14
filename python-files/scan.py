import scapy.all as scapy
import time
import json
import os
import requests
import socket
from plyer import notification
import winsound
import ctypes
# Укажите свой токен и chat_id
TOKEN = "7647390256:AAF-sRTKZRbhzGwfMnTxBsXKu2MljYri3sc"  # Замените на токен вашего бота
CHAT_ID = "6477581311"  # Замените на свой chat_id



def send_telegram_message(message):
    url = "https://api.telegram.org/bot7647390256:AAF-sRTKZRbhzGwfMnTxBsXKu2MljYri3sc/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=params)
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print("Failed to send message. Status code: {response.status_code}, Response: {response.text}")

def get_mac_vendor(mac):
    url = f"https://api.macvendors.com/{mac}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        pass
    return "Unknown Vendor"

def get_netbios_name(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        return "Unknown Name"

def scan_ports(ip):
    common_ports = [22, 80, 443, 3389]  # SSH, HTTP, HTTPS, RDP
    open_ports = []
    for port in common_ports:
        syn_packet = scapy.IP(dst=ip) / scapy.TCP(dport=port, flags="S")
        response = scapy.sr1(syn_packet, timeout=1, verbose=False)
        if response and response.haslayer(scapy.TCP) and response[scapy.TCP].flags == 18:
            open_ports.append(port)
    return open_ports

def ip_range(start_ip, end_ip):
    start_parts = list(map(int, start_ip.split('.')))
    end_parts = list(map(int, end_ip.split('.')))
    ip_list = []

    for i in range(start_parts[3], end_parts[3] + 1):
        ip_list.append(f"{start_parts[0]}.{start_parts[1]}.{start_parts[2]}.{i}")
    
    return ip_list

def scan_network(start_ip, end_ip):
    ip_list = ip_range(start_ip, end_ip)
    devices = {}
    
    for ip in ip_list:
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
        
        for answer in answered_list:
            ip = answer[1].psrc
            mac = answer[1].hwsrc
            vendor = get_mac_vendor(mac)
            netbios_name = get_netbios_name(ip)
            open_ports = scan_ports(ip)
            devices[ip] = {
                "MAC": mac,
                "Vendor": vendor,
                "NetBIOS Name": netbios_name,
                "Open Ports": open_ports
            }
    
    return devices

def save_known_devices(devices, filename="known_devices.json"):
    try:
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(filename, "w") as file:
            json.dump(devices, file, indent=4)
        print(f"Devices successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving devices: {e}")

def load_known_devices(filename="known_devices.json"):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading devices: {e}")
    return {}

def play_sound():
    frequency = 1000  # Sound frequency in Hz
    duration = 1000   # Duration in milliseconds
    winsound.Beep(frequency, duration)

def notify_new_device(ip, mac, vendor, netbios_name, open_ports):
    ports_info = "Open ports: {', '.join(map(str, open_ports))}" if open_ports else "No open ports detected"
    notification_message = f"New device detected:\nIP: {ip}\nMAC: {mac}\nVendor: {vendor}\nNetBIOS: {netbios_name}\n{ports_info}"
    send_telegram_message(notification_message)

    notification.notify(
        title="New device detected!",
        message=notification_message,
        app_name="Network Monitor"
    )
    play_sound()

def monitor_network(start_ip, end_ip, scan_interval):
    known_devices = load_known_devices()
    print("Network monitoring started...")
    
    try:
        while True:
            current_devices = scan_network(start_ip, end_ip)
            last_digits = "".join(ip[-1] for ip in current_devices.keys())
            
       

            # Преобразуем строку в список чисел
            color_string = last_digits.replace("0", "")
            digits = [int(digit) for digit in color_string]
            
            # Создаем таблицу для всех возможных комбинаций цифр и цветов
            color_mapping = {
                (1,): ("0", "E"),  # фон: черный, текст: желтый
                (2,): ("0", "B"),  # фон: черный, текст: голубой
                (3,): ("4", "7"),  # фон: красный, текст: белый
                (4,): ("0", "7"),  # фон: черный, текст: белый
                (5,): ("A", "7"),  # фон: салатовый, текст: белый
                (1, 2): ("0", "D"),  # фон: черный, текст: фиолетовый
                (1, 3): ("4", "E"),  # фон: красный, текст: желтый
                (1, 4): ("0", "E"),  # фон: черный, текст: желтый
                (1, 5): ("A", "E"),  # фон: салатовый, текст: желтый
                (2, 3): ("4", "B"),  # фон: красный, текст: голубой
                (2, 4): ("B", "E"),  # фон: черный, текст: голубой
                (2, 5): ("A", "B"),  # фон: салатовый, текст: голубой
                (3, 5): ("4", "7"),  # фон: бордовый, текст: белый
                (1, 3, 5): ("4", "E"),  # фон: бордовый, текст: желтый
                (2, 3, 5): ("4", "B"),  # фон: бордовый, текст: голубой
                (1, 2, 3): ("4", "D"),  # фон: красный, текст: фиолетовый
                (1, 2, 4): ("0", "D"),  # фон: черный, текст: фиолетовый
                (1, 2, 5): ("A", "D"),  # фон: салатовый, текст: фиолетовый
                (1, 2, 3, 5): ("4", "D"),  # фон: бордовый, текст: фиолетовый
            }

            # Функция для получения цвета фона и текста
            def get_color(digits):
                # Преобразуем digits в кортеж, чтобы искать в таблице
                digits_tuple = tuple(sorted(digits))
                
                # Ищем в таблице, если есть такая комбинация цифр
                if digits_tuple in color_mapping:
                    return color_mapping[digits_tuple]
                else:
                    # Если не нашли комбинацию, то по умолчанию - стандартный цвет
                    return ("0", "7")  # фон черный, текст белый

            # Получаем цвет фона и текста для введенной строки
            background_code, text_code = get_color(digits)

            # Меняем цвет фона и текста в консоли
            os.system(f"color {background_code}{text_code}")

            # Печатаем сообщение
            print(f"{last_digits} ->{background_code}{text_code}")

            if not current_devices:
                print("No devices found in the range.")
                
            for ip, details in current_devices.items():
              
                if ip not in known_devices:
                    print(f"New device detected: {ip} ({details['MAC']}), Vendor: {details['Vendor']}, "
                          f"NetBIOS: {details['NetBIOS Name']}, Open Ports: {details['Open Ports']}")

                    notify_new_device(ip, details['MAC'], details['Vendor'], details['NetBIOS Name'], details['Open Ports'])

                    known_devices[ip] = details
        
            time.sleep(scan_interval)

    except KeyboardInterrupt:
        print("Network monitoring stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    start_ip = "192.168.5.100"
    end_ip = "192.168.5.115"
    scan_interval = 1  # интервал сканирования в секундах
    monitor_network(start_ip, end_ip, scan_interval)

if __name__ == "__main__":
    main()
