import os, time, json, requests
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY
MODE = os.getenv("MODE", "paper").strip().lower()
PK = os.getenv("PK", "")
SIZE = float(os.getenv("SIZE", "5"))
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
        tids = mk.get("clobTokenIds") or "[]"
        if isinstance(tids, str):
            tids = json.loads(tids)
        up = float(prices[0]) if prices else 0
        down = float(prices[1]) if len(prices) > 1 else 0
        tag = "LIVE" if MODE == "live" else "PAPER"
        tid = ""
        px = 0
        if up >= 0.58:
            sig = tag + " BUY UP"
            tid = str(tids[0]) if tids else ""
            px = up
        elif down >= 0.58:
            sig = tag + " BUY DOWN"
            tid = str(tids[1]) if len(tids) > 1 else ""
            px = down
        else:
