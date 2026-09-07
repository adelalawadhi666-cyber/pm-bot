import os, time, json, requests
from datetime import datetime, timedelta, timezone

GAMMA = "https://gamma-api.polymarket.com"
MODE = os.getenv("MODE", "LIVE")
SIZE = 2.0
bought = None
client = None

try:
    from py_clob_client.client import ClobClient
    key = os.getenv("PK") or os.getenv("PRIVATE_KEY")
    if key:
        client = ClobClient("https://clob.polymarket.com", key=key, chain_id=137)
except Exception as e:
    print("client_off", type(e).__name__, flush=True)

def toks_of(m):
    t = m.get("clobTokenIds") or m.get("clob_token_ids") or []
    if isinstance(t, str):
        try:
            t = json.loads(t)
        except Exception:
            t = []
    if len(t) >= 2:
        return t[0], t[1]
    return None

def px(tok):
    try:
        r = requests.get(GAMMA + "/markets", params={"clob_token_ids": tok}, timeout=15)
        if not r.ok:
            return 0.0
        arr = r.json()
        if isinstance(arr, dict):
            arr = [arr]
        for m in arr or []:
            prices = m.get("outcomePrices") or m.get("outcome_prices")
            if isinstance(prices, str):
                prices = json.loads(prices)
            ids = m.get("clobTokenIds") or m.get("clob_token_ids") or []
            if isinstance(ids, str):
                ids = json.loads(ids)
            if prices and ids and tok in ids:
                i = ids.index(tok)
                return float(prices[i])
    except Exception:
        pass
    try:
        r = requests.get("https://clob.polymarket.com/price", params={"token_id": tok, "side": "buy"}, timeout=15)
        if r.ok:
            return float(r.json().get("price") or 0)
    except Exception:
        pass
    return 0.0

print("bot online", flush=True)

while True:
    try:
        et = timezone(timedelta(hours=-4))
        now = datetime.now(et)
        m = (now.minute // 5) * 5
        start = now.replace(minute=m, second=0, microsecond=0)
        found = None
        for i in (1, 2, 0):
            w = start + timedelta(minutes=5 * i)
            slug = f"btc-updown-5m-{int(w.timestamp())}"
            r = requests.get(GAMMA + "/markets", params={"slug": slug}, timeout=15)
            print("slug", slug, r.status_code, flush=True)
            if not r.ok:
                continue
            arr = r.json()
            if isinstance(arr, dict):
                arr = [arr]
            for m0 in arr or []:
                toks = toks_of(m0)
                if toks:
                    found = toks
                    break
            if found:
                break
        if not found:
            print("no toks", flush=True)
            time.sleep(8)
            continue
        up, down = found[0], found[1]
        pu, pd = px(up), px(down)
        if pu >= 0.55 and pu <= 0.85:
            print(f"pm {pu:.3f} {pd:.3f} LIVE BUY UP", flush=True)
            if MODE == "LIVE" and client and bought != up:
                print(client.create_order(token_id=up, price=round(pu, 2), size=SIZE, side="BUY"), flush=True)
                bought = up
        elif pd >= 0.55 and pd <= 0.85:
            print(f"pm {pu:.3f} {pd:.3f} LIVE BUY DOWN", flush=True)
            if MODE == "LIVE" and client and bought != down:
                print(client.create_order(token_id=down, price=round(pd, 2), size=SIZE, side="BUY"), flush=True)
                bought = down
        else:
            print(f"pm {pu:.3f} {pd:.3f} WAIT", flush=True)
    except Exception as e:
        print("err", type(e).__name__, str(e)[:120], flush=True)
    time.sleep(8)
