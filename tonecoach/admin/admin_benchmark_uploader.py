import streamlit as st

# Set page config must be the first Streamlit command
st.set_page_config(page_title="ToneCoach Admin - Benchmark Manager", layout="wide")

import sqlite3
import json
import shutil
from pathlib import Path

# Import SpeechAnalyzer for audio processing
from analysis.speech_analyzer import SpeechAnalyzer

# Initialize the analyzer
analyzer = SpeechAnalyzer()

# Set paths
DB_PATH = "database/tonecoach.db"
BENCHMARK_DIR = Path("benchmarks")
BENCHMARK_DIR.mkdir(exist_ok=True, parents=True)

# Database functions
def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create database tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create exercises table with benchmark_audio field
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        difficulty TEXT,
        text_content TEXT NOT NULL,
        target_emotion TEXT,
        benchmark_audio_path TEXT,
        benchmark_metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def get_exercises():
    """Get all exercises"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM exercises ORDER BY difficulty")
    
    results = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in results]

def create_exercise(title, description, category, difficulty, text_content, target_emotion):
    """Create a new exercise"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO exercises (
                title, description, category, difficulty, text_content, target_emotion
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                category,
                difficulty,
                text_content,
                target_emotion
            )
        )
        conn.commit()
        exercise_id = cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        exercise_id = None
    
    conn.close()
    return exercise_id

def update_exercise_benchmark(exercise_id, benchmark_path, metadata):
    """Update exercise with benchmark data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            UPDATE exercises SET
                benchmark_audio_path = ?,
                benchmark_metadata = ?,
                text_content = ?
            WHERE id = ?
            """,
            (
                str(benchmark_path),
                json.dumps(metadata),
                metadata.get('transcription', ''),
                exercise_id
            )
        )
        conn.commit()
        success = cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        success = False
    
    conn.close()
    return success

def save_benchmark_file(exercise_id, audio_file):
    """Save benchmark audio file"""
    # Create exercise directory
    exercise_dir = BENCHMARK_DIR / f"exercise_{exercise_id}"
    exercise_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate filename
    filename = f"benchmark_{exercise_id}.wav"
    filepath = exercise_dir / filename
    
    # Save audio data to file
    try:
        # Handle different types of input
        if hasattr(audio_file, 'getvalue'):
            # It's a file-like object with getvalue method
            with open(filepath, 'wb') as f:
                f.write(audio_file.getvalue())
        elif hasattr(audio_file, 'read'):
            # It's a file-like object with read method
            with open(filepath, 'wb') as f:
                audio_file.seek(0)
                f.write(audio_file.read())
        elif isinstance(audio_file, bytes):
            # It's raw bytes
            with open(filepath, 'wb') as f:
                f.write(audio_file)
        else:
            # Try to copy the file
            shutil.copy(audio_file, filepath)
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None
    
    # Return absolute path to benchmark audio
    return str(filepath.absolute())

