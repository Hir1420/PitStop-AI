from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entities import Part, InventoryMovement
from app.services.audit_service import log_audit_event

def get_parts_with_stock_status(db: Session, workshop_id: int) -> List[Dict[str, Any]]:
    parts = db.query(Part).filter(Part.workshop_id == workshop_id).all()
    results = []
    for p in parts:
        results.append({
            "id": p.id,
            "workshop_id": p.workshop_id,
            "sku": p.sku,
            "name": p.name,
            "category": p.category,
            "quantity_on_hand": p.quantity_on_hand,
            "reorder_threshold": p.reorder_threshold,
            "unit_cost": p.unit_cost,
            "unit_price": p.unit_price,
            "is_low_stock": p.quantity_on_hand <= p.reorder_threshold
        })
    return results

def record_inventory_movement(
    db: Session,
    workshop_id: int,
    part_id: int,
    quantity_delta: int,
    reason: str,
    work_order_id: Optional[int] = None,
    actor_id: Optional[int] = None
) -> InventoryMovement:
    part = db.query(Part).filter(
        Part.id == part_id,
        Part.workshop_id == workshop_id
    ).first()
    if not part:
        raise ValueError(f"Part with id {part_id} not found.")

    new_stock = part.quantity_on_hand + quantity_delta
    if new_stock < 0:
        raise ValueError(f"Insufficient stock for '{part.name}'. Available: {part.quantity_on_hand}, Requested delta: {quantity_delta}")

    part.quantity_on_hand = new_stock
    movement = InventoryMovement(
        workshop_id=workshop_id,
        part_id=part_id,
        quantity_delta=quantity_delta,
        reason=reason,
        work_order_id=work_order_id,
        actor_id=actor_id
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)

    # Log audit event for inventory adjustment
    log_audit_event(
        db=db,
        workshop_id=workshop_id,
        action="inventory_movement_recorded",
        entity_type="part",
        entity_id=str(part_id),
        actor_id=str(actor_id or "system"),
        metadata={
            "delta": quantity_delta,
            "new_stock": new_stock,
            "reason": reason,
            "work_order_id": work_order_id
        }
    )

    return movement

def check_service_parts_readiness(
    db: Session,
    workshop_id: int,
    part_names: List[str]
) -> Dict[str, Any]:
    """Checks whether the requested parts are ready in inventory."""
    shortages = []
    ready_parts = []
    
    for name in part_names:
        # Match by name substring or sku
        part = db.query(Part).filter(
            Part.workshop_id == workshop_id,
            Part.name.ilike(f"%{name}%")
        ).first()
        if not part or part.quantity_on_hand <= 0:
            shortages.append(name)
        else:
            ready_parts.append({
                "part_id": part.id,
                "name": part.name,
                "quantity_on_hand": part.quantity_on_hand,
                "unit_price": part.unit_price
            })
            
    return {
        "all_ready": len(shortages) == 0,
        "ready_parts": ready_parts,
        "shortages": shortages
    }
