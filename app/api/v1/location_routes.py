from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
import uuid
import math
from app.core.database import get_db
from app.models.cycle_log import HealthLocation

router = APIRouter()


class LocationResponse(BaseModel):
    id: str
    name: str
    location_type: str
    latitude: float
    longitude: float
    address: Optional[str]
    distance_km: Optional[float] = None

    class Config:
        from_attributes = True


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates straight-line distance between two GPS coordinates
    using the Haversine formula. Returns distance in kilometers.
    
    The Haversine formula accounts for the curvature of the Earth,
    which matters even at short distances for accurate results.
    """
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))


@router.get("/locations/nearby")
def get_nearby_locations(
    lat: float,
    lng: float,
    radius_km: float = 10.0,
    location_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(HealthLocation).filter(HealthLocation.is_active == True)
    if location_type:
        query = query.filter(HealthLocation.location_type == location_type)
    
    all_locations = query.all()
    
    nearby = []
    for loc in all_locations:
        distance = haversine_distance(lat, lng, loc.latitude, loc.longitude)
        if distance <= radius_km:
            nearby.append(LocationResponse(
                id=loc.id,
                name=loc.name,
                location_type=loc.location_type,
                latitude=loc.latitude,
                longitude=loc.longitude,
                address=loc.address,
                distance_km=round(distance, 2),
            ))
    
    nearby.sort(key=lambda x: x.distance_km)
    return nearby


@router.post("/locations/seed")
def seed_sample_locations(db: Session = Depends(get_db)):
    """Seeds sample disposal sites and supply points for Kerala.
    Run once to populate the database for testing."""
    
    existing = db.query(HealthLocation).count()
    if existing > 0:
        return {"message": f"Already have {existing} locations. Skipping seed."}
    
    sample_locations = [
        {
            "id": str(uuid.uuid4()),
            "name": "Kottayam District Hospital Incinerator",
            "location_type": "incinerator",
            "latitude": 9.5916,
            "longitude": 76.5222,
            "address": "Hospital Road, Kottayam, Kerala 686001",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Ettumanoor PHC Smart Incinerator",
            "location_type": "incinerator",
            "latitude": 9.6667,
            "longitude": 76.5500,
            "address": "Primary Health Centre, Ettumanoor, Kerala",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Kudumbashree Pad Distribution - Kottayam",
            "location_type": "supply_point",
            "latitude": 9.5800,
            "longitude": 76.5100,
            "address": "Kudumbashree District Mission, Kottayam",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ASHA Worker Collection Point - Changanacherry",
            "location_type": "supply_point",
            "latitude": 9.4444,
            "longitude": 76.5361,
            "address": "Community Health Centre, Changanacherry",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Vaikom PHC Incinerator",
            "location_type": "incinerator",
            "latitude": 9.7500,
            "longitude": 76.3920,
            "address": "Primary Health Centre, Vaikom, Kerala",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Government Girls School - Pad Bank",
            "location_type": "supply_point",
            "latitude": 9.6100,
            "longitude": 76.5300,
            "address": "Government Higher Secondary School, Kottayam",
        },
    ]
    
    for loc_data in sample_locations:
        db.add(HealthLocation(**loc_data))
    
    db.commit()
    return {"message": f"Seeded {len(sample_locations)} sample locations for Kerala"}


@router.get("/locations/all")
def get_all_locations(db: Session = Depends(get_db)):
    locations = db.query(HealthLocation).filter(
        HealthLocation.is_active == True
    ).all()
    return [
        LocationResponse(
            id=loc.id,
            name=loc.name,
            location_type=loc.location_type,
            latitude=loc.latitude,
            longitude=loc.longitude,
            address=loc.address,
        )
        for loc in locations
    ]
