from __future__ import annotations
import trafilatura
import spacy
import subprocess
from keybert import KeyBERT

def _get_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
        return spacy.load("en_core_web_sm")

try:
    nlp = _get_spacy_model()
except Exception:
    nlp = None

try:
    kw_model = KeyBERT()
except Exception:
    kw_model = None

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
    if not text or not nlp:
        return []
    doc = nlp(text[:5000])
    entities = {}
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LOC", "PRODUCT"]:
            name = ent.text.strip().title()
            if len(name) > 2:
                entities[name] = ent.label_
    return [{"name": name, "entity_type": etype} for name, etype in entities.items()]

def extract_keywords(text: str, top_n: int = 5) -> list[str]:
    if not text or not kw_model:
        return []
    keywords = kw_model.extract_keywords(text[:2000], keyphrase_ngram_range=(1, 2), stop_words='english', top_n=top_n)
    return [kw[0] for kw in keywords]

