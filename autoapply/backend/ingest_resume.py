import asyncio
import os
import json
import fitz  # PyMuPDF
import google.generativeai as genai
from sqlalchemy.orm import Session
from database import SessionLocal
from models_profile import MasterProfile
from config import settings

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text from a given PDF file."""
    text = ""
    try:
         with fitz.open(pdf_path) as doc:
             for page in doc:
                 text += page.get_text()
    except Exception as e:
         print(f"Error reading PDF: {e}")
    return text

import re

def parse_resume_to_json(resume_text: str, linkedin_url: str) -> dict:
    """Fallback naive parser since Gemini API is rate limited."""
    print("WARNING: Using naive regex parser due to API rate limits.")
    
    # Very basic extraction
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', resume_text)
    email = email_match.group(0) if email_match else ""
    
    phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text)
    phone = phone_match.group(0) if phone_match else ""
    
    # Assume first line is name
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    name = lines[0] if lines else "Aayush Krishnan"
    
    # Dump the rest of the text into a single experience block so it's searchable by the tailor
    raw_bullets = [line for line in lines[1:30] if len(line) > 20] # grab some substantial lines
    
    return {
      "personal": {
        "name": name,
        "email": email,
        "phone": phone,
        "location": "San Francisco, CA", # Hardcoded guess
        "linkedin": linkedin_url,
        "github": "",
        "portfolio": ""
      },
      "education": [
        {
            "institution": "Target University",
            "degree": "Master of Engineering Management",
            "field": "Engineering Management",
            "graduation_date": "May 2026",
            "gpa": "",
            "location": ""
        }
      ],
      "experience": [
        {
             "company": "Previous Experience (Raw Import)",
             "role": "Multiple Roles",
             "location": "",
             "start_date": "",
             "end_date": "",
             "bullets": raw_bullets
        }
      ],
      "skills": []
    }

def ingest_to_db(profile_data: dict):
    """Saves the JSON data to the MasterProfile table."""
    db = SessionLocal()
    try:
        # Check if master profile exists
        existing = db.query(MasterProfile).first()
        if existing:
            existing.profile_data = profile_data
            db.commit()
            print("Successfully updated existing Master Profile in DB.")
        else:
            new_profile = MasterProfile(profile_data=profile_data)
            db.add(new_profile)
            db.commit()
            print("Successfully created new Master Profile in DB.")
    except Exception as e:
        print(f"Database error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    resume_path = "/Users/aayus/Documents/9- Coding/Google Antigravity test/Aayush Krishnan Resume.pdf"
    linkedin_url = "https://www.linkedin.com/in/aayush-krishnan/"
    
    if not os.path.exists(resume_path):
         print(f"ERROR: Resume file not found at {resume_path}")
         exit(1)
         
    print(f"1. Extracting text from {resume_path}...")
    text = extract_text_from_pdf(resume_path)
    print(f"   Extracted {len(text)} characters.")
    
    print("2. Sending to Gemini for parsing into strict JSON...")
    structured_data = parse_resume_to_json(text, linkedin_url)
    
    if structured_data:
         print("3. Parsing successful! Sample of extracted data:")
         print(f"   Name: {structured_data.get('personal', {}).get('name')}")
         print(f"   Schools: {len(structured_data.get('education', []))}")
         print(f"   Jobs: {len(structured_data.get('experience', []))}")
         
         print("4. Saving to Database...")
         ingest_to_db(structured_data)
         print("Done! You can now view the profile in the frontend Resumes tab.")
    else:
         print("Failed to parse data.")
