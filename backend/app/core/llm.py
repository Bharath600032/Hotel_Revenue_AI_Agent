import re
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.core.llm")



MONTHS_NAME_MAP = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

MONTHS_KEY_MAP = {
    'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
    'apr': 4, 'april': 4, 'may': 5, 'june': 6, 'jun': 6, 'jul': 7, 'july': 7,
    'aug': 8, 'august': 8, 'sep': 9, 'sept': 9, 'september': 9, 'oct': 10, 'october': 10,
    'nov': 11, 'november': 11, 'dec': 12, 'december': 12
}


def parse_temporal_intent(text: str) -> Dict[str, Any]:
    """
    Extract accurate temporal entity, target month, target year, and scope (Holidays vs Events).
    """
    text_lower = text.lower()
    today = date.today()

    # 1. Determine Scope
    wants_hols = any(w in text_lower for w in [
        "holiday", "holidays", "observance", "observances", "public holiday", "bank holiday", "national holiday"
    ])
    wants_evs = any(w in text_lower for w in [
        "event", "events", "festival", "festivals", "summit", "conference", "concert", "expo", "exhibition", "carnival", "meeting"
    ])

    if wants_hols and not wants_evs:
        scope = "HOLIDAYS_ONLY"
    elif wants_evs and not wants_hols:
        scope = "EVENTS_ONLY"
    else:
        scope = "BOTH"

    # 2. Extract Year
    year_match = re.search(r'\b(202[4-9])\b', text_lower)
    target_year = int(year_match.group(1)) if year_match else 2026

    # 3. Extract Specific Day + Month
    m1 = re.search(r'\b(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]{3,9})\b', text_lower)
    m2 = re.search(r'\b([a-z]{3,9})\s+(\d{1,2})(?:st|nd|rd|th)?\b', text_lower)

    specific_day = None
    target_month = None

    if m1 and m1.group(2) in MONTHS_KEY_MAP:
        specific_day = int(m1.group(1))
        target_month = MONTHS_KEY_MAP[m1.group(2)]
    elif m2 and m2.group(1) in MONTHS_KEY_MAP:
        target_month = MONTHS_KEY_MAP[m2.group(1)]
        specific_day = int(m2.group(2))
    else:
        # Check for standalone month (e.g. "month of november", "in november", "november")
        for m_str, m_num in MONTHS_KEY_MAP.items():
            if re.search(rf'\b{m_str}\b', text_lower):
                target_month = m_num
                break

    # 4. Dates calculation
    if target_month and specific_day:
        try:
            exact_dt = date(target_year, target_month, specific_day).strftime("%Y-%m-%d")
            start_date = exact_dt
            end_date = exact_dt
        except ValueError:
            start_date = date(target_year, target_month, 1).strftime("%Y-%m-%d")
            end_date = (date(target_year, target_month + 1, 1) - timedelta(days=1)).strftime("%Y-%m-%d") if target_month < 12 else f"{target_year}-12-31"
    elif target_month:
        start_date = date(target_year, target_month, 1).strftime("%Y-%m-%d")
        if target_month < 12:
            end_date = (date(target_year, target_month + 1, 1) - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            end_date = f"{target_year}-12-31"
    elif "today" in text_lower:
        start_date = today.strftime("%Y-%m-%d")
        end_date = start_date
    elif "tomorrow" in text_lower:
        start_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = start_date
    elif "next week" in text_lower:
        start_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=14)).strftime("%Y-%m-%d")
    else:
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=60)).strftime("%Y-%m-%d")

    month_name = MONTHS_NAME_MAP.get(target_month) if target_month else None

    return {
        "scope": scope,
        "target_month": target_month,
        "target_month_name": month_name,
        "target_year": target_year,
        "specific_day": specific_day,
        "start_date": start_date,
        "end_date": end_date,
    }


