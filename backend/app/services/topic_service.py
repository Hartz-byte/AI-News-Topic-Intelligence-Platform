from __future__ import annotations
import json
from collections import Counter, defaultdict
from sqlalchemy.orm import Session
from app.db.models import Article
from app.services.rss_service import fetch_category_feed
from app.services.extraction_service import extract_article_text
from app.services.storage_service import upsert_articles
from app.services.embedding_service import embed_texts
from app.services.vector_service import ensure_collection, upsert_article_vector
from app.services.llm_service import summarize_topic

CATEGORIES = ["technology", "business", "sports", "health", "science", "entertainment", "world"]

def ingest_category(db: Session, category: str, limit: int = 20) -> list[Article]:
    raw_items = fetch_category_feed(category, limit=limit)
    enriched = []
    for item in raw_items:
        text = extract_article_text(item["url"])
        item["cleaned_content"] = text[:20000]
        item["summary"] = (text[:350] + "...") if text else item["title"]
        item["cluster_key"] = item["title"][:80].lower()
        enriched.append(item)

    saved = upsert_articles(db, enriched)
    if saved:
        ensure_collection()
        vectors = embed_texts([f"{a.title}. {a.cleaned_content[:1000]}" for a in saved])
        for article, vector in zip(saved, vectors):
            upsert_article_vector(article.id, vector, {
                "title": article.title,
                "source_name": article.source_name,
                "category": article.category,
                "url": article.url
            })
    return saved

def ingest_all_categories(db: Session, limit: int = 10) -> dict:
    out = {}
    for category in CATEGORIES:
        out[category] = len(ingest_category(db, category, limit))
    return out

def get_trending(db: Session, category: str, limit: int = 10) -> list[dict]:
    rows = db.query(Article).filter(Article.category == category).order_by(Article.created_at.desc()).limit(200).all()
    counter = Counter()
    bucket = defaultdict(list)
    for row in rows:
        topic = row.title.split(" - ")[0][:120]
        counter[topic] += 1
        bucket[topic].append(row)
    results = []
    for topic, count in counter.most_common(limit):
        results.append({
            "topic": topic,
            "category": category,
            "trend_score": float(count),
            "article_count": count,
        })
    return results

def search_topic(db: Session, query: str, category: str | None = None, limit: int = 8) -> dict:
    q = db.query(Article)
    if category:
        q = q.filter(Article.category == category)
    rows = q.filter(Article.title.ilike(f"%{query}%")).order_by(Article.created_at.desc()).limit(limit).all()

    if not rows:
        for cat in [category] if category else ["technology", "business", "world"]:
            ingest_category(db, cat, limit=10)
        q = db.query(Article)
        if category:
            q = q.filter(Article.category == category)
        rows = q.filter(Article.title.ilike(f"%{query}%")).order_by(Article.created_at.desc()).limit(limit).all()

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
