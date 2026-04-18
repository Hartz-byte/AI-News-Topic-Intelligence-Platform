from __future__ import annotations
from functools import lru_cache

@lru_cache(maxsize=1)
def get_model():
    from fastembed import TextEmbedding
    return TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    # fastembed.embed returns a generator
    embeddings = list(model.embed(texts))
    return [v.tolist() for v in embeddings]
