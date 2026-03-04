"""
DSPy Modules para VOID Intelligence System

Los módulos son componentes reutilizables que usan las signatures.
"""
import dspy
from datetime import datetime, timedelta
from .signatures import UnifiedAnalysis, MemoryRefinement, IntentDetection, ActionClassification


class UnifiedAnalyzer(dspy.Module):
    """
    Módulo principal que realiza análisis unificado en una sola llamada.
    Optimizado para reducir latencia y costos.
    
    🆕 Ahora inyecta contexto temporal dinámicamente para cálculo de fechas.
    """
    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought(UnifiedAnalysis)
    
    def forward(self, raw_text: str):
        """
        Analiza el input de voz y extrae toda la información.
        
        🕐 Inyecta contexto temporal automáticamente para que el modelo
        pueda calcular fechas relativas (ej: "mañana" -> ISO date).
        
        Args:
            raw_text: Texto transcrito del audio
            
        Returns:
            dspy.Prediction con todos los campos extraídos
        """
        # 🕐 Generar Contexto Temporal
        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
        day_after_tomorrow = (now + timedelta(days=2)).strftime('%Y-%m-%d')
        
        # 🔧 Inyectar instrucciones de herramientas en el contexto
        context_str = f"""
FECHA ACTUAL: {now.strftime("%Y-%m-%d %H:%M:%S %A")}
ZONA HORARIA: America/Argentina/Buenos_Aires

HERRAMIENTAS DISPONIBLES:
- calendar_add(summary, start_iso, duration_minutes, location): Usa esto para agendar eventos.
  
  IMPORTANTE: Para calcular fechas relativas, usa la fecha actual como referencia:
  - "mañana" -> '{tomorrow}'
  - "pasado mañana" -> '{day_after_tomorrow}'
  
  Ejemplos de start_iso:
  - "mañana 10am" -> '{tomorrow}T10:00:00'
  - "mañana 3pm" -> '{tomorrow}T15:00:00'
  
  Argumentos requeridos:
  - summary: Título del evento
  - start_iso: Fecha/hora ISO 8601
  - duration_minutes: int (default 60)

- send_email(to, subject, body): Usa esto para enviar correos electrónicos.
  Argumentos requeridos:
  - to: dirección de correo del destinatario
  - subject: asunto formal y descriptivo
  - body: cuerpo completo del correo, redactado de forma profesional y autónoma
           en primera persona, basándote en la intención del usuario.
           NO esperes que el usuario dicte el texto; redáctalo tú mismo.

⚡ REGLAS OBLIGATORIAS DE EJECUCIÓN:
Si detectas que la intención es agendar una reunión o evento:
1. Asigna 'ACTION' al campo type.
2. Asigna 'CALENDAR' al campo category.
3. TU DEBES ASIGNAR 'calendar_add' al campo tool_name. (No lo dejes vacío).

Si detectas que la intención es enviar un correo electrónico:
1. Asigna 'ACTION' al campo type.
2. Asigna 'TODO' al campo category.
3. TU DEBES ASIGNAR 'send_email' al campo tool_name con to, subject y body.
"""
        
        return self.analyze(raw_text=raw_text, context=context_str)


class MemoryRefiner(dspy.Module):
    """Módulo para refinar y limpiar texto de memoria"""
    def __init__(self):
        super().__init__()
        self.refine = dspy.Predict(MemoryRefinement)
    
    def forward(self, raw_input: str):
        return self.refine(raw_input=raw_input)


class IntentDetector(dspy.Module):
    """Módulo para detectar intención (ACTION vs MEMORY)"""
    def __init__(self):
        super().__init__()
        self.detect = dspy.Predict(IntentDetection)
    
    def forward(self, text: str):
        return self.detect(text=text)


class ActionClassifier(dspy.Module):
    """Módulo para clasificar tipo de acción"""
    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought(ActionClassification)
    
    def forward(self, text: str):
        return self.classify(text=text)
