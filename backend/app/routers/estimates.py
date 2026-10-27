from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import Estimate, WorkOrder
from app.schemas.schemas import EstimateCreate, EstimateApprovalRequest, EstimateResponse
from app.services.estimate_service import generate_draft_estimate, approve_estimate_by_human

router = APIRouter(prefix="/api/estimates", tags=["Estimates & Invoicing"])

@router.post("", response_model=EstimateResponse)
def create_estimate(payload: EstimateCreate, db: Session = Depends(get_db)):
    """Generates a calculated draft estimate for a work order using inventory parts and configured labor rates."""
    try:
        est = generate_draft_estimate(
            db=db,
            workshop_id=payload.workshop_id,
            work_order_id=payload.work_order_id,
            parts_included=payload.parts_included,
            labor_hours=payload.labor_hours
        )

        # Notify customer that estimate is ready for authorization
        from app.models.entities import Customer
        wo = db.query(WorkOrder).filter(WorkOrder.id == payload.work_order_id).first()
        customer = db.query(Customer).filter(Customer.id == wo.customer_id).first() if wo and wo.customer_id else None
        if customer and customer.email:
            from app.services.email_service import dispatch_transactional_email
            dispatch_transactional_email(
                db=db,
                recipient_email=customer.email,
                subject=f"Estimate Ready for Review: Work Order #{wo.id}",
                headline=f"Formal Service Estimate: ${est.grand_total:.2f}",
                body_text="Your workshop estimate has been prepared. Please sign in to your PitStop Garage portal to review the line items and authorize work.",
                notification_type="estimate_ready",
                customer_id=customer.id,
                badge_label="Action Required",
                highlight_text=f"Total: ${est.grand_total:.2f} (Parts: ${est.parts_total:.2f} + Labor: ${est.labor_total:.2f})"
            )

        return est
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/work-order/{work_order_id}", response_model=EstimateResponse)
def get_work_order_estimate(work_order_id: int, db: Session = Depends(get_db)):
    est = db.query(Estimate).filter(Estimate.work_order_id == work_order_id).first()
    if not est:
        raise HTTPException(status_code=404, detail="No estimate generated for this work order")
    return est

@router.post("/{estimate_id}/approve", response_model=EstimateResponse)
def approve_estimate(
    estimate_id: int,
    payload: EstimateApprovalRequest,
    workshop_id: int = 1,
    db: Session = Depends(get_db)
):
    """Enforces human-in-the-loop explicit approval before work begins."""
    try:
        approved = approve_estimate_by_human(
            db=db,
            workshop_id=workshop_id,
            estimate_id=estimate_id,
            approver_name=payload.approved_by,
            notes=payload.notes
        )
        return approved
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
