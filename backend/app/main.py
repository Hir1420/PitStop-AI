from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import *
from app.routers import (
    requests, work_orders, scheduling, inventory, estimates,
    integrations, analytics, audit, automation, health, seed, customer_portal
)
from app.routers.seed import seed_database

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    description="PitStop AI - AI-Powered Automotive Workshop Operations Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(requests.router)
app.include_router(work_orders.router)
app.include_router(scheduling.router)
app.include_router(inventory.router)
app.include_router(estimates.router)
app.include_router(integrations.router)
app.include_router(analytics.router)
app.include_router(audit.router)
app.include_router(automation.router)
app.include_router(seed.router)
app.include_router(customer_portal.router)

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        # Check if seeded
        from app.models.entities import Workshop
        ws = db.query(Workshop).first()
        if not ws:
            print("Auto-seeding initial PitStop AI operational workshop records...")
            seed_database(db)
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
