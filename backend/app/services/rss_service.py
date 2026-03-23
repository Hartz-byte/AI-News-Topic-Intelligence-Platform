from __future__ import annotations
import feedparser

GOOGLE_NEWS_RSS = {
    "technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en",
    "business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",
    "sports": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en",
    "health": "https://news.google.com/rss/headlines/section/topic/HEALTH?hl=en-IN&gl=IN&ceid=IN:en",
    "science": "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=en-IN&gl=IN&ceid=IN:en",
    "entertainment": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-IN&gl=IN&ceid=IN:en",
    "world": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
}

def fetch_category_feed(category: str, limit: int = 20) -> list[dict]:
    url = GOOGLE_NEWS_RSS.get(category, GOOGLE_NEWS_RSS["world"])
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:limit]:
        items.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "source_name": entry.get("source", {}).get("title", "Google News"),
            "published_at": entry.get("published", None),
            "category": category,
        })
    return items
