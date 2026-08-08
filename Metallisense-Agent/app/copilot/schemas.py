"""
Pydantic Schemas for Copilot API
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class ExplainAnalysisRequest(BaseModel):
    """Request for analysis explanation"""
    composition: Dict[str, float] = Field(
        ...,
        description="Current composition",
        example={"Fe": 94.5, "C": 3.2, "Si": 2.0, "Mn": 0.4, "P": 0.05, "S": 0.10}
    )
    grade: str = Field(
        ...,
        description="Target grade",
        example="GREY-IRON"
    )
    session_id: Optional[str] = Field(
        default="default",
        description="Identifier used to isolate chat context per operator/session"
    )


class ExplainAnalysisResponse(BaseModel):
    """Response with explanation"""
    explanation: str = Field(..., description="Full explanation text")
    summary: str = Field(..., description="Brief summary")
    action_items: List[str] = Field(..., description="Operator action items")
    risk_level: str = Field(..., description="Risk severity level")
    confidence: float = Field(..., description="Confidence in recommendations")
    context: Dict = Field(..., description="Analysis context")
    timestamp: str = Field(..., description="Analysis timestamp")


class ChatRequest(BaseModel):
    """Chat request"""
    message: str = Field(
        ...,
        description="User's question or message",
        example="Why do we need to add Manganese?"
    )
    include_context: bool = Field(
        default=True,
        description="Include latest analysis context"
    )
    session_id: Optional[str] = Field(
        default="default",
        description="Identifier used to isolate chat history per operator/session"
    )


class ChatResponse(BaseModel):
    """Chat response"""
    response: str = Field(..., description="AI copilot's response")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")


class TTSRequest(BaseModel):
    """Text-to-Speech request"""
    text: str = Field(
        ...,
        description="Text to convert to speech",
        max_length=5000
    )
    language: str = Field(
        default="en",
        description="Language code",
        example="en"
    )
    slow: bool = Field(
        default=False,
        description="Speak slowly"
    )


class TranscriptionResponse(BaseModel):
    """Speech-to-Text response"""
    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language")
    success: bool = Field(..., description="Success status")
    error: Optional[str] = Field(None, description="Error message if failed")


class LanguagesResponse(BaseModel):
    """Supported languages"""
    languages: Dict[str, str] = Field(..., description="Language code to name mapping")
