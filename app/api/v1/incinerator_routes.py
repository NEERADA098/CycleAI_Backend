from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from app.core.database import get_db
from app.models.cycle_log import IncineratorStatus

router = APIRouter()


class IncineratorStatusResponse(BaseModel):
    device_id: str
    temperature_celsius: Optional[float]
    is_burning: bool
    fill_percentage: Optional[float]
    usage_count: int
    battery_level: Optional[float]
    is_online: bool
    recorded_at: datetime

    class Config:
        from_attributes = True


class IncineratorStatusCreate(BaseModel):
    device_id: str
    temperature_celsius: Optional[float] = None
    is_burning: bool = False
    fill_percentage: Optional[float] = None
    usage_count: int = 0
    battery_level: Optional[float] = None
    is_online: bool = True


@router.get("/incinerators/{device_id}/status",
            response_model=IncineratorStatusResponse)
def get_incinerator_status(device_id: str, db: Session = Depends(get_db)):
    """Get the most recent status reading for a specific incinerator."""
    status = db.query(IncineratorStatus).filter(
        IncineratorStatus.device_id == device_id
    ).order_by(desc(IncineratorStatus.recorded_at)).first()

    if not status:
        return IncineratorStatusResponse(
            device_id=device_id,
            temperature_celsius=None,
            is_burning=False,
            fill_percentage=None,
            usage_count=0,
            battery_level=None,
            is_online=False,
            recorded_at=datetime.utcnow(),
        )
    return status


@router.get("/incinerators/", response_model=list[IncineratorStatusResponse])
def get_all_incinerators(db: Session = Depends(get_db)):
    """Get latest status for all known incinerators."""
    subquery = db.query(
        IncineratorStatus.device_id,
        db.query(IncineratorStatus.recorded_at).filter(
            IncineratorStatus.device_id == IncineratorStatus.device_id
        ).order_by(desc(IncineratorStatus.recorded_at)).limit(1).as_scalar()
    )

    statuses = db.query(IncineratorStatus).order_by(
        IncineratorStatus.device_id,
        desc(IncineratorStatus.recorded_at)
    ).all()

    seen = set()
    latest = []
    for s in statuses:
        if s.device_id not in seen:
            seen.add(s.device_id)
            latest.append(s)
    return latest


@router.post("/incinerators/reading",
             response_model=IncineratorStatusResponse)
def record_incinerator_reading(
    data: IncineratorStatusCreate,
    db: Session = Depends(get_db)
):
    """
    Receives a sensor reading and saves it.
    Called by the MQTT subscriber when a message arrives,
    or directly by the ESP32 via HTTP as a fallback.
    """
    status = IncineratorStatus(
        id=str(uuid.uuid4()),
        **data.model_dump(),
    )
    db.add(status)
    db.commit()
    db.refresh(status)
    return status
