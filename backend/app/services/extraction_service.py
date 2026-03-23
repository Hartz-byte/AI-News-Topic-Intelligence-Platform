from __future__ import annotations
import trafilatura

def extract_article_text(url: str) -> str:
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ""
        text = trafilatura.extract(downloaded, include_comments=False, include_links=False)
        return text or ""
    except Exception:
        return ""
