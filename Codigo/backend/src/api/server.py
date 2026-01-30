"""
VOID Backend - FastAPI Server
Decoupled IoT Architecture: PC Input -> Backend Processing -> Mobile Output
"""

import os
import logging
import tempfile
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from uuid import UUID

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

from src.config import Config
from src.schemas import (
    VoiceInputResponse, 
    SignalType, 
    DeviceSignalPayload,
    UnifiedOutput
)
from src.services.transcriber import transcribe_audio_async
from src.services.intelligence import IntelligenceService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
supabase: Optional[Client] = None
brain: Optional[IntelligenceService] = None
tools: Optional['ToolRegistry'] = None  # 🆕 Tool execution registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global supabase, brain, tools
    
    # Startup
    logger.info("🚀 Starting VOID Backend API...")
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        raise
    
    # Initialize Supabase client
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    logger.info("✅ Supabase client initialized")
    
    # Initialize Intelligence Service
    brain = IntelligenceService()
    logger.info("✅ Intelligence Service initialized")
    
    # 🆕 Initialize Tool Registry
    from src.services.tools import ToolRegistry
    tools = ToolRegistry()
    logger.info("✅ Tool Registry initialized")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down VOID Backend API...")
    supabase = None
    brain = None
    tools = None


# Create FastAPI app
app = FastAPI(
    title="VOID Backend API",
    description="Decoupled IoT Architecture for Voice-to-Device Communication",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "VOID Backend API",
        "version": "1.0.0"
    }


async def _run_tool_background(tool_name: str, tool_args: dict, recording_id: str):
    """
    🔥 Fire-and-Forget Background Task Executor
    
    Ejecuta herramientas (Google Calendar, Notion, etc.) en segundo plano
    sin bloquear la respuesta HTTP al usuario.
    
    Args:
        tool_name: Nombre de la herramienta (ej: 'calendar_add')
        tool_args: Argumentos para la herramienta
        recording_id: ID del recording para actualizar con el resultado
    
    Behavior:
        - Usa asyncio.to_thread() para no bloquear el Event Loop
        - Captura errores sin propagarlos (fail-safe)
        - Actualiza el recording con el resultado de la herramienta
    """
    try:
        logger.info(f"🔧 [Background] Executing tool: {tool_name}")
        logger.info(f"📦 [Background] Tool args: {tool_args}")
        
        # Ejecutar herramienta en thread pool (no bloquea Event Loop)
        tool_result = await asyncio.to_thread(tools.execute, tool_name, tool_args)
        
        logger.info(f"✅ [Background] Tool executed successfully: {tool_result}")
        
        # Actualizar recording con el resultado de la herramienta
        if tool_result and isinstance(tool_result, dict):
            try:
                supabase.table("recordings").update({
                    "entities": {
                        "tool_result": tool_result,
                        "tool_name": tool_name
                    }
                }).eq("id", recording_id).execute()
                logger.info(f"✅ [Background] Recording updated with tool result")
            except Exception as update_error:
                logger.warning(f"⚠️ [Background] Failed to update recording: {update_error}")
        
    except Exception as e:
        logger.error(f"❌ [Background] Tool execution failed: {e}")
        # No re-raise: esto es fire-and-forget, no debe tumbar el servidor
        
        # Intentar marcar el error en el recording
        try:
            supabase.table("recordings").update({
                "entities": {
                    "tool_error": str(e),
                    "tool_name": tool_name
                }
            }).eq("id", recording_id).execute()
        except Exception as update_error:
            logger.error(f"❌ [Background] Failed to log error in recording: {update_error}")


