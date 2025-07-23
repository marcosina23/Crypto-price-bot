import os
import logging
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from telegram import Bot

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

if not TOKEN or not CHAT_ID:
    logging.error("TELEGRAM_TOKEN и CHAT_ID должны быть заданы")
    exit(1)

bot = Bot(token=TOKEN)

TARGETS = {
    'ethereum': {'buy': 1600, 'sell': 2000},
    'binancecoin': {'buy': 270, 'sell': 350},
}

def check_prices():
    try:
        ids = ','.join(TARGETS.keys())
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd'
        resp = requests.get(url, timeout=10)
        data = resp.json()
        for coin, th in TARGETS.items():
            price = data.get(coin, {}).get('usd')
            if price is None: continue
            if price <= th['buy']:
                bot.send_message(int(CHAT_ID), f"💚 Цена {coin} упала до {price} USD — пора покупать! (цель: {th['buy']})")
            elif price >= th['sell']:
                bot.send_message(int(CHAT_ID), f"🔴 Цена {coin} поднялась до {price} USD — можно продавать! (цель: {th['sell']})")
    except Exception as e:
        logging.error(f"Ошибка при проверке цен: {e}")

if __name__ == '__main__':
    bot.send_message(int(CHAT_ID), "🚀 Бот запущен и отслеживает цены каждые 5 минут!")
    scheduler = BlockingScheduler()
    scheduler.add_job(check_prices, 'interval', minutes=5)
    scheduler.start()
