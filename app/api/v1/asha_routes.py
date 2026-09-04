from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.cycle_log import CycleLog, SymptomLog, UserProfile

router = APIRouter()


@router.get("/community/summary")
def get_community_summary(db: Session = Depends(get_db)):
    total_users = db.query(func.count(distinct(UserProfile.uid))).scalar() or 0

    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = db.query(
        func.count(distinct(CycleLog.user_id))
    ).filter(CycleLog.created_at >= week_ago).scalar() or 0

    total_cycles = db.query(func.count(CycleLog.id)).scalar() or 0
    total_symptoms = db.query(func.count(SymptomLog.id)).scalar() or 0

    severe_cases = db.query(
        func.count(distinct(SymptomLog.user_id))
    ).filter(SymptomLog.severity == "severe").scalar() or 0

    return {
        "total_users": total_users,
        "active_this_week": active_users,
        "total_cycles_logged": total_cycles,
        "total_symptoms_logged": total_symptoms,
        "users_with_severe_symptoms": severe_cases,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/community/flagged-users")
def get_flagged_users(db: Session = Depends(get_db)):
    severe_users = db.query(
        SymptomLog.user_id,
        func.count(SymptomLog.id).label("severe_count"),
        func.max(SymptomLog.log_date).label("last_log"),
    ).filter(
        SymptomLog.severity == "severe"
    ).group_by(
        SymptomLog.user_id
    ).having(
        func.count(SymptomLog.id) >= 3
    ).all()

    return [
        {
            "user_id": row.user_id,
            "severe_symptom_count": row.severe_count,
            "last_logged": row.last_log.isoformat() if row.last_log else None,
            "flag_reason": "3+ severe symptom entries",
        }
        for row in severe_users
    ]