def parse_date_from_text(text: str) -> str:
    """Extract stay date YYYY-MM-DD from user query text or default to 7 days from now."""
    temporal = parse_temporal_intent(text)
    if temporal.get("specific_day") and temporal.get("start_date"):
        return temporal["start_date"]
    if temporal.get("target_month") and temporal.get("start_date"):
        return temporal["start_date"]

    text_lower = text.lower()
    m_iso = re.search(r'\b(202[4-9])[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b', text)
    if m_iso:
        return f"{m_iso.group(1)}-{m_iso.group(2)}-{m_iso.group(3)}"

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
        temporal_intent = parse_temporal_intent(user_message)

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
                            "month": temporal_intent.get("target_month"),
                            "year": temporal_intent.get("target_year"),
                            "scope": temporal_intent.get("scope"),
                            "start_date": temporal_intent.get("start_date"),
                            "end_date": temporal_intent.get("end_date"),
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
            checkout_dt = (datetime.strptime(extracted_date, "%Y-%m-%d") + timedelta(days=3)).strftime("%Y-%m-%d")
            return {
                "thought": f"Evaluating group displacement and breakeven rate for stay starting {extracted_date}.",
                "tool_calls": [
                    {
                        "tool_name": "calculate_group_displacement",
                        "arguments": {
                            "group_name": "Corporate Group Request",
                            "checkin_date": extracted_date,
                            "checkout_date": checkout_dt,
                            "rooms_requested": 15,
                            "offered_rate": 6500.0,
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
                        "arguments": {"start_date": extracted_date, "days": 14},
                    }
                ],
                "content": None,
            }

        # Intent 10: TRevPAR & Non-Room Revenue Analytics Query
        elif any(w in msg_lower for w in ["trevpar", "nrevpar", "revpor", "ancillary", "non-room", "f&b", "spa", "banquet", "parking", "laundry"]):
            end_dt = (datetime.strptime(extracted_date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
            return {
                "thought": "Calculating TRevPAR, NRevPAR, RevPOR, and non-room ancillary revenue streams.",
                "tool_calls": [
                    {
                        "tool_name": "calculate_trevpar_analytics",
                        "arguments": {
                            "start_date": extracted_date,
                            "end_date": end_dt,
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

        # Intent 13: OTA / PMS Channel Manager & Two-Way Sync Query
        elif any(w in msg_lower for w in ["pms", "opera", "channel manager", "ota sync", "rate push", "sync status", "distribution channel"]):
            return {
                "thought": "Checking 2-way PMS and OTA channel connection status and live reservations.",
                "tool_calls": [
                    {
                        "tool_name": "pull_live_pms_reservations",
                        "arguments": {},
                    }
                ],
                "content": None,
            }

        # Intent 14: Multi-Agent Swarm Status & Consensus Query
        elif any(w in msg_lower for w in ["swarm", "multi-agent", "consensus", "macro", "micro", "negotiation", "swarm status"]):
            return {
                "thought": "Querying autonomous multi-agent swarm status and consensus state.",
                "tool_calls": [
                    {
                        "tool_name": "get_agent_swarm_status",
                        "arguments": {},
                    }
                ],
                "content": None,
            }

        # Intent 15: Policy / SOP / General RAG Query
        return {
            "thought": "Searching RAG Knowledge Base and system records.",
            "tool_calls": [],
            "content": None,
        }


class GeminiLLMProvider(LLMProviderInterface):
    """
    Live Google Gemini LLM Provider with automatic graceful fallback to MockLLMProvider.
    Attempts live function-calling and text generation; if offline, unauthenticated, or rate-limited,
    instantly delegates to MockLLMProvider without crashing.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.fallback = MockLLMProvider()

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        tools_declarations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt,
            )
            response = model.generate_content(user_message)
            candidate = response.candidates[0] if response.candidates else None

            tool_calls = []
            content = None
            if candidate and candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        fc = part.function_call
                        tool_calls.append({
                            "tool_name": fc.name,
                            "arguments": dict(fc.args) if fc.args else {},
                        })
                    elif hasattr(part, "text") and part.text:
                        content = part.text

            if tool_calls or content:
                return {
                    "thought": f"Gemini response generated via {self.model_name}.",
                    "tool_calls": tool_calls,
                    "content": content,
                }
            return self.fallback.generate_response(system_prompt, user_message, tools_declarations)
        except Exception as e:
            logger.warning("gemini_provider_error_falling_back_to_mock", error=str(e))
            return self.fallback.generate_response(system_prompt, user_message, tools_declarations)


def get_llm_provider() -> LLMProviderInterface:
    """Factory returning configured LLM provider instance with instant offline fallback."""
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        raw_key = (
            settings.GEMINI_API_KEY.get_secret_value()
            if hasattr(settings.GEMINI_API_KEY, "get_secret_value")
            else str(settings.GEMINI_API_KEY)
        )
        if raw_key and raw_key.strip() and not raw_key.strip().startswith("YOUR_"):
            return GeminiLLMProvider(api_key=raw_key.strip())

    return MockLLMProvider()
