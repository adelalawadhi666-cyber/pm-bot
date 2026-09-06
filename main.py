import time
import requests
print("bot online 5", flush=True)
URL = "https://gamma-api.polymarket.com/events?active=true&closed=false&slug_contains=btc-updown-5m&limit=5"
while True:
    try:
        r = requests.get(URL, timeout=15)
        data = r.json() if r.ok else []
        e = data[0] if data else {}
        title = e.get("title") or e.get("slug") or "none"
        print("pm", r.status_code, title[:90], flush=True)
    except Exception:
        print("err", flush=True)
    time.sleep(30)
