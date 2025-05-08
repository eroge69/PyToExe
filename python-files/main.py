import os
import time
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

status_file_path = 'H:\\Warenannahme\\Software\\status.txt'

def create_image(color):
    image = Image.new('RGB', (64, 64), color)
    dc = ImageDraw.Draw(image)
    dc.ellipse((8, 8, 56, 56), fill=color)
    return image

green_icon = create_image('green')
red_icon = create_image('red')

def check_status(icon):
    try:
        with open(status_file_path, 'r') as file:
            status = file.read().strip()
            if 'Keine Werkstatt Bestellungen' in status:
                icon.icon = green_icon
                icon.title = 'Status: Keine Werkstatt Bestellungen'
            else:
                icon.icon = red_icon
                icon.title = 'Status: Werkstatt Bestellungen vorhanden'
    except Exception as e:
        icon.icon = red_icon
        icon.title = f'Fehler: {e}'

def setup(icon):
    icon.visible = True
    while True:
        check_status(icon)
        time.sleep(20)

icon = pystray.Icon('status_checker')
icon.menu = pystray.Menu(item('Beenden', lambda icon, item: icon.stop()))
icon.run(setup)
