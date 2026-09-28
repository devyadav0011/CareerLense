import os
from dotenv import load_dotenv

# Load environment variables
basedir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.join(basedir, '..'))
load_dotenv(os.path.join(root_dir, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'careerlense-secret-key-production-ready')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(root_dir, "career_lense.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', 10))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(root_dir, 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}

    # AI Configuration
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini').lower()
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    # Transparent Scoring Algorithm Weights (Sum to 1.0)
    SCORE_WEIGHTS = {
        'content': 0.20,
        'skills': 0.15,
        'projects': 0.15,
        'experience': 0.15,
        'education': 0.10,
        'formatting': 0.10,
        'completeness': 0.15
    }

    # Job Match Weights (Sum to 1.0)
    JOB_MATCH_WEIGHTS = {
        'skills': 0.35,
        'experience': 0.25,
        'projects': 0.20,
        'keywords': 0.10,
        'education': 0.10
    }
