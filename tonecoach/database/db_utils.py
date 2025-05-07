import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from database.models import User, Recording, Exercise

DB_PATH = 'tonecoach.db'

def get_connection():
    """Get a connection to the database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_connection()
    c = conn.cursor()
    
    # Create users table
    c.execute('''
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
    c.execute('''
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
    
    # Create exercises table
    c.execute('''
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        text_content TEXT NOT NULL,
        difficulty TEXT,
        category TEXT,
        target_emotion TEXT
    )
    ''')
    
    # Add sample exercises if none exist
    c.execute("SELECT COUNT(*) FROM exercises")
    if c.fetchone()[0] == 0:
        sample_exercises = [
            (
                'Introduction Speech',
                'Practice introducing yourself in a professional setting.',
                'Hello everyone, my name is [Your Name]. I am excited to be here today to share my thoughts on this important topic. I have been working in this field for several years and have gained valuable insights that Im looking forward to discussing with you.',
                'Beginner',
                'Professional',
                'Confident'
            ),
            (
                'Storytelling Practice',
                'Practice telling an engaging story with emotional elements.',
                'It was a dark and stormy night. The rain pounded against the windows as I sat alone in my room. Suddenly, I heard a strange noise coming from outside. With my heart racing, I slowly approached the window and looked out into the darkness.',
                'Intermediate',
                'Storytelling',
                'Suspenseful'
            ),
            (
                'Persuasive Pitch',
                'Practice delivering a persuasive business pitch.',
                'Our product solves a critical problem in the market. With our innovative approach, we can reduce costs by 30% while improving efficiency. The opportunity is massive, with a potential market size of $2 billion. Were seeking your investment to scale our operations and capture this untapped potential.',
                'Advanced',
                'Business',
                'Passionate'
            ),
            (
                'Motivational Speech',
                'Practice delivering an inspirational message.',
                'Today marks not an end, but a beginning. As you stand at this crossroads, remember that every challenge you have overcome has prepared you for this moment. The path ahead may not be easy, but I believe in your ability to persist, to innovate, and to make a difference. Your unique perspective is exactly what the world needs right now.',
                'Intermediate',
                'Motivational',
                'Inspirational'
            ),
            (
                'Technical Explanation',
                'Practice explaining a complex concept clearly and concisely.',
                'Machine learning is a process where computers learn patterns from data without being explicitly programmed. Instead of writing specific instructions, we provide examples and let the algorithm find the underlying patterns. This approach enables systems to improve automatically through experience, similar to how humans learn from observation and feedback.',
                'Advanced',
                'Educational',
                'Informative'
            ),
            (
                'Customer Service Response',
                'Practice handling a frustrated customer with empathy.',
                'I understand how frustrating this situation must be for you, and I sincerely apologize for the inconvenience. Your satisfaction is our top priority, and I want to assure you that I will personally work to resolve this issue as quickly as possible. Let me walk you through the steps we will take to address your concerns and make things right.',
                'Beginner',
                'Professional',
                'Empathetic'
            )
        ]
        c.executemany('''
        INSERT INTO exercises (title, description, text_content, difficulty, category, target_emotion)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_exercises)
    
    conn.commit()
    conn.close()

def get_user_by_id(user_id):
    """Get user data by ID"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = c.fetchone()
    
    conn.close()
    
    if user_row:
        return User.from_row(tuple(user_row))
    return None

def get_user_by_username(username):
    """Get user data by username"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user_row = c.fetchone()
    
    conn.close()
    
    if user_row:
        return User.from_row(tuple(user_row))
    return None

def create_user(username, email, password_hash):
    """Create a new user"""
    conn = get_connection()
    c = conn.cursor()
    
    try:
        c.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def update_user(user_id, email=None, password_hash=None):
    """Update user data"""
    conn = get_connection()
    c = conn.cursor()
    
    try:
        if email:
            c.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id))
        
        if password_hash:
            c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
        
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def update_voice_model_status(user_id, has_model):
    """Update user's voice model status"""
    conn = get_connection()
    c = conn.cursor()
    
    try:
        c.execute("UPDATE users SET has_voice_model = ? WHERE id = ?", (1 if has_model else 0, user_id))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def save_recording(user_id, filename, analysis_results, feedback):
    """Save recording analysis to database"""
    conn = get_connection()
    c = conn.cursor()
    
    try:
        c.execute('''
        INSERT INTO recordings (
            user_id, filename, text_content, expressiveness_score, 
            pitch_variability, energy_variability, speech_rate, 
            emotional_tone, feedback
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 
            filename, 
            analysis_results.get('transcription', ''),
            analysis_results.get('expressiveness_score', 0.0),
            analysis_results.get('pitch_variability', 0.0),
            analysis_results.get('energy_variability', 0.0),
            analysis_results.get('speech_rate', 0.0),
            analysis_results.get('primary_emotion', 'neutral'),
            json.dumps(feedback)
        ))
        
        conn.commit()
        recording_id = c.lastrowid
        conn.close()
        return recording_id
    except Exception as e:
        print(f"Error saving recording: {e}")
        conn.close()
        return None

def get_user_recordings(user_id, limit=10):
    """Get user's recordings from database"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
    SELECT * FROM recordings 
    WHERE user_id = ? 
    ORDER BY created_at DESC
    LIMIT ?
    ''', (user_id, limit))
    
    rows = c.fetchall()
    recordings = []
    
    for row in rows:
        recordings.append(Recording.from_row(tuple(row)).to_dict())
    
    conn.close()
    return recordings

