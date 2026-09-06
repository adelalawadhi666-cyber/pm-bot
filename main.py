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

print("loop start", flush=True)
while True:
    try:
        print("tick", flush=True)
        et=timezone(timedelta(hours=-4))
        now=datetime.now(et)
        m=(now.minute//5)*5
        start=now.replace(minute=m,second=0,microsecond=0)
        w=start+timedelta(minutes=5)
        slug=f"btc-updown-5m-{int(w.timestamp())}"
        r=requests.get(GAMMA+"/markets",params={"slug":slug},timeout=15)
        print("slug", slug, r.status_code, flush=True)
    except Exception as e:
        print("err", type(e).__name__, str(e)[:160], flush=True)
    time.sleep(8)
