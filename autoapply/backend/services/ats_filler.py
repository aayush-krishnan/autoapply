import asyncio
from playwright.async_api import async_playwright
import logging
import re
import os
from services.ai_form_filler import ai_filler
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ATS Platform definitions
PLATFORMS = {
    "GREENHOUSE": "boards.greenhouse.io",
    "LEVER": "jobs.lever.co",
    "WORKDAY": "myworkdayjobs.com"
}

class SafeProfileData(BaseModel):
    """Pydantic model to strictly control what PII is passed to the browser subprocess."""
    name: str
    email: str
    phone: str
    linkedin: str | None = None
    website: str | None = None
    github: str | None = None
    summary: str | None = None
    experience: list[dict] = []
    education: list[dict] = []
    skills: list[str] = []
    visa_status: str = "Requires sponsorship (F-1 student seeking CPT/OPT/H1B)"

def detect_ats(url: str) -> str:
    """Detect the ATS platform from the source URL."""
    url_lower = url.lower()
    for platform, domain in PLATFORMS.items():
        if domain in url_lower:
            return platform
    return "UNKNOWN"

async def fill_greenhouse_form(page, profile_data, resume_path):
    """
    Automates filling out a standard Greenhouse application form.
    Uses generic CSS selectors common to Greenhouse forms.
    """
    logging.info("Starting Greenhouse form fill...")
    
    # Wait for the main form array to load
    await page.wait_for_selector('form#application_form', timeout=10000)

    personal = profile_data.get("personal", {})
    
    try:
        # 1. Basic Info
        if personal.get("name"):
            # Greenhouse often splits First and Last
            names = personal["name"].split(" ", 1)
            first_name = names[0]
            last_name = names[1] if len(names) > 1 else ""
            
            first_name_input = await page.query_selector("input[id='first_name']")
            if first_name_input: await first_name_input.fill(first_name)
                
            last_name_input = await page.query_selector("input[id='last_name']")
            if last_name_input: await last_name_input.fill(last_name)
            
        if personal.get("email"):
            email_input = await page.query_selector("input[id='email']")
            if email_input: await email_input.fill(personal["email"])
            
        if personal.get("phone"):
            phone_input = await page.query_selector("input[id='phone']")
            if phone_input: await phone_input.fill(personal["phone"])

        # 2. Upload Resume PDF
        resume_input = await page.query_selector("input[type='file'][data-source='attach'], input[id='resume_upload']")
        if resume_input and os.path.exists(resume_path):
            await resume_input.set_input_files(resume_path)
            logging.info(f"Uploaded resume: {resume_path}")
            # Wait for Greenhouse to process the upload (spinner usually disappears)
            await page.wait_for_selector(".upload-success-icon", timeout=10000, state="visible")

        # 2.1 Cover Letter (if available as a field, optional)
        cl_input = await page.query_selector("textarea[id='cover_letter_text'], input[id='cover_letter_upload']")
        if cl_input:
            # For now, we skip cover letters or just put a placeholder if it's text
            # Future expansion: Generate tailored CL with Gemini
            if await cl_input.get_attribute("type") == "file":
                 logging.info("Cover letter file field found (skipping for now)")
            else:
                 await cl_input.fill("Please see my resume for my background and interest in this role.")

        # 3. LinkedIn and Portfolio
        labels = await page.query_selector_all("label")
        for label in labels:
            text = (await label.inner_text()).lower()
            if "linkedin" in text:
                input_field = await label.query_selector("input") or await page.query_selector(f"input[id='{await label.get_attribute('for')}']")
                if input_field: await input_field.fill(personal.get("linkedin", ""))
            elif "website" in text or "portfolio" in text or "github" in text:
                input_field = await label.query_selector("input") or await page.query_selector(f"input[id='{await label.get_attribute('for')}']")
                if input_field:
                    val = personal.get("github") if "github" in text else personal.get("website", "")
                    await input_field.fill(val)

        # 4. Visa Sponsorship (Improved detection)
        for label in labels:
            text = (await label.inner_text()).lower()
            if re.search(r"visa|sponsorship|authorized to work", text):
                dropdown = await label.query_selector("select")
                if dropdown:
                    options = await dropdown.query_selector_all("option")
                    for opt in options:
                        opt_text = (await opt.inner_text()).lower()
                        # If the student is F-1, usually "Yes" to authorized and "Yes" to will require sponsorship
                        if "authorized" in text:
                            if "yes" in opt_text:
                                await dropdown.select_option(label=await opt.inner_text())
                                break
                        elif "require" in text or "sponsorship" in text:
                            if "yes" in opt_text or "require" in opt_text:
                                await dropdown.select_option(label=await opt.inner_text())
                                break
                            
        # 5. Handle remaining text inputs with AI
        inputs = await page.query_selector_all("input[type='text'], textarea")
        for inp in inputs:
            current_val = await inp.input_value()
            if not current_val:
                label_text = ""
                id_attr = await inp.get_attribute("id")
                if id_attr:
                    label = await page.query_selector(f"label[for='{id_attr}']")
                    if label: label_text = await label.inner_text()
                
                if not label_text:
                    label_text = await page.evaluate("(el) => el.closest('div').innerText", inp)

                if label_text and len(label_text.split()) < 20: # Avoid huge text blocks as questions
                    answer = await ai_filler.answer_question(label_text, profile_data)
                    if answer:
                        await inp.fill(answer)

        logging.info("Greenhouse initial form fill completed.")
        
    except Exception as e:
        logging.error(f"Error during Greenhouse form fill: {e}")
        raise e

