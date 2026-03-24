import ccxt
import pandas as pd
import ta
import asyncio
from telegram import Bot

TOKEN = "8775882177:AAFZA6boI398Qn0wkrJdZCJ214-ENeEBIms"
CHAT_ID = "800747174"

bot = Bot(token=TOKEN)
exchange = ccxt.coinbase()

last_signal = None  # чтобы не спамить

def analyze():
    ohlcv = exchange.fetch_ohlcv('BTC/USD', timeframe='1h', limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])

    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    df['ema'] = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    last = df.iloc[-1]

    score = 0

    # RSI
    if last['rsi'] < 30:
        score += 1
    elif last['rsi'] > 70:
        score -= 1

    # EMA тренд
    if last['close'] > last['ema']:
        score += 1
    else:
        score -= 1

    # MACD
    if last['macd'] > last['macd_signal']:
        score += 1
    else:
        score -= 1

    # вероятность
    probability = int((score + 3) / 6 * 100)

    if score >= 2:
        signal = "📈 BUY"
    elif score <= -2:
        signal = "📉 SELL"
    else:
        signal = "⏸ HOLD"

    return signal, probability, last

async def send_signal():
    global last_signal

    signal, probability, last = analyze()

    # анти-спам
    if signal == last_signal:
        return

    last_signal = signal

    message = f"""
BTC сигнал: {signal}
Вероятность: {probability}%

RSI: {round(last['rsi'], 1)}
Цена: {round(last['close'], 2)}
"""

    await bot.send_message(chat_id=CHAT_ID, text=message)

async def main():
    while True:
        await send_signal()
        await asyncio.sleep(900)  # каждые 15 минут

asyncio.run(main())
