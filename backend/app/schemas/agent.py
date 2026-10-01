"""
Pydantic v2 schemas for Agent Chat REST API endpoints and execution run traces.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    hotel_id: Optional[int] = Field(None, description="Target Hotel ID context")
    message: str = Field(..., min_length=2, description="User revenue management request or question")
    session_id: Optional[str] = Field(None, description="Optional multi-turn session ID")


class AgentChatResponse(BaseModel):
    answer: str
    recommendation: Optional[Dict[str, Any]] = None
    factors: List[str] = []
    tools_used: List[Dict[str, Any]] = []
    requires_approval: bool = False
    agent_run_id: str
    execution_time_seconds: float


class AgentToolCallResponse(BaseModel):
    tool_call_id: str
    tool_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]
    status: str
    execution_time_ms: float


class AgentRunResponse(BaseModel):
    agent_run_id: str
    user_id: int
    hotel_id: Optional[int]
    request: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    final_result: Optional[str]
