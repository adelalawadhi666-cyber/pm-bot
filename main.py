import os, time, json, requests
from py_clob_client.client import ClobClient
MODE = os.getenv("MODE", "paper").strip().lower()
PK = os.getenv("PK", "")
client = None
print("bot online", MODE, flush=True)
if MODE == "live" and len(PK) > 20:
    try:
        client = ClobClient("https://clob.polymarket.com", key=PK, chain_id=137)
        client.set_api_creds(client.create_or_derive_api_creds())
        print("clob ok", flush=True)
    except Exception as e:
        print("clob err", type(e).__name__, flush=True)
while True:
    try:
        ts = (int(time.time()) // 300) * 300
        slug = "btc-updown-5m-" + str(ts)
        r = requests.get("https://gamma-api.polymarket.com/events?slug=" + slug, timeout=15)
        data = r.json() if r.ok else []
        e = data[0] if data else {}
        mk = (e.get("markets") or [{}])[0]
        prices = mk.get("outcomePrices") or "[]"
        if isinstance(prices, str):
            prices = json.loads(prices)
        up = float(prices[0]) if prices else 0
        down = float(prices[1]) if len(prices) > 1 else 0
        tag = "LIVE" if MODE == "live" else "PAPER"
        if up >= 0.58:
            sig = tag + " BUY UP"
        elif down >= 0.58:
            sig = tag + " BUY DOWN"
        else:
            sig = "WAIT"
        print("pm", up, down, sig, flush=True)
    except Exception:
        print("err", flush=True)
    time.sleep(30)
