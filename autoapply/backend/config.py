"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    # Google AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./autoapply.db")

    # Scraper
    SCRAPE_INTERVAL_HOURS: int = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))
    MAX_JOBS_PER_SCRAPE: int = int(os.getenv("MAX_JOBS_PER_SCRAPE", "100"))

    # Target search config - Keyword Permutation Engine
    ROLE_BASE: list[str] = [
        "Product Manager", "Product", "PM", "APM", 
        "Technical Product Manager", "Platform PM", "Product Owner",
        "Growth PM", "Data PM", "Internal PM", "Associate PM"
    ]
    FOCUS_AREA: list[str] = [
        "AI", "Machine Learning", "B2B SaaS", "Underwriting", 
        "Fintech", "Go-To-Market", "Strategy", "Founders Associate",
        "Web3", "ClimateTech", "Robotics", "HealthTech", "Sustainability", ""
    ]
    SENIORITY: list[str] = [
        "Intern", "Internship", "Co-op", "Entry Level", "New Grad",
        "Associate", "University Graduate", "Recent Grad"
    ]

    @property
    def TARGET_KEYWORDS(self) -> list[str]:
        """Generate all permutations of focus + role + seniority."""
        keywords = set()
        for focus in self.FOCUS_AREA:
            for role in self.ROLE_BASE:
                for seniority in self.SENIORITY:
                    # Construct string, skipping empty focus areas
                    parts = [focus, role, seniority]
                    kw = " ".join(p for p in parts if p).strip()
                    keywords.add(kw)
        
        # Also add standalone roles with just seniority
        for role in self.ROLE_BASE:
            for seniority in self.SENIORITY:
                keywords.add(f"{role} {seniority}")
                
        return list(keywords)

    TARGET_CITIES: list[str] = [
        "New York",
        "San Francisco",
        "Seattle",
        "Boston",
        "Chicago",
        "Austin",
        "Los Angeles",
        "Washington",
    ]
    # Relaxed filtering - we now ingest these and let the LLM score them
    EXCLUDE_TYPES: list[str] = []

    # H1B sponsor tiers (companies known to sponsor post-internship)
    H1B_TIER1: list[str] = [
        "Google", "Amazon", "Microsoft", "Meta", "Apple",
        "Uber", "Salesforce", "Adobe", "Stripe", "Airbnb", "Netflix",
    ]
    H1B_TIER2: list[str] = [
        "IBM", "Deloitte", "EY", "JPMorgan", "Goldman Sachs",
        "Visa", "Qualcomm", "Intel", "Oracle", "SAP", "Cisco", "VMware",
    ]
    H1B_NO_SPONSOR: list[str] = [
        "CBRE", "Grant Thornton", "NSK",
    ]


settings = Settings()
