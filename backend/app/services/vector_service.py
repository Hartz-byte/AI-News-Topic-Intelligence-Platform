import json
from pinecone import Pinecone, ServerlessSpec
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.db.models import Article

settings = get_settings()
pc = Pinecone(api_key=settings.pinecone_api_key)
INDEX_NAME = "ai-news"

class FakePayload:
    def __init__(self, data):
        self.payload = data
    def get(self, key, default=None):
        return self.payload.get(key, default)

class Hit:
    def __init__(self, id, score, payload):
        self.id = int(id)
        self.score = score
        self.payload = FakePayload(payload)

def ensure_collection(vector_size: int = 384) -> None:
    if not settings.pinecone_api_key:
        return
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=vector_size,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

def upsert_article_vector(article_id: int, vector: list[float], payload: dict) -> None:
    if not settings.pinecone_api_key:
        return
    index = pc.Index(INDEX_NAME)
    # Pinecone metadata must be string, int, float, bool or list of strings
    # We'll clean the payload
    clean_metadata = {k: str(v) for k, v in payload.items()}
    index.upsert(vectors=[(str(article_id), vector, clean_metadata)])

def search_similar(vector: list[float], limit: int = 10):
    if not settings.pinecone_api_key:
        return []
    index = pc.Index(INDEX_NAME)
    results = index.query(
        vector=vector,
        top_k=limit,
        include_metadata=True
    )
    
    hits = []
    for match in results.matches:
        hits.append(Hit(
            id=match.id,
            score=match.score,
            payload=match.metadata
        ))
    return hits
