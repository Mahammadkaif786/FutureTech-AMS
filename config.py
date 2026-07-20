import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ftci_super_secret_session_key_2026')
    
    # Database configurations (Supports DATABASE_URL, MySQL, or SQLite fallback)
    DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    MYSQL_USER = os.environ.get('MYSQL_USER', '')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'futuretech_db')
    
    is_vercel = os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') is not None
    
    if DATABASE_URL:
        db_url = DATABASE_URL
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = db_url
    elif MYSQL_USER and MYSQL_DB:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    else:
        db_path = '/tmp/database.db' if is_vercel else os.path.join(BASE_DIR, 'database.db')
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_path
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder for Student Photos
    UPLOAD_FOLDER = '/tmp/uploads' if is_vercel else os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB limits
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

