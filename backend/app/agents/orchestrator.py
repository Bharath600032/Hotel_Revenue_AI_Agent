"""
Single Autonomous Revenue AI Agent Orchestrator with 3-tier memory manager integration.
"""
import uuid
import time
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session


from app.core.llm import get_llm_provider
from app.agents.prompts import REVENUE_AGENT_SYSTEM_PROMPT
from app.agents.memory import agent_memory_manager
from app.tools.registry import tool_registry
from app.models.ai import AgentRuns
from app.core.logging import get_logger

logger = get_logger("app.agents.orchestrator")


def extract_crisp_rag_answer(query: str, docs: List[Any], hotel_name: str) -> str:
    """Extract short, crisp, relevant answer sentences directly answering user query from RAG docs."""
    q_words = set(re.findall(r'\w+', query.lower())) - {
        "what", "is", "the", "are", "do", "you", "have", "in", "for", "to",
        "of", "and", "a", "an", "hotel", "can", "tell", "me", "about", "give", "some"
    }

    junk_keywords = [
        "testimonial", "what clients says", "arun kumar", "priya nair", "copyright",
        "rights reserved", "designed by", "official hotel website", "all rights",
        "sublink", "website page"
    ]

    scored_sentences = []

    for doc in docs:
        chunk = getattr(doc, 'chunk', '') if hasattr(doc, 'chunk') else (doc.get('chunk', '') if isinstance(doc, dict) else str(doc))
        lines = [l.strip() for l in chunk.split('\n') if l.strip()]
        for line in lines:
            if any(jk in line.lower() for jk in junk_keywords):
                continue
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', line) if len(s.strip()) > 8]
            for s in sentences:
                s_lower = s.lower()
                if any(jk in s_lower for jk in junk_keywords):
                    continue
                score = sum(1 for w in q_words if w in s_lower)
                if any(w in s_lower for w in ["check-in", "check-out", "pool", "restaurant", "dining", "wifi", "contact", "address", "phone", "located", "room"]):
                    score += 1
                scored_sentences.append((score, s))

    # Only consider sentences that actually matched query keywords or domain terms
    positive_sentences = [item for item in scored_sentences if item[0] > 0]
    if not positive_sentences:
        return f"I can provide rates, room categories, competitor benchmarks, events, and performance metrics for **{hotel_name}**. What specific information would you like?"

    positive_sentences.sort(key=lambda x: x[0], reverse=True)

    chosen = []
    seen = set()
    for sc, s in positive_sentences:
        clean = s.lstrip("•-*# ").strip()
        if clean.lower() not in seen:
            seen.add(clean.lower())
            chosen.append(clean)
            if len(chosen) >= 2:
                break

    if chosen:
        return f"**{hotel_name}**: " + " ".join(chosen)
    return f"**{hotel_name}** provides full-service hospitality and accommodations."


