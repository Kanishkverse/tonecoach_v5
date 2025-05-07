import sqlite3
from datetime import datetime

class User:
    def __init__(self, id=None, username=None, email=None, password_hash=None, created_at=None, has_voice_model=0):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at if created_at else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.has_voice_model = has_voice_model
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'has_voice_model': self.has_voice_model
        }
    
    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row[0],
            username=row[1],
            email=row[2],
            password_hash=row[3],
            created_at=row[4],
            has_voice_model=row[5]
        )

class Recording:
    def __init__(self, id=None, user_id=None, filename=None, text_content=None, 
                 expressiveness_score=None, pitch_variability=None, energy_variability=None,
                 speech_rate=None, emotional_tone=None, feedback=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.filename = filename
        self.text_content = text_content
        self.expressiveness_score = expressiveness_score
        self.pitch_variability = pitch_variability
        self.energy_variability = energy_variability
        self.speech_rate = speech_rate
        self.emotional_tone = emotional_tone
        self.feedback = feedback
        self.created_at = created_at if created_at else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'text_content': self.text_content,
            'expressiveness_score': self.expressiveness_score,
            'pitch_variability': self.pitch_variability,
            'energy_variability': self.energy_variability,
            'speech_rate': self.speech_rate,
            'emotional_tone': self.emotional_tone,
            'feedback': self.feedback,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row[0],
            user_id=row[1],
            filename=row[2],
            text_content=row[3],
            expressiveness_score=row[4],
            pitch_variability=row[5],
            energy_variability=row[6],
            speech_rate=row[7],
            emotional_tone=row[8],
            feedback=row[9],
            created_at=row[10]
        )

class Exercise:
    def __init__(self, id=None, title=None, description=None, text_content=None, 
                 difficulty=None, category=None, target_emotion=None):
        self.id = id
        self.title = title
        self.description = description
        self.text_content = text_content
        self.difficulty = difficulty
        self.category = category
        self.target_emotion = target_emotion
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'text_content': self.text_content,
            'difficulty': self.difficulty,
            'category': self.category,
            'target_emotion': self.target_emotion
        }
    
    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row[0],
            title=row[1],
            description=row[2],
            text_content=row[3],
            difficulty=row[4],
            category=row[5],
            target_emotion=row[6]
        )