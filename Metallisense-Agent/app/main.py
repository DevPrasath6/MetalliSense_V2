
"""
MetalliSense AI Service - FastAPI Application
Main entry point for the AI Intelligence Layer
"""
from fastapi import FastAPI, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import uvicorn
from pathlib import Path
import sys
from typing import Optional
import tempfile
import os

# Add app directory to path
sys.path.append(str(Path(__file__).parent))

from config import API_HOST, API_PORT, API_TITLE, API_VERSION, ALLOWED_ORIGINS, ENVIRONMENT
from schemas import (
    AnomalyRequest, 
    AnomalyResponse,
    AlloyRecommendationRequest,
    AlloyRecommendationResponse,
    HealthResponse,
    # Agent-based schemas
    AgentAnalysisRequest,
    AgentAnalysisResponse
)
from inference.anomaly_predict import get_anomaly_predictor
from inference.alloy_predict import get_alloy_predictor
from agents.agent_manager import get_agent_manager

# Copilot imports
from copilot import get_copilot, get_voice_service
from copilot.schemas import (
    ExplainAnalysisRequest,
    ExplainAnalysisResponse,
    ChatRequest,
    ChatResponse,
    TTSRequest,
    TranscriptionResponse,
    LanguagesResponse
)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="AI Intelligence Layer for MetalliSense - Anomaly Detection & Alloy Correction",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for Node.js/frontend integration
# "*" is invalid together with allow_credentials=True, and would allow any site to make
# credentialed requests - restrict to an explicit allow-list configured via ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global predictors (lazy loaded)
anomaly_predictor = None
alloy_predictor = None
agent_manager = None
copilot = None
voice_service = None


def initialize_models():
    """Initialize AI models on startup"""
    global anomaly_predictor, alloy_predictor, agent_manager, copilot, voice_service
    
    try:
        print("Initializing AI models...")
        anomaly_predictor = get_anomaly_predictor()
        alloy_predictor = get_alloy_predictor()
        print("✓ AI models loaded successfully")
        
        print("Initializing Agent Manager...")
        agent_manager = get_agent_manager()
        print("✓ Agent Manager initialized")
        
        print("Initializing Explainable AI Copilot...")
        copilot = get_copilot()
        print("✓ Copilot initialized")
        
        print("Initializing Voice Service...")
        voice_service = get_voice_service()
        print("✓ Voice Service initialized")
        
        return True
    except Exception as e:
        print(f"✗ Error loading AI models: {e}")
        print("Models must be trained before starting the API service.")
        print("Run: python app/training/train_anomaly.py")
        print("Run: python app/training/train_alloy_agent.py")
        return False


