"""
Pydantic schemas for Option 6: Multi-Agent Collaborative Swarm Architecture.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class AgentVote(BaseModel):
    agent_code: str
    agent_name: str
    role_description: str
    vote_decision: str  # APPROVE, REJECT, COUNTER_PROPOSE, SNOOZE
    proposed_value: Any  # e.g., ₹8,900 or 2-night MLOS or ₹7,500
    confidence_pct: float
    reasoning: str


class SwarmEvaluateRequest(BaseModel):
    hotel_id: int
    topic: str = "DYNAMIC_PRICING_AND_RESTRICTION_CONSENSUS"
    target_date: Optional[str] = None
    context_notes: Optional[str] = None


class SwarmMemberResponse(BaseModel):
    agent_id: int
    hotel_id: int
    agent_code: str
    agent_name: str
    role_description: str
    specialization: str
    status: str
    voting_weight: float
    accuracy_rating_pct: float
    total_proposals: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SwarmConsensusResponse(BaseModel):
    session_id: int
    hotel_id: int
    consensus_topic: str
    proposed_action: str
    overall_confidence_pct: float
    conflict_detected: bool
    status: str
    agent_votes: Optional[List[Dict[str, Any]]] = Field(default=[], alias="agent_votes_json")
    agent_votes_json: Optional[List[Dict[str, Any]]] = None
    synthesis_rationale: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

