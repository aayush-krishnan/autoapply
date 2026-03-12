"""SQLAlchemy database models for Master Profile and Resumes."""

from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from database import Base
from models import generate_uuid, utcnow


class MasterProfile(Base):
    """
    Stores the user's base resume data as a JSON object.
    For a single-user system, there is only one row here.
    """
    __tablename__ = "master_profiles"

    id = Column(String, primary_key=True, default=generate_uuid)
    # The `profile_data` column stores the structured JSON matching MasterProfileSchema
    profile_data = Column(JSON, nullable=False, default=dict)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class TailoredResume(Base):
    """
    Tracks a generated resume tailored for a specific job listing.
    """
    __tablename__ = "tailored_resumes"

    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, ForeignKey("job_listings.id"), nullable=False, unique=True)
    
    # The generated content
    tailored_content = Column(JSON, nullable=False)  # Matches TailoredResumeSchema
    
    # Metadata and integration
    fidelity_score = Column(Integer, nullable=True)  # Overall anti-hallucination score (0-100)
    google_doc_id = Column(String, nullable=True)
    google_doc_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    job_listing = relationship("JobListing", backref="tailored_resume")
