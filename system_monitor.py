import os
import time
import subprocess
from notifier import telegram_notify, speak

def is_hunter_running():
    """Check if solana_hunter.py process is active."""
    try:
        output = subprocess.check_output("ps -A | grep solana_hunter.py", shell=True).decode()
        return "solana_hunter.py" in output
    except subprocess.CalledProcessError:
        return False

def restart_hunter():
    """Restart the bot via deploy.sh."""
    telegram_notify("🛠 ICEDEVILS EMPIRE: Hunter was offline — restarting now.")
    speak("Hunter was offline. Restarting.")
    subprocess.run(["bash", "deploy.sh"])

def monitor_loop():
    telegram_notify("🟢 ICEDEVILS EMPIRE system monitor started.")
    speak("System monitor is active.")

    while True:
        if not is_hunter_running():
            restart_hunter()
        time.sleep(60)  # check every 60 seconds

if __name__ == "__main__":
    monitor_loop()
