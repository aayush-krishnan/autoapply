"""X.com (Twitter) Monitor for early hiring signals and funding rounds."""

from playwright.async_api import async_playwright
import asyncio
from scrapers import BaseScraper, ScrapedJob

class TwitterScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "twitter"

    async def scrape(self, keywords: list[str], locations: list[str]) -> list[ScrapedJob]:
        all_jobs = []
        seen_urls = set()

        # Hiring signals (exact phrases tech leads use on Twitter)
        HIRING_SIGNALS = [
            '"we are hiring" AND "product intern"',
            '"dm me" AND "product manager intern"',
            '"looking for an APM"',
            '"series A" AND "hiring product"',
            '"hiring" AND "founding PM"',
            '"hiring" AND "product manager" AND "intern"',
            '"we\'re hiring" AND "product"',
            '"hiring" AND "associate product manager"'
        ]

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            )
            
            for signal in HIRING_SIGNALS:
                page = await context.new_page()
                try:
                    # Dorking X.com since search requires login. Google indexes high-engagement tech tweets
                    query = f"site:twitter.com OR site:x.com {signal}"
                    await page.goto(f"https://www.google.com/search?q={query}&tbs=qdr:w") # w = past week
                    
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
                            
                            if ("twitter.com" in href or "x.com" in href) and "/status/" in href and href not in seen_urls:
                                seen_urls.add(href)
                                
                                # Determine company/poster from title "AccountName (@handle) on X: ..."
                                # Or "AccountName on X: ..."
                                raw_name = title.split(" on ")[0] if " on " in title else "X.com Poster"
                                # Clean up if it has a handle in parens
                                company_name = raw_name.split(" (")[0]
                                
                                all_jobs.append(ScrapedJob(
                                    title=f"X Chatter: {company_name} Hiring",
                                    company_name=company_name,
                                    location="Global/Remote", # Twitter jobs are usually remote-friendly or undefined
                                    source_platform="twitter",
                                    source_url=href,
                                    description=snippet, # The tweet text
                                    experience_level="internship",
                                ))
                except Exception as e:
                    print(f"[Twitter] Error parsing chatter signal: {e}")
                finally:
                    await page.close()
                    await asyncio.sleep(2.5) # Anti-captcha delay
            
            await browser.close()
            
        print(f"[Twitter] Found {len(all_jobs)} active hiring signals/chatter.")
        return all_jobs
