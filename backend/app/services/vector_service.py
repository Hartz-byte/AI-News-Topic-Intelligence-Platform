from __future__ import annotations
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.config import get_settings

settings = get_settings()

client = QdrantClient(url=settings.qdrant_url)

def ensure_collection(vector_size: int = 384) -> None:
    collections = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in collections:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

def upsert_article_vector(article_id: int, vector: list[float], payload: dict) -> None:
    client.upsert(
        collection_name=settings.qdrant_collection,
        points=[PointStruct(id=article_id, vector=vector, payload=payload)]
    )

def search_similar(vector: list[float], limit: int = 10):
    return client.search(
        collection_name=settings.qdrant_collection,
        query_vector=vector,
        limit=limit,
    )
