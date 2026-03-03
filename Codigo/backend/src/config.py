import os
import base64
import json
import warnings
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
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "gemini-embedding-001")

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

        # Advertencia si la clave de Supabase es service_role
        role = cls._get_supabase_key_role(cls.SUPABASE_KEY)
        if role == "service_role":
            warnings.warn(
                "\n⚠️  SUPABASE_KEY es de tipo 'service_role'.\n"
                "   ✅ Correcto para este backend (servidor).\n"
                "   🚫 NUNCA uses esta clave en el cliente móvil (Flutter).\n"
                "      El cliente debe usar la clave 'anon' que respeta las políticas RLS.",
                stacklevel=2
            )

    @staticmethod
    def _get_supabase_key_role(jwt: str) -> str:
        """Decodifica el payload del JWT de Supabase para extraer el rol."""
        try:
            # El JWT tiene 3 partes separadas por '.': header.payload.signature
            payload_b64 = jwt.split(".")[1]
            # Añadir padding si es necesario para base64
            payload_b64 += "=" * (-len(payload_b64) % 4)
            payload = json.loads(base64.b64decode(payload_b64))
            return payload.get("role", "unknown")
        except Exception:
            return "unknown"

    @classmethod
    def get_local_timezone(cls):
        """Obtiene la zona horaria local del sistema."""
        return datetime.now().astimezone().tzinfo