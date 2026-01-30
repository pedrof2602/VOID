"""
Ejemplo de uso de DSPy para VOID Intelligence System

Este archivo muestra cómo usar los módulos DSPy configurados.
"""
import asyncio
from src.dspy_modules import configure_dspy, UnifiedAnalyzer


async def example_unified_analysis():
    """Ejemplo de análisis unificado con DSPy"""
    
    # 1. Configurar DSPy (hacer esto UNA VEZ al inicio de la app)
    print("🔧 Configurando DSPy con Gemini...")
    configure_dspy()
    
    # 2. Crear el módulo de análisis
    analyzer = UnifiedAnalyzer()
    
    # 3. Analizar diferentes inputs
    test_cases = [
        "Inscribirme a materias mañana 10 AM poner recordatorio 1 hora antes",
        "Reunión con cliente mañana a las 3pm en calle Perón al 342",
        "Pedro me comentó que le gusta el café"
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Input: {test}")
        print(f"{'='*60}")
        
        # Ejecutar análisis
        result = analyzer(raw_text=test)
        
        # Mostrar resultados
        print(f"Type: {result.type}")
        print(f"Category: {result.category}")
        print(f"Title: {result.title}")
        print(f"Refined: {result.refined_text}")
        print(f"Date: {result.date}")
        print(f"Time: {result.time}")
        print(f"Location: {result.location}")
        print(f"Reminder: {result.reminder_minutes}")
        print(f"Confidence: {result.confidence}")


if __name__ == "__main__":
    asyncio.run(example_unified_analysis())
