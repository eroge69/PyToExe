import pyautogui
import time
import keyboard
import threading
import requests
import random
from datetime import datetime, timedelta

# === CONFIG ===
interval = 11  # Tijd tussen klikken
init_delay = 5  # Tijd om muis te plaatsen
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1362073111851307048/wonRndwptwb8jTY-jiIaMPZw-0jteLePMBbl2f85fuvKIkUZcDV_zgiV5aADrFYjNjX7"

clicking_enabled = False
click_position = None
total_money = 0
start_money = 0
session_earned = 0
last_milestone = 0
money_emojis = ["💶", "💸", "🤑", "💰", "💵"]

# === FUNCTIES ===

def send_status_log(title, description, color=3447003):
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "footer": {"text": "FiveM Autoclicker Logger"},
        "timestamp": datetime.now().astimezone().isoformat()
    }
    payload = {"embeds": [embed]}

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"❌ Webhook fout: {e}")

def send_embed_to_discord(amount, total, position, timestamp, time_to_mil, predicted_hour, progress_bar, percentage, milestone=False):
    emoji = random.choice(money_emojis)
    embed = {
        "title": f"{emoji} Automatische Klik",
        "description": f"**+€{amount}** toegevoegd\nTotale balans: **€{total}**\n📈 **Verdiend deze sessie:** €{session_earned}",
        "color": 3066993 if not milestone else 15105570,
        "fields": [
            {"name": "📍 Positie", "value": f"{position}", "inline": True},
            {"name": "⏰ Tijd", "value": f"{timestamp}", "inline": True},
            {"name": "🕒 Naar 1M", "value": f"{time_to_mil}", "inline": False},
            {"name": "⏳ Over 1 uur", "value": f"€{predicted_hour}", "inline": False},
            {"name": f"📊 Voortgang naar €1M ({percentage}%)", "value": f"`{progress_bar}`", "inline": False}
        ],
        "footer": {
            "text": "FiveM Autoclicker Logger"
        },
        "timestamp": datetime.now().astimezone().isoformat()
    }

    payload = {
        "embeds": [embed]
    }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"❌ Fout bij verzenden naar Discord: {e}")

def generate_progress_bar(current, goal, length=20):
    percentage = min(current / goal, 1.0)
    filled = int(length * percentage)
    bar = "🟩" * filled + "⬜" * (length - filled)
    return bar, round(percentage * 100, 1)

def play_sound():
    try:
        import winsound
        winsound.MessageBeep()
    except:
        print("🔕 Geluid niet ondersteund op dit systeem.")

def click_loop():
    global clicking_enabled, total_money, last_milestone, session_earned
    while True:
        if clicking_enabled and click_position:
            # Dit voorkomt dat de muis fysiek beweegt, en simuleert de klik op de opgegeven positie op scherm 1.
            pyautogui.click(x=click_position[0], y=click_position[1])  
            total_money += click_value
            session_earned += click_value
            timestamp = datetime.now().strftime("%H:%M:%S")

            clicks_per_hour = 3600 / interval
            predicted_hour = start_money + (clicks_per_hour * click_value)

            if total_money >= 1_000_000:
                time_to_mil = "🎯 Bereikt!"
            else:
                remaining = 1_000_000 - total_money
                seconds_needed = remaining / click_value * interval
                eta = timedelta(seconds=int(seconds_needed))
                time_to_mil = str(eta)

            progress_bar, percent = generate_progress_bar(total_money, 1_000_000)

            milestone_now = (total_money // 100000) * 100000
            is_milestone = False
            if milestone_now > last_milestone:
                last_milestone = milestone_now
                is_milestone = True
                print(f"🥳 Milestone bereikt: €{milestone_now}!")
                play_sound()

            print(f"[{timestamp}] +€{click_value} | Totaal: €{total_money} | Sessiewinst: €{session_earned} | {percent}% naar €1M")
            send_embed_to_discord(
                click_value,
                total_money,
                click_position,
                timestamp,
                time_to_mil,
                int(predicted_hour),
                progress_bar,
                percent,
                milestone=is_milestone
            )

        time.sleep(interval)

def toggle_clicking():
    global clicking_enabled
    clicking_enabled = not clicking_enabled
    if clicking_enabled:
        print("▶️ Klikken gestart.")
        send_status_log("🟢 Klikken gestart", "De automatische klikker is actief.")
    else:
        print("⏸️ Klikken gepauzeerd.")
        send_status_log("⏸️ Klikken gepauzeerd", "De automatische klikker is gepauzeerd.")

# === SCRIPT START ===
try:
    # Vraag nu naar het bedrag per klik en hoeveel geld je al hebt
    click_value = int(input("💰 Hoeveel wil je betaald krijgen per klik? €"))
    start_money = int(input("💼 Hoeveel geld heb je al? €"))
    total_money = start_money
except ValueError:
    print("❗ Ongeldig bedrag. Script stopt.")
    exit()

print(f"📍 Plaats je muis op de knop binnen {init_delay} seconden...")
time.sleep(init_delay)

click_position = pyautogui.position()
print(f"✅ Muispositie opgeslagen: {click_position}")
print("🎮 Ctrl + B = Start/Stop klikken | Ctrl + C = Stop script")

send_status_log("🟢 Script gestart", f"De autoclicker is gestart en klaar voor gebruik.\nJe ontvangt €{click_value} per klik en hebt al €{start_money}.")

click_thread = threading.Thread(target=click_loop, daemon=True)
click_thread.start()

keyboard.add_hotkey('ctrl+b', toggle_clicking)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("👋 Script gestopt.")
    send_status_log("🔴 Script gestopt", f"Totaal sessiewinst: **€{session_earned}**\nEindbalans: **€{total_money}**", color=15158332)
