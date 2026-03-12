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
