"""
DSPy Hybrid Inference Configuration
====================================

Arquitectura de Dos Velocidades:
- Fast Engine (Default): gemini-2.5-flash-lite - 1,500 req/día, baja latencia
- Power Engine (On-Demand): gemini-2.5-flash - Para razonamiento complejo

Author: VOID Intelligence Team
"""
import dspy
import os
from src.config import Config

# ==========================================
# CONSTANTES DE MODELOS
# ==========================================

# Fast Engine: Alta cuota, baja latencia (95% de las tareas)
MODEL_LITE = "gemini/gemini-2.5-flash-lite"

# Power Engine: Razonamiento complejo, mayor capacidad
MODEL_POWER = "gemini/gemini-2.5-flash"

# Configuración de temperatura para determinismo máximo
TEMPERATURE_DETERMINISTIC = 0.0

# Límites de tokens
MAX_TOKENS_DEFAULT = 2048
MAX_TOKENS_EXTENDED = 4096  # Para tareas complejas


# ==========================================
# CONFIGURACIÓN PRINCIPAL
# ==========================================

def configure_dspy():
    """
    Inicializa DSPy con el Fast Engine como modelo global por defecto.
    
    Este modelo se usará automáticamente para:
    - Clasificación de intenciones
    - Routing de acciones
    - Chat simple
    - Extracción de entidades
    
    Returns:
        dspy.LM: Instancia del Fast Engine configurado
    """
    # Configurar Fast Engine (Lite) como modelo por defecto
    lite_lm = dspy.LM(
        model=MODEL_LITE,
        api_key=Config.GOOGLE_API_KEY,
        temperature=TEMPERATURE_DETERMINISTIC,  # 0.0 para máximo determinismo
        max_tokens=MAX_TOKENS_DEFAULT
    )
    
    # Establecer como LM global por defecto
    dspy.settings.configure(lm=lite_lm)
    
    return lite_lm


def get_powerful_model():
    """
    Obtiene una instancia del Power Engine para tareas de razonamiento complejo.
    
    Úsalo cuando necesites:
    - Razonamiento multi-paso
    - Análisis profundo de contexto
    - Generación de contenido largo
    - Fallback cuando el Lite falle
    
    Ejemplo de uso:
        ```python
        # En un módulo específico
        power_lm = get_powerful_model()
        
        # Usar temporalmente el Power Engine
        with dspy.settings.context(lm=power_lm):
            result = complex_reasoning_module(input_data)
        ```
    
    Returns:
        dspy.LM: Instancia del Power Engine lista para usar
    """
    power_lm = dspy.LM(
        model=MODEL_POWER,
        api_key=Config.GOOGLE_API_KEY,
        temperature=TEMPERATURE_DETERMINISTIC,  # 0.0 para máximo determinismo
        max_tokens=MAX_TOKENS_EXTENDED  # Más tokens para razonamiento complejo
    )
    
    return power_lm


# ==========================================
# CONFIGURACIÓN PERSONALIZADA (OPCIONAL)
# ==========================================

def get_custom_model(
    model_name: str = MODEL_LITE,
    temperature: float = TEMPERATURE_DETERMINISTIC,
    max_tokens: int = MAX_TOKENS_DEFAULT
):
    """
    Obtiene un LM con configuración personalizada.
    
    Args:
        model_name: Nombre del modelo (usa constantes MODEL_*)
        temperature: Temperatura (0.0 = determinista, 1.0 = creativo)
        max_tokens: Límite de tokens en la respuesta
    
    Returns:
        dspy.LM: Instancia configurada del modelo
    """
    # Asegurar que el modelo tenga el prefijo correcto
    if not model_name.startswith("gemini/"):
        model_name = f"gemini/{model_name}"
    
    return dspy.LM(
        model=model_name,
        api_key=Config.GOOGLE_API_KEY,
        temperature=temperature,
        max_tokens=max_tokens
    )


# ==========================================
# UTILIDADES
# ==========================================

def get_model_info():
    """
    Retorna información sobre los modelos configurados.
    
    Returns:
        dict: Información de los modelos disponibles
    """
    return {
        "fast_engine": {
            "model": MODEL_LITE,
            "quota": "1,500 req/día",
            "latency": "Baja",
            "use_case": "95% de tareas (routing, clasificación, chat)"
        },
        "power_engine": {
            "model": MODEL_POWER,
            "quota": "Limitada",
            "latency": "Media",
            "use_case": "Razonamiento complejo, fallback"
        }
    }


# ==========================================
# EXPORTS
# ==========================================

__all__ = [
    # Constantes
    'MODEL_LITE',
    'MODEL_POWER',
    'TEMPERATURE_DETERMINISTIC',
    
    # Funciones principales
    'configure_dspy',
    'get_powerful_model',
    
    # Funciones opcionales
    'get_custom_model',
    'get_model_info',
]
