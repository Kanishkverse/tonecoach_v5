import streamlit as st
import os
import time
from pathlib import Path
import json
import tempfile
import requests
from io import BytesIO
import threading

# Define directories for user files
VOICE_MODELS_DIR = Path("voice_models")
CLONED_AUDIO_DIR = Path("cloned_audio")
CONFIG_DIR = Path("config")

# Create necessary directories
VOICE_MODELS_DIR.mkdir(exist_ok=True)
CLONED_AUDIO_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# ElevenLabs API base URL
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Voice settings
DEFAULT_VOICE_SETTINGS = {
    "stability": 0.5,
    "similarity_boost": 0.75
}

# Models for text-to-speech
ELEVENLABS_MODELS = {
    "eleven_multilingual_v2": "Multilingual (29 languages)",
    "eleven_turbo_v2": "English (Fastest)",
    "eleven_monolingual_v1": "English (Best quality)"
}

class ElevenLabsVoiceCloner:
    """Handle voice cloning and TTS using ElevenLabs API"""
    
    def __init__(self):
        self.api_key = self._load_api_key()
        self.user_voices = {}
        self.load_available_voices()
    
    def _load_api_key(self):
        """Load API key from config"""
        config_path = CONFIG_DIR / "elevenlabs_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                return config.get("api_key", "")
            except Exception as e:
                print(f"Error loading API key: {e}")
        return ""
    
    def save_api_key(self, api_key):
        """Save API key to config"""
        config = {"api_key": api_key}
        with open(CONFIG_DIR / "elevenlabs_config.json", "w") as f:
            json.dump(config, f, indent=2)
        self.api_key = api_key
        return True
    
    def load_available_voices(self):
        """Load available voices from ElevenLabs API"""
        if not self.api_key:
            return
            
        try:
            # Get voices from ElevenLabs API
            response = requests.get(
                f"{ELEVENLABS_API_URL}/voices",
                headers={"xi-api-key": self.api_key}
            )
            
            if response.status_code == 200:
                voices_data = response.json()
                
                # Store voices by category
                for voice in voices_data.get("voices", []):
                    user_id = voice.get("category", "unknown")
                    
                    if user_id not in self.user_voices:
                        self.user_voices[user_id] = []
                    
                    voice_info = {
                        "id": voice.get("voice_id"),
                        "name": voice.get("name"),
                        "description": voice.get("description", ""),
                        "category": voice.get("category"),
                        "created_at": voice.get("created_at", time.time())
                    }
                    
                    self.user_voices[user_id].append(voice_info)
        except Exception as e:
            print(f"Error loading voices: {e}")
    
    def clone_voice(self, name, description, audio_file):
        """
        Clone a voice using ElevenLabs API
        
        Args:
            name: Name for the cloned voice
            description: Description for the cloned voice
            audio_file: Audio file to use for voice cloning
            
        Returns:
            Voice ID if successful, None if failed
        """
        if not self.api_key:
            return None, "API key not set"
        
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                if hasattr(audio_file, 'getvalue'):
                    temp_file.write(audio_file.getvalue())
                elif hasattr(audio_file, 'read'):
                    temp_file.write(audio_file.read())
                else:
                    temp_file.write(audio_file)
                
                temp_path = temp_file.name
            
            # Prepare files for the request
            files = {
                'files': (os.path.basename(temp_path), open(temp_path, 'rb'), 'audio/wav'),
                'name': (None, name),
                'description': (None, description)
            }
            
            # Clone voice using ElevenLabs API
            response = requests.post(
                f"{ELEVENLABS_API_URL}/voices/add",
                headers={"xi-api-key": self.api_key},
                files=files
            )
            
            # Clean up the temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
            
            if response.status_code == 200:
                voice_data = response.json()
                voice_id = voice_data.get("voice_id")
                
                # Refresh available voices
                self.load_available_voices()
                
                return voice_id, "Voice cloned successfully"
            else:
                return None, f"Error cloning voice: {response.text}"
        
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def get_user_voices(self, category="cloned"):
        """Get voices for a specific category"""
        return self.user_voices.get(category, [])
    
    def clone_benchmark_with_voice(self, voice_id, voice_name, benchmark_path):
        """
        Clone a benchmark recording using ElevenLabs voice
        
        Args:
            voice_id: ElevenLabs voice ID
            voice_name: Name of the voice for reference
            benchmark_path: Path to the benchmark audio file
            
        Returns:
            Path to the cloned audio or None if failed
        """
        if not self.api_key:
            return None, "API key not set"
        
        if not os.path.exists(benchmark_path):
            return None, "Benchmark audio file not found"
        
        # Create output directory if it doesn't exist
        output_dir = CLONED_AUDIO_DIR / "elevenlabs"
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Generate output filename
        timestamp = int(time.time())
        output_path = output_dir / f"cloned_benchmark_{voice_name}_{timestamp}.mp3"
        
        # First convert the benchmark to text using a speech-to-text service
        # For this example, we'll simulate this step
        # In a real implementation, you would use a STT service
        
        try:
            # Get the text content from the exercise database
            # This is a placeholder - in reality you would extract text from benchmark audio
            # using a speech-to-text service or get it from the exercise database
            
            from database.db_utils import get_exercise_by_benchmark_path
            exercise = get_exercise_by_benchmark_path(benchmark_path)
            
            if not exercise:
                return None, "Could not find exercise for benchmark"
            
            text_content = exercise.get('text_content', '')
            
            if not text_content:
                return None, "No text content available for benchmark"
            
            # Use ElevenLabs to generate speech with the cloned voice
            response = self._text_to_speech(voice_id, text_content)
            
            if response:
                # Save the audio
                with open(output_path, 'wb') as f:
                    f.write(response)
                
                return str(output_path), "Success"
            else:
                return None, "Failed to generate speech"
        
        except Exception as e:
            error_msg = f"Error cloning benchmark: {str(e)}"
            print(error_msg)
            return None, error_msg
    
    def _text_to_speech(self, voice_id, text, model_id="eleven_multilingual_v2"):
        """
        Convert text to speech using ElevenLabs API
        
        Args:
            voice_id: ElevenLabs voice ID
            text: Text to convert to speech
            model_id: Model ID to use for TTS
            
        Returns:
            Audio bytes if successful, None if failed
        """
        if not self.api_key:
            return None
        
        try:
            # Prepare request data
            data = {
                "text": text,
                "model_id": model_id,
                "voice_settings": DEFAULT_VOICE_SETTINGS
            }
            
            # Call ElevenLabs API
            response = requests.post(
                f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}",
                headers={"xi-api-key": self.api_key, "Content-Type": "application/json"},
                json=data
            )
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Error generating speech: {response.text}")
                return None
        
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            return None

