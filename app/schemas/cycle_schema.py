from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CycleLogCreate(BaseModel):
    id: str
    user_id: str
    start_date: datetime
    end_date: Optional[datetime] = None
    cycle_length: Optional[int] = None
    period_length: Optional[int] = None
    flow_intensity: Optional[str] = None
    notes: Optional[str] = None

class CycleLogResponse(BaseModel):
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
        from_attributes = True


class SymptomLogCreate(BaseModel):
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


class SyncPayload(BaseModel):
    user_id: str
    cycle_logs: list[CycleLogCreate] = []
    symptom_logs: list[SymptomLogCreate] = []

class SyncResponse(BaseModel):
    synced_cycles: int
    synced_symptoms: int
    message: str
