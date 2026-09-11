import os, time, json, requests
from datetime import datetime, timezone, timedelta
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

HOST="https://clob.polymarket.com"
GAMMA="https://gamma-api.polymarket.com"
PK=os.getenv("POLY_PK")
FUNDER=os.getenv("FUNDER")
SIZE=float(os.getenv("SIZE","1"))
MODE=os.getenv("MODE","LIVE")
print("bot online live", flush=True)
client=None
try:
    creds=ApiCreds(os.getenv("POLY_API_KEY") or os.getenv("POLY_API"), os.getenv("POLY_SECRET") or os.getenv("POLY_SEC"), os.getenv("POLY_PASSPHRASE") or os.getenv("POLY_PAS"))
    client=ClobClient(HOST,key=PK,chain_id=137,creds=creds,signature_type=1,funder=FUNDER)
    print("clob ok", flush=True)
except Exception as e:
    print("clob err", type(e).__name__, str(e)[:160], flush=True)

def toks_of(m):
    t=m.get("clobTokenIds") or []
    if isinstance(t,str):
        try: t=json.loads(t)
        except: t=[]
    return t if len(t)>=2 else None

def px(tid):
    r=requests.get(HOST+"/price",params={"token_id":tid,"side":"buy"},timeout=15)
    return float((r.json() or {}).get("price") or 0) if r.ok else 0

bought=None
bought_slug=None
while True:
    try:
        et=timezone(timedelta(hours=-4))
        now=datetime.now(et)
        start=now.replace(minute=(now.minute//5)*5,second=0,microsecond=0)
        found=None
        slug=None
        for i in (0,1):
            slug=f"btc-updown-5m-{int((start+timedelta(minutes=5*i)).timestamp())}"
            r=requests.get(GAMMA+"/markets",params={"slug":slug},timeout=15)
            print("slug",slug,r.status_code,flush=True)
            if not r.ok: continue
            arr=r.json()
            if isinstance(arr,dict): arr=[arr]
            for m0 in arr or []:
                t=toks_of(m0)
                if t:
                    found=t
                    break
            if found: break
        if not found:
            print("no toks",flush=True); time.sleep(5); continue
        if bought_slug and bought_slug!=slug:
            bought=None
        up,down=found[0],found[1]
        pu,pd=px(up),px(down)
        if 0.55<=pu<=0.88:
            print(f"pm {pu:.3f} {pd:.3f} LIVE BUY UP",flush=True)
            if MODE=="LIVE" and client and bought!=up:
                o=client.create_order(OrderArgs(token_id=up,price=min(pu+0.02,0.99),size=SIZE,side=BUY))
                print(client.post_order(o, OrderType.GTC),flush=True)
                bought=up
                bought_slug=slug
        elif 0.55<=pd<=0.88:
            print(f"pm {pu:.3f} {pd:.3f} LIVE BUY DOWN",flush=True)
            if MODE=="LIVE" and client and bought!=down:
                o=client.create_order(OrderArgs(token_id=down,price=min(pd+0.02,0.99),size=SIZE,side=BUY))
                print(client.post_order(o, OrderType.GTC),flush=True)
                bought=down
                bought_slug=slug
        else:
            print(f"pm {pu:.3f} {pd:.3f} WAIT",flush=True)
    except Exception as e:
        print("err",type(e).__name__,str(e)[:160],flush=True)
    time.sleep(5)
