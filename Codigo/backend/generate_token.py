import os.path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_PATH = 'src/services/credentials.json'
TOKEN_PATH = 'token.json'

def main():
    print("🛠️ Iniciando generación de token OAuth...")
    
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"❌ Error: No se encuentra '{CREDENTIALS_PATH}'")
        print("   Descarga las credenciales desde Google Cloud Console")
        print("   y guárdalas en src/services/credentials.json")
        return

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH, SCOPES)

        # Ejecuta el servidor local y abre el navegador automáticamente
        # Puerto 0 = selecciona un puerto disponible automáticamente
        print("\n🌐 Abriendo navegador para autorización...")
        print("   Si no se abre automáticamente, copia la URL que aparecerá abajo\n")
        
        creds = flow.run_local_server(port=0)

        # Guardar el token
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            
        print(f"\n✅ ¡LISTO! {TOKEN_PATH} creado exitosamente.")
        print("   Ahora puedes usar este token para autenticar la API.\n")
        
    except Exception as e:
        print(f"\n❌ Error durante la autorización: {e}")
        print("   Verifica que credentials.json sea válido y que tengas acceso a internet.\n")

if __name__ == '__main__':
    main()