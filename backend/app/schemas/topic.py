from pydantic import BaseModel
from .article import ArticleOut

class TopicSearchResponse(BaseModel):
    query: str
    summary: str
    key_facts: list[str]
    category: str
    articles: list[ArticleOut]

class TrendingTopic(BaseModel):
    topic: str
    category: str
    trend_score: float
    article_count: int

class TrendingResponse(BaseModel):
    category: str
    topics: list[TrendingTopic]
