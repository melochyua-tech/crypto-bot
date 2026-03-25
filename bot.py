import time
import ccxt
import pandas as pd
import ta
import requests

print("СТАРТ 🚀")

# 👉 ВСТАВЬ СВОЙ ТОКЕН
TOKEN = "8775882177:AAFJk_hSyVxWIWSaTXF9C9Z9N4e-ffSKNEc"

# 👉 ТВОЙ CHAT_ID
CHAT_ID = "800747174"

exchange = ccxt.binance()

last_signal = None

def get_data():
    ohlcv = exchange.fetch_ohlcv('BTC/EUR', timeframe='1m', limit=100)
    df = pd.DataFrame(ohlcv, columns=['time','open','high','low','close','volume'])
    return df

def analyze():
    df = get_data()
    rsi = ta.momentum.RSIIndicator(df['close']).rsi().iloc[-1]

    if rsi < 40:
        return "BUY", rsi
    elif rsi > 70:
        return "SELL", rsi
    else:
        return "HOLD", rsi

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.get(url, params=params)

def send_signal(signal, rsi, price):
    global last_signal

    if signal == last_signal:
        return

    if signal == "HOLD":
        send_message(f"📊 Статус: HOLD | RSI: {round(rsi,2)}")
        return

    emoji = {
        "BUY": "🟢",
        "SELL": "🔴",
        "HOLD": "⏸"
    }

    text = f"""
📊 BTC сигнал: {emoji[signal]} {signal}

RSI: {round(rsi, 2)}
Цена: {round(price, 2)}€
"""

    send_message(text)
    last_signal = signal

while True:
    try:
        signal, rsi = analyze()
        price = get_data()['close'].iloc[-1]

        print("Работает:", signal, rsi)

        send_signal(signal, rsi, price)

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
import time

print("СТАРТ 🚀")

while True:
    signal, rsi, price = analyze()

    print("Работает:", signal, rsi)

    send_signal(signal, rsi, price)

    time.sleep(60)
