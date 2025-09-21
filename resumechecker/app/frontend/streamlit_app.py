"""
Streamlit Frontend Application

This module implements the Streamlit frontend for the Resume Relevance Check System.
"""
import os
import sys
import json
import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import API_URL, VERDICT_THRESHOLDS

# Page configuration
st.set_page_config(
    page_title="Resume Relevance Checker",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .verdict-high {
        font-size: 1.8rem;
        color: #2E7D32;
        font-weight: bold;
    }
    .verdict-medium {
        font-size: 1.8rem;
        color: #FF9800;
        font-weight: bold;
    }
    .verdict-low {
        font-size: 1.8rem;
        color: #D32F2F;
        font-weight: bold;
    }
    .score-box {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .suggestion-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def create_gauge_chart(score):
    """Create a gauge chart for the relevance score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Relevance Score", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, VERDICT_THRESHOLDS['medium']], 'color': '#ffcccb'},
                {'range': [VERDICT_THRESHOLDS['medium'], VERDICT_THRESHOLDS['high']], 'color': '#FFEB3B'},
                {'range': [VERDICT_THRESHOLDS['high'], 100], 'color': '#81c784'}
            ],
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    return fig


def create_radar_chart(hard_match_details):
    """Create a radar chart for hard match details."""
    categories = ['Skills', 'Keywords', 'Education', 'Experience']
    values = [
        hard_match_details['skill_match']['overall_skill_match_score'],
        hard_match_details['keyword_match']['keyword_match_score'],
        hard_match_details['education_match']['education_match_score'],
        hard_match_details['experience_match']['experience_match_score']
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Match Score',
        line_color='#1E88E5'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        height=300,
        margin=dict(l=70, r=70, t=20, b=20),
    )
    
    return fig


def display_results(result):
    """Display analysis results."""
    st.markdown("<h1 class='main-header'>Resume Analysis Results</h1>", unsafe_allow_html=True)
    
    # Display verdict and score
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("<div class='score-box'>", unsafe_allow_html=True)
        st.markdown("<h2 class='sub-header'>Verdict</h2>", unsafe_allow_html=True)
        
        verdict = result["verdict"]
        if verdict == "High":
            st.markdown("<p class='verdict-high'>High Match</p>", unsafe_allow_html=True)
        elif verdict == "Medium":
            st.markdown("<p class='verdict-medium'>Medium Match</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p class='verdict-low'>Low Match</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        gauge_chart = create_gauge_chart(result["relevance_score"])
        st.plotly_chart(gauge_chart, use_container_width=True)
    
    # Display match details
    st.markdown("<h2 class='sub-header'>Match Details</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        radar_chart = create_radar_chart(result["hard_match_details"])
        st.plotly_chart(radar_chart, use_container_width=True)
    
    with col2:
        st.markdown("<h3>Semantic Match</h3>", unsafe_allow_html=True)
        
        semantic_details = result["semantic_match_details"]
        overall_similarity = semantic_details["overall_similarity"]
        
        st.markdown(f"<p>Overall Semantic Similarity: <b>{overall_similarity:.2f}</b></p>", unsafe_allow_html=True)
        
        if "section_similarities" in semantic_details:
            section_data = []
            for section, score in semantic_details["section_similarities"].items():
                section_name = section.split('-')[0]
                section_data.append({"Section": section_name, "Similarity": score})
            
            if section_data:
                df = pd.DataFrame(section_data)
                fig = px.bar(df, x="Section", y="Similarity", color="Similarity",
                             color_continuous_scale=["red", "yellow", "green"],
                             range_color=[0, 1])
                fig.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
    
    # Display missing elements
    st.markdown("<h2 class='sub-header'>Missing Elements</h2>", unsafe_allow_html=True)
    
    missing_elements = result["missing_elements"]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<h3>Required Skills</h3>", unsafe_allow_html=True)
        if missing_elements["skills"]["required"]:
            for skill in missing_elements["skills"]["required"]:
                st.markdown(f"- {skill}")
        else:
            st.markdown("✅ All required skills present")
        
        st.markdown("<h3>Keywords</h3>", unsafe_allow_html=True)
        if missing_elements["keywords"]:
            for keyword in missing_elements["keywords"]:
                st.markdown(f"- {keyword}")
        else:
            st.markdown("✅ All important keywords present")
    
    with col2:
        st.markdown("<h3>Preferred Skills</h3>", unsafe_allow_html=True)
        if missing_elements["skills"]["preferred"]:
            for skill in missing_elements["skills"]["preferred"]:
                st.markdown(f"- {skill}")
        else:
            st.markdown("✅ All preferred skills present")
        
        st.markdown("<h3>Education & Experience</h3>", unsafe_allow_html=True)
        if missing_elements["education"]:
            st.markdown(f"- Required: {missing_elements['education']['required']}")
            st.markdown(f"- Current: {missing_elements['education']['current']}")
        else:
            st.markdown("✅ Education requirements met")
        
        if missing_elements["experience"]:
            st.markdown(f"- Required: {missing_elements['experience']['required_years']} years")
            st.markdown(f"- Current: {missing_elements['experience']['current_years']} years")
        else:
            st.markdown("✅ Experience requirements met")
    
    # Display suggestions
    st.markdown("<h2 class='sub-header'>Improvement Suggestions</h2>", unsafe_allow_html=True)
    
    suggestions = result["suggestions"]
    if suggestions:
        for suggestion in suggestions:
            st.markdown(f"<div class='suggestion-box'>{suggestion}</div>", unsafe_allow_html=True)
    else:
        st.markdown("✅ No suggestions needed - your resume is well-matched to this job!")


def main():
    """Main function for the Streamlit app."""
    st.markdown("<h1 class='main-header'>Resume Relevance Checker</h1>", unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.image("https://img.icons8.com/color/96/000000/resume.png", width=100)
    st.sidebar.markdown("## Upload and Analyze")
    st.sidebar.markdown("Upload your resume and enter a job description to check how well your resume matches the job requirements.")
    
    # Session state initialization
    if 'result' not in st.session_state:
        st.session_state.result = None
    
    # File upload
    resume_file = st.sidebar.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
    
    # Job description input
    st.sidebar.markdown("### Job Description")
    jd_title = st.sidebar.text_input("Job Title (Optional)")
    jd_text = st.sidebar.text_area("Paste Job Description", height=300)
    
    # Analyze button
    analyze_button = st.sidebar.button("Analyze Resume")
    
    if analyze_button and resume_file is not None and jd_text:
        with st.spinner("Analyzing your resume..."):
            try:
                # Prepare form data
                files = {"resume_file": resume_file}
                data = {"jd_text": jd_text}
                
                if jd_title:
                    data["jd_title"] = jd_title
                
                # Make API request
                response = requests.post(f"{API_URL}/analyze", files=files, data=data)
                
                if response.status_code == 200:
                    st.session_state.result = response.json()
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display results if available
    if st.session_state.result:
        display_results(st.session_state.result)
    else:
        # Display instructions
        st.markdown("""
        ## Welcome to the Resume Relevance Checker!
        
        This tool helps you analyze how well your resume matches a specific job description.
        
        ### How to use:
        1. Upload your resume (PDF or DOCX format)
        2. Enter the job title (optional)
        3. Paste the job description
        4. Click "Analyze Resume"
        
        ### What you'll get:
        - Overall relevance score and verdict
        - Detailed match analysis (skills, keywords, education, experience)
        - Missing elements that could improve your resume
        - Personalized suggestions for better alignment with the job
        
        Get started by uploading your resume and job description in the sidebar!
        """)


if __name__ == "__main__":
    main()