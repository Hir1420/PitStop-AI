from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.entities import (
    AutomationJob, Appointment, WorkOrder, Part, IntegrationEvent
)
from app.services.audit_service import log_audit_event
from app.services.calendar_service import sync_appointment_to_calendar

def run_proactive_automation_cycle(db: Session, workshop_id: int) -> Dict[str, Any]:
    """Scans and executes proactive automation jobs across workshop operations."""
    now = datetime.utcnow()
    results = {
        "reminders_prepared": 0,
        "overdue_jobs_flagged": 0,
        "low_stock_alerts": 0,
        "retries_processed": 0
    }

    # 1. Appointment Reminders
    upcoming_window = now + timedelta(days=2)
    upcoming_apps = db.query(Appointment).filter(
        Appointment.workshop_id == workshop_id,
        Appointment.status == "confirmed",
        Appointment.start_at >= now,
        Appointment.start_at <= upcoming_window
    ).all()

    for app in upcoming_apps:
        # Check if reminder already exists
        existing = db.query(AutomationJob).filter(
            AutomationJob.workshop_id == workshop_id,
            AutomationJob.job_type == "appointment_reminder",
            AutomationJob.payload["appointment_id"].as_integer() == app.id
        ).first()
        if not existing:
            job = AutomationJob(
                workshop_id=workshop_id,
                job_type="appointment_reminder",
                payload={
                    "appointment_id": app.id,
                    "customer_notification": f"Reminder: Your service appointment is scheduled for {app.start_at.strftime('%Y-%m-%d %H:%M')}.",
                    "status": "ready_for_dispatch"
                },
                status="completed",
                attempts=1,
                created_at=now
            )
            db.add(job)
            results["reminders_prepared"] += 1

    # 2. Overdue Work Orders
    in_progress_orders = db.query(WorkOrder).filter(
        WorkOrder.workshop_id == workshop_id,
        WorkOrder.status.in_(["in_progress", "awaiting_parts"])
    ).all()

    for wo in in_progress_orders:
        max_duration = timedelta(minutes=(wo.estimated_duration_minutes or 60) * 2)
        if (now - wo.updated_at) > max_duration:
            # Overdue notice
            existing = db.query(AutomationJob).filter(
                AutomationJob.workshop_id == workshop_id,
                AutomationJob.job_type == "overdue_work_order_alert",
                AutomationJob.payload["work_order_id"].as_integer() == wo.id
            ).first()
            if not existing:
                job = AutomationJob(
                    workshop_id=workshop_id,
                    job_type="overdue_work_order_alert",
                    payload={
                        "work_order_id": wo.id,
                        "service_type": wo.service_type,
                        "elapsed_minutes": int((now - wo.updated_at).total_seconds() / 60)
                    },
                    status="completed",
                    attempts=1,
                    created_at=now
                )
                db.add(job)
                results["overdue_jobs_flagged"] += 1

    # 3. Low Stock Alerts
    low_stock_parts = db.query(Part).filter(
        Part.workshop_id == workshop_id,
        Part.quantity_on_hand <= Part.reorder_threshold
    ).all()

    for part in low_stock_parts:
        existing = db.query(AutomationJob).filter(
            AutomationJob.workshop_id == workshop_id,
            AutomationJob.job_type == "low_stock_alert",
            AutomationJob.payload["part_sku"].as_string() == part.sku
        ).first()
        if not existing:
            job = AutomationJob(
                workshop_id=workshop_id,
                job_type="low_stock_alert",
                payload={
                    "part_id": part.id,
                    "part_sku": part.sku,
                    "part_name": part.name,
                    "quantity_on_hand": part.quantity_on_hand,
                    "reorder_threshold": part.reorder_threshold
                },
                status="completed",
                attempts=1,
                created_at=now
            )
            db.add(job)
            results["low_stock_alerts"] += 1

    # 4. Process Pending Retries
    pending_retries = db.query(AutomationJob).filter(
        AutomationJob.workshop_id == workshop_id,
        AutomationJob.status == "pending",
        AutomationJob.job_type == "calendar_retry"
    ).all()

    for r_job in pending_retries:
        app_id = r_job.payload.get("appointment_id")
        if app_id:
            # Execute retry
            retry_res = sync_appointment_to_calendar(db, workshop_id, app_id, force_failure=False)
            if retry_res.get("success"):
                r_job.status = "completed"
                r_job.attempts += 1
                results["retries_processed"] += 1
            else:
                r_job.attempts += 1
                if r_job.attempts >= 3:
                    r_job.status = "failed"

    db.commit()

    log_audit_event(
        db=db,
        workshop_id=workshop_id,
        action="automation_cycle_executed",
        entity_type="system",
        entity_id="cron",
        actor_id="system",
        metadata=results
    )

    return results
