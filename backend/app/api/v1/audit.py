"""
Audit Trail REST API endpoints for auditing system actions.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.audit import AuditLogs
from app.api.deps import get_current_user, require_roles
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


@router.get("/logs", response_model=List[dict])
async def list_audit_logs(
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager"])),
):
    """Retrieve immutable audit trail log records with action and entity filters."""
    query = db.query(AuditLogs)
    if action:
        query = query.filter(AuditLogs.action == action)
    if entity_type:
        query = query.filter(AuditLogs.entity_type == entity_type)
    if user_id:
        query = query.filter(AuditLogs.user_id == user_id)

    logs = query.order_by(AuditLogs.created_at.desc()).offset(skip).limit(limit).all()

    return [
        {
            "audit_id": l.audit_id,
            "user_id": l.user_id,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "old_value": l.old_value,
            "new_value": l.new_value,
            "ip_address": l.ip_address,
            "created_at": l.created_at,
        }
        for l in logs
    ]
