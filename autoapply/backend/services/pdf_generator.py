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
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
    def _create_base_pdf(self):
        pdf = FPDF()
        # Try to add Unicode-friendly font if available on macOS
        unicode_font_path = "/Library/Fonts/Arial Unicode.ttf"
        if os.path.exists(unicode_font_path):
            try:
                pdf.add_font("ArialUnicode", "", unicode_font_path)
                pdf.set_font("ArialUnicode", size=10)
                return pdf, "ArialUnicode"
            except Exception as e:
                logger.warning(f"Failed to load Arial Unicode: {e}")
        
        # Fallback to standard Helvetica
        pdf.set_font("Helvetica", size=10)
        return pdf, "Helvetica"

    def generate_resume(self, data: dict, filename: str) -> Path:
        """Generates a high-fidelity, 1-page tailored resume PDF."""
        pdf, font_name = self._create_base_pdf()
        pdf.add_page()
            pdf.multi_cell(0, 4, self._clean_text(", ".join([str(s) for s in skills_data])))
            
        output_path = OUTPUT_DIR / output_filename
        pdf.output(str(output_path))
        return str(output_path)

pdf_generator_service = PDFGeneratorService()
