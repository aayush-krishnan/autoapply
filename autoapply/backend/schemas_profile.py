"""Pydantic schemas for the Master Profile and Resumes."""

from datetime import datetime
from pydantic import BaseModel, Field


# --- Master Profile Schemas ---

class PersonalInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    portfolio: str = ""
    location: str = ""


class EducationEntry(BaseModel):
    institution: str = ""
    degree: str = ""
    graduation: str = ""
    gpa: str = ""
    relevant_courses: list[str] = Field(default_factory=list)


class ExperienceEntry(BaseModel):
    company: str = ""
    title: str = ""
    dates: str = ""
    bullets: list[str] = Field(default_factory=list)
    skills_demonstrated: list[str] = Field(default_factory=list)


class Skills(BaseModel):
    technical: list[str] = Field(default_factory=list)
    domain: list[str] = Field(default_factory=list)
    soft: list[str] = Field(default_factory=list)


class MasterProfileSchema(BaseModel):
    personal: PersonalInfo = Field(default_factory=PersonalInfo)
    education: list[EducationEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    projects: list[dict] = Field(default_factory=list)
    certifications: list[dict] = Field(default_factory=list)
    publications: list[dict] = Field(default_factory=list)


# --- Tailored Resume Schemas ---

class TailoredExperienceEntry(ExperienceEntry):
    fidelity_score: float | None = None  # Confidence score from Gemini (0-1)
    original_bullets_used: list[int] = Field(default_factory=list)  # Mapping back to master


class TailoredResumeSchema(BaseModel):
    personal: PersonalInfo
    education: list[EducationEntry]
    experience: list[TailoredExperienceEntry]
    skills: Skills
    
    # Metadata
    job_id: str
    created_at: datetime
    google_doc_url: str | None = None
    google_doc_id: str | None = None
    ats_score_estimate: int | None = None
