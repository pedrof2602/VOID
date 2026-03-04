"""
VOID Gmail Service
==================

Envía correos a través de la API oficial de Gmail usando OAuth2,
reutilizando el mismo flujo de credenciales de Google Calendar.

Filosofía: Silent Execution — el servicio actúa de forma autónoma
sin requerir intervención del usuario más allá de la autorización OAuth.

Author: VOID Intelligence Team
"""
import asyncio
import base64
import logging
import os
import pickle
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Scopes necesarios: Calendar (heredado) + Gmail send
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
]


class GmailService:
    """
    Servicio de Gmail para el envío autónomo de correos.

    Reutiliza las credenciales OAuth2 existentes (token.pickle /
    credentials.json) y expone un método async send_email().

    ⚠️  IMPORTANTE: Si el token.pickle actual no incluye el scope
    gmail.send, debe regenerarse ejecutando el flujo OAuth una vez.
    El servicio detecta este caso y retorna un dict de error sin
    crashear el servidor (fail-safe).
    """

    def __init__(self) -> None:
        self._service = self._init_gmail_service()

    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------

    def _init_gmail_service(self):
        """Carga credenciales y construye el cliente de Gmail API."""
        token_path = Path(
            os.getenv(
                "GOOGLE_TOKEN_PATH",
                str(Path(__file__).parent / "token.pickle"),
            )
        )
        credentials_path = Path(
            os.getenv(
                "GOOGLE_CREDENTIALS_PATH",
                str(Path(__file__).parent / "credentials.json"),
            )
        )

        creds: Credentials | None = None

        # Intentar cargar token existente
        if token_path.exists():
            with open(token_path, "rb") as token_file:
                creds = pickle.load(token_file)

        # Refrescar si el token expiró
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as exc:
                logger.warning(
                    f"⚠️ No se pudo refrescar el token de Google: {exc}. "
                    "Gmail deshabilitado — regenera el token localmente."
                )
                return None

        # Si no hay credenciales válidas, no podemos iniciar
        if not creds or not creds.valid:
            if credentials_path.exists():
                logger.warning(
                    "⚠️ Token de Google inválido o ausente. "
                    "Gmail deshabilitado — ejecuta el flujo OAuth para regenerarlo."
                )
            else:
                logger.warning(
                    "⚠️ credentials.json no encontrado. Gmail deshabilitado."
                )
            return None

        # Verificar que el scope gmail.send esté presente
        granted_scopes = getattr(creds, "scopes", None) or []
        if granted_scopes and "https://www.googleapis.com/auth/gmail.send" not in granted_scopes:
            logger.warning(
                "⚠️ El token actual no incluye el scope gmail.send. "
                "Regenera token.pickle para activar el envío de correos."
            )
            return None

        try:
            service = build("gmail", "v1", credentials=creds)
            logger.info("✅ GmailService inicializado correctamente")
            return service
        except Exception as exc:
            logger.error(f"❌ Error construyendo el cliente de Gmail: {exc}")
            return None

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    async def send_email(
        self, to_email: str, subject: str, body: str
    ) -> Dict[str, Any]:
        """
        Envía un correo de forma asíncrona usando la API de Gmail.

        Args:
            to_email: Dirección de destino.
            subject:  Asunto del correo.
            body:     Cuerpo del mensaje (texto plano).

        Returns:
            Dict con 'status': 'sent' | 'error' y metadatos adicionales.
        """
        if not self._service:
            error_msg = (
                "GmailService no está disponible. "
                "Verifica que token.pickle incluya el scope gmail.send."
            )
            logger.error(f"❌ {error_msg}")
            return {"status": "error", "error": error_msg}

        try:
            raw_message = self._build_raw_message(to_email, subject, body)
        except Exception as exc:
            logger.error(f"❌ Error construyendo el mensaje MIME: {exc}")
            return {"status": "error", "error": str(exc)}

        # Ejecutar la llamada bloqueante de la API en un thread pool
        # para no bloquear el event loop de FastAPI.
        try:
            result = await asyncio.to_thread(
                self._execute_send, raw_message
            )
            logger.info(f"✅ Correo enviado a {to_email} | ID: {result.get('id')}")
            return {
                "status": "sent",
                "message_id": result.get("id"),
                "thread_id": result.get("threadId"),
                "to": to_email,
                "subject": subject,
            }
        except Exception as exc:
            logger.error(f"❌ Error enviando correo a {to_email}: {exc}")
            return {"status": "error", "error": str(exc)}

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _build_raw_message(self, to_email: str, subject: str, body: str) -> dict:
        """
        Construye el payload 'raw' requerido por la API de Gmail.

        La API espera el mensaje codificado en base64url (RFC 4648 §5).
        Se usa `urlsafe_b64encode` y se decodifica a str para el JSON.
        """
        message = MIMEText(body, "plain", "utf-8")
        message["to"] = to_email
        message["subject"] = subject

        # Codificación base64url — evitar el padding '=' que rechaza la API
        encoded_bytes = base64.urlsafe_b64encode(message.as_bytes())
        raw = encoded_bytes.decode("utf-8").rstrip("=")
        return {"raw": raw}

    def _execute_send(self, raw_message: dict) -> dict:
        """Llamada síncrona a la API (se usa desde asyncio.to_thread)."""
        return (
            self._service
            .users()
            .messages()
            .send(userId="me", body=raw_message)
            .execute()
        )
