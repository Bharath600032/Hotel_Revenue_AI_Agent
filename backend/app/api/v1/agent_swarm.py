"""
API routes for Option 6: Multi-Agent Collaborative Swarm Architecture.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent_swarm import (
    SwarmEvaluateRequest,
    SwarmConsensusResponse,
    SwarmMemberResponse,
)
from app.services.agent_swarm_service import agent_swarm_service
from app.api.deps import verify_hotel_access, get_current_user
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger("app.api.v1.agent_swarm")

router = APIRouter(prefix="/hotels/{hotel_id}/swarm", tags=["Multi-Agent Swarm Architecture"])


@router.get("/members", response_model=List[SwarmMemberResponse])
def get_swarm_members(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve status and metrics for all 5 specialized sub-agents in the swarm."""
    verify_hotel_access(hotel_id, current_user, db)
    return agent_swarm_service.get_swarm_members(db, hotel_id)


@router.get("/sessions", response_model=List[SwarmConsensusResponse])
def get_swarm_sessions(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch multi-agent consensus session decision logs for a property."""
    verify_hotel_access(hotel_id, current_user, db)
    return agent_swarm_service.get_swarm_sessions(db, hotel_id)


@router.post("/evaluate", response_model=SwarmConsensusResponse)
def evaluate_swarm_consensus(
    hotel_id: int,
    req: SwarmEvaluateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run a live multi-agent collaborative swarm consensus evaluation across Pricing, Demand, Compete, Displacement, and TRevPAR sub-agents."""
    verify_hotel_access(hotel_id, current_user, db)
    if req.hotel_id != hotel_id:
        req.hotel_id = hotel_id
    return agent_swarm_service.evaluate_swarm_consensus(db, req)
