"""
Hard Match Analyzer Module

This module provides functionality for analyzing hard matches between resumes and job descriptions.
"""
import re
import string
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class HardMatchAnalyzer:
    """
    Analyzer for hard matching between resume and job description.
    
    This class provides methods to analyze exact and fuzzy matches between
    resume and job description for skills, keywords, education, and experience.
    """
    
    def __init__(self):
        """Initialize the HardMatchAnalyzer."""
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def analyze(self, resume_data, jd_data):
        """
        Analyze hard matches between resume and job description.
        
        Args:
            resume_data (dict): Parsed resume data
            jd_data (dict): Parsed job description data
            
        Returns:
            dict: Hard match analysis results
        """
        # Analyze skill matches
        skill_match = self.analyze_skill_match(resume_data.get('skills', []), 
                                              jd_data.get('skills', []))
        
        # Analyze keyword matches
        keyword_match = self.analyze_keyword_match(resume_data.get('raw_text', ''), 
                                                 jd_data.get('raw_text', ''))
        
        # Analyze education matches
        education_match = self.analyze_education_match(resume_data.get('education', []), 
                                                     jd_data.get('education_requirements', []))
        
        # Analyze experience matches
        experience_match = self.analyze_experience_match(resume_data.get('experience', []), 
                                                       jd_data.get('experience_requirements', []))
        
        # Calculate overall hard match score
        overall_score = self.calculate_overall_hard_match_score(
            skill_match, keyword_match, education_match, experience_match
        )
        
        return {
            'skill_match': skill_match,
            'keyword_match': keyword_match,
            'education_match': education_match,
            'experience_match': experience_match,
            'overall_hard_match_score': overall_score
        }
    
    def analyze_skill_match(self, resume_skills, jd_skills):
        """
        Analyze skill matches between resume and job description.
        
        Args:
            resume_skills (list): Skills from resume
            jd_skills (list): Skills from job description
            
        Returns:
            dict: Skill match analysis results
        """
        if not jd_skills:
            return {
                'matched_skills': [],
                'missing_skills': [],
                'skill_match_score': 0,
                'overall_skill_match_score': 0
            }
        
        # Convert to lowercase for better matching
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        jd_skills_lower = [skill.lower() for skill in jd_skills]
        
        # Find exact matches
        exact_matches = []
        for jd_skill in jd_skills_lower:
            if jd_skill in resume_skills_lower:
                exact_matches.append(jd_skill)
        
        # Find fuzzy matches for skills not exactly matched
        fuzzy_matches = []
        missing_skills = []
        
        for jd_skill in jd_skills_lower:
            if jd_skill not in exact_matches:
                best_match = None
                best_ratio = 0
                
                for resume_skill in resume_skills_lower:
                    ratio = SequenceMatcher(None, jd_skill, resume_skill).ratio()
                    if ratio > 0.8 and ratio > best_ratio:  # 80% similarity threshold
                        best_match = resume_skill
                        best_ratio = ratio
                
                if best_match:
                    fuzzy_matches.append((jd_skill, best_match, best_ratio))
                else:
                    missing_skills.append(jd_skill)
        
        # Calculate scores
        if len(jd_skills) > 0:
            exact_match_score = (len(exact_matches) / len(jd_skills)) * 100
            fuzzy_match_score = (len(fuzzy_matches) / len(jd_skills)) * 100 * 0.8  # Fuzzy matches count less
            overall_score = (len(exact_matches) + len(fuzzy_matches) * 0.8) / len(jd_skills) * 100
        else:
            exact_match_score = 0
            fuzzy_match_score = 0
            overall_score = 0
        
        return {
            'matched_skills': exact_matches,
            'fuzzy_matched_skills': [(jd, resume, round(score * 100)) for jd, resume, score in fuzzy_matches],
            'missing_skills': missing_skills,
            'skill_match_score': exact_match_score,
            'fuzzy_match_score': fuzzy_match_score,
            'overall_skill_match_score': overall_score
        }
    
    def analyze_keyword_match(self, resume_text, jd_text):
        """
        Analyze keyword matches between resume and job description using TF-IDF.
        
        Args:
            resume_text (str): Raw text from resume
            jd_text (str): Raw text from job description
            
        Returns:
            dict: Keyword match analysis results
        """
        if not resume_text or not jd_text:
            return {'keyword_match_score': 0}
        
        # Clean and tokenize texts
        resume_text = self._clean_text(resume_text)
        jd_text = self._clean_text(jd_text)
        
        # Create TF-IDF matrix
        try:
            tfidf_matrix = self.vectorizer.fit_transform([jd_text, resume_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            similarity = 0
        
        # Convert similarity to percentage score
        keyword_match_score = similarity * 100
        
        return {
            'keyword_match_score': keyword_match_score
        }
    
    def analyze_education_match(self, resume_education, jd_education_requirements):
        """
        Analyze education matches between resume and job description.
        
        Args:
            resume_education (list): Education entries from resume
            jd_education_requirements (list): Education requirements from job description
            
        Returns:
            dict: Education match analysis results
        """
        if not jd_education_requirements:
            return {'education_match_score': 100}  # No requirements means perfect match
        
        # Extract degrees from resume
        resume_degrees = []
        for edu in resume_education:
            degree = edu.get('degree', '').lower()
            if degree:
                resume_degrees.append(degree)
        
        # Match degrees
        matched_degrees = []
        missing_degrees = []
        
        for req in jd_education_requirements:
            req_lower = req.lower()
            matched = False
            
            for degree in resume_degrees:
                if req_lower in degree or degree in req_lower:
                    matched = True
                    matched_degrees.append(req)
                    break
            
            if not matched:
                missing_degrees.append(req)
        
        # Calculate score
        if len(jd_education_requirements) > 0:
            education_match_score = (len(matched_degrees) / len(jd_education_requirements)) * 100
        else:
            education_match_score = 100  # No requirements means perfect match
        
        return {
            'matched_degrees': matched_degrees,
            'missing_degrees': missing_degrees,
            'education_match_score': education_match_score
        }
    
    def analyze_experience_match(self, resume_experience, jd_experience_requirements):
        """
        Analyze experience matches between resume and job description.
        
        Args:
            resume_experience (list): Experience entries from resume
            jd_experience_requirements (list): Experience requirements from job description
            
        Returns:
            dict: Experience match analysis results
        """
        if not jd_experience_requirements:
            return {'experience_match_score': 100}  # No requirements means perfect match
        
        # Extract years of experience from resume
        total_years = 0
        for exp in resume_experience:
            years = exp.get('duration_years', 0)
            if years:
                total_years += years
        
        # Extract required years from job description
        required_years = 0
        for req in jd_experience_requirements:
            # Try to extract years from requirement text
            years_match = re.search(r'(\d+)[\+]?\s*(?:year|yr)', req.lower())
            if years_match:
                req_years = int(years_match.group(1))
                required_years = max(required_years, req_years)
        
        # Calculate score
        if required_years > 0:
            if total_years >= required_years:
                experience_match_score = 100
            else:
                experience_match_score = (total_years / required_years) * 100
        else:
            experience_match_score = 100  # No specific year requirement means perfect match
        
        return {
            'resume_years': total_years,
            'required_years': required_years,
            'experience_match_score': experience_match_score
        }
    
    def calculate_overall_hard_match_score(self, skill_match, keyword_match, education_match, experience_match):
        """
        Calculate overall hard match score.
        
        Args:
            skill_match (dict): Skill match results
            keyword_match (dict): Keyword match results
            education_match (dict): Education match results
            experience_match (dict): Experience match results
            
        Returns:
            float: Overall hard match score
        """
        # Weights for different components
        weights = {
            'skill': 0.4,
            'keyword': 0.3,
            'education': 0.15,
            'experience': 0.15
        }
        
        # Get individual scores
        skill_score = skill_match.get('overall_skill_match_score', 0)
        keyword_score = keyword_match.get('keyword_match_score', 0)
        education_score = education_match.get('education_match_score', 0)
        experience_score = experience_match.get('experience_match_score', 0)
        
        # Calculate weighted average
        overall_score = (
            skill_score * weights['skill'] +
            keyword_score * weights['keyword'] +
            education_score * weights['education'] +
            experience_score * weights['experience']
        )
        
        return overall_score
    
    def _clean_text(self, text):
        """
        Clean text for TF-IDF processing.
        
        Args:
            text (str): Text to clean
            
        Returns:
            str: Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text