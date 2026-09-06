import os, time, json, requests
from py_clob_client_v2 import ClobClient, OrderArgs, PartialCreateOrderOptions, Side
MODE = os.getenv("MODE", "paper").strip().lower()
PK = os.getenv("POLY_PK", "")
client = None
print("bot online", MODE, flush=True)
if MODE == "live" and len(PK) > 20:
    try:
        client = ClobClient(host="https://clob.polymarket.com", chain_id=137, key=PK)
        creds = client.create_or_derive_api_key()
        client = ClobClient(host="https://clob.polymarket.com", chain_id=137, key=PK, creds=creds)
        print("clob ok", flush=True)
    except Exception as e:
        print("clob err", type(e).__name__, str(e)[:80], flush=True)
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
        if client and sig.startswith("LIVE BUY"):
            tid = mk.get("clobTokenIds") or "[]"
            if isinstance(tid, str):
                tid = json.loads(tid)
            tok = tid[0] if "UP" in sig else tid[1]
            sz = float(os.getenv("SIZE", "1"))
            px = down if "DOWN" in sig else up
            px = min(0.99, max(0.01, round(px, 2)))
            if px >= 0.90:
                print("skip late", px, flush=True)
            else:
                try:
                    o = client.create_and_post_order(OrderArgs(token_id=str(tok), price=px, size=sz, side=Side.BUY), options=PartialCreateOrderOptions(tick_size="0.01"))
                    print("ord ok", px, flush=True)
                except Exception as e:
                    print("ord err", type(e).__name__, str(e)[:80], flush=True)
    except Exception:
        print("err", flush=True)
    time.sleep(30)
