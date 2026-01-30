import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Config:
    # Credenciales
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    USER_ID = os.getenv("USER_ID")
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # LLM Configuration
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash-lite")
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "models/text-embedding-004")

    # Validación al iniciar
    @classmethod
    def validate(cls):
        """Valida que todas las variables de entorno requeridas estén presentes."""
        required = {
            "SUPABASE_URL": cls.SUPABASE_URL,
            "SUPABASE_KEY": cls.SUPABASE_KEY,
            "DEEPGRAM_API_KEY": cls.DEEPGRAM_API_KEY,
            "GOOGLE_API_KEY": cls.GOOGLE_API_KEY
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(f"❌ ERROR: Faltan variables en .env: {', '.join(missing)}")
    
    @classmethod
    def get_local_timezone(cls):
        """Obtiene la zona horaria local del sistema."""
        return datetime.now().astimezone().tzinfo