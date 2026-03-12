"""Resume tailoring service integrating Gemini with strategic keyword embedding."""

import json
import re

from services.gemini import gemini_service
from services.google_docs import google_docs_service
from schemas_profile import MasterProfileSchema, TailoredResumeSchema, TailoredExperienceEntry


class ResumeTailorService:

    async def tailor_resume(self, job_title: str, job_description: str, master_profile: MasterProfileSchema) -> dict:
        """
        Uses Gemini to tailor a resume based on the Master Profile and Job Description.
        FEATURES: Strategic Keyword Embedding & Adaptive Summary.
        """
        prompt = f"""You are an expert technical recruiter and resume writer specialized in ATS (Applicant Tracking System) optimization.
Your task is to tailor a candidate's master resume to perfectly match a specific job description.

Target Job: {job_title}
Job Description: {job_description[:4000]}

Candidate's Master Profile (JSON):
{master_profile.model_dump_json(indent=2)}

CRITICAL TAILORING RULES:
1. **Strategic Keyword Embedding**: Analyze the Job Description for key terms (technical skills, methodologies, keywords). Weave these keywords into the experience bullet points where they naturally fit, while MAINTAINING FACTUAL INTEGRITY.
2. **Selective Selection**: Choose the 3-4 most relevant bullet points for each experience entry that directly address the job's requirements.
3. **Adaptive Hooks**: Generate a professional 'summary' (2-3 sentences) that specifically highlights why the candidate's background (HyperVerge, Clan, etc.) makes them an ideal fit for THIS role.
4. **Anti-Hallucination**: Do NOT invent metrics, revenue figures, or skills. You are rephrasing and prioritizing existing experience, not creating a fictional persona.
5. **Consistency**: Do NOT change job titles, company names, or dates.

Output Requirements:
- Return a valid JSON object matching the MasterProfileSchema structure.
- Include a 'summary' field.
- For each experience entry, provide 'dates' (string) and 'bullets' (list of strings).
- Add a top-level "fidelity_score" (0-100).
- RETURN ONLY THE JSON OBJECT. NO MARKDOWN."""

        try:
            response = gemini_service.pro_model.generate_content(prompt)
            text = response.text.strip()
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            
            tailored_data = json.loads(text)
            
            # Ensure field name consistency for PDF generation (dating back to previous fixes)
            if "experience" in tailored_data:
                for exp in tailored_data["experience"]:
                    if "start_date" in exp and "end_date" in exp:
                        exp["dates"] = f"{exp['start_date']} - {exp['end_date']}"
                    if "bullet_points" in exp:
                        exp["bullets"] = exp["bullet_points"]
            
            return tailored_data
            
        except Exception as e:
            print(f"[Tailor] Error tailoring resume: {e}")
            return master_profile.model_dump()


resume_tailor_service = ResumeTailorService()
