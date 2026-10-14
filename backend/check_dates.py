from app.db.session import SessionLocal
from app.models.ai import PriceRecommendations
from datetime import date

db = SessionLocal()
recs = db.query(PriceRecommendations).filter(PriceRecommendations.hotel_id == 4).all()
print(f"Total for hotel 4: {len(recs)}")
if recs:
    min_date = min(r.stay_date for r in recs)
    max_date = max(r.stay_date for r in recs)
    print(f"Date range: {min_date} to {max_date}")
    today = date.today()
    print(f"Today is: {today}")
    future_recs = [r for r in recs if r.stay_date >= today]
    print(f"Future or today recs count: {len(future_recs)}")
    past_recs = [r for r in recs if r.stay_date < today]
    print(f"Past recs count: {len(past_recs)}")
    pending_future = [r for r in future_recs if r.status == 'PENDING']
    print(f"Pending future count: {len(pending_future)}")
    published_future = [r for r in future_recs if r.status == 'PUBLISHED']
    print(f"Published future count: {len(published_future)}")
    for r in recs[:10]:
        print(f"ID={r.recommendation_id}, stay_date={r.stay_date}, status={r.status}, requires_approval={r.requires_approval}, rec_rate={r.recommended_rate}")
