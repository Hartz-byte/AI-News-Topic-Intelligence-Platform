from __future__ import annotations
from functools import lru_cache

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

@lru_cache
def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)

def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vectors]
