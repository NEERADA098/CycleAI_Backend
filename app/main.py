from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.cycle_routes import router as cycle_router
from app.api.v1.asha_routes import router as asha_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="CycleAI Backend API — offline-first menstrual health data sync for rural deployment.",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cycle_router, prefix="/api/v1", tags=["Health Data"])
app.include_router(asha_router, prefix="/api/v1", tags=["ASHA Dashboard"])

@app.get("/")
def root():
    return {
        "message": "CycleAI Backend is running",
        "docs": "/docs",
        "version": settings.version
    }
