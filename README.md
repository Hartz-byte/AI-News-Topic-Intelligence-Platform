# AI News & Topic Intelligence Platform

An intelligent, natively running AI News Aggregator that bridges modern Natural Language Processing (NLP) and Large Language Models (LLMs) to automatically group, summarize, and semantically search through live news stories.

This platform operates 100% locally using native Python frameworks and SQLite, eliminating any reliance on cumbersome Docker containers, standalone vector databases, or complex background workers.

## Core Features

- **Live Aggregation Engine**: Continuously ingests live news feeds 24/7 across multiple categories (Technology, Business, Science, Health, etc.) via open RSS protocols.
- **Native Semantic Vector Search**: Employs raw NumPy Cosine Similarity atop localized JSON matrices built directly into SQLite, providing blazing semantic search capabilities without external databases like Qdrant or Pinecone.
- **Algorithmic Trend Scoring**: Uses mathematical evaluation combining Recency, Volume, and Diversity to calculate true news trends instead of naive word counts.
- **Topical Chronology (Timelines)**: Group matched headlines and track the progression of a story dynamically through a dedicated timeline endpoint.
- **Deep NLP Extractions**: Uses in-memory Entity Recognition mapping via `spaCy` alongside intelligent keyword phrasing extraction via `KeyBERT`.
- **LLM Grounding**: Analyzes raw HTML texts using LLMs mapped on the blazing fast Groq inference hardware for real-time summarization and fact synthesis.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite, APScheduler, DiskCache
- **AI / NLP**: Groq (LLaMA-3), spaCy, KeyBERT, fastembed, native NumPy
- **Frontend**: Streamlit, Requests

## Project Structure

- `backend/`: Core FastAPI server, intelligence pipelines, and the SQLite storage logic.
- `frontend/`: Lightweight Streamlit dashboard for viewing trends and searching concepts.
- `render.yaml`: Infrastructure-as-code configuration for Render deployment.

## Local Setup & Development

### 1. Prerequisites
Ensure you have Python 3.11.x installed on your operating system. 

### 2. Configure Environment Variables
Inside the root folder, copy the example configuration and fill in the required keys:

```bash
cp .env.example .env
```
Make sure to add your `GROQ_API_KEY` (freely available at console.groq.com).

### 3. Install Dependencies
Switch into the `backend` folder and install the processing packages. (Note: This may take a few minutes as it downloads PyTorch, spaCy, and fastembed).

```bash
python -m venv venv
venv\Scripts\activate  # Or `source venv/bin/activate` on Mac/Linux

pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 4. Start the Application

The architecture requires two running terminal instances:

**Terminal 1: Start the Engine & API**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
(Upon first boot, the system will pause for several seconds as it compiles the initial SQLite database and downloads the first batch of RSS news.)

**Terminal 2: Start the Dashboard**
```bash
cd frontend
streamlit run app.py
```
This will open the user interface at `http://localhost:8501`.

## Deployment

The application dependencies have been cleanly isolated to allow deployment on standard free-tier web hosting.

### Deploying Backend (Render)
1. Push your repository to GitHub.
2. Create a new "Blueprint" on Render.com and connect your repository.
3. Render will instantly parse the `render.yaml` file, download the `en_core_web_sm` pipeline automatically during the build phase, and launch the server.
4. Add your `GROQ_API_KEY` inside Render's "Environment" tab.
Note: Render's Free Tier has an ephemeral hard drive, which wipes native SQLite databases upon sleeping. Consider adding a `DATABASE_URL` from Neon.tech/Supabase in the Environment tab for persistent free-tier storage.

### Deploying Frontend (Streamlit Community Cloud)
1. Navigate to share.streamlit.io.
2. Select your GitHub repository and point the main file path to `frontend/app.py`.
3. Open "Advanced Settings" and paste your newly acquired Render backend URL:
`API_BASE_URL = "https://ai-news-topic-intelligence-platform.onrender.com/"`
4. Deploy the application. Streamlit will only read `frontend/requirements.txt`, launching instantly.

## Verification / Testing

The repository contains basic testing infrastructure to ensure caching layers and NLP tokenizers are behaving deterministically.
```bash
cd backend
python -m pytest tests/
```