@app.post("/input/voice", response_model=VoiceInputResponse)
async def process_voice_input(
    file: UploadFile = File(..., description="Audio file (WAV format)"),
    user_id: str = Form(..., description="User UUID")
):
    """
    Process voice input from PC client
    
    Flow:
    1. Receive audio file
    2. Transcribe using Deepgram (STT)
    3. Process with DSPy Brain (Intelligence)
    4. PERSIST TO DATABASE:
       A. Insert into recordings table
       B. Insert into memory_embeddings table (with vector)
       C. Insert into device_signals table
    5. Return success confirmation
    
    Args:
        file: Audio file upload
        user_id: UUID of the user
        
    Returns:
        VoiceInputResponse with status and signal_id
    """
    temp_audio_path = None
    recording_id = None
    
    try:
        # Validate user_id format
        try:
            UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id format. Must be a valid UUID."
            )
        
        # Validate file type
        if not file.filename.endswith(('.wav', '.mp3', '.m4a', '.ogg')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Supported formats: WAV, MP3, M4A, OGG"
            )
        
        logger.info(f"📥 Received audio file from user {user_id[-4:]}: {file.filename}")
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_audio_path = temp_file.name
        
        logger.info(f"💾 Saved to temporary file: {temp_audio_path}")
        
        # Step 1: Transcribe audio
        logger.info("👂 Transcribing audio...")
        transcription = await transcribe_audio_async(temp_audio_path)
        
        if not transcription:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not transcribe audio. Please try again with clearer audio."
            )
        
        logger.info(f"🗣️ Transcription: {transcription}")
        
        # Step 2: Process with DSPy Brain
        logger.info("🧠 Processing with Intelligence Service...")
        analysis: UnifiedOutput = await brain.analyze_input_dspy(transcription)
        
        logger.info(f"🎯 Analysis result - Type: {analysis.type}, Category: {analysis.category}")
        
        # Step 3: Generate embedding vector (768 dimensions)
        logger.info("🔢 Generating embedding vector...")
        try:
            embedding_vector = await brain.generate_embedding(transcription)
            logger.info(f"✅ Embedding generated: {len(embedding_vector)} dimensions")
        except Exception as e:
            logger.warning(f"⚠️ Embedding generation failed: {e}, using fallback")
            embedding_vector = [0.0] * 768  # Fallback
        
        # Step 4A: INSERT INTO RECORDINGS
        logger.info("💾 Inserting into recordings table...")
        
        # Build summary from analysis
        summary = analysis.refined_text if analysis.refined_text else transcription
        
        recording_data = {
            "user_id": user_id,
            "title": analysis.title if analysis.title else "Nueva Nota",
            "audio_url": None,  # Could upload to Storage later
            "duration": 0.0,
            "transcription": transcription,
            "summary": summary,
            "category": analysis.category,
            "priority": "NORMAL",
            "tags": analysis.tags if analysis.tags else [],
            "entities": analysis.entities if analysis.entities else {},
            "is_handled": False
        }
        
        recording_result = supabase.table("recordings").insert(recording_data).execute()
        
        if not recording_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save recording to database"
            )
        
        recording_id = recording_result.data[0]['id']
        logger.info(f"✅ Recording saved with ID: {recording_id}")
        
        # Step 4B: INSERT INTO MEMORY_EMBEDDINGS
        logger.info("🧠 Inserting into memory_embeddings table...")
        
        embedding_data = {
            "user_id": user_id,
            "recording_id": recording_id,
            "content": transcription,
            "embedding": embedding_vector
        }
        
        embedding_result = supabase.table("memory_embeddings").insert(embedding_data).execute()
        
        if embedding_result.data:
            logger.info(f"✅ Embedding saved with ID: {embedding_result.data[0]['id']}")
        else:
            logger.warning("⚠️ Failed to save embedding (non-critical)")
        
        # Step 4C: INSERT INTO DEVICE_SIGNALS
        logger.info("📱 Inserting into device_signals table...")
        
        signal_type = _determine_signal_type(analysis)
        payload = _build_signal_payload(analysis)
        
        signal_result = supabase.table("device_signals").insert({
            "user_id": user_id,
            "type": signal_type.value,
            "payload": payload.model_dump(exclude_none=True)
        }).execute()
        
        if not signal_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to insert signal into database"
            )
        
        signal_id = signal_result.data[0]["id"]
        logger.info(f"✅ Signal queued successfully: {signal_id}")
        
        logger.info("🎉 FULL PERSISTENCE COMPLETED - No amnesia!")

        logger.info(f"🔍 DEBUG RAW ANALYSIS: Tool: '{analysis.tool_name}' | Args: {analysis.tool_args}")
        
        # 🔥 AUTONOMOUS TOOL EXECUTION (ASYNC FIRE-AND-FORGET)
        # El modelo decide, Python ejecuta en segundo plano SIN BLOQUEAR
        if analysis.tool_name:
            logger.info(f"🚀 Queueing tool for background execution: {analysis.tool_name}")
            
            # Lanzar tarea en background (no esperar a que termine)
            asyncio.create_task(
                _run_tool_background(
                    tool_name=analysis.tool_name,
                    tool_args=analysis.tool_args,
                    recording_id=recording_id
                )
            )
            
            logger.info(f"✅ Tool queued successfully (non-blocking)")
        
        # ⚡ RETORNAR INMEDIATAMENTE (no esperar a la herramienta)
        return VoiceInputResponse(
            status="success",
            message="Signal queued for mobile device",
            signal_id=signal_id,
            signal_type=signal_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error processing voice input: {e}")
        
        # Attempt rollback if recording was created
        if recording_id:
            try:
                supabase.table("recordings").delete().eq("id", recording_id).execute()
                logger.info(f"🗑️ Rolled back recording: {recording_id}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup: {cleanup_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        # Cleanup temporary file
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.unlink(temp_audio_path)
                logger.info(f"🗑️ Cleaned up temporary file")
            except Exception as e:
                logger.warning(f"⚠️ Could not delete temporary file: {e}")


def _determine_signal_type(analysis: UnifiedOutput) -> SignalType:
    """Determine the appropriate signal type based on analysis"""
    if analysis.type == "ACTION":
        return SignalType.ACTION
    elif analysis.refined_text and len(analysis.refined_text) > 0:
        return SignalType.TEXT
    else:
        return SignalType.HAPTIC_ONLY


def _build_signal_payload(analysis: UnifiedOutput) -> DeviceSignalPayload:
    """Build the JSONB payload from analysis result"""
    payload = DeviceSignalPayload()
    
    if analysis.type == "ACTION":
        payload.action = analysis.category
        payload.params = {
            "title": analysis.title,
            "date": analysis.date,
            "time": analysis.time,
            "location": analysis.location,
            "reminder_minutes": analysis.reminder_minutes,
            "entities": analysis.entities,
            "tags": analysis.tags
        }
        payload.params = {k: v for k, v in payload.params.items() if v is not None}
        payload.haptic = "MEDIUM"
    elif analysis.refined_text:
        payload.text = analysis.refined_text
        payload.haptic = "LIGHT"
    else:
        payload.haptic = "LIGHT"
    
    return payload


# Run with: uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
