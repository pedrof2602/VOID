import os
import logging
from deepgram import DeepgramClient
from src.config import Config

logger = logging.getLogger(__name__)

# AQUI ESTA EL CAMBIO: Añadimos ", keywords: list = None" para que acepte el argumento
async def transcribe_audio_async(file_path: str, keywords: list = None) -> str:
    """
    Transcribe audio usando Deepgram.
    Acepta 'keywords' para mejorar la precisión de términos técnicos.
    """
    try:
        if not os.path.exists(file_path):
            logger.error("❌ Archivo de audio no encontrado.")
            return None

        deepgram = DeepgramClient(api_key=Config.DEEPGRAM_API_KEY)

        with open(file_path, "rb") as file:
            buffer_data = file.read()

        # Preparar opciones para la API v5.3.1
        transcribe_options = {
            "model": "nova-2",
            "smart_format": True,
            "language": "es",
        }
        
        # SI recibimos keywords del main, se las pasamos a Deepgram
        if keywords:
            transcribe_options["keywords"] = keywords

        # Usar la nueva API: client.listen.v1.media.transcribe_file()
        response = deepgram.listen.v1.media.transcribe_file(
            request=buffer_data,
            **transcribe_options
        )
        
        transcript = response.results.channels[0].alternatives[0].transcript
        return transcript

    except Exception as e:
        logger.error(f"❌ Error en transcripción: {e}")
        return None