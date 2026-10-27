from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.entities import ServiceRequest, Customer, Vehicle, ConversationMessage
from app.schemas.schemas import (
    IntakeRequest, ExtractedServiceInfo, ServiceRequestCreate,
    ServiceRequestResponse, ClarificationSubmitRequest
)
from app.services.ai_intake_service import extract_service_request_agent
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/api/requests", tags=["Service Requests"])

@router.post("/intake", response_model=ExtractedServiceInfo)
async def analyze_intake_message(payload: IntakeRequest):
    """AI Agent Intake Endpoint: Structures customer message, evaluates safety risks, and returns missing fields."""
    extracted = await extract_service_request_agent(
        message=payload.message,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        vehicle_make=payload.vehicle_make,
        vehicle_model=payload.vehicle_model,
        vehicle_year=payload.vehicle_year
    )
    return extracted

@router.post("", response_model=ServiceRequestResponse)
async def create_service_request(payload: ServiceRequestCreate, db: Session = Depends(get_db)):
    """Creates a validated service request with customer, vehicle association, and AI structured data."""
    # 1. AI structuring
    extracted = await extract_service_request_agent(
        message=payload.original_message,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        vehicle_make=payload.vehicle_make,
        vehicle_model=payload.vehicle_model,
        vehicle_year=payload.vehicle_year
    )

    # 2. Customer record
    customer = None
    if payload.customer_name:
        customer = db.query(Customer).filter(
            Customer.workshop_id == payload.workshop_id,
            Customer.name == payload.customer_name
        ).first()
        if not customer:
            customer = Customer(
                workshop_id=payload.workshop_id,
                name=payload.customer_name,
                phone=payload.customer_phone,
                email=payload.customer_email
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)

    # 3. Vehicle record
    vehicle = None
    if extracted.vehicle_make and customer:
        vehicle = Vehicle(
            workshop_id=payload.workshop_id,
            customer_id=customer.id,
            make=extracted.vehicle_make,
            model=extracted.vehicle_model or "Unknown Model",
            year=extracted.vehicle_year or 2020
        )
        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)

    # 4. Service Request record
    status = "clarification_needed" if extracted.clarification_questions and extracted.missing_fields else "under_review"
    req = ServiceRequest(
        workshop_id=payload.workshop_id,
        customer_id=customer.id if customer else None,
        vehicle_id=vehicle.id if vehicle else None,
        original_message=payload.original_message,
        structured_intake=extracted.model_dump(),
        priority=extracted.urgency,
        safety_escalation=extracted.safety_escalation,
        status=status,
        created_at=datetime.utcnow()
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    # Initial conversation message
    msg = ConversationMessage(
        request_id=req.id,
        sender_type="customer",
        content=payload.original_message,
        created_at=datetime.utcnow()
    )
    db.add(msg)

    # If clarification questions, add assistant message
    if extracted.clarification_questions:
        q_text = " ".join(extracted.clarification_questions)
        if extracted.safety_advisory:
            q_text = f"{extracted.safety_advisory} {q_text}"
        assistant_msg = ConversationMessage(
            request_id=req.id,
            sender_type="assistant",
            content=q_text,
            created_at=datetime.utcnow()
        )
        db.add(assistant_msg)

    db.commit()

    if customer and customer.email:
        from app.services.email_service import dispatch_transactional_email
        dispatch_transactional_email(
            db=db,
            recipient_email=customer.email,
            subject=f"Service Request Received: {extracted.proposed_service_type.replace('_', ' ').title()}",
            headline=f"We received your request for your {extracted.vehicle_make or 'vehicle'}",
            body_text=f"Our AI intake agent has structured your request. Estimated duration: {extracted.estimated_duration_minutes} min. {extracted.safety_advisory or 'A workshop coordinator will review your request shortly.'}",
            notification_type="intake_received",
            customer_id=customer.id,
            badge_label="Intake Logged",
            highlight_text=extracted.ai_summary
        )

    log_audit_event(
        db=db,
        workshop_id=payload.workshop_id,
        action="service_request_created",
        entity_type="service_request",
        entity_id=str(req.id),
        actor_id=customer.name if customer else "customer",
        actor_role="customer",
        metadata={
            "service_type": extracted.proposed_service_type,
            "safety_escalation": extracted.safety_escalation,
            "urgency": extracted.urgency
        }
    )

    return req

@router.get("", response_model=List[ServiceRequestResponse])
def list_service_requests(
    workshop_id: int = 1,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ServiceRequest).filter(ServiceRequest.workshop_id == workshop_id)
    if status:
        query = query.filter(ServiceRequest.status == status)
    if priority:
        query = query.filter(ServiceRequest.priority == priority)
    return query.order_by(ServiceRequest.created_at.desc()).all()

@router.get("/{request_id}")
def get_service_request_detail(request_id: int, db: Session = Depends(get_db)):
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Service request not found")

    customer = db.query(Customer).filter(Customer.id == req.customer_id).first() if req.customer_id else None
    vehicle = db.query(Vehicle).filter(Vehicle.id == req.vehicle_id).first() if req.vehicle_id else None
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.request_id == req.id
    ).order_by(ConversationMessage.created_at.asc()).all()

    return {
        "id": req.id,
        "workshop_id": req.workshop_id,
        "customer_id": req.customer_id,
        "customer": {"name": customer.name, "phone": customer.phone, "email": customer.email} if customer else None,
        "vehicle_id": req.vehicle_id,
        "vehicle": {"make": vehicle.make, "model": vehicle.model, "year": vehicle.year} if vehicle else None,
        "original_message": req.original_message,
        "structured_intake": req.structured_intake,
        "priority": req.priority,
        "safety_escalation": req.safety_escalation,
        "status": req.status,
        "created_at": req.created_at,
        "messages": [
            {"id": m.id, "sender_type": m.sender_type, "content": m.content, "created_at": m.created_at}
            for m in messages
        ]
    }

@router.post("/{request_id}/messages")
def submit_clarification_message(
    request_id: int,
    payload: ClarificationSubmitRequest,
    db: Session = Depends(get_db)
):
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Service request not found")

    msg = ConversationMessage(
        request_id=request_id,
        sender_type=payload.sender_type,
        content=payload.message,
        created_at=datetime.utcnow()
    )
    db.add(msg)

    # Transition state to under_review once customer answers
    if payload.sender_type == "customer":
        req.status = "under_review"

    db.commit()
    db.refresh(msg)
    return {"id": msg.id, "status": "message_recorded"}
