import time
import requests
print("bot online")
while True:
    try:
        r = requests.get("https://gamma-api.polymarket.com/markets?closed=false&limit=1", timeout=20)
        print("pm", r.status_code)
    except Exception as e:
        print("err")
    time.sleep(60)
