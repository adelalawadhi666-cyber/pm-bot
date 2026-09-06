import time
import json
import requests
print("bot online 8", flush=True)
while True:
    try:
        ts = (int(time.time()) // 300) * 300
        slug = "btc-updown-5m-" + str(ts)
        r = requests.get("https://gamma-api.polymarket.com/events", params={"slug": slug}, timeout=15)
        data = r.json() if r.ok else []
        e = data[0] if data else {}
        mk = (e.get("markets") or [{}])[0]
        prices = mk.get("outcomePrices") or "[]"
        if isinstance(prices, str):
            prices = json.loads(prices)
        print("pm", r.status_code, e.get("title", slug)[:50], "up", prices[0] if prices else "?", "down", prices[1] if len(prices) > 1 else "?", flush=True)
    except Exception:
        print("err", flush=True)
    time.sleep(30)
