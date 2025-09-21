"""
Semantic Match Analyzer Module

This module handles semantic matching between resumes and job descriptions using embeddings.
"""
import numpy as np
from sentence_transformers import SentenceTransformer


class SemanticMatchAnalyzer:
    """Analyzer for semantic matching between resumes and job descriptions."""

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initialize the SemanticMatchAnalyzer.
        
        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        self.model = SentenceTransformer(model_name)

    def analyze(self, resume_data, jd_data):
        """
        Analyze the semantic match between a resume and job description.

        Args:
            resume_data (dict): Parsed resume data
            jd_data (dict): Parsed job description data

        Returns:
            dict: Semantic match analysis results
        """
        # Extract text from resume and job description
        resume_text = resume_data['raw_text']
        jd_text = jd_data['raw_text']
        
        # Calculate overall semantic similarity
        overall_similarity = self._calculate_overall_similarity(resume_text, jd_text)
        
        # Calculate section-wise similarities
        section_similarities = self._calculate_section_similarities(resume_data, jd_data)
        
        # Calculate semantic match score
        semantic_match_score = self._calculate_semantic_match_score(overall_similarity, section_similarities)
        
        # Combine all semantic match results
        semantic_match_results = {
            'overall_similarity': overall_similarity,
            'section_similarities': section_similarities,
            'semantic_match_score': semantic_match_score
        }
        
        return semantic_match_results

    def _calculate_overall_similarity(self, resume_text, jd_text):
        """
        Calculate overall semantic similarity between resume and job description.
        
        Args:
            resume_text (str): Raw resume text
            jd_text (str): Raw job description text
            
        Returns:
            float: Cosine similarity score
        """
        # Generate embeddings
        resume_embedding = self.model.encode(resume_text)
        jd_embedding = self.model.encode(jd_text)
        
        # Calculate cosine similarity
        similarity = self._cosine_similarity(resume_embedding, jd_embedding)
        
        return similarity

    def _calculate_section_similarities(self, resume_data, jd_data):
        """
        Calculate semantic similarities between corresponding sections.
        
        Args:
            resume_data (dict): Parsed resume data
            jd_data (dict): Parsed job description data
            
        Returns:
            dict: Section-wise similarity scores
        """
        section_similarities = {}
        
        # Define section mappings between resume and job description
        section_mappings = {
            'EXPERIENCE': ['RESPONSIBILITIES', 'WHAT YOU\'LL DO', 'ABOUT THE ROLE'],
            'SKILLS': ['REQUIREMENTS', 'QUALIFICATIONS', 'SKILLS', 'WHAT YOU\'LL NEED'],
            'EDUCATION': ['EDUCATION', 'QUALIFICATIONS']
        }
        
        # Calculate similarities for each section mapping
        for resume_section, jd_sections in section_mappings.items():
            resume_section_text = None
            
            # Find the resume section (case-insensitive)
            for section_name, content in resume_data.get('sections', {}).items():
                if resume_section.lower() in section_name.lower():
                    resume_section_text = content
                    break
            
            if not resume_section_text:
                continue
            
            # Find matching JD sections and calculate similarities
            for jd_section in jd_sections:
                jd_section_text = None
                
                # Find the JD section (case-insensitive)
                for section_name, content in jd_data.get('sections', {}).items():
                    if jd_section.lower() in section_name.lower():
                        jd_section_text = content
                        break
                
                if jd_section_text:
                    # Generate embeddings
                    resume_section_embedding = self.model.encode(resume_section_text)
                    jd_section_embedding = self.model.encode(jd_section_text)
                    
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(resume_section_embedding, jd_section_embedding)
                    
                    # Store similarity score
                    section_similarities[f"{resume_section}-{jd_section}"] = similarity
        
        return section_similarities

    def _calculate_semantic_match_score(self, overall_similarity, section_similarities):
        """
        Calculate semantic match score based on similarities.
        
        Args:
            overall_similarity (float): Overall similarity score
            section_similarities (dict): Section-wise similarity scores
            
        Returns:
            float: Semantic match score
        """
        # Define weights
        overall_weight = 0.6
        section_weight = 0.4
        
        # Calculate weighted score
        if section_similarities:
            section_avg_similarity = sum(section_similarities.values()) / len(section_similarities)
            semantic_match_score = (
                overall_weight * overall_similarity +
                section_weight * section_avg_similarity
            ) * 100
        else:
            semantic_match_score = overall_similarity * 100
        
        return semantic_match_score

    def _cosine_similarity(self, embedding1, embedding2):
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1 (numpy.ndarray): First embedding vector
            embedding2 (numpy.ndarray): Second embedding vector
            
        Returns:
            float: Cosine similarity score
        """
        # Normalize embeddings
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2)
        
        return similarity