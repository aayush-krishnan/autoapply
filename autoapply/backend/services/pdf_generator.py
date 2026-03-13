"""
Service for generating tailored PDF resumes locally using fpdf2.
Optimized for ONE PAGE, EDUCATION FIRST, and UNICODE SUPPORT.
"""

import os
import logging
from fpdf import FPDF
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "resumes" / "tailored"
FONT_DIR = BASE_DIR / "assets" / "fonts"

logger = logging.getLogger(__name__)

class ResumePDF(FPDF):
    def header(self):
        pass

    def footer(self):
        # No footer for one-page resume to save space
        pass

class PDFGeneratorService:
    """Generates tailored resumes as PDFs using fpdf2 - optimized for ONE PAGE, EDUCATION FIRST."""

    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def _clean_text(self, text: str) -> str:
        """Replace non-ASCII characters that standard fonts can't handle."""
        if not text:
            return ""
        # Still do some cleaning even with Unicode font for safety
        replacements = {
            "\u2018": "'", "\u2019": "'",
            "\u201c": '"', "\u201d": '"',
            "\u2013": "-", "\u2014": "-",
            "\u2022": "*", 
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def _create_base_pdf(self):
        pdf = ResumePDF()
        # Look for bundled DejaVuSans (handles Unicode well)
        regular = FONT_DIR / "DejaVuSans.ttf"
        bold = FONT_DIR / "DejaVuSans-Bold.ttf"
        
        if regular.exists() and bold.exists():
            try:
                pdf.add_font("DejaVu", "", str(regular))
                pdf.add_font("DejaVu", "B", str(bold))
                return pdf, "DejaVu"
            except Exception as e:
                logger.warning(f"Failed to load DejaVu fonts: {e}")
                
        # Fallback to macOS-specific Arial Unicode if available
        unicode_font_path = "/Library/Fonts/Arial Unicode.ttf"
        if os.path.exists(unicode_font_path):
            try:
                pdf.add_font("ArialUnicode", "", unicode_font_path)
                return pdf, "ArialUnicode"
            except Exception as e:
                logger.warning(f"Failed to load Arial Unicode: {e}")
        
        # Final fallback to standard Helvetica
        return pdf, "helvetica"

    def generate_resume(self, data: dict, output_filename: str) -> str:
        """
        Generate a strictly ONE-PAGE PDF resume from data.
        """
        pdf, font_name = self._create_base_pdf()
        
        # Set tighter margins (12.7mm = 0.5 inch)
        margin = 12.7
        pdf.set_margins(margin, margin, margin)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=10)
        
        # Header - Contact Info (Compact)
        pdf.set_font(font_name, 'B', 16) 
        pdf.cell(0, 10, self._clean_text(data.get('name', 'User')), ln=True, align='C')
        
        pdf.set_font(font_name, '', 9)
        personal = data.get('personal', {})
        email = data.get('email') or personal.get('email', '')
        phone = data.get('phone') or personal.get('phone', '')
        location = data.get('location') or personal.get('location', '')
        
        contact = f"{email} | {phone} | {self._clean_text(location)}"
        pdf.cell(0, 4, contact, ln=True, align='C')
        
        linkedin = data.get('linkedin') or personal.get('linkedin', '')
        portfolio = data.get('portfolio') or personal.get('website', '')
        links = f"LinkedIn: {linkedin} | Portfolio: {portfolio}"
        pdf.cell(0, 4, links, ln=True, align='C')
        pdf.ln(2) 
        
        # Section Utility
        def add_section_header(title):
            pdf.ln(1)
            pdf.set_font(font_name, 'B', 11) 
            pdf.set_text_color(26, 54, 93) # Dark blue
            pdf.cell(0, 6, title, ln=True)
            pdf.line(margin, pdf.get_y(), 210-margin, pdf.get_y())
            pdf.ln(1)
            pdf.set_text_color(0, 0, 0) # Reset to black

        # 1. Section: Education
        add_section_header("EDUCATION")
        for edu in data.get('education', []):
            pdf.set_font(font_name, 'B', 10)
            school = edu.get('institution') or edu.get('school', '')
            pdf.cell(140, 5, self._clean_text(school), ln=False)
            pdf.set_font(font_name, 'I', 9)
            dates = edu.get('graduation') or edu.get('dates', '')
            pdf.cell(0, 5, self._clean_text(dates), ln=True, align='R')
            
            pdf.set_font(font_name, '', 9.5)
            degree = edu.get('degree', '')
            field = edu.get('field', '')
            degree_line = f"{degree}"
            if field: degree_line += f" in {field}"
            if edu.get('gpa'): degree_line += f" | GPA: {edu.get('gpa')}"
            pdf.cell(0, 4, self._clean_text(degree_line), ln=True)
            
            if edu.get('relevant_courses'):
                pdf.set_font(font_name, 'I', 8.5)
                courses = ', '.join(edu.get('relevant_courses', []))
                pdf.multi_cell(0, 4, f"Relevant Coursework: {self._clean_text(courses)}")
            pdf.ln(0.5)

        # 2. Section: Experience
        add_section_header("WORK EXPERIENCE")
        for job in data.get('experience', []):
            pdf.set_font(font_name, 'B', 10)
            pdf.cell(140, 5, self._clean_text(job.get('company', '')), ln=False)
            pdf.set_font(font_name, 'I', 9)
            pdf.cell(0, 5, self._clean_text(job.get('dates', '')), ln=True, align='R')
            
            pdf.set_font(font_name, 'B', 9.5)
            pdf.cell(0, 4, f"{self._clean_text(job.get('title'))} | {self._clean_text(job.get('location', ''))}", ln=True)
            
            pdf.set_font(font_name, '', 9.5)
            for bullet in job.get('bullets', []):
                start_y = pdf.get_y()
                pdf.set_x(margin)
                pdf.cell(4, 4, chr(149) if font_name == 'helvetica' else "•", ln=False)
                avail_w = 210 - (margin * 2) - 4
                pdf.multi_cell(avail_w, 4, self._clean_text(bullet))
            pdf.ln(1)
            
        # 3. Section: Skills (Compact)
        add_section_header("SKILLS & INTERESTS")
        skills_data = data.get('skills', [])
        if isinstance(skills_data, dict):
            for cat, items in skills_data.items():
                if items:
                    pdf.set_font(font_name, 'B', 9)
                    pdf.cell(30, 4, f"{cat.capitalize()}:", ln=False)
                    pdf.set_font(font_name, '', 9)
                    pdf.multi_cell(0, 4, self._clean_text(", ".join(items)))
        elif isinstance(skills_data, list):
            pdf.set_font(font_name, '', 9)
            pdf.multi_cell(0, 4, self._clean_text(", ".join([str(s) for s in skills_data])))
            
        output_path = OUTPUT_DIR / output_filename
        pdf.output(str(output_path))
        logger.info(f"✅ Local PDF generated at {output_path}")
        return str(output_path)

pdf_generator_service = PDFGeneratorService()
