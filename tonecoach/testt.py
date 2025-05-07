import streamlit as st

# Native Streamlit audio input (available in newer versions)
audio_data = st.audio_input("Record your voice")

if audio_data:
    # Process audio data
    st.audio(audio_data)