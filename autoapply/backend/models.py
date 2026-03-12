"""SQLAlchemy database models for AutoApply."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, JSON, ForeignKey
)
from sqlalchemy.orm import relationship

from database import Base


def generate_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
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
    company_id = Column(String, ForeignKey("companies.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)
    source_platform = Column(String, nullable=False)  # "linkedin", "indeed", "glassdoor"
    source_url = Column(String, nullable=False, unique=True)
    match_score = Column(Integer, nullable=True)  # 0-100
    extracted_keywords = Column(JSON, nullable=True)
    visa_info = Column(String, nullable=True)  # "cpt_opt_ok", "no_sponsorship", "unknown"
    company_name = Column(String, nullable=True)  # Denormalized for easy display
    is_dismissed = Column(Boolean, default=False)
    posted_at = Column(DateTime, nullable=True)
    discovered_at = Column(DateTime, default=utcnow)
    status = Column(String, default="new")  # "new", "interested", "applied", "dismissed"

    # Relationships
    company = relationship("Company", back_populates="job_listings")


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
