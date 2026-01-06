import asyncio
import requests
import time
from telegram import Bot
from datetime import datetime

# ===== CONFIG =====
TOKEN = "8524868065:AAEYfEsnBoAny2_DEEPTXXuss3qDUIG1rsc"
CHAT_ID = "1042967664"

PRICE_THRESHOLD = 700      # dollars
TIME_WINDOW = 3600         # 60 minutes = 3600 secondes
CHECK_INTERVAL = 60        # vérification toutes les 60s
# ==================

bot = Bot(token=TOKEN)

import asyncio  # nécessaire pour asyncio

async def send_alert(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

def get_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    r = requests.get(url, timeout=10)
    return float(r.json()["price"])

# Prix et temps de référence
reference_price = get_btc_price()
reference_time = time.time()

print("Bot BTC actif — surveillance variation ±700$ sur 60 minutes")

while True:
    try:
        # code à exécuter
        current_price = get_btc_price()
        current_time = time.time()

        elapsed_time = current_time - reference_time
        price_change = current_price - reference_price

        if elapsed_time >= TIME_WINDOW:
            if abs(price_change) >= PRICE_THRESHOLD:
                direction = "📈 FORTE HAUSSE" if price_change > 0 else "📉 FORTE CHUTE"
                message = (
                    f"{direction} BTC (1 min)\n\n"
                    f"Variation : {price_change:+,.2f} $\n"
                    f"Prix initial : {reference_price:,.2f} $\n"
                    f"Prix actuel : {current_price:,.2f} $\n"
                    f"Heure : {datetime.now().strftime('%H:%M:%S')}"
                )
                asyncio.run(send_alert(message))

            reference_price = current_price
            reference_time = current_time

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("Erreur :", e)
        time.sleep(10)