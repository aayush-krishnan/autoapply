"""Wellfound (AngelList) scraper using Playwright and Google Dorking to bypass login walls."""

from playwright.async_api import async_playwright
import asyncio
from scrapers import BaseScraper, ScrapedJob

class WellfoundScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "wellfound"

    async def scrape(self, keywords: list[str], locations: list[str]) -> list[ScrapedJob]:
        all_jobs = []
        seen_urls = set()

        # We use Google Dorking since Wellfound requires login for direct search
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            
            # Limit Wellfound dragging to top 5 combinations to avoid Google rate limit captchas
            for keyword in keywords[:5]:
                page = await context.new_page()
                try:
                    query = f"site:wellfound.com/job \"{keyword}\""
                    await page.goto(f"https://www.google.com/search?q={query}")
                    
                    # Wait for results
                    await page.wait_for_selector("div.g", timeout=5000)
                    results = await page.query_selector_all("div.g")
                    
                    for res in results:
                        title_el = await res.query_selector("h3")
                        link_el = await res.query_selector("a")
                        snippet_el = await res.query_selector("div.VwiC3b")
                        
                        if title_el and link_el:
                            title = await title_el.inner_text()
                            href = await link_el.get_attribute("href")
                            snippet = await snippet_el.inner_text() if snippet_el else ""
                            
                            if "wellfound.com/job" in href and href not in seen_urls:
                                seen_urls.add(href)
                                
                                # Parse title: "Product Manager Intern at Example Startup"
                                company_name = "Unknown Startup"
                                if " at " in title:
                                    company_name = title.split(" at ")[-1].split(" - ")[0].split(" | ")[0]
                                
                                clean_title = title.split(" at ")[0]
                                
                                all_jobs.append(ScrapedJob(
                                    title=clean_title,
                                    company_name=company_name,
                                    location="Startup Remote/Hub",
                                    source_platform="wellfound",
                                    source_url=href,
                                    description=snippet,
                                    experience_level="entry_level",
                                ))
                except Exception as e:
                    print(f"[Wellfound] Error parsing Google Dork result: {e}")
                finally:
                    await page.close()
                    await asyncio.sleep(3) # Be very polite to Google
            
            await browser.close()
            
        print(f"[Wellfound] Total unique jobs scraped via Dorking: {len(all_jobs)}")
        return all_jobs
