from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

# Categorías para recuerdos/memoria
class MemoryCategory(str, Enum):
    FACT = "FACT"
    IDEA = "IDEA"
    JOURNAL = "JOURNAL"
    GOAL = "GOAL"
    NOISE = "NOISE"
    EMERGENCY = "EMERGENCY"

# Categorías para acciones
class ActionCategory(str, Enum):
    CALENDAR = "CALENDAR"
    TODO = "TODO"
    REMINDER = "REMINDER"

class IntelligenceOutput(BaseModel):
    category: MemoryCategory
    confidence: float
    tags: List[str] = Field(default_factory=list)
    entities: Dict[str, Any] = Field(default_factory=dict)

class ActionOutput(BaseModel):
    """Output para clasificación de acciones"""
    category: ActionCategory
    confidence: float
    tags: List[str] = Field(default_factory=list)
    entities: Dict[str, Any] = Field(default_factory=dict)

class UnifiedOutput(BaseModel):
    """Output unificado que combina detección de intención, clasificación y extracción de entidades"""
    type: str  # "ACTION" o "MEMORY"
    category: str  # CALENDAR, TODO, REMINDER, FACT, IDEA, etc.
    refined_text: str  # Texto limpio sin ruido
    title: Optional[str] = None  # Para eventos: título corto
    date: Optional[str] = None  # Fecha extraída
    time: Optional[str] = None  # Hora extraída
    location: Optional[str] = None  # Ubicación física del evento
    reminder_minutes: Optional[int] = None  # Minutos antes para recordatorio
    entities: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    
    # 🆕 Autonomous Tool Execution
    tool_name: Optional[str] = None  # e.g., "calendar_add", "notion_create"
    tool_args: Optional[Dict[str, Any]] = None  # Arguments for the tool
    
    
class MemoryPayload(BaseModel):
    """El paquete final que viaja a la base de datos"""
    raw_input: str
    content: str          # El texto refinado
    vector: List[float]
    category: MemoryCategory
    priority: str = "LOW"
    tags: List[str] = Field(default_factory=list)  # ✅ Correcto: no mutable
    entities: Dict[str, Any] = Field(default_factory=dict)  # ✅ Correcto: no mutable
    duration: float = Field(default=0.0, ge=0.0)  # Validación: debe ser >= 0

# ============================================
# Device Signal Schemas (for FastAPI/IoT)
# ============================================

class SignalType(str, Enum):
    """Signal types matching database ENUM"""
    HAPTIC_ONLY = "HAPTIC_ONLY"
    TEXT = "TEXT"
    ACTION = "ACTION"

class DeviceSignalPayload(BaseModel):
    """Flexible payload structure for device signals"""
    text: Optional[str] = None
    haptic: Optional[str] = None  # e.g., "LIGHT", "MEDIUM", "HEAVY"
    action: Optional[str] = None  # e.g., "OPEN_CALENDAR", "CREATE_NOTE"
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "examples": [
                {"text": "4590", "haptic": "HEAVY"},
                {"action": "OPEN_CALENDAR", "params": {"event_id": "123"}},
                {"haptic": "LIGHT"}
            ]
        }

class DeviceSignal(BaseModel):
    """Device signal record from database"""
    id: str
    user_id: str
    type: SignalType
    payload: DeviceSignalPayload
    is_delivered: bool
    created_at: str

class VoiceInputResponse(BaseModel):
    """Response from /input/voice endpoint"""
    status: str
    message: str
    signal_id: Optional[str] = None
    signal_type: Optional[SignalType] = None
