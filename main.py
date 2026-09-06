import os, time, json, requests
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

def mkt():
    r=requests.get(GAMMA+"/markets",params={"closed":"false","active":"true","limit":200,"order":"endDate","ascending":"true"},timeout=20)
    r.raise_for_status()
    now=time.time()
    best=None
    for m in r.json():
        slug=(m.get("slug") or "")
        q=(m.get("question") or "").lower()
        if not slug.startswith("btc-updown-5m"): continue
        if m.get("acceptingOrders") is False: continue
        toks=toks_of(m)
        if not toks: continue
        print("hit", q[:80], flush=True)
        return toks[0],toks[1]
    win=int(now//300*300)
    for off in (0,300,-300,600,-600,900):
        slug=f"btc-updown-5m-{win+off}"
        r=requests.get(GAMMA+"/markets",params={"slug":slug},timeout=15)
        arr=r.json() if r.ok else []
        if isinstance(arr,dict): arr=[arr]
        for m in arr or []:
            toks=toks_of(m)
            if toks:
                print("hit slug", slug, flush=True)
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
