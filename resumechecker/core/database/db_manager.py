"""
Database Manager Module

This module handles database operations for storing and retrieving analysis results.
"""
import os
import json
import sqlite3
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import DATABASE_URI


class DatabaseManager:
    """Manager for database operations."""

    def __init__(self):
        """Initialize the DatabaseManager."""
        self.db_path = DATABASE_URI
        self._create_tables_if_not_exist()

    def _create_tables_if_not_exist(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create analyses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            resume_filename TEXT,
            job_title TEXT,
            relevance_score REAL,
            verdict TEXT,
            created_at TIMESTAMP,
            result_json TEXT
        )
        ''')
        
        conn.commit()
        conn.close()

    def save_analysis(self, analysis_id, resume_filename, job_title, result):
        """
        Save analysis result to database.
        
        Args:
            analysis_id (str): Unique ID for the analysis
            resume_filename (str): Original resume filename
            job_title (str): Job title
            result (dict): Analysis result
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''
                INSERT INTO analyses (id, resume_filename, job_title, relevance_score, verdict, created_at, result_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    analysis_id,
                    resume_filename,
                    job_title or "Untitled Position",
                    result["relevance_score"],
                    result["verdict"],
                    datetime.now().isoformat(),
                    json.dumps(result)
                )
            )
            
            conn.commit()
            conn.close()
            
            return True
        
        except Exception as e:
            print(f"Error saving analysis to database: {str(e)}")
            return False

    def get_analysis(self, analysis_id):
        """
        Get analysis result by ID.
        
        Args:
            analysis_id (str): Analysis ID
            
        Returns:
            dict: Analysis result or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT * FROM analyses WHERE id = ?',
                (analysis_id,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                result = dict(row)
                result["result_json"] = json.loads(result["result_json"])
                return result
            
            return None
        
        except Exception as e:
            print(f"Error retrieving analysis from database: {str(e)}")
            return None

    def get_recent_analyses(self, limit=10):
        """
        Get recent analyses.
        
        Args:
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of recent analyses
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                '''
                SELECT id, resume_filename, job_title, relevance_score, verdict, created_at
                FROM analyses
                ORDER BY created_at DESC
                LIMIT ?
                ''',
                (limit,)
            )
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        
        except Exception as e:
            print(f"Error retrieving recent analyses from database: {str(e)}")
            return []


if __name__ == "__main__":
    # Example usage
    db_manager = DatabaseManager()
    
    # Example analysis result
    example_result = {
        "id": "test-id-123",
        "relevance_score": 85.5,
        "verdict": "High",
        "missing_elements": {
            "skills": {
                "required": ["Docker"],
                "preferred": ["GraphQL"]
            },
            "keywords": ["cloud"],
            "education": {},
            "experience": {}
        },
        "suggestions": [
            "Add Docker to your skills section",
            "Consider adding GraphQL to your skills"
        ],
        "hard_match_details": {
            "skill_match": {"overall_skill_match_score": 80.0},
            "keyword_match": {"keyword_match_score": 90.0},
            "education_match": {"education_match_score": 100.0},
            "experience_match": {"experience_match_score": 85.0}
        },
        "semantic_match_details": {
            "overall_similarity": 0.85,
            "semantic_match_score": 85.0
        }
    }
    
    # Save example analysis
    db_manager.save_analysis(
        "test-id-123",
        "example_resume.pdf",
        "Software Developer",
        example_result
    )
    
    # Retrieve analysis
    retrieved = db_manager.get_analysis("test-id-123")
    if retrieved:
        print(f"Retrieved analysis for {retrieved['job_title']}")
        print(f"Score: {retrieved['relevance_score']}, Verdict: {retrieved['verdict']}")
    
    # Get recent analyses
    recent = db_manager.get_recent_analyses(5)
    print(f"Found {len(recent)} recent analyses")