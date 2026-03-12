"""Router for handling system configuration and settings."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path
from config import settings

router = APIRouter(prefix="/api/config", tags=["Settings"])

class ConfigUpdate(BaseModel):
    proxy_url: str | None = None
    scrape_interval: int | None = None
    keywords: str | None = None
    locations: str | None = None

@router.get("/")
async def get_config():
    """Return the current system configuration."""
    return {
        "proxy_url": settings.PROXY_URL,
        "scrape_interval": settings.SCRAPE_INTERVAL_HOURS,
        "keywords": ", ".join(settings.ROLE_BASE),
        "locations": ", ".join(settings.TARGET_CITIES)
    }

@router.post("/")
async def update_config(update: ConfigUpdate):
    """
    Update the .env file with new configuration.
    In a real production app, this would use a database or a secure config store.
    """
    env_path = Path(__file__).resolve().parent.parent / ".env"
    
    try:
        # Read current .env
        lines = []
        if env_path.exists():
            with open(env_path, "r") as f:
                lines = f.readlines()
        
        # Prepare updates
        updates = {}
        if update.proxy_url is not None:
            updates["PROXY_URL"] = update.proxy_url
        if update.scrape_interval is not None:
            updates["SCRAPE_INTERVAL_HOURS"] = str(update.scrape_interval)
            
        # Apply updates
        new_lines = []
        applied_keys = set()
        
        for line in lines:
            if "=" in line:
                key = line.split("=")[0].strip()
                if key in updates:
                    new_lines.append(f"{key}={updates[key]}\n")
                    applied_keys.add(key)
                    continue
            new_lines.append(line)
            
        # Add new keys
        for key, val in updates.items():
            if key not in applied_keys:
                new_lines.append(f"{key}={val}\n")
                
        # Write back
        with open(env_path, "w") as f:
            f.writelines(new_lines)
            
        # Update runtime settings
        if update.proxy_url is not None:
            settings.PROXY_URL = update.proxy_url
        if update.scrape_interval is not None:
            settings.SCRAPE_INTERVAL_HOURS = update.scrape_interval
            
        return {"status": "success", "message": "Settings updated and saved to .env"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")
