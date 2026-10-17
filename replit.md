# Running the bot on Replit

The `Start application` workflow runs `PORT=5000 python main.py`. It starts the Flask status page and the Telegram market-checking loop together.

Set `BOT_TOKEN` and `CHAT_ID` in Replit Secrets before starting the workflow. The Replit workflow sets port 5000 for the web preview; running `python main.py` directly defaults to port 10000 unless `PORT` is set.
