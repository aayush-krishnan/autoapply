import logging
logger = logging.getLogger(__name__)

import httpx
import random
import asyncio
from bs4 import BeautifulSoup
from scrapers import BaseScraper, ScrapedJob
from config import settings
import re

class BuiltInScraper(BaseScraper):
    """Scraper for BuiltIn.com (Tech/Startup focused)."""

    @property
    def source_name(self) -> str:
        return "builtin"

    def _get_headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://builtin.com/",
        }

    async def scrape(self, keywords: list[str], locations: list[str]) -> list[ScrapedJob]:
        all_jobs: list[ScrapedJob] = []
        seen_urls: set[str] = set()
        
        proxy = settings.PROXY_URL if settings.PROXY_URL else None
        async with httpx.AsyncClient(headers=self._get_headers(), timeout=30.0, follow_redirects=True, proxy=proxy) as client:
            for keyword in keywords:
                # BuiltIn uses specific city hubs
                city_slugs = ["san-francisco", "new-york-city", "seattle", "austin", "chicago", "los-angeles"]
                for city in city_slugs:
                    await asyncio.sleep(random.uniform(3.0, 6.0))
                    
                    # Format: https://builtin.com/jobs/san-francisco/internship/product-management
                    # Simplified search for now:
                    search_url = f"https://builtin.com/jobs?search={keyword}&location={city}"
                    
                    try:
                        resp = await client.get(search_url)
                        if resp.status_code != 200:
                            continue
                            
                        soup = BeautifulSoup(resp.text, "lxml")
                        # BuiltIn job card selector
                        job_cards = soup.select(".card-job")
                        
                        for card in job_cards:
                            title_el = card.select_one(".card-title a")
                            company_el = card.select_one(".company-title")
                            
                            if not title_el or not company_el:
                                continue
                                
                            job_url = "https://builtin.com" + title_el["href"] if title_el["href"].startswith("/") else title_el["href"]
                            if job_url in seen_urls:
                                continue
                                
                            seen_urls.add(job_url)
                            all_jobs.append(ScrapedJob(
                                title=title_el.text.strip(),
                                company_name=company_el.text.strip(),
                                location=city.replace("-", " ").title(),
                                source_platform="builtin",
                                source_url=job_url,
                                description=""
                            ))
                    except Exception as e:
                        logger.info(f"[BuiltIn] Error: {e}")
                        
        return all_jobs
