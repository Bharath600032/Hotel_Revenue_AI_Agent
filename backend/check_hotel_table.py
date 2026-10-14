from app.db.session import SessionLocal
from app.models.hotel import Hotel

db = SessionLocal()
hotels = db.query(Hotel).all()
for h in hotels:
    print(f"Hotel id={h.hotel_id}, code={getattr(h, 'code', None)}, hotel_code={getattr(h, 'hotel_code', None)}, name={h.hotel_name}")
    for col in h.__table__.columns:
        print(f"   {col.name}: {getattr(h, col.name)}")
