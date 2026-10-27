from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Intake & AI Extraction
class IntakeRequest(BaseModel):
    message: str = Field(..., description="Customer's initial message or concern")
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None
    preferred_date: Optional[str] = None

class ExtractedServiceInfo(BaseModel):
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None
    symptoms: List[str] = Field(default_factory=list)
    proposed_service_type: str = "general_inspection"
    estimated_duration_minutes: int = 60
    urgency: str = "normal"  # low, normal, high, safety_critical
    safety_escalation: bool = False
    safety_advisory: Optional[str] = None
    missing_fields: List[str] = Field(default_factory=list)
    clarification_questions: List[str] = Field(default_factory=list)
    recommended_parts: List[str] = Field(default_factory=list)
    ai_confidence_score: float = 0.95
    ai_summary: str = ""

class ClarificationSubmitRequest(BaseModel):
    request_id: int
    message: str
    sender_type: str = "customer"

# Customer & Vehicle
class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None

class VehicleCreate(BaseModel):
    customer_id: int
    make: str
    model: str
    year: int
    license_plate: Optional[str] = None
    mileage: Optional[int] = None

# Service Request
class ServiceRequestCreate(BaseModel):
    workshop_id: int = 1
    original_message: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None

class ServiceRequestResponse(BaseModel):
    id: int
    workshop_id: int
    customer_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    original_message: str
    structured_intake: Dict[str, Any]
    priority: str
    safety_escalation: bool
    status: str
    created_at: datetime
    customer: Optional[Dict[str, Any]] = None
    vehicle: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

# Work Orders
class WorkOrderCreate(BaseModel):
    workshop_id: int = 1
    request_id: Optional[int] = None
    customer_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    mechanic_id: Optional[int] = None
    service_type: str
    estimated_duration_minutes: int = 60
    customer_complaint: Optional[str] = None
    mechanic_notes: Optional[str] = None

class WorkOrderUpdate(BaseModel):
    status: Optional[str] = None
    mechanic_id: Optional[int] = None
    mechanic_notes: Optional[str] = None
    actual_duration_minutes: Optional[int] = None

class WorkOrderResponse(BaseModel):
    id: int
    workshop_id: int
    request_id: Optional[int] = None
    customer_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    mechanic_id: Optional[int] = None
    service_type: str
    status: str
    estimated_duration_minutes: int
    actual_duration_minutes: Optional[int] = None
    customer_complaint: Optional[str] = None
    mechanic_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Scheduling & Slots
class AvailabilityQuery(BaseModel):
    workshop_id: int = 1
    service_type: str
    duration_minutes: int = 60
    target_date: str = Field(..., description="Target date YYYY-MM-DD")

class SlotOption(BaseModel):
    start_at: str
    end_at: str
    bay_id: int
    bay_name: str
    mechanic_id: int
    mechanic_name: str
    available: bool = True
    reason: Optional[str] = None

class AppointmentBookingRequest(BaseModel):
    workshop_id: int = 1
    work_order_id: int
    bay_id: int
    mechanic_id: int
    start_at: datetime
    idempotency_key: str = Field(..., description="Unique client key preventing duplicate bookings")

class AppointmentResponse(BaseModel):
    id: int
    workshop_id: int
    work_order_id: int
    bay_id: int
    mechanic_id: int
    start_at: datetime
    end_at: datetime
    calendar_event_id: Optional[str] = None
    calendar_sync_status: str
    status: str
    idempotency_key: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Inventory
class PartCreate(BaseModel):
    workshop_id: int = 1
    sku: str
    name: str
    category: str = "general"
    quantity_on_hand: int = 0
    reorder_threshold: int = 5
    unit_cost: float = 0.0
    unit_price: float = 0.0

class PartResponse(BaseModel):
    id: int
    workshop_id: int
    sku: str
    name: str
    category: str
    quantity_on_hand: int
    reorder_threshold: int
    unit_cost: float
    unit_price: float
    is_low_stock: bool = False

    model_config = ConfigDict(from_attributes=True)

class InventoryMovementCreate(BaseModel):
    workshop_id: int = 1
    part_id: int
    quantity_delta: int
    reason: str
    work_order_id: Optional[int] = None

# Estimates
class EstimateCreate(BaseModel):
    workshop_id: int = 1
    work_order_id: int
    parts_included: List[Dict[str, Any]] = Field(default_factory=list)
    labor_hours: float = 1.0

class EstimateApprovalRequest(BaseModel):
    approved_by: str
    notes: Optional[str] = None

class EstimateResponse(BaseModel):
    id: int
    workshop_id: int
    work_order_id: int
    line_items: List[Dict[str, Any]]
    parts_total: float
    labor_rate: float
    labor_hours: float
    labor_total: float
    grand_total: float
    status: str
    approver_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Weather context
class WeatherContextResponse(BaseModel):
    location: str
    target_date: str
    temperature_c: float
    weather_condition: str
    precipitation_probability: int
    advisory_for_service: Optional[str] = None
    source: str = "Open-Meteo API"
    timestamp: datetime

# Audit Event
class AuditEventResponse(BaseModel):
    id: int
    workshop_id: int
    actor_id: str
    actor_role: str
    action: str
    entity_type: str
    entity_id: str
    correlation_id: Optional[str] = None
    metadata_json: Dict[str, Any]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# Operational Analytics
class AnalyticsSummaryResponse(BaseModel):
    total_service_requests: int
    pending_review_requests: int
    safety_escalations_count: int
    active_work_orders: int
    completed_work_orders: int
    scheduled_appointments_today: int
    bay_utilization_rate: float
    low_stock_parts_count: int
    total_estimated_revenue: float
    total_approved_revenue: float
    audit_events_count: int
