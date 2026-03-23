from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.topic import TrendingResponse
from app.services.topic_service import get_trending, ingest_category
from app.core.cache import get_cache, set_cache, generate_cache_key

router = APIRouter(prefix="/api", tags=["trending"])

@router.get("/trending", response_model=TrendingResponse)
def trending(
    category: str = Query("technology"),
    refresh: bool = Query(False),
    db: Session = Depends(get_db),
):
    cache_key = generate_cache_key("trending", category=category)
    
    if refresh:
        ingest_category(db, category, limit=12)
    else:
        cached = get_cache(cache_key)
        if cached:
            return cached
            
    topics = get_trending(db, category)
    response_data = {"category": category, "topics": topics}
    
    set_cache(cache_key, response_data, expire_seconds=600)
    return response_data
