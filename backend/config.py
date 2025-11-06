import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class Settings:
    # Database
    MONGO_URL: str = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME: str = os.environ.get('DB_NAME', 'hireflow_db')
    
    # JWT
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET: str = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_URI: str = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:3000/auth/google/callback')
    
    # Groq API
    GROQ_API_KEY: str = os.environ.get('GROQ_API_KEY', '')
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # CORS
    CORS_ORIGINS: str = os.environ.get('CORS_ORIGINS', '*')
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Frontend URL
    FRONTEND_URL: str = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

settings = Settings()
