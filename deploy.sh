#!/bin/bash
echo "🔥 Starting ICEDEVILS-EMPIRE setup..."
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo "🔑 Loading environment variables..."
export $(grep -v '^#' .env | xargs)

echo "--- 🛡️ INITIALIZING THE ICEDEVILS EMPIRE 🛡️ ---"
sleep 1

# Launch Solana Hunter
if [ -f "solana_hunter.py" ]; then
  python3 solana_hunter.py > hunter_activity.log 2>&1 &
  echo "[✅] SolanaHunter thread launched."
else
  echo "⚠️ Warning: solana_hunter.py not found."
fi

# Launch Telegram Command Bot
if [ -f "telegram_bot.py" ]; then
  python3 telegram_bot.py > telegram_bot.log 2>&1 &
  echo "[✅] Telegram CommandHandler launched."
else
  echo "⚠️ Warning: telegram_bot.py not found. Command Handler is offline."
fi

# Optional future monitor module
if [ -f "system_monitor.py" ]; then
  python3 system_monitor.py > monitor.log 2>&1 &
  echo "[✅] System Monitor launched."
else
  echo "⚠️ Warning: system_monitor.py not found. System Monitor is offline."
fi

echo ""
echo "✅✅✅ ALL SYSTEMS ARE GO. THE EMPIRE IS LIVE. ✅✅✅"
echo "🔄 Running in background. Check logs:"
echo "   tail -f hunter_activity.log"
echo "   tail -f telegram_bot.log"
