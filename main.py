import time
import requests
print("bot online 3", flush=True)
while True:
    try:
        r = requests.get("https://gamma-api.polymarket.com/markets?closed=false&limit=1", timeout=15)
        data = r.json()
        m = data[0] if data else {}
        print("pm", r.status_code, m.get("question", "")[:80], flush=True)
    except Exception:
        print("err", flush=True)
    time.sleep(30)
