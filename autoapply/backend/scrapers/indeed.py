import logging
logger = logging.getLogger(__name__)

import httpx
import random
import asyncio
from config import settings
from bs4 import BeautifulSoup
from scrapers import BaseScraper, ScrapedJob
from urllib.parse import quote_plus
import re


class IndeedScraper(BaseScraper):
    """Scrape Indeed job listings via public search URLs."""

    BASE_URL = "https://www.indeed.com/jobs"
    # Rotating User-Agents
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    ]

    def _get_headers(self) -> dict:
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    @property
    def source_name(self) -> str:
        return "indeed"

    async def scrape(self, keywords: list[str], locations: list[str]) -> list[ScrapedJob]:
        """Scrape Indeed for PM intern jobs across keywords and locations."""
        all_jobs: list[ScrapedJob] = []
        seen_urls: set[str] = set()

        proxy = settings.PROXY_URL if settings.PROXY_URL else None
        async with httpx.AsyncClient(headers=self._get_headers(), timeout=30.0, follow_redirects=True, proxy=proxy) as client:
            for keyword in keywords:
                for location in locations:
                    await asyncio.sleep(random.uniform(2.0, 5.0))
                    for page in range(3): # Deep pagination (up to 3 pages per combo)
                        start = page * 10
                        try:
                            jobs = await self._scrape_search(client, keyword, location, start)
                            if not jobs:
                                break
                                
                            for job in jobs:
                                if job.source_url not in seen_urls:
                                    seen_urls.add(job.source_url)
                                    all_jobs.append(job)
                        except Exception as e:
                            logger.info(f"[Indeed] Error scraping '{keyword}' in '{location}': {e}")
                            break # Skip further pages on error

                        # Be polite — wait between requests
                        await asyncio.sleep(1.5)

        logger.info(f"[Indeed] Total unique jobs scraped: {len(all_jobs)}")
        return all_jobs

    async def _scrape_search(
        self, client: httpx.AsyncClient, keyword: str, location: str, start: int = 0
    ) -> list[ScrapedJob]:
        """Scrape a single Indeed search page."""
        params = {
            "q": keyword,
            "l": location,
            "jt": "internship",  # Filter to internships
            "sort": "date",  # Most recent first
            "fromage": "7",  # Last 7 days
            "start": str(start),
        }

        try:
            response = await client.get(self.BASE_URL, params=params)
            if response.status_code != 200:
                logger.info(f"[Indeed] Got status {response.status_code} for {keyword} in {location}")
                return []
        except httpx.HTTPError as e:
            logger.info(f"[Indeed] HTTP error: {e}")
            return []

        return self._parse_search_results(response.text, keyword)

    def _parse_search_results(self, html: str, keyword: str) -> list[ScrapedJob]:
        """Parse Indeed search results HTML into ScrapedJob objects."""
        soup = BeautifulSoup(html, "lxml")
        jobs: list[ScrapedJob] = []

        # Indeed uses multiple card selectors — try common patterns
        job_cards = soup.select("div.job_seen_beacon") or soup.select("div.jobsearch-SerpJobCard")
        if not job_cards:
            # Fallback: look for any result containers
            job_cards = soup.select("[data-jk]")

        for card in job_cards:
            try:
                job = self._parse_card(card, keyword)
                if job:
                    jobs.append(job)
            except Exception:
                continue

        return jobs

    def _parse_card(self, card, keyword: str) -> ScrapedJob | None:
        """Parse a single Indeed job card."""
        # Title
        title_el = card.select_one("h2.jobTitle a, h2 a, a.jcs-JobTitle")
        if not title_el:
            return None
        title = title_el.get_text(strip=True)

        # Company
        company_el = card.select_one("span.css-1h7lukg, span[data-testid='company-name'], div.company")
        company_name = company_el.get_text(strip=True) if company_el else "Unknown"

        # Location
        location_el = card.select_one("div.css-1restlb, div[data-testid='text-location'], span.location")
        location = location_el.get_text(strip=True) if location_el else "Unknown"

        # URL
        job_key = card.get("data-jk") or ""
        if title_el and title_el.get("href"):
            href = title_el["href"]
            if href.startswith("/"):
                source_url = f"https://www.indeed.com{href}"
            else:
                source_url = href
        elif job_key:
            source_url = f"https://www.indeed.com/viewjob?jk={job_key}"
        else:
            return None

        # Description snippet
        snippet_el = card.select_one("div.css-9446fg, td.snip, div.job-snippet")
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""

        # Salary
        salary_el = card.select_one("div.salary-snippet-container, span.salary-snippet, div.metadata.salary-snippet-container")
        salary = salary_el.get_text(strip=True) if salary_el else ""

        # Check for visa/sponsorship mentions
        visa_info = ""
        full_text = f"{title} {snippet}".lower()
        if "no sponsorship" in full_text or "not sponsor" in full_text or "without sponsorship" in full_text:
            visa_info = "no_sponsorship"
        elif "cpt" in full_text or "opt" in full_text or "f-1" in full_text:
            visa_info = "cpt_opt_ok"

        # Posted date
        date_el = card.select_one("span.css-qvloho, span.date, span[data-testid='myJobsStateDate']")
        posted_at = date_el.get_text(strip=True) if date_el else ""

        return ScrapedJob(
            title=title,
            company_name=company_name,
            location=location,
            source_platform="indeed",
            source_url=source_url,
            description=snippet,
            salary_range=salary,
            posted_at=posted_at,
            experience_level="internship",
            visa_info=visa_info,
        )
