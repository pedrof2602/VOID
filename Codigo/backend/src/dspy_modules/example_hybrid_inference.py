"""
Ejemplo de uso de Hybrid Inference con DSPy
============================================

Demuestra cómo usar Fast Engine vs Power Engine según la complejidad de la tarea.
"""
import asyncio
from src.dspy_modules.config import (
    configure_dspy,
    get_powerful_model,
    get_model_info,
    MODEL_LITE,
    MODEL_POWER
)
import dspy

# Ejemplo de módulo simple (usa Fast Engine)
class SimpleClassifier(dspy.Module):
    """Clasificador simple que usa el Fast Engine por defecto"""
    def __init__(self):
        super().__init__()
        self.classify = dspy.Predict("text -> category")
    
    def forward(self, text):
        return self.classify(text=text)


# Ejemplo de módulo complejo (usa Power Engine)
class ComplexReasoner(dspy.Module):
    """Razonador complejo que usa el Power Engine"""
    def __init__(self):
        super().__init__()
        self.reason = dspy.ChainOfThought("problem -> solution, reasoning")
    
    def forward(self, problem):
        return self.reason(problem=problem)


async def demo_hybrid_inference():
    """Demuestra el uso de ambos engines"""
    
    print("🚀 Configurando DSPy con Hybrid Inference...\n")
    
    # 1. Configurar Fast Engine como default
    configure_dspy()
    print(f"✅ Fast Engine configurado: {MODEL_LITE}")
    
    # 2. Mostrar info de modelos
    info = get_model_info()
    print(f"\n📊 Modelos disponibles:")
    print(f"  Fast: {info['fast_engine']['model']} - {info['fast_engine']['quota']}")
    print(f"  Power: {info['power_engine']['model']} - {info['power_engine']['quota']}")
    
    # 3. Tarea simple con Fast Engine (automático)
    print(f"\n{'='*60}")
    print("🏃 Tarea Simple (Fast Engine)")
    print(f"{'='*60}")
    
    simple_task = SimpleClassifier()
    result_simple = simple_task(text="Reunión mañana a las 3pm")
    print(f"Input: 'Reunión mañana a las 3pm'")
    print(f"Resultado: {result_simple.category}")
    print(f"Motor usado: Fast Engine (automático)")
    
    # 4. Tarea compleja con Power Engine (explícito)
    print(f"\n{'='*60}")
    print("🧠 Tarea Compleja (Power Engine)")
    print(f"{'='*60}")
    
    # Obtener Power Engine
    power_lm = get_powerful_model()
    
    # Usar temporalmente el Power Engine
    complex_task = ComplexReasoner()
    
    with dspy.settings.context(lm=power_lm):
        result_complex = complex_task(
            problem="Analiza el impacto de implementar DSPy en producción"
        )
    
    print(f"Input: 'Analiza el impacto de implementar DSPy...'")
    print(f"Solución: {result_complex.solution}")
    print(f"Razonamiento: {result_complex.reasoning}")
    print(f"Motor usado: Power Engine (explícito)")
    
    print(f"\n{'='*60}")
    print("✅ Demo completada!")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(demo_hybrid_inference())
