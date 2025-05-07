import os
import json
import uuid
from pathlib import Path
from datetime import datetime
import shutil

# Path to upload directory
UPLOAD_FOLDER = Path("uploads")
BENCHMARK_FOLDER = Path("benchmarks")

# Ensure directories exist
UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)
BENCHMARK_FOLDER.mkdir(exist_ok=True, parents=True)

def save_audio_file(user_id, audio_data):
    """
    Save audio data to file
    
    Args:
        user_id: User ID
        audio_data: Audio data (file-like object or bytes)
        
    Returns:
        Filename of saved audio
    """
    # Create user directory if it doesn't exist
    user_dir = UPLOAD_FOLDER / str(user_id)
    user_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.wav"
    filepath = user_dir / filename
    
    # Save audio data to file
    if hasattr(audio_data, 'read'):
        # It's a file-like object
        with open(filepath, 'wb') as f:
            f.write(audio_data.read())
    else:
        # It's bytes
        with open(filepath, 'wb') as f:
            f.write(audio_data)
    
    # Return relative path from UPLOAD_FOLDER
    return str(Path(str(user_id)) / filename)

def save_benchmark_audio(exercise_id, audio_data, metadata=None):
    """
    Save benchmark audio data for an exercise
    
    Args:
        exercise_id: Exercise ID
        audio_data: Audio data (file-like object or bytes)
        metadata: Dictionary containing metadata about the benchmark recording
        
    Returns:
        Path to saved benchmark audio
    """
    # Create exercise directory if it doesn't exist
    exercise_dir = BENCHMARK_FOLDER / f"exercise_{exercise_id}"
    exercise_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate filename
    filename = f"benchmark_{exercise_id}.wav"
    filepath = exercise_dir / filename
    
    # Save audio data to file
    if hasattr(audio_data, 'read'):
        # It's a file-like object
        with open(filepath, 'wb') as f:
            f.write(audio_data.read())
    else:
        # It's bytes
        with open(filepath, 'wb') as f:
            f.write(audio_data)
    
    # Save metadata if provided
    if metadata:
        metadata_path = exercise_dir / f"benchmark_{exercise_id}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    # Return absolute path to benchmark audio
    return str(filepath.absolute())

def delete_audio_file(filepath):
    """
    Delete audio file
    
    Args:
        filepath: Path to audio file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.remove(filepath)
        return True
    except Exception as e:
        print(f"Error deleting audio file: {e}")
        return False

def get_benchmark_audio_path(exercise_id):
    """
    Get path to benchmark audio for an exercise
    
    Args:
        exercise_id: Exercise ID
        
    Returns:
        Path to benchmark audio or None if not found
    """
    exercise_dir = BENCHMARK_FOLDER / f"exercise_{exercise_id}"
    filepath = exercise_dir / f"benchmark_{exercise_id}.wav"
    
    if filepath.exists():
        return str(filepath.absolute())
    
    return None

def get_benchmark_metadata(exercise_id):
    """
    Get metadata for benchmark audio
    
    Args:
        exercise_id: Exercise ID
        
    Returns:
        Dictionary containing metadata or None if not found
    """
    exercise_dir = BENCHMARK_FOLDER / f"exercise_{exercise_id}"
    metadata_path = exercise_dir / f"benchmark_{exercise_id}_metadata.json"
    
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading benchmark metadata: {e}")
    
    return None

def create_admin_tool():
    """
    Create benchmark recordings management
    
    This function would provide functionality for admin users to:
    1. Upload benchmark recordings for exercises
    2. Process and analyze benchmark recordings
    3. Associate benchmark recordings with exercises in the database
    
    For actual implementation, this would be a separate admin interface
    """
    pass