async def fill_lever_form(page, profile_data, resume_path):
    """
    Automates filling out a standard Lever application form.
    """
    logging.info("Starting Lever form fill...")
    personal = profile_data.get("personal", {})

    # Basic Info
    name_input = await page.query_selector("input[name='name']")
    if name_input: await name_input.fill(personal.get("name", ""))

    email_input = await page.query_selector("input[name='email']")
    if email_input: await email_input.fill(personal.get("email", ""))

    phone_input = await page.query_selector("input[name='phone']")
    if phone_input: await phone_input.fill(personal.get("phone", ""))

    org_input = await page.query_selector("input[name='org']")
    if org_input: 
        # Find current company from experience
        exp = profile_data.get("experience", [])
        if exp: await org_input.fill(exp[0].get("company", ""))

    # Resume Upload
    resume_input = await page.query_selector("input[type='file'][name='resume']")
    if resume_input and os.path.exists(resume_path):
        await resume_input.set_input_files(resume_path)
        # Lever typically shows a success checkmark or text after upload
        await page.wait_for_selector(".file-upload-success", timeout=10000, state="attached")

    # AI Fallback for custom questions
    custom_inputs = await page.query_selector_all("input[type='text'], textarea, input[type='url']")
    for inp in custom_inputs:
        val = await inp.input_value()
        if not val:
            # Find label
            label_text = await page.evaluate("(el) => el.closest('.application-question').innerText", inp)
            if label_text:
                answer = await ai_filler.answer_question(label_text, profile_data)
                if answer:
                    await inp.fill(answer)

    logging.info("Lever form fill completed.")

async def fill_workday_form(page, profile_data, resume_path):
    """
    Automates Workday - focuses on the 'Quick Apply' or first page experience.
    """
    logging.info("Starting Workday form fill...")
    # Workday is notoriously difficult; we'll target common data-automation-id attributes
    
    # Check if we need to click "Apply" first
    apply_btn = await page.query_selector("[data-automation-id='applyButton']")
    if apply_btn: await apply_btn.click()
    
    # Look for "Autofill with Resume" if available
    autofill_btn = await page.query_selector("[data-automation-id='autofillWithResume']")
    if autofill_btn:
        await autofill_btn.click()
        # Upload
        upload_input = await page.query_selector("input[type='file']")
        if upload_input: 
            await upload_input.set_input_files(resume_path)
            # Wait for Workday to acknowledge the upload
            await page.wait_for_load_state("networkidle")
    else:
        # Manual fill if autofill isn't an option
        first_name = await page.query_selector("[data-automation-id='legalNameSection_firstName']")
        if first_name: await first_name.fill(profile_data["personal"]["name"].split(" ")[0])
        
        last_name = await page.query_selector("[data-automation-id='legalNameSection_lastName']")
        if last_name: await last_name.fill(profile_data["personal"]["name"].split(" ")[-1])

        email = await page.query_selector("[data-automation-id='email']")
        if email: await email.fill(profile_data["personal"]["email"])

    # Handle "Next" button in multi-step Workday flow
    next_btn = await page.query_selector("[data-automation-id='bottomBarNextButton']")
    if next_btn:
        await next_btn.click()
        await page.wait_for_load_state("networkidle")
    
    # AI Fallback for screening questions on subsequent pages
    custom_inputs = await page.query_selector_all("input[type='text'], textarea")
    for inp in custom_inputs:
        val = await inp.input_value()
        if not val:
            label_text = await page.evaluate("(el) => el.closest('[data-automation-id=\"formField\"]').innerText", inp)
            if label_text:
                answer = await ai_filler.answer_question(label_text, profile_data)
                if answer:
                    await inp.fill(answer)

    logging.info("Workday is a multi-step process; initial fill sent.")

async def run_auto_apply(job_url: str, profile_data: dict, resume_path: str):
    """
    Main entry point for auto apply. Launches playwright, navigates, and delegates to ATS specific scripts.
    """
    ats_type = detect_ats(job_url)
    if ats_type == "UNKNOWN":
        raise ValueError("Unsupported ATS platform.")

    async with async_playwright() as p:
        # Use env var for headless mode, default to true for production-safety
        headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
        browser = await p.chromium.launch(headless=headless) 
        context = await browser.new_context()
        page = await context.new_page()

        logging.info(f"Navigating to {job_url}")
        await page.goto(job_url, wait_until="networkidle")

        try:
            if ats_type == "GREENHOUSE":
                await fill_greenhouse_form(page, profile_data, resume_path)
            elif ats_type == "LEVER":
                await fill_lever_form(page, profile_data, resume_path)
            elif ats_type == "WORKDAY":
                await fill_workday_form(page, profile_data, resume_path)
                
            # Take screenshot before doing anything else
            screenshot_path = "autoapply_final_review.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            logging.info(f"Form filled. Screenshot saved to {screenshot_path}.")
            
            # NOTE: We do NOT click submit here automatically for safety.
            # We keep the browser open for local review, or close it if headless
            await page.wait_for_timeout(5000) 
            
        except Exception as e:
            logging.error(f"Failed to fill form: {e}")
            await page.screenshot(path="autoapply_error.png", full_page=True)
            
        finally:
            await browser.close()
            
        return screenshot_path
