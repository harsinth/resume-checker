"""
Job Description Parser Module

This module handles the extraction and structuring of job description data.
"""
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter


class JobDescriptionParser:
    """Parser for extracting structured data from job descriptions."""

    def __init__(self):
        """Initialize the JobDescriptionParser."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def parse(self, text):
        """
        Parse a job description and extract structured information.

        Args:
            text (str): Raw job description text

        Returns:
            dict: Structured job description data
        """
        # Extract key components from the job description
        sections = self._extract_sections(text)
        
        # Extract skills from the job description
        skills = self._extract_skills(text)
        
        # Extract role information
        role_info = self._extract_role_info(text)
        
        # Create structured job description
        structured_jd = {
            'raw_text': text,
            'sections': sections,
            'skills': skills,
            'role_info': role_info,
            'chunks': self.text_splitter.split_text(text)
        }
        
        return structured_jd

    def _extract_sections(self, text):
        """
        Extract common job description sections.
        
        Args:
            text (str): Raw job description text
            
        Returns:
            dict: Dictionary with section names as keys and content as values
        """
        # Common section headers in job descriptions
        section_headers = [
            "RESPONSIBILITIES", "REQUIREMENTS", "QUALIFICATIONS", 
            "SKILLS", "EXPERIENCE", "EDUCATION", "ABOUT THE ROLE",
            "ABOUT THE COMPANY", "BENEFITS", "WHAT YOU'LL DO",
            "WHAT YOU'LL NEED", "WHO YOU ARE"
        ]
        
        # Initialize sections dictionary
        sections = {}
        
        # Simple section extraction based on common headers
        lines = text.split('\n')
        current_section = "DESCRIPTION"  # Default section
        sections[current_section] = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            is_header = False
            for header in section_headers:
                if header in line.upper() and len(line) < 100:  # Avoid matching text within paragraphs
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

    def _extract_skills(self, text):
        """
        Extract technical skills and requirements from job description.
        
        Args:
            text (str): Raw job description text
            
        Returns:
            dict: Dictionary with required and preferred skills
        """
        # Initialize skills dictionary
        skills = {
            'required': [],
            'preferred': []
        }
        
        # Look for required skills sections
        required_patterns = [
            r"required skills[:\s]*(.*?)(?=preferred skills|\Z)",
            r"requirements[:\s]*(.*?)(?=preferred|\Z)",
            r"qualifications[:\s]*(.*?)(?=preferred|\Z)",
            r"must have[:\s]*(.*?)(?=nice to have|\Z)",
            r"essential[:\s]*(.*?)(?=desirable|\Z)"
        ]
        
        # Look for preferred skills sections
        preferred_patterns = [
            r"preferred skills[:\s]*(.*?)(?=\Z)",
            r"nice to have[:\s]*(.*?)(?=\Z)",
            r"desirable[:\s]*(.*?)(?=\Z)",
            r"bonus[:\s]*(.*?)(?=\Z)"
        ]
        
        # Extract required skills
        for pattern in required_patterns:
            matches = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                skill_text = matches.group(1).strip()
                # Extract bullet points or list items
                skill_items = re.findall(r"[•\-\*]\s*(.*?)(?=\n[•\-\*]|\Z)", skill_text, re.DOTALL)
                if skill_items:
                    skills['required'].extend([item.strip() for item in skill_items])
                else:
                    # If no bullet points, split by sentences or newlines
                    skill_items = re.split(r'[.\n]', skill_text)
                    skills['required'].extend([item.strip() for item in skill_items if item.strip()])
        
        # Extract preferred skills
        for pattern in preferred_patterns:
            matches = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                skill_text = matches.group(1).strip()
                # Extract bullet points or list items
                skill_items = re.findall(r"[•\-\*]\s*(.*?)(?=\n[•\-\*]|\Z)", skill_text, re.DOTALL)
                if skill_items:
                    skills['preferred'].extend([item.strip() for item in skill_items])
                else:
                    # If no bullet points, split by sentences or newlines
                    skill_items = re.split(r'[.\n]', skill_text)
                    skills['preferred'].extend([item.strip() for item in skill_items if item.strip()])
        
        # Remove duplicates
        skills['required'] = list(set(skills['required']))
        skills['preferred'] = list(set(skills['preferred']))
        
        return skills

    def _extract_role_info(self, text):
        """
        Extract basic role information like title, experience level, etc.
        
        Args:
            text (str): Raw job description text
            
        Returns:
            dict: Dictionary with role information
        """
        role_info = {
            'title': None,
            'experience_level': None,
            'education': None,
            'location': None
        }
        
        # Extract job title
        title_patterns = [
            r"job title[:\s]*([^\n]*)",
            r"position[:\s]*([^\n]*)",
            r"role[:\s]*([^\n]*)"
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                role_info['title'] = match.group(1).strip()
                break
        
        # Extract experience level
        exp_patterns = [
            r"(\d+)[+\s]*years? of experience",
            r"experience[:\s]*(\d+)[+\s]*years",
            r"(\d+)[+\s]*years? exp"
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                role_info['experience_level'] = match.group(1).strip()
                break
        
        # Extract education requirements
        edu_patterns = [
            r"(bachelor'?s|master'?s|phd|doctorate|degree)[^\n]*",
            r"education[:\s]*([^\n]*degree[^\n]*)"
        ]
        
        for pattern in edu_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                role_info['education'] = match.group(0).strip()
                break
        
        # Extract location
        loc_patterns = [
            r"location[:\s]*([^\n]*)",
            r"based in[:\s]*([^\n]*)",
            r"position is in[:\s]*([^\n]*)"
        ]
        
        for pattern in loc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                role_info['location'] = match.group(1).strip()
                break
        
        return role_info


if __name__ == "__main__":
    # Example usage
    parser = JobDescriptionParser()
    sample_jd = """
    Job Title: Senior Python Developer
    
    About the Role:
    We are looking for an experienced Python developer to join our team.
    
    Requirements:
    • 5+ years of experience in Python development
    • Strong knowledge of web frameworks like Django or Flask
    • Experience with database design and optimization
    • Familiarity with front-end technologies (HTML, CSS, JavaScript)
    
    Preferred Skills:
    • Experience with cloud platforms (AWS, GCP)
    • Knowledge of containerization (Docker, Kubernetes)
    • Machine learning experience is a plus
    
    Education:
    Bachelor's degree in Computer Science or related field
    
    Location: Hybrid (New York office with remote options)
    """
    
    result = parser.parse(sample_jd)
    print("Role Info:", result['role_info'])
    print("\nRequired Skills:", result['skills']['required'])
    print("\nPreferred Skills:", result['skills']['preferred'])