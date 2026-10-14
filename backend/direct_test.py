from app.db.session import SessionLocal
from app.models.user import User
from app.api.v1.pricing import list_recommendations
from app.api.v1.approval import list_pending_approvals
import asyncio

async def test():
    db = SessionLocal()
    user = db.query(User).filter(User.role == "Super Admin").first()
    print("User:", user.email, user.role)
    
    # Check approvals
    approvals = await list_pending_approvals(hotel_id=4, db=db, current_user=user)
    print("Approvals for hotel 4:", len(approvals))
    for a in approvals[:5]:
        print(" Approval item:", a.recommendation_id, a.stay_date, a.status, a.requires_approval)
        
    # Check recommendations
    recs = await list_recommendations(hotel_id=4, db=db, current_user=user)
    print("Recommendations for hotel 4:", len(recs))
    for r in recs[:5]:
        print(" Rec item:", r.recommendation_id, r.stay_date, r.status, r.requires_approval)

asyncio.run(test())
