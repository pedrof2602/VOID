"""
Script para verificar el estado de la cuota de Gemini API
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("=" * 60)
print("🔍 VERIFICACIÓN DE CUOTA GEMINI API")
print("=" * 60)
print(f"⏰ Hora actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Modelos a probar (del menos al más restrictivo)
modelos_a_probar = [
    "gemini-2.0-flash",
    "gemini-2.5-flash-lite", 
    "gemini-2.5-flash"
]

for modelo_nombre in modelos_a_probar:
    try:
        print(f"📡 Probando: {modelo_nombre}")
        model = genai.GenerativeModel(modelo_nombre)
        
        # Intento simple
        response = model.generate_content("Di solo: OK")
        
        print(f"   ✅ FUNCIONA - Respuesta: {response.text.strip()}")
        print(f"   💡 Usa este modelo: {modelo_nombre}")
        print()
        
    except Exception as e:
        error_msg = str(e)
        
        if "429" in error_msg or "quota" in error_msg.lower():
            print(f"   ❌ CUOTA EXCEDIDA")
            
            # Intentar extraer tiempo de espera
            if "retry in" in error_msg.lower():
                import re
                match = re.search(r'retry in ([\d.]+)', error_msg)
                if match:
                    segundos = float(match.group(1))
                    minutos = segundos / 60
                    horas = minutos / 60
                    
                    if horas >= 1:
                        print(f"   ⏳ Espera: {horas:.1f} horas")
                    elif minutos >= 1:
                        print(f"   ⏳ Espera: {minutos:.1f} minutos")
                    else:
                        print(f"   ⏳ Espera: {segundos:.0f} segundos")
        else:
            print(f"   ⚠️ Error: {error_msg[:100]}")
        
        print()

print("=" * 60)
print("📊 OPCIONES DISPONIBLES:")
print("=" * 60)
print()
print("1️⃣  ESPERAR (Gratis)")
print("   - La cuota se resetea cada 24 horas")
print("   - Revisa el tiempo de espera arriba")
print()
print("2️⃣  AGREGAR TARJETA (Pay-as-you-go)")
print("   - Costo: ~$0.10 por 1M tokens")
print("   - Para 1,000 resúmenes: ~$0.10 USD")
print("   - Link: https://aistudio.google.com/app/apikey")
print()
print("3️⃣  USAR MODELO LOCAL (Gratis, sin límites)")
print("   - Ollama + Llama 3.2")
print("   - Ejecuta en tu PC, sin API")
print("   - Requiere: 8GB RAM mínimo")
print()
print("4️⃣  DESACTIVAR RESÚMENES TEMPORALMENTE")
print("   - Guardar solo transcripciones")
print("   - Generar resúmenes después")
print()
