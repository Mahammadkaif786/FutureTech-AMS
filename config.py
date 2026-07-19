import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ftci_super_secret_session_key_2026')
    
    # Database configurations (Supports SQLite fallback or MySQL setup)
    MYSQL_USER = os.environ.get('MYSQL_USER', '')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'futuretech_db')
    
    if MYSQL_USER and MYSQL_DB:
        # e.g., mysql+pymysql://user:password@localhost/futuretech_db
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder for Student Photos
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB limits
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
