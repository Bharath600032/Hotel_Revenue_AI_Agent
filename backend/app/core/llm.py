import re
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.core.llm")


def parse_date_from_text(text: str) -> str:
    """Extract stay date YYYY-MM-DD from user query text or default to 7 days from now."""
    text_lower = text.lower()

    # ISO date match (2026-10-10 or 2026/10/10)
    m_iso = re.search(r'\b(202[4-9])[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b', text)
    if m_iso:
        return f"{m_iso.group(1)}-{m_iso.group(2)}-{m_iso.group(3)}"

    months_map = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
        'apr': 4, 'april': 4, 'may': 5, 'june': 6, 'jun': 6, 'jul': 7, 'july': 7,
        'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10,
        'nov': 11, 'november': 11, 'dec': 12, 'december': 12
    }

    # Pattern 1: 10th oct 2026 or 10 october 2026 or 10 oct
    m1 = re.search(r'\b(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]{3,9})\s*(202[4-9])?\b', text_lower)
    if m1 and m1.group(2) in months_map:
        day = int(m1.group(1))
        month = months_map[m1.group(2)]
        year = int(m1.group(3)) if m1.group(3) else 2026
        try:
            return date(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Pattern 2: oct 10 2026 or october 20
    m2 = re.search(r'\b([a-z]{3,9})\s+(\d{1,2})(?:st|nd|rd|th)?\s*(202[4-9])?\b', text_lower)
    if m2 and m2.group(1) in months_map:
        month = months_map[m2.group(1)]
        day = int(m2.group(2))
        year = int(m2.group(3)) if m2.group(3) else 2026
        try:
            return date(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            pass

    today = date.today()
    if "today" in text_lower:
        return today.strftime("%Y-%m-%d")
    elif "tomorrow" in text_lower:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "next week" in text_lower:
        return (today + timedelta(days=7)).strftime("%Y-%m-%d")

    return (today + timedelta(days=7)).strftime("%Y-%m-%d")


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
        extracted_date = parse_date_from_text(user_message)

        # Detect follow-up list requests (e.g., "provide me the list?", "the list?", "give me the list")
        is_followup_list = any(w in msg_lower for w in [
            "provide me the list", "give me the list", "show me the list", "what is the list",
            "the list?", "the list", "list them", "give list", "show list", "tell me the list",
            "which are they", "what are they", "who are they", "which ones", "names please"
        ]) or (("list" in msg_lower or "name" in msg_lower or "who" in msg_lower) and len(msg_lower.split()) <= 5)

        # Extract only the actual recent conversation history turns from system_prompt
        recent_chat_history = ""
        if "RECENT CONVERSATION HISTORY:" in system_prompt:
            parts = system_prompt.split("RECENT CONVERSATION HISTORY:")
            if len(parts) > 1:
                recent_chat_history = parts[1].split("HOTEL OPERATIONAL MEMORY:")[0].lower()

        # Intent 1: Events, Festivals, Holidays & Dates Query (High Priority)
        if any(w in msg_lower for w in [
            "event", "events", "holiday", "holidays", "festival", "festivals",
            "summit", "conference", "diwali", "navratri", "golu", "pongal", "calendar",
            "weather", "rain", "temp", "expo", "exhibition", "carnival", "concert"
        ]) or any(k in msg_lower for k in ["what date", "when is", "dates of", "dates for", "date is"]) or (
            is_followup_list and any(k in recent_chat_history for k in ["event", "festival", "holiday", "summit", "conference"])
        ):
            return {
                "thought": f"Fetching local events and holiday dates for query: '{user_message}'.",
                "tool_calls": [
                    {
                        "tool_name": "get_events_holidays",
                        "arguments": {
                            "query": user_message,
                            "start_date": extracted_date,
                            "end_date": extracted_date,
                        },
                    }
                ],
                "content": None,
            }

        # Intent 2: Total Rooms / Hotel Capacity Query
        elif any(w in msg_lower for w in [
            "total room", "total rooms", "how many room", "how many rooms",
            "hotel capacity", "room capacity", "property capacity", "number of room", "number of rooms"
        ]):
            return {
                "thought": "Fetching property profile and total room capacity.",
                "tool_calls": [
                    {
                        "tool_name": "get_hotel_profile",
                        "arguments": {},
                    }
                ],
                "content": None,
            }

        # Intent 3: Room Types / Categories / Inventory / Baseline Rate Query
        elif any(w in msg_lower for w in [
            "room type", "room types", "room category", "room categories",
            "room name", "room names", "inventory", "suite", "suites",
            "baseline rate", "baseline rates", "base rate", "base rates"
        ]) or (
            is_followup_list and any(k in recent_chat_history for k in ["room", "suite", "inventory", "category", "baseline"])
        ):
            return {
                "thought": "Fetching room categories, base prices, and master inventory allocations.",
                "tool_calls": [
                    {
                        "tool_name": "get_room_types",
                        "arguments": {},
                    }
                ],
                "content": None,
            }

        # Intent 4: Competitor Benchmark & Competitor Names Query
        elif any(w in msg_lower for w in [
            "competitor", "competitors", "market median", "comp set", "rival", "rivals",
            "benchmark", "parity", "rate gap", "price gap", "who are competitors", "competitor names",
            "competitors name", "list out competitors", "list out competitor", "list competitors",
            "list competitor", "competitor list", "competitors list"
        ]) or (
            is_followup_list and any(k in recent_chat_history for k in ["competitor", "rival", "comp", "orange"])
        ):
            return {
                "thought": "Analyzing competitor set, names, and market rates.",
                "tool_calls": [
                    {
                        "tool_name": "get_competitor_rates",
                        "arguments": {"stay_date": extracted_date},
                    }
                ],
                "content": None,
            }

        # Intent 5: Demand Forecast & Occupancy Query
        elif any(w in msg_lower for w in ["forecast", "occupancy", "pickup", "pace", "projection", "predict demand"]):
            return {
                "thought": "Running demand forecasting model pipeline.",
                "tool_calls": [
                    {
                        "tool_name": "run_demand_forecast",
                        "arguments": {
                            "stay_date": extracted_date,
                            "horizon_days": 7,
                        },
                    }
                ],
                "content": None,
            }

        # Intent 6: Pricing & Rate Recommendation / Fix Price Query
        elif any(w in msg_lower for w in ["rate", "price", "charge", "cost", "tariff", "recommend", "how much", "fix", "optimi"]):
            return {
                "thought": f"Calculating pricing recommendation for stay date {extracted_date}.",
                "tool_calls": [
                    {
                        "tool_name": "calculate_pricing_recommendation",
                        "arguments": {
                            "stay_date": extracted_date,
                        },
                    }
                ],
                "content": None,
            }

        # Intent 7: RevPAR / ADR Revenue Financial Analytics Query
        elif any(w in msg_lower for w in ["revpar", "adr", "revenue", "financial", "metrics", "summary", "performance"]):
            return {
                "thought": "Calculating RevPAR and ADR revenue metrics.",
                "tool_calls": [
                    {
                        "tool_name": "calculate_revpar",
                        "arguments": {"start_date": extracted_date, "end_date": extracted_date},
                    }
                ],
                "content": None,
            }

        # Intent 8: Group Displacement Query
        elif any(w in msg_lower for w in ["group", "displacement", "block", "corporate rate", "breakeven", "counter offer", "accept group"]):
            return {
                "thought": f"Evaluating group displacement and breakeven rate for stay starting {extracted_date}.",
                "tool_calls": [
                    {
                        "tool_name": "calculate_group_displacement",
                        "arguments": {
                            "start_date": extracted_date,
                            "end_date": (datetime.strptime(extracted_date, "%Y-%m-%d") + timedelta(days=3)).strftime("%Y-%m-%d"),
                            "rooms_requested": 15,
                            "offered_rate": 180.0,
                        },
                    }
                ],
                "content": None,
            }

        # Intent 9: Length of Stay (LOS / MLOS / CTA / CTD) Restrictions Query
        elif any(w in msg_lower for w in ["los", "mlos", "minimum stay", "length of stay", "closed to arrival", "cta", "ctd"]):
            return {
                "thought": "Fetching length of stay restrictions and dynamic MLOS recommendations.",
                "tool_calls": [
                    {
                        "tool_name": "get_los_restrictions",
                        "arguments": {"start_date": extracted_date, "end_date": extracted_date},
                    }
                ],
                "content": None,
            }

        # Intent 10: TRevPAR & Non-Room Revenue Analytics Query
        elif any(w in msg_lower for w in ["trevpar", "nrevpar", "revpor", "ancillary", "non-room", "f&b", "spa", "banquet", "parking", "laundry"]):
            return {
                "thought": "Calculating TRevPAR, NRevPAR, RevPOR, and non-room ancillary revenue streams.",
                "tool_calls": [
                    {
                        "tool_name": "calculate_trevpar_analytics",
                        "arguments": {
                            "start_date": extracted_date,
                            "end_date": extracted_date,
                        },
                    }
                ],
                "content": None,
            }

        # Intent 11: Hotel Profile / Overview / Amenities Query
        elif any(w in msg_lower for w in ["hotel profile", "property profile", "property details", "hotel overview", "amenity", "amenities", "about hotel"]):
            return {
                "thought": "Fetching property profile and amenities.",
                "tool_calls": [
                    {
                        "tool_name": "get_hotel_profile",
                        "arguments": {},
                    }
                ],
                "content": None,
            }

        # Intent 11: Ancillary Upsell Packages & Bundle Yield Query
        elif any(w in msg_lower for w in ["package", "bundle", "upsell", "addon", "add-on", "voucher"]):
            return {
                "thought": "Generating AI dynamic non-room revenue upsell packages and bundle yield optimization.",
                "tool_calls": [
                    {
                        "tool_name": "generate_ancillary_upsell_packages",
                        "arguments": {},
                    }
                ],
                "content": None,
            }

        # Intent 12: Multi-Channel Alerts & Notification Query
        elif any(w in msg_lower for w in ["alert", "notification", "whatsapp", "slack", "email alert", "undercut alert", "broadcast"]):
            return {
                "thought": "Checking active multi-channel alerts and notification logs.",
                "tool_calls": [
                    {
                        "tool_name": "get_active_alerts_and_rule_config",
                        "arguments": {"status_filter": "ALL", "channel_filter": "ALL"},
                    }
                ],
                "content": None,
            }

        # Intent 13: Policy / SOP / General RAG Query
        return {
            "thought": "Searching RAG Knowledge Base and system records.",
            "tool_calls": [],
            "content": None,
        }


def get_llm_provider() -> LLMProviderInterface:
    """Factory returning configured LLM provider instance."""
    return MockLLMProvider()
