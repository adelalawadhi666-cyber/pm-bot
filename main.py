import os, time, json, requests
from datetime import datetime
from py_clob_client_v2 import ClobClient, Side

HOST="https://clob.polymarket.com"
GAMMA="https://gamma-api.polymarket.com"
PK=os.getenv("POLY_PK")
FUNDER=os.getenv("FUNDER")
SIZE=float(os.getenv("SIZE","1"))
MODE=os.getenv("MODE","LIVE")

print("bot online live", flush=True)
client=ClobClient(HOST,key=PK,chain_id=137,signature_type=3,funder=FUNDER)
creds=client.create_or_derive_api_key()
client=ClobClient(HOST,key=PK,chain_id=137,signature_type=3,funder=FUNDER,creds=creds)
print("clob ok", flush=True)

def toks_of(m):
    toks=m.get("clobTokenIds") or []
    if isinstance(toks,str):
        try: toks=json.loads(toks)
        except: toks=[]
    return toks if len(toks)>=2 else None

def alive(m):
    if m.get("acceptingOrders") is False: return False
    if m.get("closed") is True: return False
    ed=m.get("endDate") or ""
    try:
        t=datetime.fromisoformat(ed.replace("Z","+00:00")).timestamp()
        return t>time.time()+30
    except:
        return False

def mkt():
    r=requests.get(GAMMA+"/markets",params={"closed":"false","limit":300,"order":"endDate","ascending":"true"},timeout=20)
    r.raise_for_status()
    for m in r.json():
        slug=(m.get("slug") or "")
        if not slug.startswith("btc-updown-5m"): continue
        if not alive(m): continue
        toks=toks_of(m)
        if not toks: continue
        print("hit", (m.get("question") or "")[:80], flush=True)
        return toks[0],toks[1]
    return None

def px(tid):
    r=requests.get(HOST+"/price",params={"token_id":tid,"side":"buy"},timeout=15)
    r.raise_for_status()
    return float(r.json().get("price") or 0)

bought=None
while True:
    try:
        ids=mkt()
        if not ids:
            print("no mkt", flush=True)
            time.sleep(8)
            continue
        up,down=ids
        pu,pd=px(up),px(down)
        if pu>=0.70:
            print(f"pm {pu:.3f} {pd:.3f} LIVE BUY UP", flush=True)
            if MODE=="LIVE" and bought!=up:
                print(client.create_order(token_id=up,price=min(pu+0.02,0.99),size=SIZE,side=Side.BUY), flush=True)
                bought=up
        elif pd>=0.70:
            print(f"pm {pu:.3f} {pd:.3f} LIVE BUY DOWN", flush=True)
            if MODE=="LIVE" and bought!=down:
                print(client.create_order(token_id=down,price=min(pd+0.02,0.99),size=SIZE,side=Side.BUY), flush=True)
                bought=down
        else:
            print(f"pm {pu:.3f} {pd:.3f} WAIT", flush=True)
    except Exception as e:
        print("err", type(e).__name__, str(e)[:160], flush=True)
    time.sleep(8)
