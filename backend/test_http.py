import urllib.request
import json

# 1. Login to get token
login_data = json.dumps({"email": "admin@hotelrevenue.ai", "password": "AdminPass123!"}).encode('utf-8')
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/auth/login",
    data=login_data,
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req, timeout=5) as response:
        res_json = json.loads(response.read().decode('utf-8'))
        token = res_json.get("access_token")
        print("Login SUCCESS, token received:", token[:20], "...")
except Exception as e:
    print("Login FAILED:", e)
    token = None

if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test recommendations for hotel 4
    req_recs = urllib.request.Request("http://127.0.0.1:8000/api/v1/hotels/4/pricing/recommendations", headers=headers)
    try:
        with urllib.request.urlopen(req_recs, timeout=5) as res:
            recs = json.loads(res.read().decode('utf-8'))
            print("Recommendations count:", len(recs))
    except Exception as e:
        print("Recommendations request FAILED:", e)
        if hasattr(e, 'read'):
            print("Error body:", e.read().decode('utf-8'))

    # 3. Test approvals for hotel 4
    req_app = urllib.request.Request("http://127.0.0.1:8000/api/v1/hotels/4/approvals/pending", headers=headers)
    try:
        with urllib.request.urlopen(req_app, timeout=5) as res:
            approvals = json.loads(res.read().decode('utf-8'))
            print("Approvals count:", len(approvals))
    except Exception as e:
        print("Approvals request FAILED:", e)
        if hasattr(e, 'read'):
            print("Error body:", e.read().decode('utf-8'))
