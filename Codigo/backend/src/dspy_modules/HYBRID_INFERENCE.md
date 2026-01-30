# Hybrid Inference Configuration - DSPy

## 🚀 Arquitectura Implementada

### Dos Velocidades de Inteligencia

| Engine | Modelo | Cuota | Latencia | Uso |
|--------|--------|-------|----------|-----|
| **Fast** | `gemini-2.5-flash-lite` | 1,500 req/día | Baja | 95% de tareas |
| **Power** | `gemini-2.5-flash` | Limitada | Media | Razonamiento complejo |

---

## 📋 Configuración

### Constantes Definidas

```python
MODEL_LITE = "gemini/gemini-2.5-flash-lite"  # Fast Engine
MODEL_POWER = "gemini/gemini-2.5-flash"      # Power Engine
TEMPERATURE_DETERMINISTIC = 0.0               # Máximo determinismo
```

### Funciones Principales

#### 1. `configure_dspy()`
Inicializa DSPy con el **Fast Engine** como modelo global por defecto.

```python
from src.dspy_modules import configure_dspy

# Configurar al inicio de la aplicación
configure_dspy()

# Ahora todos los módulos DSPy usan Fast Engine automáticamente
```

#### 2. `get_powerful_model()`
Obtiene una instancia del **Power Engine** para tareas complejas.

```python
from src.dspy_modules import get_powerful_model
import dspy

# Obtener Power Engine
power_lm = get_powerful_model()

# Usar temporalmente para tarea compleja
with dspy.settings.context(lm=power_lm):
    result = complex_reasoning_module(input_data)
```

#### 3. `get_custom_model()` (Opcional)
Configuración personalizada de cualquier modelo.

```python
from src.dspy_modules import get_custom_model

# Modelo personalizado con temperatura creativa
creative_lm = get_custom_model(
    model_name="gemini/gemini-2.5-flash",
    temperature=0.7,
    max_tokens=4096
)
```

---

## 💡 Casos de Uso

### Fast Engine (Automático)

Usado por defecto para:
- ✅ Clasificación de intenciones
- ✅ Routing de acciones
- ✅ Chat simple
- ✅ Extracción de entidades
- ✅ Análisis rápido

**Ventajas**:
- Alta cuota (1,500 req/día)
- Baja latencia
- Suficiente para la mayoría de tareas

### Power Engine (Explícito)

Usar cuando necesites:
- 🧠 Razonamiento multi-paso
- 🧠 Análisis profundo de contexto
- 🧠 Generación de contenido largo
- 🧠 Fallback cuando Lite falle

**Ejemplo**:
```python
# Tarea simple - usa Fast automáticamente
simple_result = simple_classifier(text="Reunión mañana")

# Tarea compleja - usa Power explícitamente
power_lm = get_powerful_model()
with dspy.settings.context(lm=power_lm):
    complex_result = deep_reasoner(problem="Analiza impacto...")
```

---

## 🔧 Integración en Intelligence Service

El `IntelligenceService` ya usa esta configuración:

```python
# En intelligence.py
class IntelligenceService:
    def __init__(self):
        # Configura Fast Engine como default
        if DSPY_AVAILABLE:
            configure_dspy()
            self.dspy_analyzer = UnifiedAnalyzer()
```

**Resultado**: Todas las llamadas a `analyze_input_dspy()` usan el Fast Engine automáticamente.

---

## 📊 Monitoreo de Uso

```python
from src.dspy_modules import get_model_info

# Ver info de modelos
info = get_model_info()
print(info)
```

**Output**:
```json
{
  "fast_engine": {
    "model": "gemini/gemini-2.5-flash-lite",
    "quota": "1,500 req/día",
    "latency": "Baja",
    "use_case": "95% de tareas"
  },
  "power_engine": {
    "model": "gemini/gemini-2.5-flash",
    "quota": "Limitada",
    "latency": "Media",
    "use_case": "Razonamiento complejo"
  }
}
```

---

## 🎯 Mejores Prácticas

### ✅ DO

```python
# Usar Fast Engine por defecto
configure_dspy()
result = standard_module(input)

# Usar Power Engine solo cuando sea necesario
power_lm = get_powerful_model()
with dspy.settings.context(lm=power_lm):
    result = complex_module(input)
```

### ❌ DON'T

```python
# NO uses Power Engine para todo
power_lm = get_powerful_model()
dspy.settings.configure(lm=power_lm)  # ❌ Desperdicia cuota

# NO olvides configurar DSPy al inicio
# configure_dspy()  # ❌ Sin esto, no hay modelo default
```

---

## 🧪 Testing

Ejecuta el ejemplo de demostración:

```bash
python src/dspy_modules/example_hybrid_inference.py
```

Esto mostrará:
1. Configuración del Fast Engine
2. Tarea simple con Fast Engine (automático)
3. Tarea compleja con Power Engine (explícito)

---

## 📝 Archivos Modificados

1. **`config.py`** - Configuración híbrida completa
2. **`__init__.py`** - Exports actualizados
3. **`example_hybrid_inference.py`** - Demo de uso

---

## 🔄 Migración desde Versión Anterior

Si tenías código usando `get_gemini_lm()`:

**Antes**:
```python
from src.dspy_modules import get_gemini_lm

lm = get_gemini_lm(model_name="gemini-2.5-flash-lite")
```

**Ahora**:
```python
from src.dspy_modules import configure_dspy, get_custom_model

# Opción 1: Usar Fast Engine (recomendado)
configure_dspy()

# Opción 2: Personalizar
lm = get_custom_model(model_name="gemini-2.5-flash-lite")
```
