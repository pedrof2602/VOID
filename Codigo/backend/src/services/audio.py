import asyncio
import logging
import sounddevice as sd
import scipy.io.wavfile as wav
from src.config import Config

logger = logging.getLogger(__name__)

async def record_audio() -> bool:
    """Graba audio del micrófono de forma asíncrona."""
    logger.info(f"🎤 GRABANDO ({Config.DURATION}s)...")
    try:
        # Ejecutar grabación en thread separado para no bloquear el event loop
        recording = await asyncio.to_thread(
            sd.rec,
            int(Config.DURATION * Config.FREQ), 
            samplerate=Config.FREQ, 
            channels=1
        )
        await asyncio.to_thread(sd.wait)
        await asyncio.to_thread(wav.write, Config.FILENAME, Config.FREQ, recording)
        logger.info("⏹️ Audio capturado.")
        return True
    except Exception as e:
        logger.error(f"❌ Error grabando audio: {e}")
        return False