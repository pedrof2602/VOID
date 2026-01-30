import requests
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import time

# --- CONFIGURACIÓN ---
API_URL = "http://localhost:8000/input/voice"
USER_ID = "98181061-0369-4267-9a9a-72f480744a2b"
SAMPLE_RATE = 44100
DURATION = 5  # Segundos de grabación

def record_audio(filename="temp_input.wav"):
    print(f"\n🎤 Grabando por {DURATION} segundos... ¡HABLA AHORA!")
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()  # Esperar a que termine
    wav.write(filename, SAMPLE_RATE, recording)
    print("✅ Grabación terminada.")

def send_to_void(filename):
    print("🚀 Enviando a VOID...")
    if not os.path.exists(filename):
        print("❌ Error: No se encontró el archivo de audio.")
        return

    try:
        with open(filename, 'rb') as f:
            files = {'file': (filename, f, 'audio/wav')}
            data = {'user_id': USER_ID}
            
            start_time = time.time()
            response = requests.post(API_URL, files=files, data=data)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                print(f"\n✨ ÉXITO ({latency:.2f}s)")
                print(f"📩 Respuesta del Servidor: {response.json()}")
                print("👀 Revisa tu tabla 'device_signals' en Supabase, ¡debería haber una fila nueva!")
            else:
                print(f"\n🔥 Error {response.status_code}: {response.text}")
                
    except Exception as e:
        print(f"\n☠️ Error de conexión: {e}")
        print("¿Está Docker corriendo?")

if __name__ == "__main__":
    print("--- VOID HARDWARE SIMULATOR ---")
    input("Presiona ENTER para comenzar a grabar...")
    
    record_audio()
    send_to_void("temp_input.wav")