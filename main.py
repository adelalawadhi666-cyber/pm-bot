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
    et=timezone(timedelta(hours=-4))
    now=datetime.now(et)
    m=(now.minute//5)*5
    start=now.replace(minute=m,second=0,microsecond=0)
    for i in (1,2,0,3):
        w=start+timedelta(minutes=5*i)
        slug=f"btc-updown-5m-{int(w.timestamp())}"
        r=requests.get(GAMMA+"/markets",params={"slug":slug},timeout=15)
        if not r.ok: continue
