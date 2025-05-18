import webbrowser
import time
from pypresence import Presence
import os

# === CONFIG ===
client_id = "1371253971846565919"  # Your Discord App ID
gta_vi_url = "https://www.rockstargames.com/VI"
trailer_url = "https://www.youtube.com/watch?v=V0RLujxTm3c"

# === Open GTA VI Site ===
webbrowser.open(gta_vi_url)

# === Start Discord RPC ===
RPC = Presence(client_id)
RPC.connect()

RPC.update(
    details="Exploring Leonida Keys",
    large_image="gta-6",
    large_text="Grand Theft Auto VI",
    buttons=[
        {"label": "Learn More", "url": gta_vi_url},
        {"label": "Watch Trailer 2", "url": trailer_url}
    ]
)

print("RPC is now live...")

try:
    while True:
        time.sleep(15)  # Keeps the RPC running
except KeyboardInterrupt:
    RPC.close()
    print("RPC stopped.")
