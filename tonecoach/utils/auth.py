import hashlib
import re
from database.db_utils import get_user_by_username, get_user_by_email, update_user as db_update_user

def validate_email(email):
    """
    Validate email format
    
    Args:
        email: Email address
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    Validate password strength
    
    Args:
        password: Password
        
    Returns:
        True if valid, False otherwise
    """
    # At least 8 characters, at least one letter and one number
    return len(password) >= 8 and any(c.isalpha() for c in password) and any(c.isdigit() for c in password)

def hash_password(password):
    """
    Hash password
    
    Args:
        password: Plain text password
        
    Returns:
        SHA-256 hash of password
    """
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(username, password):
    """
    Attempt to log in a user
    
    Args:
        username: Username
        password: Password
        
    Returns:
        User ID if successful, None otherwise
    """
    # Hash password
    password_hash = hash_password(password)
    
    # Get user by username
    user = get_user_by_username(username)
    
    if user and user['password_hash'] == password_hash:
        return user['id']
    
    return None

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
    # Validate email
    if not validate_email(email):
        return False
    
    # Validate password
    if not validate_password(password):
        return False
    
    # Check if username or email already exists
    if get_user_by_username(username) or get_user_by_email(email):
        return False
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create user
    try:
        create_user(username, email, password_hash)
        return True
    except Exception:
        return False

def update_user(user_id, email=None, password=None):
    """
    Update user data
    
    Args:
        user_id: User ID
        email: New email address (optional)
        password: New password (optional)
        
    Returns:
        True if successful, False otherwise
    """
    # Validate email if provided
    if email and not validate_email(email):
        return False
    
    # Validate password if provided
    if password and not validate_password(password):
        return False
    
    # Hash password if provided
    password_hash = hash_password(password) if password else None
    
    # Update user
    return db_update_user(user_id, email=email, password_hash=password_hash)

def create_user(username, email, password_hash):
    """
    Create a new user
    
    Args:
        username: Username
        email: Email address
        password_hash: Hashed password
        
    Returns:
        User ID if successful, None otherwise
    """
    from database.db_utils import create_user as db_create_user
    return db_create_user(username, email, password_hash)