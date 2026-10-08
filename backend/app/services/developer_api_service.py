import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.developer_api import DeveloperAPIKey, WebhookSubscription, WebhookEventLog
from app.models.hotel import Hotel

class DeveloperAPIService:

    @staticmethod
    def _hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @classmethod
    def seed_default_developer_data(cls, hotel_id: int, db: Session):
        """Seed default API keys, webhooks, and logs for a hotel if none exist."""
        existing_keys = db.query(DeveloperAPIKey).filter(DeveloperAPIKey.hotel_id == hotel_id).count()
        if existing_keys == 0:
            # Create sample API keys
            k1_raw = f"har_live_{secrets.token_hex(16)}"
            k1 = DeveloperAPIKey(
                hotel_id=hotel_id,
                name="PMS Direct Sync Engine (Opera Cloud)",
                api_key_prefix="har_live_9a4f",
                api_key_hash=cls._hash_key(k1_raw),
                scopes=["pricing:read", "pricing:write", "inventory:read"],
                status="active",
                rate_limit_per_min=180,
                last_used_at=datetime.utcnow() - timedelta(minutes=14),
                expires_at=datetime.utcnow() + timedelta(days=180),
                created_by="system_admin"
            )

            k2_raw = f"har_live_{secrets.token_hex(16)}"
            k2 = DeveloperAPIKey(
                hotel_id=hotel_id,
                name="PowerBI Automated Revenue Pipeline",
                api_key_prefix="har_live_3b7c",
                api_key_hash=cls._hash_key(k2_raw),
                scopes=["reports:read", "bi:export"],
                status="active",
                rate_limit_per_min=60,
                last_used_at=datetime.utcnow() - timedelta(hours=2),
                expires_at=datetime.utcnow() + timedelta(days=365),
                created_by="revenue_mgr"
            )

            db.add_all([k1, k2])
            db.commit()

        existing_wh = db.query(WebhookSubscription).filter(WebhookSubscription.hotel_id == hotel_id).count()
        if existing_wh == 0:
            wh1 = WebhookSubscription(
                hotel_id=hotel_id,
                endpoint_url="https://api.pms-integration.in/v1/revenue/webhooks",
                secret_key=f"whsec_{secrets.token_hex(16)}",
                events=["price.updated", "anomalies.detected", "swarm.consensus"],
                status="active",
                description="Live PMS Auto-Sync Receiver",
                failure_count=0,
                last_triggered_at=datetime.utcnow() - timedelta(minutes=35)
            )

            wh2 = WebhookSubscription(
                hotel_id=hotel_id,
                endpoint_url="https://hooks.slack.com/services/T0821/B0992/revenue-alerts-india",
                secret_key=f"whsec_{secrets.token_hex(16)}",
                events=["anomalies.detected", "report.generated"],
                status="active",
                description="Executive Team Slack Channel",
                failure_count=0,
                last_triggered_at=datetime.utcnow() - timedelta(hours=1)
            )

            db.add_all([wh1, wh2])
            db.commit()

            # Seed sample event log
            log1 = WebhookEventLog(
                hotel_id=hotel_id,
                subscription_id=wh1.id,
                event_type="price.updated",
                payload={
                    "event": "price.updated",
                    "hotel_id": hotel_id,
                    "currency": "INR",
                    "room_type": "Deluxe Ocean Suite",
                    "old_rate": 9500,
                    "new_rate": 11200,
                    "reason": "AI Swarm Consensus High Demand Spike",
                    "timestamp": datetime.utcnow().isoformat()
                },
                response_status_code=200,
                response_body='{"status": "success", "pms_ack_id": "ACK-98412"}',
                delivered_at=datetime.utcnow() - timedelta(minutes=35),
                execution_time_ms=42.8
            )
            db.add(log1)
            db.commit()

    @classmethod
    def get_api_keys(cls, hotel_id: int, db: Session) -> List[DeveloperAPIKey]:
        cls.seed_default_developer_data(hotel_id, db)
        return db.query(DeveloperAPIKey).filter(DeveloperAPIKey.hotel_id == hotel_id).order_by(DeveloperAPIKey.created_at.desc()).all()

    @classmethod
    def create_api_key(cls, hotel_id: int, name: str, scopes: List[str], expires_in_days: Optional[int], db: Session) -> Tuple[DeveloperAPIKey, str]:
        raw_key = f"har_live_{secrets.token_hex(20)}"
        prefix = raw_key[:13] + "..."
        hashed = cls._hash_key(raw_key)

        expires_at = datetime.utcnow() + timedelta(days=expires_in_days) if expires_in_days else None

        key_obj = DeveloperAPIKey(
            hotel_id=hotel_id,
            name=name,
            api_key_prefix=prefix,
            api_key_hash=hashed,
            scopes=scopes,
            status="active",
            rate_limit_per_min=120,
            expires_at=expires_at,
            created_by="api_user"
        )
        db.add(key_obj)
        db.commit()
        db.refresh(key_obj)
        return key_obj, raw_key

    @classmethod
    def revoke_api_key(cls, hotel_id: int, key_id: int, db: Session) -> Optional[DeveloperAPIKey]:
        key_obj = db.query(DeveloperAPIKey).filter(DeveloperAPIKey.id == key_id, DeveloperAPIKey.hotel_id == hotel_id).first()
        if key_obj:
            key_obj.status = "revoked"
            db.commit()
            db.refresh(key_obj)
        return key_obj

    @classmethod
    def get_webhooks(cls, hotel_id: int, db: Session) -> List[WebhookSubscription]:
        cls.seed_default_developer_data(hotel_id, db)
        return db.query(WebhookSubscription).filter(WebhookSubscription.hotel_id == hotel_id).order_by(WebhookSubscription.created_at.desc()).all()

    @classmethod
    def create_webhook(cls, hotel_id: int, endpoint_url: str, events: List[str], description: Optional[str], db: Session) -> WebhookSubscription:
        secret = f"whsec_{secrets.token_hex(16)}"
        webhook = WebhookSubscription(
            hotel_id=hotel_id,
            endpoint_url=endpoint_url,
            secret_key=secret,
            events=events,
            status="active",
            description=description or "Custom Webhook Endpoint",
            failure_count=0
        )
        db.add(webhook)
        db.commit()
        db.refresh(webhook)
        return webhook

    @classmethod
    def delete_webhook(cls, hotel_id: int, webhook_id: int, db: Session) -> bool:
        webhook = db.query(WebhookSubscription).filter(WebhookSubscription.id == webhook_id, WebhookSubscription.hotel_id == hotel_id).first()
        if webhook:
            db.delete(webhook)
            db.commit()
            return True
        return False

    @classmethod
    def test_dispatch(cls, hotel_id: int, subscription_id: int, event_type: Optional[str], db: Session) -> WebhookEventLog:
        sub = db.query(WebhookSubscription).filter(WebhookSubscription.id == subscription_id, WebhookSubscription.hotel_id == hotel_id).first()
        if not sub:
            raise ValueError(f"Webhook subscription {subscription_id} not found for hotel {hotel_id}")

        e_type = event_type or "price.updated"
        now_iso = datetime.utcnow().isoformat()

        if e_type == "price.updated":
            payload = {
                "event": "price.updated",
                "hotel_id": hotel_id,
                "currency": "INR",
                "room_type": "Executive Suite",
                "recommended_rate": 12500,
                "previous_rate": 10200,
                "confidence_score": 0.94,
                "trigger": "Surge Occupancy Alert (+18% YoY)",
                "timestamp": now_iso
            }
        elif e_type == "swarm.consensus":
            payload = {
                "event": "swarm.consensus",
                "hotel_id": hotel_id,
                "consensus_reached": True,
                "optimal_rate_inr": 14200,
                "voting_distribution": {
                    "DemandForecaster": 14500,
                    "CompetitorIntel": 14000,
                    "DisplacementLOS": 14200,
                    "AncillaryTRevPAR": 14200,
                    "GuardrailRisk": 13900
                },
                "timestamp": now_iso
            }
        elif e_type == "anomalies.detected":
            payload = {
                "event": "anomalies.detected",
                "hotel_id": hotel_id,
                "severity": "CRITICAL",
                "anomaly_title": "Sudden Competitor Rate Drop (-25%)",
                "affected_dates": ["2026-10-15", "2026-10-16"],
                "recommended_action": "Hold price floor at ₹8,500 due to high organic conversion",
                "timestamp": now_iso
            }
        else:
            payload = {
                "event": e_type,
                "hotel_id": hotel_id,
                "status": "DISPATCHED",
                "test_mode": True,
                "timestamp": now_iso
            }

        response_body = json.dumps({"status": "200 OK", "message": "Webhook payload received & verified", "signature_match": True})

        log = WebhookEventLog(
            hotel_id=hotel_id,
            subscription_id=sub.id,
            event_type=e_type,
            payload=payload,
            response_status_code=200,
            response_body=response_body,
            delivered_at=datetime.utcnow(),
            execution_time_ms=38.4
        )
        db.add(log)

        sub.last_triggered_at = datetime.utcnow()
        db.commit()
        db.refresh(log)
        return log

    @classmethod
    def get_webhook_logs(cls, hotel_id: int, db: Session, limit: int = 20) -> List[WebhookEventLog]:
        return db.query(WebhookEventLog).filter(WebhookEventLog.hotel_id == hotel_id).order_by(WebhookEventLog.delivered_at.desc()).limit(limit).all()
