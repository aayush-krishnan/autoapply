"""SQLAlchemy database models for AutoApply."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
import hashlib

from database import Base


def generate_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


def generate_title_hash(title: str, company: str) -> str:
    """Normalize title and company and return MD5 hash for O(1) dedup."""
    key = f"{title.lower().strip()}|{company.lower().strip()}"
    return hashlib.md5(key.encode()).hexdigest()


class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True, index=True)
    website = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    size_range = Column(String, nullable=True)
    glassdoor_rating = Column(Float, nullable=True)
    careers_page_url = Column(String, nullable=True)
    h1b_sponsor_tier = Column(String, nullable=True)  # "tier1", "tier2", "tier3", "no_sponsor", null
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    job_listings = relationship("JobListing", back_populates="company")


class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(String, primary_key=True, default=generate_uuid)
    company_id = Column(String, ForeignKey("companies.id"), nullable=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True, index=True)
    experience_level = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)
    source_platform = Column(String, nullable=False, index=True)  # "linkedin", "indeed", "glassdoor"
    source_url = Column(String, nullable=False, unique=True)
    match_score = Column(Integer, nullable=True, index=True)  # 0-100
    extracted_keywords = Column(JSON, nullable=True)
    visa_info = Column(String, nullable=True)  # "cpt_opt_ok", "no_sponsorship", "unknown"
    company_name = Column(String, nullable=True, index=True)  # Denormalized for easy display
    title_hash = Column(String, nullable=True, index=True)  # MD5 of title+company
    is_dismissed = Column(Boolean, default=False, index=True)
    posted_at = Column(DateTime, nullable=True)
    discovered_at = Column(DateTime, default=utcnow, index=True)
    status = Column(String, default="new", index=True)  # "new", "interested", "applied", "dismissed"

    # Relationships
    company = relationship("Company", back_populates="job_listings")


class SystemConfig(Base):
    """Key-value store for dynamic system settings (e.g. proxy, scrape interval)."""
    __tablename__ = "system_config"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class ScraperRun(Base):
    __tablename__ = "scraper_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    source = Column(String, nullable=False)  # "linkedin", "indeed"
    started_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)
    jobs_found = Column(Integer, default=0)
    jobs_new = Column(Integer, default=0)
    jobs_duplicate = Column(Integer, default=0)
    status = Column(String, default="running")  # "running", "completed", "failed"
    error = Column(Text, nullable=True)
