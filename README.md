# CycleAI Backend

FastAPI backend server for the CycleAI menstrual health platform.

## What This Does

Provides REST API endpoints for:
- Cycle log storage and retrieval
- Symptom log storage and retrieval  
- Batch sync for offline-first mobile data
- ASHA worker community health analytics

## Stack

- **FastAPI** — REST API framework
- **PostgreSQL** — Primary database
- **SQLAlchemy** — ORM
- **Pydantic** — Data validation

## Running Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API documentation available at `http://localhost:8000/docs`

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/cycles/ | Create cycle log |
| GET | /api/v1/cycles/{user_id} | Get user cycles |
| POST | /api/v1/symptoms/ | Create symptom log |
| GET | /api/v1/symptoms/{user_id} | Get user symptoms |
| POST | /api/v1/sync/ | Batch sync offline data |
| GET | /api/v1/community/summary | ASHA community stats |
| GET | /api/v1/community/flagged-users | Users needing follow-up |
| GET | /api/v1/health/ | Health check |

## Part of CycleAI

This backend is one component of the CycleAI ecosystem.  
Flutter app: github.com/NEERADA098/Menstrual_Health_System
