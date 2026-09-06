import time
import requests
print("bot online 7", flush=True)
while True:
    try:
        ts = (int(time.time()) // 300) * 300
        slug = "btc-updown-5m-" + str(ts)
        r = requests.get("https://gamma-api.polymarket.com/events", params={"slug": slug}, timeout=15)
        data = r.json() if r.ok else []
        e = data[0] if data else {}
        print("pm", r.status_code, e.get("title") or slug, flush=True)
    except Exception:
        print("err", flush=True)
    time.sleep(30)
