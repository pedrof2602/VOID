# DSPy Modules - README

## Configuración de DSPy para VOID

Este módulo configura DSPy para usar Gemini como modelo de lenguaje.

### Estructura

```
src/dspy_modules/
├── __init__.py          # Exporta todos los componentes
├── config.py            # Configuración de DSPy con Gemini
├── signatures.py        # Definiciones de entrada/salida
├── compiler.py          # Módulos DSPy reutilizables
├── example_usage.py     # Ejemplos de uso
└── README.md           # Este archivo
```

### Uso Básico

#### 1. Configurar DSPy (una vez al inicio)

```python
from src.dspy_modules import configure_dspy

# Configurar DSPy con Gemini
configure_dspy()
```

#### 2. Usar el Analizador Unificado

```python
from src.dspy_modules import UnifiedAnalyzer

# Crear instancia
analyzer = UnifiedAnalyzer()

# Analizar input
result = analyzer(raw_text="Reunión mañana a las 3pm")

# Acceder a resultados
print(result.type)      # "ACTION"
print(result.category)  # "CALENDAR"
print(result.title)     # "Reunión"
```

### Módulos Disponibles

#### UnifiedAnalyzer
Análisis completo en una sola llamada (reemplaza 3 llamadas LLM).

```python
analyzer = UnifiedAnalyzer()
result = analyzer(raw_text="texto del usuario")
```

**Outputs:**
- `type`: ACTION o MEMORY
- `category`: CALENDAR, TODO, REMINDER, FACT, IDEA, etc.
- `refined_text`: Texto limpio
- `title`: Título corto (para eventos)
- `date`, `time`, `location`: Entidades extraídas
- `reminder_minutes`: Minutos antes para recordatorio
- `confidence`: Confianza de la clasificación

#### MemoryRefiner
Limpia y refina texto.

```python
refiner = MemoryRefiner()
result = refiner(raw_input="ehh, Pedro me dijo que...")
print(result.refined_output)  # "Pedro mencionó que..."
```

#### IntentDetector
Detecta si es acción o memoria.

```python
detector = IntentDetector()
result = detector(text="Reunión mañana")
print(result.intent)  # "ACTION"
```

#### ActionClassifier
Clasifica tipo de acción.

```python
classifier = ActionClassifier()
result = classifier(text="Agendar llamada mañana 3pm")
print(result.category)  # "CALENDAR"
```

### Configuración Avanzada

#### Usar modelo específico

```python
from src.dspy_modules import get_gemini_lm
import dspy

# Obtener LM personalizado
lm = get_gemini_lm(
    model_name="gemini-1.5-pro",
    temperature=0.3
)

# Configurar DSPy con este LM
dspy.settings.configure(lm=lm)
```

#### Modelos disponibles
- `gemini-2.0-flash-exp` (rápido, económico) ✅ Por defecto
- `gemini-1.5-pro` (más potente)
- `gemini-1.5-flash` (balance)

### Integración con Intelligence Service

Para integrar DSPy en el servicio existente:

```python
# En intelligence.py
from src.dspy_modules import configure_dspy, UnifiedAnalyzer

class IntelligenceService:
    def __init__(self):
        # Configurar DSPy
        configure_dspy()
        
        # Crear módulo
        self.dspy_analyzer = UnifiedAnalyzer()
    
    async def analyze_input_dspy(self, text: str):
        """Versión DSPy del análisis unificado"""
        result = self.dspy_analyzer(raw_text=text)
        
        # Convertir a UnifiedOutput
        return UnifiedOutput(
            type=result.type,
            category=result.category,
            refined_text=result.refined_text,
            title=result.title,
            date=result.date,
            time=result.time,
            location=result.location,
            reminder_minutes=int(result.reminder_minutes) if result.reminder_minutes else None,
            confidence=float(result.confidence)
        )
```

### Ventajas de DSPy

1. **Optimización automática**: DSPy puede optimizar prompts automáticamente
2. **Composición modular**: Combina módulos fácilmente
3. **Type safety**: Signatures definen tipos claramente
4. **Debugging**: Mejor trazabilidad de llamadas LLM
5. **Compilación**: Puede compilar pipelines para mejor performance

### Próximos Pasos

1. **Optimización con datos**: Usar `dspy.BootstrapFewShot` para mejorar con ejemplos
2. **Compilación**: Compilar módulos para reducir latencia
3. **Métricas**: Agregar evaluación automática de calidad
4. **Cache**: Implementar cache de resultados

### Ejemplo Completo

Ver `example_usage.py` para un ejemplo completo ejecutable.
