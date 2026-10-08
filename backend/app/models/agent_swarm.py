"""
SQLAlchemy ORM models for Option 6: Multi-Agent Collaborative Swarm Architecture.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class AgentSwarmMember(Base):
    """Configuration and state registry for specialized AI sub-agents in the swarm."""
    __tablename__ = "agent_swarm_members"

    agent_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id", ondelete="CASCADE"), nullable=False, index=True)

    agent_code = Column(String(50), nullable=False)  # PRICING_AGENT, DEMAND_AGENT, COMPETE_AGENT, DISPLACEMENT_AGENT, TREVPAR_AGENT
    agent_name = Column(String(100), nullable=False)
    role_description = Column(Text, nullable=False)
    specialization = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, ANALYZING, IDLE
    voting_weight = Column(Float, nullable=False, default=1.0)
    accuracy_rating_pct = Column(Float, nullable=False, default=94.5)
    total_proposals = Column(Integer, nullable=False, default=42)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    hotel = relationship("Hotel", backref="swarm_members")


class SwarmSessionLog(Base):
    """Log of multi-agent collaborative swarm consensus evaluations and decisions."""
    __tablename__ = "swarm_session_logs"

    session_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id", ondelete="CASCADE"), nullable=False, index=True)

    consensus_topic = Column(String(200), nullable=False)
    proposed_action = Column(String(100), nullable=False)  # BAR_RATE_ADJUSTMENT, MLOS_RESTRICTION_TRIGGER, GROUP_COUNTER_OFFER, ANCILLARY_BUNDLE
    overall_confidence_pct = Column(Float, nullable=False, default=92.0)
    conflict_detected = Column(Boolean, nullable=False, default=False)
    status = Column(String(30), nullable=False, default="EXECUTED")  # EXECUTED, PENDING_APPROVAL, REJECTED

    agent_votes_json = Column(JSON, nullable=False)  # List of individual agent votes, confidence %, and rationales
    synthesis_rationale = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    hotel = relationship("Hotel", backref="swarm_sessions")
