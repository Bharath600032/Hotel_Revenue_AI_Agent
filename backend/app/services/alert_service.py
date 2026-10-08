"""
Service layer for Option 4: Automated Multi-Channel Alerts & Notifications.
Handles notification rules, multi-channel payload formatting (Email, WhatsApp, Slack, In-App),
dispatch logging, and acknowledgment tracking.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.alerts import AlertNotificationRule, AlertNotificationLog
from app.models.hotel import Hotel
from app.schemas.alerts import AlertDispatchPayload, AlertRuleUpdate, ChannelTestRequest, ChannelTestResponse
from app.core.logging import get_logger

logger = get_logger("app.services.alert_service")


class AlertService:
    """Core domain logic for automated multi-channel revenue alerts."""

    def seed_default_rules_and_demo_alerts(self, db: Session, hotel_id: int) -> None:
        """Seed default notification rules and realistic demo alert history in INR (₹) for a property."""
        rule_count = db.query(AlertNotificationRule).filter(AlertNotificationRule.hotel_id == hotel_id).count()
        if rule_count == 0:
            logger.info("seeding_default_alert_rules", hotel_id=hotel_id)
            default_rules = [
                AlertNotificationRule(
                    hotel_id=hotel_id,
                    alert_type="COMPETITOR_UNDERCUT",
                    rule_name="Competitor Rate Undercut Spike",
                    description="Triggers when primary comp-set drops rates by > 10% or undercuts property ADR.",
                    threshold_value=10.0,
                    severity="CRITICAL",
                    is_enabled=True,
                    notify_email=True,
                    notify_whatsapp=True,
                    notify_slack=True,
                    notify_in_app=True,
                    recipients="gm@hotel.com, revenue@hotel.com",
                    slack_webhook_url="https://hooks.slack.com/services/T00/B00/XXXX",
                ),
                AlertNotificationRule(
                    hotel_id=hotel_id,
                    alert_type="PACE_SURGE",
                    rule_name="Unusual Pace & Occupancy Surge",
                    description="Notifies revenue team when 24h pickup exceeds 25 rooms or 20% pace surge.",
                    threshold_value=25.0,
                    severity="WARNING",
                    is_enabled=True,
                    notify_email=True,
                    notify_whatsapp=True,
                    notify_slack=True,
                    notify_in_app=True,
                    recipients="revenue@hotel.com",
                ),
                AlertNotificationRule(
                    hotel_id=hotel_id,
                    alert_type="DISPLACEMENT_THRESHOLD",
                    rule_name="Group Displacement Revenue Risk",
                    description="Alerts when proposed group displacement loss exceeds ₹50,000 net breakeven margin.",
                    threshold_value=50000.0,
                    severity="WARNING",
                    is_enabled=True,
                    notify_email=True,
                    notify_whatsapp=False,
                    notify_slack=True,
                    notify_in_app=True,
                    recipients="sales@hotel.com, revenue@hotel.com",
                ),
                AlertNotificationRule(
                    hotel_id=hotel_id,
                    alert_type="TREVPAR_BREACH",
                    rule_name="Non-Room Revenue Deficit Warning",
                    description="Fires when daily F&B/Spa/Ancillary TRevPAR drops > 15% below target budget.",
                    threshold_value=15.0,
                    severity="WARNING",
                    is_enabled=True,
                    notify_email=True,
                    notify_whatsapp=False,
                    notify_slack=True,
                    notify_in_app=True,
                    recipients="fb_mgr@hotel.com, revenue@hotel.com",
                ),
                AlertNotificationRule(
                    hotel_id=hotel_id,
                    alert_type="HIGH_DEMAND_EVENT",
                    rule_name="High-Demand Event Market Alert",
                    description="Notifies when local city event or holiday demand surge is detected.",
                    threshold_value=1.0,
                    severity="INFO",
                    is_enabled=True,
                    notify_email=False,
                    notify_whatsapp=True,
                    notify_slack=True,
                    notify_in_app=True,
                    recipients="reservations@hotel.com",
                ),
            ]
            db.add_all(default_rules)
            db.commit()

        # Seed demo alert log entries if table empty
        log_count = db.query(AlertNotificationLog).filter(AlertNotificationLog.hotel_id == hotel_id).count()
        if log_count == 0:
            logger.info("seeding_demo_alert_logs", hotel_id=hotel_id)
            hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
            hotel_name = hotel.hotel_name if hotel else f"Property #{hotel_id}"

            rules = db.query(AlertNotificationRule).filter(AlertNotificationRule.hotel_id == hotel_id).all()
            rule_map = {r.alert_type: r.rule_id for r in rules}

            demo_logs = [
                AlertNotificationLog(
                    hotel_id=hotel_id,
                    rule_id=rule_map.get("COMPETITOR_UNDERCUT"),
                    alert_type="COMPETITOR_UNDERCUT",
                    severity="CRITICAL",
                    title=f"🚨 Competitor Undercut Alert: Oberoi Grand dropped Deluxe room to ₹8,200/night",
                    message=f"Primary competitor Oberoi Grand slashed Executive rates by 14.5% (down to ₹8,200). Current property ADR is ₹9,500. Suggested action: Match or trigger dynamic package bundle.",
                    channel="MULTI_CHANNEL",
                    status="DISPATCHED",
                    recipient="gm@hotel.com, WhatsApp (+91-9876543210), Slack (#revenue-alerts)",
                    metadata_json={
                        "competitor_name": "Oberoi Grand",
                        "room_type": "Deluxe Executive",
                        "old_rate": 9600,
                        "new_rate": 8200,
                        "price_drop_pct": 14.5,
                        "recommended_adr": 8900,
                    },
                    created_at=datetime.utcnow(),
                ),
                AlertNotificationLog(
                    hotel_id=hotel_id,
                    rule_id=rule_map.get("PACE_SURGE"),
                    alert_type="PACE_SURGE",
                    severity="WARNING",
                    title="📈 Booking Pace Spike: +32 Rooms Picked Up for Oct 24-26 Weekend",
                    message="Sudden pickup surge detected! 32 Superior Comfort rooms booked in last 6 hours for upcoming weekend. Occupancy reached 88%. AI recommendation: Increase BAR rate by ₹750/night.",
                    channel="WHATSAPP",
                    status="ACKNOWLEDGED",
                    recipient="+91-9876543210 (Senior Revenue Manager)",
                    metadata_json={
                        "dates": "2026-10-24 to 2026-10-26",
                        "pickup_rooms": 32,
                        "current_occupancy_pct": 88.0,
                        "suggested_rate_increase": 750,
                    },
                    created_at=datetime.utcnow(),
                    acknowledged_at=datetime.utcnow(),
                    acknowledged_by="Senior Revenue Manager",
                ),
                AlertNotificationLog(
                    hotel_id=hotel_id,
                    rule_id=rule_map.get("DISPLACEMENT_THRESHOLD"),
                    alert_type="DISPLACEMENT_THRESHOLD",
                    severity="WARNING",
                    title="⚠️ Group Inquiry Displacement Loss: ₹74,500 Net Negative Impact",
                    message="Group lead from TechCorp (45 rooms for 3 nights at offered ₹5,800/night) produces ₹74,500 transient displacement deficit. Counter-offer floor rate calculated at ₹7,420/night.",
                    channel="SLACK",
                    status="DISPATCHED",
                    recipient="Slack (#group-sales-leads)",
                    metadata_json={
                        "group_name": "TechCorp Annual Summit",
                        "rooms_requested": 45,
                        "los_nights": 3,
                        "offered_rate": 5800,
                        "breakeven_floor_rate": 7420,
                        "net_displacement_impact": -74500,
                    },
                    created_at=datetime.utcnow(),
                ),
                AlertNotificationLog(
                    hotel_id=hotel_id,
                    rule_id=rule_map.get("TREVPAR_BREACH"),
                    alert_type="TREVPAR_BREACH",
                    severity="WARNING",
                    title="🍽️ Non-Room TRevPAR Deficit: Spa & Banquet revenue 18.2% below target",
                    message="Daily Non-Room revenue recorded ₹1,420 RevPOR vs ₹1,750 target. Dynamic Spa + Gourmet Dining Package recommended for weekend guests to boost TRevPAR.",
                    channel="EMAIL",
                    status="DISPATCHED",
                    recipient="fb_mgr@hotel.com, revenue@hotel.com",
                    metadata_json={
                        "actual_revpor": 1420,
                        "target_revpor": 1750,
                        "deficit_pct": 18.2,
                        "top_underperforming_category": "Spa & Wellness",
                    },
                    created_at=datetime.utcnow(),
                ),
                AlertNotificationLog(
                    hotel_id=hotel_id,
                    rule_id=rule_map.get("HIGH_DEMAND_EVENT"),
                    alert_type="HIGH_DEMAND_EVENT",
                    severity="INFO",
                    title="🎉 Event Demand Alert: International Tech Expo confirmed at City Convention Center",
                    message="Major city event registered for Nov 12-15 (Importance Level 4/5). Unconstrained transient demand estimated +40%. MLOS 2-night restriction recommended.",
                    channel="IN_APP",
                    status="DISPATCHED",
                    recipient="In-App Revenue Dashboard",
                    metadata_json={
                        "event_name": "International Tech Expo 2026",
                        "start_date": "2026-11-12",
                        "end_date": "2026-11-15",
                        "importance": 4,
                        "recommended_mlos": 2,
                    },
                    created_at=datetime.utcnow(),
                ),
            ]
            db.add_all(demo_logs)
            db.commit()

    def get_alert_rules(self, db: Session, hotel_id: int) -> List[AlertNotificationRule]:
        """Fetch all notification rules for a hotel."""
        self.seed_default_rules_and_demo_alerts(db, hotel_id)
        return (
            db.query(AlertNotificationRule)
            .filter(AlertNotificationRule.hotel_id == hotel_id)
            .order_by(AlertNotificationRule.rule_id.asc())
            .all()
        )

    def update_alert_rule(self, db: Session, hotel_id: int, rule_id: int, payload: AlertRuleUpdate) -> AlertNotificationRule:
        """Update notification rule configuration matrix."""
        rule = (
            db.query(AlertNotificationRule)
            .filter(AlertNotificationRule.hotel_id == hotel_id, AlertNotificationRule.rule_id == rule_id)
            .first()
        )
        if not rule:
            raise ValueError(f"Alert rule ID {rule_id} not found for hotel {hotel_id}")

        update_data = payload.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(rule, key, val)

        rule.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(rule)
        return rule

    def dispatch_alert(self, db: Session, payload: AlertDispatchPayload) -> AlertNotificationLog:
        """Dispatch automated multi-channel alert notification and record in log history."""
        self.seed_default_rules_and_demo_alerts(db, payload.hotel_id)

        # Match corresponding rule if available
        rule = (
            db.query(AlertNotificationRule)
            .filter(
                AlertNotificationRule.hotel_id == payload.hotel_id,
                AlertNotificationRule.alert_type == payload.alert_type,
            )
            .first()
        )

        channels = payload.channels or ["EMAIL", "WHATSAPP", "SLACK", "IN_APP"]
        channel_str = ", ".join(channels) if len(channels) > 1 else (channels[0] if channels else "MULTI_CHANNEL")

        log = AlertNotificationLog(
            hotel_id=payload.hotel_id,
            rule_id=rule.rule_id if rule else None,
            alert_type=payload.alert_type,
            severity=payload.severity or (rule.severity if rule else "WARNING"),
            title=payload.title,
            message=payload.message,
            channel=channel_str,
            status="DISPATCHED",
            recipient=payload.recipient or (rule.recipients if rule else "revenue@hotel.com"),
            metadata_json=payload.metadata_json or {},
            created_at=datetime.utcnow(),
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        logger.info(
            "multi_channel_alert_dispatched",
            log_id=log.log_id,
            hotel_id=payload.hotel_id,
            channels=channel_str,
            severity=log.severity,
        )
        return log

    def get_alert_logs(
        self,
        db: Session,
        hotel_id: int,
        status_filter: Optional[str] = None,
        channel_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
    ) -> List[AlertNotificationLog]:
        """Fetch alert dispatch logs with optional filters."""
        self.seed_default_rules_and_demo_alerts(db, hotel_id)

        query = db.query(AlertNotificationLog).filter(AlertNotificationLog.hotel_id == hotel_id)

        if status_filter and status_filter.upper() != "ALL":
            query = query.filter(AlertNotificationLog.status == status_filter.upper())
        if severity_filter and severity_filter.upper() != "ALL":
            query = query.filter(AlertNotificationLog.severity == severity_filter.upper())
        if channel_filter and channel_filter.upper() != "ALL":
            query = query.filter(AlertNotificationLog.channel.contains(channel_filter.upper()))

        return query.order_by(AlertNotificationLog.created_at.desc()).all()

    def acknowledge_alert(self, db: Session, hotel_id: int, log_id: int, acknowledged_by: str) -> AlertNotificationLog:
        """Mark an alert log entry as ACKNOWLEDGED."""
        log = (
            db.query(AlertNotificationLog)
            .filter(AlertNotificationLog.hotel_id == hotel_id, AlertNotificationLog.log_id == log_id)
            .first()
        )
        if not log:
            raise ValueError(f"Alert log ID {log_id} not found for hotel {hotel_id}")

        log.status = "ACKNOWLEDGED"
        log.acknowledged_at = datetime.utcnow()
        log.acknowledged_by = acknowledged_by
        db.commit()
        db.refresh(log)
        return log

    def test_channel_dispatch(self, db: Session, hotel_id: int, request: ChannelTestRequest) -> ChannelTestResponse:
        """Simulate real-time multi-channel delivery payload generation."""
        hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        hotel_name = hotel.hotel_name if hotel else f"Property #{hotel_id}"

        channel = request.channel.upper()
        sample_type = request.sample_type or "COMPETITOR_UNDERCUT"
        dest = request.target_destination or ("revenue@hotel.com" if channel == "EMAIL" else "+91-9876543210")

        if channel == "SLACK":
            formatted_payload = (
                f"{{\n"
                f'  "text": "🚨 [HIGH ALARM] Competitor Rate Undercut Alert for {hotel_name}",\n'
                f'  "blocks": [\n'
                f'    {{\n'
                f'      "type": "section",\n'
                f'      "text": {{\n'
                f'        "type": "mrkdwn",\n'
                f'        "text": "*🚨 Competitor Undercut Alert*\\n*Property:* {hotel_name}\\n*Competitor:* Oberoi Grand dropped rates by 14.5% to *₹8,200/night*.\\n*Current BAR:* ₹9,500."\n'
                f'      }}\n'
                f'    }},\n'
                f'    {{\n'
                f'      "type": "actions",\n'
                f'      "elements": [\n'
                f'        {{ "type": "button", "text": {{ "type": "plain_text", "text": "Approve Rate Adjustment (₹8,900)" }}, "style": "primary" }},\n'
                f'        {{ "type": "button", "text": {{ "type": "plain_text", "text": "Acknowledge Alert" }} }}\n'
                f'      ]\n'
                f'    }}\n'
                f'  ]\n'
                f"}}"
            )
        elif channel == "WHATSAPP":
            formatted_payload = (
                f"📱 *HOTEL REVENUE AI ALERT*\n"
                f"----------------------------\n"
                f"🏨 Property: {hotel_name}\n"
                f"⚡ Alert: Competitor Price Drop\n"
                f"📉 Oberoi Grand is now ₹8,200 (₹1,300 lower than your ₹9,500 BAR).\n"
                f"💡 AI Suggestion: Update BAR to ₹8,900 or activate dynamic breakfast package.\n"
                f"🔗 Tap to respond: https://app.revenueagent.ai/pricing"
            )
        elif channel == "EMAIL":
            formatted_payload = (
                f"Subject: [CRITICAL ALERT] Competitor Price Undercut Detected at {hotel_name}\n\n"
                f"Dear Revenue Team,\n\n"
                f"Our Autonomous Revenue AI Agent has detected a significant rate drop by your primary competitor:\n\n"
                f"• Property: {hotel_name}\n"
                f"• Competitor Name: Oberoi Grand\n"
                f"• New Rate: ₹8,200 / night (14.5% decrease)\n"
                f"• Current Property BAR: ₹9,500 / night\n\n"
                f"Recommended Instant Action: Align rate to ₹8,900 or enable MLOS 2-night restriction.\n\n"
                f"Best regards,\n"
                f"Autonomous Hotel Revenue AI Agent"
            )
        else:  # IN_APP
            formatted_payload = (
                f"Title: 🔔 Market Anomaly Alert - Competitor Undercut\n"
                f"Body: Oberoi Grand slashed rates to ₹8,200/night. Click to review dynamic pricing recommendations in INR (₹)."
            )

        return ChannelTestResponse(
            success=True,
            channel=channel,
            recipient=dest,
            formatted_payload=formatted_payload,
            dispatched_at=datetime.utcnow(),
        )


alert_service = AlertService()
