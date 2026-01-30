"""
Script de prueba para verificar el método unificado analyze_input
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.intelligence import IntelligenceService

async def test_unified_analysis():
    print("🧪 Iniciando pruebas del análisis unificado...\n")
    
    brain = IntelligenceService()
    
    # Test 1: Evento simple
    print("=" * 60)
    print("Test 1: Evento simple")
    print("=" * 60)
    test1 = "Guardar en calendario e inscribirme a materias mañana en la mañana"
    result1 = await brain.analyze_input(test1)
    print(f"Input: {test1}")
    print(f"Type: {result1.type}")
    print(f"Category: {result1.category}")
    print(f"Title: {result1.title}")
    print(f"Refined: {result1.refined_text}")
    print(f"Date: {result1.date}")
    print(f"Time: {result1.time}")
    print()
    
    # Test 2: Evento con ubicación
    print("=" * 60)
    print("Test 2: Evento con ubicación")
    print("=" * 60)
    test2 = "Reunión con cliente mañana a las 3pm en calle Perón al 342"
    result2 = await brain.analyze_input(test2)
    print(f"Input: {test2}")
    print(f"Type: {result2.type}")
    print(f"Category: {result2.category}")
    print(f"Title: {result2.title}")
    print(f"Location: {result2.location}")
    print(f"Date: {result2.date}")
    print(f"Time: {result2.time}")
    print()
    
    # Test 3: Evento con recordatorio
    print("=" * 60)
    print("Test 3: Evento con recordatorio")
    print("=" * 60)
    test3 = "Agendar llamada con Juan pasado mañana a las 10am, avisarme 2 horas antes"
    result3 = await brain.analyze_input(test3)
    print(f"Input: {test3}")
    print(f"Type: {result3.type}")
    print(f"Category: {result3.category}")
    print(f"Title: {result3.title}")
    print(f"Reminder: {result3.reminder_minutes} minutos")
    print(f"Date: {result3.date}")
    print(f"Time: {result3.time}")
    print()
    
    # Test 4: Memoria (no acción)
    print("=" * 60)
    print("Test 4: Memoria (no acción)")
    print("=" * 60)
    test4 = "Pedro me comentó que le gusta el café"
    result4 = await brain.analyze_input(test4)
    print(f"Input: {test4}")
    print(f"Type: {result4.type}")
    print(f"Category: {result4.category}")
    print(f"Refined: {result4.refined_text}")
    print()
    
    print("✅ Pruebas completadas!")

if __name__ == "__main__":
    asyncio.run(test_unified_analysis())
