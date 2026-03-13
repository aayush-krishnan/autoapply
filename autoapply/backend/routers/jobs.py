import logging
logger = logging.getLogger(__name__)

"""Jobs API router — discovery, listing, search, and scraping."""

import time
import random
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from database import get_db
from scrapers import ScrapedJob, parse_posted_at
from config import settings
from models import JobListing, Company, ScraperRun, generate_title_hash
from schemas import (
    JobListingResponse, JobListingDetail, PaginatedJobs,
    ScrapeRequest, ScrapeResponse,
)
from scrapers.indeed import IndeedScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.wellfound import WellfoundScraper
from scrapers.twitter import TwitterScraper
from scrapers.simplyhired import SimplyHiredScraper
from scrapers.builtin import BuiltInScraper
from scrapers.ziprecruiter import ZipRecruiterScraper
from scrapers.mcp_scraper import MCPJobScraper
from services.scorer import score_job
from services.dedup import find_existing_job
from config import settings

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("", response_model=PaginatedJobs)
async def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    keyword: str = Query(None, description="Search keyword"),
    location: str = Query(None, description="Filter by location"),
    min_score: int = Query(None, ge=0, le=100, description="Minimum match score"),
    source: str = Query(None, description="Filter by source platform"),
    show_dismissed: bool = Query(False, description="Include dismissed jobs"),
    db: Session = Depends(get_db),
):
    """List discovered jobs with pagination and filters."""
    query = db.query(JobListing)

    if not show_dismissed:
        query = query.filter(JobListing.is_dismissed == False)  # noqa: E712

    if keyword:
        query = query.filter(
            (JobListing.title.ilike(f"%{keyword}%")) |
            (JobListing.company_name.ilike(f"%{keyword}%")) |
            (JobListing.description.ilike(f"%{keyword}%"))
        )

    if location:
        query = query.filter(JobListing.location.ilike(f"%{location}%"))

    if min_score is not None:
        query = query.filter(JobListing.match_score >= min_score)

    if source:
        query = query.filter(JobListing.source_platform == source)

    total = query.count()
    total_pages = max(1, (total + per_page - 1) // per_page)

    jobs = (
        query
        .order_by(desc(JobListing.match_score), desc(JobListing.discovered_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    # Enrich with H1B sponsor tier from company
    job_responses = []
    for job in jobs:
        resp = JobListingResponse.model_validate(job)
        if job.company:
            resp.h1b_sponsor_tier = job.company.h1b_sponsor_tier
        else:
            # Check config tiers
            company_lower = (job.company_name or "").lower()
            if any(c in company_lower for c in settings.H1B_TIER1_LOWER):
                resp.h1b_sponsor_tier = "tier1"
            elif any(c in company_lower for c in settings.H1B_TIER2_LOWER):
                resp.h1b_sponsor_tier = "tier2"
            elif any(c in company_lower for c in settings.H1B_NO_SPONSOR_LOWER):
                resp.h1b_sponsor_tier = "no_sponsor"
        job_responses.append(resp)

    return PaginatedJobs(
        jobs=job_responses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/stats")
async def get_job_stats(db: Session = Depends(get_db)):
    """Summary stats specifically for jobs ( legacy support )."""
    total = db.query(JobListing).count()
    applied = db.query(JobListing).filter(JobListing.status == "applied").count()
    return {"total": total, "applied": applied}


@router.get("/{job_id}", response_model=JobListingDetail)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific job."""
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}/dismiss")
async def dismiss_job(job_id: str, db: Session = Depends(get_db)):
    """Dismiss a job from the feed."""
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.is_dismissed = True
    db.commit()
    return {"status": "dismissed", "job_id": job_id}


@router.put("/{job_id}/status")
async def update_job_status(
    job_id: str, status: str = Query(...), db: Session = Depends(get_db)
):
    """Update a job's status (new, interested, applied, dismissed)."""
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    valid_statuses = ["new", "interested", "applied", "dismissed"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

    job.status = status
    if status == "dismissed":
        job.is_dismissed = True
    db.commit()
    return {"status": status, "job_id": job_id}


@router.post("/scrape", response_model=ScrapeResponse)
async def trigger_scrape(
    request: ScrapeRequest = None,
    db: Session = Depends(get_db),
):
    """Trigger a manual job scrape from specified sources."""
    if request is None:
        request = ScrapeRequest(sources=["indeed", "linkedin", "wellfound", "twitter", "simplyhired", "builtin", "ziprecruiter"])
    
    return await run_scrape_logic(db, request.sources)

async def run_scrape_logic(db: Session, sources: list[str]):
    """Core logic to run scrapers, score jobs, and save to DB."""
    start_time = time.time()
    total_found = 0
    total_new = 0
    total_dup = 0

    # Create scraper run record
    scraper_run = ScraperRun(
        source=",".join(sources),
        status="running",
    )
    db.add(scraper_run)
    db.commit()

    scrapers = {
        "indeed": MCPJobScraper("indeed") if settings.USE_MCP else IndeedScraper(),
        "linkedin": MCPJobScraper("linkedin") if settings.USE_MCP else LinkedInScraper(),
        "wellfound": WellfoundScraper(),
        "twitter": TwitterScraper(),
        "simplyhired": SimplyHiredScraper(),
        "builtin": BuiltInScraper(),
        "ziprecruiter": ZipRecruiterScraper(),
    }

    for source_name in sources:
        scraper = scrapers.get(source_name)
        if not scraper:
            continue

        try:
            # Randomly sample to avoid rate limits while casting a broad net across runs
            selected_keywords = random.sample(settings.TARGET_KEYWORDS, min(20, len(settings.TARGET_KEYWORDS)))
            selected_locations = random.sample(settings.TARGET_CITIES, min(4, len(settings.TARGET_CITIES)))

            raw_jobs = await scraper.scrape(
                keywords=selected_keywords,
                locations=selected_locations,
            )
            total_found += len(raw_jobs)

            for raw_job in raw_jobs:
                # Check for duplicates
                existing = find_existing_job(
                    db, raw_job.title, raw_job.company_name, raw_job.source_url
                )
                if existing:
                    total_dup += 1
                    continue

                # Get or create company
                company = db.query(Company).filter(
                    func.lower(Company.name) == raw_job.company_name.lower()
                ).first()
                if not company:
                    # Determine H1B tier
                    h1b_tier = None
                    cl = raw_job.company_name.lower()
                    if any(c in cl for c in settings.H1B_TIER1_LOWER):
                        h1b_tier = "tier1"
                    elif any(c in cl for c in settings.H1B_TIER2_LOWER):
                        h1b_tier = "tier2"
                    elif any(c in cl for c in settings.H1B_NO_SPONSOR_LOWER):
                        h1b_tier = "no_sponsor"

                    company = Company(
                        name=raw_job.company_name,
                        h1b_sponsor_tier=h1b_tier,
                    )
                    db.add(company)
                    db.flush()

                # Calculate real days_ago for scoring
                posted_dt = parse_posted_at(raw_job.posted_at)
                days_ago = (datetime.now(timezone.utc) - posted_dt.replace(tzinfo=timezone.utc)).days if posted_dt else 1

                # Calculate match score with real data
                match_score = score_job(
                    title=raw_job.title,
                    company_name=raw_job.company_name,
                    location=raw_job.location,
                    description=raw_job.description,
                    visa_info=raw_job.visa_info,
                    posted_days_ago=days_ago,
                )

                # Create job listing
                job = JobListing(
                    company_id=company.id,
                    title=raw_job.title,
                    description=raw_job.description,
                    location=raw_job.location,
                    experience_level=raw_job.experience_level,
                    salary_range=raw_job.salary_range,
                    source_platform=raw_job.source_platform,
                    source_url=raw_job.source_url,
                    match_score=match_score,
                    visa_info=raw_job.visa_info,
                    company_name=raw_job.company_name,
                    posted_at=posted_dt,
                    title_hash=generate_title_hash(raw_job.title, raw_job.company_name)
                )
                db.add(job)
                total_new += 1

            db.commit()
        except Exception as e:
            logger.info(f"[Scrape] Error with {source_name}: {e}")
            db.rollback()

    # Update scraper run record
    duration = time.time() - start_time
    scraper_run.completed_at = datetime.now(timezone.utc)
    scraper_run.jobs_found = total_found
    scraper_run.jobs_new = total_new
    scraper_run.jobs_duplicate = total_dup
    scraper_run.status = "completed"
    db.commit()

    return ScrapeResponse(
        status="completed",
        jobs_found=total_found,
        jobs_new=total_new,
        jobs_duplicate=total_dup,
        duration_seconds=round(duration, 2),
    )
