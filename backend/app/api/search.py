from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.topic import TopicSearchResponse
from app.services.topic_service import search_topic

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/search", response_model=TopicSearchResponse)
def search(
    q: str = Query(..., min_length=2),
    category: str | None = None,
    db: Session = Depends(get_db),
):
    return search_topic(db, q, category)
