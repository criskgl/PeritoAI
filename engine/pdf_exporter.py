"""PDF Export functionality for insurance reports."""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from fpdf import FPDF


class ReportPDFExporter:
    """Handles PDF generation for insurance adjuster reports."""

    def __init__(self):
        """Initialize PDF Exporter."""
        self.pdf = None

    def _setup_pdf(self):
        """Initialize PDF with proper settings."""
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        self.pdf.set_font("Helvetica", size=10)
        return self.pdf

    def _add_header(self, title: str = "INFORME PERICIAL"):
        """Add header to PDF."""
        self.pdf.set_font("Helvetica", "B", 16)
        self.pdf.cell(0, 10, title, ln=1, align="C")
        self.pdf.ln(5)

    def _add_section(self, title: str, content: str):
        """
        Add a section to the PDF.

        Args:
            title: Section title
            content: Section content
        """
        # Section title
        self.pdf.set_font("Helvetica", "B", 12)
        self.pdf.cell(0, 8, title, ln=1)
        self.pdf.ln(2)

        # Section content
        self.pdf.set_font("Helvetica", size=10)

        # Handle special characters and encoding
        try:
            # Replace common special characters that might cause issues
            content = content.encode("latin-1", "replace").decode("latin-1")

            # Split content into paragraphs
            paragraphs = content.split("\n\n")
            for para in paragraphs:
                if para.strip():
                    # Split long paragraphs into lines that fit page width
                    lines = para.split("\n")
                    for line in lines:
                        if line.strip():
                            # Handle lines that are too long
                            self.pdf.multi_cell(0, 5, line.strip(), align="L")
                            self.pdf.ln(1)
                    self.pdf.ln(2)
        except Exception as e:
            # Fallback: try with UTF-8 encoding
            try:
                content = content.encode("utf-8", "replace").decode("utf-8")
                self.pdf.multi_cell(0, 5, content, align="L")
            except Exception:
                # Last resort: basic text
                self.pdf.cell(0, 5, "Error encoding text. Please check special characters.", ln=1)

        self.pdf.ln(3)

    def _parse_report_sections(self, report_text: str) -> Dict[str, str]:
        """
        Parse report text into sections.

        Args:
            report_text: Full report text

        Returns:
            Dictionary with section titles and content
        """
        sections = {}
        current_section = "INTRODUCCIÓN"
        current_content = []

        # Common section headers in Spanish
        section_markers = [
            "IDENTIFICACIÓN",
            "ANTECEDENTES",
            "ANÁLISIS DE CAUSALIDAD",
            "ANÁLISIS DE COBERTURA",
            "TASACIÓN Y PROPUESTA",
            "CONCLUSIONES",
        ]

        lines = report_text.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Check if line is a section header
            is_section_header = False
            for marker in section_markers:
                if marker in line.upper() and len(line) < 100:
                    # Save previous section
                    if current_content:
                        sections[current_section] = "\n".join(current_content)

                    # Start new section
                    current_section = marker
                    current_content = []
                    is_section_header = True
                    i += 1
                    break

            if not is_section_header:
                current_content.append(line)
                i += 1

        # Save last section
        if current_content:
            sections[current_section] = "\n".join(current_content)

        # If no sections found, treat entire text as content
        if not sections:
            sections["INFORME COMPLETO"] = report_text

        return sections

    def export_to_pdf(
        self,
        report_text: str,
        output_path: Optional[str] = None,
        policy_id: Optional[str] = None,
        claim_id: Optional[str] = None,
    ) -> str:
        """
        Export report to PDF file.

        Args:
            report_text: Full report text in Spanish
            output_path: Output file path. If None, generates filename automatically
            policy_id: Policy ID for filename
            claim_id: Claim ID for filename

        Returns:
            Path to generated PDF file
        """
        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"informe_pericial_{policy_id or 'unknown'}_{claim_id or timestamp}.pdf"
            output_path = f"data/reports/{filename}"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Setup PDF
        self._setup_pdf()

        # Add header
        self._add_header("INFORME PERICIAL")

        # Add metadata
        self.pdf.set_font("Helvetica", size=9)
        if policy_id:
            self.pdf.cell(0, 5, f"Póliza: {policy_id}", ln=1)
        if claim_id:
            self.pdf.cell(0, 5, f"Número de Siniestro: {claim_id}", ln=1)
        self.pdf.cell(0, 5, f"Fecha de Generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=1)
        self.pdf.ln(5)

        # Parse and add sections
        sections = self._parse_report_sections(report_text)

        for section_title, section_content in sections.items():
            self._add_section(section_title, section_content)

        # Add footer on last page
        self.pdf.set_y(-15)
        self.pdf.set_font("Helvetica", "I", 8)
        self.pdf.cell(0, 10, f"Generado por PeritoAI - {datetime.now().strftime('%d/%m/%Y')}", align="C")

        # Save PDF
        try:
            self.pdf.output(str(output_path))
            return str(output_path)
        except Exception as e:
            raise Exception(f"Error saving PDF: {str(e)}")

    def export_from_dict(
        self,
        report_dict: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> str:
        """
        Export report from dictionary to PDF.

        Args:
            report_dict: Dictionary containing report data
            output_path: Output file path

        Returns:
            Path to generated PDF file
        """
        report_text = report_dict.get("report_text", "")
        policy_id = report_dict.get("policy_id")
        claim_id = report_dict.get("claim_id")

        return self.export_to_pdf(
            report_text=report_text,
            output_path=output_path,
            policy_id=policy_id,
            claim_id=claim_id,
        )
