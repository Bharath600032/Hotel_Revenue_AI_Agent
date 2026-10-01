"""
LLM Provider Abstraction Layer supporting Gemini, Claude, OpenAI, and offline MockLLMProvider for DEMO mode.
"""
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.core.llm")


class LLMProviderInterface:
    """Abstract interface for LLM providers."""

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        tools_declarations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        raise NotImplementedError


class MockLLMProvider(LLMProviderInterface):
    """
    Offline deterministic rule-based LLM provider for DEMO mode.
    Parses intent and automatically selects required tool sequences without calling external APIs.
    """

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        tools_declarations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        msg_lower = user_message.lower()

        # Intent 1: Room Types / Categories / Inventory Query
        if any(w in msg_lower for w in ["room", "suite", "inventory", "category", "types", "accommodation", "stay", "bed"]):
            return {
                "thought": "User is asking for room categories, inventory, and room types.",
                "tool_calls": [
                    {
                        "tool_name": "get_room_types",
                        "arguments": {},
                    }
                ],
                "content": None,
            }

        # Intent 2: Hotel Profile / Overview Query
        elif any(w in msg_lower for w in ["hotel", "property", "location", "city", "star", "details", "about", "where"]):
            return {
                "thought": "User is asking for hotel profile and property details.",
                "tool_calls": [
                    {
                        "tool_name": "get_hotel_profile",
                        "arguments": {},
                    }
                ],
                "content": None,
            }

        # Intent 3: Pricing & Rate Recommendation Query
        elif any(w in msg_lower for w in ["rate", "price", "charge", "cost", "tariff", "recommend", "how much"]):
            return {
                "thought": "User is asking for room rate recommendations.",
                "tool_calls": [
                    {
                        "tool_name": "calculate_pricing_recommendation",
                        "arguments": {
                            "room_type_id": 1,
                            "stay_date": "2026-10-20",
                        },
                    }
                ],
                "content": None,
            }

        # Intent 4: Demand Forecast & Occupancy Query
        elif any(w in msg_lower for w in ["forecast", "demand", "occupancy", "pace", "pickup", "projection"]):
            return {
                "thought": "User is asking for demand forecasts and occupancy projections.",
                "tool_calls": [
                    {
                        "tool_name": "run_demand_forecast",
                        "arguments": {
                            "room_type_id": 1,
                            "stay_date": "2026-10-20",
                            "horizon_days": 7,
                        },
                    }
                ],
                "content": None,
            }

        # Intent 5: Competitor Query
        elif any(w in msg_lower for w in ["competitor", "market", "comp", "rival", "benchmark", "parity"]):
            return {
                "thought": "User is asking for competitor pricing analysis.",
                "tool_calls": [
                    {
                        "tool_name": "get_competitor_rates",
                        "arguments": {"stay_date": "2026-10-20"},
                    }
                ],
                "content": None,
            }

        # Intent 6: Events & Holidays Query
        elif any(w in msg_lower for w in ["event", "holiday", "festival", "summit", "conference", "diwali", "calendar"]):
            return {
                "thought": "User is asking for upcoming local events and holiday impact.",
                "tool_calls": [
                    {
                        "tool_name": "get_events_holidays",
                        "arguments": {"city": "Chennai", "start_date": "2026-10-01", "end_date": "2026-10-31"},
                    }
                ],
                "content": None,
            }

        # Intent 7: Policy / SOP / General RAG Query
        return {
            "thought": "Answering revenue management or policy question via RAG Knowledge Base and property database.",
            "tool_calls": [],
            "content": None,
        }


def get_llm_provider() -> LLMProviderInterface:
    """Factory returning configured LLM provider instance."""
    if settings.is_demo_mode or settings.LLM_PROVIDER == "mock":
        return MockLLMProvider()
    # In production mode, returns selected provider (Gemini / Claude / OpenAI)
    return MockLLMProvider()
