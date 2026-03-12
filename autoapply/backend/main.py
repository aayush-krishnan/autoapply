"""AutoApply Backend — FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, init_db
from routers import jobs, dashboard, resumes, apply


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    print("🚀 AutoApply Backend starting...")
    init_db()
    print("✅ Database initialized")
    yield
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
