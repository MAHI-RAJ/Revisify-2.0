import os
from pathlib import Path

class Config:
    """Application configuration"""
    
    # Base directory
    BASE_DIR = Path(__file__).parent.parent
    BACKEND_DIR = BASE_DIR / "backend"
    
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{BACKEND_DIR}/revisify.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or SECRET_KEY
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", 24))
    
    # Email (SMTP)
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.gmail.com"
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_FROM = os.environ.get("MAIL_FROM") or MAIL_USERNAME
    
    # Storage paths
    UPLOAD_FOLDER = BACKEND_DIR / "storage" / "uploads"
    EXTRACTED_FOLDER = BACKEND_DIR / "storage" / "extracted"
    INDICES_FOLDER = BACKEND_DIR / "storage" / "indices"
    EMBEDDINGS_FOLDER = BACKEND_DIR / "storage" / "embeddings"
    
    # File upload
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {"pdf", "ppt", "pptx", "doc", "docx"}
    
    # LLM Configuration
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")  # openai, anthropic, etc.
    LLM_API_KEY = os.environ.get("LLM_API_KEY")
    LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")  # or gpt-4, claude-3-haiku, etc.
    LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", 0.3))
    LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", 2000))
    
    # Embeddings
    EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION = int(os.environ.get("EMBEDDING_DIMENSION", 384))
    
    # Chunking
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", 200))
    
    # Learning thresholds
    MCQ_THRESHOLD_SCORE = float(os.environ.get("MCQ_THRESHOLD_SCORE", 0.5))  # 5/10 = 0.5
    MAX_HINTS_PER_STEP = int(os.environ.get("MAX_HINTS_PER_STEP", 3))
    MCQ_COUNT_MIN = int(os.environ.get("MCQ_COUNT_MIN", 5))
    MCQ_COUNT_MAX = int(os.environ.get("MCQ_COUNT_MAX", 10))
    
    # RAG
    RAG_TOP_K = int(os.environ.get("RAG_TOP_K", 5))
    RAG_SIMILARITY_THRESHOLD = float(os.environ.get("RAG_SIMILARITY_THRESHOLD", 0.5))
    
    # CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
    
    # Frontend URL (for email links)
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    
    # Processing
    PROCESSING_POLL_INTERVAL = int(os.environ.get("PROCESSING_POLL_INTERVAL", 2))  # seconds
    
    @staticmethod
    def init_app(app):
        """Initialize app with config"""
        # Ensure storage directories exist
        Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        Config.EXTRACTED_FOLDER.mkdir(parents=True, exist_ok=True)
        Config.INDICES_FOLDER.mkdir(parents=True, exist_ok=True)
        Config.EMBEDDINGS_FOLDER.mkdir(parents=True, exist_ok=True)

