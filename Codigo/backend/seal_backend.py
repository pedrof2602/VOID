import os
import sys

# Aseguramos que Python encuentre la carpeta services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.services.intelligence import IntelligenceService
    print("🧠 Inicializando Cerebro con nueva lógica ChainOfThought...")
    
    # Esto carga la clase con la nueva lógica (ChainOfThought) que editamos en modules.py
    # No necesita entrenamiento, solo inicializarse para establecer la estructura.
    service = IntelligenceService()

    # Verificar que DSPy se haya inicializado correctamente
    if service.dspy_analyzer is None:
        print("❌ ERROR: DSPy no se inicializó correctamente.")
        print("📋 Posibles causas:")
        print("   1. DSPy no está instalado: pip install dspy-ai")
        print("   2. Error en src/dspy_modules.py")
        print("   3. Falta configuración de API keys")
        print("\n Verifica los logs anteriores para más detalles.")
        sys.exit(1)

    print("💾 Guardando estado estructural del cerebro en void_brain.json...")
    # Forzamos el guardado. Esto crea el archivo que Docker necesita.
    service.dspy_analyzer.save("void_brain.json")

    print("✅ ¡ÉXITO! Archivo 'void_brain.json' generado correctamente.")
    print("👉 Ahora puedes descomentar la línea en tu Dockerfile.")

except Exception as e:
    print(f"❌ Error fatal: {e}")
    import traceback
    traceback.print_exc()