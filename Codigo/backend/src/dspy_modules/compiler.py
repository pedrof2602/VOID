"""
src/dspy_modules/compiler.py
Script de entrenamiento y optimización.
"""
import dspy
import os
from dspy.teleprompt import BootstrapFewShot
from .config import configure_dspy
from .modules import UnifiedAnalyzer

def compile_void():
    print("🚀 Iniciando compilación de VOID Intelligence System...")
    
    # 1. Conectar con Gemini
    configure_dspy()
    
    # 2. DEFINIR EL "LIBRO DE TEXTO" (Training Data)
    # Aquí le enseñamos a VOID con ejemplos perfectos.
    train_data = [
        # --- CALENDARIO ---
        
        # --- CASO 6: CORRECCIÓN EN EL MOMENTO (Muy común hablando) ---
        dspy.Example(
            raw_text="Agendar reunión con Pedro... no, espera, mejor con Pablo el lunes",
            type="ACTION",
            category="CALENDAR",
            refined_text="El usuario corrige su petición inicial: agendar reunión con Pablo el lunes.",
            title="Reunión con Pablo",
            date="lunes",
            time="", # No dijo hora
            location="",
            reminder_minutes="15",
            confidence="0.85"
        ).with_inputs('raw_text'),

        # --- CASO 7: AMBIGÜEDAD (¿Deseo o Acción?) ---
        # "Quiero ir al cine" sin fecha suele ser un deseo (MEMORY), no una cita (CALENDAR).
        dspy.Example(
            raw_text="Tengo muchas ganas de ir a ver la nueva de Batman",
            type="MEMORY",
            category="IDEA", # O 'WISH'
            refined_text="El usuario expresa deseo de ver la nueva película de Batman.",
            title="",
            date="",
            time="",
            location="",
            reminder_minutes="0",
            confidence="0.90"
        ).with_inputs('raw_text'),

        # --- CASO 8: RECORDATORIO RELATIVO (Inferencia temporal) ---
        dspy.Example(
            raw_text="Avísame en 20 minutos que saque la pizza del horno",
            type="ACTION",
            category="REMINDER", # O TODO con reminder
            refined_text="Recordatorio para sacar la pizza del horno en 20 minutos.",
            title="Sacar pizza horno",
            date="hoy",
            time="in 20 minutes", # El parser de fechas luego manejará esto
            location="",
            reminder_minutes="0",
            confidence="0.99"
        ).with_inputs('raw_text'),

        # --- CASO 9: INFORMACIÓN TÉCNICA/ESTUDIO (Tu contexto de ingeniería) ---
        dspy.Example(
            raw_text="La fórmula de Green relaciona una integral de línea con una doble",
            type="MEMORY",
            category="FACT", # O 'STUDY'
            refined_text="Concepto de Cálculo: Teorema de Green relaciona integral de línea con doble.",
            title="",
            date="",
            time="",
            location="",
            reminder_minutes="0",
            confidence="0.95"
        ).with_inputs('raw_text'),

        # --- CASO 10: NEGATIVA O CANCELACIÓN ---
        dspy.Example(
            raw_text="Olvida lo que dije antes, no es importante",
            type="MEMORY", # O una categoría especial 'IGNORE'
            category="FACT",
            refined_text="El usuario indica descartar la instrucción previa.",
            title="",
            date="",
            time="",
            location="",
            reminder_minutes="0",
            confidence="0.10" # Baja confianza porque no hay contenido real
        ).with_inputs('raw_text'),
    ]

    # 3. EL MAESTRO (Teleprompter)
    # BootstrapFewShot toma tus ejemplos y crea el mejor prompt posible.
    print(f"📚 Entrenando con {len(train_data)} ejemplos...")
    teleprompter = BootstrapFewShot(metric=None, max_labeled_demos=5)
    
    # 4. COMPILAR (Optimizar el módulo)
    # Aquí es donde DSPy hace su magia.
    compiled_void = teleprompter.compile(UnifiedAnalyzer(), trainset=train_data)
    
    # 5. GUARDAR CEREBRO
    output_path = "void_brain.json"
    compiled_void.save(output_path)
    print(f"✅ Cerebro optimizado guardado en: {output_path}")

    # 6. PRUEBA FINAL
    print("\n--- PRUEBA DE DIAGNÓSTICO ---")
    test_input = "Llamar al mecánico el martes por la tarde"
    print(f"Input: '{test_input}'")
    pred = compiled_void(raw_text=test_input)
    print(f"Predicción -> Tipo: {pred.type} | Categoría: {pred.category}")
    print(f"Título: {pred.title}")
    # ✅ CORREGIDO: Eliminado pred.reasoning (no existe en la signature)
    # Si quieres ver el razonamiento, usa ChainOfThought y accede a pred.rationale
    if hasattr(pred, 'rationale'):
        print(f"Razonamiento: {pred.rationale}")

if __name__ == "__main__":
    compile_void()