def error_detail(prefix: str, exc: Exception) -> str:
    """Build an HTTPException detail string, only including the raw exception
    text outside production so internal error messages aren't leaked to clients."""
    if ENVIRONMENT == "production":
        return prefix
    return f"{prefix}: {str(exc)}"


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    print("="*60)
    print(f"{API_TITLE} v{API_VERSION}")
    print("="*60)
    initialize_models()
    print("="*60)
    print(f"API Server starting on http://{API_HOST}:{API_PORT}")
    print(f"Documentation: http://{API_HOST}:{API_PORT}/docs")
    print("="*60)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": API_TITLE,
        "version": API_VERSION,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "agent_analysis": "/agents/analyze",
            "anomaly_detection": "/anomaly/predict",
            "alloy_correction": "/alloy/recommend",
            "copilot_explain": "/copilot/explain",
            "copilot_chat": "/copilot/chat",
            "copilot_voice_transcribe": "/copilot/voice/transcribe",
            "copilot_voice_synthesize": "/copilot/voice/synthesize",
            "grades": "/grades",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns status of AI models and agents
    """
    models_loaded = {
        "anomaly_model": anomaly_predictor is not None and anomaly_predictor.is_healthy(),
        "alloy_model": alloy_predictor is not None and alloy_predictor.is_healthy(),
        "agent_manager": agent_manager is not None and agent_manager.is_ready(),
        "copilot": copilot is not None,
        "voice_service": voice_service is not None
    }
    
    all_healthy = all(models_loaded.values())
    
    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        message="All models loaded" if all_healthy else "Some models not loaded",
        models_loaded=models_loaded
    )


# ============================================================================
# AGENT-BASED ENDPOINTS (Production Agent Architecture)
# ============================================================================

@app.post("/agents/analyze", response_model=AgentAnalysisResponse, tags=["Agents"])
async def agent_analysis(request: AgentAnalysisRequest):
    """
    🤖 AGENT ANALYSIS ENDPOINT
    
    Production-grade agent orchestration for MetalliSense
    
    This endpoint:
    ✅ Triggers Agent Manager
    ✅ Coordinates Anomaly Detection Agent
    ✅ Conditionally invokes Alloy Correction Agent
    ✅ Aggregates responses with safety notes
    
    Agent Workflow:
    1. Anomaly Detection Agent ALWAYS runs
    2. If HIGH severity detected, Alloy Correction Agent runs
    3. All outputs require human approval
    4. No autonomous actions
    
    Request:
    ```json
    {
        "composition": {"Fe": 81.2, "C": 4.4, "Si": 3.1, "Mn": 0.4, "P": 0.04, "S": 0.02},
        "grade": "SG-IRON"
    }
    ```
    
    Response:
    ```json
    {
        "anomaly_agent": {
            "agent": "AnomalyDetectionAgent",
            "anomaly_score": 0.87,
            "severity": "HIGH",
            "confidence": 0.93,
            "explanation": "..."
        },
        "alloy_agent": {
            "agent": "AlloyCorrectionAgent",
            "recommended_additions": {"Si": 0.22, "Mn": 0.15},
            "confidence": 0.91,
            "explanation": "..."
        },
        "final_note": "Human approval required before action"
    }
    ```
    
    🔐 Safety:
    - Agents are advisory only
    - No autonomous actions
    - Human approval ALWAYS required
    - All decisions logged
    """
    if agent_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent Manager not initialized. Please train models first."
        )
    
    if not agent_manager.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent Manager not ready. Some agents are not initialized."
        )
    
    try:
        # Convert Pydantic model to dict
        composition = request.composition.dict()
        grade = request.grade
        
        # Orchestrate agent analysis
        result = agent_manager.analyze(composition, grade)
        
        # Return aggregated response
        return AgentAnalysisResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail("Agent analysis error", e)
        )


# ============================================================================
# LEGACY ENDPOINTS (Backward Compatibility)
# ============================================================================

@app.post("/anomaly/predict", response_model=AnomalyResponse, tags=["Anomaly Detection"])
async def predict_anomaly(request: AnomalyRequest):
    """
    Anomaly Detection Endpoint
    
    Detects abnormal spectrometer behavior:
    - Sensor drift
    - Measurement noise
    - Unstable melt chemistry
    
    **This endpoint does NOT decide if metal is PASS/FAIL**
    
    Returns:
    - anomaly_score: 0.0 (normal) to 1.0 (highly anomalous)
    - severity: LOW, MEDIUM, or HIGH
    - message: Human-readable explanation
    """
    global anomaly_predictor
    if anomaly_predictor is None:
        try:
            anomaly_predictor = get_anomaly_predictor()
        except Exception as e:
            print(f"Failed to lazy-load anomaly predictor: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error_detail("Anomaly detection model not loaded", e)
            )
    
    try:
        # Convert Pydantic model to dict
        composition = request.composition.dict()
        
        # Get prediction
        result = anomaly_predictor.predict(composition)
        
        # Check for errors
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return AnomalyResponse(
            anomaly_score=result["anomaly_score"],
            severity=result["severity"],
            message=result["message"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail("Prediction error", e)
        )


@app.post("/alloy/recommend", response_model=AlloyRecommendationResponse, tags=["Alloy Correction"])
async def recommend_alloy_additions(request: AlloyRecommendationRequest):
    """
    Alloy Correction Recommendation Endpoint
    
    Given a deviated composition, recommends:
    - Which alloying elements to add
    - Required amount (%) for each element
    
    **This endpoint does NOT decide if metal is PASS/FAIL**
    
    It only answers: "What alloy additions will correct the deviation?"
    
    Returns:
    - recommended_additions: Dict of element additions (%)
    - confidence: 0.0 to 1.0
    - message: Human-readable explanation
    - warning: Safety warnings if applicable
    """
    global alloy_predictor
    if alloy_predictor is None:
        try:
            alloy_predictor = get_alloy_predictor()
        except Exception as e:
            print(f"Failed to load alloy predictor: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error_detail("Alloy correction model not loaded", e)
            )
    
    try:
        # Convert Pydantic model to dict
        composition = request.composition.dict()
        grade = request.grade
        
        # Validate grade
        available_grades = alloy_predictor.get_available_grades()
        if grade not in available_grades:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown grade: {grade}. Available grades: {available_grades}"
            )
        
        # Get prediction
        result = alloy_predictor.predict(grade, composition)
        
        # Check for errors
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return AlloyRecommendationResponse(
            recommended_additions=result["recommended_additions"],
            confidence=result["confidence"],
            message=result["message"],
            warning=result.get("warning")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail("Prediction error", e)
        )


@app.get("/grades", tags=["Grades"])
async def get_available_grades():
    """
    Get list of available metal grades
    
    Returns all grades supported by the alloy correction agent
    """
    if alloy_predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Alloy correction model not loaded"
        )
    
    try:
        grades = alloy_predictor.get_available_grades()
        return {
            "grades": grades,
            "count": len(grades)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail("Error retrieving grades", e)
        )


@app.get("/grades/{grade}", tags=["Grades"])
async def get_grade_specification(grade: str):
    """
    Get specification for a specific grade
    
    Returns composition ranges for all elements in the grade
    """
    if alloy_predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Alloy correction model not loaded"
        )
    
    try:
        spec = alloy_predictor.get_grade_spec(grade)
        return spec
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail("Error retrieving grade specification", e)
        )


# ============================================================================
# COPILOT ENDPOINTS (Explainable AI with Groq LLM)
# ============================================================================

@app.post("/copilot/explain", response_model=ExplainAnalysisResponse, tags=["Copilot"])
async def explain_analysis(request: ExplainAnalysisRequest, include_voice: bool = False):
    """
    🤖 EXPLAINABLE AI - Get human explanation for ML predictions
    
    Takes composition and grade, runs full agent analysis, and generates
    human-readable explanation using Groq LLM.
    
    This endpoint:
    ✅ Runs anomaly detection
    ✅ Runs alloy correction (if needed)
    ✅ Generates natural language explanation
    ✅ Provides risk assessment
    ✅ Gives operator action items
    
    Request:
    ```json
    {
        "composition": {"Fe": 94.5, "C": 3.2, "Si": 2.0, "Mn": 0.4, "P": 0.05, "S": 0.10},
        "grade": "GREY-IRON"
    }
    ```
    
    Response includes:
    - Full explanation text (human-readable)
    - Brief summary
    - Action items for operators
    - Risk level assessment
    - Confidence score
    - Analysis context (ML predictions)
    
    🔐 Safety:
    - Explanations are advisory only
    - Human approval ALWAYS required
    - All recommendations logged
    """
    global copilot, agent_manager
    if agent_manager is None:
        try:
            agent_manager = get_agent_manager()
        except Exception as e:
            print(f"Lazy loading agent manager error: {e}")

    if copilot is None:
        try:
            copilot = get_copilot()
        except Exception as e:
            print(f"Lazy loading copilot error: {e}")
    
    try:
        # Run agent analysis first
        composition = request.composition
        grade = request.grade
        
        agent_result = agent_manager.analyze(composition, grade)
        
        # Generate explanation
        explanation_result = copilot.explain_analysis(
            composition=composition,
            grade=grade,
            anomaly_result=agent_result.get("anomaly_agent"),
            alloy_result=agent_result.get("alloy_agent"),
            session_id=request.session_id or "default"
        )
        
        return ExplainAnalysisResponse(**explanation_result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail("Explanation generation error", e)
        )


@app.post("/copilot/chat", response_model=ChatResponse, tags=["Copilot"])
async def chat_with_copilot(request: ChatRequest):
    """
    💬 CHATBOT - Interactive Q&A with AI Copilot
    
    Ask questions about the latest analysis, metallurgical concepts,
    or get clarification on recommendations.
    
    Examples:
    - "Why do we need to add Manganese?"
    - "What happens if we don't correct this?"
    - "Explain the risk level"
    - "What is the confidence score?"
    
    The copilot maintains conversation history and can reference
    previous questions and the latest analysis context.
    
    Request:
    ```json
    {
        "message": "Why do we need to add Manganese?",
        "include_context": true
    }
    ```
    
    Response:
    ```json
    {
        "response": "Manganese is recommended because...",
        "conversation_id": "12345"
    }
    ```
    """
    if copilot is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Explainable AI Copilot not initialized"
        )
    
    try:
        response = copilot.chat(
            user_message=request.message,
            include_context=request.include_context,
            session_id=request.session_id or "default"
        )
        
        return ChatResponse(**response)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail("Chat error", e)
        )


@app.delete("/copilot/chat/history", tags=["Copilot"])
async def clear_chat_history(session_id: Optional[str] = None):
    """
    🗑️ Clear conversation history

    Clears the conversation history for a fresh start.
    Useful when starting a new analysis session.

    If `session_id` is omitted, ALL sessions are cleared - pass the same
    session_id used for /copilot/chat to only clear that operator's history.
    """
    if copilot is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Explainable AI Copilot not initialized"
        )

    try:
        copilot.clear_history(session_id=session_id)
        return {"message": "Conversation history cleared", "success": True}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail("Error clearing history", e)
        )


@app.post("/copilot/voice/transcribe", response_model=TranscriptionResponse, tags=["Voice"])
async def transcribe_audio(audio: UploadFile = File(...), language: Optional[str] = None):
    """
    🎤 SPEECH-TO-TEXT - Convert voice input to text
    
    Upload audio file and get transcribed text.
    Uses Groq Whisper large-v3 model for high accuracy.
    
    Supported formats: WAV, MP3, M4A, OGG, FLAC
    
    Example usage:
    ```bash
    curl -X POST "http://localhost:8001/copilot/voice/transcribe" \
         -F "audio=@recording.wav" \
         -F "language=en"
    ```
    
    Response:
    ```json
    {
        "text": "Why do we need to add manganese?",
        "language": "en",
        "success": true
    }
    ```
    """
    if voice_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice Service not initialized"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio.filename).suffix) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Transcribe
            result = voice_service.transcribe_audio(tmp_path, language)
            return TranscriptionResponse(**result)
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail("Transcription error", e)
        )


@app.post("/copilot/voice/synthesize", tags=["Voice"])
async def synthesize_speech(request: TTSRequest):
    """
    🔊 TEXT-TO-SPEECH - Convert text to voice
    
    Convert text to speech audio (MP3 format).
    Uses Google Text-to-Speech (gTTS) for natural voice output.
    
    Request:
    ```json
    {
        "text": "Manganese addition of 0.15% is recommended to improve tensile strength.",
        "language": "en",
        "slow": false
    }
    ```
    
    Returns: MP3 audio file
    
    Supported languages: en, es, fr, de, it, pt, ru, ja, ko, zh, hi, ar
    
    Example usage in browser:
    ```javascript
    const response = await fetch('/copilot/voice/synthesize', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: "Hello", language: "en"})
    });
    const blob = await response.blob();
    const audio = new Audio(URL.createObjectURL(blob));
    audio.play();
    ```
    """
    if voice_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice Service not initialized"
        )
    
    try:
        audio_bytes = voice_service.text_to_speech(
            text=request.text,
            language=request.language,
            slow=request.slow
        )
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail("Speech synthesis error", e)
        )


@app.get("/copilot/voice/languages", response_model=LanguagesResponse, tags=["Voice"])
async def get_supported_languages():
    """
    🌍 Get supported languages for voice services
    
    Returns list of language codes and names supported
    by both Speech-to-Text and Text-to-Speech services.
    
    Response:
    ```json
    {
        "languages": {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            ...
        }
    }
    ```
    """
    if voice_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice Service not initialized"
        )
    
    try:
        languages = voice_service.get_supported_languages()
        return LanguagesResponse(languages=languages)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail("Error retrieving languages", e)
        )


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler - only leak exception details outside production"""
    print(f"Unhandled exception on {request.url.path}: {exc}")
    content = {
        "error": "Internal server error",
        "status_code": 500
    }
    if ENVIRONMENT != "production":
        content["detail"] = str(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content
    )


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
