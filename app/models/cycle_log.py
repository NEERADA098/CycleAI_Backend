from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float
from sqlalchemy.sql import func
from app.core.database import Base

class CycleLog(Base):
    """
    Represents one logged menstrual period in PostgreSQL.
    Mirrors the cycle_logs SQLite table on the device,
    but this version lives in the cloud.
    """
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
    is_synced = Column(Boolean, default=True)  # Always True server-side

class SymptomLog(Base):
    """
    Represents one logged symptom in PostgreSQL.
    Mirrors the symptom_logs SQLite table.
    """
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
    """
    Stores user profile data synced from Firebase Auth.
    Firebase handles authentication (who you are),
    PostgreSQL handles profile data (what we know about you).
    """
    __tablename__ = "user_profiles"

    uid = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    role = Column(String, default="user")
    date_of_birth = Column(DateTime, nullable=True)
    # CLINICAL: stored to suppress irregularity warnings
    # for users within 2 years of menarche (per gynecologist)
    menarche_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    last_active = Column(DateTime, nullable=True)
