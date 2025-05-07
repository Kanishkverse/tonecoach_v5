import numpy as np
import librosa
import librosa.display
import soundfile as sf
import os
import time
from io import BytesIO
import tempfile
import torch
from transformers import pipeline, AutoProcessor, AutoModelForSpeechSeq2Seq
import streamlit as st
from pydub import AudioSegment
import scipy  # Add this import to ensure compatibility

# Add this compatibility function at the top of the file
def get_hann_window(length):
    """
    Compatibility function for different scipy versions
    """
    try:
        # Try newer scipy versions
        return scipy.signal.windows.hann(length)
    except AttributeError:
        try:
            # Try older scipy versions
            return scipy.signal.hann(length)
        except AttributeError:
            # Fallback implementation if neither is available
            import numpy as np
            return 0.5 * (1 - np.cos(2 * np.pi * np.arange(length) / (length - 1)))

# Patch librosa's beat.py function
original_beat_track = librosa.beat.beat_track

def patched_beat_track(*args, **kwargs):
    """
    Patch for librosa's beat_track function to handle different scipy versions
    """
    try:
        return original_beat_track(*args, **kwargs)
    except AttributeError as e:
        if "module 'scipy.signal' has no attribute 'hann'" in str(e):
            # Monkey patch scipy.signal.hann temporarily
            if not hasattr(scipy.signal, 'hann'):
                scipy.signal.hann = get_hann_window
            return original_beat_track(*args, **kwargs)
        else:
            raise

# Apply the patch
librosa.beat.beat_track = patched_beat_track

