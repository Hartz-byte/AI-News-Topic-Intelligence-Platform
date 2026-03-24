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

@lru_cache(maxsize=1)
def get_kw_model():
    from keybert import KeyBERT
    return KeyBERT()

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
    if not text:
        return []
    kw_model = get_kw_model()
    keywords = kw_model.extract_keywords(text[:2000], keyphrase_ngram_range=(1, 2), stop_words='english', top_n=top_n)
    return [kw[0] for kw in keywords]

