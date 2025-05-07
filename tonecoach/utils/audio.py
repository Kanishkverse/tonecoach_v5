import os
import time
from io import BytesIO
from pathlib import Path

# Path to upload directory
UPLOAD_FOLDER = Path("uploads")

def save_audio_file(user_id, audio_file):
    """
    Save audio file to disk
    
    Args:
        user_id: User ID
        audio_file: Audio file bytes or BytesIO object
        
    Returns:
        Filename of saved file
    """
    # Ensure directory exists
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    
    # Generate a unique filename
    filename = f"{user_id}_{int(time.time())}.wav"
    file_path = UPLOAD_FOLDER / filename
    
    # Reset file pointer to beginning if it's a BytesIO object
    if isinstance(audio_file, BytesIO):
        audio_file.seek(0)
    
    # Save file to disk
    with open(file_path, "wb") as f:
        if isinstance(audio_file, BytesIO):
            f.write(audio_file.getvalue())
        else:
            f.write(audio_file)
    
    # Return the filename for database storage
    return filename

def get_audio_file_path(filename):
    """
    Get full path to audio file
    
    Args:
        filename: Filename of audio file
        
    Returns:
        Full path to audio file
    """
    return UPLOAD_FOLDER / filename

def delete_audio_file(filename):
    """
    Delete audio file from disk
    
    Args:
        filename: Filename of audio file
        
    Returns:
        True if deletion successful, False otherwise
    """
    file_path = UPLOAD_FOLDER / filename
    
    try:
        if file_path.exists():
            os.remove(file_path)
        return True
    except:
        return False