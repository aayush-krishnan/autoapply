import logging
logger = logging.getLogger(__name__)

import httpx
import random
import asyncio
from bs4 import BeautifulSoup
from scrapers import BaseScraper, ScrapedJob
from config import settings
from urllib.parse import quote_plus

class ZipRecruiterScraper(BaseScraper):
    """Scraper for ZipRecruiter."""

    @property
    def source_name(self) -> str:
        return "ziprecruiter"

    def _get_headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }

    async def scrape(self, keywords: list[str], locations: list[str]) -> list[ScrapedJob]:
        all_jobs: list[ScrapedJob] = []
        seen_urls: set[str] = set()
        
        proxy = settings.PROXY_URL if settings.PROXY_URL else None
        async with httpx.AsyncClient(headers=self._get_headers(), timeout=30.0, follow_redirects=True, proxy=proxy) as client:
            for keyword in keywords:
                for location in locations:
                    await asyncio.sleep(random.uniform(2.0, 5.0))
                    
                    search_url = f"https://www.ziprecruiter.com/jobs/search?search={quote_plus(keyword)}&location={quote_plus(location)}"
                    
                    try:
                        resp = await client.get(search_url)
                        if resp.status_code != 200:
                            continue
                            
                        soup = BeautifulSoup(resp.text, "lxml")
                        job_cards = soup.select(".job_content")
                        
                        for card in job_cards:
                            title_el = card.select_one(".job_title")
                            company_el = card.select_one(".company_name")
                            loc_el = card.select_one(".location")
                            
                            if not title_el or not company_el:
                                continue
                                
                            job_url = title_el.find("a")["href"] if title_el.find("a") else ""
                            if not job_url or job_url in seen_urls:
                                continue
                                
                            seen_urls.add(job_url)
                            all_jobs.append(ScrapedJob(
                                title=title_el.text.strip(),
                                company_name=company_el.text.strip(),
                                location=loc_el.text.strip() if loc_el else location,
                                source_platform="ziprecruiter",
                                source_url=job_url,
                                description=""
                            ))
                    except Exception as e:
                        logger.info(f"[ZipRecruiter] Error: {e}")
                        
        return all_jobs
