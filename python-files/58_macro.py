import requests

headers = {
    'Host': '192.168.1.58:50443',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Sec-Fetch-Site': 'same-origin',
    'Origin': 'https://192.168.1.58:50443',
    'Sec-Fetch-Mode': 'navigate',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Mobile/15E148 Safari/604.1',
    'Referer': 'https://192.168.1.58:50443/panel/remote_panel.cgi',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'en-US,en;q=0.9',
    'Priority': 'u=0, i',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
    'LCD.x': '790',
    'LCD.y': '451',
}
import time
while True:
    response = requests.post('https://192.168.1.58:50443/panel/remote_panel.cgi', headers=headers, data=data, verify=False)
    print(response.text)
    time.sleep(1)