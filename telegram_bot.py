import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from notifier import telegram_notify, speak

# Load your .env
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BUSINESS_BOT_TOKEN")
PRIVATE_CHANNEL_ID = os.getenv("TELEGRAM_PRIVATE_CHANNEL_ID")
PUBLIC_CHANNEL_IDS = os.getenv("TELEGRAM_PUBLIC_CHANNEL_IDS", "").split(",")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 ICEDEVILS EMPIRE Hunter online and ready!")
    speak("Hunter is online and ready.")
    telegram_notify("🧠 Start command received — Hunter confirmed active.", PRIVATE_CHANNEL_ID)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Solana Hunter is active and scanning.")
    telegram_notify("📡 Status checked via Telegram.", PRIVATE_CHANNEL_ID)

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("♻️ Restarting Solana Hunter...")
    speak("Restarting the hunter.")
    telegram_notify("♻️ Restart command issued by admin.", PRIVATE_CHANNEL_ID)
    os.system("bash deploy.sh &")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("⚠️ Usage: /broadcast <message>")
        return
    for ch in PUBLIC_CHANNEL_IDS:
        telegram_notify(f"📢 Broadcast: {msg}", ch)
    await update.message.reply_text("✅ Message broadcasted to all public channels.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🧠 *ICEDEVILS EMPIRE COMMANDS:*\n\n"
        "/start - Initialize bot\n"
        "/status - Check hunter status\n"
        "/restart - Restart the hunter\n"
        "/broadcast <msg> - Send marketing message to all channels\n"
        "/help - Show this help"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

def main():
    if not BOT_TOKEN:
        print("❌ Missing TELEGRAM_BUSINESS_BOT_TOKEN in .env")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("help", help_command))

    print("✅ Telegram command interface started.")
    app.run_polling()

if __name__ == "__main__":
    main()
