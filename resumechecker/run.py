"""
Run script for the Automated Resume Relevance Check System.

This script provides commands to run the backend API and frontend Streamlit app.
"""
import os
import sys
import subprocess
import time
import webbrowser
from config import FLASK_HOST, FLASK_PORT, STREAMLIT_PORT

def run_backend():
    """Run the FastAPI backend server."""
    print("Starting FastAPI backend server...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.Popen([sys.executable, "-m", "uvicorn", "app.api.app:app", "--host", "0.0.0.0", "--port", "8000"])
    print("Backend server started at http://localhost:8000")

def run_frontend():
    """Run the Streamlit frontend app."""
    print("Starting Streamlit frontend app...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app/frontend/streamlit_app.py"])
    print("Frontend app started at http://localhost:8501")

def run_all():
    """Run both backend and frontend."""
    run_backend()
    time.sleep(2)  # Wait for backend to start
    run_frontend()
    time.sleep(2)  # Wait for frontend to start
    
    # Open browser tabs
    webbrowser.open("http://localhost:8000")
    webbrowser.open("http://localhost:8501")
    
    print("\nResume Relevance Check System is now running!")
    print("API Documentation: http://localhost:8000/docs")
    print("Frontend Interface: http://localhost:8501")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "backend":
            run_backend()
        elif sys.argv[1] == "frontend":
            run_frontend()
        else:
            print("Invalid argument. Use 'backend', 'frontend', or no argument to run both.")
    else:
        run_all()