from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import create_access_token

db = SessionLocal()
admin = db.query(User).filter(User.email == "admin@hotelrevenue.ai").first()
if not admin:
    admin = db.query(User).first()

token = create_access_token({"sub": admin.email, "role": admin.role})
client = TestClient(app)
headers = {"Authorization": f"Bearer {token}"}

print(f"Testing with User: {admin.email}, Role: {admin.role}")

# Test 1: Approvals pending for hotel 4
resp1 = client.get("/api/v1/hotels/4/approvals/pending", headers=headers)
print(f"Pending Approvals Status: {resp1.status_code}")
data1 = resp1.json() if resp1.status_code == 200 else resp1.text
print(f"Pending Approvals Count: {len(data1) if isinstance(data1, list) else data1}")

# Test 2: Recommendations for hotel 4
resp2 = client.get("/api/v1/hotels/4/pricing/recommendations", headers=headers)
print(f"Recommendations Status: {resp2.status_code}")
data2 = resp2.json() if resp2.status_code == 200 else resp2.text
print(f"Recommendations Count: {len(data2) if isinstance(data2, list) else data2}")
if isinstance(data2, list) and len(data2) > 0:
    print(f"Sample recommendation: id={data2[0].get('recommendation_id')}, stay_date={data2[0].get('stay_date')}, status={data2[0].get('status')}")
