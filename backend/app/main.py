from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.logging import setup_logging
from app.db.session import Base, engine, SessionLocal
from app.api.health import router as health_router
from app.api.search import router as search_router
from app.api.trending import router as trending_router
from app.api.admin import router as admin_router
from app.services.topic_service import ingest_all_categories

scheduler = BackgroundScheduler()

def refresh_job():
    db = SessionLocal()
    try:
        ingest_all_categories(db, limit=6)
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    Base.metadata.create_all(bind=engine)
    scheduler.add_job(refresh_job, "interval", minutes=30, id="refresh_job", replace_existing=True)
    scheduler.start()
    refresh_job()
    yield
    scheduler.shutdown()

app = FastAPI(title="AI Topic Intelligence API", version="1.0.0", lifespan=lifespan)
app.include_router(health_router)
app.include_router(search_router)
app.include_router(trending_router)
app.include_router(admin_router)
