import time
import requests
print("bot online 6", flush=True)
URL = "https://gamma-api.polymarket.com/markets?closed=false&slug_contains=btc-updown-5m&limit=5"
while True:
    try:
        r = requests.get(URL, timeout=15)
        data = r.json() if r.ok else []
        m = data[0] if data else {}
        print("pm", r.status_code, (m.get("question") or m.get("slug") or "none")[:90], flush=True)
    except Exception:
        print("err", flush=True)
    time.sleep(30)
