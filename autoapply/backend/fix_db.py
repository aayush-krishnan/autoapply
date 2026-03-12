from sqlalchemy.orm import Session
from database import SessionLocal
from models_profile import MasterProfile
import json

def fix_profile():
    db = SessionLocal()
    try:
        profile = db.query(MasterProfile).first()
        if not profile:
            print("No profile to fix")
            return
            
        data = profile.profile_data
        
        # Fix education keys
        for edu in data.get("education", []):
            if "graduation_date" in edu:
                edu["graduation"] = edu.pop("graduation_date")
            if "field" in edu:
                # not strictly required in schema, but we can leave it
                pass
                
        # Fix experience keys
        for exp in data.get("experience", []):
            if "role" in exp:
                exp["title"] = exp.pop("role")
            if "start_date" in exp and "end_date" in exp:
                exp["dates"] = f"{exp.pop('start_date')} - {exp.pop('end_date')}"
                
        # Fix skills format
        if isinstance(data.get("skills"), list):
            data["skills"] = {"technical": data["skills"], "domain": [], "soft": []}
            
        profile.profile_data = data
        db.commit()
        print("Profile fixed successfully.")
    except Exception as e:
        print("Error:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_profile()
