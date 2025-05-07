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
    Display audio recorder widget
    
    Returns:
        Audio bytes if recorded, otherwise None
    """
    st.write("### Record Your Speech")
    
    # Use the file uploader as a more reliable alternative
    # This is a workaround since audio_recorder may not be available in all Streamlit versions
    uploaded_file = st.file_uploader("Upload an audio recording", type=["wav", "mp3", "ogg"])
    
    if uploaded_file is not None:
        # Read the file
        audio_bytes = uploaded_file.read()
        
        # Display the audio
        st.audio(audio_bytes)
        
        return audio_bytes
    
    # Add a checkbox to simulate recording (for development purposes)
    use_sample = st.checkbox("Use sample recording")
    if use_sample:
        # Return a small sample audio file for testing
        import io
        import numpy as np
        from scipy.io.wavfile import write
        
        # Generate a simple sine wave
        sample_rate = 44100
        duration = 3  # seconds
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(2 * np.pi * 440 * t)  # 440 Hz
        
        # Convert to 16-bit PCM
        tone = (tone * 32767).astype(np.int16)
        
        # Create a BytesIO object
        buffer = io.BytesIO()
        write(buffer, sample_rate, tone)
        buffer.seek(0)
        
        # Display the audio
        audio_bytes = buffer.read()
        st.audio(audio_bytes)
        
        return audio_bytes
    
    return None