import threading
import sys
import os
from dotenv import load_dotenv
import time
import asyncio
# --- This script assumes you have these files. ---
# If any are missing, it will report it and continue.

# We will try to import all the weapons in your arsenal
try:
    from solana_hunter import hunt_for_launches
    HAVE_HUNTER = True
except ImportError:
    HAVE_HUNTER = False

try:
    from telegram_bot import start_command_handler
    HAVE_HANDLER = True
except ImportError:
    HAVE_HANDLER = False

try:
    from system_monitor import start_monitoring
    HAVE_MONITOR = True
except ImportError:
    HAVE_MONITOR = False

# This is a temporary logger until we build your new log_utils.py
def log_event(message: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] - {message}")

# Load the secrets that power everything
load_dotenv()

def run_background_task(target, name):
    """A helper to run each weapon in its own thread."""
    thread = threading.Thread(target=target, name=name)
    thread.daemon = True
    thread.start()
    log_event(f"✅ System Online: '{name}' thread has been launched.")

if __name__ == "__main__":
    log_event("--- 🛡️ INITIALIZING THE ICEDEVILS EMPIRE 🛡️ ---")

    # --- LAUNCH SEQUENCE ---
    # The brain checks if each weapon exists before trying to launch it.

    if HAVE_HUNTER:
        # We need to run asyncio tasks in the main thread or a dedicated one
        # For now, let's keep it simple and launch it in the background.
        # Note: This might cause issues if other bots also use asyncio.
        run_background_task(lambda: asyncio.run(hunt_for_launches()), "SolanaHunter")
    else:
        log_event("⚠️  Warning: `solana_hunter.py` not found. Hunter is offline.")

    if HAVE_HANDLER:
        run_background_task(start_command_handler, "TelegramBot")
    else:
        log_event("⚠️  Warning: `telegram_bot.py` not found. Command Handler is offline.")
 
    if HAVE_MONITOR:
        run_background_task(start_monitoring, "SystemMonitor")
    else:
        log_event("⚠️  Warning: `system_monitor.py` not found. System Monitor is offline.")

    # A check to import asyncio if needed by the hunter
    if HAVE_HUNTER:
        import asyncio

    log_event("\n✅✅✅ ALL SYSTEMS ARE GO. THE EMPIRE IS LIVE. ✅✅✅")
    log_event("--- The machine will now run forever. Press Ctrl+C to stop. ---")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_event("\n...Shutting down all systems...")
        sys.exit(0)
