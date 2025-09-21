"""
FastAPI Backend Application

This module implements the FastAPI backend for the Resume Relevance Check System.
"""
import os
import sys
import uuid
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.parser.resume_parser import ResumeParser
from core.parser.jd_parser import JobDescriptionParser
from core.analyzer.hard_match_analyzer import HardMatchAnalyzer
from core.analyzer.semantic_match_analyzer import SemanticMatchAnalyzer
from core.scoring.score_calculator import ScoreCalculator
from config import DATA_DIR, UPLOAD_SETTINGS

# Create FastAPI app
app = FastAPI(
    title="Resume Relevance Check API",
    description="API for checking resume relevance against job descriptions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create data directories if they don't exist
os.makedirs(os.path.join(DATA_DIR, "resumes"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "job_descriptions"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "results"), exist_ok=True)

# Initialize parsers and analyzers
resume_parser = ResumeParser()
jd_parser = JobDescriptionParser()
hard_match_analyzer = HardMatchAnalyzer()
semantic_match_analyzer = SemanticMatchAnalyzer()
score_calculator = ScoreCalculator()


# Models
class AnalysisResult(BaseModel):
    """Model for analysis result."""
    id: str
    relevance_score: float
    verdict: str
    missing_elements: dict
    suggestions: List[str]
    hard_match_details: dict
    semantic_match_details: dict


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Resume Relevance Check API is running"}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_resume(
    resume_file: UploadFile = File(...),
    jd_text: str = Form(...),
    jd_title: Optional[str] = Form(None)
):
    """
    Analyze resume against job description.
    
    Args:
        resume_file: Resume file (PDF or DOCX)
        jd_text: Job description text
        jd_title: Job title (optional)
        
    Returns:
        AnalysisResult: Analysis result
    """
    try:
        # Generate unique ID for this analysis
        analysis_id = str(uuid.uuid4())
        
        # Save resume file
        resume_path = os.path.join(DATA_DIR, "resumes", f"{analysis_id}_{resume_file.filename}")
        with open(resume_path, "wb") as f:
            f.write(await resume_file.read())
        
        # Save job description
        jd_path = os.path.join(DATA_DIR, "job_descriptions", f"{analysis_id}.txt")
        with open(jd_path, "w") as f:
            f.write(jd_text)
        
        # Parse resume
        resume_data = resume_parser.parse(resume_path)
        
        # Parse job description
        jd_data = jd_parser.parse(jd_text, jd_title)
        
        # Perform hard match analysis
        hard_match_results = hard_match_analyzer.analyze(resume_data, jd_data)
        
        # Perform semantic match analysis
        semantic_match_results = semantic_match_analyzer.analyze(resume_data, jd_data)
        
        # Calculate final score and verdict
        final_result = score_calculator.calculate(hard_match_results, semantic_match_results)
        
        # Combine results
        result = {
            "id": analysis_id,
            "relevance_score": final_result["relevance_score"],
            "verdict": final_result["verdict"],
            "missing_elements": final_result["missing_elements"],
            "suggestions": final_result["suggestions"],
            "hard_match_details": hard_match_results,
            "semantic_match_details": semantic_match_results
        }
        
        # Save result
        result_path = os.path.join(DATA_DIR, "results", f"{analysis_id}.json")
        import json
        with open(result_path, "w") as f:
            json.dump(result, f)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/analysis/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(analysis_id: str):
    """
    Get analysis result by ID.
    
    Args:
        analysis_id: Analysis ID
        
    Returns:
        AnalysisResult: Analysis result
    """
    try:
        result_path = os.path.join(DATA_DIR, "results", f"{analysis_id}.json")
        
        if not os.path.exists(result_path):
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        import json
        with open(result_path, "r") as f:
            result = json.load(f)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analysis: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)