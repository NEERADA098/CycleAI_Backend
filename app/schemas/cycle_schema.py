from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ── Cycle Schemas ──────────────────────────────────────────────────

class CycleLogCreate(BaseModel):
    """Shape of data the Flutter app sends when logging a period."""
    id: str  # UUID generated on device - same ID used in SQLite
    user_id: str
    start_date: datetime
    end_date: Optional[datetime] = None
    cycle_length: Optional[int] = None
    period_length: Optional[int] = None
    flow_intensity: Optional[str] = None
    notes: Optional[str] = None

class CycleLogResponse(BaseModel):
    """Shape of data we send back to the Flutter app."""
    id: str
    user_id: str
    start_date: datetime
    end_date: Optional[datetime] = None
    cycle_length: Optional[int] = None
    period_length: Optional[int] = None
    flow_intensity: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # Allows creating from SQLAlchemy model

# ── Symptom Schemas ────────────────────────────────────────────────

class SymptomLogCreate(BaseModel):
    """Shape of data the Flutter app sends when logging a symptom."""
    id: str
    user_id: str
    log_date: datetime
    symptom_type: str
    severity: str
    notes: Optional[str] = None

class SymptomLogResponse(BaseModel):
    id: str
    user_id: str
    log_date: datetime
    symptom_type: str
    severity: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ── Sync Schema ────────────────────────────────────────────────────

class SyncPayload(BaseModel):
    """
    Batch sync - Flutter app sends ALL unsynced records at once.
    This is more efficient than one HTTP request per record,
    which matters in low-connectivity rural environments.
    """
    user_id: str
    cycle_logs: list[CycleLogCreate] = []
    symptom_logs: list[SymptomLogCreate] = []

class SyncResponse(BaseModel):
    synced_cycles: int
    synced_symptoms: int
    message: str
