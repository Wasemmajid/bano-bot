import os, requests, yfinance as yf, time
from datetime import datetime
from threading import Thread
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bano Bot is Alive 24/7"

def send(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except:
        pass

def loop():
    send("✅ بوت بانو اشتغل 24 ساعة")
    pairs = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "BTC-USD"]
    while True:
        for s in pairs:
            try:
                df = yf.download(s, period="1d", interval="5m", progress=False)
                if len(df) < 30: continue
                close = df['Close']
                price = float(close.iloc[-1])
                ema9 = float(close.ewm(span=9).mean().iloc[-1])
                ema21 = float(close.ewm(span=21).mean().iloc[-1])
                if ema9 > ema21:
                    send(f"🟢 {s} CALL {price}")
                elif ema9 < ema21:
                    send(f"🔴 {s} PUT {price}")
            except:
                continue
        time.sleep(120)

Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
