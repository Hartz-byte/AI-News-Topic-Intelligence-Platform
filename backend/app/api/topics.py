from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Article
from app.core.cache import get_cache, set_cache, generate_cache_key

router = APIRouter(prefix="/api/topics", tags=["topics"])

@router.get("/timeline")
def get_timeline(
    topic: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
):
    cluster_key = topic.lower()
    cache_key = generate_cache_key("timeline", cluster_key=cluster_key)
    cached = get_cache(cache_key)
    if cached:
        return cached

    articles = db.query(Article).filter(Article.cluster_key == cluster_key).order_by(Article.published_at.asc(), Article.created_at.asc()).limit(50).all()
    if not articles:
        # fallback to ilike if cluster_key exact match fails
        articles = db.query(Article).filter(Article.title.ilike(f"%{topic}%")).order_by(Article.published_at.asc(), Article.created_at.asc()).limit(50).all()
        if not articles:
            raise HTTPException(status_code=404, detail="Topic timeline not found")

    timeline = []
    for a in articles:
        dt = a.published_at or a.created_at
        timeline.append({
            "id": a.id,
            "title": a.title,
            "source": a.source_name,
            "date": dt.isoformat() if dt else None,
            "url": a.url
        })
        
    set_cache(cache_key, timeline, expire_seconds=3600)
    return timeline
