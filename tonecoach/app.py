import streamlit as st

# First Streamlit command must be set_page_config
st.set_page_config(
    page_title="ToneCoach - AI Speech Coaching",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)
from utils.voice_cloning import integrate_voice_cloning
import time
from pathlib import Path

# Import UI components
from ui.pages import (
    display_login_page,
    display_register_page,
    display_dashboard_page,
    display_practice_page,
    display_exercises_page,
    display_exercise_detail_page,
    display_recordings_page,
    display_recording_detail_page,
    display_voice_enrollment_page,
    display_settings_page
)

# Import admin component
from admin.benchmark_tool import display_admin_benchmark_tool

# Import analysis components
from analysis.speech_analyzer import SpeechAnalyzer
from analysis.feedback_generator import FeedbackGenerator

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'login'

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Initialize analyzer and feedback generator
@st.cache_resource
def load_analyzer():
    return SpeechAnalyzer()

@st.cache_resource
def load_feedback_generator():
    return FeedbackGenerator()

if 'analyzer' not in st.session_state:
    st.session_state.analyzer = load_analyzer()

if 'feedback_generator' not in st.session_state:
    st.session_state.feedback_generator = load_feedback_generator()

# Add custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .stButton button {
        width: 100%;
    }
    
    .metric-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
    }
    
    .comparison-chart {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
def sidebar():
    if st.session_state.user_id:
        st.sidebar.title("Navigation")
        
        if st.sidebar.button("Dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
        
        if st.sidebar.button("Practice"):
            st.session_state.page = 'practice'
            st.rerun()
        
        if st.sidebar.button("Exercises"):
            st.session_state.page = 'exercises'
            st.rerun()
        
        if st.sidebar.button("My Recordings"):
            st.session_state.page = 'recordings'
            st.rerun()
        
        if st.sidebar.button("Voice Enrollment"):
            st.session_state.page = 'voice_enrollment'
            st.rerun()
        
        if st.sidebar.button("Settings"):
            st.session_state.page = 'settings'
            st.rerun()
        
        # Admin access (in a real app, this would be restricted to admin users)
        st.sidebar.markdown("---")
        st.sidebar.title("Admin")
        
        if st.sidebar.button("Benchmark Management"):
            st.session_state.page = 'admin_benchmark'
            st.rerun()
        
        st.sidebar.markdown("---")
        if st.sidebar.button("Logout"):
            st.session_state.user_id = None
            st.session_state.page = 'login'
            st.rerun()

# Main function
def main():
    # Check if user is logged in
    if not st.session_state.user_id and st.session_state.page not in ['login', 'register']:
        st.session_state.page = 'login'
    
    # Display sidebar if user is logged in
    if st.session_state.user_id:
        sidebar()
        
    # Integrate voice cloning with proper error handling
    try:
        integrate_voice_cloning()
    except Exception as e:
        st.error(f"Voice cloning feature is currently unavailable: {str(e)}")
    
    # Display the appropriate page
    if st.session_state.page == 'login':
        display_login_page()
        
        # Link to register page
        if st.button("Create an Account"):
            st.session_state.page = 'register'
            st.rerun()
    
    elif st.session_state.page == 'register':
        display_register_page()
        
        # Link to login page
        if st.button("Already have an account? Log in"):
            st.session_state.page = 'login'
            st.rerun()
    
    elif st.session_state.page == 'dashboard':
        display_dashboard_page()
    
    elif st.session_state.page == 'practice':
        display_practice_page(st.session_state.analyzer, st.session_state.feedback_generator)
    
    elif st.session_state.page == 'exercises':
        display_exercises_page()
    
    elif st.session_state.page == 'exercise_detail':
        display_exercise_detail_page(st.session_state.analyzer, st.session_state.feedback_generator)
    
    elif st.session_state.page == 'recordings':
        display_recordings_page()
    
    elif st.session_state.page == 'recording_detail':
        display_recording_detail_page()
    
    elif st.session_state.page == 'voice_enrollment':
        display_voice_enrollment_page(st.session_state.analyzer)
    
    elif st.session_state.page == 'settings':
        display_settings_page()
    
    elif st.session_state.page == 'admin_benchmark':
        display_admin_benchmark_tool()

# Run the app
if __name__ == "__main__":
    main()