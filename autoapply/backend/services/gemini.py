"""Gemini AI service for job description parsing and analysis."""

import google.generativeai as genai
import json
import re

from config import settings


class GeminiService:
    """Wrapper around Google Gemini Pro for job-related AI tasks."""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.pro_model = genai.GenerativeModel("gemini-2.0-flash")

    async def parse_job_description(self, title: str, description: str) -> dict:
        """
        Extract structured information from a job description.

        Returns:
            dict with keys: required_skills, nice_to_have_skills,
            experience_years, visa_info, is_internship, key_responsibilities
        """
        if not description or len(description) < 20:
            return {
                "required_skills": [],
                "nice_to_have_skills": [],
                "experience_years": "internship",
                "visa_info": "unknown",
                "is_internship": "intern" in title.lower(),
                "key_responsibilities": [],
            }

        prompt = f"""Analyze this job posting and extract structured information.

Job Title: {title}
Job Description: {description[:3000]}

Return a JSON object with these exact keys:
- "required_skills": list of required skills/qualifications (strings)
- "nice_to_have_skills": list of nice-to-have skills (strings)
- "experience_years": expected experience (e.g. "0-1", "internship", "2-3")
- "visa_info": one of "cpt_opt_ok", "no_sponsorship", "sponsors_h1b", "unknown"
- "is_internship": boolean
- "key_responsibilities": list of 3-5 main responsibilities (strings)

Return ONLY valid JSON, no markdown formatting."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Clean up any markdown code fences
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

            return json.loads(text)
        except Exception as e:
            print(f"[Gemini] Error parsing job description: {e}")
            return {
                "required_skills": [],
                "nice_to_have_skills": [],
                "experience_years": "unknown",
                "visa_info": "unknown",
                "is_internship": "intern" in title.lower(),
                "key_responsibilities": [],
            }

    async def enrich_job_with_company_intel(self, company_name: str) -> dict:
        """
        Get AI-powered intelligence about a company's hiring practices.

        Returns:
            dict with keys: h1b_sponsor_likelihood, company_culture,
            interview_process, glassdoor_summary
        """
        prompt = f"""Based on your knowledge, provide brief intelligence about {company_name} for a job seeker:

Return a JSON object with these exact keys:
- "h1b_sponsor_likelihood": one of "high", "medium", "low", "unknown"
- "known_for": 1-2 sentence description of what the company is known for
- "interview_tips": 1-2 sentences about their typical interview process
- "intern_program_quality": one of "excellent", "good", "average", "unknown"

Return ONLY valid JSON, no markdown formatting."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            return json.loads(text)
        except Exception as e:
            print(f"[Gemini] Error getting company intel: {e}")
            return {
                "h1b_sponsor_likelihood": "unknown",
                "known_for": "",
                "interview_tips": "",
                "intern_program_quality": "unknown",
            }


# Singleton
gemini_service = GeminiService()
