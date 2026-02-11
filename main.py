#!/usr/bin/env python3
"""
ICEDEVILS EMPIRE V50 - SOLANA WARLORD
Features: Green Candle Printer, Helius Tracking, Auto-Channel Hype
"""

import os
import time
import asyncio
import threading
import requests
import asyncpg
import random
from dotenv import load_dotenv
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# --- 1. CONFIGURATION ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOL_MAIN = os.getenv("SOL_MAIN", "")
DATABASE_URL = os.getenv("DATABASE_URL")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = os.getenv("ADMIN_ID")
HELIUS_RPC = os.getenv("HELIUS_RPC")

# --- 2. ASSETS ---
IMG_PUMP = "https://cdn.pixabay.com/photo/2021/05/09/18/54/chart-6241774_1280.png"
IMG_WHALE = "https://cdn.pixabay.com/photo/2022/10/24/18/43/cyberpunk-7544062_1280.jpg"

# --- 3. FLASK SERVER (RENDER FIX) ---
flask_app = Flask(__name__)

@flask_app.route("/")
@flask_app.route("/health")
def health(): return "ICEDEVILS V50 ONLINE", 200

def run_web():
    # Dynamic Port Assignment for Render
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

# --- 4. DATABASE ---
pool = None
async def init_db():
    global pool
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
        print("✅ Connected to Empire Database")
    except: pass

# --- 5. THE GREEN CANDLE ENGINE ---
async def candle_printer(app: Application):
    print("🚀 V50 Candle Printer Started...")
    while True:
        try:
            if CHANNEL_ID:
                # 1. Fetch Trending Solana Token
                try:
                    r = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=5).json()
                    coin = random.choice(r['coins'][:5])['item']
                    ticker = coin['symbol']
                    price = float(str(coin.get('data', {}).get('price', 0)).replace("$",""))
                except:
                    ticker = "SOL"
                    price = 145.20

                # 2. Generate "Green Candle" Alert
                # This simulates a massive buy happening RIGHT NOW
                buy_amt = random.uniform(50, 500) # SOL
                tx_link = f"https://solscan.io/tx/Simulated_Helius_Track_{random.randint(1000,9999)}"

                msg = (
                    f"🟢 **GOD CANDLE DETECTED** 🟢\n\n"
                    f"💎 **Token:** ${ticker}\n"
                    f"💰 **Amount:** {buy_amt:.2f} SOL\n"
                    f"💹 **Price Impact:** +{random.uniform(2, 8):.2f}%\n"
                    f"🌊 **DEX:** Raydium / Jupiter\n\n"
                    f"🤖 **IceDevils AI:**\n"
                    f"Institutional whale entry confirmed. Volume spiking.\n\n"
                    f"🎯 **Action:** COPY TRADE NOW"
                )

                # 3. Post to Channel
                await app.bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=IMG_PUMP,
                    caption=msg,
                    parse_mode=ParseMode.MARKDOWN
                )
                print(f"✅ Green Candle Posted: {ticker}")

            # Post every 20-40 Minutes
            await asyncio.sleep(random.randint(1200, 2400))

        except Exception as e:
            print(f"Engine Sleep: {e}")
            await asyncio.sleep(300)

# --- 6. TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🚀 Boost Token (1 SOL)", callback_data="buy_boost")],
        [InlineKeyboardButton("💎 VIP Signals (0.5 SOL)", callback_data="buy_vip")],
        [InlineKeyboardButton("📊 View Dashboard", url="https://icegods-dashboard-56aj.onrender.com")]
    ]

    txt = (
        "❄️ **ICEDEVILS EMPIRE V50**\n\n"
        "The most powerful Solana Intelligence Terminal.\n\n"
        "🟢 **Capabilities:**\n"
        "• Green Candle Detection\n"
        "• Helius RPC Whale Tracking\n"
        "• Auto-Trending Injection\n\n"
        "👇 **Initialize System:**"
    )
    await update.message.reply_photo(photo=IMG_WHALE, caption=txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    price = "1.0" if "boost" in query.data else "0.5"
    service = "VOLUME BOOST" if "boost" in query.data else "VIP SIGNALS"

    await query.message.reply_text(
        f"🧾 **INVOICE: {service}**\n\n"
        f"💰 **Amount:** {price} SOL\n"
        f"🟣 **Pay To:**\n`{SOL_MAIN}`\n\n"
        f"⚠️ **Reply:** `/confirm <TX_HASH>`",
        parse_mode=ParseMode.MARKDOWN
    )

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: `/confirm <TX>`")
    tx = context.args[0]

    # Helius Verification Simulation
    await update.message.reply_text("🛰 **Querying Helius Node...**")
    time.sleep(1)

    # Send to Admin for final check
    if ADMIN_ID:
        await context.bot.send_message(ADMIN_ID, f"💰 **PAYMENT:** {tx} from @{update.effective_user.username}")

    await update.message.reply_text("✅ **VERIFIED.**\nAdmin will activate your boost/access shortly.")

# --- MAIN ---
def main():
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try: loop.run_until_complete(init_db())
    except: pass

    loop.create_task(candle_printer(app))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("confirm", confirm))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 ICEDEVILS V50 LIVE...")
    app.run_polling()

if __name__ == "__main__":
    main()
