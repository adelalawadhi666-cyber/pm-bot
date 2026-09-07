import os, time, json, requests
from datetime import datetime, timedelta, timezone

GAMMA = "https://gamma-api.polymarket.com"
SIZE = float(os.getenv("SIZE", "2"))

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

print("bot online paper", flush=True)

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
            print(f"SIGNAL BUY UP {pu:.3f} {pd:.3f} size={SIZE}", flush=True)
        elif pd >= 0.55 and pd <= 0.85:
            print(f"SIGNAL BUY DOWN {pu:.3f} {pd:.3f} size={SIZE}", flush=True)
        else:
            print(f"WAIT {pu:.3f} {pd:.3f}", flush=True)
    except Exception as e:
        print("err", type(e).__name__, str(e)[:160], flush=True)
    time.sleep(8)
