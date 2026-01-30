"""
Script de prueba para verificar la integración de DSPy en intelligence.py
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.intelligence import IntelligenceService

async def test_dspy_integration():
    print("🧪 Probando integración de DSPy en Intelligence Service...\n")
    
    # Inicializar servicio
    brain = IntelligenceService()
    
    # Verificar si DSPy está cargado
    if brain.dspy_analyzer:
        print("✅ DSPy cargado correctamente")
        print(f"📍 Cerebro compilado: {'Sí' if brain.dspy_analyzer else 'No'}\n")
    else:
        print("⚠️ DSPy no disponible, usando método tradicional\n")
    
    # Test cases
    test_cases = [
        "Inscribirme a materias mañana 10 AM poner recordatorio 1 hora antes",
        "Reunión con cliente mañana a las 3pm en calle Perón al 342",
        "Pedro me comentó que le gusta el café"
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"{'='*60}")
        print(f"Test {i}: {test}")
        print(f"{'='*60}")
        
        try:
            # Probar con DSPy si está disponible
            if brain.dspy_analyzer:
                print("🧠 Usando DSPy...")
                result = await brain.analyze_input_dspy(test)
            else:
                print("📝 Usando método tradicional...")
                result = await brain.analyze_input(test)
            
            # Mostrar resultados
            print(f"Type: {result.type}")
            print(f"Category: {result.category}")
            print(f"Title: {result.title}")
            print(f"Refined: {result.refined_text}")
            print(f"Date: {result.date}")
            print(f"Time: {result.time}")
            print(f"Location: {result.location}")
            print(f"Reminder: {result.reminder_minutes} min")
            print(f"Confidence: {result.confidence}")
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(test_dspy_integration())
