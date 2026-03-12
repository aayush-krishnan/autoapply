import asyncio
import os
from services.ats_filler import run_auto_apply
from database import SessionLocal
from models_profile import MasterProfile

async def run_test():
    # Write a dummy PDF to serve as the exported resume
    pdf_path = "/tmp/dummy_resume.pdf"
    with open(pdf_path, "w") as f:
        f.write("DUMMY PDF CONTENT")
        
    db = SessionLocal()
    profile = db.query(MasterProfile).first()
    db.close()
    
    data = profile.profile_data
    
    # Run the auto apply against our mock local file using file:// protocol
    # Since ATS script uses detect_ats(), we'll temporarily monkey patch the host explicitly to hit Lever branch
    import services.ats_filler
    services.ats_filler.detect_ats = lambda url: "LEVER"
    
    # We must use an absolute file URI
    file_uri = f"file:///tmp/mock_lever.html"
    print(f"Testing against: {file_uri}")
    
    screenshot = await run_auto_apply(file_uri, data, pdf_path)
    print(f"Success! Screenshot saved to: {screenshot}")

if __name__ == "__main__":
    asyncio.run(run_test())
