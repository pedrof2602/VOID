import asyncio
import logging
from supabase import create_client, Client
from src.config import Config
from src.schemas import MemoryPayload

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self):
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.user_id = Config.USER_ID

    async def save_memory(self, payload: MemoryPayload) -> bool:
        """Guarda memoria de forma asíncrona usando el esquema estricto."""
        logger.info("💾 Escribiendo en Cortex...")
        
        try:
            # 1. Insertar Grabación (Metadata)
            rec_data = {
                "user_id": self.user_id,
                "transcription": payload.raw_input,
                "summary": payload.content, # El contenido refinado es el mejor resumen
                "duration": payload.duration,
                "category": payload.category.value, # .value para sacar el string del Enum
                "priority": payload.priority,
                "tags": payload.tags,
                "entities": payload.entities
            }
            
            # Ejecutar insert en thread separado para no bloquear el event loop
            res_rec = await asyncio.to_thread(
                lambda: self.supabase.table("recordings").insert(rec_data).execute()
            )
            
            if not res_rec.data:
                raise Exception("No se generó ID para la grabación")
                
            rec_id = res_rec.data[0]['id']

            # 2. Insertar Embedding (Si existe vector)
            if payload.vector:
                mem_data = {
                    "user_id": self.user_id,
                    "recording_id": rec_id,
                    "content": payload.content,
                    "embedding": payload.vector
                }
                await asyncio.to_thread(
                    lambda: self.supabase.table("memory_embeddings").insert(mem_data).execute()
                )
                logger.info("✅ Recuerdo cristalizado correctamente.")
                
            return True

        except Exception as e:
            logger.critical(f"FATAL DB ERROR: {e}")
            return False