from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    url = Column(String(1200), nullable=False, unique=True, index=True)
    source_name = Column(String(200), nullable=False, default="unknown")
    published_at = Column(DateTime(timezone=True), nullable=True)
    category = Column(String(100), nullable=False, default="general")
    language = Column(String(20), nullable=False, default="en")
    cleaned_content = Column(Text, nullable=False, default="")
    summary = Column(Text, nullable=False, default="")
    cluster_key = Column(String(250), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(300), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=False, default="general")
    summary = Column(Text, nullable=False, default="")
    trend_score = Column(Float, nullable=False, default=0.0)
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TopicArticle(Base):
    __tablename__ = "topic_articles"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
