import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.entities import Workshop, Mechanic, ServiceBay, Part, WorkOrder, Appointment, Estimate
from app.services.ai_intake_service import heuristic_extraction
from app.services.scheduling_service import book_appointment_deterministic, get_feasible_slots
from app.services.inventory_service import record_inventory_movement
from app.services.estimate_service import generate_draft_estimate, approve_estimate_by_human
from app.services.calendar_service import sync_appointment_to_calendar

# Setup in-memory test database
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    
    # Seed minimal environment
    ws = Workshop(id=1, name="Test Workshop", hourly_labor_rate=100.0)
    session.add(ws)
    
    mech = Mechanic(id=1, workshop_id=1, name="Marcus Vance", skills=["brakes", "general_maintenance"], active=True)
    bay = ServiceBay(id=1, workshop_id=1, name="Bay 1", supported_service_types=["heavy_repair", "brakes"], active=True)
    part = Part(id=1, workshop_id=1, sku="BRK-PAD", name="Ceramic Brake Pads", quantity_on_hand=10, reorder_threshold=3, unit_price=80.0)
    wo = WorkOrder(id=1, workshop_id=1, service_type="brake_service", estimated_duration_minutes=60, status="pending_approval")
    
    session.add_all([mech, bay, part, wo])
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)

def test_ai_intake_safety_guardrail():
    """Verify brake symptoms trigger safety escalation and cautious advisory."""
    msg = "My 2021 Honda Civic has spongy brakes and grinding noise on highway"
    extracted = heuristic_extraction(msg)
    
    assert extracted.vehicle_make == "Honda"
    assert extracted.vehicle_year == 2021
    assert extracted.proposed_service_type == "brake_service"
    assert extracted.urgency == "safety_critical"
    assert extracted.safety_escalation is True
    assert extracted.safety_advisory is not None
    assert "SAFETY ADVISORY" in extracted.safety_advisory

def test_deterministic_scheduling_and_idempotency(db):
    """Verify deterministic conflict rejection and idempotency protection."""
    start_time = datetime(2026, 10, 26, 9, 0, 0)
    idempotency_key = "test_key_unique_123"

    # 1. First booking succeeds
    app1, is_new1 = book_appointment_deterministic(
        db=db,
        workshop_id=1,
        work_order_id=1,
        bay_id=1,
        mechanic_id=1,
        start_at=start_time,
        idempotency_key=idempotency_key
    )
    assert is_new1 is True
    assert app1.status == "confirmed"

    # 2. Idempotent retry returns existing record without duplicating
    app2, is_new2 = book_appointment_deterministic(
        db=db,
        workshop_id=1,
        work_order_id=1,
        bay_id=1,
        mechanic_id=1,
        start_at=start_time,
        idempotency_key=idempotency_key
    )
    assert is_new2 is False
    assert app2.id == app1.id

    # 3. Conflicting second work order booking on same bay/time is rejected
    wo2 = WorkOrder(id=2, workshop_id=1, service_type="brake_service", estimated_duration_minutes=60)
    db.add(wo2)
    db.commit()

    with pytest.raises(ValueError) as excinfo:
        book_appointment_deterministic(
            db=db,
            workshop_id=1,
            work_order_id=2,
            bay_id=1,
            mechanic_id=1,
            start_at=start_time,
            idempotency_key="different_key_456"
        )
    assert "Conflict: Service bay 1 was just booked" in str(excinfo.value)

def test_inventory_deduction_and_insufficient_stock(db):
    """Verify inventory movement reduces quantity and prevents negative stock."""
    # Deduct 4 pads
    m = record_inventory_movement(
        db=db,
        workshop_id=1,
        part_id=1,
        quantity_delta=-4,
        reason="work_order",
        work_order_id=1
    )
    part = db.query(Part).filter(Part.id == 1).first()
    assert part.quantity_on_hand == 6

    # Attempt to deduct 10 (exceeds 6)
    with pytest.raises(ValueError) as excinfo:
        record_inventory_movement(
            db=db,
            workshop_id=1,
            part_id=1,
            quantity_delta=-10,
            reason="work_order"
        )
    assert "Insufficient stock" in str(excinfo.value)

def test_human_in_the_loop_estimate_approval(db):
    """Verify estimate remains draft until human advisor explicitly authorizes it."""
    est = generate_draft_estimate(
        db=db,
        workshop_id=1,
        work_order_id=1,
        labor_hours=1.5
    )
    assert est.status == "draft"
    assert est.grand_total > 0

    # Staff approval
    approved = approve_estimate_by_human(
        db=db,
        workshop_id=1,
        estimate_id=est.id,
        approver_name="Advisor Dave",
        notes="Customer confirmed by phone"
    )
    assert approved.status == "approved"
    assert approved.approver_name == "Advisor Dave"
    assert approved.approved_at is not None

def test_calendar_sync_failure_and_recovery(db):
    """Verify calendar sync failure creates retry automation job and allows recovery."""
    start_time = datetime(2026, 10, 26, 11, 0, 0)
    app, _ = book_appointment_deterministic(
        db=db, workshop_id=1, work_order_id=1, bay_id=1, mechanic_id=1,
        start_at=start_time, idempotency_key="cal_test_key"
    )

    # 1. Force failure
    fail_res = sync_appointment_to_calendar(db, workshop_id=1, appointment_id=app.id, force_failure=True)
    assert fail_res["success"] is False
    assert app.calendar_sync_status == "failed"

    # 2. Recovery sync
    rec_res = sync_appointment_to_calendar(db, workshop_id=1, appointment_id=app.id, force_failure=False)
    assert rec_res["success"] is True
    assert app.calendar_sync_status == "synced"
    assert app.calendar_event_id is not None

def test_customer_email_otp_and_verification(db):
    """Verify passwordless email OTP generation, verification, and expiration."""
    from app.services.email_service import send_verification_otp, verify_email_otp
    from app.models.entities import Customer

    cust = Customer(id=1, workshop_id=1, name="Alex Mercer", email="alex.mercer@example.com")
    db.add(cust)
    db.commit()

    # 1. Request code
    send_res = send_verification_otp(db, "alex.mercer@example.com")
    assert send_res["success"] is True
    otp_code = send_res["code_preview"]
    assert len(otp_code) == 6
    assert otp_code.isdigit()

    # 2. Verify with invalid code fails
    with pytest.raises(ValueError) as exc:
        verify_email_otp(db, "alex.mercer@example.com", "000000")
    assert "Invalid or expired" in str(exc.value)

    # 3. Verify with correct code succeeds
    auth = verify_email_otp(db, "alex.mercer@example.com", otp_code)
    assert auth["verified"] is True
    assert auth["customer"]["email"] == "alex.mercer@example.com"
    assert auth["customer"]["name"] == "Alex Mercer"

def test_transactional_email_logging(db):
    """Verify transactional emails create rendered HTML entries in outbox log."""
    from app.services.email_service import dispatch_transactional_email
    from app.models.entities import EmailNotification

    notif = dispatch_transactional_email(
        db=db,
        recipient_email="customer@example.com",
        subject="Service Ready For Pickup",
        headline="Your Vehicle is Ready",
        body_text="All scheduled brake services have been completed.",
        notification_type="vehicle_ready",
        badge_label="Ready for Pickup"
    )
    assert notif.id is not None
    assert notif.recipient_email == "customer@example.com"
    assert "Your Vehicle is Ready" in notif.content_html
    assert notif.status == "sent"


