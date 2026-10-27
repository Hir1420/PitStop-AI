from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.entities import Part, InventoryMovement
from app.schemas.schemas import PartCreate, PartResponse, InventoryMovementCreate
from app.services.inventory_service import get_parts_with_stock_status, record_inventory_movement

router = APIRouter(prefix="/api/inventory", tags=["Inventory Management"])

@router.get("/parts", response_model=List[PartResponse])
def get_parts(workshop_id: int = 1, db: Session = Depends(get_db)):
    """Lists inventory parts with stock levels and low-stock warning indicators."""
    return get_parts_with_stock_status(db, workshop_id)

@router.post("/parts", response_model=PartResponse)
def create_part(payload: PartCreate, db: Session = Depends(get_db)):
    existing = db.query(Part).filter(
        Part.workshop_id == payload.workshop_id,
        Part.sku == payload.sku
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Part with SKU '{payload.sku}' already exists.")

    part = Part(
        workshop_id=payload.workshop_id,
        sku=payload.sku,
        name=payload.name,
        category=payload.category,
        quantity_on_hand=payload.quantity_on_hand,
        reorder_threshold=payload.reorder_threshold,
        unit_cost=payload.unit_cost,
        unit_price=payload.unit_price,
        created_at=datetime.utcnow()
    )
    db.add(part)
    db.commit()
    db.refresh(part)
    return part

@router.post("/movements")
def create_movement(payload: InventoryMovementCreate, db: Session = Depends(get_db)):
    """Records an authorized stock movement (deduction for work order or replenishment)."""
    try:
        movement = record_inventory_movement(
            db=db,
            workshop_id=payload.workshop_id,
            part_id=payload.part_id,
            quantity_delta=payload.quantity_delta,
            reason=payload.reason,
            work_order_id=payload.work_order_id
        )
        return {
            "id": movement.id,
            "part_id": movement.part_id,
            "quantity_delta": movement.quantity_delta,
            "reason": movement.reason,
            "status": "success"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/movements")
def list_movements(workshop_id: int = 1, db: Session = Depends(get_db)):
    movements = db.query(InventoryMovement).filter(
        InventoryMovement.workshop_id == workshop_id
    ).order_by(InventoryMovement.created_at.desc()).limit(50).all()
    
    results = []
    for m in movements:
        part = db.query(Part).filter(Part.id == m.part_id).first()
        results.append({
            "id": m.id,
            "part_name": part.name if part else f"Part #{m.part_id}",
            "part_sku": part.sku if part else "",
            "quantity_delta": m.quantity_delta,
            "reason": m.reason,
            "work_order_id": m.work_order_id,
            "created_at": m.created_at
        })
    return results
