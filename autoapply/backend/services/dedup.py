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


def find_existing_job(db: Session, title: str, company: str, source_url: str):
    """
    Find if a job already exists in the DB.
    Check priority:
    1. Exact URL match (fastest)
    2. Exact title_hash match (O(1) with index)
    3. Fuzzy match (fallback, computationally expensive)
    """
    # 1. Exact URL
    existing = db.query(JobListing).filter(JobListing.source_url == source_url).first()
    if existing: return existing

    # 2. Title Hash (New production-grade O(1) check)
    h = generate_title_hash(title, company)
    existing = db.query(JobListing).filter(JobListing.title_hash == h).first()
    if existing: return existing

    # 3. Fuzzy Match (Fallback for slight title variations)
    # Load limited candidates from the same company to avoid full table scan
    candidates = db.query(JobListing).filter(
        func.lower(JobListing.company_name) == company.lower()
    ).limit(20).all()

    for candidate in candidates:
        if are_jobs_duplicate(
            title, company_name, "",
            candidate.title, candidate.company_name or "", "",
        ):
            return candidate

    return None
