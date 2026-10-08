"""
Main API v1 Router aggregating domain endpoints.
"""
from fastapi import APIRouter
from app.api.v1 import (
    auth,
    hotels,
    inventory,
    revenue,
    forecasts,
    competitors,
    events,
    pricing,
    guardrails,
    rag,
    agent,
    reports,
    approval,
    feedback,
    health,
    audit,
    users,
    weather,
    los_displacement,
    trevpar_ancillary,
    alerts,
    pdf_bi_reports,
    agent_swarm,
    developer_api,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(hotels.router)
api_router.include_router(inventory.router)
api_router.include_router(revenue.router)
api_router.include_router(forecasts.router)
api_router.include_router(competitors.router)
api_router.include_router(events.router)
api_router.include_router(weather.router)
api_router.include_router(pricing.router)
api_router.include_router(guardrails.router)
api_router.include_router(rag.router)
api_router.include_router(agent.router)
api_router.include_router(reports.router)
api_router.include_router(approval.router)
api_router.include_router(feedback.router)
api_router.include_router(health.router)
api_router.include_router(audit.router)
api_router.include_router(users.router)
api_router.include_router(los_displacement.router)
api_router.include_router(trevpar_ancillary.router)
api_router.include_router(alerts.router)
api_router.include_router(pdf_bi_reports.router)
api_router.include_router(agent_swarm.router)
api_router.include_router(developer_api.router)

