from __future__ import annotations
from groq import Groq
from app.core.config import get_settings

settings = get_settings()

def summarize_topic(query: str, article_chunks: list[dict]) -> dict:
    if not article_chunks:
        return {
            "summary": "No strong recent coverage was found for this topic yet.",
            "key_facts": [],
            "category": "general",
        }

    if not settings.groq_api_key:
        lines = [f"- {a['title']} ({a['source_name']})" for a in article_chunks[:5]]
        return {
            "summary": f"Recent coverage for '{query}' spans {len(article_chunks)} articles. Top headlines include: " + "; ".join(lines),
            "key_facts": [a["title"] for a in article_chunks[:5]],
            "category": article_chunks[0].get("category", "general"),
        }

    client = Groq(api_key=settings.groq_api_key)
    context = "\n\n".join(
        f"Title: {a['title']}\nSource: {a['source_name']}\nContent: {a['cleaned_content'][:1500]}"
        for a in article_chunks[:8]
    )
    prompt = f'''
You are a grounded news analyst.
Only use the provided source material.
Return valid JSON with keys: summary, key_facts, category.

Query: {query}

Sources:
{context}
'''.strip()

    completion = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    return completion.choices[0].message.content
