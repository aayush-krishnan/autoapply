"""Resume tailoring service integrating Gemini and Google Docs."""

import json
import re

from services.gemini import gemini_service
from services.google_docs import google_docs_service
from schemas_profile import MasterProfileSchema, TailoredResumeSchema, TailoredExperienceEntry


class ResumeTailorService:

    async def tailor_resume(self, job_title: str, job_description: str, master_profile: MasterProfileSchema) -> dict:
        """
        Uses Gemini to tailor a resume based on the Master Profile and Job Description.
        STRICT ANTI-HALLUCINATION PROMPT.
        """
        prompt = f"""You are an expert technical recruiter and resume writer.
Your task is to tailor a candidate's master resume to perfectly match a specific job description.

Target Job: {job_title}
Job Description: {job_description[:3000]}

Candidate's Master Profile (JSON):
{master_profile.model_dump_json(indent=2)}

CRITICAL ANTI-HALLUCINATION RULES:
1. DO NOT invent any numbers, metrics, or revenue figures.
2. DO NOT add skills the user does not have.
3. DO NOT change job titles or dates of employment.
4. You may ONLY reorder, select, and subtly rephrase the EXISTNG bullet points from the master profile to highlight relevance to the target job.
5. If the job requires "Data Analysis" and the user has a bullet about "SQL queries", you can rewrite the bullet to emphasize Data Analysis.
6. Select exactly 3 or 4 of the most relevant bullets per experience entry.

Output a valid JSON object matching the Candidate's Master Profile structure, but with the 'experience' array containing your tailored bullets.
Add a top-level key "fidelity_score" (0-100) indicating your confidence that no facts were hallucinated.

Return ONLY JSON, no markdown."""

        try:
            response = gemini_service.pro_model.generate_content(prompt)
            text = response.text.strip()
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            
            tailored_data = json.loads(text)
            
            # Basic validation
            fidelity = tailored_data.get("fidelity_score", 0)
            if fidelity < 90:
                print(f"[Tailor] Warning: Low fidelity score ({fidelity}). Potential hallucination.")

            return tailored_data
            
        except Exception as e:
            print(f"[Tailor] Error tailoring resume: {e}")
            # Fallback to returning master data
            return master_profile.model_dump()


resume_tailor_service = ResumeTailorService()
