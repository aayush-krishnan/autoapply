# AutoApply 🚀

High-volume AI job discovery and automated application engine. Built for 2026 PM Internship cycle.

## 🌟 Features
- **High-Volume Discovery**: Generates 300+ keyword permutations (AI, SaaS, GTM, Strategy) to cast a massive net.
- **Multi-Source Scraping**: Scrapes LinkedIn, Indeed, Wellfound (Startups), and X.com (Twitter hiring chatter).
- **AI Scoring**: Every job is scored against your Master Profile using Gemini 2.0 Flash to ensure 90%+ match relevance.
- **One-Page Resume Tailoring**: Automatically generates a high-fidelity, strictly one-page PDF resume tailored to each job description.
- **Strategic Keyword Embedding**: AI weaves job-specific keywords into your experience bullets while maintaining factual integrity (anti-hallucination).
- **Auto-Apply Bot**: Playwright-powered browser automation that fills out Greenhouse and Lever forms, uploads tailored resumes, and answers custom questions via LLM.
- **Cred-Style UI**: Premium, high-contrast dark theme dashboard for managing your application pipeline.

## 🛠️ Stack
- **Backend**: FastAPI, SQLAlchemy, Playwright, Google Generative AI (Gemini), fpdf2.
- **Frontend**: Next.js 16, Tailwind CSS, Lucide, Framer Motion.
- **Database**: SQLite (Local) / PostgreSQL (Containerized).

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- [Google Gemini API Key](https://aistudio.google.com/)

### 2. Installation
```bash
# Setup Backend
cd autoapply/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium --with-deps

# Setup Frontend
cd ../frontend
npm install
```

### 3. Environment Config
Create a `.env` in the root directory:
```env
GEMINI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./autoapply.db
GOOGLE_APPLICATION_CREDENTIALS=path/to/google_service_account.json
# Optional:
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_if_using_google_docs
PROXY_URL=your_proxy_url
```

### 4. Run Locally
```bash
# Terminal 1: Backend
cd autoapply/backend
uvicorn main:app --reload

# Terminal 2: Frontend
cd autoapply/frontend
npm run dev
```

## 🛠️ Key Modules
- **Resume Tailor**: `backend/services/resume_tailor.py` - AI logic for strategic bullet points.
- **PDF Generator**: `backend/services/pdf_generator.py` - Local, space-optimized PDF assembly.
- **Scrapers**: `backend/scrapers/` - Multi-platform hiring signal discovery.
- **Auto-Apply**: `backend/routers/apply.py` - Automation engine for applying to roles.

## 📈 Roadmap
- [ ] Phase 7: Recruiter Outreach Automation (LinkedIn DMs).
- [ ] Phase 8: Interview Prep Coaching Integration.
- [ ] Phase 9: Advanced Application Analytics Dashboard.

## 📄 License
MIT
