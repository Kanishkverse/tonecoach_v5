import streamlit as st

def display_stats_cards(stats):
    """
    Display metric cards in a grid
    
    Args:
        stats: Dictionary containing speech analysis stats
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Expressiveness Score",
            f"{stats['expressiveness_score']:.1f}%",
            delta=None
        )
    
    with col2:
        st.metric(
            "Pitch Variation",
            f"{stats['pitch_variability']:.1f}",
            delta=None,
            help="Higher values indicate more expressive speech"
        )
    
    with col3:
        st.metric(
            "Energy Variation",
            f"{stats['energy_variability']:.3f}",
            delta=None,
            help="Higher values indicate more dynamic volume"
        )
    
    with col4:
        st.metric(
            "Speech Rate",
            f"{stats['speech_rate']:.1f} syl/sec",
            delta=None,
            help="Optimal range is 3-4 syllables per second"
        )

def display_feedback(feedback):
    """
    Display the feedback in a structured format
    
    Args:
        feedback: Dictionary containing feedback components
    """
    if not feedback:
        st.warning("No feedback available")
        return
    
    st.subheader("Overall Assessment")
    st.info(feedback['overall_assessment'])
    
    # Display specific feedback
    st.subheader("Specific Feedback")
    for item in feedback['specific_feedback']:
        st.write(f"• {item}")
    
    # Create two columns for strengths and suggestions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Strengths")
        for strength in feedback['strengths']:
            st.success(f"✓ {strength}")
    
    with col2:
        st.subheader("Improvement Suggestions")
        for suggestion in feedback['improvement_suggestions']:
            st.warning(f"→ {suggestion}")
    
    # Display content accuracy if available
    if feedback.get('content_accuracy'):
        st.subheader("Content Accuracy")
        acc = feedback['content_accuracy']
        st.info(f"Accuracy Score: {acc['accuracy_score']}%")
        st.write(acc['feedback'])
        
        if acc['missing_words']:
            st.write("Missing words: " + ", ".join(acc['missing_words']))
        
        if acc['added_words']:
            st.write("Added words: " + ", ".join(acc['added_words']))

def display_audio_recorder():
    """
    Display audio recorder widget using Streamlit's native audio_input
    
    Returns:
        Audio bytes if recorded, otherwise None
    """
    st.write("### Record Your Speech")
    
    # Use Streamlit's native audio_input component
    audio_bytes = st.audio_input("Click to record your speech", key="speech_recorder")
    
    if audio_bytes:
        # Display the recorded audio
        st.audio(audio_bytes)
        return audio_bytes
    
    # Alternative: Keep file upload option for users who prefer to upload pre-recorded files
    st.write("Or upload a pre-recorded file:")
    uploaded_file = st.file_uploader("Upload an audio recording", type=["wav", "mp3", "ogg"])
    
    if uploaded_file is not None:
        # Read the file
        audio_bytes = uploaded_file.read()
        # Display the audio
        st.audio(audio_bytes)
        return audio_bytes
    
    return None