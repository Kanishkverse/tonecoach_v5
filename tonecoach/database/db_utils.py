import sqlite3
import json
from pathlib import Path
from datetime import datetime
import hashlib

# Database connection
DATABASE_PATH = Path("database/tonecoach.db")

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create database tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        has_voice_model BOOLEAN DEFAULT 0
    )
    ''')
    
    # Create recordings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recordings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        text_content TEXT,
        expressiveness_score REAL,
        pitch_variability REAL,
        energy_variability REAL,
        speech_rate REAL,
        emotional_tone TEXT,
        feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
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

def login_user(username, password):
    """
    Attempt to log in a user
    
    Args:
        username: Username
        password: Password
        
    Returns:
        User ID if successful, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute(
        "SELECT id FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    )
    
    result = cursor.fetchone()
    user_id = result['id'] if result else None
    
    conn.close()
    return user_id

def create_user(username, email, password_hash):
    """
    Create a new user
    
    Args:
        username: Username
        email: Email address
        password_hash: Password hash
        
    Returns:
        User ID if successful, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        # Username or email already exists
        user_id = None
        conn.rollback()
    
    conn.close()
    return user_id

def register_user(username, email, password):
    """
    Register a new user
    
    Args:
        username: Username
        email: Email address
        password: Password
        
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        # Username or email already exists
        success = False
    
    conn.close()
    return success

def update_user(user_id, email=None, password_hash=None, has_voice_model=None):
    """
    Update user data
    
    Args:
        user_id: User ID
        email: New email address (optional)
        password_hash: New password hash (optional)
        has_voice_model: Voice model status (optional)
        
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if email:
        updates.append("email = ?")
        params.append(email)
    
    if password_hash:
        # Hash the password if it's a plain text password
        if len(password_hash) != 64:  # SHA-256 hash is 64 characters long
            password_hash = hashlib.sha256(password_hash.encode()).hexdigest()
        updates.append("password_hash = ?")
        params.append(password_hash)
    
    if has_voice_model is not None:
        updates.append("has_voice_model = ?")
        params.append(1 if has_voice_model else 0)
    
    if not updates:
        conn.close()
        return False
    
    try:
        cursor.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
            params + [user_id]
        )
        conn.commit()
        success = cursor.rowcount > 0
    except sqlite3.Error:
        success = False
    
    conn.close()
    return success

def update_voice_model_status(user_id, has_voice_model):
    """
    Update user's voice model status
    
    Args:
        user_id: User ID
        has_voice_model: Whether the user has a voice model
        
    Returns:
        True if successful, False otherwise
    """
    return update_user(user_id, has_voice_model=has_voice_model)

def get_user_by_username(username):
    """
    Get user data by username
    
    Args:
        username: Username
        
    Returns:
        User data or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    
    result = cursor.fetchone()
    
    conn.close()
    return result

def get_user_by_email(email):
    """
    Get user data by email
    
    Args:
        email: Email address
        
    Returns:
        User data or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )
    
    result = cursor.fetchone()
    
    conn.close()
    return result

def get_user_by_id(user_id):
    """
    Get user data by ID
    
    Args:
        user_id: User ID
        
    Returns:
        User data or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )
    
    result = cursor.fetchone()
    
    conn.close()
    return result

def save_recording(user_id, filename, analysis_results, feedback):
    """
    Save recording data to database
    
    Args:
        user_id: User ID
        filename: Audio filename
        analysis_results: Dictionary containing analysis results
        feedback: Dictionary containing feedback
        
    Returns:
        Recording ID if successful, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO recordings (
                user_id, filename, text_content, expressiveness_score,
                pitch_variability, energy_variability, speech_rate,
                emotional_tone, feedback
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                filename,
                analysis_results.get('transcription', ''),
                analysis_results.get('expressiveness_score', 0),
                analysis_results.get('pitch_variability', 0),
                analysis_results.get('energy_variability', 0),
                analysis_results.get('speech_rate', 0),
                analysis_results.get('primary_emotion', 'neutral'),
                json.dumps(feedback)
            )
        )
        conn.commit()
        recording_id = cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        recording_id = None
    
    conn.close()
    return recording_id

def get_recording(recording_id, user_id=None):
    """
    Get recording data by ID
    
    Args:
        recording_id: Recording ID
        user_id: User ID (optional, for validation)
        
    Returns:
        Recording data or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute(
            "SELECT * FROM recordings WHERE id = ? AND user_id = ?",
            (recording_id, user_id)
        )
    else:
        cursor.execute(
            "SELECT * FROM recordings WHERE id = ?",
            (recording_id,)
        )
    
    result = cursor.fetchone()
    
    conn.close()
    return dict(result) if result else None

def get_user_recordings(user_id, limit=None, offset=0):
    """
    Get recordings for a user
    
    Args:
        user_id: User ID
        limit: Maximum number of recordings to return (optional)
        offset: Offset for pagination (optional)
        
    Returns:
        List of recording data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if limit:
        cursor.execute(
            "SELECT * FROM recordings WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset)
        )
    else:
        cursor.execute(
            "SELECT * FROM recordings WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
    
    results = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in results]

def get_all_exercises():
    """
    Get all exercises
    
    Returns:
        List of exercise data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM exercises ORDER BY category, difficulty")
    
    results = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in results]

def get_exercise(exercise_id):
    """
    Get exercise data by ID
    
    Args:
        exercise_id: Exercise ID
        
    Returns:
        Exercise data or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM exercises WHERE id = ?",
        (exercise_id,)
    )
    
    result = cursor.fetchone()
    
    conn.close()
    return dict(result) if result else None

def save_benchmark_audio(exercise_id, audio_path, metadata=None):
    """
    Save benchmark audio data for an exercise
    
    Args:
        exercise_id: Exercise ID
        audio_path: Path to benchmark audio file
        metadata: Dictionary containing metadata about the benchmark recording
        
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            UPDATE exercises SET
                benchmark_audio_path = ?,
                benchmark_metadata = ?
            WHERE id = ?
            """,
            (
                str(audio_path),
                json.dumps(metadata) if metadata else None,
                exercise_id
            )
        )
        conn.commit()
        success = cursor.rowcount > 0
    except sqlite3.Error:
        success = False
    
    conn.close()
    return success

def get_user_progress(user_id):
    """
    Get progress data for a user
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary containing progress data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get recordings for the user
    cursor.execute(
        """
        SELECT 
            expressiveness_score, pitch_variability, energy_variability, 
            speech_rate, emotional_tone, created_at
        FROM recordings 
        WHERE user_id = ? 
        ORDER BY created_at
        """,
        (user_id,)
    )
    
    recordings = cursor.fetchall()
    
    conn.close()
    
    if not recordings:
        return None
    
    # Calculate averages
    total_expressiveness = 0
    total_pitch_variability = 0
    total_energy_variability = 0
    total_speech_rate = 0
    emotion_counts = {}
    
    for recording in recordings:
        total_expressiveness += recording['expressiveness_score']
        total_pitch_variability += recording['pitch_variability']
        total_energy_variability += recording['energy_variability']
        total_speech_rate += recording['speech_rate']
        
        emotion = recording['emotional_tone']
        if emotion:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    recording_count = len(recordings)
    
    # Calculate improvements (compare last 3 to previous 3)
    improvements = {}
    
    if recording_count >= 6:
        recent_recordings = recordings[-3:]
        previous_recordings = recordings[-6:-3]
        
        recent_expressiveness = sum(r['expressiveness_score'] for r in recent_recordings) / 3
        previous_expressiveness = sum(r['expressiveness_score'] for r in previous_recordings) / 3
        improvements['expressiveness'] = recent_expressiveness - previous_expressiveness
        
        recent_pitch = sum(r['pitch_variability'] for r in recent_recordings) / 3
        previous_pitch = sum(r['pitch_variability'] for r in previous_recordings) / 3
        improvements['pitch_variability'] = recent_pitch - previous_pitch
        
        recent_energy = sum(r['energy_variability'] for r in recent_recordings) / 3
        previous_energy = sum(r['energy_variability'] for r in previous_recordings) / 3
        improvements['energy_variability'] = recent_energy - previous_energy
        
        recent_rate = sum(r['speech_rate'] for r in recent_recordings) / 3
        previous_rate = sum(r['speech_rate'] for r in previous_recordings) / 3
        improvements['speech_rate'] = recent_rate - previous_rate
    
    # Prepare time series data for charting
    time_series = []
    for recording in recordings:
        created_at = datetime.strptime(recording['created_at'], '%Y-%m-%d %H:%M:%S')
        time_series.append({
            'date': created_at.strftime('%Y-%m-%d'),
            'expressiveness': recording['expressiveness_score'],
            'pitch_variability': recording['pitch_variability'],
            'energy_variability': recording['energy_variability'],
            'speech_rate': recording['speech_rate']
        })
    
    # Return progress data
    return {
        'recording_count': recording_count,
        'average_scores': {
            'expressiveness': total_expressiveness / recording_count,
            'pitch_variability': total_pitch_variability / recording_count,
            'energy_variability': total_energy_variability / recording_count,
            'speech_rate': total_speech_rate / recording_count
        },
        'improvements': improvements,
        'emotion_distribution': emotion_counts,
        'time_series': time_series
    }

# Create tables when the module is imported
create_tables()