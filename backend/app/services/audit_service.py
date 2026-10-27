from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.entities import AuditEvent

def log_audit_event(
    db: Session,
    workshop_id: int,
    action: str,
    entity_type: str,
    entity_id: str,
    actor_id: str = "system",
    actor_role: str = "system",
    correlation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> AuditEvent:
    event = AuditEvent(
        workshop_id=workshop_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        correlation_id=correlation_id,
        metadata_json=metadata or {},
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
