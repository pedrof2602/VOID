"""
tests/test_gmail_routing.py
Smoke test para verificar que ToolRegistry enruta send_email correctamente.
Usa unittest.mock para evitar llamadas reales a la API de Gmail.
"""
import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_send_email_routing():
    """
    Verifica que ToolRegistry.execute('send_email', {...}) llama a
    GmailService.send_email con los parámetros correctos.
    """
    from src.services.tools import ToolRegistry

    async def _run():
        # Mock de GmailService para no tocar la red
        mock_gmail = MagicMock()
        mock_gmail.send_email = AsyncMock(return_value={
            "status": "sent",
            "message_id": "mock-id-123",
            "to": "test@example.com",
            "subject": "Asunto de prueba",
        })

        # Parchear la inicialización de ToolRegistry para evitar dependencias OAuth
        with patch("src.services.tools.GmailService", return_value=mock_gmail), \
             patch.object(ToolRegistry, "_init_google_calendar", return_value=None):

            registry = ToolRegistry()
            registry.gmail = mock_gmail

            args = {
                "to": "test@example.com",
                "subject": "Asunto de prueba",
                "body": "Cuerpo del correo de prueba.",
            }

            result = await registry.execute("send_email", args)

            # Verificar que el mock fue llamado con los args correctos
            mock_gmail.send_email.assert_called_once_with(
                to_email="test@example.com",
                subject="Asunto de prueba",
                body="Cuerpo del correo de prueba.",
            )

            # Verificar el resultado
            assert result["status"] == "sent", f"Estado inesperado: {result}"
            assert result["message_id"] == "mock-id-123"
            print("✅ send_email routing: OK")
            return result

    return asyncio.run(_run())


def test_unknown_tool_raises():
    """Verifica que una herramienta desconocida lanza ValueError."""
    from src.services.tools import ToolRegistry

    async def _run():
        with patch("src.services.tools.GmailService", return_value=MagicMock()), \
             patch.object(ToolRegistry, "_init_google_calendar", return_value=None):

            registry = ToolRegistry()

            try:
                await registry.execute("herramienta_inexistente", {})
                assert False, "Debería haber lanzado ValueError"
            except ValueError as e:
                assert "herramienta_inexistente" in str(e)
                print("✅ unknown tool raises ValueError: OK")

    asyncio.run(_run())


def test_calendar_add_routing():
    """Verifica que calendar_add sigue siendo accesible desde el dispatcher."""
    from src.services.tools import ToolRegistry

    async def _run():
        mock_calendar = MagicMock()
        mock_calendar.events.return_value.insert.return_value.execute.return_value = {
            "id": "cal-event-123",
            "htmlLink": "https://calendar.google.com/event?id=cal-event-123",
        }

        with patch("src.services.tools.GmailService", return_value=MagicMock()), \
             patch.object(ToolRegistry, "_init_google_calendar", return_value=mock_calendar):

            registry = ToolRegistry()

            args = {
                "summary": "Reunión de prueba",
                "start_iso": "2026-03-10T10:00:00",
                "duration_minutes": 60,
            }

            result = await registry.execute("calendar_add", args)
            assert result["status"] == "created", f"Estado inesperado: {result}"
            print("✅ calendar_add routing: OK")

    asyncio.run(_run())


if __name__ == "__main__":
    print("[TEST] Ejecutando smoke tests del ToolRegistry...\n")
    test_send_email_routing()
    test_unknown_tool_raises()
    test_calendar_add_routing()
    print("\n[PASS] Todos los tests pasaron.")
