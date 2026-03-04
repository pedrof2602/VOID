"""
VOID Tool Registry - Autonomous Tool Execution
================================================

Filosofía: El modelo (DSPy/Gemini) decide QUÉ herramientas usar.
Python es un ejecutor ciego que solo obedece.

Author: VOID Intelligence Team
"""
import asyncio
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

# Gmail service
from src.services.gmail_service import GmailService

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
        self.gmail = GmailService()
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
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo refrescar el token de Google Calendar: {e}")
                    logger.warning("⚠️ Google Calendar deshabilitado - regenera el token localmente")
                    return None
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
    # HERRAMIENTAS ASÍNCRONAS
    # ==========================================

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
    ) -> Dict[str, Any]:
        """
        Envía un correo electrónico usando la API de Gmail.

        Args:
            to:      Dirección de correo del destinatario.
            subject: Asunto del correo.
            body:    Cuerpo del mensaje.

        Returns:
            Dict con 'status': 'sent' | 'error' y metadatos.
        """
        return await self.gmail.send_email(
            to_email=to,
            subject=subject,
            body=body,
        )

    # ==========================================
    # DESPACHADOR GENÉRICO (ASYNC)
    # ==========================================
    
    async def execute(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Despachador genérico de herramientas (async).
        
        Herramientas síncronas (e.g. calendar_add) se ejecutan dentro de
        asyncio.to_thread() para no bloquear el Event Loop.
        Herramientas asíncronas (e.g. send_email) se awaitan directamente.

        Args:
            tool_name: Nombre de la herramienta (e.g., "calendar_add", "send_email")
            args: Argumentos para la herramienta

        Returns:
            Resultado de la ejecución de la herramienta

        Raises:
            ValueError: Si la herramienta no existe
        """
        # Herramientas síncronas (ejecutadas en thread pool)
        sync_tools = {
            'calendar_add': self.calendar_add,
        }

        # Herramientas asíncronas (awaited directamente)
        async_tools = {
            'send_email': self.send_email,
        }

        if tool_name in sync_tools:
            return await asyncio.to_thread(sync_tools[tool_name], **args)

        if tool_name in async_tools:
            return await async_tools[tool_name](**args)

        raise ValueError(f"Herramienta desconocida: '{tool_name}'")
    
    def get_available_tools(self) -> Dict[str, str]:
        """
        Retorna lista de herramientas disponibles con sus descripciones.
        
        Útil para debugging y para que el modelo sepa qué puede usar.
        """
        return {
            'calendar_add': 'Agregar evento a Google Calendar con fecha ISO exacta',
            'send_email': 'Enviar correo electrónico vía Gmail API (OAuth2)',
        }
