import os, time, json, requests
from datetime import datetime, timedelta, timezone

GAMMA = "https://gamma-api.polymarket.com"
MODE = os.getenv("MODE", "LIVE")
SIZE = float(os.getenv("SIZE", "2"))
bought = None
client = None
BUY = "BUY"

try:
    from py_clob_client.client import ClobClient
    from py_clob_client.clob_types import OrderArgs, OrderType
    from py_clob_client.order_builder.constants import BUY as BUY_SIDE
    BUY = BUY_SIDE
    pk = os.getenv("POLY_PK") or os.getenv("PK") or ""
    funder = os.getenv("FUNDER") or None
    if pk:
        client = ClobClient("https://clob.polymarket.com", key=pk, chain_id=137, funder=funder)
        api = os.getenv("POLY_API_KEY") or os.getenv("POLY_API")
        sec = os.getenv("POLY_SECRET") or os.getenv("POLY_SEC")
        pas = os.getenv("POLY_PASSPHRASE") or os.getenv("POLY_PASS") or os.getenv("POLY_PAS")
        if api and sec and pas:
            try:
                from py_clob_client.clob_types import ApiCreds
                client.set_api_creds(ApiCreds(api_key=api, api_secret=sec, api_passphrase=pas))
            except Exception as e:
                print("creds_off", type(e).__name__, flush=True)
        print("client_on", flush=True)
except Exception as e:
    print("client_off", type(e).__name__, str(e)[:80], flush=True)

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
        r = requests.get("https://clob.polymarket.com/price", params={"token_id": tok, "side": "buy"}, timeout=15)
        if r.ok:
            return float(r.json().get("price") or 0)
    except Exception:
        pass
    return 0.0

def buy(tok, price):
    args = OrderArgs(token_id=str(tok), price=round(float(price), 2), size=SIZE, side=BUY)
    signed = client.create_order(args)
    return client.post_order(signed, OrderType.GTC)

print("bot online", flush=True)

while True:
    try:
        et = timezone(timedelta(hours=-4))
        now = datetime.now(et)
        m = (now.minute // 5) * 5
        start = now.replace(minute=m, second=0, microsecond=0)
        found = None
        for i in (0, 1, 2):
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
                print(buy(up, pu), flush=True)
                bought = up
        elif pd >= 0.55 and pd <= 0.85:
            print(f"pm {pu:.3f} {pd:.3f} LIVE BUY DOWN", flush=True)
            if MODE == "LIVE" and client and bought != down:
                print(buy(down, pd), flush=True)
                bought = down
        else:
            print(f"pm {pu:.3f} {pd:.3f} WAIT", flush=True)
    except Exception as e:
        print("err", type(e).__name__, str(e)[:160], flush=True)
    time.sleep(8)
