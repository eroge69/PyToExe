from pypresence import Presence
import time

# Discord Application ID
client_id = '809790036307738637'  # Replace this with your actual App ID
RPC = Presence(client_id)
RPC.connect()

# --- User inputs ---
activity_type = input("Activity type (playing, listening, watching, competing): ").capitalize()
details_text = input("Details (what are you doing?): ")
state_text = input("State message (e.g., current status): ")
party_current = int(input("Party size (current): "))
party_max = int(input("Party size (max): "))
duration = int(input("Duration to show presence (in seconds): "))

# --- Configure Rich Presence ---
start_time = int(time.time())
RPC.update(
    details=details_text,
    state=f"{state_text} ({party_current}/{party_max})",
    start=start_time,
    large_image="https://i.pinimg.com/originals/6d/46/f9/6d46f977733e6f9a9fa8f356e2b3e0fa.gif",           # This must match an uploaded asset in your Developer Portal
    large_text="Nyoom",      # Text shown when hovering over the image
    buttons=[
        {"label": "Click me!", "url": "https://nimble.li/p9qrgwvd"},
        {"label": "More Info", "url": "https://your-info-link.com"}
    ]
)

print(f"{activity_type} Rich Presence is now active.")

# --- Keep Presence Active ---
time.sleep(duration)

# --- Clear Presence ---
RPC.clear()
print("Presence cleared.")
