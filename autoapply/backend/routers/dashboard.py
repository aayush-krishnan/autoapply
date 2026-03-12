"""Dashboard API router — aggregated stats and analytics."""

from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import JobListing, Company
from schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get aggregated dashboard statistics."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Total non-dismissed jobs
    total_jobs = db.query(JobListing).filter(
        JobListing.is_dismissed == False  # noqa: E712
    ).count()

    # Jobs discovered today
    jobs_today = db.query(JobListing).filter(
        JobListing.discovered_at >= today_start,
        JobListing.is_dismissed == False,  # noqa: E712
    ).count()

    # Average match score
    avg_score_result = db.query(func.avg(JobListing.match_score)).filter(
        JobListing.match_score.isnot(None),
        JobListing.is_dismissed == False,  # noqa: E712
    ).scalar()
    avg_score = round(avg_score_result, 1) if avg_score_result else 0.0

    # Top companies (by number of listings)
    top_companies_query = (
        db.query(
            JobListing.company_name,
            func.count(JobListing.id).label("count"),
            func.avg(JobListing.match_score).label("avg_score"),
        )
        .filter(
            JobListing.is_dismissed == False,  # noqa: E712
            JobListing.company_name.isnot(None),
        )
        .group_by(JobListing.company_name)
        .order_by(func.count(JobListing.id).desc())
        .limit(10)
        .all()
    )
    top_companies = [
        {
            "name": row[0],
            "count": row[1],
            "avg_score": round(row[2], 1) if row[2] else 0,
        }
        for row in top_companies_query
    ]

    # Jobs by source
    source_counts = (
        db.query(
            JobListing.source_platform,
            func.count(JobListing.id),
        )
        .filter(JobListing.is_dismissed == False)  # noqa: E712
        .group_by(JobListing.source_platform)
        .all()
    )
    jobs_by_source = {row[0]: row[1] for row in source_counts}

    # Score distribution
    high = db.query(JobListing).filter(
        JobListing.match_score >= 80,
        JobListing.is_dismissed == False,  # noqa: E712
    ).count()
    medium = db.query(JobListing).filter(
        JobListing.match_score >= 60,
        JobListing.match_score < 80,
        JobListing.is_dismissed == False,  # noqa: E712
    ).count()
    low = db.query(JobListing).filter(
        JobListing.match_score < 60,
        JobListing.is_dismissed == False,  # noqa: E712
    ).count()

    return DashboardSummary(
        total_jobs=total_jobs,
        jobs_today=jobs_today,
        avg_score=avg_score,
        top_companies=top_companies,
        jobs_by_source=jobs_by_source,
        score_distribution={"high": high, "medium": medium, "low": low},
    )