def setup_elevenlabs_api():
    """
    Set up ElevenLabs API
    Check if API key is set and prompt user if not
    """
    voice_cloner = ElevenLabsVoiceCloner()
    
    if not voice_cloner.api_key:
        st.sidebar.warning("ElevenLabs API key not set")
        
        with st.sidebar.form("api_key_form"):
            api_key = st.text_input("Enter your ElevenLabs API key:", type="password")
            submitted = st.form_submit_button("Save API Key")
            
            if submitted and api_key:
                if voice_cloner.save_api_key(api_key):
                    st.success("API key saved successfully!")
                    # Reload the page to apply the new API key
                    st.rerun()
            
            st.markdown("""
            **How to get an API key:**
            1. Create an account on [ElevenLabs](https://elevenlabs.io)
            2. Go to your profile settings
            3. Copy your API key
            """)
        
        return False
    
    return True

def display_voice_cloning_sidebar():
    """Display the voice cloning sidebar in ToneCoach"""
    st.sidebar.title("Voice Cloning Tools")
    
    # Initialize voice cloner
    voice_cloner = ElevenLabsVoiceCloner()
    
    # Check if user is logged in
    if not hasattr(st.session_state, 'user_id') or st.session_state.user_id is None:
        st.sidebar.warning("Please log in to use voice cloning features")
        return
    
    # Check API setup
    api_ready = setup_elevenlabs_api()
    
    if not api_ready:
        return
    
    # Load user voices
    cloned_voices = voice_cloner.get_user_voices("cloned")
    
    # Voice cloning section
    st.sidebar.subheader("Create Voice Clone")
    
    # Audio input for voice cloning
    voice_sample = st.sidebar.file_uploader("Upload voice sample (15-30 seconds)", 
                                           type=["wav", "mp3", "ogg"], 
                                           key="voice_sample")
    
    # Alternative: Record voice directly
    use_recorder = st.sidebar.checkbox("Record voice sample instead")
    
    recorded_audio = None
    if use_recorder:
        st.sidebar.write("Record a 15-30 second sample of your voice:")
        recorded_audio = st.sidebar.audio_input("Click to record", key="voice_recorder")
    
    # Voice name and description
    voice_name = st.sidebar.text_input("Voice name (required)")
    voice_description = st.sidebar.text_area("Voice description (optional)", 
                                            "My custom voice for ToneCoach")
    
    if st.sidebar.button("Create Voice Clone"):
        if not voice_name:
            st.sidebar.error("Please provide a name for your voice")
            return
        
        audio_to_use = recorded_audio if use_recorder else voice_sample
        
        if not audio_to_use:
            st.sidebar.error("Please upload or record a voice sample")
            return
        
        # Show a spinner while cloning
        with st.spinner("Creating voice clone... This may take a minute."):
            voice_id, message = voice_cloner.clone_voice(
                voice_name, voice_description, audio_to_use
            )
            
            if voice_id:
                st.sidebar.success(f"Voice '{voice_name}' cloned successfully!")
                # Refresh the voices list
                voice_cloner.load_available_voices()
                # Trigger a page refresh to show the new voice
                st.rerun()
            else:
                st.sidebar.error(f"Voice cloning failed: {message}")
    
    # Benchmark cloning section
    st.sidebar.subheader("Clone Benchmark with Your Voice")
    
    # Refresh cloned voices
    cloned_voices = voice_cloner.get_user_voices("cloned")
    
    if not cloned_voices:
        st.sidebar.info("No voice clones available. Create a voice clone first.")
    else:
        # Select voice
        voice_options = [(voice["id"], voice["name"]) for voice in cloned_voices]
        selected_voice_tuple = st.sidebar.selectbox(
            "Select your voice clone",
            options=voice_options,
            format_func=lambda x: x[1]
        )
        
        if selected_voice_tuple:
            selected_voice_id, selected_voice_name = selected_voice_tuple
            
            # Get available exercises with benchmarks
            from database.db_utils import get_all_exercises
            exercises = get_all_exercises()
            benchmark_exercises = [ex for ex in exercises if ex.get('benchmark_audio_path')]
            
            if not benchmark_exercises:
                st.sidebar.info("No benchmark recordings available.")
            else:
                # Select exercise
                exercise_options = [(ex['id'], f"{ex['title']}") for ex in benchmark_exercises]
                selected_exercise = st.sidebar.selectbox(
                    "Select benchmark",
                    options=exercise_options,
                    format_func=lambda x: x[1]
                )
                
                if selected_exercise:
                    exercise_id, _ = selected_exercise
                    selected_ex = next((ex for ex in benchmark_exercises if ex['id'] == exercise_id), None)
                    
                    if selected_ex and selected_ex.get('benchmark_audio_path'):
                        benchmark_path = selected_ex['benchmark_audio_path']
                        
                        # Select TTS model
                        model_options = list(ELEVENLABS_MODELS.items())
                        selected_model = st.sidebar.selectbox(
                            "Select voice model",
                            options=model_options,
                            format_func=lambda x: f"{x[1]}"
                        )
                        
                        if os.path.exists(benchmark_path):
                            # Display benchmark audio
                            st.sidebar.subheader("Original Benchmark")
                            st.sidebar.audio(benchmark_path)
                            
                            if st.sidebar.button("Clone with My Voice"):
                                with st.spinner("Cloning benchmark with your voice... This may take a minute."):
                                    output_path, message = voice_cloner.clone_benchmark_with_voice(
                                        selected_voice_id, selected_voice_name, benchmark_path
                                    )
                                    
                                    if output_path:
                                        st.sidebar.success("Voice cloning successful!")
                                        st.sidebar.subheader("Cloned Benchmark")
                                        st.sidebar.audio(output_path)
                                        
                                        # Save to session state for access in other pages
                                        if not hasattr(st.session_state, 'cloned_benchmarks'):
                                            st.session_state.cloned_benchmarks = {}
                                        
                                        st.session_state.cloned_benchmarks[exercise_id] = output_path
                                    else:
                                        st.sidebar.error(f"Voice cloning failed: {message}")
                        else:
                            st.sidebar.warning("Benchmark audio file not found")

def integrate_voice_cloning():
    """
    Add voice cloning capabilities to ToneCoach
    This function should be called from the main app.py file
    """
    # Add voice cloning sidebar
    display_voice_cloning_sidebar()
    
    # If a cloned benchmark exists for the current exercise, show it
    if (hasattr(st.session_state, 'cloned_benchmarks') and 
        hasattr(st.session_state, 'exercise_id') and 
        st.session_state.exercise_id in st.session_state.cloned_benchmarks):
        
        cloned_path = st.session_state.cloned_benchmarks[st.session_state.exercise_id]
        
        if os.path.exists(cloned_path):
            st.subheader("Your Voice Clone of Benchmark")
            st.audio(cloned_path)
            st.info("This is what the benchmark would sound like with your voice. Try to match the rhythm, pauses, and emphasis while using your natural voice.")