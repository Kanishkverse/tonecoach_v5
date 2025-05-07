import streamlit as st
import os
from pathlib import Path

# Import modules
from database.db_utils import init_db
from ui.pages import (
    display_login_page,
    display_register_page,
    display_dashboard_page,
    display_practice_page,
    display_exercises_page,
    display_recordings_page,
    display_recording_detail_page,
    display_voice_enrollment_page,
    display_settings_page,
    display_exercise_detail_page
)
from analysis.speech_analyzer import SpeechAnalyzer
from analysis.feedback_generator import FeedbackGenerator
from utils.auth import check_auth

# Setup folders
UPLOAD_FOLDER = Path("uploads")
MODEL_FOLDER = Path("models")
for folder in [UPLOAD_FOLDER, MODEL_FOLDER]:
    folder.mkdir(exist_ok=True)

# Initialize database
init_db()

# Main app
def main():
    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    
    # Initialize analyzers if not already done
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = SpeechAnalyzer()
    
    if 'feedback_generator' not in st.session_state:
        st.session_state.feedback_generator = FeedbackGenerator()
    
    # Custom CSS
    st.markdown("""
    <style>
    /* Primary Colors */
    :root {
        --primary: #4F46E5;
        --primary-dark: #4338CA;
        --secondary: #10B981;
        --accent: #F59E0B;
        --background: #F9FAFB;
        --surface: #FFFFFF;
        --text: #1F2937;
        --text-light: #6B7280;
    }
    
    /* General styling */
    .main {
        background-color: var(--background);
        color: var(--text);
    }
    
    h1, h2, h3 {
        color: var(--text);
        font-weight: 600;
    }
    
    /* Cards */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Stats */
    .metric-container {
        display: flex;
        justify-content: space-between;
    }
    
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
        width: 23%;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--primary);
    }
    
    .metric-label {
        font-size: 14px;
        color: var(--text-light);
    }
    
    /* Custom button styling */
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: var(--primary-dark);
    }
    
    /* Feedback sections */
    .feedback-section {
        margin-top: 20px;
        margin-bottom: 20px;
    }
    
    /* Auth forms */
    .auth-form {
        max-width: 400px;
        margin: 0 auto;
    }
    
    /* Progress positive/negative */
    .positive {
        color: var(--secondary);
    }
    
    .negative {
        color: #EF4444;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App title and sidebar
    st.sidebar.title("ToneCoach")
    
    # Navigation
    if check_auth():
        # User is authenticated
        nav_options = [
            "Dashboard",
            "Practice",
            "Exercises",
            "My Recordings",
            "Voice Enrollment",
            "Settings",
            "Logout"
        ]
        
        nav_selection = st.sidebar.radio("Navigation", nav_options)
        handle_navigation(nav_selection)
    else:
        # User is not authenticated
        auth_option = st.sidebar.radio("Authentication", ["Login", "Register"])
        
        if auth_option == "Login":
            st.session_state.page = 'login'
        else:
            st.session_state.page = 'register'
    
    # Page content
    if st.session_state.page == 'login':
        display_login_page()
    elif st.session_state.page == 'register':
        display_register_page()
    elif st.session_state.page == 'dashboard':
        display_dashboard_page()
    elif st.session_state.page == 'practice':
        display_practice_page(st.session_state.analyzer, st.session_state.feedback_generator)
    elif st.session_state.page == 'exercises':
        display_exercises_page()
    elif st.session_state.page == 'recordings':
        display_recordings_page()
    elif st.session_state.page == 'recording_detail':
        display_recording_detail_page()
    elif st.session_state.page == 'voice_enrollment':
        display_voice_enrollment_page(st.session_state.analyzer)
    elif st.session_state.page == 'settings':
        display_settings_page()
    elif st.session_state.page == 'exercise_detail':
        display_exercise_detail_page(st.session_state.analyzer, st.session_state.feedback_generator)

def handle_navigation(selection):
    if selection == "Dashboard":
        st.session_state.page = 'dashboard'
    elif selection == "Practice":
        st.session_state.page = 'practice'
    elif selection == "Exercises":
        st.session_state.page = 'exercises'
    elif selection == "My Recordings":
        st.session_state.page = 'recordings'
    elif selection == "Voice Enrollment":
        st.session_state.page = 'voice_enrollment'
    elif selection == "Settings":
        st.session_state.page = 'settings'
    elif selection == "Logout":
        st.session_state.user_id = None
        st.session_state.page = 'login'
        st.rerun()

if __name__ == "__main__":
    main()