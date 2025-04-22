from pypresence import Presence
import time
import psutil
import pynvml
 
time.sleep(1)
 
pynvml.nvmlInit()
 
client_id = 1364250594835169424
#Пример client_id = 1107349645656588412
RPC: Presence = Presence(client_id)
ButtonsList = [
    {
        "label": "V potoke",
        "url": "https://i.postimg.cc/43ghMKFT/image.jpg"
    },
    {
        "label": "",
        "url": ""
    }
]
 
RPC.connect()
 
device_count = pynvml.nvmlDeviceGetCount()
if device_count == 0:
    print("Video not found")
    has_video_card = False
else:
    has_video_card = True
 
while True:
    time.sleep(1)
    ram_percent=psutil.virtual_memory().percent
    cpu_percent=psutil.cpu_percent()
 
    if has_video_card:
        device_count = pynvml.nvmlDeviceGetCount()
        gpu_utilization = ''
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            gpu_utilization += f"{pynvml.nvmlDeviceGetUtilizationRates(handle).gpu / 1:.1f}% "
    else:
        gpu_utilization = ''
 # здесь отоброжение в приложение
    RPC.update(details=f"CPU: {cpu_percent}% GPU: {gpu_utilization} RAM: {ram_percent}%",
            large_image='https://media.tenor.com/gg.gif',
            large_text='3.14',
            buttons=ButtonsList,
            small_image='https://cdn3.emoji.gg/gg.png',
    )
 
pynvml.nvmlShutdown()