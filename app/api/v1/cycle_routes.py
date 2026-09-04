from fastapi import APIRouter, Depends
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


@router.post("/cycles/", response_model=CycleLogResponse)
def create_cycle_log(cycle: CycleLogCreate, db: Session = Depends(get_db)):
    existing = db.query(CycleLog).filter(CycleLog.id == cycle.id).first()
    if existing:
        return existing
    db_cycle = CycleLog(**cycle.model_dump())
    db.add(db_cycle)
    db.commit()
    db.refresh(db_cycle)
    return db_cycle


@router.get("/cycles/{user_id}", response_model=List[CycleLogResponse])
def get_cycles_for_user(user_id: str, db: Session = Depends(get_db)):
    return db.query(CycleLog).filter(
        CycleLog.user_id == user_id
    ).order_by(CycleLog.start_date.desc()).all()


@router.post("/symptoms/", response_model=SymptomLogResponse)
def create_symptom_log(symptom: SymptomLogCreate, db: Session = Depends(get_db)):
    existing = db.query(SymptomLog).filter(SymptomLog.id == symptom.id).first()
    if existing:
        return existing
    db_symptom = SymptomLog(**symptom.model_dump())
    db.add(db_symptom)
    db.commit()
    db.refresh(db_symptom)
    return db_symptom


@router.get("/symptoms/{user_id}", response_model=List[SymptomLogResponse])
def get_symptoms_for_user(user_id: str, db: Session = Depends(get_db)):
    return db.query(SymptomLog).filter(
        SymptomLog.user_id == user_id
    ).order_by(SymptomLog.log_date.desc()).all()


@router.post("/sync/", response_model=SyncResponse)
def sync_data(payload: SyncPayload, db: Session = Depends(get_db)):
    synced_cycles = 0
    synced_symptoms = 0

    for cycle in payload.cycle_logs:
        if not db.query(CycleLog).filter(CycleLog.id == cycle.id).first():
            db.add(CycleLog(**cycle.model_dump()))
            synced_cycles += 1

    for symptom in payload.symptom_logs:
        if not db.query(SymptomLog).filter(SymptomLog.id == symptom.id).first():
            db.add(SymptomLog(**symptom.model_dump()))
            synced_symptoms += 1

    db.commit()

    return SyncResponse(
        synced_cycles=synced_cycles,
        synced_symptoms=synced_symptoms,
        message=f"Synced {synced_cycles} cycles and {synced_symptoms} symptoms"
    )


@router.get("/health/")
def health_check():
    return {"status": "healthy", "service": "CycleAI Backend"}
