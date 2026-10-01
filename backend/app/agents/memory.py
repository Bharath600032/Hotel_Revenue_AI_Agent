"""
Agent Memory Manager implementing Short-term Conversation Memory, Hotel Operational Memory, and Knowledge Base Context.
"""
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.hotel import Hotel, RoomType
from app.models.ai import AgentRuns
from app.core.logging import get_logger

logger = get_logger("app.agents.memory")


class AgentMemoryManager:
    """Manages 3-tier memory context for the AI Agent."""

    def __init__(self):
        self._short_term_sessions: Dict[str, List[Dict[str, str]]] = {}

    # --- Tier 1: Short-Term Conversation Memory ---
    def add_conversation_turn(self, session_id: str, role: str, content: str) -> None:
        """Append user or assistant message to session short-term memory (capped at last 10 turns)."""
        if session_id not in self._short_term_sessions:
            self._short_term_sessions[session_id] = []
        self._short_term_sessions[session_id].append({"role": role, "content": content})
        # Truncate to keep at most 10 recent messages
        if len(self._short_term_sessions[session_id]) > 10:
            self._short_term_sessions[session_id] = self._short_term_sessions[session_id][-10:]

    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieve recent conversation history turns."""
        return self._short_term_sessions.get(session_id, [])

    def clear_short_term_memory(self, session_id: str) -> None:
        """Reset short-term conversation session memory."""
        self._short_term_sessions.pop(session_id, None)

    # --- Tier 2: Hotel-Specific Operational Memory ---
    def get_hotel_operational_memory(self, db: Session, hotel_id: int) -> Dict[str, Any]:
        """
        Fetch persistent hotel operational guidelines, pricing strategy floor limits, and management policies.
        """
        hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if not hotel:
            return {
                "preferred_price_floor": 1000.0,
                "preferred_competitive_position": "MODERATE_PREMIUM",
                "max_daily_change_pct": 20.0,
                "approval_threshold_pct": 10.0,
            }

        # Query recent agent runs for property-level context overrides
        past_runs = (
            db.query(AgentRuns)
            .filter(AgentRuns.hotel_id == hotel_id, AgentRuns.status == "COMPLETED")
            .order_by(AgentRuns.started_at.desc())
            .limit(5)
            .all()
        )

        return {
            "hotel_id": hotel_id,
            "hotel_name": hotel.hotel_name,
            "city": hotel.city,
            "currency": hotel.currency,
            "preferred_price_floor": 1000.0,
            "preferred_competitive_position": "MODERATE_PREMIUM",
            "max_daily_change_pct": 20.0,
            "approval_threshold_pct": 10.0,
            "past_decisions_count": len(past_runs),
        }

    # --- Tier 3: Strategy Knowledge Memory Summary ---
    def build_memory_context_prompt(
        self, db: Session, session_id: str, hotel_id: Optional[int]
    ) -> str:
        """
        Synthesize short-term conversation history and operational memory into an LLM context block.
        """
        context_parts = []

        # Short-term history
        history = self.get_conversation_history(session_id)
        if history:
            context_parts.append("RECENT CONVERSATION HISTORY:")
            for msg in history[-4:]:
                context_parts.append(f"[{msg['role'].upper()}]: {msg['content']}")

        # Operational memory
        if hotel_id:
            op_mem = self.get_hotel_operational_memory(db, hotel_id)
            context_parts.append("\nHOTEL OPERATIONAL MEMORY:")
            context_parts.append(f"• Property: {op_mem.get('hotel_name')} ({op_mem.get('city')})")
            context_parts.append(f"• Target Positioning: {op_mem.get('preferred_competitive_position')}")
            context_parts.append(f"• Price Floor Limit: ₹{op_mem.get('preferred_price_floor'):,.0f}")
            context_parts.append(f"• Max Daily Price Variation Limit: ±{op_mem.get('max_daily_change_pct')}%")

        return "\n".join(context_parts)


agent_memory_manager = AgentMemoryManager()
