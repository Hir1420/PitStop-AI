from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.entities import AuditEvent
from app.schemas.schemas import AuditEventResponse

router = APIRouter(prefix="/api/audit-events", tags=["Audit Log & Governance"])

@router.get("", response_model=List[AuditEventResponse])
def get_audit_trail(
    workshop_id: int = 1,
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Retrieves immutable audit trail of all AI extractions, bookings, approvals, and mutations."""
    query = db.query(AuditEvent).filter(AuditEvent.workshop_id == workshop_id)
    if entity_type:
        query = query.filter(AuditEvent.entity_type == entity_type)
    if action:
        query = query.filter(AuditEvent.action == action)
    return query.order_by(AuditEvent.timestamp.desc()).limit(limit).all()
