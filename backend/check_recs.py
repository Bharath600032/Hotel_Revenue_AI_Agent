from app.db.session import SessionLocal
from app.models.ai import PriceRecommendations
from app.models.hotel import Hotel, RoomType
from collections import Counter

db = SessionLocal()
hotels = db.query(Hotel).all()
print("Hotels in DB:")
for h in hotels:
    r_count = db.query(PriceRecommendations).filter(PriceRecommendations.hotel_id == h.hotel_id).count()
    p_count = db.query(PriceRecommendations).filter(PriceRecommendations.hotel_id == h.hotel_id, PriceRecommendations.status == "PENDING").count()
    pub_count = db.query(PriceRecommendations).filter(PriceRecommendations.hotel_id == h.hotel_id, PriceRecommendations.status == "PUBLISHED").count()
    app_count = db.query(PriceRecommendations).filter(PriceRecommendations.hotel_id == h.hotel_id, PriceRecommendations.status == "APPROVED").count()
    statuses = [r.status for r in db.query(PriceRecommendations).filter(PriceRecommendations.hotel_id == h.hotel_id).all()]
    print(f"Hotel {h.hotel_id}: {h.hotel_name} -> Total: {r_count}, Statuses: {Counter(statuses)}")
