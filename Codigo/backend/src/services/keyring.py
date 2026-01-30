import asyncio
import logging
from typing import Optional, Dict
from supabase import create_client, Client
from src.config import Config

logger = logging.getLogger(__name__)

class KeyringService:
    def __init__(self):
        # Conectamos con Supabase usando las claves de tu .env
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self._cache: Dict[str, dict] = {}  # Cache simple para evitar queries repetidas

    async def get_credentials(self, user_id: str, service_name: str) -> Optional[dict]:
        """
        Busca las credenciales en la tabla user_integrations con cache.
        """
        cache_key = f"{user_id}:{service_name}"
        
        # Verificar cache primero
        if cache_key in self._cache:
            logger.debug(f"✅ Credenciales de {service_name} obtenidas del cache")
            return self._cache[cache_key]
        
        try:
            # Ejecutar query en thread separado para no bloquear
            response = await asyncio.to_thread(
                lambda: self.supabase.table("user_integrations")
                    .select("credentials")
                    .eq("user_id", user_id)
                    .eq("provider", service_name)
                    .execute()
            )

            if response.data and len(response.data) > 0:
                creds = response.data[0]['credentials']
                self._cache[cache_key] = creds  # Guardar en cache
                return creds
            else:
                logger.warning(f"⚠️ El usuario {user_id} no tiene conectado {service_name}")
                return None
        except Exception as e:
            logger.error(f"❌ Error buscando llaves en DB: {e}")
            return None