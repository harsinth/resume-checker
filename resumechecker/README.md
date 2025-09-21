# Automated Resume Relevance Check System

An AI-powered system that evaluates resumes against job descriptions to generate relevance scores, identify gaps, and provide actionable feedback.

## Features

- Resume parsing (PDF/DOCX)
- Job description analysis
- Relevance scoring (0-100)
- Gap identification (missing skills, certifications, projects)
- Fit verdict (High/Medium/Low suitability)
- Personalized improvement feedback
- Web-based dashboard for placement team

## Project Structure

```
resumechecker/
├── app/                    # Web application
│   ├── api/                # API endpoints
│   ├── static/             # Static files
│   ├── templates/          # HTML templates
│   └── app.py              # Main application file
├── core/                   # Core functionality
│   ├── parser/             # Resume and JD parsing
│   ├── analyzer/           # Relevance analysis
│   └── scoring/            # Scoring mechanism
├── data/                   # Sample data and storage
│   ├── resumes/            # Sample resumes
│   └── job_descriptions/   # Sample job descriptions
├── models/                 # Database models
├── utils/                  # Utility functions
├── config.py               # Configuration settings
├── requirements.txt        # Dependencies
└── README.md               # Project documentation
```

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Download required NLTK data: `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"`
6. Download spaCy model: `python -m spacy download en_core_web_md`

## Usage

1. Start the web application: `python app/app.py`
2. Access the dashboard at `http://localhost:5000`
3. Upload job descriptions and resumes
4. View evaluation results and recommendations

## Tech Stack

- Python (core language)
- PyMuPDF / pdfplumber (PDF parsing)
- python-docx / docx2txt (DOCX parsing)
- spaCy / NLTK (NLP)
- LangChain (LLM workflows)
- Flask (backend)
- Streamlit (frontend)
- SQLite/PostgreSQL (database)