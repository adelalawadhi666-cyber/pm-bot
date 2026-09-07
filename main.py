import os, time, json, requests
from datetime import datetime, timezone, timedelta
from py_clob_client_v2 import ClobClient, Side

HOST="https://clob.polymarket.com"
GAMMA="https://gamma-api.polymarket.com"
PK=os.getenv("POLY_PK")
FUNDER=os.getenv("FUNDER")
SIZE=float(os.getenv("SIZE","1"))
MODE=os.getenv("MODE","LIVE")

print("bot online live", flush=True)
try:
    client=ClobClient(HOST,key=PK,chain_id=137,signature_type=3,funder=FUNDER)
    creds=client.create_or_derive_api_key()
    client=ClobClient(HOST,key=PK,chain_id=137,signature_type=3,funder=FUNDER,creds=creds)
    print("clob ok", flush=True)
except Exception as e:
    print("clob err", type(e).__name__, str(e)[:160], flush=True)
    client=None

def toks_of(m):
    toks=m.get("clobTokenIds") or []
    if isinstance(toks,str):
        try: toks=json.loads(toks)
        except: toks=[]
    return toks if len(toks)>=2 else None

def px(tid):
    r=requests.get(HOST+"/price",params={"token_id":tid,"side":"buy"},timeout=15)
    r.raise_for_status()
    return float(r.json().get("price") or 0)

bought=None
while True:
    try:
        et=timezone(timedelta(hours=-4))
        now=datetime.now(et)
        m=(now.minute//5)*5
        start=now.replace(minute=m,second=0,microsecond=0)
        found=None
        for i in (1,2,0):
            w=start+timedelta(minutes=5*i)
            slug=f"btc-updown-5m-{int(w.timestamp())}"
            r=requests.get(GAMMA+"/markets",params={"slug":slug},timeout=15)
            print("slug", slug, r.status_code, flush=True)
            if not r.ok: continue
            arr=r.json()
            if isinstance(arr,dict): arr=[arr]
            for m0 in arr or []:
                toks=toks_of(m0)
                if toks:
                    found=toks
                    break
            if found: break
        if not found:
            print("no toks", flush=True)
            time.sleep(8)
            continue
        up,down=found[0],found[1]
        pu,pd=px(up),px(down)
        if pu>=0.62 and pu<=0.85:
            print(f"pm {pu:.3f} {pd:.3f} LIVE BUY UP", flush=True)
            if MODE=="LIVE" and client and bought!=up:
                print(client.create_order(token_id=up,price=min(pu+0.02,0.99),size=SIZE,side=Side.BUY), flush=True)
                bought=up
        elif pd>=0.62 and pd<=0.85:
            print(f"pm {pu:.3f} {pd:.3f} LIVE BUY DOWN", flush=True)
            if MODE=="LIVE" and client and bought!=down:
                print(client.create_order(token_id=down,price=min(pd+0.02,0.99),size=SIZE,side=Side.BUY), flush=True)
                bought=down
        else:
            print(f"pm {pu:.3f} {pd:.3f} WAIT", flush=True)
    except Exception as e:
        print("err", type(e).__name__, str(e)[:160], flush=True)
    time.sleep(8)
