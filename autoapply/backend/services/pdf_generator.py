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
        # Clean more aggressively for Helvetica
        replacements = {
            "\u2018": "'", "\u2019": "'",
            "\u201c": '"', "\u201d": '"',
            "\u2013": "-", "\u2014": "-",
            "\u2022": "*", 
            "\u2026": "...",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Final safety check: encode as latin-1 to drop anything else
        return text.encode('latin-1', 'replace').decode('latin-1')

    def _create_base_pdf(self):
        pdf = ResumePDF()
        # Fallback to standard Helvetica (Core font) for maximum reliability
        return pdf, "helvetica"

    def generate_resume(self, data: dict, output_filename: str) -> str:
        """
        Generate a strictly ONE-PAGE PDF resume from data with premium formatting.
        """
        from fpdf import FPDF
        pdf = FPDF(unit='mm', format='A4')
        
        margin = 12.7 
        pdf.set_left_margin(margin)
        pdf.set_right_margin(margin)
        pdf.set_top_margin(margin)
        pdf.add_page()
        cw = 210 - margin * 2

        def safe_set_font(style='', size=10):
            pdf.set_font("helvetica", style, size)
        
        # 1. Header - Contact Info (Compact)
        safe_set_font('B', 18)
        pdf.cell(cw, 10, self._clean_text(str(data.get('name', 'User'))), ln=True, align='C')
        
        safe_set_font('', 9)
        personal = {
            "email": data.get('email', ''),
            "phone": data.get('phone', ''),
            "location": data.get('location', ''),
            "linkedin": data.get('linkedin', ''),
            "portfolio": data.get('portfolio', '')
        }
        
        contact_line = []
        if personal["email"]: contact_line.append(personal["email"])
        if personal["phone"]: contact_line.append(personal["phone"])
        if personal["location"]: contact_line.append(self._clean_text(personal["location"]))
        
        pdf.cell(cw, 4, " | ".join(contact_line), ln=True, align='C')
        
        links_line = []
        if personal["linkedin"]: links_line.append(f"LinkedIn: {personal['linkedin']}")
        if personal["portfolio"]: links_line.append(f"Portfolio: {personal['portfolio']}")
        
        if links_line:
            pdf.cell(cw, 4, self._clean_text(" | ".join(links_line)), ln=True, align='C')
        
        pdf.ln(2)

        # Section Utility
        def add_section_header(title):
            pdf.ln(1)
            safe_set_font('B', 11) 
            pdf.set_text_color(26, 54, 93) # Dark blue for sections
            pdf.cell(cw, 6, title, ln=True)
            pdf.line(margin, pdf.get_y(), 210-margin, pdf.get_y())
            pdf.ln(1)
            pdf.set_text_color(0, 0, 0) # Reset to black

        # 2. Professional Summary
        if data.get('summary'):
            add_section_header("PROFESSIONAL SUMMARY")
            safe_set_font('', 9.5)
            pdf.multi_cell(cw, 4, self._clean_text(data['summary']))
            pdf.ln(1)

        # 3. Education
        if data.get('education'):
            add_section_header("EDUCATION")
            for edu in data.get('education', []):
                safe_set_font('B', 10)
                pdf.cell(140, 5, self._clean_text(edu.get('institution', edu.get('school', ''))), ln=False)
                safe_set_font('I', 9)
                pdf.cell(cw - 140, 5, self._clean_text(edu.get('graduation', edu.get('dates', ''))), ln=True, align='R')
                
                safe_set_font('', 9.5)
                degree = edu.get('degree', '')
                field = edu.get('field', '')
                degree_line = f"{degree}"
                if field: degree_line += f" in {field}"
                if edu.get('gpa'): degree_line += f" | GPA: {edu.get('gpa')}"
                pdf.cell(cw, 4, self._clean_text(degree_line), ln=True)
                
                if edu.get('relevant_courses'):
                    safe_set_font('I', 8.5)
                    courses = ', '.join(edu.get('relevant_courses', []))
                    pdf.multi_cell(cw, 4, f"Relevant Coursework: {self._clean_text(courses)}")
                pdf.ln(0.5)

        # 4. Work Experience
        if data.get('experience'):
            add_section_header("WORK EXPERIENCE")
            for job in data.get('experience', []):
                safe_set_font('B', 10)
                pdf.cell(140, 5, self._clean_text(job.get('company', '')), ln=False)
                safe_set_font('I', 9)
                pdf.cell(cw - 140, 5, self._clean_text(job.get('dates', '')), ln=True, align='R')
                
                safe_set_font('B', 9.5)
                job_title = job.get('title', '')
                location = job.get('location', '')
                pdf.cell(cw, 4, f"{self._clean_text(job_title)} | {self._clean_text(location)}", ln=True)
                
                safe_set_font('', 9.5)
                for bullet in job.get('bullets', []):
                    pdf.set_x(margin + 2)
                    pdf.cell(3, 4, "-", ln=False)
                    pdf.multi_cell(cw - 5, 4, self._clean_text(bullet))
                pdf.ln(1)
            
        # 5. Skills
        if data.get('skills'):
            add_section_header("SKILLS & INTERESTS")
            skills_data = data.get('skills', [])
            if isinstance(skills_data, dict):
                for cat, items in skills_data.items():
                    if items:
                        safe_set_font('B', 9.5)
                        cat_label = f"{cat.capitalize()}: "
                        cat_w = pdf.get_string_width(cat_label) + 2
                        pdf.cell(cat_w, 4, cat_label, ln=False)
                        safe_set_font('', 9.5)
                        pdf.multi_cell(cw - cat_w, 4, self._clean_text(", ".join(items)))
            elif isinstance(skills_data, list):
                safe_set_font('', 9.5)
                pdf.multi_cell(cw, 4, self._clean_text(", ".join([str(s) for s in skills_data])))

        # 6. Certifications
        if data.get('certifications'):
            add_section_header("CERTIFICATIONS")
            safe_set_font('', 9.5)
            for cert in data.get('certifications', []):
                name = cert.get('name', '')
                issuer = cert.get('issuer', '')
                line = f"{name}"
                if issuer: line += f", {issuer}"
                pdf.cell(cw, 4, f"• {self._clean_text(line)}", ln=True)

        output_path = OUTPUT_DIR / output_filename
        pdf.output(str(output_path))
        return str(output_path)
            
        output_path = OUTPUT_DIR / output_filename
        pdf.output(str(output_path))
        return str(output_path)

pdf_generator_service = PDFGeneratorService()
