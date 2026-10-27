from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entities import Estimate, WorkOrder, Workshop, Part
from app.services.audit_service import log_audit_event

def generate_draft_estimate(
    db: Session,
    workshop_id: int,
    work_order_id: int,
    parts_included: Optional[List[Dict[str, Any]]] = None,
    labor_hours: Optional[float] = None
) -> Estimate:
    work_order = db.query(WorkOrder).filter(
        WorkOrder.id == work_order_id,
        WorkOrder.workshop_id == workshop_id
    ).first()
    if not work_order:
        raise ValueError(f"Work order {work_order_id} not found.")

    workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    labor_rate = workshop.hourly_labor_rate if workshop else 95.0

    if labor_hours is None:
        labor_hours = max(1.0, (work_order.estimated_duration_minutes or 60) / 60.0)

    line_items = []
    parts_total = 0.0

    # Auto-resolve parts if none provided
    if not parts_included:
        service_type = work_order.service_type or "general_inspection"
        # Match inventory parts by category or name
        sample_parts = db.query(Part).filter(
            Part.workshop_id == workshop_id
        ).limit(2).all()
        for p in sample_parts:
            cost = p.unit_price or 45.0
            line_items.append({
                "type": "part",
                "part_id": p.id,
                "description": p.name,
                "quantity": 1,
                "unit_price": cost,
                "subtotal": cost
            })
            parts_total += cost
    else:
        for p in parts_included:
            qty = p.get("quantity", 1)
            price = p.get("unit_price", 50.0)
            sub = qty * price
            line_items.append({
                "type": "part",
                "part_id": p.get("part_id"),
                "description": p.get("description", "Replacement Part"),
                "quantity": qty,
                "unit_price": price,
                "subtotal": sub
            })
            parts_total += sub

    labor_total = round(labor_hours * labor_rate, 2)
    line_items.append({
        "type": "labor",
        "description": f"Certified Technician Labor ({labor_hours:.1f} hrs @ ${labor_rate:.2f}/hr)",
        "quantity": labor_hours,
        "unit_price": labor_rate,
        "subtotal": labor_total
    })

    grand_total = round(parts_total + labor_total, 2)

    # Check if existing estimate
    estimate = db.query(Estimate).filter(
        Estimate.work_order_id == work_order_id
    ).first()

    if estimate:
        estimate.line_items = line_items
        estimate.parts_total = parts_total
        estimate.labor_rate = labor_rate
        estimate.labor_hours = labor_hours
        estimate.labor_total = labor_total
        estimate.grand_total = grand_total
        estimate.status = "draft"
    else:
        estimate = Estimate(
            workshop_id=workshop_id,
            work_order_id=work_order_id,
            line_items=line_items,
            parts_total=parts_total,
            labor_rate=labor_rate,
            labor_hours=labor_hours,
            labor_total=labor_total,
            grand_total=grand_total,
            status="draft",
            created_at=datetime.utcnow()
        )
        db.add(estimate)

    db.commit()
    db.refresh(estimate)

    log_audit_event(
        db=db,
        workshop_id=workshop_id,
        action="estimate_drafted",
        entity_type="estimate",
        entity_id=str(estimate.id),
        actor_id="system",
        metadata={"grand_total": grand_total, "work_order_id": work_order_id}
    )

    return estimate

def approve_estimate_by_human(
    db: Session,
    workshop_id: int,
    estimate_id: int,
    approver_name: str,
    notes: Optional[str] = None
) -> Estimate:
    """Human-in-the-loop explicit estimate authorization."""
    estimate = db.query(Estimate).filter(
        Estimate.id == estimate_id,
        Estimate.workshop_id == workshop_id
    ).first()
    if not estimate:
        raise ValueError(f"Estimate {estimate_id} not found.")

    estimate.status = "approved"
    estimate.approver_name = approver_name
    estimate.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(estimate)

    log_audit_event(
        db=db,
        workshop_id=workshop_id,
        action="estimate_approved",
        entity_type="estimate",
        entity_id=str(estimate.id),
        actor_id=approver_name,
        actor_role="service_advisor",
        metadata={"grand_total": estimate.grand_total, "notes": notes}
    )

    return estimate
