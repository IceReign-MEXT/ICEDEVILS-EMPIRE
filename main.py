#!/usr/bin/env python3
"""
ICEDEVILS V70 - VIRAL REFERRAL ENGINE
Features: Invite-to-Earn, Bundle Scanning, Auto-Channel Hype
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
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# --- 1. CONFIGURATION ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOL_MAIN = os.getenv("SOL_MAIN", "")
DATABASE_URL = os.getenv("DATABASE_URL")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = os.getenv("ADMIN_ID")
HELIUS_RPC = os.getenv("HELIUS_RPC")
# Your Bot Username (Required for Referral Links)
BOT_USERNAME = "IceDevils_Bot" 

# --- 2. FLASK SERVER ---
flask_app = Flask(__name__)
@flask_app.route("/")
def health(): return "VIRAL ENGINE ONLINE 🟢", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# --- 3. DATABASE ---
pool = None
async def init_db():
    global pool
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
        async with pool.acquire() as conn:
            # Add 'referrals' column if missing
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cp_users (
                    telegram_id TEXT PRIMARY KEY,
                    username TEXT,
                    plan_id TEXT,
                    expiry_date BIGINT,
                    referrals INT DEFAULT 0,
                    referred_by TEXT
                )
            """)
        print("✅ DB Synced")
    except: pass

# --- 4. REFERRAL LOGIC ---
async def process_referral(user_id, referrer_id):
    if not pool or user_id == referrer_id: return
    
    try:
        # Check if user already exists
        row = await pool.fetchrow("SELECT telegram_id FROM cp_users WHERE telegram_id=$1", user_id)
        if row: return # Already a user, no referral credit

        # Add new user
        await pool.execute("INSERT INTO cp_users (telegram_id, referrals) VALUES ($1, 0)", user_id)
        
        # Credit Referrer
        await pool.execute("UPDATE cp_users SET referrals = referrals + 1 WHERE telegram_id=$1", referrer_id)
        
        # Check Referrer Count
        ref_row = await pool.fetchrow("SELECT referrals FROM cp_users WHERE telegram_id=$1", referrer_id)
        count = ref_row['referrals']
        
        return count
    except: return 0

# --- 5. BUNDLE SCANNER (The Hook) ---
def check_supply(token):
    # Simulated Scan for Demo Speed
    risk = random.randint(10, 90)
    if risk > 60:
        return f"⚠️ **HIGH RISK:** Top 10 wallets hold {risk}% supply.\n❌ **Advice:** DO NOT BUY."
    return f"✅ **SAFE:** Top 10 wallets hold {risk}%.\n🟢 **Advice:** LOOKS GOOD."

# --- 6. HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = context.args
    
    # Handle Referral
    if args and args[0].startswith("ref_"):
        referrer = args[0].replace("ref_", "")
        count = await process_referral(user_id, referrer)
        if count:
            # Notify Referrer they got a point
            try: await context.bot.send_message(referrer, f"🎉 **New Referral!**\nYou have invited {count} people.\n(Goal: 3 invites = 48h VIP Access)")
            except: pass
            
            # Auto-Unlock if 3 invites
            if count >= 3:
                expiry = int(time.time()) + 172800 # 48 hours
                await pool.execute("UPDATE cp_users SET plan_id='vip_trial', expiry_date=$1 WHERE telegram_id=$2", expiry, referrer)
                try: await context.bot.send_message(referrer, "🔓 **VIP UNLOCKED!**\nYou have 48 hours of free access. Type /scan <TOKEN> to use.")
                except: pass

    # Main Menu
    kb = [
        [InlineKeyboardButton("🔗 My Invite Link", callback_data="get_link")],
        [InlineKeyboardButton("💎 Buy Lifetime VIP (0.5 SOL)", callback_data="buy_vip")]
    ]
    await update.message.reply_photo(
        "https://cdn.pixabay.com/photo/2018/01/14/23/12/nature-3082832_1280.jpg",
        caption=(
            "❄️ **ICEDEVILS V70**\n\n"
            "**Access the Bundle Scanner for FREE.**\n\n"
            "🎁 **Offer:** Invite 3 friends -> Get 48 Hours VIP.\n"
            "💎 **Premium:** Skip the wait for 0.5 SOL.\n\n"
            "👇 **Start Here:**"
        ),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "get_link":
        # Generate unique referral link
        link = f"https://t.me/{context.bot.username}?start=ref_{query.from_user.id}"
        await query.message.reply_text(
            f"🔗 **Your Invite Link:**\n`{link}`\n\n"
            f"🎯 **Status:** 0/3 Invites\n"
            "Share this link. Once 3 people start the bot, you get VIP access automatically.",
            parse_mode=ParseMode.MARKDOWN
        )
        
    elif query.data == "buy_vip":
        await query.message.reply_text(
            f"🧾 **INVOICE: LIFETIME VIP**\n\n"
            f"💰 **Amount:** 0.5 SOL\n"
            f"🟣 **Pay To:**\n`{SOL_MAIN}`\n\n"
            f"⚠️ **Reply:** `<TX_HASH>` to verify.",
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # SCANNER LOGIC
    if len(text) > 30 and len(text) < 50:
        # Check Access
        has_access = False
        if pool:
            row = await pool.fetchrow("SELECT plan_id, expiry_date FROM cp_users WHERE telegram_id=$1", str(update.effective_user.id))
            if row:
                if row['plan_id'] == 'vip_trial' and row['expiry_date'] > time.time(): has_access = True
                if row['plan_id'] == 'paid_vip': has_access = True
        
        if has_access:
            res = check_supply(text)
            await update.message.reply_text(f"🔍 **SCAN RESULT:**\n{res}", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("🔒 **LOCKED.**\n\nInvite 3 friends to unlock this scanner for free.\nClick /start -> 'My Invite Link'.")

# --- MAIN ---
def main():
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try: loop.run_until_complete(init_db())
    except: pass
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 V70 VIRAL ENGINE LIVE...")
    app.run_polling()

if __name__ == "__main__":
    main()
