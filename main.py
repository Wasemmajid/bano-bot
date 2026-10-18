import os, requests, yfinance as yf, time
from datetime import datetime
from threading import Thread
from flask import Flask
import numpy as np

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

app = Flask(__name__)


@app.route("/")
def home():
    return "Bano Bot V2 Live - All Pairs + OTC ✅"


def send(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except:
        pass


def get_rsi(prices, period=14):
    prices = np.array(prices)
    if len(prices) < period + 2:
        return 50
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    if down == 0:
        return 70 if up != 0 else 50
    rs = up / down
    rsi = 100 - (100 / (1 + rs))
    for i in range(period, len(deltas)):
        delta = deltas[i]
        if delta > 0:
            upval, downval = delta, 0
        else:
            upval, downval = 0, -delta
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        if down == 0:
            return 70
        rs = up / down
        rsi = 100 - (100 / (1 + rs))
    return rsi


last_times = {}


def loop():
    time.sleep(10)
    send("✅ بوت بانو V2 النهائي اشتغل - OTC لكل الازواج + RSI محسن")
    pairs = [
        "EURUSD=X",
        "GBPUSD=X",
        "USDJPY=X",
        "AUDUSD=X",
        "EURJPY=X",
        "GBPJPY=X",
        "USDCHF=X",
        "USDCAD=X",
        "EURGBP=X",
        "BTC-USD",
        "ETH-USD",
        "GC=F",
    ]

    while True:
        try:
            for pair in pairs:
                try:
                    hist = yf.Ticker(pair).history(period="2d", interval="5m")
                    if len(hist) < 20:
                        continue
                    prices = hist["Close"].tolist()
                    price = prices[-1]
                    rsi = get_rsi(prices)

                    key = pair
                    # كولداون 15 دقيقة لكل زوج
                    if time.time() - last_times.get(key, 0) < 300:
                        continue

                    signal = None
                    name = pair.replace("=X", "").replace("-USD", "")

                    if rsi < 35:
                        signal = f"🟢 {name} CALL ⬆️\nRSI {rsi:.1f} | {datetime.now().strftime('%H:%M')} | {price:.5f}"
                    elif rsi > 65:
                        signal = f"🔴 {name} PUT ⬇️\nRSI {rsi:.1f} | {datetime.now().strftime('%H:%M')} | {price:.5f}"

                    if signal:
                        send(signal)
                        # يدز OTC لكل الازواج ما عدا الكريبتو
                        if "BTC" not in pair and "ETH" not in pair:
                            send(signal.replace(name, f"{name} OTC") + " (OTC)")
                        last_times[key] = time.time()
                        time.sleep(2)
                except:
                    continue
            time.sleep(120)
        except:
            time.sleep(60)


Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
