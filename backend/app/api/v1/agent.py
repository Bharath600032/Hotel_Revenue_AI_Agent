"""
Agent Chat REST API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
    AgentRunResponse,
    AgentToolCallResponse,
)
from app.agents.orchestrator import single_agent_orchestrator
from app.models.ai import AgentRuns, AgentToolCalls
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/agent", tags=["AI Revenue Agent"])


@router.post("/chat", response_model=AgentChatResponse, status_code=status.HTTP_200_OK)
async def agent_chat(
    payload: AgentChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst"])),
):
    """
    Primary endpoint for natural language interaction with the Single Autonomous Revenue AI Agent.
    Executes intent parsing, tool selection, demand analytics, forecasting, and pricing guardrail checks.
    """
    if payload.hotel_id:
        verify_hotel_access(payload.hotel_id, current_user)

    result = single_agent_orchestrator.execute_request(
        db,
        user_id=current_user.user_id,
        hotel_id=payload.hotel_id,
        user_message=payload.message,
        session_id=payload.session_id,
    )

    return AgentChatResponse(
        answer=result["answer"],
        recommendation=result["recommendation"],
        factors=result["factors"],
        tools_used=result["tools_used"],
        requires_approval=result["requires_approval"],
        agent_run_id=result["agent_run_id"],
        execution_time_seconds=result["execution_time_seconds"],
    )


@router.get("/runs", response_model=List[AgentRunResponse])
async def list_agent_runs(
    hotel_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve history of agent execution runs."""
    query = db.query(AgentRuns)
    if hotel_id:
        verify_hotel_access(hotel_id, current_user)
        query = query.filter(AgentRuns.hotel_id == hotel_id)

    return query.order_by(AgentRuns.started_at.desc()).offset(skip).limit(limit).all()


@router.get("/runs/{agent_run_id}/calls", response_model=List[AgentToolCallResponse])
async def get_agent_tool_calls(
    agent_run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve detailed tool call execution trace for a specific agent run."""
    return (
        db.query(AgentToolCalls)
        .filter(AgentToolCalls.agent_run_id == agent_run_id)
        .order_by(AgentToolCalls.execution_time_ms)
        .all()
    )
