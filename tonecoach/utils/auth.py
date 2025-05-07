import hashlib
import streamlit as st
from database.db_utils import get_user_by_username, create_user, update_user

def hash_password(password):
    """
    Hash a password for storage
    
    Args:
        password: Password string
        
    Returns:
        Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, password):
    """
    Verify a password against stored hash
    
    Args:
        stored_hash: Stored password hash
        password: Password to verify
        
    Returns:
        True if password matches, False otherwise
    """
    return stored_hash == hash_password(password)

def register_user(username, email, password):
    """
    Register a new user
    
    Args:
        username: User's username
        email: User's email
        password: User's password
        
    Returns:
        User ID if registration successful, otherwise None
    """
    # Hash password
    password_hash = hash_password(password)
    
    # Create user
    user_id = create_user(username, email, password_hash)
    
    return user_id

def login_user(username, password):
    """
    Login a user
    
    Args:
        username: User's username
        password: User's password
        
    Returns:
        User ID if login successful, otherwise None
    """
    # Get user
    user = get_user_by_username(username)
    
    if user and verify_password(user.password_hash, password):
        return user.id
    
    return None

def update_password(user_id, password):
    """
    Update a user's password
    
    Args:
        user_id: User ID
        password: New password
        
    Returns:
        True if update successful, False otherwise
    """
    # Hash password
    password_hash = hash_password(password)
    
    # Update user
    return update_user(user_id, password_hash=password_hash)

def check_auth():
    """
    Check if user is authenticated
    
    Returns:
        True if user is authenticated, False otherwise
    """
    return st.session_state.user_id is not None