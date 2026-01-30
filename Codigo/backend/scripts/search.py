import os
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

# --- CONFIGURACIÓN ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Inicializamos clientes
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GOOGLE_API_KEY)

def search_memory(query_text):
    print(f"\n🕵️  Buscando en tu Segundo Cerebro: '{query_text}'...")

    # 1. Vectorizar la pregunta (Convertir texto a números)
    # IMPORTANTE: Usar el mismo modelo que usamos al guardar (embedding-004)
    try:
        embedding_resp = genai.embed_content(
            model="models/text-embedding-004",
            content=query_text,
            task_type="retrieval_query" # Le avisamos a Google que esto es una búsqueda
        )
        query_vector = embedding_resp['embedding']
    except Exception as e:
        print(f"❌ Error al vectorizar (Quota o Red): {e}")
        return

    # 2. Llamar a Supabase (Función match_memories)
    try:
        response = supabase.rpc("match_memories", {
            "query_embedding": query_vector,
            "match_threshold": 0.45, # Umbral de similitud (0.0 a 1.0). 0.5 es exigente, 0.3 es laxo.
            "match_count": 5         # Cuántos resultados traer
        }).execute()
        
        matches = response.data
        
        if not matches:
            print("🤷 No encontré nada relacionado semánticamente.")
        else:
            print(f"✅ Encontré {len(matches)} recuerdos relevantes:\n")
            for m in matches:
                # Convertimos similitud a porcentaje
                score = m['similarity'] * 100
                print(f"   🔹 [{score:.1f}%] {m['content']}")
                print(f"       📅 {m['created_at']}")
                print("       -------")

    except Exception as e:
        print(f"❌ Error en base de datos: {e}")

if __name__ == "__main__":
    print("--- BUSCADOR SEMÁNTICO V1 ---")
    while True:
        q = input("\n🔍 Pregunta (o 'salir'): ")
        if q.lower() in ['salir', 'exit']: break
        if q.strip(): search_memory(q)