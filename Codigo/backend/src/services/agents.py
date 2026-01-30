import httpx
import logging
from datetime import datetime, timedelta
from src.services.keyring import KeyringService
from src.services.memory import MemoryService
from src.services.intelligence import IntelligenceService
from src.config import Config
from src.schemas import MemoryPayload, MemoryCategory

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        # Inicializamos el llavero para poder buscar credenciales
        self.keyring = KeyringService()
        # Servicios para auto-documentación
        self.memory = MemoryService()
        self.brain = IntelligenceService()
        # Cliente HTTP reutilizable para mejor performance
        self.http_client: httpx.AsyncClient = None
    
    async def __aenter__(self):
        """Context manager entry - inicializa el cliente HTTP."""
        self.http_client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, *args):
        """Context manager exit - cierra el cliente HTTP."""
        if self.http_client:
            await self.http_client.aclose()

    async def _save_action_to_memory(self, action_summary: str, raw_input: str):
        """
        Auto-documentación: Guarda la acción ejecutada en la base de datos de memoria.
        Esto permite que VOID recuerde qué acciones tomó para futuras consultas.
        """
        try:
            logger.info("📝 Auto-documentando acción en memoria...")
            
            # Generar embedding para búsqueda futura
            vector = await self.brain.generate_embedding(action_summary)
            
            # Crear payload de memoria
            payload = MemoryPayload(
                raw_input=raw_input,
                content=action_summary,
                vector=vector,
                category=MemoryCategory.FACT,  # Las acciones ejecutadas son hechos
                tags=["action", "automated"],
                entities={},
                duration=0.0
            )
            
            # Guardar en la base de datos
            success = await self.memory.save_memory(payload)
            if success:
                logger.info("✅ Acción documentada en memoria")
            else:
                logger.warning("⚠️ No se pudo documentar la acción")
                
        except Exception as e:
            logger.error(f"Error auto-documentando acción: {e}")

    async def route_action(self, user_id: str, unified_data: 'UnifiedOutput') -> str:
        """
        El Capataz: Recibe una orden y decide a qué especialista (Agente) llamar.
        Ahora recibe UnifiedOutput con toda la información ya extraída.
        """
        from src.schemas import UnifiedOutput
        
        category = unified_data.category
        content = unified_data.refined_text
        
        logger.info(f"⚡ AGENTE: Ejecutando acción '{category}' para usuario {user_id}...")

        if category == "TODO" or "notion" in content.lower():
            return await self._notion_agent(user_id, unified_data)
        
        elif category == "CALENDAR" or "agendar" in content.lower():
            return await self._google_calendar_agent(user_id, unified_data)
            
        else:
            return "⚠️ No tengo un agente para esto todavía."

    # --- AGENTE 1: NOTION (El Escribano) ---
    async def _notion_agent(self, user_id: str, unified_data: 'UnifiedOutput'):
        """Agente de Notion - ahora recibe UnifiedOutput"""
        from src.schemas import UnifiedOutput
        
        # 1. Buscamos las llaves
        creds = await self.keyring.get_credentials(user_id, "NOTION")
        if not creds: return "❌ Error: No has conectado Notion."

        # Usar título si existe, sino el texto refinado
        task_text = unified_data.title or unified_data.refined_text

        # 2. Preparamos la petición
        headers = {
            "Authorization": f"Bearer {creds.get('token')}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        payload = {
            "parent": {"database_id": creds.get("database_id")},
            "properties": {
                "Name": {"title": [{"text": {"content": task_text}}]},
                "Origen": {"select": {"name": "VOID Audio"}}
            }
        }

        # 3. Ejecutamos usando el cliente reutilizable
        try:
            res = await self.http_client.post(
                "https://api.notion.com/v1/pages", 
                headers=headers, 
                json=payload
            )
            
            if res.status_code == 200:
                # 4. AUTO-DOCUMENTACIÓN: Guardar en memoria
                action_summary = f"Se agregó tarea en Notion: {task_text}"
                await self._save_action_to_memory(action_summary, unified_data.refined_text)
                return "✅ Guardado en Notion."
            else:
                return f"❌ Notion Error: {res.status_code}"
                
        except Exception as e:
            logger.error(f"Error de red Notion: {e}")
            return f"❌ Error de red Notion: {e}"

    # --- AGENTE 2: GOOGLE CALENDAR (El Secretario) ---
    async def _google_calendar_agent(self, user_id: str, unified_data: 'UnifiedOutput'):
        """Agente de Google Calendar - ahora con soporte para ubicación y recordatorios"""
        from src.schemas import UnifiedOutput
        
        # 1. Buscamos las llaves
        creds = await self.keyring.get_credentials(user_id, "GOOGLE")
        if not creds: return "❌ Error: No has conectado Google Calendar."

        # 2. Canjeamos el Refresh Token por un Access Token fresco (La magia de OAuth)
        access_token = await self._get_google_access_token(creds)
        if not access_token: return "❌ Error: No pude renovar el token de Google."

        # 3. Calculamos la fecha usando timezone local del sistema
        local_tz = Config.get_local_timezone()
        start_time = datetime.now(tz=local_tz) + timedelta(days=1)
        start_time = start_time.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Formato ISO requerido por Google (incluye timezone automáticamente)
        start_iso = start_time.isoformat()
        end_iso = (start_time + timedelta(hours=1)).isoformat()

        # ✅ Usar título extraído por IA (corto y descriptivo)
        event_title = unified_data.title or unified_data.refined_text
        
        event_body = {
            "summary": event_title,  # ✅ Título limpio y corto
            "description": f"Agendado vía VOID: {unified_data.refined_text}",
            "start": {"dateTime": start_iso},
            "end": {"dateTime": end_iso}
        }
        
        # ✅ Agregar ubicación si existe
        if unified_data.location:
            event_body["location"] = unified_data.location
            logger.info(f"📍 Ubicación agregada: {unified_data.location}")
        
        # ✅ Agregar recordatorio personalizado si se especificó
        if unified_data.reminder_minutes:
            event_body["reminders"] = {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": unified_data.reminder_minutes}
                ]
            }
            logger.info(f"⏰ Recordatorio configurado: {unified_data.reminder_minutes} minutos antes")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # 4. Ejecutamos usando el cliente reutilizable
        try:
            res = await self.http_client.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers=headers,
                json=event_body
            )
            if res.status_code == 200:
                link = res.json().get('htmlLink')
                
                # 5. AUTO-DOCUMENTACIÓN: Guardar en memoria
                fecha_legible = start_time.strftime("%d/%m/%Y a las %H:%M")
                action_summary = f"Se agendó en Google Calendar: {event_title} para el {fecha_legible}"
                if unified_data.location:
                    action_summary += f" en {unified_data.location}"
                await self._save_action_to_memory(action_summary, unified_data.refined_text)
                
                return f"✅ Agendado en Google Calendar. Link: {link}"
            else:
                return f"❌ Google Error ({res.status_code}): {res.text}"
        except Exception as e:
            logger.error(f"Error de red Google: {e}")
            return f"❌ Error de red Google: {e}"

    async def _get_google_access_token(self, creds: dict) -> str:
        """
        Función auxiliar para renovar el token caducado usando el Refresh Token eterno.
        """
        params = {
            "client_id": creds.get("client_id"),
            "client_secret": creds.get("client_secret"),
            "refresh_token": creds.get("refresh_token"),
            "grant_type": "refresh_token"
        }
        
        try:
            res = await self.http_client.post(
                "https://oauth2.googleapis.com/token", 
                data=params
            )
            if res.status_code == 200:
                return res.json().get("access_token")
            else:
                logger.error(f"Fallo renovando token: {res.text}")
                return None
        except Exception as e:
            logger.error(f"Error conexión OAuth: {e}")
            return None