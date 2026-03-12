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
    tailored = db.query(TailoredResume).filter(TailoredResume.job_id == job_id).first()
    if not tailored:
        raise HTTPException(status_code=400, detail="Tailored Resume not generated for this job yet.")

    # 4. Determine Resume Path (Local or Google Doc)
    pdf_filename = f"resume_{job_id}.pdf"
    pdf_path = os.path.join("/tmp", pdf_filename)
    
    # If it's a local filename (doesn't start with '#' and isn't a long Google ID)
    if tailored.google_doc_id and tailored.google_doc_id.startswith("Resume_") and tailored.google_doc_id.endswith(".pdf"):
        # This is a local file
        local_dir = os.path.join(os.getcwd(), "data", "resumes", "tailored")
        pdf_path = os.path.join(local_dir, tailored.google_doc_id)
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="Tailored local PDF file missing on server.")
        print(f"📄 Using local PDF for auto-apply: {pdf_path}")
    elif tailored.google_doc_id and len(tailored.google_doc_id) > 20:
        # Likely a Google Doc ID
        try:
            print(f"🌐 Exporting Google Doc {tailored.google_doc_id} to PDF...")
            await google_docs_service.export_doc_as_pdf(tailored.google_doc_id, pdf_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to export Google Doc PDF: {e}")
    else:
        raise HTTPException(status_code=400, detail="Tailored resume data is invalid or missing ID.")

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
