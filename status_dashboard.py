import os
import time
import psutil
from datetime import datetime

def get_status(process_name):
    """Return True if a process is running."""
    for proc in psutil.process_iter(attrs=['cmdline']):
        try:
            if any(process_name in " ".join(proc.info['cmdline']) for process_name in [process_name]):
                return True
        except Exception:
            continue
    return False

def read_launches_count():
    """Count launch detections from log."""
    try:
        with open("hunter_activity.log", "r") as f:
            data = f.read()
        return data.count("New Launch Detected")
    except FileNotFoundError:
        return 0

def dashboard():
    start_time = datetime.now()
    os.system("clear")
    print("🧠 ICEDEVILS EMPIRE — Live Terminal Dashboard 🧠")
    print("=" * 60)

    while True:
        os.system("clear")
        uptime = datetime.now() - start_time
        hunter = "✅ ACTIVE" if get_status("solana_hunter.py") else "❌ OFFLINE"
        telegram = "✅ ACTIVE" if get_status("telegram_bot.py") else "❌ OFFLINE"
        monitor = "✅ ACTIVE" if get_status("system_monitor.py") else "❌ OFFLINE"
        launches = read_launches_count()

        print("🧠 ICEDEVILS EMPIRE — Live Status Dashboard")
        print("=" * 60)
        print(f"🧩 Solana Hunter:       {hunter}")
        print(f"💬 Command Handler:     {telegram}")
        print(f"🛰 System Monitor:      {monitor}")
        print(f"🚀 Launches Detected:   {launches}")
        print(f"⏱️  Uptime:             {str(uptime).split('.')[0]}")
        print("=" * 60)
        print("🔄 Refreshing every 5 seconds — Press Ctrl+C to exit.")
        time.sleep(5)

if __name__ == "__main__":
    try:
        dashboard()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped manually.")
