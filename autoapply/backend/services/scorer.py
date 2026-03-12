"""Job scoring algorithm based on PRD §5.1.4."""

from config import settings


def score_job(
    title: str,
    company_name: str,
    location: str,
    description: str = "",
    visa_info: str = "",
    posted_days_ago: int = 0,
) -> int:
    """
    Score a job listing on a 0-100 scale.

    Weights (from PRD):
      - Keyword match:      25%
      - Skills overlap:     20%
      - Location fit:       10%
      - Company fit:        10%
      - Recency:            10%
      - H1B sponsor history: 15%
      - CPT/OPT friendly:   10%
    """
    score = 0.0
    title_lower = title.lower()
    desc_lower = description.lower()
    company_lower = company_name.lower()
    full_text = f"{title_lower} {desc_lower}"

    # --- 1. Keyword Match (25%) ---
    keyword_score = 0.0
    target_terms = [kw.lower() for kw in settings.TARGET_KEYWORDS]
    matches = sum(1 for term in target_terms if term in full_text)
    if matches > 0:
        keyword_score = min(matches / 2, 1.0)  # 2+ keyword matches = full score

    # Bonus: exact title match
    if any(term in title_lower for term in target_terms):
        keyword_score = max(keyword_score, 0.8)

    # Must have at least "intern" in title
    if "intern" in title_lower:
        keyword_score = max(keyword_score, 0.5)
    elif "intern" not in full_text:
        keyword_score *= 0.3  # Heavy penalty if "intern" isn't even mentioned

    score += keyword_score * 25

    # --- 2. Skills Overlap (20%) ---
    pm_skills = [
        "product", "roadmap", "agile", "scrum", "user research",
        "a/b test", "analytics", "sql", "python", "figma", "jira",
        "stakeholder", "cross-functional", "data-driven", "strategy",
        "user interview", "prioritization", "mvp", "sprint",
    ]
    skill_matches = sum(1 for skill in pm_skills if skill in full_text)
    skills_score = min(skill_matches / 5, 1.0)  # 5+ matches = full score
    score += skills_score * 20

    # --- 3. Location Fit (10%) ---
    location_lower = location.lower()
    target_cities_lower = [c.lower() for c in settings.TARGET_CITIES]
    location_score = 0.0
    if any(city in location_lower for city in target_cities_lower):
        location_score = 1.0
    elif "united states" in location_lower or "usa" in location_lower:
        location_score = 0.5
    score += location_score * 10

    # --- 4. Company Fit (10%) ---
    company_score = 0.5  # Default: unknown company
    # Known large tech companies get a boost
    big_tech = settings.H1B_TIER1 + settings.H1B_TIER2
    if any(bt.lower() in company_lower for bt in big_tech):
        company_score = 1.0
    elif any(ns.lower() in company_lower for ns in settings.H1B_NO_SPONSOR):
        company_score = 0.2
    score += company_score * 10

    # --- 5. Recency (10%) ---
    if posted_days_ago <= 1:
        recency_score = 1.0
    elif posted_days_ago <= 3:
        recency_score = 0.8
    elif posted_days_ago <= 7:
        recency_score = 0.6
    elif posted_days_ago <= 14:
        recency_score = 0.3
    else:
        recency_score = 0.1
    score += recency_score * 10

    # --- 6. H1B Sponsor History (15%) ---
    h1b_score = 0.3  # Default: unknown
    if any(c.lower() in company_lower for c in settings.H1B_TIER1):
        h1b_score = 1.0
    elif any(c.lower() in company_lower for c in settings.H1B_TIER2):
        h1b_score = 0.7
    elif any(c.lower() in company_lower for c in settings.H1B_NO_SPONSOR):
        h1b_score = 0.0
    score += h1b_score * 15

    # --- 7. CPT/OPT Friendly (10%) ---
    cpt_score = 0.5  # Default: unknown
    if visa_info == "cpt_opt_ok":
        cpt_score = 1.0
    elif visa_info == "no_sponsorship":
        cpt_score = 0.0  # Explicitly says no sponsorship
    elif "sponsorship" in full_text and "no" not in full_text:
        cpt_score = 0.8
    score += cpt_score * 10

    return max(0, min(100, round(score)))
