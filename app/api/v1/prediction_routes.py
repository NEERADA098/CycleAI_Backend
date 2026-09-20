from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.services.prediction_service import prediction_service

router = APIRouter()


class PredictionResponse(BaseModel):
    user_id: str
    predicted_days: float
    confidence: str
    method: str
    message: str
    cycles_used: int


@router.get("/predict/{user_id}", response_model=PredictionResponse)
def predict_next_cycle(user_id: str, db: Session = Depends(get_db)):
    """
    Predicts the next cycle length for a specific user.

    Fetches their cycle history from PostgreSQL, runs it through
    the LSTM model, and returns a prediction with confidence level.

    The method field tells you which prediction approach was used:
    - "lstm": Real AI prediction (best)
    - "average": Simple average (when < 5 cycles available)
    - "default": 28-day default (no data)
    - "fallback": Error fallback
    """
    result = db.execute(text("""
        SELECT cycle_length
        FROM cycle_logs
        WHERE user_id = :uid
          AND cycle_length IS NOT NULL
          AND cycle_length BETWEEN 21 AND 45
        ORDER BY start_date ASC
        LIMIT 20
    """), {"uid": user_id})

    cycle_lengths = [float(row[0]) for row in result.fetchall()]

    prediction = prediction_service.predict_next_cycle(cycle_lengths)

    return PredictionResponse(
        user_id=user_id,
        predicted_days=prediction["predicted_days"],
        confidence=prediction["confidence"],
        method=prediction["method"],
        message=prediction["message"],
        cycles_used=len(cycle_lengths),
    )


@router.get("/predict/global/stats")
def get_global_prediction_stats(db: Session = Depends(get_db)):
    """
    Returns aggregate statistics about cycle data in the system.
    Used by the research paper for dataset characterization.
    """
    result = db.execute(text("""
        SELECT
            COUNT(*) as total_logs,
            COUNT(DISTINCT user_id) as total_users,
            AVG(cycle_length) as avg_cycle_length,
            MIN(cycle_length) as min_cycle_length,
            MAX(cycle_length) as max_cycle_length,
            STDDEV(cycle_length) as std_cycle_length
        FROM cycle_logs
        WHERE cycle_length IS NOT NULL
          AND cycle_length BETWEEN 21 AND 45
    """))

    row = result.fetchone()

    return {
        "total_cycle_logs": row[0],
        "total_users": row[1],
        "avg_cycle_length": round(float(row[2] or 0), 2),
        "min_cycle_length": row[3],
        "max_cycle_length": row[4],
        "std_cycle_length": round(float(row[5] or 0), 2),
        "model_status": "lstm" if prediction_service._initialized else "not_loaded"
    }
