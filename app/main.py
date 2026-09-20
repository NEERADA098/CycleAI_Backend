from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.cycle_routes import router as cycle_router
from app.api.v1.asha_routes import router as asha_router
from app.api.v1.chat_routes import router as chat_router
from app.api.v1.location_routes import router as location_router
from app.api.v1.incinerator_routes import router as incinerator_router
from app.api.v1.supply_routes import router as supply_router
from app.api.v1.prediction_routes import router as prediction_router
from app.services.mqtt_subscriber import start_mqtt_subscriber

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
app.include_router(chat_router, prefix="/api/v1", tags=["Chatbot"])
app.include_router(location_router, prefix="/api/v1", tags=["Geospatial"])
app.include_router(incinerator_router, prefix="/api/v1", tags=["IoT Incinerators"])
app.include_router(supply_router, prefix="/api/v1", tags=["Supply Analytics"])
app.include_router(prediction_router, prefix="/api/v1", tags=["AI Prediction"])

@app.on_event("startup")
async def startup_event():
    start_mqtt_subscriber()

@app.get("/")
def root():
    return {
        "message": "CycleAI Backend is running",
        "docs": "/docs",
        "version": settings.version
    }