class SpeechAnalyzer:
    # Class variables for cached models
    processor = None
    model = None
    emotion_classifier = None
    
    def __init__(self):
        # Initialize speech-to-text model
        self.init_stt_model()
        
        # Initialize emotion detection model
        self.init_emotion_model()
    
    @staticmethod
    @st.cache_resource
    def load_stt_model():
        """Initialize speech-to-text model with caching"""
        try:
            # Use a smaller, faster model for demo purposes
            model_id = "openai/whisper-small"
            processor = AutoProcessor.from_pretrained(model_id)
            model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id)
            
            return processor, model
        except Exception as e:
            st.error(f"Error initializing speech-to-text model: {e}")
            return None, None
    
    def init_stt_model(self):
        """Initialize speech-to-text model"""
        SpeechAnalyzer.processor, SpeechAnalyzer.model = SpeechAnalyzer.load_stt_model()
        self.processor = SpeechAnalyzer.processor
        self.model = SpeechAnalyzer.model
    
    @staticmethod
    @st.cache_resource
    def load_emotion_classifier():
        """Initialize emotion classifier with caching"""
        try:
            emotion_classifier = pipeline(
                "text-classification", 
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None
            )
            return emotion_classifier
        except Exception as e:
            st.error(f"Error initializing emotion classifier: {e}")
            return None
    
    def init_emotion_model(self):
        """Initialize emotion detection model"""
        SpeechAnalyzer.emotion_classifier = SpeechAnalyzer.load_emotion_classifier()
        self.emotion_classifier = SpeechAnalyzer.emotion_classifier
    
    def analyze(self, audio_file):
        """
        Analyze speech features from an audio file
        
        Args:
            audio_file: A file-like object containing audio data
            
        Returns:
            Dictionary containing analysis results
        """
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_file.getvalue())
            temp_path = temp_file.name
        
        try:
            # Convert to .wav with correct parameters if needed
            try:
                audio_segment = AudioSegment.from_file(temp_path)
                if audio_segment.channels > 1:
                    audio_segment = audio_segment.set_channels(1)
                if audio_segment.frame_rate != 16000:
                    audio_segment = audio_segment.set_frame_rate(16000)
                audio_segment.export(temp_path, format="wav")
            except Exception as e:
                st.warning(f"Audio conversion warning: {e}. Proceeding with original file.")
            
            # Load audio
            audio, sr = librosa.load(temp_path, sr=22050)
            
            # Trim silence
            audio, _ = librosa.effects.trim(audio, top_db=20)
            
            # Transcribe audio
            transcription = self.transcribe_audio(temp_path)
            
            # Calculate pitch (fundamental frequency)
            pitch, voiced_flag, voiced_probs = librosa.pyin(
                audio, 
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7'),
                sr=sr,
                frame_length=2048,
                hop_length=512
            )
            
            # Calculate energy/volume
            energy = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
            
            # Calculate speech rate
            onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
            tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            
            # Extract syllable information for speech rate
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            mfcc_delta = librosa.feature.delta(mfcc)
            onset_frames = librosa.onset.onset_detect(
                onset_envelope=onset_env,
                sr=sr,
                units='frames'
            )
            estimated_syllables = len(onset_frames)
            duration = len(audio) / sr
            speech_rate = estimated_syllables / duration if duration > 0 else 0
            
            # Calculate pitch variability (removing NaN values)
            valid_pitch = pitch[~np.isnan(pitch)]
            pitch_variability = np.std(valid_pitch) if len(valid_pitch) > 0 else 0
            
            # Calculate energy variability
            energy_variability = np.std(energy)
            
            # Detect pauses
            energy_threshold = 0.01 * np.max(energy)
            is_pause = energy < energy_threshold
            pause_frames = np.sum(is_pause)
            pause_ratio = pause_frames / len(energy)
            
            # Detect emphasis
            emphasis_threshold = 0.8 * np.max(energy)
            is_emphasis = energy > emphasis_threshold
            emphasis_count = np.sum(is_emphasis)
            emphasis_ratio = emphasis_count / len(energy)
            
            # Emotion detection
            emotions, primary_emotion = self.detect_emotion(transcription)
            
            # Calculate expressiveness score
            expressiveness_score = self.calculate_expressiveness_score(
                pitch_variability, energy_variability, speech_rate, pause_ratio,
                emotions.get(primary_emotion, 0.0) if emotions else 0.5
            )
            
            # Convert time series to lists for visualization
            timestamps = librosa.times_like(pitch, sr=sr, hop_length=512)
            
            # Clean up
            os.unlink(temp_path)
            
            return {
                'pitch': valid_pitch.tolist() if len(valid_pitch) > 0 else [],
                'pitch_timestamps': timestamps.tolist(),
                'energy': energy.tolist(),
                'energy_timestamps': librosa.times_like(energy, sr=sr, hop_length=512).tolist(),
                'pitch_variability': float(pitch_variability),
                'energy_variability': float(energy_variability),
                'speech_rate': float(speech_rate),
                'tempo': float(tempo),
                'pause_ratio': float(pause_ratio),
                'emphasis_ratio': float(emphasis_ratio),
                'duration': float(duration),
                'estimated_syllables': int(estimated_syllables),
                'transcription': transcription,
                'emotions': emotions,
                'primary_emotion': primary_emotion,
                'expressiveness_score': expressiveness_score
            }
            
        except Exception as e:
            st.error(f"Error analyzing speech: {e}")
            os.unlink(temp_path)
            return None
    
    def transcribe_audio(self, audio_path):
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            String containing transcribed text
        """
        if not self.processor or not self.model:
            return "Transcription unavailable (model not loaded)"
        
        try:
            # Load audio
            audio_array, sampling_rate = librosa.load(audio_path, sr=16000)
            
            # Process audio
            input_features = self.processor(
                audio_array, 
                sampling_rate=sampling_rate, 
                return_tensors="pt"
            ).input_features
            
            # Generate transcription
            with torch.no_grad():
                predicted_ids = self.model.generate(input_features)
            
            # Decode transcription
            transcription = self.processor.batch_decode(
                predicted_ids, 
                skip_special_tokens=True
            )[0]
            
            return transcription
        except Exception as e:
            st.warning(f"Transcription error: {e}")
            return "Transcription failed"
    
    def detect_emotion(self, text):
        """
        Detect emotions in text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of emotions and scores, and the primary emotion
        """
        if not self.emotion_classifier or not text:
            return {"neutral": 1.0}, "neutral"
        
        try:
            emotion_results = self.emotion_classifier(text)
            emotions = {item['label']: item['score'] for item in emotion_results[0]}
            primary_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            return emotions, primary_emotion
        except Exception as e:
            st.warning(f"Emotion detection error: {e}")
            return {"neutral": 1.0}, "neutral"
    
    def calculate_expressiveness_score(self, pitch_var, energy_var, speech_rate, pause_ratio, emotion_confidence=0.5):
        """
        Calculate overall expressiveness score
        
        Args:
            pitch_var: Pitch variability
            energy_var: Energy variability
            speech_rate: Speech rate in syllables per second
            pause_ratio: Ratio of pauses to total frames
            emotion_confidence: Confidence in primary emotion detection
            
        Returns:
            Expressiveness score (0-100)
        """
        # Normalize pitch variability (0-50 range to 0-1)
        pitch_score = min(1.0, pitch_var / 50.0)
        
        # Normalize energy variability (0-0.2 range to 0-1)
        energy_score = min(1.0, energy_var / 0.2)
        
        # Normalize speech rate (optimal around 3-4 syllables/sec)
        if speech_rate < 2.0:
            rate_score = speech_rate / 2.0  # Linear from 0 to 1.0
        elif speech_rate > 5.0:
            rate_score = max(0, 1.0 - (speech_rate - 5.0) / 3.0)  # Linear decrease after 5.0
        else:
            # Peak at 3.5 syllables/second
            rate_score = 1.0 - abs(speech_rate - 3.5) / 1.5
        
        # Normalize pause ratio (optimal around 0.15-0.25)
        if pause_ratio < 0.15:
            pause_score = pause_ratio / 0.15  # Linear increase
        elif pause_ratio > 0.3:
            pause_score = max(0, 1.0 - (pause_ratio - 0.3) / 0.2)  # Linear decrease
        else:
            pause_score = 1.0
        
        # Normalize emotion confidence (already in 0-1 range)
        emotion_score = emotion_confidence
        
        # Weights for different components
        weights = {
            'pitch_variability': 0.35,
            'energy_variability': 0.25,
            'speech_rate': 0.15,
            'pause_ratio': 0.15,
            'emotion_confidence': 0.10
        }
        
        # Calculate weighted score
        weighted_score = (
            weights['pitch_variability'] * pitch_score +
            weights['energy_variability'] * energy_score +
            weights['speech_rate'] * rate_score +
            weights['pause_ratio'] * pause_score +
            weights['emotion_confidence'] * emotion_score
        )
        
        # Convert to 0-100 scale
        return min(100, max(0, weighted_score * 100))