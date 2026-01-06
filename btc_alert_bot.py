import asyncio
import requests
import time
import os
from telegram import Bot
from datetime import datetime

# ===== CONFIG =====
TOKEN = os.environ['TOKEN']
CHAT_ID = os.environ['CHAT_ID']

PRICE_THRESHOLD = float(os.environ.get('PRICE_THRESHOLD', 700))
TIME_WINDOW = int(os.environ.get('TIME_WINDOW', 1200))
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 60))

# ==================
bot = Bot(token=TOKEN)

async def send_alert(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        print(f"Alerte envoyée : {message[:50]}...")
    except Exception as e:
        print(f"Erreur envoi Telegram : {e}")

def get_btc_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return float(r.json()["price"])
    except Exception as e:
        print(f"Erreur API Binance : {e}")
        return None

print("Bot BTC actif — surveillance variation ±{} $ sur {} minutes".format(PRICE_THRESHOLD, TIME_WINDOW // 60))

# Prix et temps de référence
reference_price = get_btc_price()
if reference_price is None:
    reference_price = 0  # fallback
reference_time = time.time()

# Boucle principale (sans asyncio.run dans une loop)
loop = asyncio.get_event_loop()

while True:
    try:
        current_price = get_btc_price()
        if current_price is None:
            time.sleep(CHECK_INTERVAL)
            continue

        current_time = time.time()
        elapsed_time = current_time - reference_time
        price_change = current_price - reference_price

        if elapsed_time >= TIME_WINDOW:
            if abs(price_change) >= PRICE_THRESHOLD:
                direction = "📈 FORTE HAUSSE" if price_change > 0 else "📉 FORTE CHUTE"
                message = (
                    f"{direction} BTC\n\n"
                    f"Variation : {price_change:+,.2f} $\n"
                    f"Prix initial : {reference_price:,.2f} $\n"
                    f"Prix actuel : {current_price:,.2f} $\n"
                    f"Heure : {datetime.now().strftime('%H:%M:%S')}"
                )
                loop.run_until_complete(send_alert(message))

            # Reset référence
            reference_price = current_price
            reference_time = current_time

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print(f"Erreur inattendue : {e}")
        time.sleep(10)