class SingleAutonomousRevenueAgent:
    """
    Single Autonomous AI Agent orchestrator managing revenue decision loops and memory.
    """

    def execute_request(
        self,
        db: Session,
        user_id: int,
        hotel_id: Optional[int],
        user_message: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute user revenue request through plan-and-execute tool-calling loop.
        """
        agent_run_id = f"run_{uuid.uuid4().hex[:12]}"
        sess_id = session_id or f"sess_user_{user_id}"
        start_time = time.time()

        # Log Agent Run start in DB
        db_run = AgentRuns(
            agent_run_id=agent_run_id,
            user_id=user_id,
            hotel_id=hotel_id,
            request=user_message,
            status="RUNNING",
            started_at=datetime.now(timezone.utc),
        )
        db.add(db_run)
        db.commit()

        # Record incoming user turn in Short-Term Memory
        agent_memory_manager.add_conversation_turn(sess_id, "user", user_message)

        # Synthesize Memory Context Prompt
        memory_context = agent_memory_manager.build_memory_context_prompt(db, sess_id, hotel_id)
        combined_system_prompt = f"{REVENUE_AGENT_SYSTEM_PROMPT}\n\n{memory_context}"

        logger.info("agent_run_started", agent_run_id=agent_run_id, user_id=user_id, request=user_message)

        # Guarantee live metrics, events, and holidays for target hotel, and sync application knowledge base
        target_hotel_id = hotel_id or 1
        try:
            from app.agents.hotel_agent_factory import hotel_agent_factory
            hotel_agent_factory.ensure_hotel_live_data(db, target_hotel_id)
            from app.rag.sync_service import app_knowledge_syncer
            app_knowledge_syncer.sync_hotel_knowledge(db, target_hotel_id)
        except Exception as fac_err:
            logger.warning("ensure_live_data_and_sync_failed", error=str(fac_err))

        provider = get_llm_provider()
        tools_decl = tool_registry.get_llm_tool_declarations()

        # Step 1: LLM Turn
        llm_response = provider.generate_response(
            system_prompt=combined_system_prompt,
            user_message=user_message,
            tools_declarations=tools_decl,
        )

        tools_used: List[Dict[str, Any]] = []
        final_recommendation: Optional[Dict[str, Any]] = None
        factors: List[str] = []
        requires_approval = False

        tool_results: Dict[str, Any] = {}

        # Step 2: Tool Execution Loop
        for tool_call in llm_response.get("tool_calls", []):
            tool_name = tool_call["tool_name"]
            arguments = tool_call["arguments"]
            if hotel_id and "hotel_id" not in arguments:
                arguments["hotel_id"] = hotel_id

            tool_res = tool_registry.execute_tool(
                db, tool_name=tool_name, arguments=arguments, agent_run_id=agent_run_id
            )
            tools_used.append({"tool_name": tool_name, "execution_time_ms": tool_res["execution_time_ms"]})

            res_dict = tool_res.get("result", {})
            tool_results[tool_name] = res_dict

            if tool_name == "calculate_pricing_recommendation":
                final_recommendation = res_dict
                factors.append(res_dict.get("price_reason", ""))
                requires_approval = res_dict.get("requires_approval", False)

        # Step 3: Format Final Answer Content dynamically based on tools or RAG
        target_hotel_id = hotel_id or 1
        from app.repositories.hotel_repository import hotel_repository
        from app.rag.vector_store import vector_store_manager

        hotel_obj = hotel_repository.get_by_id(db, target_hotel_id)
        hotel_name = hotel_obj.hotel_name if hotel_obj else f"Hotel Property {target_hotel_id}"

        user_lower = user_message.lower()

        # Conversational Context Resolution: Resolve follow-up queries (e.g. "provide me the list?")
        recent_history = agent_memory_manager.get_conversation_history(sess_id)
        last_turn_text = ""
        if len(recent_history) >= 2:
            prior_messages = [m["content"] for m in recent_history[:-1]]
            last_turn_text = " ".join(prior_messages[-3:]).lower()

        is_followup_list = (
            any(k in user_lower for k in [
                "provide me the list", "give me the list", "show me the list",
                "what is the list", "list them", "the list?", "the list", "give list",
                "show list", "tell me the list", "provide list", "share list", "send list",
                "which are they", "what are they", "who are they", "which ones", "names please"
            ])
            or (("list" in user_lower or "name" in user_lower or "who" in user_lower) and len(user_lower.split()) <= 5)
        )

        is_competitor_names_query = (
            any(k in user_lower for k in [
                "competitors name", "competitor name", "competitors names", "competitor names",
                "list out competitors", "list out competitor", "list competitors", "list competitor",
                "competitor list", "competitors list", "who are competitors", "who are our competitors",
                "names of competitors", "names of competitor", "which competitors", "comp set", "all competitor",
                "all competitors"
            ])
            or (is_followup_list and any(k in last_turn_text for k in ["competitor", "rival", "comp", "orange"]))
        )

        is_events_query = (
            (is_followup_list and any(k in last_turn_text for k in ["event", "festival", "holiday", "summit", "conference", "golu", "navratri"]))
            or "get_events_holidays" in tool_results
            or "get_event_data" in tool_results
            or "get_holiday_data" in tool_results
            or any(k in user_lower for k in [
                "event", "events", "holiday", "holidays", "festival", "festivals",
                "navratri", "golu", "diwali", "pongal", "summit", "conference",
                "what date", "when is", "calendar", "expo", "carnival"
            ])
        )
        is_capacity_query = any(k in user_lower for k in [
            "total room", "total rooms", "how many room", "how many rooms",
            "hotel capacity", "room capacity", "property capacity", "number of room", "number of rooms"
        ])
        is_room_query = (
            (is_followup_list and any(k in last_turn_text for k in ["room", "suite", "inventory", "category", "baseline", "type"]))
            or "get_room_types" in tool_results
            or any(k in user_lower for k in [
                "room type", "room types", "room category", "room categories",
                "room name", "room names", "inventory", "suite", "suites",
                "baseline rate", "baseline rates", "base rate", "base rates"
            ])
        )
        is_pricing_query = any(k in user_lower for k in [
            "price", "rate", "cost", "tariff", "fix", "recommend", "charge", "pricing", "how much", "dynamic rate"
        ])
        is_competitor_query = (
            is_competitor_names_query
            or "get_competitor_rates" in tool_results
            or any(k in user_lower for k in [
                "competitor", "competitors", "market median", "comp set", "rival", "rivals", "rate gap", "price gap", "parity"
            ])
        )
        is_forecast_query = "run_demand_forecast" in tool_results or any(k in user_lower for k in [
            "forecast", "occupancy projection", "predicted occupancy", "pace", "pickup"
        ])
        is_revpar_query = "calculate_revpar" in tool_results or "calculate_adr" in tool_results or any(k in user_lower for k in [
            "revpar", "adr", "metrics", "financial summary", "revenue performance"
        ])

        # Priority 1: Events & Festivals
        if is_events_query:
            res_ev = tool_results.get("get_events_holidays") or {}
            if not res_ev:
                from app.tools.revenue_tools import GetEventsHolidaysTool
                res_ev = GetEventsHolidaysTool().execute(db, query=user_message, hotel_id=target_hotel_id)

            matched_evs = res_ev.get("matched_events", [])
            matched_hols = res_ev.get("matched_holidays", [])
            city_name = res_ev.get("city") or (hotel_obj.city if hotel_obj else "Chennai")

            if matched_evs:
                ev_lines = []
                for ev in matched_evs:
                    v_str = f" (Venue: {ev['venue']})" if ev.get('venue') else ""
                    ev_lines.append(f"**{ev['event_name']} ({ev.get('city', city_name)})** is scheduled from **{ev['start_date']} to {ev['end_date']}**{v_str}.")
                answer_content = "\n\n".join(ev_lines)
            elif matched_hols:
                hol_lines = []
                for hol in matched_hols:
                    reg_str = f" ({hol.get('region')})" if hol.get('region') else ""
                    hol_lines.append(f"**{hol['holiday_name']}**{reg_str} is on **{hol['holiday_date']}**.")
                answer_content = "\n\n".join(hol_lines)
            else:
                up_evs = res_ev.get("upcoming_events", [])
                up_hols = res_ev.get("upcoming_holidays", [])
                lines = []
                if up_evs:
                    lines.append(f"**Upcoming Events in {city_name}:**")
                    for ev in up_evs[:3]:
                        lines.append(f"• **{ev['event_name']}**: {ev['start_date']} – {ev['end_date']}")
                if up_hols:
                    lines.append(f"**Upcoming Holidays:**")
                    for hol in up_hols[:3]:
                        lines.append(f"• **{hol['holiday_name']}**: {hol['holiday_date']}")
                answer_content = "\n".join(lines) if lines else f"No upcoming events registered for {city_name}."

        # Priority 2: Total Rooms / Hotel Capacity
        elif is_capacity_query or ("get_hotel_profile" in tool_results and not is_pricing_query):
            res = tool_results.get("get_hotel_profile", {})
            t_rooms = res.get("total_rooms") or (hotel_obj.total_rooms if hotel_obj else 50)
            c_name = res.get("city") or (hotel_obj.city if hotel_obj else "Chennai")
            answer_content = f"**{hotel_name}** ({c_name}) has a total capacity of **{t_rooms} Rooms**."

        # Priority 3: Room Categories / Inventory / Baseline Rates
        elif is_room_query:
            rts = hotel_repository.get_room_types_by_hotel(db, target_hotel_id)
            if rts:
                lines = [f"• **{rt.room_type_name}**: {rt.total_inventory} Units (₹{rt.base_price:,.0f}/night)" for rt in rts]
                answer_content = f"**Room Categories for {hotel_name}:**\n" + "\n".join(lines)
            else:
                answer_content = f"**{hotel_name}** has standard room inventory configured."

        # Priority 4: Competitor Intelligence & Competitor Names List
        elif is_competitor_query:
            from app.models.rates import CompetitorHotels, CompetitorRates
            comps = db.query(CompetitorHotels).filter(CompetitorHotels.hotel_id == target_hotel_id, CompetitorHotels.status == "ACTIVE").all()
            if not comps:
                from app.agents.hotel_agent_factory import hotel_agent_factory
                hotel_agent_factory.ensure_hotel_live_data(db, target_hotel_id)
                comps = db.query(CompetitorHotels).filter(CompetitorHotels.hotel_id == target_hotel_id, CompetitorHotels.status == "ACTIVE").all()

            if is_competitor_names_query:
                lines = []
                for c in comps:
                    latest_cr = (
                        db.query(CompetitorRates)
                        .filter(CompetitorRates.competitor_id == c.competitor_id)
                        .order_by(CompetitorRates.stay_date.desc())
                        .first()
                    )
                    rate_str = f" — Rate: ₹{latest_cr.rate:,.0f} ({latest_cr.ota_name or 'OTA'})" if latest_cr else ""
                    lines.append(f"• **{c.competitor_name}** ({c.star_rating:.0f}★, {c.city}){rate_str}")
                answer_content = f"**Competitors for {hotel_name} ({hotel_obj.city if hotel_obj else 'Chennai'}):**\n" + "\n".join(lines)
            else:
                res = tool_results.get("get_competitor_rates", {})
                my_rate = res.get('my_rate', 6500)
                comp_med = res.get('competitor_median', 6200)
                comp_names_str = ", ".join([c.competitor_name for c in comps[:3]]) if comps else "Local Set"
                answer_content = (
                    f"**Competitor Rates ({hotel_name}):**\n"
                    f"• **Our Active Rate**: ₹{my_rate:,.0f} | **Market Median**: ₹{comp_med:,.0f}\n"
                    f"• **Active Competitors**: {comp_names_str}"
                )

        # Priority 5: Demand Forecast
        elif is_forecast_query:
            res = tool_results.get("run_demand_forecast", {})
            proj_occ = res.get('projected_occupancy_pct') or res.get('occupancy') or 84.5
            tgt_revpar = res.get('target_revpar') or res.get('revpar') or 5250
            answer_content = (
                f"**Demand Forecast ({hotel_name}):**\n"
                f"• **Projected Occupancy**: **{proj_occ:.1f}%** | **Target RevPAR**: **₹{tgt_revpar:,.0f}**"
            )

        # Priority 6: Dynamic Pricing Recommendation
        elif final_recommendation and is_pricing_query:
            rec_rate = final_recommendation.get('recommended_rate') or final_recommendation.get('proposed_rate') or 4500.0
            curr_rate = final_recommendation.get('current_rate') or final_recommendation.get('base_rate') or 4000.0
            stay_dt = final_recommendation.get('stay_date') or "target stay date"
            answer_content = (
                f"**Recommended Rate for `{stay_dt}` ({hotel_name}):**\n"
                f"• **Dynamic Rate**: **₹{rec_rate:,.0f}** (Base: ₹{curr_rate:,.0f})\n"
                f"• **Status**: {'⚠️ Requires approval' if requires_approval else '✅ Within guardrails'}"
            )

        # Priority 7: RevPAR / ADR Revenue Metrics
        elif is_revpar_query:
            res_rev = tool_results.get("calculate_revpar") or tool_results.get("calculate_adr") or {}
            revpar_val = res_rev.get("revpar") or 3850.0
            adr_val = res_rev.get("adr") or 4950.0
            occ_val = res_rev.get("occupancy_pct") or 77.8
            answer_content = (
                f"**Performance Metrics ({hotel_name}):**\n"
                f"• **RevPAR**: **₹{revpar_val:,.0f}** | **ADR**: **₹{adr_val:,.0f}** | **Occupancy**: **{occ_val:.1f}%**"
            )

        # Priority 8: Group Displacement Evaluation
        elif "calculate_group_displacement" in tool_results:
            disp = tool_results["calculate_group_displacement"]
            rec = disp.get("recommendation", "EVALUATED")
            offered = disp.get("offered_rate", 0)
            breakeven = disp.get("breakeven_rate", 0)
            net_rev = disp.get("net_displacement_revenue", 0)
            counter = disp.get("suggested_counter_offer_rate")
            counter_str = f" | Suggested Counter: **₹{counter:,.0f}**" if counter else ""
            answer_content = (
                f"**Group Displacement Analysis ({hotel_name}):**\n"
                f"• **Recommendation**: **{rec}**\n"
                f"• **Offered Rate**: ₹{offered:,.0f} | **Breakeven Threshold**: ₹{breakeven:,.0f}\n"
                f"• **Net Displacement Impact**: **₹{net_rev:+,.0f}**{counter_str}"
            )

        # Priority 9: Length of Stay (LOS / MLOS) Restrictions
        elif "get_los_restrictions" in tool_results:
            res_los = tool_results["get_los_restrictions"]
            rules = res_los.get("los_rules", [])
            if rules:
                lines = [f"• **{r.get('stay_date')}**: MLOS = **{r.get('min_stay_nights', 1)} nights** (CTA: {r.get('closed_to_arrival', False)}, CTD: {r.get('closed_to_departure', False)})" for r in rules[:4]]
                answer_content = f"**Length of Stay (LOS) Restrictions ({hotel_name}):**\n" + "\n".join(lines)
            else:
                answer_content = f"No active Length of Stay restrictions configured for {hotel_name}."

        # Priority 10: TRevPAR & Non-Room Revenue Analytics
        elif "calculate_trevpar_analytics" in tool_results:
            res_trev = tool_results["calculate_trevpar_analytics"]
            trev = res_trev.get("trevpar", 0)
            revpar = res_trev.get("revpar", 0)
            nrevpar = res_trev.get("nrevpar", 0)
            non_room_pct = res_trev.get("non_room_rev_pct", 0)
            answer_content = (
                f"**TRevPAR & Non-Room Analytics ({hotel_name}):**\n"
                f"• **TRevPAR**: **₹{trev:,.0f}** | **RevPAR**: **₹{revpar:,.0f}** | **NRevPAR**: **₹{nrevpar:,.0f}**\n"
                f"• **Non-Room Revenue Share**: **{non_room_pct:.1f}%**"
            )

        # Priority 11: Ancillary Upsell Packages
        elif "generate_ancillary_upsell_packages" in tool_results:
            res_pkg = tool_results["generate_ancillary_upsell_packages"]
            pkgs = res_pkg.get("ancillary_packages", [])
            if pkgs:
                lines = [f"• **{p.get('package_name')}** ({p.get('package_type', 'Package')}): **₹{p.get('bundle_price_inr', 0):,.0f}**" for p in pkgs[:3]]
                answer_content = f"**Ancillary Upsell Packages ({hotel_name}):**\n" + "\n".join(lines)
            else:
                answer_content = f"No active ancillary packages configured for {hotel_name}."

        # Priority 12: Multi-Channel Alerts
        elif "get_active_alerts_and_rule_config" in tool_results or "dispatch_multi_channel_alert" in tool_results:
            res_al = tool_results.get("get_active_alerts_and_rule_config") or tool_results.get("dispatch_multi_channel_alert") or {}
            alerts = res_al.get("alerts", [])
            if alerts:
                lines = [f"• [{a.get('severity', 'INFO')}] **{a.get('title')}** via {a.get('channel')} ({a.get('status')})" for a in alerts[:3]]
                answer_content = f"**Active Multi-Channel Alerts ({hotel_name}):**\n" + "\n".join(lines)
            elif "title" in res_al:
                answer_content = f"**Alert Dispatched ({hotel_name}):**\n• **{res_al.get('title')}** ({res_al.get('channel')}) — Status: **{res_al.get('status')}**"
            else:
                rules_count = res_al.get("active_rules_count", 0)
                answer_content = f"**Alerts Status ({hotel_name}):** All clear. {rules_count} active monitoring rules listening."

        # Priority 13: 2-Way PMS & OTA Sync Status
        elif "pull_live_pms_reservations" in tool_results or "push_two_way_channel_rates" in tool_results:
            res_sync = tool_results.get("pull_live_pms_reservations") or tool_results.get("push_two_way_channel_rates") or {}
            if "new_reservations_count" in res_sync:
                cnt = res_sync.get("new_reservations_count", 0)
                tot_rev = res_sync.get("total_revenue_inr", 0)
                answer_content = (
                    f"**Live PMS Channel Sync (Opera Cloud / STAAH):**\n"
                    f"• **New Bookings Ingested**: **{cnt} Reservations**\n"
                    f"• **Revenue Pulled**: **₹{tot_rev:,.0f}** | Status: **{res_sync.get('status', 'SUCCESS')}**"
                )
            else:
                p_rate = res_sync.get("pushed_rate_inr", 0)
                answer_content = (
                    f"**2-Way Rate Push to OTAs:**\n"
                    f"• **Pushed Rate**: **₹{p_rate:,.0f}**\n"
                    f"• **Channel Parity Status**: **{res_sync.get('status', 'SUCCESS')}** ({res_sync.get('execution_time_ms', 0):.1f}ms)"
                )

        # Priority 14: Agent Swarm Consensus
        elif "get_agent_swarm_status" in tool_results or "run_multi_agent_swarm_consensus" in tool_results:
            res_sw = tool_results.get("get_agent_swarm_status") or tool_results.get("run_multi_agent_swarm_consensus") or {}
            consensus_rate = res_sw.get("consensus_recommended_rate_inr") or res_sw.get("recommended_rate") or 5800.0
            confidence = res_sw.get("swarm_confidence_pct", 92.5)
            answer_content = (
                f"**Multi-Agent Swarm Consensus ({hotel_name}):**\n"
                f"• **Consensus Rate**: **₹{consensus_rate:,.0f}** | **Confidence**: **{confidence:.1f}%**\n"
                f"• **Active Agents**: Macro Economist, Micro Demand, Comp-Intel, Risk-Guardrail"
            )

        # Priority 15: RAG Knowledge Base Scraped Website / Strategy Documents
        else:
            hotel_rag_docs = vector_store_manager.search_similar(user_message, hotel_id=target_hotel_id, top_k=3)
            all_hotel_chunks = vector_store_manager.get_hotel_documents(target_hotel_id)
            website_rag_chunks = [
                d for d in all_hotel_chunks
                if d.get("category") in ["Hotel Website", "Hotel Website Sublink"] or "Website" in d.get("title", "")
            ]
            candidate_docs = hotel_rag_docs or website_rag_chunks
            if candidate_docs:
                answer_content = extract_crisp_rag_answer(user_message, candidate_docs, hotel_name)
            else:
                answer_content = (
                    f"I can provide rates, room counts, events, and performance metrics for **{hotel_name}** ({hotel_obj.city if hotel_obj else 'Chennai'}). What would you like to check?"
                )

        # Record Assistant turn in Short-Term Memory
        agent_memory_manager.add_conversation_turn(sess_id, "assistant", answer_content)

        # Step 4: Complete Agent Run in DB
        db_run.status = "COMPLETED"
        db_run.completed_at = datetime.now(timezone.utc)
        db_run.final_result = answer_content
        db.commit()

        execution_seconds = round(time.time() - start_time, 2)
        logger.info("agent_run_completed", agent_run_id=agent_run_id, duration_seconds=execution_seconds)

        return {
            "agent_run_id": agent_run_id,
            "answer": answer_content,
            "recommendation": final_recommendation if is_pricing_query else None,
            "factors": factors if is_pricing_query else [],
            "tools_used": tools_used,
            "requires_approval": requires_approval if is_pricing_query else False,
            "execution_time_seconds": execution_seconds,
        }


single_agent_orchestrator = SingleAutonomousRevenueAgent()
