"""AutoApply Backend — FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, init_db
from routers import jobs, dashboard, resumes, apply


from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from database import SessionLocal
import datetime

def run_automated_scrape():
    """Background task to trigger a fresh scrape."""
    print(f"⏰ [{datetime.datetime.now()}] Starting automated hourly scrape...")
    db = SessionLocal()
    try:
        from routers.jobs import run_scrape_logic
        # For simplicity in background, we run for all common sources
        sources = ["indeed", "linkedin", "wellfound", "twitter", "simplyhired", "builtin", "ziprecruiter"]
        # Use existing event loop or create one for the async scrape
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_scrape_logic(db, sources))
        loop.close()
        print(f"✅ [{datetime.datetime.now()}] Automated scrape completed.")
    except Exception as e:
        print(f"❌ [{datetime.datetime.now()}] Scrape failed: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 AutoApply Backend starting...")
    init_db()
    
    # Init scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_automated_scrape, 'interval', hours=1, next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=10))
    scheduler.start()
    print("📅 [Scheduler] Hourly background scrape scheduled.")
    
    yield
    scheduler.shutdown()
    print("👋 AutoApply Backend shutting down")


app = FastAPI(
    title="AutoApply API",
    description="Intelligent Job Application & Outreach Platform for MEM Students",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router)
app.include_router(dashboard.router)
app.include_router(resumes.router)
app.include_router(apply.router)


@app.get("/api/health")
async def root():
    return {
        "name": "AutoApply API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
