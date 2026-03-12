"""Deduplication service for job listings across sources."""

from difflib import SequenceMatcher
from sqlalchemy.orm import Session

from models import JobListing


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    return text.lower().strip().replace("  ", " ")


def are_jobs_duplicate(job1_title: str, job1_company: str, job1_location: str,
                       job2_title: str, job2_company: str, job2_location: str,
                       threshold: float = 0.8) -> bool:
    """
    Check if two jobs are duplicates using fuzzy matching.

    Compares normalized title + company + location.
    """
    text1 = normalize_text(f"{job1_title} {job1_company} {job1_location}")
    text2 = normalize_text(f"{job2_title} {job2_company} {job2_location}")

    similarity = SequenceMatcher(None, text1, text2).ratio()
    return similarity >= threshold


def find_existing_job(db: Session, title: str, company_name: str,
                      source_url: str) -> JobListing | None:
    """
    Check if a job already exists in the database.

    First checks exact URL match, then fuzzy title+company match.
    """
    # 1. Exact URL match
    existing = db.query(JobListing).filter(
        JobListing.source_url == source_url
    ).first()
    if existing:
        return existing

    # 2. Fuzzy match on title + company (for cross-platform dedup)
    title_normalized = normalize_text(title)
    company_normalized = normalize_text(company_name)

    # Get recent jobs from the same company
    candidates = db.query(JobListing).filter(
        JobListing.company_name.ilike(f"%{company_normalized[:20]}%")
    ).limit(50).all()

    for candidate in candidates:
        if are_jobs_duplicate(
            title, company_name, "",
            candidate.title, candidate.company_name or "", "",
        ):
            return candidate

    return None
