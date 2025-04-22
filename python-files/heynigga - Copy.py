import time
import keyboard
import pyautogui
import requests
from PIL import ImageGrab
import pytesseract
import re
from collections import defaultdict
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
WEBHOOK_URL = "https://discord.com/api/webhooks/1363983001918242816/a9pkkm9ly1w45scp0iGQpjNNyGom1Yq5tnEhGlDmUW0eEBZeA0pga2qIDbeSRcYDfd5O"
SCAN_REGION = (0, 0, 1300, 500)

print("Use Cursed Flag? True or False")
CFLAG = input()

print("Low Performance Mode? True or False")
LPM = input()

item_counts = defaultdict(int)
webhook_message_id = None

def send_or_update_embed():
    if LPM is False:
        global webhook_message_id

        # Format description
        description = "```\n"
        for item, count in sorted(item_counts.items()):
            description += f"{item} x{count}\n"
        description += "```"

        # Save to text file
        try:
            with open("collected_items.txt", "w", encoding="utf-8") as f:
                for item, count in sorted(item_counts.items()):
                    f.write(f"{item} x{count}\n")
        except Exception as e:
            print(f"Failed to write to file: {e}")

        # Create embed
        embed = DiscordEmbed(
            title="🎁 [ Items Collected! ] 🎁",
            description=description,
            color=0x00ff00
        )
        embed.set_footer(text=f"Last updated: {datetime.now().strftime('%m/%d/%Y %I:%M %p')}")

        if webhook_message_id is None:
            webhook = DiscordWebhook(url=WEBHOOK_URL)
            webhook.add_embed(embed)
            response = webhook.execute()

            try:
                webhook_message_id = response.json()[0]['id']
                print(f"Webhook created with message ID: {webhook_message_id}")
            except Exception as e:
                print("Failed to get webhook message ID:", e)
        else:
            webhook = DiscordWebhook(
                url=WEBHOOK_URL,
                id=webhook_message_id,
                use_async=False
            )
            webhook.embeds = []  # Replace old embeds
            webhook.add_embed(embed)
            response = webhook.edit()
            if response.status_code != 200:
                print("Failed to edit message. Status:", response.status_code)
    else:
        return


def scan_for_bracketed_words():
    if LPM is False:
        try:
            screenshot = ImageGrab.grab(bbox=SCAN_REGION)
            text = pytesseract.image_to_string(screenshot)
            matches = re.findall(r'\[(.*?)\]', text)

            if matches:
                for word in matches:
                    item_name = word.strip()
                    if item_name and item_name != "X1":
                        if item_name != "><1":
                            if item_name != "x1":
                                if item_name != "<1":
                                    if item_name != ">1":
                                        item_counts[item_name] += 1
                                        print(f"Found item: {item_name} (Total: {item_counts[item_name]})")
                                        send_or_update_embed()

        except Exception as e:
            print(f"Error scanning screen: {e}")
    else:
        return


def main_loop(arlong_spawn_time=11750):
    try:
        while True:
            if CFLAG:
                keyboard.press('x')
                keyboard.release('x')
                time.sleep(2)
            else:
                pyautogui.click()
                time.sleep(1)
                
            for _ in range(3):
                keyboard.press('e')
                keyboard.release('e')
                scan_for_bracketed_words()
                time.sleep(0.7)
            
            keyboard.press('m')
            keyboard.release('m')
            time.sleep(arlong_spawn_time / 1000)
            # scan_for_bracketed_words()
            keyboard.press('m')
            keyboard.release('m')

            if keyboard.is_pressed('F5'):
                print("Exiting...")
                break
                
    except KeyboardInterrupt:
        print("Script stopped by user")

if __name__ == "__main__":
    print("Starting script... Press X to begin (if not auto-started), F5 to exit.")
    print("Make sure the game window is active!")
    time.sleep(5)
    main_loop()