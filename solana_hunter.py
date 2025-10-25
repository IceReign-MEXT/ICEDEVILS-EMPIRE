import os
import json
import asyncio
import websockets
from dotenv import load_dotenv
from business_tools import log_event, send_alert
from notifier import telegram_notify, speak

load_dotenv()

with open('config.json', 'r') as f:
    config = json.load(f)

SOLANA_WSS_URL = "wss://api.mainnet-beta.solana.com"
RAYDIUM_LP_V4 = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
HIGH_LIQUIDITY_THRESHOLD_SOL = config.get("alien_brain_threshold_sol", 25)
BUSINESS_BOT_USERNAME = config.get("business_bot_username")
BUSINESS_NAME = config.get("business_name", "ICEDEVILS-EMPIRE")


async def hunt_for_launches():
    log_event("[SOLANA HUNTER] Hunter is online. Watching the jungle...")
    telegram_notify("🟢 Solana Hunter is online and watching the jungle...")
    speak("Hunter is online and watching the jungle")

    while True:
        try:
            async with websockets.connect(SOLANA_WSS_URL, ping_interval=20, ping_timeout=20) as websocket:
                sub_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "logsSubscribe",
                    "params": [
                        {"mentions": [RAYDIUM_LP_V4]},
                        {"commitment": "confirmed"}
                    ]
                }

                await websocket.send(json.dumps(sub_request))
                await websocket.recv()

                log_event("[SOLANA HUNTER] Subscription successful. Hunting for high-quality launches...")
                telegram_notify("🎯 Subscription successful — hunting for high-quality launches.")
                speak("Subscription successful")

                async for message in websocket:
                    data = json.loads(message)
                    if "params" in data and "result" in data["params"]:
                        logs = data["params"]["result"]["value"]["logs"]
                        signature = data["params"]["result"]["value"]["signature"]

                        if any("initialize2" in log for log in logs):
                            log_event(f"[SOLANA HUNTER] New Launch Detected! Signature: {signature}")
                            telegram_notify(f"🚀 New launch detected on Solana! Signature: {signature}")
                            speak("New token launch detected")

                            starting_liquidity_sol = 1.5  # Placeholder
                            token_name = "NewToken"        # Placeholder

                            private_message = (
                                f"🚀 **New Launch Signal!** 🚀\n\n"
                                f"**Token:** `{token_name}`\n"
                                f"**Liquidity:** ~{starting_liquidity_sol:.2f} SOL\n\n"
                                f"[View on Solscan](https://solscan.io/tx/{signature})"
                            )
                            send_alert(private_message, is_public=False)

                            if starting_liquidity_sol > HIGH_LIQUIDITY_THRESHOLD_SOL:
                                log_event(f"[ALIEN BRAIN] High-value target found! Initiating public marketing...")
                                telegram_notify("🧠 High-value target found — initiating marketing.")
                                speak("High-value target detected")

                                public_message = (
                                    f"🚀 **High-Signal Launch Detected by {BUSINESS_NAME} AI** 🚀\n\n"
                                    f"A new token launch shows high liquidity!\n\n"
                                    f"[View on Solscan](https://solscan.io/tx/{signature})"
                                )
                                send_alert(public_message, is_public=True)

        except Exception as e:
            log_event(f"[SOLANA HUNTER] Error: {e}. Reconnecting in 15 seconds...")
            telegram_notify(f"⚠️ Solana Hunter error: {e}")
            speak("Hunter encountered an error")
            await asyncio.sleep(15)


if __name__ == "__main__":
    start_msg = "--- 🚀 SOLANA HUNTER WEAPON IS ACTIVATING 🚀 ---"
    log_event(start_msg)
    telegram_notify(start_msg)
    speak("Solana Hunter is activating")
    asyncio.run(hunt_for_launches())
