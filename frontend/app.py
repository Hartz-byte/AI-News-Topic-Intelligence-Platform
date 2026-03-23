import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Topic Intelligence", layout="wide")
st.title("AI News & Topic Intelligence Platform")
st.caption("Streamlit frontend on top of FastAPI + Groq/local models")

categories = ["technology", "business", "sports", "health", "science", "entertainment", "world"]
tab1, tab2 = st.tabs(["Trending", "Topic Search"])

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
