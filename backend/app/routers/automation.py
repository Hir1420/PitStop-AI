from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import AutomationJob
from app.services.automation_service import run_proactive_automation_cycle

router = APIRouter(prefix="/api/automation", tags=["Background Automation"])

@router.post("/run")
def trigger_automation_cycle(workshop_id: int = 1, db: Session = Depends(get_db)):
    """Manually triggers the background automation cycle for reminders, overdue work orders, and stock alerts."""
    results = run_proactive_automation_cycle(db, workshop_id)
    return {"status": "success", "results": results}

@router.get("/jobs")
def list_automation_jobs(workshop_id: int = 1, db: Session = Depends(get_db)):
    jobs = db.query(AutomationJob).filter(
        AutomationJob.workshop_id == workshop_id
    ).order_by(AutomationJob.created_at.desc()).limit(30).all()
    return jobs
