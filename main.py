import os, requests, yfinance as yf, time
from datetime import datetime
from threading import Thread
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bano Bot Live 24/7 OTC ✅"

def send(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except:
        pass

def get_rsi(prices, period=14):
    deltas = [prices[i+1]-prices[i] for i in range(len(prices)-1)]
    gains = [d if d>0 else 0 for d in deltas]
    losses = [-d if d<0 else 0 for d in deltas]
    if len(gains) < period: return 50
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

last_signals = {}
last_times = {}

def loop():
    time.sleep(10)
    send("✅ بوت بانو V2 اشتغل - OTC لكل الازواج")
    pairs = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "EURJPY=X", "GBPJPY=X", "USDCHF=X", "BTC-USD"]
    while True:
        try:
            for pair in pairs:
                hist = yf.Ticker(pair).history(period="1d", interval="1m")
                if len(hist) < 20: continue
                prices = hist['Close'].tolist()
                price = prices[-1]
                rsi = get_rsi(prices)
                key = pair
                if time.time() - last_times.get(key, 0) < 900: continue
                if abs(price - last_signals.get(key, {}).get('price',0)) < 0.00005: continue

                signal = None
                name = pair.replace("=X","").replace("-USD","")
                if rsi < 38:
                    signal = f"🟢 {name} CALL ⬆️\nRSI {rsi:.1f} | {datetime.now().strftime('%H:%M')} | {price:.5f}"
                elif rsi > 62:
                    signal = f"🔴 {name} PUT ⬇️\nRSI {rsi:.1f} | {datetime.now().strftime('%H:%M')} | {price:.5f}"

                if signal:
                    send(signal)
                    if "BTC" not in pair:
                        send(signal.replace(name, f"{name} OTC") + " (OTC)")
                    last_signals[key] = {'price': price}
                    last_times[key] = time.time()
                    time.sleep(2)
            time.sleep(120)
        except:
            time.sleep(60)

# شغل البوت بالخلفية
Thread(target=loop, daemon=True).start()

# افتح البورت بسرعة حتى ما يفشل
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)