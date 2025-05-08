import streamlit as st
import os
import torch
from pathlib import Path
import time
import tempfile
import subprocess
import sys
import librosa
import numpy as np
from scipy.io import wavfile

# Define paths
MODELS_DIR = Path("models")
VOICE_MODELS_DIR = Path("voice_models")
CLONED_AUDIO_DIR = Path("cloned_audio")

# Create directories
MODELS_DIR.mkdir(exist_ok=True)
VOICE_MODELS_DIR.mkdir(exist_ok=True)
CLONED_AUDIO_DIR.mkdir(exist_ok=True)

class VoiceModelManager:
    """Simplified voice cloning using compatible libraries"""
    
    def __init__(self):
        self.user_models = {}
        self.load_available_models()
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
    def load_available_models(self):
        """Load existing voice models"""
        if not VOICE_MODELS_DIR.exists():
            return
            
        for user_dir in VOICE_MODELS_DIR.iterdir():
            if user_dir.is_dir():
                user_id = user_dir.name
                self.user_models[user_id] = []
                for model_path in user_dir.glob("*.pt"):
                    self.user_models[user_id].append({
                        "name": model_path.stem,
                        "path": str(model_path),
                        "created_at": model_path.stat().st_mtime
                    })
    
    def create_voice_model(self, user_id, audio_file, model_name=None):
        """Create voice model from audio"""
        if not model_name:
            model_name = f"voice_{int(time.time())}"
        
        model_path = VOICE_MODELS_DIR / str(user_id) / f"{model_name}.pt"
        model_path.parent.mkdir(exist_ok=True)
        
        try:
            # Save temporary audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp.write(audio_file.read())
                tmp_path = tmp.name
            
            # Extract features
            success, features = self._extract_features(tmp_path)
            if success:
                torch.save(features, model_path)
                model_info = {
                    "name": model_name,
                    "path": str(model_path),
                    "created_at": time.time()
                }
                if user_id not in self.user_models:
                    self.user_models[user_id] = []
                self.user_models[user_id].append(model_info)
                return model_info
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        return None
    
    def _extract_features(self, audio_path):
        """Extract voice features using librosa"""
        try:
            y, sr = librosa.load(audio_path, sr=16000)
            mfcc = librosa.feature.mfcc(
                y=y, sr=sr, n_mfcc=13,
                n_fft=2048, hop_length=512
            )
            return True, torch.from_numpy(mfcc).float()
        except Exception as e:
            st.error(f"Feature extraction failed: {str(e)}")
            return False, None
    
    def clone_voice(self, user_id, model_name, source_audio_path):
        """Basic voice cloning implementation"""
        model_path = VOICE_MODELS_DIR / str(user_id) / f"{model_name}.pt"
        if not model_path.exists():
            return None
        
        output_path = CLONED_AUDIO_DIR / str(user_id) / f"clone_{int(time.time())}.wav"
        output_path.parent.mkdir(exist_ok=True)
        
        try:
            # Load model and source audio
            features = torch.load(model_path)
            y, sr = librosa.load(source_audio_path, sr=16000)
            
            # Simple pitch shifting (demo only)
            y_shifted = librosa.effects.pitch_shift(
                y, sr=sr, n_steps=2  # Small pitch adjustment
            )
            
            # Save modified audio
            wavfile.write(output_path, sr, y_shifted)
            return str(output_path)
        except Exception as e:
            st.error(f"Cloning failed: {str(e)}")
            return None

def check_dependencies():
    """Verify required packages are installed"""
    try:
        import importlib
        for pkg in ['torch', 'torchaudio', 'librosa', 'numpy']:
            importlib.import_module(pkg)
        return True
    except ImportError:
        return False

def voice_cloning_ui():
    """Streamlit UI for voice cloning"""
    st.sidebar.title("Voice Cloning")
    
    if not hasattr(st.session_state, 'user_id'):
        st.sidebar.warning("Please log in first")
        return
    
    if not check_dependencies():
        st.sidebar.warning("Missing required packages")
        if st.sidebar.button("Install Dependencies"):
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "torch", "torchaudio", "librosa", "numpy"
                ])
                st.sidebar.success("Please restart the app")
            except:
                st.sidebar.error("Installation failed")
        return
    
    manager = VoiceModelManager()
    user_id = str(st.session_state.user_id)
    
    # Voice model creation
    st.sidebar.subheader("Create Voice Model")
    audio_file = st.sidebar.file_uploader(
        "Upload voice sample", 
        type=["wav", "mp3", "mp4", "ogg"]
    )
    if audio_file and st.sidebar.button("Create Model"):
        with st.spinner("Creating voice model..."):  # Fixed spinner location
            model = manager.create_voice_model(user_id, audio_file)
            if model:
                st.sidebar.success(f"Created model: {model['name']}")
            else:
                st.sidebar.error("Failed to create model")
    
    # Voice cloning
    st.sidebar.subheader("Clone Audio")
    if user_id not in manager.user_models or not manager.user_models[user_id]:
        st.sidebar.info("No voice models available")
    else:
        model_name = st.sidebar.selectbox(
            "Select your voice model",
            [m["name"] for m in manager.user_models[user_id]]
        )
        
        source_audio = st.sidebar.file_uploader(
            "Audio to clone", 
            type=["wav", "mp3", "mp4", "ogg"]
        )
        
        if source_audio and st.sidebar.button("Clone Voice"):
            with st.spinner("Cloning voice..."):  # Fixed spinner location
                # Save temp file
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(source_audio.read())
                    tmp_path = tmp.name
                
                try:
                    output_path = manager.clone_voice(user_id, model_name, tmp_path)
                    if output_path:
                        st.sidebar.success("Cloning complete!")
                        st.sidebar.audio(output_path)
                    else:
                        st.sidebar.error("Cloning failed")
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

def integrate_voice_cloning():
    """Main integration point"""
    try:
        voice_cloning_ui()
    except Exception as e:
        st.error(f"Voice cloning error: {str(e)}")