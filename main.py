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

def mkt():
    r=requests.get(GAMMA+"/events?closed=false&active=true&limit=80",timeout=20)
    r.raise_for_status()
    for e in r.json():
        title=(e.get("title") or "").lower()
        if "bitcoin" not in title and "btc" not in title: continue
        for m in e.get("markets") or []:
            q=(m.get("question") or "").lower()
            if "up or down" not in q and "up/down" not in q: continue
            toks=m.get("clobTokenIds") or []
            if isinstance(toks,str):
                try: toks=json.loads(toks)
                except: toks=[]
            if len(toks)>=2:
                print("hit", q[:70], flush=True)
                return toks[0],toks[1]
    r=requests.get(GAMMA+"/markets?closed=false&limit=300",timeout=20)
    r.raise_for_status()
    for m in r.json():
        q=(m.get("question") or "").lower()
        if ("bitcoin" in q or "btc" in q) and ("up or down" in q or "up/down" in q):
            toks=m.get("clobTokenIds") or []
            if isinstance(toks,str):
                try: toks=json.loads(toks)
                except: toks=[]
            if len(toks)>=2:
                print("hit", q[:70], flush=True)
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
