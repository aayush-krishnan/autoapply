"""AutoApply Backend — FastAPI Application Entry Point."""

import logging

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("autoapply")

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
import os

from database import engine, init_db
from routers import jobs, dashboard, resumes, apply, config


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AutoApply Backend starting...")
    from config import settings
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    init_db()
    
    from config import settings
    logger.info(f"📂 [Config] Google Drive Folder ID: {settings.GOOGLE_DRIVE_FOLDER_ID or 'NOT CONFIGURED'}")
    
    yield
    logger.info("👋 AutoApply Backend shutting down")


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

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from config import settings

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    # Allow local frontend, health checks, and docs
    path = request.url.path
    if path in ["/health", "/api/health", "/docs", "/openapi.json"] or path.startswith("/api/static/assets"):
        return await call_next(request)
    
    # Check for API Key in header or query param
    api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    
    if settings.API_KEY and api_key != settings.API_KEY:
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized. Please provide a valid X-API-Key header."}
        )
    
    return await call_next(request)

# Static files for assets (non-sensitive)
app.mount("/api/static/assets", StaticFiles(directory="assets"), name="assets")

# Include routers
app.include_router(jobs.router)
app.include_router(dashboard.router)
app.include_router(resumes.router)
app.include_router(apply.router)
app.include_router(config.router)


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
