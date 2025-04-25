
import socket
import psutil
from PIL import Image, ImageDraw, ImageFont
from pystray import Icon, Menu, MenuItem

def get_ip():
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                return addr.address
    return "IP Yok"

def create_icon_image():
    img = Image.new('RGB', (64, 64), color=(50, 150, 250))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    d.text((10, 25), "IP", fill=(255, 255, 255), font=font)
    return img

def refresh(icon):
    icon.title = f"IP: {get_ip()}"

menu = Menu(
    MenuItem('Yenile', refresh),
    MenuItem('Çık', lambda icon, item: icon.stop())
)

icon = Icon("ip_tray", create_icon_image(), f"IP: {get_ip()}", menu)
icon.run()
