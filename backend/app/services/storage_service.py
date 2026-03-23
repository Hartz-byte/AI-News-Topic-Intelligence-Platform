from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from dateparser import parse as parse_date
from app.db.models import Article
from rapidfuzz.fuzz import token_set_ratio

def upsert_articles(db: Session, items: list[dict]) -> list[Article]:
    saved: list[Article] = []
    for item in items:
        existing = db.query(Article).filter(Article.url == item["url"]).first()
        if existing:
            saved.append(existing)
            continue

        title = item.get("title", "").strip()
        near_dup = db.query(Article).filter(Article.source_name == item.get("source_name", "unknown")).all()
        if any(token_set_ratio(title, x.title) > 96 for x in near_dup):
            continue

        published_at = parse_date(item.get("published_at")) if item.get("published_at") else None
        article = Article(
            title=title[:500],
            url=item["url"][:1200],
            source_name=item.get("source_name", "unknown")[:200],
            published_at=published_at if isinstance(published_at, datetime) else None,
            category=item.get("category", "general"),
            cleaned_content=item.get("cleaned_content", "")[:20000],
            summary=item.get("summary", "")[:5000],
            cluster_key=item.get("cluster_key"),
            entities=item.get("entities", []),
            keywords=item.get("keywords", []),
        )
        db.add(article)
        db.flush()
        saved.append(article)
    db.commit()
    return saved
