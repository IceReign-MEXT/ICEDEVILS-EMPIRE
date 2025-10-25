import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

LOG_FILE = "hunter_activity.log"
PRIVATE_CHANNEL_ID = os.getenv("TELEGRAM_PRIVATE_CHANNEL_ID")
PUBLIC_CHANNEL_IDS = os.getenv("TELEGRAM_PUBLIC_CHANNEL_IDS", "").split(',')
BOT_TOKEN = os.getenv("TELEGRAM_BUSINESS_BOT_TOKEN")

def log_event(message: str):
    log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}"
    print(log_message)
    with open(LOG_FILE, 'a') as f: f.write(log_message + '\n')

def send_alert(message: str, is_public: bool = False):
    if not BOT_TOKEN: return

    target_ids = PUBLIC_CHANNEL_IDS if is_public else [PRIVATE_CHANNEL_ID]

    for chat_id in target_ids:
        if not chat_id: continue
        api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {'chat_id': chat_id.strip(), 'text': message, 'parse_mode': 'Markdown'}
        try:
            requests.post(api_url, json=payload, timeout=10)
        except Exception as e:
            log_event(f"[ALERTER] FAILED to send to {chat_id}: {e}")

