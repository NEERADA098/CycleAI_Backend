from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float
from sqlalchemy.sql import func
from app.core.database import Base

class CycleLog(Base):
    __tablename__ = "cycle_logs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    cycle_length = Column(Integer, nullable=True)
    period_length = Column(Integer, nullable=True)
    flow_intensity = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_synced = Column(Boolean, default=True)


class SymptomLog(Base):
    __tablename__ = "symptom_logs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    log_date = Column(DateTime, nullable=False)
    symptom_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    is_synced = Column(Boolean, default=True)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    uid = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    role = Column(String, default="user")
    date_of_birth = Column(DateTime, nullable=True)
    menarche_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    last_active = Column(DateTime, nullable=True)


class HealthLocation(Base):
    """
    Stores disposal sites and pad supply points with GPS coordinates.
    Populated by ASHA workers and administrators via the dashboard.
    """
    __tablename__ = "health_locations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location_type = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class IncineratorStatus(Base):
    """
    Stores real-time sensor readings from smart incinerators.
    Each row is one reading from one device at one point in time.
    The ESP32 publishes via MQTT, FastAPI saves here.
    """
    __tablename__ = "incinerator_status"

    id = Column(String, primary_key=True, index=True)
    device_id = Column(String, nullable=False, index=True)
    temperature_celsius = Column(Float, nullable=True)
    is_burning = Column(Boolean, default=False)
    fill_percentage = Column(Float, nullable=True)
    usage_count = Column(Integer, default=0)
    battery_level = Column(Float, nullable=True)
    is_online = Column(Boolean, default=True)
    recorded_at = Column(DateTime, server_default=func.now())
