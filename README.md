# AutoApply 🚀

High-volume AI job discovery and automated application engine. Built for 2026 PM Internship cycle.

## 🌟 Features
- **High-Volume Discovery**: Generates 300+ keyword permutations (AI, SaaS, GTM, Strategy) to cast a massive net.
- **Multi-Source Scraping**: Scrapes LinkedIn, Indeed, Wellfound (Startups), and X.com (Twitter hiring chatter).
- **AI Scoring**: Every job is scored against your Master Profile using Gemini 2.0 Flash to ensure 90%+ match relevance.
- **Auto-Apply Bot**: Playwright-powered browser automation that fills out Greenhouse and Lever forms, uploads tailored resumes, and answers custom questions via LLM.
- **Cred-Style UI**: Premium, high-contrast dark theme dashboard for managing your application pipeline.

## 🛠️ Stack
- **Backend**: FastAPI, SQLAlchemy, Playwright, Google Generative AI (Gemini).
- **Frontend**: Next.js 16, Tailwind CSS, Lucide.
- **Database**: SQLite (Local) / PostgreSQL (Containerized).
- **Cloud**: Docker, Docker Compose ready.

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

### 5. Run with Docker (Recommended for Cloud)
```bash
docker-compose up --build
```

## 📈 Next Phases
- [ ] Phase 6: Full Cloud Deployment (AWS/DigitalOcean).
- [ ] Phase 7: Recruiter Outreach Automation (LinkedIn DMs).
- [ ] Phase 8: Interview Prep Coaching Integration.

## 🛠️ Troubleshooting & Common Blocks

### 1. Scraper 403/0 Results (Indeed & LinkedIn)
Job boards like Indeed and LinkedIn have extremely aggressive anti-scraping measures (Cloudflare, IP rate limiting).
- **Current Mitigation**: We use randomized delays and rotate search permutations.
- **Recommended Fix**: Use a **Proxy Service** (like BrightData, ScrapingBee, or Oxylabs) inside `scrapers/`. 
- **Wait/Backoff**: If you get too many 403s, wait 1-2 hours before running again.

### 2. Gemini Quota Violations
The Free Tier of Gemini has a strict Requests Per Minute (RPM) limit. 
- **Current Mitigation**: The system fallbacks to regex for resume parsing if AI is blocked.
- **Recommended Fix**: Upgrade to the **Pay-as-you-go tier** in Google AI Studio to increase RPM limits.

## 📦 Pushing to GitHub

To put this project on your personal GitHub:
1. Create a personal repository on [GitHub.com](https://github.com/new).
2. Run these commands:
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## 📄 License
MIT
