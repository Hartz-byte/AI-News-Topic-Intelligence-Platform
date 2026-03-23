from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.topic import TrendingResponse
from app.services.topic_service import get_trending, ingest_category

router = APIRouter(prefix="/api", tags=["trending"])

@router.get("/trending", response_model=TrendingResponse)
def trending(
    category: str = Query("technology"),
    refresh: bool = Query(False),
    db: Session = Depends(get_db),
):
    if refresh:
        ingest_category(db, category, limit=12)
    topics = get_trending(db, category)
    return {"category": category, "topics": topics}
