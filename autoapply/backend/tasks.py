import logging
import asyncio
from celery_app import celery_app
from database import SessionLocal
from routers.jobs import run_scrape_logic

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.scrape_jobs_task")
def scrape_jobs_task():
    """
    Celery task to run the automated scrape logic.
    Since run_scrape_logic is async, we need to run it in an event loop.
    """
    logger.info("Starting Celery-managed automated scrape...")
    
    db = SessionLocal()
    try:
        # Run the async logic in a sync context for Celery worker
        loop = asyncio.get_event_loop()
        sources = ["indeed", "linkedin", "wellfound", "twitter", "simplyhired", "builtin", "ziprecruiter"]
        
        # If the loop is already running (unlikely for sync celery worker), use run_coroutine_threadsafe
        # otherwise create a new one.
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(run_scrape_logic(db, sources), loop)
            result = future.result()
        else:
            result = asyncio.run(run_scrape_logic(db, sources))
            
        logger.info(f"Celery scrape completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Celery scrape failed: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
