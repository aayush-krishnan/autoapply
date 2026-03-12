import httpx
import random
import asyncio
from bs4 import BeautifulSoup
from scrapers import BaseScraper, ScrapedJob
from config import settings
from urllib.parse import quote_plus

class SimplyHiredScraper(BaseScraper):
    """Scraper for SimplyHired using public search URLs."""

    @property
    def source_name(self) -> str:
        return "simplyhired"

    def _get_headers(self) -> dict:
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def scrape(self, keywords: list[str], locations: list[str]) -> list[ScrapedJob]:
        all_jobs: list[ScrapedJob] = []
        seen_urls: set[str] = set()
        
        proxy = settings.PROXY_URL if settings.PROXY_URL else None
        async with httpx.AsyncClient(headers=self._get_headers(), timeout=30.0, follow_redirects=True, proxy=proxy) as client:
            for keyword in keywords:
                for location in locations:
                    # Jitter
                    await asyncio.sleep(random.uniform(2.0, 4.0))
                    
                    search_url = f"https://www.simplyhired.com/search?q={quote_plus(keyword)}&l={quote_plus(location)}&t=7"
                    try:
                        resp = await client.get(search_url)
                        if resp.status_code != 200:
                            print(f"[SimplyHired] Error {resp.status_code} for {keyword} in {location}")
                            continue
                            
                        soup = BeautifulSoup(resp.text, "lxml")
                        job_cards = soup.select("li.vjs-job-list-item")
                        
                        for card in job_cards:
                            title_el = card.select_one("h3.job-title a")
                            company_el = card.select_one("span[data-testid='companyName']")
                            loc_el = card.select_one("span[data-testid='searchSerpJobLocation']")
                            
                            if not title_el or not company_el:
                                continue
                                
                            job_url = "https://www.simplyhired.com" + title_el["href"]
                            if job_url in seen_urls:
                                continue
                                
                            seen_urls.add(job_url)
                            all_jobs.append(ScrapedJob(
                                title=title_el.text.strip(),
                                company_name=company_el.text.strip(),
                                location=loc_el.text.strip() if loc_el else location,
                                source_platform="simplyhired",
                                source_url=job_url,
                                description="" # SimplyHired often requires a separate request for description
                            ))
                            
                    except Exception as e:
                        print(f"[SimplyHired] Failed to scrape {keyword}: {e}")
                        
        return all_jobs
