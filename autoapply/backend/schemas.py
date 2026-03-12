"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from pydantic import BaseModel


# --- Job Listing Schemas ---

class JobListingBase(BaseModel):
    title: str
    company_name: str | None = None
    location: str | None = None
    source_platform: str
    source_url: str
    description: str | None = None
    salary_range: str | None = None
    experience_level: str | None = None
    visa_info: str | None = None
    posted_at: datetime | None = None


class JobListingResponse(JobListingBase):
    id: str
    match_score: int | None = None
    extracted_keywords: list[str] | None = None
    is_dismissed: bool = False
    discovered_at: datetime
    status: str = "new"
    h1b_sponsor_tier: str | None = None  # From company

    class Config:
        from_attributes = True


class JobListingDetail(JobListingResponse):
    description: str | None = None


# --- Dashboard Schemas ---

class DashboardSummary(BaseModel):
    total_jobs: int
    jobs_today: int
    avg_score: float
    top_companies: list[dict]
    jobs_by_source: dict[str, int]
    score_distribution: dict[str, int]  # "high", "medium", "low"


# --- Scraper Schemas ---

class ScrapeRequest(BaseModel):
    sources: list[str] = ["indeed", "linkedin"]


class ScrapeResponse(BaseModel):
    status: str
    jobs_found: int
    jobs_new: int
    jobs_duplicate: int
    duration_seconds: float


# --- Pagination ---

class PaginatedJobs(BaseModel):
    jobs: list[JobListingResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
