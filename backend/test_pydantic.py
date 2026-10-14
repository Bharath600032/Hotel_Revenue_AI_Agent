from app.db.session import SessionLocal
from app.models.ai import PriceRecommendations
from app.schemas.pricing import PriceRecommendationResponse

db = SessionLocal()
recs = db.query(PriceRecommendations).filter(PriceRecommendations.hotel_id == 4).all()
print(f"Total recs for hotel 4: {len(recs)}")

errors = []
for i, r in enumerate(recs):
    try:
        # Check Pydantic validation
        PriceRecommendationResponse.model_validate(r)
    except Exception as e:
        errors.append((r.recommendation_id, str(e)))

print(f"Total Pydantic validation errors: {len(errors)}")
if errors:
    print("First 5 errors:")
    for eid, err in errors[:5]:
        print(f"ID {eid}: {err}")
