"""
Script para regenerar el token de Google Calendar.
Ejecutar cuando el token expire o se revoque.
"""
import os
import pickle
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes para Google Calendar
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send'
    ]

def regenerate_token(): #coment
    """Regenera el token de Google Calendar."""
    # Rutas
    token_path = Path(__file__).parent.parent / 'src' / 'services' / 'token.pickle'
    credentials_path = Path(__file__).parent.parent / 'src' / 'services' / 'credentials.json'
    
    print(f"📂 Token path: {token_path}")
    print(f"📂 Credentials path: {credentials_path}")
    
    if not credentials_path.exists():
        print(f"❌ ERROR: No se encontró credentials.json en {credentials_path}")
        print("   Descarga las credenciales desde Google Cloud Console")
        return
    
    print("\n🔐 Iniciando flujo de autenticación...")
    print("   Se abrirá tu navegador para autenticarte con Google")
    
    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path), SCOPES
    )
    creds = flow.run_local_server(port=0)
    
    # Guardar token
    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)
    
    print(f"\n✅ Token guardado exitosamente en: {token_path}")
    print("   Reinicia el backend para usar el nuevo token")

if __name__ == '__main__':
    regenerate_token()
