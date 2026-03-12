"""LinkedIn job scraper using public search URLs (no login required)."""

import httpx
from bs4 import BeautifulSoup
import asyncio
import re
import random
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus

from scrapers import BaseScraper, ScrapedJob


class LinkedInScraper(BaseScraper):
    """Scrape LinkedIn job listings via public guest search URLs."""

    # LinkedIn's public job search (no login needed)
    BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    # Rotating User-Agents to avoid pattern detection
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    ]

    @property
    def source_name(self) -> str:
        return "linkedin"

    def _get_headers(self) -> dict:
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }

    # LinkedIn location GeoIDs for target cities
    GEO_IDS = {
        "New York": "102571732",
        "San Francisco": "102277331",
        "Seattle": "104116203",
        "Boston": "100407218",
        "Chicago": "103112676",
        "Austin": "104472866",
        "Los Angeles": "102448103",
        "Washington": "104383272",
    }

    @property
    def source_name(self) -> str:
        return "linkedin"

    async def scrape(self, keywords: list[str], locations: list[str]) -> list[ScrapedJob]:
        """Scrape LinkedIn for PM intern jobs."""
        all_jobs: list[ScrapedJob] = []
        seen_urls: set[str] = set()

        proxy = settings.PROXY_URL if settings.PROXY_URL else None
        async with httpx.AsyncClient(headers=self._get_headers(), timeout=30.0, follow_redirects=True, proxy=proxy) as client:
            for keyword in keywords:
                for location in locations:
                    # Random jitter before starting a new combination
                    await asyncio.sleep(random.uniform(1.0, 4.0))
                    for page in range(3): # Deep pagination (up to 3 pages per combo)
                        start = page * 25
                        try:
                            jobs = await self._scrape_search(client, keyword, location, start)
                            if not jobs:
                                break # Exit pagination if no more jobs found
                                
                            for job in jobs:
                                if job.source_url not in seen_urls:
                                    seen_urls.add(job.source_url)
                                    all_jobs.append(job)
                        except Exception as e:
                            print(f"[LinkedIn] Error scraping '{keyword}' in '{location}': {e}")
                            break # Skip further pages on error

                        # Be polite between pages
                        await asyncio.sleep(2.0)

                    # Be polite
                    await asyncio.sleep(2.0)

        print(f"[LinkedIn] Total unique jobs scraped: {len(all_jobs)}")
        return all_jobs

    async def _scrape_search(
        self, client: httpx.AsyncClient, keyword: str, location: str, start: int = 0
    ) -> list[ScrapedJob]:
        """Scrape a single LinkedIn search page."""
        geo_id = self.GEO_IDS.get(location, "")

        params = {
            "keywords": keyword,
            "location": location,
            "f_TPR": "r604800",  # Past week
            "f_E": "1",  # Entry level / internship
            "f_JT": "I",  # Internship job type
            "start": str(start),
        }
        if geo_id:
            params["geoId"] = geo_id

        try:
            response = await client.get(self.BASE_URL, params=params)
            if response.status_code != 200:
                print(f"[LinkedIn] Got status {response.status_code} for {keyword} in {location}")
                return []
        except httpx.HTTPError as e:
            print(f"[LinkedIn] HTTP error: {e}")
            return []

        return self._parse_search_results(response.text, keyword)

    def _parse_search_results(self, html: str, keyword: str) -> list[ScrapedJob]:
        """Parse LinkedIn job listing HTML."""
        soup = BeautifulSoup(html, "lxml")
        jobs: list[ScrapedJob] = []

        # LinkedIn guest API returns <li> cards
        job_cards = soup.select("li") or soup.select("div.base-card")

        for card in job_cards:
            try:
                job = self._parse_card(card)
                if job:
                    jobs.append(job)
            except Exception:
                continue

        return jobs

    def _parse_card(self, card) -> ScrapedJob | None:
        """Parse a single LinkedIn job card."""
        # Title
        title_el = card.select_one("h3.base-search-card__title, h3, a.base-card__full-link")
        if not title_el:
            return None
        title = title_el.get_text(strip=True)

        # Company
        company_el = card.select_one("h4.base-search-card__subtitle, h4, a.hidden-nested-link")
        company_name = company_el.get_text(strip=True) if company_el else "Unknown"

        # Location
        location_el = card.select_one("span.job-search-card__location, span.base-search-card__metadata")
        location = location_el.get_text(strip=True) if location_el else "Unknown"

        # URL
        link_el = card.select_one("a.base-card__full-link, a[href*='linkedin.com/jobs']")
        if link_el and link_el.get("href"):
            source_url = link_el["href"].split("?")[0]  # Clean URL
        else:
            return None

        # Time posted
        time_el = card.select_one("time, span.job-search-card__listdate")
        posted_at = ""
        if time_el:
            posted_at = time_el.get("datetime", "") or time_el.get_text(strip=True)

        return ScrapedJob(
            title=title,
            company_name=company_name,
            location=location,
            source_platform="linkedin",
            source_url=source_url,
            description="",  # LinkedIn doesn't show full desc in search
            posted_at=posted_at,
            experience_level="internship",
        )
