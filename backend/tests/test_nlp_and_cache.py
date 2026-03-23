import pytest
from app.core.cache import generate_cache_key
from app.services.extraction_service import extract_entities, extract_keywords

def test_cache_key_generation():
    key1 = generate_cache_key("test", a=1, b=2)
    key2 = generate_cache_key("test", b=2, a=1)
    assert key1 == key2

def test_extract_entities():
    # Should automatically download model if not found because of subprocess wrap
    text = "Elon Musk is the CEO of Tesla and SpaceX, located in Texas."
    entities = extract_entities(text)
    names = [e["name"] for e in entities]
    assert "Elon Musk" in names
    assert "Tesla" in names

def test_extract_keywords():
    text = "Artificial intelligence is rapidly evolving. Machine learning models are becoming very accurate."
    keywords = extract_keywords(text)
    assert len(keywords) > 0
