from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.services.cycle_analysis_service import cycle_analysis_service

router = APIRouter()

@router.get("/analyze/{user_id}")
def analyze_cycles(user_id: str, db: Session = Depends(get_db)):
    """
    Analyzes a user cycle history for irregularity patterns.
    Flags possible PCOS indicators without diagnosing.
    """
    result = db.execute(text("""
        SELECT cycle_length FROM cycle_logs
        WHERE user_id = :uid
        AND cycle_length IS NOT NULL
        AND cycle_length BETWEEN 15 AND 90
        ORDER BY start_date ASC
    """), {"uid": user_id})
    
    lengths = [float(row[0]) for row in result.fetchall()]
    return cycle_analysis_service.analyze_irregularity(lengths)
