import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base

class Workshop(Base):
    __tablename__ = "workshops"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    timezone = Column(String(64), default="UTC")
    business_hours = Column(JSON, default=lambda: {
        "monday": {"open": "08:00", "close": "18:00"},
        "tuesday": {"open": "08:00", "close": "18:00"},
        "wednesday": {"open": "08:00", "close": "18:00"},
        "thursday": {"open": "08:00", "close": "18:00"},
        "friday": {"open": "08:00", "close": "18:00"},
        "saturday": {"open": "09:00", "close": "15:00"},
        "sunday": None
    })
    hourly_labor_rate = Column(Float, default=95.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(50), nullable=False, default="coordinator")  # manager, coordinator, mechanic, customer
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    notification_preferences = Column(JSON, default=lambda: {"sms": True, "email": True})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicles = relationship("Vehicle", back_populates="customer", cascade="all, delete-orphan")

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    license_plate = Column(String(50), nullable=True)
    vin = Column(String(100), nullable=True)
    mileage = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="vehicles")

class ServiceRequest(Base):
    __tablename__ = "service_requests"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True, index=True)
    original_message = Column(Text, nullable=False)
    structured_intake = Column(JSON, default=dict)
    priority = Column(String(50), default="normal")  # low, normal, high, safety_critical
    safety_escalation = Column(Boolean, default=False)
    status = Column(String(50), default="under_review")  # draft, clarification_needed, under_review, converted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("ConversationMessage", back_populates="service_request", cascade="all, delete-orphan")

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False, index=True)
    sender_type = Column(String(50), nullable=False)  # customer, assistant, advisor
    content = Column(Text, nullable=False)
    extra_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    service_request = relationship("ServiceRequest", back_populates="messages")

class WorkOrder(Base):
    __tablename__ = "work_orders"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    mechanic_id = Column(Integer, ForeignKey("mechanics.id"), nullable=True)
    service_type = Column(String(100), nullable=False)
    status = Column(String(50), default="draft")  # draft, pending_approval, scheduled, in_progress, awaiting_parts, completed, cancelled
    estimated_duration_minutes = Column(Integer, default=60)
    actual_duration_minutes = Column(Integer, nullable=True)
    customer_complaint = Column(Text, nullable=True)
    mechanic_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="work_order", uselist=False)
    estimate = relationship("Estimate", back_populates="work_order", uselist=False)

class Mechanic(Base):
    __tablename__ = "mechanics"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    skills = Column(JSON, default=list)  # ["brakes", "engine", "transmission", "diagnostics", "detailing", "general_maintenance"]
    working_hours = Column(JSON, default=lambda: {"start": "08:00", "end": "17:00"})
    active = Column(Boolean, default=True)

class ServiceBay(Base):
    __tablename__ = "service_bays"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    supported_service_types = Column(JSON, default=list)  # ["heavy_repair", "quick_lube", "detailing", "inspection"]
    active = Column(Boolean, default=True)

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, unique=True, index=True)
    bay_id = Column(Integer, ForeignKey("service_bays.id"), nullable=False)
    mechanic_id = Column(Integer, ForeignKey("mechanics.id"), nullable=False)
    start_at = Column(DateTime, nullable=False, index=True)
    end_at = Column(DateTime, nullable=False, index=True)
    calendar_event_id = Column(String(255), nullable=True)
    calendar_sync_status = Column(String(50), default="pending")  # synced, pending, failed
    status = Column(String(50), default="scheduled")  # scheduled, confirmed, in_progress, completed, cancelled
    idempotency_key = Column(String(128), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    work_order = relationship("WorkOrder", back_populates="appointment")
    bay = relationship("ServiceBay")
    mechanic = relationship("Mechanic")

class Part(Base):
    __tablename__ = "parts"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    sku = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), default="general")
    quantity_on_hand = Column(Integer, default=0)
    reorder_threshold = Column(Integer, default=5)
    unit_cost = Column(Float, default=0.0)
    unit_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, index=True)
    quantity_delta = Column(Integer, nullable=False)  # positive for restock, negative for consumed
    reason = Column(String(255), nullable=False)  # work_order, restock, manual_adjustment, return
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=True)
    actor_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    part = relationship("Part")

class Estimate(Base):
    __tablename__ = "estimates"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, unique=True, index=True)
    line_items = Column(JSON, default=list)  # list of {"type": "part"|"labor", "description": str, "quantity": num, "unit_price": num, "subtotal": num}
    parts_total = Column(Float, default=0.0)
    labor_rate = Column(Float, default=95.0)
    labor_hours = Column(Float, default=1.0)
    labor_total = Column(Float, default=95.0)
    grand_total = Column(Float, default=95.0)
    status = Column(String(50), default="draft")  # draft, approved, rejected
    approver_name = Column(String(255), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    work_order = relationship("WorkOrder", back_populates="estimate")

class AutomationJob(Base):
    __tablename__ = "automation_jobs"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    job_type = Column(String(100), nullable=False)  # appointment_reminder, overdue_check, stock_alert, calendar_retry
    payload = Column(JSON, default=dict)
    status = Column(String(50), default="pending")  # pending, completed, failed, retrying
    attempts = Column(Integer, default=0)
    run_after = Column(DateTime, default=datetime.utcnow)
    last_error_code = Column(String(100), nullable=True)
    last_error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    actor_id = Column(String(100), default="system")
    actor_role = Column(String(50), default="system")
    action = Column(String(100), nullable=False)  # intake_extracted, work_order_created, appointment_booked, estimate_approved, etc.
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=False)
    correlation_id = Column(String(128), nullable=True, index=True)
    metadata_json = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class IntegrationEvent(Base):
    __tablename__ = "integration_events"
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    provider = Column(String(100), nullable=False)  # google_calendar, open_meteo
    operation = Column(String(100), nullable=False)
    external_reference = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")  # success, failed, pending
    attempts = Column(Integer, default=1)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EmailVerification(Base):
    __tablename__ = "email_verifications"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    code = Column(String(10), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

class EmailNotification(Base):
    __tablename__ = "email_notifications"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    recipient_email = Column(String(255), index=True, nullable=False)
    subject = Column(String(255), nullable=False)
    content_html = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # auth_code, intake_received, appointment_confirmed, estimate_ready, vehicle_ready
    status = Column(String(50), default="sent")
    created_at = Column(DateTime, default=datetime.utcnow)
