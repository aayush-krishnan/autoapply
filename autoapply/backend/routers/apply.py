from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from models_profile import MasterProfile, TailoredResume
from models import JobListing
from services.ats_filler import run_auto_apply
from services.google_docs import google_docs_service
import os

router = APIRouter(prefix="/api/apply", tags=["Apply"])

@router.post("/{job_id}")
async def trigger_auto_apply(job_id: str, db: Session = Depends(get_db)):
    """
    Triggers the headless browser to apply to the specified job using the tailored resume.
    """
    # 1. Fetch Job
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 2. Fetch Master Profile
    master = db.query(MasterProfile).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master Profile not found. Please fill it out first.")

    # 3. Fetch Tailored Resume
    tailored = db.query(TailoredResume).filter(TailoredResume.job_listing_id == job_id).first()
    if not tailored or not tailored.google_doc_id:
        raise HTTPException(status_code=400, detail="Tailored Resume not generated for this job yet.")

    # 4. Export the Google Doc as PDF
    pdf_filename = f"resume_{job_id}.pdf"
    pdf_path = os.path.join("/tmp", pdf_filename) # Using /tmp for now
    
    try:
        await google_docs_service.export_doc_as_pdf(tailored.google_doc_id, pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export PDF: {e}")

    # 5. Run the Playwright script
    try:
        screenshot_path = await run_auto_apply(job.source_url, master.profile_data, pdf_path)
    except ValueError as val_ext:
        raise HTTPException(status_code=400, detail=str(val_ext))
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Failed to run auto apply: {e}")

    # Return success message and screenshot path for frontend (if any)
    return {
        "status": "success",
        "message": "Auto-apply script successfully executed.",
        "screenshot": screenshot_path
    }
