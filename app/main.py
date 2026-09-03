from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.cycle_routes import router as cycle_router

# Create all database tables automatically on startup
# SQLAlchemy reads your model classes and creates the corresponding
# tables in PostgreSQL if they dont exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="""
    CycleAI Backend API

    Handles data sync between Flutter app and PostgreSQL database.
    Provides endpoints for cycle logs, symptom logs, and batch sync
    for offline-first rural deployment.

    Built with FastAPI + SQLAlchemy + PostgreSQL.
    """,
    docs_url="/docs",  # Auto-generated interactive API documentation
)

# CORS - Cross Origin Resource Sharing
# Without this, browsers block requests from Flutter web to this server
# because they come from different origins (localhost:64034 vs localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: restrict to your actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes under /api/v1 prefix
app.include_router(cycle_router, prefix="/api/v1", tags=["Health Data"])

@app.get("/")
def root():
    return {
        "message": "CycleAI Backend is running",
        "docs": "/docs",
        "version": settings.version
    }
