import time
import requests
print("bot online 4", flush=True)
URL = "https://gamma-api.polymarket.com/markets?closed=false&limit=100"
while True:
    try:
        r = requests.get(URL, timeout=15)
        data = r.json() if r.ok else []
        hit = None
        for m in data:
            q = (m.get("question") or "").lower()
            if "bitcoin" in q and "up or down" in q:
                hit = m
                break
        if hit:
            print("pm", r.status_code, hit.get("question", "")[:90], flush=True)
        else:
            print("pm", r.status_code, "no btc", flush=True)
    except Exception:
        print("err", flush=True)
    time.sleep(30)
