from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Dependency function that provides a database session.
    FastAPI calls this automatically for routes that need DB access.
    The try/finally ensures the session is always closed,
    even if an error occurs - preventing connection leaks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
