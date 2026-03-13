"""AI-powered service to answer custom job application questions."""

import google.generativeai as genai
from config import settings
import json

class AIFormFiller:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from config import settings
            import google.generativeai as genai
            # Ensure configured (lifespan usually handles this, but property ensures it)
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._model = genai.GenerativeModel('gemini-2.0-flash')
        return self._model

    async def answer_question(self, question_text: str, profile_data: dict) -> str:
        """
        Uses Gemini to determine the best answer for a custom form question 
        based on the user's master profile.
        """
        # Strip PII before sending to AI
        safe_profile = {k: v for k, v in profile_data.items() if k != "personal"}
        safe_profile["personal_context"] = {
            "name": profile_data.get("personal", {}).get("name", ""),
            "visa_status": "Requires sponsorship (F-1 student seeking CPT/OPT/H1B)"
        }

        prompt = f"""
        You are an expert career assistant helping a Master of Engineering Management (MEM) candidate apply for Product Management (PM) roles.
        The job application form has a custom question: "{question_text}"

        Based on the candidate's profile below, provide a short, professional, and truthful answer (max 3 sentences).
        
        Guidelines:
        - Highlight engineering management skills, technical background, and business acumen where relevant.
        - If it's a Yes/No question regarding visa sponsorship, use the candidate's status: "{safe_profile['personal_context']['visa_status']}".
        - Keep the tone confident but humble.
        
        Candidate Profile (Sanitized):
        {json.dumps(safe_profile, indent=2)}

        Answer:
        """
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            # Clean up markdown if any
            answer = answer.replace("\"", "").replace("'", "")
            return answer
        except Exception as e:
            logger.error(f"AI Form Filler Error: {e}")
            return ""

logger = logging.getLogger(__name__)
ai_filler = AIFormFiller()