# Main admin UI
def main():
    st.title("ToneCoach Admin - Benchmark Audio Management")
    st.write("This tool allows administrators to manage benchmark recordings for the 5 levels of exercises.")
    
    # Create tables if they don't exist
    create_tables()
    
    # Navigation tabs
    tab1, tab2 = st.tabs(["Manage Exercises", "Upload Benchmarks"])
    
    with tab1:
        st.header("Manage Exercises")
        
        # Display existing exercises
        exercises = get_exercises()
        
        if exercises:
            st.subheader("Existing Exercises")
            
            # Group by difficulty level
            difficulties = sorted(list(set([ex.get('difficulty', '') for ex in exercises])))
            
            for diff in difficulties:
                with st.expander(f"Level: {diff}", expanded=True):
                    level_exercises = [ex for ex in exercises if ex.get('difficulty', '') == diff]
                    
                    for ex in level_exercises:
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**{ex['title']}**")
                            st.write(f"Category: {ex['category']}")
                            
                            # Check if benchmark exists
                            has_benchmark = ex['benchmark_audio_path'] is not None
                            if has_benchmark:
                                st.success("✓ Has benchmark recording")
                            else:
                                st.warning("✗ No benchmark recording")
                        
                        with col2:
                            if has_benchmark:
                                benchmark_path = Path(ex['benchmark_audio_path'])
                                if benchmark_path.exists():
                                    st.audio(str(benchmark_path))
        
        # Create new exercise
        st.subheader("Create New Exercise")
        
        with st.form("create_exercise_form"):
            title = st.text_input("Title")
            description = st.text_area("Description")
            
            col1, col2 = st.columns(2)
            
            with col1:
                category = st.text_input("Category")
                difficulty = st.selectbox(
                    "Difficulty Level", 
                    ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]
                )
            
            with col2:
                target_emotion = st.selectbox(
                    "Target Emotion",
                    ["neutral", "confident", "enthusiastic", "persuasive", "inspiring"]
                )
            
            text_content = st.text_area("Exercise Text Content (will be replaced by transcription if provided)")
            
            submit = st.form_submit_button("Create Exercise")
            
            if submit:
                if not title or not text_content:
                    st.error("Title and text content are required")
                else:
                    exercise_id = create_exercise(
                        title, description, category, difficulty, text_content, target_emotion
                    )
                    
                    if exercise_id:
                        st.success(f"Exercise created successfully with ID: {exercise_id}")
                        st.info("Now you can upload a benchmark recording for this exercise")
                    else:
                        st.error("Error creating exercise")
    
    with tab2:
        st.header("Upload Benchmark Recordings")
        st.write("Upload benchmark audio files for the exercises. The system will analyze the audio, extract the text, and save the results.")
        
        # Get exercises
        exercises = get_exercises()
        
        if not exercises:
            st.warning("No exercises found. Please create exercises first.")
        else:
            # Select exercise
            exercise_options = [""] + [f"{ex['id']}: {ex['title']} ({ex['difficulty']})" for ex in exercises]
            selected_exercise = st.selectbox(
                "Select Exercise",
                exercise_options,
                format_func=lambda x: "Select an exercise..." if x == "" else x
            )
            
            if selected_exercise:
                exercise_id = int(selected_exercise.split(":")[0])
                exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
                
                if exercise:
                    st.write(f"**Selected Exercise:** {exercise['title']}")
                    st.write(f"**Difficulty:** {exercise['difficulty']}")
                    st.write(f"**Category:** {exercise['category']}")
                    
                    # Current text content
                    st.subheader("Current Text Content")
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
                            
                            # Display metadata
                            if exercise['benchmark_metadata']:
                                try:
                                    metadata = json.loads(exercise['benchmark_metadata'])
                                    
                                    with st.expander("Current Benchmark Analysis", expanded=True):
                                        col1, col2, col3, col4 = st.columns(4)
                                        
                                        with col1:
                                            st.metric("Expressiveness", f"{metadata.get('expressiveness_score', 0):.1f}%")
                                        with col2:
                                            st.metric("Pitch Variation", f"{metadata.get('pitch_variability', 0):.1f}")
                                        with col3:
                                            st.metric("Energy Variation", f"{metadata.get('energy_variability', 0):.3f}")
                                        with col4:
                                            st.metric("Speech Rate", f"{metadata.get('speech_rate', 0):.1f} syl/sec")
                                        
                                        st.subheader("Transcription")
                                        st.write(metadata.get('transcription', 'No transcription available'))
                                except Exception as e:
                                    st.error(f"Error loading metadata: {e}")
                    
                    # Upload benchmark
                    st.subheader("Upload Benchmark Recording")
                    uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "ogg"])
                    
                    if uploaded_file:
                        st.success("File uploaded successfully!")
                        st.audio(uploaded_file)
                        
                        # Ask if text should be replaced with transcription
                        replace_text = st.checkbox("Replace exercise text with transcription", value=True)
                        
                        if st.button("Process and Save Benchmark"):
                            with st.spinner("Analyzing benchmark recording..."):
                                try:
                                    # Reset file position
                                    uploaded_file.seek(0)
                                    
                                    # Analyze benchmark
                                    analysis_results = analyzer.analyze(uploaded_file)
                                    
                                    if analysis_results:
                                        # Reset file position for saving
                                        uploaded_file.seek(0)
                                        
                                        # Save benchmark file
                                        filepath = save_benchmark_file(exercise_id, uploaded_file)
                                        
                                        if filepath:
                                            # Create metadata
                                            metadata = {
                                                'transcription': analysis_results.get('transcription', ''),
                                                'expressiveness_score': analysis_results.get('expressiveness_score', 0),
                                                'pitch_variability': analysis_results.get('pitch_variability', 0),
                                                'energy_variability': analysis_results.get('energy_variability', 0),
                                                'speech_rate': analysis_results.get('speech_rate', 0),
                                                'primary_emotion': analysis_results.get('primary_emotion', 'neutral'),
                                                'pitch': analysis_results.get('pitch', []),
                                                'pitch_timestamps': analysis_results.get('pitch_timestamps', []),
                                                'energy': analysis_results.get('energy', []),
                                                'energy_timestamps': analysis_results.get('energy_timestamps', []),
                                                'emotions': analysis_results.get('emotions', {})
                                            }
                                            
                                            # Update exercise with benchmark data
                                            text_to_use = analysis_results.get('transcription', '') if replace_text else exercise['text_content']
                                            metadata['text_content'] = text_to_use
                                            
                                            success = update_exercise_benchmark(exercise_id, filepath, metadata)
                                            
                                            if success:
                                                st.success("Benchmark saved successfully!")
                                                
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
                                                st.subheader("Extracted Transcription")
                                                st.info(analysis_results.get('transcription', 'No transcription available'))
                                                
                                                if replace_text:
                                                    st.success("Exercise text has been replaced with the transcription")
                                                
                                                # Display rerun button
                                                st.button("Refresh Page", on_click=lambda: st.rerun())
                                            else:
                                                st.error("Error saving benchmark data")
                                        else:
                                            st.error("Error saving benchmark file")
                                    else:
                                        st.error("Error analyzing benchmark recording")
                                except Exception as e:
                                    st.error(f"Error processing benchmark: {e}")

if __name__ == "__main__":
    main()