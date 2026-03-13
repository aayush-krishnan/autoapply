import logging
import asyncio
from typing import List
from scrapers import BaseScraper, ScrapedJob
from services.mcp_client import get_mcp_client

logger = logging.getLogger("autoapply.scrapers.mcp")

class MCPJobScraper(BaseScraper):
    """
    Unified scraper using MCP servers (like JobSpy) to fetch jobs from multiple platforms.
    """

    def __init__(self, platform: str):
        self._platform = platform # 'linkedin', 'indeed', etc.

    @property
    def source_name(self) -> str:
        return f"mcp_{self._platform}"

    async def scrape(self, keywords: List[str], locations: List[str]) -> List[ScrapedJob]:
        """Scrape jobs via MCP tool calls."""
        all_jobs: List[ScrapedJob] = []
        
        # In a real scenario, this would be configured via settings.
        # For now, we'll assume a 'jobspy' MCP server is available.
        # Example command: npx -y @modelcontextprotocol/server-jobspy
        mcp_name = "jobspy"
        mcp_cmd = ["npx", "-y", "@modelcontextprotocol/server-jobspy"]
        
        try:
            client = await get_mcp_client(mcp_name, mcp_cmd)
            
            for kw in keywords:
                for loc in locations:
                    # JobSpy MCP tool 'search_jobs' parameters:
                    # site_name (List[str]), search_term (str), location (str), results_wanted (int), etc.
                    args = {
                        "site_name": [self._platform],
                        "search_term": kw,
                        "location": loc,
                        "results_wanted": 20,
                        "hours_old": 168 # 1 week
                    }
                    
                    try:
                        # result.content might contain the data
                        response = await client.call_tool("search_jobs", args)
                        
                        # Parsing depends on the exact output format of the MCP server.
                        # Usually it's a list of JSON objects or a formatted string.
                        # Assuming 'response' has a 'content' field with list of jobs.
                        # result.content is a list of TextContent/ImageContent/EmbeddedResource
                        
                        # For now, we log the response to understand the structure
                        # In a production setup, we'd have robust parsing here.
                        # logger.info(f"MCP Response for {kw}/{loc}: {response}")
                        
                        # Mock parsing based on expected JobSpy structure:
                        if hasattr(response, 'content'):
                            for content in response.content:
                                if hasattr(content, 'text'):
                                    import json
                                    try:
                                        jobs_data = json.loads(content.text)
                                        for job_raw in jobs_data:
                                            all_jobs.append(self._map_to_scraped_job(job_raw))
                                    except:
                                        # If text is not JSON, might be a table or text summary
                                        logger.warning(f"Could not parse MCP text as JSON: {content.text[:100]}")
                                        
                    except Exception as e:
                        logger.error(f"Error scraping via MCP for {kw} in {loc}: {e}")
                        
                    await asyncio.sleep(2) # Be polite
                    
        except Exception as e:
            logger.error(f"Failed to initialize MCP client '{mcp_name}': {e}")
            
        return all_jobs

    def _map_to_scraped_job(self, data: dict) -> ScrapedJob:
        """Map raw MCP data to ScrapedJob model."""
        return ScrapedJob(
            title=data.get("title", "Unknown"),
            company_name=data.get("company", "Unknown"),
            location=data.get("location", "Unknown"),
            source_platform=self._platform,
            source_url=data.get("job_url", ""),
            description=data.get("description", ""),
            posted_at=data.get("date_posted", ""),
            experience_level="internship" # Heuristic for our target
        )
