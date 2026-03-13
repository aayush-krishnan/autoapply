import logging
logger = logging.getLogger(__name__)

"""Base scraper interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ScrapedJob:
    """Raw job data from a scraper before saving to DB."""
    title: str
    company_name: str
    location: str
    source_platform: str
    source_url: str
    description: str = ""
    salary_range: str = ""
    posted_at: str = ""  # ISO format or descriptive ("2 days ago")
    experience_level: str = ""
    visa_info: str = ""  # "no_sponsorship" if detected, else ""

from datetime import datetime, timezone, timedelta
import re

def parse_posted_at(raw: str) -> datetime | None:
    """Parse relative strings like '2 days ago', '3 hours ago' into UTC datetime."""
    if not raw:
        return None
    raw = raw.lower().strip()
    now = datetime.now(timezone.utc)
    
    # Match patterns like "3 days ago", "1 hour ago", "Just posted"
    m = re.search(r"(\d+)\s*(hour|day|week|month)", raw)
    if not m:
        # Fallback for "today", "just posted", "yesterday"
        if "today" in raw or "just" in raw:
            return now
        if "yesterday" in raw:
            return now - timedelta(days=1)
        return now  # fallback: assume just posted
        
    n, unit = int(m.group(1)), m.group(2)
    delta = {
        "hour": timedelta(hours=n), 
        "day": timedelta(days=n),
        "week": timedelta(weeks=n), 
        "month": timedelta(days=n*30)
    }
    return now - delta.get(unit, timedelta(days=1))


class BaseScraper(ABC):
    """Abstract base class for job scrapers."""

    @abstractmethod
    async def scrape(self, keywords: list[str], locations: list[str]) -> list[ScrapedJob]:
        """
        Scrape job listings from the source.

        Args:
            keywords: List of job title keywords to search for.
            locations: List of target cities/locations.

        Returns:
            List of ScrapedJob objects.
        """
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of this scraper source (e.g. 'indeed', 'linkedin')."""
        pass
