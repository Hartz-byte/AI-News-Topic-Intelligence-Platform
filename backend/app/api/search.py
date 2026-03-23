from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.topic import TopicSearchResponse
from app.services.topic_service import search_topic
from app.core.cache import get_cache, set_cache, generate_cache_key

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/search", response_model=TopicSearchResponse)
def search(
    q: str = Query(..., min_length=2),
    category: str | None = None,
    db: Session = Depends(get_db),
):
    cache_key = generate_cache_key("search", q=q, category=category)
    cached = get_cache(cache_key)
    if cached:
        return cached

    result = search_topic(db, q, category)
    set_cache(cache_key, result, expire_seconds=86400)
    return result
