"""
DSPy Signatures para VOID Intelligence System

Las signatures definen la estructura de entrada/salida para los módulos DSPy.
"""
import dspy


class UnifiedAnalysis(dspy.Signature):
    """
    Signature para análisis unificado de input de voz.
    Reemplaza múltiples llamadas LLM con una sola estructura optimizada.
    
    🆕 Ahora incluye soporte para ejecución autónoma de herramientas.
    """
    # Inputs
    raw_text = dspy.InputField(desc="Texto transcrito del audio del usuario")
    context = dspy.InputField(desc="Fecha actual, hora y lista de herramientas disponibles")
    
    # Outputs Standard
    type = dspy.OutputField(desc="Tipo de input: 'ACTION' o 'MEMORY'")
    category = dspy.OutputField(desc="Categoría específica: CALENDAR, TODO, REMINDER, FACT, IDEA, etc.")
    refined_text = dspy.OutputField(desc="Texto limpio sin ruido, en 3ra persona")
    title = dspy.OutputField(desc="Título corto del evento (solo para CALENDAR, máx 5 palabras)")
    date = dspy.OutputField(desc="Fecha extraída si se menciona")
    time = dspy.OutputField(desc="Hora extraída si se menciona")
    location = dspy.OutputField(desc="Ubicación física si se menciona")
    reminder_minutes = dspy.OutputField(desc="Minutos antes para recordatorio (número entero)")
    confidence = dspy.OutputField(desc="Confianza de la clasificación (0.0-1.0)")
    
    # 🆕 Outputs para Herramientas (Autonomous Tool Execution)
    tool_name = dspy.OutputField(desc="SIEMPRE que la category sea 'CALENDAR', este campo DEBE SER 'calendar_add'. Si no, None.")
    tool_args = dspy.OutputField(desc="Diccionario con los argumentos exactos para la herramienta (ej: {'summary': 'Dentista', 'start_iso': '2026-01-30T17:00:00'}).")


class MemoryRefinement(dspy.Signature):
    """Limpia y refina texto de memoria"""
    raw_input = dspy.InputField(desc="Texto crudo con posible ruido")
    refined_output = dspy.OutputField(desc="Texto limpio en 3ra persona, técnico")


class IntentDetection(dspy.Signature):
    """Detecta si el input es una acción o un recuerdo"""
    text = dspy.InputField(desc="Texto a analizar")
    intent = dspy.OutputField(desc="'ACTION' o 'MEMORY'")


class ActionClassification(dspy.Signature):
    """Clasifica el tipo específico de acción"""
    text = dspy.InputField(desc="Texto de la acción")
    category = dspy.OutputField(desc="'CALENDAR', 'TODO', o 'REMINDER'")
    date = dspy.OutputField(desc="Fecha si se menciona")
    time = dspy.OutputField(desc="Hora si se menciona")
    location = dspy.OutputField(desc="Ubicación si se menciona")
