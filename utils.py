import json
import os
from pathlib import Path
import streamlit as st

# Default settings to use if settings.json doesn't exist
DEFAULT_SETTINGS = {
    "universities": ["Example University"],
    "semesters": {"Example University": ["Semester 1", "Semester 2"]},
    "courses": {"Example University_Semester 1": ["Introduction to Computer Science", "Calculus I"]}
}

def create_directory_if_not_exists(directory_path):
    """Create a directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def load_settings():
    """Load settings from the settings.json file"""
    settings_path = Path("data/settings.json")
    
    if not settings_path.exists():
        # Create the default settings file if it doesn't exist
        create_directory_if_not_exists(settings_path.parent)
        with open(settings_path, 'w') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS
    
    try:
        with open(settings_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS

def save_settings(settings):
    """Save settings to the settings.json file"""
    settings_path = Path("data/settings.json")
    
    try:
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)
        st.session_state.settings = settings
        return True
    except Exception as e:
        st.error(f"Error saving settings: {e}")
        return False

def get_file_path(university, semester, course):
    """Generate a file path for a given university, semester, and course"""
    # Replace any characters that might cause issues in file paths
    safe_uni = university.replace(" ", "_").replace("/", "-")
    safe_semester = semester.replace(" ", "_").replace("/", "-")
    safe_course = course.replace(" ", "_").replace("/", "-")
    
    # Construct and return the path
    return Path(f"data/uploads/{safe_uni}/{safe_semester}/{safe_course}")

def send_email_notification(recipient, subject, message):
    """
    Send an email notification
    
    This is a placeholder function that would be implemented with a real email service
    like SMTP, SendGrid, or similar in a production environment.
    """
    # In a real implementation, this would send an actual email
    # For now, we'll just log the notification to the console
    print(f"NOTIFICATION: To: {recipient}, Subject: {subject}, Message: {message}")
    
    # Return success assuming the email was sent
    return True

def validate_email(email):
    """Simple email validation"""
    if not email:
        return False
    
    # Check for @ symbol and period
    if '@' not in email or '.' not in email:
        return False
    
    # Check for spaces
    if ' ' in email:
        return False
    
    return True

def format_datetime(iso_datetime):
    """Format ISO datetime string to readable format"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(iso_datetime)
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        return iso_datetime
