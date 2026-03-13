import logging
logger = logging.getLogger(__name__)

"""Resumes API router — master profile and tailored resumes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi.responses import FileResponse
import os
from pathlib import Path

from database import get_db
from models import JobListing
from models_profile import MasterProfile, TailoredResume, ResumeSource
from schemas_profile import MasterProfileSchema, TailoredResumeSchema
from services.resume_tailor import resume_tailor_service
from services.google_docs import google_docs_service
from services.pdf_generator import pdf_generator_service
from config import settings

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])


@router.get("/master", response_model=MasterProfileSchema)
async def get_master_profile(db: Session = Depends(get_db)):
    """Get the user's master profile."""
    # Assuming single-user for now; fetch the first record
    profile = db.query(MasterProfile).first()
    if not profile or not profile.profile_data:
        # Return empty schema
        return MasterProfileSchema()
    
    return MasterProfileSchema(**profile.profile_data)


@router.post("/master", response_model=MasterProfileSchema)
async def update_master_profile(profile_data: MasterProfileSchema, db: Session = Depends(get_db)):
    """Update the user's master profile."""
    profile = db.query(MasterProfile).first()
    if not profile:
        profile = MasterProfile(profile_data=profile_data.model_dump())
        db.add(profile)
    else:
        profile.profile_data = profile_data.model_dump()
        profile.updated_at = datetime.now(timezone.utc)
        
    db.commit()
    return profile_data


@router.post("/tailor/{job_id}")
async def tailor_resume(job_id: str, db: Session = Depends(get_db)):
    """
    Trigger the resume tailoring process for a specific job:
    1. Fetch Job and Master Profile.
    2. Pass to Gemini for tailored bullets.
    3. Feed tailored bullets to Google Docs API to duplicate template.
    4. Save the generated Google Doc URL to DB.
    """
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    master_profile_record = db.query(MasterProfile).first()
    if not master_profile_record or not master_profile_record.profile_data:
        raise HTTPException(
            status_code=400, 
            detail="Master profile missing. Please complete it first."
        )

    # Convert mapping to Pydantic object
    schema = MasterProfileSchema(**master_profile_record.profile_data)


    # 1. Ask Gemini to Tailor Bullets
    tailored_data = await resume_tailor_service.tailor_resume(
        job_title=job.title,
        job_description=job.description or "",
        master_profile=schema
    )
    fidelity = tailored_data.pop("fidelity_score", 100)

    # 2. Build replacements dict for Google Docs
    # E.g., {{COMPANY_1_NAME}}, {{COMPANY_1_TITLE}}, {{COMPANY_1_BULLET_1}}
    replacements = {}
    experiences = tailored_data.get("experience", [])
    for idx, exp in enumerate(experiences):
        prefix = "{{COMPANY_" + str(idx+1)
        replacements[f"{prefix}_NAME}}"] = exp.get("company", "")
        replacements[f"{prefix}_TITLE}}"] = exp.get("title", "")
        replacements[f"{prefix}_DATES}}"] = exp.get("dates", "")
        
        bullets = exp.get("bullets", [])
        for b_idx in range(4): # Assume max 4 bullets supported by template
            bullet_text = bullets[b_idx] if b_idx < len(bullets) else ""
            if bullet_text:
                bullet_text = f"• {bullet_text}"
            replacements[f"{prefix}_BULLET_{b_idx+1}}}"] = bullet_text


    # 3. Generate Local PDF (Reliable alternative to Google Drive quota issues)
    filename = f"Resume_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Prepare data for local PDF template
    pdf_data = {
        "name": schema.personal.name,
        "email": schema.personal.email,
        "phone": schema.personal.phone,
        "location": schema.personal.location,
        "linkedin": schema.personal.linkedin,
        "portfolio": schema.personal.portfolio,
        "summary": tailored_data.get("summary", ""),
        "experience": tailored_data.get("experience", []),
        "education": tailored_data.get("education", []),
        "skills": tailored_data.get("skills", []), # Note: tailored_data['skills'] is a list of strings
        "certifications": tailored_data.get("certifications", [])
    }
    
    try:
        local_path = pdf_generator_service.generate_resume(pdf_data, filename)
        # return protected download URL
        doc_url = f"/api/resumes/download/{filename}"
        doc_id = filename 
        source = ResumeSource.local
        logger.info(f"✅ Local PDF generated: {local_path}")
    except Exception as e:
        logger.error(f"❌ Local PDF generation failed for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    # Optional: Still try to create Google Doc if configured, but don't let it crash the request
    try:
        if settings.GOOGLE_SERVICE_ACCOUNT_FILE and settings.GOOGLE_DRIVE_FOLDER_ID:
            template_id = settings.GOOGLE_RESUME_TEMPLATE_ID
            new_title = f"{schema.personal.name} - Resume - {job.company_name} ({job.title})"
            g_id, g_url = await google_docs_service.create_tailored_doc(
                template_id=template_id,
                replacements=replacements,
                new_title=new_title,
                folder_id=settings.GOOGLE_DRIVE_FOLDER_ID
            )
            # If Google succeeds, update the record later (we already have local URL as primary)
            source = ResumeSource.google_doc
            doc_id = g_id
            doc_url = g_url
            logger.info(f"✅ Google Doc also created: {g_url}")
    except Exception as g_e:
        logger.info(f"⚠️ Google Doc creation failed (likely quota): {g_e}")

    # 4. Save to Database
    tailored_record = TailoredResume(
        job_id=job_id,
        tailored_content=tailored_data,
        fidelity_score=fidelity,
        google_doc_id=doc_id,
        google_doc_url=doc_url,
        resume_source=source
    )
    db.add(tailored_record)
    db.commit()


    return {
        "status": "success",
        "job_id": job_id,
        "fidelity_score": fidelity,
        "google_doc_url": doc_url
    }

@router.get("/download/{filename}")
async def download_resume(filename: str):
    """
    Protected endpoint to download a tailored resume.
    Access controlled by global API key middleware.
    """
    # Import locally to avoid circular dependency if any
    output_dir = Path("data/resumes/tailored")
    file_path = output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Resume file not found")
        
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )
