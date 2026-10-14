import urllib.request
import json
import time

print("Testing /api/v1/health ...")
t0 = time.time()
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health", timeout=10) as res:
        data = res.read().decode('utf-8')
        print(f"Health response ({time.time()-t0:.2f}s):", data)
except Exception as e:
    print(f"Health failed ({time.time()-t0:.2f}s):", e)
