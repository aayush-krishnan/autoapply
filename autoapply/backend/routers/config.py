import logging
logger = logging.getLogger(__name__)

"""Router for handling system configuration and settings."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path
from config import settings
from database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from models import SystemConfig

router = APIRouter(prefix="/api/config", tags=["Settings"])

class ConfigUpdate(BaseModel):
    proxy_url: str | None = None
    scrape_interval: int | None = None
    keywords: str | None = None
    locations: str | None = None

@router.get("/")
async def get_config(db: Session = Depends(get_db)):
    """Return the current system configuration."""
    # Sync settings with DB first
    proxy_cfg = db.query(SystemConfig).filter(SystemConfig.key == "PROXY_URL").first()
    if proxy_cfg: settings.PROXY_URL = proxy_cfg.value
    
    interval_cfg = db.query(SystemConfig).filter(SystemConfig.key == "SCRAPE_INTERVAL_HOURS").first()
    if interval_cfg: settings.SCRAPE_INTERVAL_HOURS = int(interval_cfg.value)

    return {
        "proxy_url": settings.PROXY_URL,
        "scrape_interval": settings.SCRAPE_INTERVAL_HOURS,
        "keywords": ", ".join(settings.ROLE_BASE),
        "locations": ", ".join(settings.TARGET_CITIES)
    }

@router.post("/")
async def update_config(update: ConfigUpdate, db: Session = Depends(get_db)):
    """
    Update the system configuration in the database.
    """
    try:
        if update.proxy_url is not None:
            cfg = db.query(SystemConfig).filter(SystemConfig.key == "PROXY_URL").first()
            if not cfg:
                cfg = SystemConfig(key="PROXY_URL", value=update.proxy_url)
                db.add(cfg)
            else:
                cfg.value = update.proxy_url
            settings.PROXY_URL = update.proxy_url
            
        if update.scrape_interval is not None:
            cfg = db.query(SystemConfig).filter(SystemConfig.key == "SCRAPE_INTERVAL_HOURS").first()
            if not cfg:
                cfg = SystemConfig(key="SCRAPE_INTERVAL_HOURS", value=str(update.scrape_interval))
                db.add(cfg)
            else:
                cfg.value = str(update.scrape_interval)
            settings.SCRAPE_INTERVAL_HOURS = update.scrape_interval
            
        db.commit()
        return {"status": "success", "message": "Settings updated and saved to database"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")
