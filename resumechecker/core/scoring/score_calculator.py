"""
Score Calculator Module

This module calculates the final relevance score and generates verdict based on analysis results.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import WEIGHTS, VERDICT_THRESHOLDS


class ScoreCalculator:
    """Calculator for generating relevance score and verdict."""

    def __init__(self):
        """Initialize the ScoreCalculator."""
        self.weights = WEIGHTS
        self.verdict_thresholds = VERDICT_THRESHOLDS

    def calculate(self, hard_match_results, semantic_match_results):
        """
        Calculate the final relevance score and generate verdict.

        Args:
            hard_match_results (dict): Results from hard match analysis
            semantic_match_results (dict): Results from semantic match analysis

        Returns:
            dict: Final score and verdict
        """
        # Extract scores from analysis results
        hard_match_score = hard_match_results['overall_hard_match_score']
        semantic_match_score = semantic_match_results['semantic_match_score']
        
        # Calculate weighted final score
        final_score = (
            self.weights['hard_match'] * hard_match_score +
            self.weights['semantic_match'] * semantic_match_score
        )
        
        # Round to 2 decimal places
        final_score = round(final_score, 2)
        
        # Generate verdict
        verdict = self._generate_verdict(final_score)
        
        # Identify missing elements
        missing_elements = self._identify_missing_elements(hard_match_results)
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(hard_match_results, semantic_match_results, missing_elements)
        
        return {
            'relevance_score': final_score,
            'verdict': verdict,
            'missing_elements': missing_elements,
            'suggestions': suggestions
        }

    def _generate_verdict(self, score):
        """
        Generate verdict based on score.
        
        Args:
            score (float): Final relevance score
            
        Returns:
            str: Verdict (High/Medium/Low suitability)
        """
        if score >= self.verdict_thresholds['high']:
            return "High"
        elif score >= self.verdict_thresholds['medium']:
            return "Medium"
        else:
            return "Low"

    def _identify_missing_elements(self, hard_match_results):
        """
        Identify missing elements from hard match results.
        
        Args:
            hard_match_results (dict): Results from hard match analysis
            
        Returns:
            dict: Missing elements by category
        """
        missing_elements = {
            'skills': {
                'required': hard_match_results['skill_match']['missing_required'],
                'preferred': hard_match_results['skill_match']['missing_preferred']
            },
            'keywords': hard_match_results['keyword_match']['missing_keywords'],
            'education': {},
            'experience': {}
        }
        
        # Add education details if not matching
        education_match = hard_match_results['education_match']
        if education_match['education_match_score'] < 100:
            missing_elements['education'] = {
                'required': education_match['jd_education'],
                'current': f"Level {education_match['resume_education_level']}"
            }
        
        # Add experience details if not matching
        experience_match = hard_match_results['experience_match']
        if experience_match['experience_match_score'] < 100:
            missing_elements['experience'] = {
                'required_years': experience_match['jd_required_years'],
                'current_years': experience_match['resume_experience_years']
            }
        
        return missing_elements

    def _generate_suggestions(self, hard_match_results, semantic_match_results, missing_elements):
        """
        Generate improvement suggestions based on analysis results.
        
        Args:
            hard_match_results (dict): Results from hard match analysis
            semantic_match_results (dict): Results from semantic match analysis
            missing_elements (dict): Missing elements by category
            
        Returns:
            list: Improvement suggestions
        """
        suggestions = []
        
        # Skill suggestions
        if missing_elements['skills']['required']:
            suggestions.append(
                f"Add the following required skills to your resume: {', '.join(missing_elements['skills']['required'][:5])}"
                + (f" and {len(missing_elements['skills']['required']) - 5} more" if len(missing_elements['skills']['required']) > 5 else "")
            )
        
        if missing_elements['skills']['preferred']:
            suggestions.append(
                f"Consider adding these preferred skills: {', '.join(missing_elements['skills']['preferred'][:3])}"
                + (f" and {len(missing_elements['skills']['preferred']) - 3} more" if len(missing_elements['skills']['preferred']) > 3 else "")
            )
        
        # Keyword suggestions
        if missing_elements['keywords']:
            suggestions.append(
                f"Include these important keywords: {', '.join(missing_elements['keywords'][:5])}"
                + (f" and {len(missing_elements['keywords']) - 5} more" if len(missing_elements['keywords']) > 5 else "")
            )
        
        # Education suggestions
        if missing_elements['education']:
            suggestions.append(
                f"The job requires {missing_elements['education']['required']}. "
                f"Consider highlighting relevant education or certifications."
            )
        
        # Experience suggestions
        if missing_elements['experience']:
            required_years = missing_elements['experience']['required_years']
            current_years = missing_elements['experience']['current_years']
            
            if required_years and current_years:
                gap = int(required_years) - int(current_years)
                if gap > 0:
                    suggestions.append(
                        f"The job requires {required_years} years of experience, but your resume shows {current_years} years. "
                        f"Highlight relevant projects or additional experience to bridge this gap."
                    )
        
        # General suggestions based on semantic match
        section_similarities = semantic_match_results.get('section_similarities', {})
        
        # Find the section with lowest similarity
        if section_similarities:
            lowest_section = min(section_similarities.items(), key=lambda x: x[1])
            section_name = lowest_section[0].split('-')[0]
            
            if lowest_section[1] < 0.7:  # If similarity is low
                suggestions.append(
                    f"Your {section_name.lower()} section could be better aligned with the job requirements. "
                    f"Consider tailoring this section to match the job description more closely."
                )
        
        return suggestions


if __name__ == "__main__":
    # Example usage
    hard_match_results = {
        'overall_hard_match_score': 75.5,
        'skill_match': {
            'matched_required': ['Python', 'Django'],
            'missing_required': ['AWS', 'Docker'],
            'matched_preferred': ['React'],
            'missing_preferred': ['GraphQL', 'TypeScript'],
            'overall_skill_match_score': 70.0
        },
        'keyword_match': {
            'matched_keywords': ['develop', 'software', 'application'],
            'missing_keywords': ['cloud', 'microservices', 'CI/CD'],
            'keyword_match_score': 65.0
        },
        'education_match': {
            'jd_education': "Bachelor's degree in Computer Science",
            'resume_education_level': 3,
            'jd_education_level': 3,
            'education_match_score': 100.0
        },
        'experience_match': {
            'jd_required_years': '5',
            'resume_experience_years': 3,
            'experience_match_score': 60.0
        }
    }
    
    semantic_match_results = {
        'overall_similarity': 0.82,
        'section_similarities': {
            'EXPERIENCE-RESPONSIBILITIES': 0.75,
            'SKILLS-REQUIREMENTS': 0.85,
            'EDUCATION-QUALIFICATIONS': 0.90
        },
        'semantic_match_score': 80.0
    }
    
    calculator = ScoreCalculator()
    result = calculator.calculate(hard_match_results, semantic_match_results)
    
    print(f"Relevance Score: {result['relevance_score']}")
    print(f"Verdict: {result['verdict']} suitability")
    print("\nMissing Elements:")
    for category, elements in result['missing_elements'].items():
        print(f"- {category.capitalize()}: {elements}")
    
    print("\nSuggestions:")
    for suggestion in result['suggestions']:
        print(f"- {suggestion}")