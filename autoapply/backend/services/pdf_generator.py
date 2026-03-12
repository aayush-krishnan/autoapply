"""Service for generating tailored PDF resumes locally using fpdf2 - one page, education first."""

import os
from fpdf import FPDF
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "resumes" / "tailored"

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
        """Replace non-ASCII characters that FPDF Helvetica can't handle."""
        if not text:
            return ""
        replacements = {
            "\u2018": "'", "\u2019": "'",
            "\u201c": '"', "\u201d": '"',
            "\u2013": "-", "\u2014": "-",
            "\u2022": "*", 
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.encode("latin-1", "replace").decode("latin-1")

    def generate_resume(self, data: dict, output_filename: str) -> str:
        """
        Generate a strictly ONE-PAGE PDF resume from data.
        """
        # Set tighter margins (12.7mm = 0.5 inch)
        margin = 12.7
        pdf = ResumePDF()
        pdf.set_margins(margin, margin, margin)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Header - Contact Info (Compact)
        pdf.set_font('helvetica', 'B', 18) 
        pdf.cell(0, 10, self._clean_text(data.get('name', 'User')), ln=True, align='C')
        
        pdf.set_font('helvetica', '', 9)
        contact = f"{data.get('email')} | {data.get('phone')} | {self._clean_text(data.get('location'))}"
        pdf.cell(0, 4, contact, ln=True, align='C')
        
        links = f"LinkedIn: {data.get('linkedin')} | Portfolio: {data.get('portfolio')}"
        pdf.cell(0, 4, links, ln=True, align='C')
        pdf.ln(2) 
        
        # Section Utility
        def add_section_header(title):
            pdf.ln(1)
            pdf.set_font('helvetica', 'B', 11) 
            pdf.set_text_color(26, 54, 93) 
            pdf.cell(0, 6, title, ln=True)
            pdf.line(margin, pdf.get_y(), 210-margin, pdf.get_y())
            pdf.ln(1)

        # 1. Section: Education (Moved to top as requested)
        add_section_header("EDUCATION")
        pdf.set_text_color(0, 0, 0)
        for edu in data.get('education', []):
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(140, 5, self._clean_text(edu.get('institution', '')), ln=False)
            pdf.set_font('helvetica', 'I', 9)
            pdf.cell(0, 5, self._clean_text(edu.get('graduation', '')), ln=True, align='R')
            
            pdf.set_font('helvetica', '', 9.5)
            pdf.cell(0, 4, f"{self._clean_text(edu.get('degree', ''))} | GPA: {edu.get('gpa', '')}", ln=True)
            if edu.get('relevant_courses'):
                pdf.set_font('helvetica', 'I', 8.5)
                courses = ', '.join(edu.get('relevant_courses', []))
                pdf.multi_cell(0, 4, f"Relevant Coursework: {self._clean_text(courses)}")
            pdf.ln(0.5)

        # 2. Section: Experience
        add_section_header("WORK EXPERIENCE")
        pdf.set_text_color(0, 0, 0)
        for job in data.get('experience', []):
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(140, 5, self._clean_text(job.get('company', '')), ln=False)
            pdf.set_font('helvetica', 'I', 9)
            pdf.cell(0, 5, self._clean_text(job.get('dates', '')), ln=True, align='R')
            
            pdf.set_font('helvetica', 'B', 9.5)
            pdf.cell(0, 4, f"{self._clean_text(job.get('title'))} | {self._clean_text(job.get('location', ''))}", ln=True)
            
            pdf.set_font('helvetica', '', 9.5)
            for bullet in job.get('bullets', []):
                start_x = pdf.get_x()
                pdf.cell(4, 4, "-", ln=False)
                avail_w = 210 - (margin * 2) - 4
                pdf.multi_cell(avail_w, 4, self._clean_text(bullet))
                pdf.set_x(start_x)
            pdf.ln(1)
            
        # 3. Section: Skills (Compact Flow)
        add_section_header("SKILLS & INTERESTS")
        pdf.set_text_color(0, 0, 0)
        
        skills_data = data.get('skills', [])
        if isinstance(skills_data, dict):
            for cat, items in skills_data.items():
                if items:
                    pdf.set_font('helvetica', 'B', 9)
                    pdf.cell(30, 4, f"{cat.capitalize()}:", ln=False)
                    pdf.set_font('helvetica', '', 9)
                    pdf.multi_cell(0, 4, self._clean_text(", ".join(items)))
        else:
            pdf.set_font('helvetica', '', 9)
            pdf.multi_cell(0, 4, self._clean_text(", ".join([str(s) for s in skills_data])))
            
        output_path = OUTPUT_DIR / output_filename
        pdf.output(str(output_path))
        return str(output_path)

pdf_generator_service = PDFGeneratorService()
