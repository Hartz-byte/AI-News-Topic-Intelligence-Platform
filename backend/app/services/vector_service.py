import json
import numpy as np
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Article

def cosine_similarity(v1, v2):
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0: return 0.0
    return dot / (norm1 * norm2)

class FakePayload:
    def __init__(self, data):
        self.payload = data

    def get(self, key, default=None):
        return self.payload.get(key, default)

class Hit:
    def __init__(self, id, score, payload):
        self.id = id
        self.score = score
        self.payload = FakePayload(payload)

def ensure_collection(vector_size: int = 384) -> None:
    pass

def upsert_article_vector(article_id: int, vector: list[float], payload: dict) -> None:
    db = SessionLocal()
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if article:
            article.vector = json.dumps(vector) if not isinstance(vector, list) else vector
            db.commit()
    finally:
        db.close()

def search_similar(vector: list[float], limit: int = 10):
    db = SessionLocal()
    try:
        articles = db.query(Article).filter(Article.vector.isnot(None)).all()
        if not articles:
            return []
        
        target_vec = np.array(vector, dtype=float)
        hits = []
        for a in articles:
            v_data = json.loads(a.vector) if isinstance(a.vector, str) else a.vector
            if not v_data: continue
            v = np.array(v_data, dtype=float)
            score = cosine_similarity(target_vec, v)
            
            hits.append(Hit(
                id=a.id,
                score=score,
                payload={
                    "cluster_key": a.cluster_key,
                    "title": a.title,
                    "url": a.url
                }
            ))
        hits.sort(key=lambda x: x.score, reverse=True)
        return hits[:limit]
    finally:
        db.close()
