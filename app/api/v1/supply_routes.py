from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import uuid
from app.core.database import get_db
from app.models.cycle_log import SupplyDistribution, SupplyStock

router = APIRouter()


class DistributionCreate(BaseModel):
    location_id: str
    location_name: str
    pads_distributed: int
    beneficiary_count: int
    distributed_by: Optional[str] = None
    notes: Optional[str] = None


class DistributionResponse(BaseModel):
    id: str
    location_id: str
    location_name: str
    pads_distributed: int
    beneficiary_count: int
    distributed_by: Optional[str]
    distributed_at: datetime

    class Config:
        from_attributes = True


class StockResponse(BaseModel):
    location_id: str
    location_name: str
    current_stock: int
    minimum_threshold: int
    is_low_stock: bool
    last_restocked_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/supply/distribution", response_model=DistributionResponse)
def record_distribution(
    data: DistributionCreate,
    db: Session = Depends(get_db)
):
    distribution = SupplyDistribution(
        id=str(uuid.uuid4()),
        **data.model_dump(),
    )
    db.add(distribution)

    stock = db.query(SupplyStock).filter(
        SupplyStock.location_id == data.location_id
    ).first()

    if stock:
        stock.current_stock = max(0, stock.current_stock - data.pads_distributed)
    
    db.commit()
    db.refresh(distribution)
    return distribution


@router.get("/supply/stock", response_model=list[StockResponse])
def get_all_stock(db: Session = Depends(get_db)):
    stocks = db.query(SupplyStock).all()
    return [
        StockResponse(
            location_id=s.location_id,
            location_name=s.location_name,
            current_stock=s.current_stock,
            minimum_threshold=s.minimum_threshold,
            is_low_stock=s.current_stock <= s.minimum_threshold,
            last_restocked_at=s.last_restocked_at,
        )
        for s in stocks
    ]


@router.get("/supply/analytics")
def get_supply_analytics(db: Session = Depends(get_db)):
    """
    Returns aggregated supply analytics for the ASHA dashboard.
    Includes total distribution, trends, and low stock alerts.
    """
    total_pads = db.query(
        func.sum(SupplyDistribution.pads_distributed)
    ).scalar() or 0

    total_beneficiaries = db.query(
        func.sum(SupplyDistribution.beneficiary_count)
    ).scalar() or 0

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_distributions = db.query(
        func.sum(SupplyDistribution.pads_distributed)
    ).filter(
        SupplyDistribution.distributed_at >= thirty_days_ago
    ).scalar() or 0

    by_location = db.query(
        SupplyDistribution.location_name,
        func.sum(SupplyDistribution.pads_distributed).label('total_pads'),
        func.sum(SupplyDistribution.beneficiary_count).label('total_beneficiaries'),
        func.count(SupplyDistribution.id).label('distribution_count'),
    ).group_by(
        SupplyDistribution.location_name
    ).order_by(
        desc('total_pads')
    ).all()

    low_stock_locations = db.query(SupplyStock).filter(
        SupplyStock.current_stock <= SupplyStock.minimum_threshold
    ).all()

    return {
        "total_pads_distributed": total_pads,
        "total_beneficiaries": total_beneficiaries,
        "distributed_last_30_days": recent_distributions,
        "by_location": [
            {
                "location": row.location_name,
                "total_pads": row.total_pads,
                "total_beneficiaries": row.total_beneficiaries,
                "distribution_count": row.distribution_count,
            }
            for row in by_location
        ],
        "low_stock_alerts": [
            {
                "location_id": s.location_id,
                "location_name": s.location_name,
                "current_stock": s.current_stock,
                "minimum_threshold": s.minimum_threshold,
            }
            for s in low_stock_locations
        ],
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.post("/supply/seed")
def seed_supply_data(db: Session = Depends(get_db)):
    """Seeds sample stock levels and distribution history for Kerala."""
    existing = db.query(SupplyStock).count()
    if existing > 0:
        return {"message": f"Already have {existing} stock records."}

    sample_stocks = [
        {
            "id": str(uuid.uuid4()),
            "location_id": "SP001",
            "location_name": "Kudumbashree Pad Distribution - Kottayam",
            "current_stock": 120,
            "minimum_threshold": 50,
            "last_restocked_at": datetime.utcnow() - timedelta(days=7),
        },
        {
            "id": str(uuid.uuid4()),
            "location_id": "SP002",
            "location_name": "ASHA Worker Collection Point - Changanacherry",
            "current_stock": 35,
            "minimum_threshold": 50,
            "last_restocked_at": datetime.utcnow() - timedelta(days=21),
        },
        {
            "id": str(uuid.uuid4()),
            "location_id": "SP003",
            "location_name": "Government Girls School - Pad Bank",
            "current_stock": 85,
            "minimum_threshold": 30,
            "last_restocked_at": datetime.utcnow() - timedelta(days=3),
        },
    ]

    sample_distributions = [
        {
            "id": str(uuid.uuid4()),
            "location_id": "SP001",
            "location_name": "Kudumbashree Pad Distribution - Kottayam",
            "pads_distributed": 30,
            "beneficiary_count": 15,
            "distributed_by": "ASHA Worker - Ward 4",
        },
        {
            "id": str(uuid.uuid4()),
            "location_id": "SP001",
            "location_name": "Kudumbashree Pad Distribution - Kottayam",
            "pads_distributed": 20,
            "beneficiary_count": 10,
            "distributed_by": "ASHA Worker - Ward 4",
        },
        {
            "id": str(uuid.uuid4()),
            "location_id": "SP002",
            "location_name": "ASHA Worker Collection Point - Changanacherry",
            "pads_distributed": 65,
            "beneficiary_count": 32,
            "distributed_by": "ASHA Worker - Ward 7",
        },
        {
            "id": str(uuid.uuid4()),
            "location_id": "SP003",
            "location_name": "Government Girls School - Pad Bank",
            "pads_distributed": 45,
            "beneficiary_count": 45,
            "distributed_by": "School Health Teacher",
        },
    ]

    for stock in sample_stocks:
        db.add(SupplyStock(**stock))
    for dist in sample_distributions:
        db.add(SupplyDistribution(**dist))

    db.commit()
    return {
        "message": f"Seeded {len(sample_stocks)} stock records "
                   f"and {len(sample_distributions)} distribution events"
    }
