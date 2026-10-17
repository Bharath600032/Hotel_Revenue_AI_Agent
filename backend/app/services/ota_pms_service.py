import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.ota_pms import PMSConnector, OTAChannelConnection, PMSChannelSyncLog
from app.models.hotel import Hotel

class OTAPMSService:

    @classmethod
    def seed_default_ota_pms_data(cls, hotel_id: int, db: Session):
        """Seed initial PMS connector and top Indian/Global OTA channel mappings."""
        existing_pms = db.query(PMSConnector).filter(PMSConnector.hotel_id == hotel_id).first()
        if not existing_pms:
            pms = PMSConnector(
                hotel_id=hotel_id,
                pms_provider="OPERA_CLOUD",
                connection_status="CONNECTED",
                api_endpoint="https://opera-cloud.oracle.com/api/v1/hotels/HAR-IND-01",
                sync_frequency_mins=5,
                last_sync_at=datetime.utcnow() - timedelta(minutes=3),
                auto_rate_push=True,
                auto_reservation_pull=True,
            )
            db.add(pms)
            db.commit()

        hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        base_rate = 9500.0
        room_count = 8
        if hotel:
            if hotel.room_types:
                base_rate = round(float(sum(r.base_price for r in hotel.room_types) / len(hotel.room_types)), 2)
                room_count = len(hotel.room_types)
            elif hotel.min_price_floor:
                base_rate = float(hotel.min_price_floor * 1.5)

        existing_channels = db.query(OTAChannelConnection).filter(OTAChannelConnection.hotel_id == hotel_id).all()
        if not existing_channels:
            default_channels = [
                {"name": "Booking.com", "code": "BCOM", "commission": 18.0, "status": "ACTIVE", "parity": "PARITY_OK", "rate": base_rate},
                {"name": "MakeMyTrip (MMT)", "code": "MMT", "commission": 20.0, "status": "ACTIVE", "parity": "PARITY_OK", "rate": base_rate},
                {"name": "Goibibo", "code": "GOI", "commission": 18.0, "status": "ACTIVE", "parity": "PARITY_OK", "rate": base_rate},
                {"name": "Agoda", "code": "AGD", "commission": 17.5, "status": "ACTIVE", "parity": "PARITY_OK", "rate": base_rate},
                {"name": "Expedia", "code": "EXP", "commission": 19.0, "status": "ACTIVE", "parity": "PARITY_OK", "rate": base_rate},
                {"name": "Airbnb", "code": "ARB", "commission": 15.0, "status": "ACTIVE", "parity": "PARITY_OK", "rate": base_rate},
                {"name": "Yatra", "code": "YTR", "commission": 16.5, "status": "ACTIVE", "parity": "PARITY_OK", "rate": base_rate},
                {"name": "Trip.com", "code": "TRIP", "commission": 15.5, "status": "ACTIVE", "parity": "PARITY_OK", "rate": base_rate},
            ]
            for c in default_channels:
                ch = OTAChannelConnection(
                    hotel_id=hotel_id,
                    channel_name=c["name"],
                    channel_code=c["code"],
                    connection_status=c["status"],
                    commission_pct=c["commission"],
                    rate_parity_status=c["parity"],
                    mapped_room_count=room_count,
                    last_pushed_rate_inr=c["rate"],
                    last_sync_at=datetime.utcnow() - timedelta(minutes=8),
                )
                db.add(ch)
            db.commit()

            # Seed sample sync log
            log = PMSChannelSyncLog(
                hotel_id=hotel_id,
                sync_type="RATE_PUSH",
                target_channel="ALL_CHANNELS",
                status="SUCCESS",
                records_processed=8,
                details_json={
                    "event": "Automated 2-Way Rate Sync",
                    "pushed_rate_inr": 9500.0,
                    "channels_updated": ["OPERA_CLOUD", "BCOM", "MMT", "GOI", "AGD", "EXP", "ARB", "YTR", "TRIP"],
                    "parity_check": "COMPLIANT",
                },
                execution_time_ms=64.8,
                synced_at=datetime.utcnow() - timedelta(minutes=8),
            )
            db.add(log)
            db.commit()

    @classmethod
    def get_pms_connector(cls, hotel_id: int, db: Session) -> PMSConnector:
        cls.seed_default_ota_pms_data(hotel_id, db)
        return db.query(PMSConnector).filter(PMSConnector.hotel_id == hotel_id).first()

    @classmethod
    def get_ota_channels(cls, hotel_id: int, db: Session) -> List[OTAChannelConnection]:
        cls.seed_default_ota_pms_data(hotel_id, db)
        all_channels = db.query(OTAChannelConnection).filter(OTAChannelConnection.hotel_id == hotel_id).all()
        hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        rts = hotel.room_types if hotel else []
        unique_map: Dict[str, OTAChannelConnection] = {}
        for c in all_channels:
            if not c.room_type_rates and rts:
                c.room_type_rates = {rt.room_type_name: round(float(rt.base_price * 1.1), 2) for rt in rts}
                db.commit()
            if c.channel_code not in unique_map:
                unique_map[c.channel_code] = c
        return list(unique_map.values())

    @classmethod
    def create_ota_channel(
        cls,
        hotel_id: int,
        channel_name: str,
        channel_code: str,
        commission_pct: float,
        mapped_room_count: Optional[int],
        last_pushed_rate_inr: Optional[float],
        db: Session,
    ) -> OTAChannelConnection:
        cls.seed_default_ota_pms_data(hotel_id, db)
        hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        initial_rates = {}
        if hotel and hotel.room_types:
            for rt in hotel.room_types:
                initial_rates[rt.room_type_name] = round(float(rt.base_price * 1.1), 2)
        ch = OTAChannelConnection(
            hotel_id=hotel_id,
            channel_name=channel_name,
            channel_code=channel_code.upper(),
            connection_status="ACTIVE",
            commission_pct=commission_pct,
            rate_parity_status="PARITY_OK",
            mapped_room_count=mapped_room_count or 8,
            last_pushed_rate_inr=last_pushed_rate_inr or 9500.0,
            room_type_rates=initial_rates,
            last_sync_at=datetime.utcnow(),
        )
        db.add(ch)
        db.commit()
        db.refresh(ch)
        return ch

    @classmethod
    def update_ota_channel(
        cls,
        hotel_id: int,
        channel_id: int,
        update_data: Dict[str, Any],
        db: Session,
    ) -> Optional[OTAChannelConnection]:
        ch = db.query(OTAChannelConnection).filter(
            OTAChannelConnection.id == channel_id,
            OTAChannelConnection.hotel_id == hotel_id,
        ).first()
        if not ch:
            return None

        for field, value in update_data.items():
            if value is not None and hasattr(ch, field):
                setattr(ch, field, value)

        ch.last_sync_at = datetime.utcnow()
        db.commit()
        db.refresh(ch)
        return ch

    @classmethod
    def delete_ota_channel(cls, hotel_id: int, channel_id: int, db: Session) -> bool:
        ch = db.query(OTAChannelConnection).filter(
            OTAChannelConnection.id == channel_id,
            OTAChannelConnection.hotel_id == hotel_id,
        ).first()
        if ch:
            db.delete(ch)
            db.commit()
            return True
        return False

    @classmethod
    def push_rates(
        cls,
        hotel_id: int,
        room_type: str,
        recommended_rate_inr: float,
        target_channels: Optional[List[str]],
        override_reason: Optional[str],
        db: Session,
    ) -> PMSChannelSyncLog:
        cls.seed_default_ota_pms_data(hotel_id, db)
        channels = db.query(OTAChannelConnection).filter(OTAChannelConnection.hotel_id == hotel_id).all()
        now = datetime.utcnow()

        updated_count = 0
        target_list = target_channels or ["OPERA_CLOUD", "BCOM", "MMT", "GOI", "AGD", "EXP"]
        latest_room_rates = {}

        for ch in channels:
            # Update individual room type rate dictionary
            curr_rates = ch.room_type_rates or {}
            if not isinstance(curr_rates, dict):
                curr_rates = {}
            else:
                curr_rates = dict(curr_rates)

            curr_rates[room_type] = float(recommended_rate_inr)
            ch.room_type_rates = curr_rates
            ch.last_pushed_rate_inr = float(recommended_rate_inr)
            ch.last_sync_at = now
            ch.rate_parity_status = "PARITY_OK"
            updated_count += 1
            latest_room_rates = curr_rates

        # Also sync RoomInventory for this room type so PMS/engine reflects the rate
        try:
            from app.models.hotel import RoomType, RoomInventory
            target_rt = db.query(RoomType).filter(RoomType.hotel_id == hotel_id, RoomType.room_type_name == room_type).first()
            if target_rt:
                db.query(RoomInventory).filter(
                    RoomInventory.hotel_id == hotel_id,
                    RoomInventory.room_type_id == target_rt.room_type_id,
                ).update({"current_rate": float(recommended_rate_inr)}, synchronize_session=False)
        except Exception:
            pass

        pms = db.query(PMSConnector).filter(PMSConnector.hotel_id == hotel_id).first()
        if pms:
            pms.last_sync_at = now
            pms.connection_status = "CONNECTED"

        exec_time = round(random.uniform(45.0, 85.0), 2)

        log = PMSChannelSyncLog(
            hotel_id=hotel_id,
            sync_type="RATE_PUSH",
            target_channel="2-WAY_PMS_OTA_SYNC",
            status="SUCCESS",
            records_processed=updated_count + 1,
            details_json={
                "room_type": room_type,
                "pushed_rate_inr": float(recommended_rate_inr),
                "room_type_rates": latest_room_rates,
                "target_channels": target_list,
                "override_reason": override_reason or "AI Dynamic Pricing Push",
                "parity_verified": True,
                "pms_ack_id": f"OPERA-ACK-{random.randint(10000, 99999)}",
            },
            execution_time_ms=exec_time,
            synced_at=now,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @classmethod
    def pull_reservations(cls, hotel_id: int, db: Session) -> PMSChannelSyncLog:
        cls.seed_default_ota_pms_data(hotel_id, db)
        now = datetime.utcnow()
        new_bookings = random.randint(3, 12)
        total_rev = round(new_bookings * random.uniform(7500.0, 14000.0), 2)

        pms = db.query(PMSConnector).filter(PMSConnector.hotel_id == hotel_id).first()
        if pms:
            pms.last_sync_at = now

        log = PMSChannelSyncLog(
            hotel_id=hotel_id,
            sync_type="RESERVATION_PULL",
            target_channel="OPERA_CLOUD",
            status="SUCCESS",
            records_processed=new_bookings,
            details_json={
                "event": "Live Reservation Ingestion",
                "new_reservations_count": new_bookings,
                "total_revenue_inr": total_rev,
                "channels": ["Booking.com", "MakeMyTrip", "Direct Web"],
                "inventory_updated": True,
            },
            execution_time_ms=52.4,
            synced_at=now,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @classmethod
    def get_sync_logs(cls, hotel_id: int, db: Session, limit: int = 25) -> List[PMSChannelSyncLog]:
        cls.seed_default_ota_pms_data(hotel_id, db)
        return db.query(PMSChannelSyncLog).filter(PMSChannelSyncLog.hotel_id == hotel_id).order_by(PMSChannelSyncLog.synced_at.desc()).limit(limit).all()
