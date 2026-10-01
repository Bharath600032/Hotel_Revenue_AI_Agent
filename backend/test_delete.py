import sys
from app.db.session import SessionLocal
from app.services.hotel_service import hotel_service
from app.models.hotel import Hotel

db = SessionLocal()
try:
    print("Testing delete hotel logic...")
    hotels = db.query(Hotel).all()
    print("Existing hotels:")
    for h in hotels:
        print(f"ID: {h.hotel_id}, Code: {h.hotel_code}, Name: {h.hotel_name}")

    # Find hotel with HTL_GOA or highest ID
    target = db.query(Hotel).filter(Hotel.hotel_code == "HTL_GOA").first()
    if target:
        print(f"Attempting to delete hotel: {target.hotel_id} ({target.hotel_name})")
        res = hotel_service.delete_hotel(db, target.hotel_id, 1)
        print(f"Delete result: {res}")
    else:
        print("HTL_GOA not found")
except Exception as e:
    import traceback
    print("ERROR OCCURRED:")
    traceback.print_exc()
finally:
    db.close()
