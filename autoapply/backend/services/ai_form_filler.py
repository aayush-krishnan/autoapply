"""AI-powered service to answer custom job application questions."""

import google.generativeai as genai
from config import settings
import json

class AIFormFiller:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    async def answer_question(self, question_text: str, profile_data: dict) -> str:
        """
        Uses Gemini to determine the best answer for a custom form question 
        based on the user's master profile.
        """
        prompt = f"""
        You are an expert career assistant helping a Master of Engineering Management (MEM) candidate apply for Product Management (PM) roles.
        The job application form has a custom question: "{question_text}"

        Based on the candidate's profile below, provide a short, professional, and truthful answer (max 3 sentences).
        
        Guidelines:
        - Highlight engineering management skills, technical background, and business acumen where relevant.
        - If it's a Yes/No question regarding visa sponsorship, the candidate's status is: "Requires sponsorship (F-1 student seeking CPT/OPT/H1B)".
        - Keep the tone confident but humble.
        
        Candidate Profile:
        {json.dumps(profile_data, indent=2)}

        Answer:
        """
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            # Clean up markdown if any
            answer = answer.replace("\"", "").replace("'", "")
            return answer
        except Exception as e:
            print(f"AI Form Filler Error: {e}")
            return ""

ai_filler = AIFormFiller()
