"""
VOID Tool Registry - Autonomous Tool Execution
================================================

Filosofía: El modelo (DSPy/Gemini) decide QUÉ herramientas usar.
Python es un ejecutor ciego que solo obedece.

Author: VOID Intelligence Team
"""
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Google Calendar imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

logger = logging.getLogger(__name__)

# Scopes para Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']


class ToolRegistry:
    """
    Registro central de herramientas disponibles para el sistema.
    
    Cada herramienta es una función que el modelo puede solicitar ejecutar.
    El registro se encarga de:
    1. Autenticación con servicios externos (Google, Notion, etc.)
    2. Ejecución de herramientas solicitadas por el modelo
    3. Manejo de errores y logging
    """
    
    def __init__(self):
        """Inicializa el registro y autentica servicios"""
        self.google_calendar = self._init_google_calendar()
        logger.info("✅ ToolRegistry initialized")
    
    def _init_google_calendar(self):
        """
        Inicializa y autentica Google Calendar API.
        
        🔒 PROTOTIPO: Usa credenciales hardcodeadas en src/
        
        🚀 PRODUCCIÓN (TODO):
        - Guardar tokens por usuario en Supabase
        - Flujo OAuth por usuario vía web
        - Refresh automático de tokens
        """
        creds = None
        # 🔧 Rutas configurables vía environment variables (production-ready)
        token_path = Path(os.getenv('GOOGLE_TOKEN_PATH', str(Path(__file__).parent / 'token.pickle')))
        credentials_path = Path(os.getenv('GOOGLE_CREDENTIALS_PATH', str(Path(__file__).parent / 'credentials.json')))
        
        # PROTOTIPO: Buscar token local
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Si no hay credenciales válidas, autenticar
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif credentials_path.exists():
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
                
                # Guardar token para próxima vez
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            else:
                logger.warning("⚠️ No se encontró credentials.json - Google Calendar deshabilitado")
                return None
        
        # TODO: PRODUCCIÓN - Autenticación por usuario
        # """
        # async def _init_google_calendar_per_user(self, user_id: str):
        #     # 1. Buscar token en Supabase
        #     token_data = await supabase.table('user_tokens')
        #         .select('*')
        #         .eq('user_id', user_id)
        #         .eq('service', 'google_calendar')
        #         .single()
        #         .execute()
        #     
        #     # 2. Si no existe, redirigir a OAuth flow
        #     if not token_data:
        #         oauth_url = generate_oauth_url(user_id)
        #         return {'status': 'auth_required', 'url': oauth_url}
        #     
        #     # 3. Crear credenciales desde token guardado
        #     creds = Credentials.from_authorized_user_info(token_data)
        #     
        #     # 4. Refresh si expiró
        #     if creds.expired:
        #         creds.refresh(Request())
        #         await supabase.table('user_tokens').update({
        #             'token': creds.to_json()
        #         }).eq('id', token_data['id']).execute()
        #     
        #     return build('calendar', 'v3', credentials=creds)
        # """
        
        return build('calendar', 'v3', credentials=creds)
    
    # ==========================================
    # HERRAMIENTAS DISPONIBLES
    # ==========================================
    
    def calendar_add(
        self,
        summary: str,
        start_iso: str,
        duration_minutes: int = 60,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Agrega un evento a Google Calendar.
        
        Args:
            summary: Título del evento (calculado por la IA)
            start_iso: Fecha/hora de inicio en formato ISO 8601 (calculado por la IA)
            duration_minutes: Duración en minutos (default: 60)
            description: Descripción opcional del evento
            location: Ubicación opcional del evento
        
        Returns:
            Dict con el ID del evento creado y link
        
        Ejemplo de uso por la IA:
            Input: "Reunión con Juan mañana a las 3pm"
            IA calcula: start_iso = "2026-01-24T15:00:00"
            Python ejecuta: calendar_add(
                summary="Reunión con Juan",
                start_iso="2026-01-24T15:00:00"
            )
        """
        if not self.google_calendar:
            raise Exception("Google Calendar no está autenticado")
        
        try:
            # Parsear fecha de inicio
            start_dt = datetime.fromisoformat(start_iso)
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            # Construir evento
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'America/Argentina/Buenos_Aires',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'America/Argentina/Buenos_Aires',
                }
            }
            
            # Agregar campos opcionales
            if description:
                event['description'] = description
            if location:
                event['location'] = location
            
            # Ejecutar creación
            result = self.google_calendar.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            logger.info(f"✅ Evento creado: {result.get('htmlLink')}")
            
            return {
                'event_id': result['id'],
                'link': result.get('htmlLink'),
                'status': 'created'
            }
            
        except Exception as e:
            logger.error(f"❌ Error creando evento: {e}")
            # ✅ Retornar error dict en lugar de raise (fail-safe para background tasks)
            return {
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # ==========================================
    # DESPACHADOR GENÉRICO
    # ==========================================
    
    def execute(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Despachador genérico de herramientas.
        
        El modelo solicita una herramienta, Python la ejecuta ciegamente.
        
        Args:
            tool_name: Nombre de la herramienta (e.g., "calendar_add")
            args: Argumentos para la herramienta
        
        Returns:
            Resultado de la ejecución de la herramienta
        
        Raises:
            ValueError: Si la herramienta no existe
        """
        # Mapeo de nombres a funciones
        tools = {
            'calendar_add': self.calendar_add,
            # Futuras herramientas:
            # 'notion_create': self.notion_create,
            # 'reminder_set': self.reminder_set,
            # 'email_send': self.email_send,
        }
        
        if tool_name not in tools:
            raise ValueError(f"Herramienta desconocida: {tool_name}")
        
        # Ejecutar herramienta
        tool_func = tools[tool_name]
        return tool_func(**args)
    
    def get_available_tools(self) -> Dict[str, str]:
        """
        Retorna lista de herramientas disponibles con sus descripciones.
        
        Útil para debugging y para que el modelo sepa qué puede usar.
        """
        return {
            'calendar_add': 'Agregar evento a Google Calendar con fecha ISO exacta',
            # 'notion_create': 'Crear página en Notion',
            # 'reminder_set': 'Configurar recordatorio',
        }
