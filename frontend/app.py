import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="AI News & Topic Intelligence", page_icon="📰", layout="wide")
st.title("AI News & Topic Intelligence Platform")
# st.caption("Streamlit frontend on top of FastAPI + Groq/local models")

categories = ["technology", "business", "sports", "health", "science", "entertainment", "world"]

with st.sidebar:
    st.header("Navigation Guide")
    st.markdown("""
    **📈 Trending**
    Discover the most active news topics right now. The AI dynamically groups related articles into clusters and calculates a complex "Trend Score" based on recency, volume, and publisher diversity. Click "View Timeline" on any topic to see how the story developed.

    **🔍 Topic Search**
    Perform semantic vector searches across your local database. Type any concept or entity, and the native NLP engine will find mathematically related articles, instantly synthesizing them into a clean briefing using Groq LLaMA models.

    **📰 About the project**
    Learn about the underlying architecture, data flow, NLP techniques, and technology stack powering this 100% native Python application.
    """)

tab1, tab2, tab3 = st.tabs(["Trending", "Topic Search", "About the project"])

with tab1:
    category = st.selectbox("Category", categories, index=0)
    col1, col2 = st.columns([1, 5])
    with col1:
        refresh = st.button("Refresh category")
    try:
        resp = requests.get(
            f"{API_BASE_URL}/api/trending",
            params={"category": category, "refresh": refresh},
            timeout=90,
        )
        data = resp.json()
        st.subheader(f"Top trending in {data['category']}")
        for i, item in enumerate(data["topics"], start=1):
            with st.container(border=True):
                st.markdown(f"**{i}. {item['topic']}**")
                st.write(f"Trend score: {item['trend_score']} | Articles: {item['article_count']}")
                if st.button(f"View Timeline", key=f"timeline_trend_{i}"):
                    with st.spinner("Loading..."):
                        try:
                            t_resp = requests.get(f"{API_BASE_URL}/api/topics/timeline", params={"topic": item['topic']}, timeout=30)
                            t_data = t_resp.json()
                            if isinstance(t_data, list):
                                for event in t_data:
                                    st.caption(f"{event['date'][:10] if event['date'] else 'No Date'} &mdash; {event['source']}")
                                    st.markdown(f"[{event['title']}]({event['url']})")
                            else:
                                st.warning(t_data.get("detail", "Not found"))
                        except Exception as e:
                            st.error("Failed to load timeline.")
    except Exception as e:
        st.error(f"Could not load trending topics: {e}")

with tab2:
    q = st.text_input("Type any topic", placeholder="OpenAI, Nvidia, India budget, AI jobs...")
    search_cat = st.selectbox("Optional category", ["all"] + categories, index=0)
    if st.button("Search", type="primary"):
        if not q.strip():
            st.warning("Enter a topic first.")
        else:
            params = {"q": q}
            if search_cat != "all":
                params["category"] = search_cat
            try:
                resp = requests.get(f"{API_BASE_URL}/api/search", params=params, timeout=120)
                data = resp.json()
                st.subheader(data["query"])
                st.write(data["summary"])
                if data["key_facts"]:
                    st.markdown("### Key facts")
                    for fact in data["key_facts"]:
                        st.write(f"- {fact}")
                st.markdown("### Articles")
                for article in data["articles"]:
                    with st.container(border=True):
                        st.markdown(f"**{article['title']}**")
                        st.write(f"Source: {article['source_name']} | Category: {article['category']}")
                        st.write(article["summary"])
                        st.link_button("Open source", article["url"])
            except Exception as e:
                st.error(f"Search failed: {e}")

with tab3:
    st.markdown("""
# AI News & Topic Intelligence

A 100% natively running AI News Aggregator bridging modern NLP and large language models without reliance on cumbersome Docker servers.

### 🚀 Core Features
- **Dynamic Context Engines**: Ingests live news feeds continuously 24/7.
- **Micro-Vector Search**: Employs raw NumPy Cosine Similarity atop localized JSON matrices built into SQLite, providing blazing semantic search.
- **Algorithmic Trend Scoring**: Mathematical evaluation combining Recency, Volume, and Diversity to calculate true news trends.
- **Deep NLP Extractions**: In-memory Entity Recognition mapping (spaCy) alongside smart keyword phrasing extraction (KeyBERT).
- **LLM Grounding**: AI Summarization using LLaMA models on Groq hardware.

### 🛠️ Tech Stack
* **Backend**: FastAPI, SQLAlchemy, SQLite, APScheduler, DiskCache
* **AI/NLP**: Groq (LLaMA-3), local spaCy, KeyBERT, fastembed, native numpy cosine similarity
* **Frontend**: Streamlit, Python Requests

---
⭐️ Liked my work? 
Check out the [GitHub repo](https://github.com/Hartz-byte/AI-News-Topic-Intelligence-Platform) and give it a star!
""")
