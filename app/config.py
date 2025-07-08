import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key_here")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

    # MongoDB
    MONGO_URI = os.environ.get("MONGODB_URL", "mongodb://admin:password@mongodb:27017/")
    MONGO_DB_NAME = os.environ.get("MONGODB_DB_NAME", "academic_rag")

    # ChromaDB
    CHROMA_HOST = os.environ.get("CHROMADB_HOST", "chromadb")
    CHROMA_PORT = int(os.environ.get("CHROMADB_PORT", 8000))

    # Ollama LLM
    OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "academic-assistant")
    EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")

    # RAG settings
    DEFAULT_CHUNK_SIZE = int(os.environ.get("DEFAULT_CHUNK_SIZE", 1000))
    DEFAULT_CHUNK_OVERLAP = int(os.environ.get("DEFAULT_CHUNK_OVERLAP", 200))
    DEFAULT_TOP_K = int(os.environ.get("DEFAULT_TOP_K", 5))

    # Collection Names
    PAPERS_COLLECTION = os.environ.get("PAPERS_COLLECTION", "academic_papers")
    LOGS_COLLECTION = os.environ.get("LOGS_COLLECTION", "query_logs")

    # File uploads
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "/tmp/uploads")
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB

    # Swagger/OpenAPI
    SWAGGER_URL = "/docs"
    API_URL = "/static/swagger.json"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": Config,
}