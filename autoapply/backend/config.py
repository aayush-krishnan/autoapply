"""Application configuration loaded from environment variables using Pydantic Settings."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import cached_property

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Google AI
    GEMINI_API_KEY: str = ""
    API_KEY: str = "autoapply-secret-key-2026"

    # Google Docs / Drive
    GOOGLE_SERVICE_ACCOUNT_FILE: str = "google-credentials.json"
    GOOGLE_DRIVE_FOLDER_ID: str = ""
    GOOGLE_RESUME_TEMPLATE_ID: str = "1sTsA0rOhi2M0JrEibVfG4Ig8LEc-MAyY"

    # Database
    DATABASE_URL: str = "sqlite:///./autoapply.db"

    # Scraper
    SCRAPE_INTERVAL_HOURS: int = 6
    MAX_JOBS_PER_SCRAPE: int = 100
    PROXY_URL: str = ""

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

    @cached_property
    def TARGET_KEYWORDS(self) -> list[str]:
        """Generate all permutations and cache the result."""
        keywords = set()
        for focus in self.FOCUS_AREA:
            for role in self.ROLE_BASE:
                for seniority in self.SENIORITY:
                    parts = [focus, role, seniority]
                    kw = " ".join(p for p in parts if p).strip()
                    keywords.add(kw)
        
        for role in self.ROLE_BASE:
            for seniority in self.SENIORITY:
                keywords.add(f"{role} {seniority}")
                
        return list(keywords)

    @cached_property
    def TARGET_KEYWORDS_LOWER(self) -> list[str]:
        """Cache lowercased keywords for faster scoring."""
        return [kw.lower() for kw in self.TARGET_KEYWORDS]

    TARGET_CITIES: list[str] = [
        "New York", "San Francisco", "Seattle", "Boston", 
        "Chicago", "Austin", "Los Angeles", "Washington"
    ]

    # H1B sponsor tiers
    H1B_TIER1: list[str] = [
        "Google", "Amazon", "Microsoft", "Meta", "Apple",
        "Uber", "Salesforce", "Adobe", "Stripe", "Airbnb", "Netflix",
    ]
    H1B_TIER2: list[str] = [
        "IBM", "Deloitte", "EY", "JPMorgan", "Goldman Sachs",
        "Visa", "Qualcomm", "Intel", "Oracle", "SAP", "Cisco", "VMware",
    ]
    H1B_NO_SPONSOR: list[str] = ["CBRE", "Grant Thornton", "NSK"]

    @cached_property
    def H1B_TIER1_LOWER(self) -> set[str]:
        return {c.lower() for c in self.H1B_TIER1}

    @cached_property
    def H1B_TIER2_LOWER(self) -> set[str]:
        return {c.lower() for c in self.H1B_TIER2}

    @cached_property
    def H1B_NO_SPONSOR_LOWER(self) -> set[str]:
        return {c.lower() for c in self.H1B_NO_SPONSOR}

settings = Settings()
