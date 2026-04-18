from __future__ import annotations
import trafilatura
import subprocess
from functools import lru_cache

@lru_cache(maxsize=1)
def get_spacy_model():
    import spacy
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
        return spacy.load("en_core_web_sm")

def extract_article_text(url: str) -> str:
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ""
        text = trafilatura.extract(downloaded, include_comments=False, include_links=False)
        return text or ""
    except Exception:
        return ""

def extract_entities(text: str) -> list[dict]:
    if not text:
        return []
    nlp = get_spacy_model()
    doc = nlp(text[:5000])
    entities = {}
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LOC", "PRODUCT"]:
            name = ent.text.strip().title()
            if len(name) > 2:
                entities[name] = ent.label_
    return [{"name": name, "entity_type": etype} for name, etype in entities.items()]

def extract_keywords(text: str, top_n: int = 5) -> list[str]:
    """Lightweight spaCy-based keyword extraction to save memory."""
    if not text:
        return []
    nlp = get_spacy_model()
    doc = nlp(text[:3000].lower())
    
    # Extract noun chunks and frequent nouns/proper nouns
    keywords = []
    for chunk in doc.noun_chunks:
        cln = chunk.text.strip()
        if len(cln) > 3 and " " in cln: # Prefer phrases
            keywords.append(cln)
    
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 3:
            keywords.append(token.text)
            
    # Simple frequency ranking
    from collections import Counter
    counts = Counter(keywords)
    return [k for k, v in counts.most_common(top_n)]

