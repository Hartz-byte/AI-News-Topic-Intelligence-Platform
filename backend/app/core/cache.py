import json
import hashlib
from typing import Any, Optional
import diskcache
from app.core.config import get_settings

settings = get_settings()

cache = diskcache.Cache(settings.cache_dir)

def get_cache(key: str) -> Optional[Any]:
    try:
        val = cache.get(key)
        return val
    except Exception:
        return None

def set_cache(key: str, value: Any, expire_seconds: int = 300) -> None:
    try:
        cache.set(key, value, expire=expire_seconds)
    except Exception:
        pass

def generate_cache_key(prefix: str, **kwargs) -> str:
    key_str = json.dumps(kwargs, sort_keys=True)
    hash_str = hashlib.md5(key_str.encode()).hexdigest()
    return f"{prefix}:{hash_str}"
