import json
import logging
import asyncio
import os
from google import genai
from google.genai import types
from typing import Optional
from src.config import Config
from src.schemas import IntelligenceOutput, MemoryCategory

# DSPy imports
try:
    from src.dspy_modules import configure_dspy, UnifiedAnalyzer
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    logging.warning("DSPy no disponible, usando método tradicional")

logger = logging.getLogger(__name__)

class IntelligenceService:
    FALLBACK_MODEL = "gemini-1.5-flash"  # Fallback cuando se agota quota
    
    def __init__(self):
        # Initialize new google-genai client
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        self.model_name = Config.LLM_MODEL_NAME
        
        # 🧠 DSPy: Cargar cerebro compilado si está disponible
        self.dspy_analyzer = None
        if DSPY_AVAILABLE:
            try:
                configure_dspy()
                self.dspy_analyzer = UnifiedAnalyzer()
                
                # Cargar cerebro compilado si existe
                brain_path = os.path.join(os.path.dirname(__file__), '../../void_brain.json')
                if os.path.exists(brain_path):
                    self.dspy_analyzer.load(brain_path)
                    logging.info("🧠 Cerebro DSPy cargado exitosamente")
                else:
                    logging.warning(f"⚠️ Cerebro DSPy no encontrado en {brain_path}")
            except Exception as e:
                logger.error(f"Error cargando DSPy: {e}")
                self.dspy_analyzer = None
    
    async def _generate_with_fallback(self, model: str, contents: str, config=None):
        """Helper para generar contenido con fallback automático si se agota quota."""
        try:
            return await self.client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
        except Exception as e:
            error_msg = str(e)
            # Detectar error 429 RESOURCE_EXHAUSTED
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                logger.warning(f"⚠️ Quota agotada para {model}, usando fallback: {self.FALLBACK_MODEL}")
                # Reintentar con modelo fallback
                return await self.client.aio.models.generate_content(
                    model=self.FALLBACK_MODEL,
                    contents=contents,
                    config=config
                )
            else:
                # Si no es error de quota, re-lanzar la excepción
                raise

    async def analyze_input(self, text: str) -> 'UnifiedOutput':
        """
        🚀 MÉTODO UNIFICADO: Análisis completo en UNA sola llamada LLM.
        Reemplaza: refine_memory() + detect_intent() + classify_action()
        
        Retorna: tipo (ACTION/MEMORY), categoría, entidades extraídas, texto limpio, 
                 ubicación, recordatorios, etc.
        """
        from src.schemas import UnifiedOutput
        from datetime import datetime, timedelta
        
        # 🕐 CONTEXTO TEMPORAL: Inyectar fecha/hora actual
        now = datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M:%S %A")
        tomorrow_date = (now + timedelta(days=1)).strftime('%Y-%m-%d')
        day_after_tomorrow = (now + timedelta(days=2)).strftime('%Y-%m-%d')
        
        prompt = f"""
CONTEXTO TEMPORAL:
Fecha y hora actual: {current_datetime}
Zona horaria: America/Argentina/Buenos_Aires

Analiza el siguiente input de voz y extrae TODA la información en un solo JSON:

Input: "{text}"

Tareas:
1. Limpia ruido (ehh, umm, saludos, repeticiones)
2. Detecta si es ACTION (tarea/evento/recordatorio) o MEMORY (nota/idea/información)
3. Clasifica categoría específica:
   - Para ACTION: 
     * CALENDAR: Cualquier evento con fecha/hora específica (incluso si menciona "recordatorio")
     * TODO: Tareas sin fecha específica
     * REMINDER: Solo recordatorios vagos SIN fecha/hora específica (ej: "recordarme comprar leche")
   - Para MEMORY: FACT (hechos), IDEA (ideas), JOURNAL (diario), GOAL (metas)
4. Extrae entidades: fecha, hora, personas, lugares, ubicación física
5. Para eventos CALENDAR: genera un título corto y descriptivo (máximo 5 palabras)
6. Extrae ubicación física completa si se menciona (dirección, lugar, calle y número)
7. Extrae recordatorio si se menciona (ejemplos: "2 horas antes" → 120, "30 minutos antes" → 30, "1 día antes" → 1440)
8. Reescribe el texto limpio en 3ra persona de forma técnica

🔧 HERRAMIENTAS DISPONIBLES:
Si necesitas AGENDAR un evento en Google Calendar, usa la herramienta "calendar_add":
- Calcula la fecha ISO 8601 exacta (YYYY-MM-DDTHH:MM:SS)
- Ejemplo: "mañana a las 3pm" → "{tomorrow_date}T15:00:00"
- Ejemplo: "pasado mañana 10am" → "{day_after_tomorrow}T10:00:00"

Ejemplos:
- "Reunión con Juan mañana a las 3pm en calle Perón 342"
  → type: ACTION, category: CALENDAR, title: "Reunión con Juan", location: "Calle Perón 342",
     tool_name: "calendar_add", tool_args: {{"summary": "Reunión con Juan", "start_iso": "{tomorrow_date}T15:00:00", "duration_minutes": 60, "location": "Calle Perón 342"}}

- "Inscribirme a materias mañana 10 AM"
  → type: ACTION, category: CALENDAR, title: "Inscripción a materias",
     tool_name: "calendar_add", tool_args: {{"summary": "Inscripción a materias", "start_iso": "{tomorrow_date}T10:00:00", "duration_minutes": 60}}



- "Recordarme comprar leche" (SIN fecha/hora específica)
  → type: ACTION, category: REMINDER, title: "Comprar leche", tool_name: null

- "Pedro me comentó que le gusta el café"
  → type: MEMORY, category: FACT, refined_text: "A Pedro le gusta el café", tool_name: null

Responde SOLO con JSON válido (sin markdown):
{{
  "type": "ACTION" | "MEMORY",
  "category": "CALENDAR" | "TODO" | "REMINDER" | "FACT" | "IDEA" | "JOURNAL" | "GOAL",
  "refined_text": "texto limpio en 3ra persona",
  "title": "título corto del evento (solo para CALENDAR, máx 5 palabras)",
  "date": "fecha si se menciona (ej: mañana, pasado mañana, 25 de enero)",
  "time": "hora si se menciona (ej: 3pm, 15:00, mañana)",
  "location": "dirección completa si se menciona",
  "reminder_minutes": número entero de minutos antes para recordatorio (null si no se menciona),
  "entities": {{"person": "nombre", "place": "lugar"}},
  "tags": ["tag1", "tag2"],
  "confidence": 0.0-1.0,
  "tool_name": "calendar_add" (solo si es CALENDAR y necesitas agendar) | null,
  "tool_args": {{"summary": "...", "start_iso": "YYYY-MM-DDTHH:MM:SS", "duration_minutes": 60, "location": "..."}} (solo si tool_name no es null) | null
}}
"""
        try:
            response = await self._generate_with_fallback(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)
            return UnifiedOutput(**data)
        except Exception as e:
            logger.error(f"Error en análisis unificado: {e}")
            # Fallback seguro
            return UnifiedOutput(
                type="MEMORY",
                category="IDEA",
                refined_text=text,
                confidence=0.0
            )

    async def analyze_input_dspy(self, text: str) -> 'UnifiedOutput':
        """
        🧠 MÉTODO DSPy: Usa el cerebro compilado para análisis optimizado.
        Mucho más rápido y eficiente que analyze_input() tradicional.
        """
        from src.schemas import UnifiedOutput
        
        if not self.dspy_analyzer:
            # Fallback al método tradicional si DSPy no está disponible
            logging.warning("DSPy no disponible, usando método tradicional")
            return await self.analyze_input(text)
        
        try:
            # Ejecutar análisis con DSPy (usa prompts optimizados)
            result = self.dspy_analyzer(raw_text=text)
            
            # Convertir resultado DSPy a UnifiedOutput
            return UnifiedOutput(
                type=result.type,
                category=result.category,
                refined_text=result.refined_text,
                title=result.title if hasattr(result, 'title') else None,
                date=result.date if hasattr(result, 'date') else None,
                time=result.time if hasattr(result, 'time') else None,
                location=result.location if hasattr(result, 'location') else None,
                reminder_minutes=int(result.reminder_minutes) if hasattr(result, 'reminder_minutes') and result.reminder_minutes else None,
                confidence=float(result.confidence) if hasattr(result, 'confidence') else 0.0
            )
        except Exception as e:
            logging.error(f"Error en DSPy, fallback a método tradicional: {e}")
            return await self.analyze_input(text)

    async def refine_memory(self, text: str) -> Optional[str]:
        """Limpia el ruido usando IA (Async)"""
        prompt = f"""
        Eres un procesador de datos estricto.
        Input: "{text}"
        
        Tarea:
        1. Extrae el hecho/idea principal.
        2. Elimina ruido ("ehh", saludos).
        3. Reescribe en 3ra persona de forma técnica.
        4. Si no hay valor, responde: NULL
        
        Output (Solo texto):
        """
        try:
            # Llamada asíncrona para no bloquear
            response = await self._generate_with_fallback(
                model=self.model_name,
                contents=prompt
            )
            cleaned = response.text.strip()
            return None if "NULL" in cleaned or not cleaned else cleaned
        except Exception as e:
            logger.error(f"Error en refinamiento: {e}")
            return text # Fail-safe

    async def detect_intent(self, text: str) -> str:
        """Detecta si el input es una ACCIÓN o un RECUERDO"""
        prompt = f"""
        Analiza el siguiente texto y determina si es una ACCIÓN (tarea, evento, recordatorio) 
        o un RECUERDO (nota, idea, información para guardar).
        
        Texto: "{text}"
        
        Responde SOLO con una palabra: ACTION o MEMORY
        
        Ejemplos:
        - "Reunión con Juan mañana a las 3pm" -> ACTION
        - "Pedro me comentó que le gusta el café" -> MEMORY
        - "Recordarme comprar leche" -> ACTION
        - "La capital de Francia es París" -> MEMORY
        """
        try:
            response = await self._generate_with_fallback(
                model=self.model_name,
                contents=prompt
            )
            intent = response.text.strip().upper()
            return "ACTION" if "ACTION" in intent else "MEMORY"
        except Exception as e:
            logger.error(f"Error detectando intención: {e}")
            return "MEMORY"  # Default seguro

    async def classify_content(self, text: str) -> IntelligenceOutput:
        """Clasifica y extrae metadatos retornando un Objeto Pydantic"""
        prompt = f"""
        Analiza: "{text}"
        Categorías válidas: {', '.join([c.value for c in MemoryCategory])}
        
        Responde JSON estricto:
        {{
            "category": "...",
            "confidence": 0.0-1.0,
            "tags": ["..."],
            "entities": {{}}
        }}
        """
        try:
            response = await self._generate_with_fallback(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)
            # Validación automática con Pydantic
            return IntelligenceOutput(**data)
        except Exception as e:
            logger.error(f"Error clasificando: {e}")
            # Retorno por defecto seguro
            return IntelligenceOutput(category=MemoryCategory.IDEA, confidence=0.0)

    async def classify_action(self, text: str) -> 'ActionOutput':
        """Clasifica acciones específicas (CALENDAR, TODO, REMINDER)"""
        from src.schemas import ActionOutput, ActionCategory
        
        prompt = f"""
        Analiza el siguiente texto y determina qué tipo de ACCIÓN es:
        
        Texto: "{text}"
        
        Categorías válidas: {', '.join([c.value for c in ActionCategory])}
        
        - CALENDAR: Eventos, reuniones, citas con fecha/hora
        - TODO: Tareas, recordatorios de hacer algo, listas
        - REMINDER: Recordatorios simples sin fecha específica
        
        Responde JSON estricto:
        {{
            "category": "CALENDAR" | "TODO" | "REMINDER",
            "confidence": 0.0-1.0,
            "tags": ["..."],
            "entities": {{
                "date": "fecha si se menciona",
                "time": "hora si se menciona",
                "person": "persona si se menciona"
            }}
        }}
        
        Ejemplos:
        - "Reunión con Juan mañana a las 3pm" -> CALENDAR
        - "Recordarme comprar leche" -> TODO
        - "Agendar llamada con el cliente" -> CALENDAR
        - "Agregar tarea en Notion" -> TODO
        """
        try:
            response = await self._generate_with_fallback(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)
            return ActionOutput(**data)
        except Exception as e:
            logger.error(f"Error clasificando acción: {e}")
            return ActionOutput(category=ActionCategory.TODO, confidence=0.0)

    async def generate_embedding(self, text: str) -> list[float]:
        """Genera embeddings de forma verdaderamente asíncrona."""
        try:
            # Usar el nuevo SDK con async nativo
            # FIX: Forzar 768 dimensiones para compatibilidad con Supabase
            response = await self.client.aio.models.embed_content(
                model=Config.EMBEDDING_MODEL_NAME,
                contents=text,
                config=types.EmbedContentConfig(
                    output_dimensionality=768  # Matryoshka embedding truncation
                )
            )
            # Acceder al vector usando la nueva API
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Error vectorizando: {e}")
            return []