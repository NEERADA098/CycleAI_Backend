from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.cycle_log import CycleLog, SymptomLog
from app.schemas.cycle_schema import (
    CycleLogCreate, CycleLogResponse,
    SymptomLogCreate, SymptomLogResponse,
    SyncPayload, SyncResponse
)

router = APIRouter()

# ── CYCLE LOG ENDPOINTS ────────────────────────────────────────────

@router.post("/cycles/", response_model=CycleLogResponse)
def create_cycle_log(cycle: CycleLogCreate, db: Session = Depends(get_db)):
    """
    Create one cycle log.
    Flutter app calls this URL with cycle data in the request body.
    FastAPI automatically validates the data matches CycleLogCreate.
    """
    # Check if this ID already exists (device may retry on network failure)
    existing = db.query(CycleLog).filter(CycleLog.id == cycle.id).first()
    if existing:
        return existing  # Return existing instead of creating duplicate

    db_cycle = CycleLog(**cycle.model_dump())
    db.add(db_cycle)
    db.commit()
    db.refresh(db_cycle)
    return db_cycle

@router.get("/cycles/{user_id}", response_model=List[CycleLogResponse])
def get_cycles_for_user(user_id: str, db: Session = Depends(get_db)):
    """
    Get all cycle logs for a specific user.
    The {user_id} in the URL is a path parameter -
    calling /cycles/abc123 returns cycles for user abc123.
    """
    cycles = db.query(CycleLog).filter(
        CycleLog.user_id == user_id
    ).order_by(CycleLog.start_date.desc()).all()
    return cycles

# ── SYMPTOM LOG ENDPOINTS ──────────────────────────────────────────

@router.post("/symptoms/", response_model=SymptomLogResponse)
def create_symptom_log(symptom: SymptomLogCreate, db: Session = Depends(get_db)):
    """Create one symptom log."""
    existing = db.query(SymptomLog).filter(
        SymptomLog.id == symptom.id
    ).first()
    if existing:
        return existing

    db_symptom = SymptomLog(**symptom.model_dump())
    db.add(db_symptom)
    db.commit()
    db.refresh(db_symptom)
    return db_symptom

@router.get("/symptoms/{user_id}", response_model=List[SymptomLogResponse])
def get_symptoms_for_user(user_id: str, db: Session = Depends(get_db)):
    """Get all symptom logs for a specific user."""
    symptoms = db.query(SymptomLog).filter(
        SymptomLog.user_id == user_id
    ).order_by(SymptomLog.log_date.desc()).all()
    return symptoms

# ── BATCH SYNC ENDPOINT ────────────────────────────────────────────

@router.post("/sync/", response_model=SyncResponse)
def sync_data(payload: SyncPayload, db: Session = Depends(get_db)):
    """
    Batch sync endpoint - the most important endpoint for rural users.

    WHY THIS EXISTS:
    A rural user may log 10 periods and 50 symptoms while offline.
    When she gets connectivity, we dont want 60 separate HTTP requests
    (slow, unreliable on weak connections). This endpoint accepts
    ALL unsynced data in one request and processes everything at once.

    This directly addresses the offline-first architecture requirement
    from your project literature review (Section 2.6).
    """
    synced_cycles = 0
    synced_symptoms = 0

    for cycle in payload.cycle_logs:
        existing = db.query(CycleLog).filter(
            CycleLog.id == cycle.id
        ).first()
        if not existing:
            db_cycle = CycleLog(**cycle.model_dump())
            db.add(db_cycle)
            synced_cycles += 1

    for symptom in payload.symptom_logs:
        existing = db.query(SymptomLog).filter(
            SymptomLog.id == symptom.id
        ).first()
        if not existing:
            db_symptom = SymptomLog(**symptom.model_dump())
            db.add(db_symptom)
            synced_symptoms += 1

    db.commit()

    return SyncResponse(
        synced_cycles=synced_cycles,
        synced_symptoms=synced_symptoms,
        message=f"Synced {synced_cycles} cycles and {synced_symptoms} symptoms successfully"
    )

@router.get("/health/")
def health_check():
    """
    Simple health check endpoint.
    Your Flutter app can call this to verify the server is reachable
    before attempting a full sync. Returns instantly with no DB query.
    """
    return {"status": "healthy", "service": "CycleAI Backend"}
