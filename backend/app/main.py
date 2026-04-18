from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.logging import setup_logging
from app.db.session import Base, engine, SessionLocal
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="requests")

from app.api.health import router as health_router
from app.api.search import router as search_router
from app.api.trending import router as trending_router
from app.api.admin import router as admin_router
from app.api.topics import router as topics_router
from app.services.topic_service import ingest_all_categories

scheduler = BackgroundScheduler()

import logging
logger = logging.getLogger(__name__)

def refresh_job():
    logger.info("Starting background refresh job...")
    db = SessionLocal()
    try:
        import time
        from app.services.topic_service import CATEGORIES, ingest_category
        for cat in CATEGORIES:
            try:
                ingest_category(db, cat, limit=4)
                time.sleep(2) # Give Render CPU a breather for API requests
            except Exception as e:
                logger.error(f"Error ingesting category {cat}: {e}")
        logger.info("Background refresh job completed.")
    except Exception as e:
        logger.error(f"Critical error in refresh_job: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    Base.metadata.create_all(bind=engine)
    scheduler.add_job(refresh_job, "interval", minutes=30, id="refresh_job", replace_existing=True)
    
    import datetime
    scheduler.add_job(refresh_job, "date", run_date=datetime.datetime.now() + datetime.timedelta(seconds=2))
    
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="AI News & Topic Intelligence API", version="1.0.0", lifespan=lifespan)
app.include_router(health_router)
app.include_router(search_router)
app.include_router(trending_router)
app.include_router(admin_router)
app.include_router(topics_router)

@app.get("/")
def read_root():
    return {"detail": "AI News & Topic Intelligence Platform Backend is Running"}

Instrumentator().instrument(app).expose(app)

