from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.topic_service import ingest_all_categories

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/refresh")
def refresh(db: Session = Depends(get_db)):
    return {"ingested": ingest_all_categories(db, limit=8)}

import os
@router.get("/logs")
def get_logs(lines: int = 50):
    if not os.path.exists("app.log"):
        return {"logs": ["No logs generated yet."]}
    with open("app.log", "r", encoding="utf-8") as f:
        all_lines = f.readlines()
    return {"logs": all_lines[-lines:]}
