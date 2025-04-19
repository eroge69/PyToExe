import requests

import time
import requests

# --- CONFIG ---

TELEGRAM_BOT_TOKEN = 'your_bot_token_here'
TELEGRAM_CHANNEL_ID = '@yourchannelname'
POST_INTERVAL = 60 * 60  # post every hour
SUBSCRIBERS = {
    "0xwallet1...": "pro",
    "0xwallet2...": "lifetime",
    # Add more wallet addresses with tiers
}

# --- FUNCTIONALITY ---

def check_subscription(wallet_address):
    return SUBSCRIBERS.get(wallet_address, None)

def format_forecast_message(ticker, entry, target, risk_level):
    return f"""⚡ TRADE IDEA ⚡

Ticker: {ticker.upper()}
Entry Zone: {entry}
Target: {target}
Risk Level: {risk_level}/10

Forecast generated exclusively for subscribers.
"""

def post_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    print("Posted to Telegram:", response.status_code)

# --- MAIN LOOP ---

def main():
    print("Starting forecast poster...")
    while True:
        # Simulate generating a new forecast
        forecast = format_forecast_message("TSLA", "$160-162", "$178", 6)
        post_to_telegram(forecast)
        time.sleep(POST_INTERVAL)

if __name__ == "__main__":
    main()
# --hidden-import=requests
