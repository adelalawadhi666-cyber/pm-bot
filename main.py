import time
import requests
print("bot online", flush=True)
while True:
    try:
        r = requests.get("https://gamma-api.polymarket.com/markets?limit=1", timeout=15)
        print("pm", r.status_code, flush=True)
    except Exception:
        print("err", flush=True)
    time.sleep(30)
