"""
Resume Parser Module

This module handles the extraction of text from resume files (PDF and DOCX).
"""
import os
import fitz  # PyMuPDF
import docx2txt
import pdfplumber
from pathlib import Path


class ResumeParser:
    """Parser for extracting text from resume files."""

    def __init__(self):
        """Initialize the ResumeParser."""
        pass

    def parse(self, file_path):
        """
        Parse a resume file and extract its text content.

        Args:
            file_path (str): Path to the resume file (PDF or DOCX)

        Returns:
            dict: Parsed resume data with sections
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            text = self._parse_pdf(file_path)
        elif file_ext == '.docx':
            text = self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Process the extracted text to identify sections
        sections = self._extract_sections(text)
        
        return {
            'raw_text': text,
            'sections': sections
        }

    def _parse_pdf(self, file_path):
        """
        Extract text from a PDF file using PyMuPDF and pdfplumber as backup.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text
        """
        # Try PyMuPDF first (faster)
        try:
            text = ""
            with fitz.open(file_path) as pdf:
                for page in pdf:
                    text += page.get_text()
            
            # If text extraction was successful and not empty
            if text.strip():
                return text
        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}")
        
        # Fallback to pdfplumber if PyMuPDF fails or returns empty text
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        except Exception as e:
            print(f"pdfplumber extraction failed: {e}")
            raise ValueError(f"Failed to extract text from PDF: {e}")

    def _parse_docx(self, file_path):
        """
        Extract text from a DOCX file.
        
        Args:
            file_path (str): Path to the DOCX file
            
        Returns:
            str: Extracted text
        """
        try:
            text = docx2txt.process(file_path)
            return text
        except Exception as e:
            print(f"DOCX extraction failed: {e}")
            raise ValueError(f"Failed to extract text from DOCX: {e}")

    def _extract_sections(self, text):
        """
        Extract common resume sections from text.
        
        Args:
            text (str): Raw text extracted from resume
            
        Returns:
            dict: Dictionary with section names as keys and content as values
        """
        # Common section headers in resumes
        section_headers = [
            "EDUCATION", "EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT",
            "SKILLS", "TECHNICAL SKILLS", "PROJECTS", "PROJECT EXPERIENCE",
            "CERTIFICATIONS", "ACHIEVEMENTS", "PUBLICATIONS", "LANGUAGES",
            "INTERESTS", "SUMMARY", "OBJECTIVE", "PROFILE"
        ]
        
        # Initialize sections dictionary
        sections = {}
        
        # Simple section extraction based on common headers
        # This is a basic implementation and can be improved with NLP techniques
        lines = text.split('\n')
        current_section = "UNKNOWN"
        sections[current_section] = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            is_header = False
            for header in section_headers:
                if header in line.upper() and len(line) < 50:  # Avoid matching text within paragraphs
                    current_section = header
                    sections[current_section] = []
                    is_header = True
                    break
            
            if not is_header:
                sections[current_section].append(line)
        
        # Convert lists to strings
        for section, content in sections.items():
            sections[section] = '\n'.join(content)
        
        return sections


if __name__ == "__main__":
    # Example usage
    parser = ResumeParser()
    sample_resume = "../data/resumes/sample_resume.pdf"  # Update with actual path
    
    if os.path.exists(sample_resume):
        result = parser.parse(sample_resume)
        print(f"Extracted {len(result['raw_text'])} characters")
        print("Sections found:")
        for section in result['sections']:
            print(f"- {section}")
    else:
        print(f"Sample resume not found at {sample_resume}")