import time
from datetime import datetime, timezone

print("bot online")
while True:
    now = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print("alive", now)
    time.sleep(30)
