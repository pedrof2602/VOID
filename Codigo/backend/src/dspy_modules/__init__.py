"""
DSPy Modules para VOID Intelligence System

Exporta configuración, signatures y módulos.
"""
from .config import (
    configure_dspy,
    get_powerful_model,
    get_custom_model,
    get_model_info,
    MODEL_LITE,
    MODEL_POWER
)
from .signatures import (
    UnifiedAnalysis,
    MemoryRefinement,
    IntentDetection,
    ActionClassification
)
# ✅ CORREGIDO: Los módulos están en modules.py, NO en compiler.py
from .modules import (
    UnifiedAnalyzer,
    MemoryRefiner,
    IntentDetector,
    ActionClassifier
)

__all__ = [
    # Config - Hybrid Inference
    'configure_dspy',
    'get_powerful_model',
    'get_custom_model',
    'get_model_info',
    'MODEL_LITE',
    'MODEL_POWER',
    
    # Signatures
    'UnifiedAnalysis',
    'MemoryRefinement',
    'IntentDetection',
    'ActionClassification',
    
    # Modules
    'UnifiedAnalyzer',
    'MemoryRefiner',
    'IntentDetector',
    'ActionClassifier',
]
