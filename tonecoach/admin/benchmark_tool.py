import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO

from database.db_utils import (
    get_all_exercises,
    get_exercise,
    save_benchmark_audio
)
from utils.audio import save_benchmark_audio as save_benchmark_file
from analysis.speech_analyzer import SpeechAnalyzer

# Initialize speech analyzer
analyzer = SpeechAnalyzer()

def display_admin_benchmark_tool():
    """Display admin tool for managing benchmark recordings"""
    st.title("Benchmark Recording Management")
    st.write("This tool allows administrators to upload and manage benchmark recordings for exercises.")
    
    # Get all exercises
    exercises = get_all_exercises()
    
    if not exercises:
        st.warning("No exercises found. Please create exercises first.")
        return
    
    # Convert to DataFrame for easier display
    df = pd.DataFrame(exercises)
    
    # Add a column to show if benchmark is available
    df['has_benchmark'] = df['benchmark_audio_path'].apply(lambda x: "✓" if x else "✗")
    
    # Display exercises table
    st.subheader("Exercises")
    st.dataframe(
        df[['id', 'title', 'category', 'difficulty', 'has_benchmark']],
        use_container_width=True
    )
    
    # Exercise selection for benchmark management
    st.subheader("Upload Benchmark Recording")
    
    exercise_options = [""] + [f"{ex['id']}: {ex['title']} ({ex['difficulty']})" for ex in exercises]
    selected_exercise = st.selectbox(
        "Select an exercise",
        exercise_options,
        format_func=lambda x: "Select an exercise..." if x == "" else x
    )
    
    if selected_exercise:
        exercise_id = int(selected_exercise.split(":")[0])
        exercise = get_exercise(exercise_id)
        
        if exercise:
            st.write(f"**Selected Exercise:** {exercise['title']}")
            st.write(f"**Category:** {exercise['category']}")
            st.write(f"**Difficulty:** {exercise['difficulty']}")
            
            # Display text content
            st.subheader("Exercise Text:")
            st.info(exercise['text_content'])
            
            # Check if benchmark already exists
            has_benchmark = exercise['benchmark_audio_path'] is not None
            
            if has_benchmark:
                st.success("This exercise already has a benchmark recording.")
                st.write("You can replace it by uploading a new one.")
                
                # Display existing benchmark
                benchmark_path = Path(exercise['benchmark_audio_path'])
                if benchmark_path.exists():
                    st.audio(str(benchmark_path))
            
            # Benchmark recording methods
            st.subheader("Upload Benchmark Recording")
            
            tab1, tab2 = st.tabs(["Record New Benchmark", "Upload Audio File"])
            
            with tab1:
                st.write("Record a high-quality benchmark for this exercise:")
                audio_bytes = st.audio_input("Click to record benchmark audio", key="benchmark_recorder")
                
                if audio_bytes:
                    st.success("Benchmark recorded successfully!")
                    st.audio(audio_bytes)
                    
                    if st.button("Save as Benchmark", key="save_recorded_benchmark"):
                        with st.spinner("Processing benchmark recording..."):
                            # Handle audio bytes
                            try:
                                # Analyze the benchmark recording
                                analysis_results = analyzer.analyze(audio_bytes)
                                
                                if analysis_results:
                                    # Save the benchmark audio file
                                    benchmark_path = save_benchmark_file(
                                        exercise_id, 
                                        audio_bytes, 
                                        metadata={
                                            "transcription": analysis_results.get('transcription', ''),
                                            "expressiveness_score": analysis_results.get('expressiveness_score', 0),
                                            "pitch_variability": analysis_results.get('pitch_variability', 0),
                                            "energy_variability": analysis_results.get('energy_variability', 0),
                                            "speech_rate": analysis_results.get('speech_rate', 0),
                                            "primary_emotion": analysis_results.get('primary_emotion', 'neutral')
                                        }
                                    )
                                    
                                    # Update database with benchmark path
                                    save_benchmark_audio(
                                        exercise_id, 
                                        benchmark_path, 
                                        metadata={
                                            "transcription": analysis_results.get('transcription', ''),
                                            "expressiveness_score": analysis_results.get('expressiveness_score', 0),
                                            "pitch_variability": analysis_results.get('pitch_variability', 0),
                                            "energy_variability": analysis_results.get('energy_variability', 0),
                                            "speech_rate": analysis_results.get('speech_rate', 0),
                                            "primary_emotion": analysis_results.get('primary_emotion', 'neutral')
                                        }
                                    )
                                    
                                    st.success("Benchmark recording saved successfully!")
                                    
                                    # Display analysis results
                                    st.subheader("Benchmark Analysis")
                                    
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Expressiveness", f"{analysis_results.get('expressiveness_score', 0):.1f}%")
                                    with col2:
                                        st.metric("Pitch Variation", f"{analysis_results.get('pitch_variability', 0):.1f}")
                                    with col3:
                                        st.metric("Energy Variation", f"{analysis_results.get('energy_variability', 0):.3f}")
                                    with col4:
                                        st.metric("Speech Rate", f"{analysis_results.get('speech_rate', 0):.1f} syl/sec")
                                    
                                    # Display transcription
                                    st.subheader("Transcription")
                                    st.write(analysis_results.get('transcription', 'No transcription available.'))
                                    
                                    # Reload the page to show updated benchmark
                                    st.rerun()
                                else:
                                    st.error("Error analyzing benchmark recording.")
                            except Exception as e:
                                st.error(f"Error processing benchmark recording: {e}")
            
            with tab2:
                st.write("Upload an existing audio file as benchmark:")
                uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "ogg"], key="benchmark_uploader")
                
                if uploaded_file:
                    st.success("File uploaded successfully!")
                    st.audio(uploaded_file)
                    
                    if st.button("Save as Benchmark", key="save_uploaded_benchmark"):
                        with st.spinner("Processing benchmark file..."):
                            try:
                                # Analyze the benchmark recording
                                analysis_results = analyzer.analyze(uploaded_file)
                                
                                # Reset file position
                                uploaded_file.seek(0)
                                
                                if analysis_results:
                                    # Save the benchmark audio file
                                    benchmark_path = save_benchmark_file(
                                        exercise_id, 
                                        uploaded_file, 
                                        metadata={
                                            "transcription": analysis_results.get('transcription', ''),
                                            "expressiveness_score": analysis_results.get('expressiveness_score', 0),
                                            "pitch_variability": analysis_results.get('pitch_variability', 0),
                                            "energy_variability": analysis_results.get('energy_variability', 0),
                                            "speech_rate": analysis_results.get('speech_rate', 0),
                                            "primary_emotion": analysis_results.get('primary_emotion', 'neutral')
                                        }
                                    )
                                    
                                    # Update database with benchmark path
                                    save_benchmark_audio(
                                        exercise_id, 
                                        benchmark_path, 
                                        metadata={
                                            "transcription": analysis_results.get('transcription', ''),
                                            "expressiveness_score": analysis_results.get('expressiveness_score', 0),
                                            "pitch_variability": analysis_results.get('pitch_variability', 0),
                                            "energy_variability": analysis_results.get('energy_variability', 0),
                                            "speech_rate": analysis_results.get('speech_rate', 0),
                                            "primary_emotion": analysis_results.get('primary_emotion', 'neutral')
                                        }
                                    )
                                    
                                    st.success("Benchmark recording saved successfully!")
                                    
                                    # Display analysis results
                                    st.subheader("Benchmark Analysis")
                                    
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Expressiveness", f"{analysis_results.get('expressiveness_score', 0):.1f}%")
                                    with col2:
                                        st.metric("Pitch Variation", f"{analysis_results.get('pitch_variability', 0):.1f}")
                                    with col3:
                                        st.metric("Energy Variation", f"{analysis_results.get('energy_variability', 0):.3f}")
                                    with col4:
                                        st.metric("Speech Rate", f"{analysis_results.get('speech_rate', 0):.1f} syl/sec")
                                    
                                    # Display transcription
                                    st.subheader("Transcription")
                                    st.write(analysis_results.get('transcription', 'No transcription available.'))
                                    
                                    # Reload the page to show updated benchmark
                                    st.rerun()
                                else:
                                    st.error("Error analyzing benchmark recording.")
                            except Exception as e:
                                st.error(f"Error processing benchmark recording: {e}")

if __name__ == "__main__":
    # This allows the file to be run directly for testing
    display_admin_benchmark_tool()