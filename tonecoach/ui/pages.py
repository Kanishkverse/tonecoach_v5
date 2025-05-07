import streamlit as st
import json
import time
from io import BytesIO
from datetime import datetime
from pathlib import Path

from database.db_utils import (
    get_user_by_username,
    get_user_recordings,
    get_recording,
    get_user_progress,
    get_all_exercises,
    get_exercise,
    save_recording,
    update_voice_model_status
)
from utils.auth import login_user, register_user, update_user
from ui.charts import (
    create_pitch_chart,
    create_energy_chart,
    create_emotion_chart,
    create_progress_chart
)
from ui.components import (
    display_stats_cards,
    display_feedback,
    display_audio_recorder
)
from utils.audio import save_audio_file

# Path to upload directory
UPLOAD_FOLDER = Path("uploads")

def display_login_page():
    """Display the login page"""
    st.title("Login to ToneCoach")
    
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                user_id = login_user(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.page = 'dashboard'
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    st.write("Don't have an account? [Register here](#register)")

def display_register_page():
    """Display the registration page"""
    st.title("Register for ToneCoach")
    
    with st.form("register_form", clear_on_submit=True):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")
        
        if submit:
            if not username or not email or not password:
                st.error("All fields are required")
            elif password != password_confirm:
                st.error("Passwords do not match")
            else:
                success = register_user(username, email, password)
                if success:
                    st.success("Registration successful! Please log in.")
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error("Username or email already exists")
    
    st.write("Already have an account? [Login here](#login)")

def display_dashboard_page():
    """Display the dashboard page"""
    st.title("Your Speaking Progress")
    
    # Get user progress data
    progress_data = get_user_progress(st.session_state.user_id)
    
    if not progress_data or progress_data['recording_count'] == 0:
        st.info("Record your first speech to see your progress dashboard!")
        st.button("Start Practicing", on_click=lambda: setattr(st.session_state, 'page', 'practice'))
        return
    
    # Display average scores
    avg_scores = progress_data['average_scores']
    improvements = progress_data.get('improvements', {})
    
    # Display metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta = improvements.get('expressiveness') 
        delta_color = "normal" if delta is None else ("inverse" if delta < 0 else "normal")
        st.metric(
            "Avg. Expressiveness",
            f"{avg_scores['expressiveness']:.1f}%",
            delta=f"{delta:.1f}%" if delta is not None else None,
            delta_color=delta_color
        )
    
    with col2:
        delta = improvements.get('pitch_variability')
        delta_color = "normal" if delta is None else ("inverse" if delta < 0 else "normal")
        st.metric(
            "Pitch Variation",
            f"{avg_scores['pitch_variability']:.1f}",
            delta=f"{delta:.1f}" if delta is not None else None,
            delta_color=delta_color
        )
    
    with col3:
        delta = improvements.get('energy_variability')
        delta_color = "normal" if delta is None else ("inverse" if delta < 0 else "normal")
        st.metric(
            "Energy Variation",
            f"{avg_scores['energy_variability']:.3f}",
            delta=f"{delta:.3f}" if delta is not None else None,
            delta_color=delta_color
        )
    
    with col4:
        delta = improvements.get('speech_rate')
        # For speech rate, closer to the ideal (3.5) is better
        ideal_rate = 3.5
        current_rate = avg_scores['speech_rate']
        prev_rate = current_rate - (delta if delta is not None else 0)
        
        current_distance = abs(current_rate - ideal_rate)
        prev_distance = abs(prev_rate - ideal_rate)
        
        improvement = prev_distance - current_distance
        delta_color = "normal" if improvement >= 0 else "inverse"
        
        st.metric(
            "Speech Rate",
            f"{current_rate:.1f} syl/sec",
            delta=f"{delta:.1f}" if delta is not None else None,
            delta_color=delta_color
        )
    
    # Progress chart
    st.subheader("Progress Over Time")
    progress_chart = create_progress_chart(progress_data)
    if progress_chart:
        st.plotly_chart(progress_chart, use_container_width=True)
    
    # Emotion distribution
    st.subheader("Emotional Tone Distribution")
    if progress_data['emotion_distribution']:
        emotion_chart = create_emotion_chart(progress_data['emotion_distribution'])
        st.plotly_chart(emotion_chart, use_container_width=True)
    
    # Recent recordings
    st.subheader("Recent Practice Sessions")
    recordings = get_user_recordings(st.session_state.user_id, limit=5)
    
    if recordings:
        for recording in recordings:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                created_at = datetime.strptime(recording['created_at'], '%Y-%m-%d %H:%M:%S')
                st.write(f"**{created_at.strftime('%b %d, %Y at %I:%M %p')}**")
                
                # Display truncated transcription if available
                if recording['text_content']:
                    text = recording['text_content']
                    if len(text) > 100:
                        text = text[:100] + "..."
                    st.write(text)
            
            with col2:
                st.metric(
                    "Score",
                    f"{recording['expressiveness_score']:.1f}%",
                    delta=None
                )
            
            with col3:
                st.button(
                    "View Feedback",
                    key=f"view_{recording['id']}",
                    on_click=lambda rid=recording['id']: set_recording_detail(rid)
                )
            
            st.markdown("---")
    else:
        st.info("No recordings yet. Start practicing to see your progress!")

def set_recording_detail(recording_id):
    """Set the recording detail page for a specific recording"""
    st.session_state.recording_id = recording_id
    st.session_state.page = 'recording_detail'

def display_recording_detail_page():
    """Display the recording detail page"""
    if not hasattr(st.session_state, 'recording_id'):
        st.error("No recording selected")
        st.button("Back to Recordings", on_click=lambda: setattr(st.session_state, 'page', 'recordings'))
        return
    
    recording = get_recording(st.session_state.recording_id, st.session_state.user_id)
    
    if not recording:
        st.error("Recording not found")
        st.button("Back to Recordings", on_click=lambda: setattr(st.session_state, 'page', 'recordings'))
        return
    
    st.title("Speech Feedback")
    
    # Back button
    st.button("← Back to Recordings", on_click=lambda: setattr(st.session_state, 'page', 'recordings'))
    
    # Display recording date
    created_at = datetime.strptime(recording['created_at'], '%Y-%m-%d %H:%M:%S')
    st.subheader(f"Recorded on {created_at.strftime('%B %d, %Y at %I:%M %p')}")
    
    # Display audio player
    audio_path = UPLOAD_FOLDER / recording['filename']
    if audio_path.exists():
        st.audio(str(audio_path))
    
    # Display expressiveness stats
    st.subheader("Speech Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Expressiveness", f"{recording['expressiveness_score']:.1f}%")
    with col2:
        st.metric("Pitch Variation", f"{recording['pitch_variability']:.1f}")
    with col3:
        st.metric("Energy Variation", f"{recording['energy_variability']:.3f}")
    with col4:
        st.metric("Speech Rate", f"{recording['speech_rate']:.1f} syl/sec")
    
    # Display feedback
    st.subheader("Feedback")
    try:
        feedback = json.loads(recording['feedback'])
        display_feedback(feedback)
    except Exception as e:
        st.error(f"Error loading feedback: {e}")
    
    # Display transcription if available
    if recording['text_content']:
        st.subheader("Transcription")
        st.write(recording['text_content'])

def display_practice_page(analyzer, feedback_generator):
    """Display the practice page"""
    st.title("Practice Your Speaking")
    
    # Exercise selection
    st.subheader("Choose an Exercise or Enter Custom Text")
    exercises = get_all_exercises()
    
    tab1, tab2 = st.tabs(["Select Exercise", "Custom Text"])
    
    with tab1:
        exercise_options = [""] + [f"{ex['id']}: {ex['title']} ({ex['difficulty']})" for ex in exercises]
        selected_exercise = st.selectbox(
            "Select an exercise",
            exercise_options,
            format_func=lambda x: "Select an exercise..." if x == "" else x
        )
        
        exercise_id = None
        exercise_text = ""
        
        if selected_exercise:
            exercise_id = int(selected_exercise.split(":")[0])
            exercise = get_exercise(exercise_id)
            
            if exercise:
                st.write(f"**Description:** {exercise['description']}")
                st.write(f"**Category:** {exercise['category']}")
                st.write(f"**Target Emotion:** {exercise['target_emotion']}")
                
                st.markdown("### Text to Read:")
                st.info(exercise['text_content'])
                exercise_text = exercise['text_content']
    
    with tab2:
        custom_text = st.text_area(
            "Enter your own text to practice",
            height=150,
            placeholder="Type or paste your own text here..."
        )
        
        if custom_text:
            exercise_id = None
            exercise_text = custom_text
    
    # Audio recorder
    st.subheader("Record Your Speech")
    audio_bytes = display_audio_recorder()
    
    # Analysis button
    if audio_bytes:
        st.success("Audio recorded successfully!")
        
        st.subheader("Your Recording")
        st.audio(audio_bytes)
        
        if st.button("Analyze My Speech"):
            with st.spinner("Analyzing your speech..."):
                # Create a file-like object from audio bytes
                audio_file = BytesIO(audio_bytes)
                
                # Analyze speech
                analysis_results = analyzer.analyze(audio_file)
                
                if analysis_results:
                    # Generate feedback
                    target_text = exercise_text if exercise_text else None
                    feedback = feedback_generator.generate(
                        analysis_results, target_text
                    )
                    
                    # Save recording to filesystem
                    filename = save_audio_file(st.session_state.user_id, audio_file)
                    
                    # Store results in database
                    recording_id = save_recording(
                        st.session_state.user_id, filename, analysis_results, feedback
                    )
                    
                    if recording_id:
                        # Display analysis results
                        st.subheader("Analysis Results")
                        display_stats_cards(analysis_results)
                        
                        # Display charts
                        tab1, tab2, tab3 = st.tabs(["Pitch", "Energy", "Emotions"])
                        
                        with tab1:
                            pitch_chart = create_pitch_chart(
                                analysis_results['pitch'], 
                                analysis_results['pitch_timestamps']
                            )
                            st.plotly_chart(pitch_chart, use_container_width=True)
                        
                        with tab2:
                            energy_chart = create_energy_chart(
                                analysis_results['energy'], 
                                analysis_results['energy_timestamps']
                            )
                            st.plotly_chart(energy_chart, use_container_width=True)
                        
                        with tab3:
                            emotion_chart = create_emotion_chart(analysis_results['emotions'])
                            st.plotly_chart(emotion_chart, use_container_width=True)
                        
                        # Display feedback
                        st.subheader("Feedback")
                        display_feedback(feedback)
                    else:
                        st.error("Error storing analysis results")
                else:
                    st.error("Error analyzing speech")
    else:
        st.info("Record your speech to get feedback")

def display_exercises_page():
    """Display the exercises page"""
    st.title("Practice Exercises")
    
    # Filter by category
    exercises = get_all_exercises()
    
    if not exercises:
        st.warning("No exercises found")
        return
    
    # Get unique categories
    categories = sorted(list(set(ex['category'] for ex in exercises)))
    
    # Filter controls
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_category = st.selectbox(
            "Filter by category",
            ["All"] + categories
        )
    
    with col2:
        difficulty_options = ["All", "Beginner", "Intermediate", "Advanced"]
        selected_difficulty = st.selectbox(
            "Filter by difficulty",
            difficulty_options
        )
    
    # Filter exercises
    filtered_exercises = exercises
    
    if selected_category != "All":
        filtered_exercises = [ex for ex in filtered_exercises if ex['category'] == selected_category]
    
    if selected_difficulty != "All":
        filtered_exercises = [ex for ex in filtered_exercises if ex['difficulty'] == selected_difficulty]
    
    # Display exercises
    if not filtered_exercises:
        st.info("No exercises match your filters")
    else:
        for exercise in filtered_exercises:
            with st.expander(f"{exercise['title']} ({exercise['difficulty']})"):
                st.write(f"**Description:** {exercise['description']}")
                st.write(f"**Category:** {exercise['category']}")
                st.write(f"**Target Emotion:** {exercise['target_emotion']}")
                
                # Preview of text
               # Preview of text
                text = exercise['text_content']
                if len(text) > 100:
                    text = text[:100] + "..."
                st.write("**Text Preview:**")
                st.info(text)
                
                # Practice button
                st.button(
                    "Practice This Exercise",
                    key=f"practice_{exercise['id']}",
                    on_click=lambda eid=exercise['id']: set_exercise_detail(eid)
                )

def set_exercise_detail(exercise_id):
    """Set the exercise detail page for a specific exercise"""
    st.session_state.exercise_id = exercise_id
    st.session_state.page = 'exercise_detail'

def display_exercise_detail_page(analyzer, feedback_generator):
    """Display the exercise detail page"""
    if not hasattr(st.session_state, 'exercise_id'):
        st.error("No exercise selected")
        st.button("Back to Exercises", on_click=lambda: setattr(st.session_state, 'page', 'exercises'))
        return
    
    exercise = get_exercise(st.session_state.exercise_id)
    
    if not exercise:
        st.error("Exercise not found")
        st.button("Back to Exercises", on_click=lambda: setattr(st.session_state, 'page', 'exercises'))
        return
    
    st.title(exercise['title'])
    
    # Back button
    st.button("← Back to Exercises", on_click=lambda: setattr(st.session_state, 'page', 'exercises'))
    
    # Exercise details
    st.subheader("Exercise Details")
    st.write(f"**Description:** {exercise['description']}")
    st.write(f"**Category:** {exercise['category']}")
    st.write(f"**Difficulty:** {exercise['difficulty']}")
    st.write(f"**Target Emotion:** {exercise['target_emotion']}")
    
    # Text to read
    st.subheader("Text to Read:")
    st.info(exercise['text_content'])
    
    # Audio recorder
    st.subheader("Record Your Speech")
    audio_bytes = display_audio_recorder()
    
    # Analysis button
    if audio_bytes:
        st.success("Audio recorded successfully!")
        
        st.subheader("Your Recording")
        st.audio(audio_bytes)
        
        if st.button("Analyze My Speech"):
            with st.spinner("Analyzing your speech..."):
                # Create a file-like object from audio bytes
                audio_file = BytesIO(audio_bytes)
                
                # Analyze speech
                analysis_results = analyzer.analyze(audio_file)
                
                if analysis_results:
                    # Generate feedback
                    target_text = exercise['text_content']
                    feedback = feedback_generator.generate(
                        analysis_results, target_text
                    )
                    
                    # Save recording to filesystem
                    filename = save_audio_file(st.session_state.user_id, audio_file)
                    
                    # Store results in database
                    recording_id = save_recording(
                        st.session_state.user_id, filename, analysis_results, feedback
                    )
                    
                    if recording_id:
                        # Display analysis results
                        st.subheader("Analysis Results")
                        display_stats_cards(analysis_results)
                        
                        # Display charts
                        tab1, tab2, tab3 = st.tabs(["Pitch", "Energy", "Emotions"])
                        
                        with tab1:
                            pitch_chart = create_pitch_chart(
                                analysis_results['pitch'], 
                                analysis_results['pitch_timestamps']
                            )
                            st.plotly_chart(pitch_chart, use_container_width=True)
                        
                        with tab2:
                            energy_chart = create_energy_chart(
                                analysis_results['energy'], 
                                analysis_results['energy_timestamps']
                            )
                            st.plotly_chart(energy_chart, use_container_width=True)
                        
                        with tab3:
                            emotion_chart = create_emotion_chart(analysis_results['emotions'])
                            st.plotly_chart(emotion_chart, use_container_width=True)
                        
                        # Display feedback
                        st.subheader("Feedback")
                        display_feedback(feedback)
                    else:
                        st.error("Error storing analysis results")
                else:
                    st.error("Error analyzing speech")

def display_recordings_page():
    """Display the recordings page"""
    st.title("My Practice Recordings")
    
    # Get user recordings
    recordings = get_user_recordings(st.session_state.user_id, limit=20)
    
    if not recordings:
        st.info("You haven't made any recordings yet.")
        st.button("Start Practicing", on_click=lambda: setattr(st.session_state, 'page', 'practice'))
        return
    
    # Display recordings
    for recording in recordings:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            created_at = datetime.strptime(recording['created_at'], '%Y-%m-%d %H:%M:%S')
            st.write(f"**{created_at.strftime('%b %d, %Y at %I:%M %p')}**")
            
            # Display emotion and truncated transcription if available
            emotion = recording['emotional_tone'].capitalize() if recording['emotional_tone'] else 'Unknown'
            st.write(f"Primary emotion: {emotion}")
            
            if recording['text_content']:
                text = recording['text_content']
                if len(text) > 100:
                    text = text[:100] + "..."
                st.write(text)
        
        with col2:
            st.metric(
                "Score",
                f"{recording['expressiveness_score']:.1f}%",
                delta=None
            )
        
        with col3:
            # Audio player
            audio_path = UPLOAD_FOLDER / recording['filename']
            if audio_path.exists():
                st.audio(str(audio_path))
            
            # View feedback button
            st.button(
                "View Feedback",
                key=f"view_{recording['id']}",
                on_click=lambda rid=recording['id']: set_recording_detail(rid)
            )
        
        st.markdown("---")

def display_voice_enrollment_page(analyzer):
    """Display the voice enrollment page"""
    st.title("Voice Model Enrollment")
    
    # Check if user already has a voice model
    user = get_user_by_username('username')  # TODO: Get actual username
    
    if user and user.has_voice_model:
        st.success("You already have a voice model! You can re-enroll if you want to update it.")
    
    st.write("""
    Record a 1-2 minute sample of your voice speaking naturally.
    This will be used to create a voice model that can help enhance your speech delivery.
    """)
    
    st.info("Speak clearly and use your natural speaking voice. Read a paragraph or tell a story.")
    
    # Audio recorder
    st.subheader("Record Your Voice Sample")
    audio_bytes = display_audio_recorder()
    
    if audio_bytes:
        st.success("Voice sample recorded successfully!")
        
        st.subheader("Your Recording")
        st.audio(audio_bytes)
        
        # In a real implementation, we would validate the length here
        audio_file = BytesIO(audio_bytes)
        
        if st.button("Create Voice Model"):
            with st.spinner("Creating your voice model... This may take a minute."):
                # In a real implementation, this would create an actual voice model
                # Here we'll analyze the audio to ensure it's valid
                analysis_results = analyzer.analyze(audio_file)
                
                if analysis_results and analysis_results.get('duration', 0) >= 10:  # Minimum 10 seconds
                    # Update user record to indicate they have a voice model
                    update_voice_model_status(st.session_state.user_id, True)
                    
                    st.success("Voice model created successfully!")
                    st.info("Your voice model will be used to provide enhanced feedback in future practice sessions.")
                else:
                    st.error("Error creating voice model. Please ensure your recording is at least 10 seconds long.")

def display_settings_page():
    """Display the settings page"""
    st.title("Settings")
    
    # Get user data
    user = get_user_by_id(st.session_state.user_id)
    
    if not user:
        st.error("Error loading user data")
        return
    
    # Profile section
    st.subheader("Profile")
    
    with st.form("profile_form"):
        st.write(f"**Username:** {user.username}")
        email = st.text_input("Email", user.email)
        
        update_profile = st.form_submit_button("Update Profile")
        
        if update_profile:
            if email and email != user.email:
                if update_user(st.session_state.user_id, email=email):
                    st.success("Profile updated successfully!")
                else:
                    st.error("Error updating profile")
    
    # Password section
    st.subheader("Change Password")
    
    with st.form("password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        update_password = st.form_submit_button("Change Password")
        
        if update_password:
            if not current_password or not new_password or not confirm_password:
                st.error("All fields are required")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            else:
                # Verify current password
                if login_user(user.username, current_password):
                    if update_user(st.session_state.user_id, password_hash=new_password):
                        st.success("Password updated successfully!")
                    else:
                        st.error("Error updating password")
                else:
                    st.error("Current password is incorrect")
    
    # Voice model section
    st.subheader("Voice Model")
    
    if user.has_voice_model:
        st.success("You have a voice model")
        if st.button("Reset Voice Model"):
            update_voice_model_status(st.session_state.user_id, False)
            st.success("Voice model reset successfully")
            st.rerun()
    else:
        st.info("You don't have a voice model yet")
        if st.button("Create Voice Model"):
            st.session_state.page = 'voice_enrollment'
            st.rerun()