def get_recording(recording_id, user_id):
    """Get a specific recording"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
    SELECT * FROM recordings 
    WHERE id = ? AND user_id = ?
    ''', (recording_id, user_id))
    
    row = c.fetchone()
    conn.close()
    
    if row:
        return Recording.from_row(tuple(row)).to_dict()
    return None

def get_user_progress(user_id, days=30):
    """Get user progress data for the dashboard"""
    conn = get_connection()
    c = conn.cursor()
    
    # Get date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Convert dates to strings for SQLite
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Get recordings in date range
    c.execute('''
    SELECT created_at, expressiveness_score, pitch_variability, 
           energy_variability, speech_rate, emotional_tone
    FROM recordings
    WHERE user_id = ? AND created_at BETWEEN ? AND ?
    ORDER BY created_at
    ''', (user_id, start_date_str, end_date_str))
    
    results = c.fetchall()
    conn.close()
    
    if not results:
        return None
    
    # Extract data for progress charts
    dates = [row[0] for row in results]
    expressiveness_scores = [row[1] for row in results]
    pitch_variability = [row[2] for row in results]
    energy_variability = [row[3] for row in results]
    speech_rate = [row[4] for row in results]
    emotions = [row[5] for row in results]
    
    # Calculate improvements if we have at least 2 recordings
    improvements = {}
    if len(expressiveness_scores) >= 2:
        improvements['expressiveness'] = expressiveness_scores[-1] - expressiveness_scores[0]
        improvements['pitch_variability'] = pitch_variability[-1] - pitch_variability[0]
        improvements['energy_variability'] = energy_variability[-1] - energy_variability[0]
        improvements['speech_rate'] = speech_rate[-1] - speech_rate[0]
    
    # Count emotions
    emotion_counts = {}
    for emotion in emotions:
        if emotion in emotion_counts:
            emotion_counts[emotion] += 1
        else:
            emotion_counts[emotion] = 1
    
    # Calculate average scores
    avg_expressiveness = sum(expressiveness_scores) / len(expressiveness_scores) if expressiveness_scores else 0
    avg_pitch_var = sum(pitch_variability) / len(pitch_variability) if pitch_variability else 0
    avg_energy_var = sum(energy_variability) / len(energy_variability) if energy_variability else 0
    avg_speech_rate = sum(speech_rate) / len(speech_rate) if speech_rate else 0
    
    return {
        'dates': dates,
        'expressiveness_scores': expressiveness_scores,
        'pitch_variability': pitch_variability,
        'energy_variability': energy_variability,
        'speech_rate': speech_rate,
        'improvements': improvements,
        'emotion_distribution': emotion_counts,
        'average_scores': {
            'expressiveness': avg_expressiveness,
            'pitch_variability': avg_pitch_var,
            'energy_variability': avg_energy_var,
            'speech_rate': avg_speech_rate
        },
        'recording_count': len(results)
    }

def get_all_exercises():
    """Get all exercises"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('SELECT * FROM exercises')
    rows = c.fetchall()
    
    exercises = []
    for row in rows:
        exercises.append(Exercise.from_row(tuple(row)).to_dict())
    
    conn.close()
    return exercises

def get_exercise(exercise_id):
    """Get a specific exercise"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('SELECT * FROM exercises WHERE id = ?', (exercise_id,))
    row = c.fetchone()
    
    conn.close()
    
    if row:
        return Exercise.from_row(tuple(row)).to_dict()
    return None