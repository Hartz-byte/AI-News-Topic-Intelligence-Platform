from __future__ import annotations
import json
from collections import Counter, defaultdict
from sqlalchemy.orm import Session
from app.db.models import Article
from app.services.rss_service import fetch_category_feed, fetch_search_feed
from app.services.extraction_service import extract_article_text, extract_entities, extract_keywords
from app.services.storage_service import upsert_articles
from app.services.embedding_service import embed_texts
from app.services.vector_service import ensure_collection, upsert_article_vector
from app.services.llm_service import summarize_topic

CATEGORIES = ["technology", "business", "sports", "health", "science", "entertainment", "world"]

def ingest_query(db: Session, query: str, limit: int = 10) -> list[Article]:
    raw_items = fetch_search_feed(query, limit=limit)
    return _process_and_save(db, raw_items, query.lower())

def ingest_category(db: Session, category: str, limit: int = 20) -> list[Article]:
    raw_items = fetch_category_feed(category, limit=limit)
    return _process_and_save(db, raw_items, None)

def _process_and_save(db: Session, raw_items: list[dict], forced_cluster: str | None = None) -> list[Article]:
    from app.services.vector_service import search_similar
    enriched = []
    for item in raw_items:
        text = extract_article_text(item["url"])
        item["cleaned_content"] = text[:20000]
        item["summary"] = (text[:350] + "...") if text else item["title"]
        item["entities"] = extract_entities(text)
        item["keywords"] = extract_keywords(text)
        enriched.append(item)

    ensure_collection()
    if not enriched: return []

    vectors = embed_texts([f"{a['title']}. {a.get('cleaned_content', '')[:1000]}" for a in enriched])
    
    for item, vector in zip(enriched, vectors):
        if forced_cluster:
            item["cluster_key"] = forced_cluster
        else:
            hits = search_similar(vector, limit=1)
            if hits and hits[0].score > 0.85:
                item["cluster_key"] = hits[0].payload.get("cluster_key") or item["title"][:80].lower()
            else:
                item["cluster_key"] = item["title"][:80].lower()

    saved = upsert_articles(db, enriched)
    saved_urls = {a.url: a for a in saved}
    
    for item, vector in zip(enriched, vectors):
        article = saved_urls.get(item["url"])
        if article:
            upsert_article_vector(article.id, vector, {
                "title": article.title,
                "source_name": article.source_name,
                "category": article.category,
                "url": article.url,
                "cluster_key": article.cluster_key
            })
    return saved

def ingest_all_categories(db: Session, limit: int = 10) -> dict:
    out = {}
    for category in CATEGORIES:
        out[category] = len(ingest_category(db, category, limit))
    return out

def get_trending(db: Session, category: str, limit: int = 10) -> list[dict]:
    from datetime import datetime, timezone
    rows = db.query(Article).filter(Article.category == category).order_by(Article.created_at.desc()).limit(300).all()
    
    bucket = defaultdict(list)
    for row in rows:
        bucket[row.cluster_key].append(row)
        
    results = []
    now = datetime.now(timezone.utc)
    for cluster_key, articles in bucket.items():
        article_volume = len(articles)
        source_diversity = len(set([a.source_name for a in articles]))
        
        # Recency score (0 to 1 based on how many hours old the newest article is)
        times = []
        for a in articles:
            dt = a.published_at or a.created_at
            if dt:
                # Handle naive datetimes from DB
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                times.append(dt)
        
        newest_time = max(times) if times else now
        hours_old = (now - newest_time).total_seconds() / 3600
        recency_score = max(0.0, 1.0 - (hours_old / 48.0)) # Decays over 48 hours
        
        # Calculate score (out of 10 approx)
        trend_score = (
            (0.40 * recency_score * 10) + 
            (0.30 * min(article_volume, 10)) + 
            (0.30 * min(source_diversity, 5) * 2)
        )
        
        results.append({
            "topic": cluster_key.title(),
            "category": category,
            "trend_score": round(trend_score, 2),
            "article_count": article_volume,
        })
        
    results.sort(key=lambda x: x["trend_score"], reverse=True)
    return results[:limit]

def search_topic(db: Session, query: str, category: str | None = None, limit: int = 8) -> dict:
    from app.services.vector_service import search_similar

    ensure_collection()
    query_vector = embed_texts([query])[0]
    hits = search_similar(query_vector, limit=limit * 2)

    rows = []
    if hits:
        # Only accept hits with a decent similarity score (e.g. 0.35+)
        qualified_hits = [h for h in hits if h.score > 0.35]
        if qualified_hits:
            hit_ids = [hit.id for hit in qualified_hits]
            q = db.query(Article).filter(Article.id.in_(hit_ids))
            if category:
                q = q.filter(Article.category == category)
            fetched_rows = q.all()
            fetched_rows.sort(key=lambda x: hit_ids.index(x.id) if x.id in hit_ids else 999)
            rows = fetched_rows[:limit]
        
    if not rows:
        # Real-time search if no local results
        ingest_query(db, query, limit=10)
        
        # Retry search with the newly ingested data
        hits = search_similar(query_vector, limit=limit * 2)
        qualified_hits = [h for h in hits if h.score > 0.35]
        if qualified_hits:
            hit_ids = [hit.id for hit in qualified_hits]
            q = db.query(Article).filter(Article.id.in_(hit_ids))
            if category:
                q = q.filter(Article.category == category)
            fetched_rows = q.all()
            fetched_rows.sort(key=lambda x: hit_ids.index(x.id) if x.id in hit_ids else 999)
            rows = fetched_rows[:limit]

    payload = [
        {
            "title": r.title,
            "source_name": r.source_name,
            "cleaned_content": r.cleaned_content,
            "category": r.category,
        } for r in rows
    ]
    llm_out = summarize_topic(query, payload)
    if isinstance(llm_out, str):
        llm_out = json.loads(llm_out)

    return {
        "query": query,
        "summary": llm_out.get("summary", ""),
        "key_facts": llm_out.get("key_facts", []),
        "category": llm_out.get("category", category or (rows[0].category if rows else "general")),
        "articles": rows,
    }
