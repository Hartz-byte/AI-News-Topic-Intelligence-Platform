from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.topic_service import ingest_all_categories

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/refresh")
def refresh(db: Session = Depends(get_db)):
    return {"ingested": ingest_all_categories(db, limit=8)}
