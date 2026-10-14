from app.db.session import SessionLocal
from app.models.user import User
from app.api.v1.pricing import recommend_price_batch
from app.schemas.pricing import BatchRecommendationRequest
from datetime import date
import asyncio

async def test():
    db = SessionLocal()
    user = db.query(User).filter(User.role == "Super Admin").first()
    payload = BatchRecommendationRequest(start_date=date.today(), days_count=7)
    res = await recommend_price_batch(hotel_id=4, payload=payload, db=db, current_user=user)
    print("Batch recs generated:", res.total_recommendations)

asyncio.run(test())
