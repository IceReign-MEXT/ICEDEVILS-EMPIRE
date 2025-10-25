import os
import requests
import subprocess

def speak(message: str):
    """Speak message aloud in Termux (ignore errors if Termux TTS not installed)."""
    try:
        subprocess.run(["termux-tts-speak", message])
    except Exception:
        pass

def telegram_notify(message: str):
    """Send Telegram alert if credentials available."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("OWNER_ID")
    if not token or not chat_id:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=payload, timeout=5)
    except Exception:
        pass
